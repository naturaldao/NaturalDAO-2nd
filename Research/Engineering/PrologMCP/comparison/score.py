"""Recompute all scores from observed responses. Missing responses count as incorrect."""
import csv
import json
import math
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8-sig"))

def by_id(records):
    index = {r["id"]: r for r in records}
    if len(index) != len(records):
        raise ValueError("Duplicate case IDs")
    return index

def timing(samples):
    if not samples:
        return {}
    values = sorted(samples)
    return {"p50_ms": round(statistics.median(values), 1),
            "p95_ms": round(values[math.ceil(.95 * len(values))-1], 1)}

def main():
    cases = by_id(load("cases.json"))
    groups = sorted({c["family"] for c in cases.values()})
    predictions, scores, fact_checks = {}, {}, {}
    spans = {}
    def add(name, records, field, latencies):
        rows = by_id(records)
        if rows.keys() - cases.keys():
            raise ValueError("Unknown case IDs")
        pred = {i: rows.get(i, {}).get(field) for i in cases}
        predictions[name] = pred
        scores[name] = {"correct": sum(pred[i] == c["gold"] for i,c in cases.items()),
                        "total": len(cases), "missing": sum(x is None for x in pred.values()),
                        "groups": {g: sum(pred[i] == c["gold"] for i,c in cases.items() if c["family"] == g)
                                   for g in groups}, **timing(latencies)}

    for variant, prefix in (("hybrid",""), ("record-only","record_only_")):
        raw = [json.loads(line) for line in (ROOT/(prefix+"llm_raw.jsonl")).read_text().splitlines()]
        direct = [r for r in raw if r["mode"] == "direct"]
        if direct:
            add("llama-direct", direct, "answer", [r["elapsed_ms"] for r in direct])
        ext = by_id([r for r in raw if r["mode"] == "extract"])
        spans[variant] = {i: r["elapsed_ms"] for i,r in ext.items()}
        counts = dict(exact=0, extra=0, missing=0, total=len(cases), invalid=0, true_positives=0)
        for i, case in cases.items():
            actual = ext.get(i, {}).get("answer")
            if actual is None:
                counts["invalid"] += 1
                continue
            actual, expected = set(actual), set(case["facts"])
            counts["exact"] += actual == expected
            counts["extra"] += len(actual-expected)
            counts["missing"] += len(expected-actual)
            counts["true_positives"] += len(expected & actual)
        fact_checks[variant] = counts

    for variant in ("oracle","hybrid","record-only"):
        for server in ("prolog","euclid"):
            rows = load(f"raw/{variant}/{server}.json")["cases"]
            # Sequential stage-time estimate for hybrid; execution used saved extractions.
            durations = [r["elapsed_ms"] + spans.get(variant,{}).get(r["id"],0) for r in rows]
            add(variant+"-"+server, rows, "predicted", durations)

    if (ROOT/"kev-m10.json").exists():
        rows = load("kev-m10.json")["results"]
        add("kev-m10", rows, "prediction", [1000*r["elapsed_s"] for r in rows])

    gates = {}
    def agreement(name, arms):
        accepted = [i for i in cases if predictions[arms[0]][i] is not None and
                    len({predictions[a][i] for a in arms}) == 1]
        wrong = [i for i in accepted if predictions[arms[0]][i] != cases[i]["gold"]]
        gates[name] = {"agree": len(accepted), "correct_agreements":len(accepted)-len(wrong),
                       "wrong_agreements":wrong,"review":len(cases)-len(accepted)}
        predictions[name] = {i: predictions[arms[0]][i] if i in accepted else "REVIEW" for i in cases}
    agreement("direct+hybrid", ["llama-direct","hybrid-prolog"])
    if "kev-m10" in predictions:
        agreement("direct+hybrid+kev", ["llama-direct","hybrid-prolog","kev-m10"])

    output = dict(scores=scores, fact_checks=fact_checks, agreement=gates)
    (ROOT/"metrics.json").write_text(json.dumps(output, indent=2)+"\n")
    with (ROOT/"predictions.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id","gold",*predictions.keys()])
        for i,c in cases.items():
            writer.writerow([i,c["gold"],*[pred[i] for pred in predictions.values()]])
    print(json.dumps(output,indent=2))

if __name__ == "__main__":
    main()
