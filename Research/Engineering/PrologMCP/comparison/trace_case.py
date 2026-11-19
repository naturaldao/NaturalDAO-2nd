"""Trace one archived case, from model responses and MCP queries to the final labels."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8-sig"))


def model_answers(path, case_id):
    answers = {}
    for line in (ROOT / path).read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if row["id"] == case_id:
            content = json.loads(row["response"]["message"]["content"])
            answers[row["mode"]] = content
    return answers


def mcp_trace(case, source, server):
    rows = read(f"raw/{source}/{server}.json")["cases"]
    row = next(r for r in rows if r["id"] == case["id"])
    if row.get("error") or row.get("cleanup_error"):
        raise ValueError(row)
    evidence = {}
    for call in row["calls"]:
        if call["tool"] not in ("reason", "run_goal"):
            continue
        reply = call["response"]
        if reply["isError"]:
            raise ValueError(reply)
        body = reply.get("structuredContent")
        if body is None:
            body = json.loads(reply["content"][0]["text"])
        if server == "prolog":
            if not body["ok"] or body["outcome"] not in ("success", "failure"):
                raise ValueError(body)
            goal = call["arguments"]["goal"]
            evidence[goal] = body["outcome"] == "success"
        else:
            goal = call["arguments"]["query"]
            if body.get("error") or body["query"] != goal or not isinstance(body["solutions"], list):
                raise ValueError(body)
            evidence[goal] = bool(body["solutions"])
    bits = "".join("1" if evidence[g] else "0" for g in case["goals"])
    return {"support": evidence, "bits": bits, "label": case["decode"][bits]}


def replay(case):
    case_id = case["id"]
    llama = model_answers("llm_raw.jsonl", case_id)
    record_only = model_answers("record_only_llm_raw.jsonl", case_id)
    fact_sets = {"oracle": case["facts"], "hybrid": llama["extract"]["facts"],
                 "record-only": record_only["extract"]["facts"]}
    traces = {}
    for source, facts in fact_sets.items():
        traces[source] = {"facts": sorted(set(facts))}
        for server in ("prolog", "euclid"):
            traces[source][server] = mcp_trace(case, source, server)
    kev = next(r for r in read("kev-m10.json")["results"] if r["id"] == case_id)
    kev_label = max(kev["logits"], key=kev["logits"].get)
    direct = llama["direct"]["label"]
    hybrid = traces["hybrid"]["prolog"]["label"]
    pair = direct if direct == hybrid else "REVIEW"
    triple = direct if direct == hybrid == kev_label else "REVIEW"
    return {"id": case_id, "text": case["text"], "llama_direct": direct,
            "kev": {"label": kev_label, "probabilities": kev["probabilities"]},
            "mcp": traces, "two_way": pair, "three_way": triple, "reference_label": case["gold"]}


if __name__ == "__main__":
    cases = {case["id"]: case for case in read("cases.json")}
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case_id", choices=cases, nargs="?", default="release-01")
    args = parser.parse_args()
    print(json.dumps(replay(cases[args.case_id]), indent=2, ensure_ascii=False))
