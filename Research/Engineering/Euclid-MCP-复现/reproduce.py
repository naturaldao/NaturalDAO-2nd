"""Run from the pinned Euclid-MCP checkout using its Python environment."""
import argparse
import json
import sys
import time
from pathlib import Path

root = Path.cwd()
sys.path[:0] = [str(root), str(root / "benchmarks"),
                str(root / "examples" / "07_it_security_compliance")]

import rbac_1000
import reasoning_benchmark

def benchmarks(conditions):
    for table, bench in [(2, reasoning_benchmark), (3, rbac_1000)]:
        for condition in conditions:
            for q in bench.QUESTIONS:
                model = bench.CLOUD_MODEL if condition == "B" else bench.SMALL_MODEL
                run = bench.run_with_euclid if condition == "C" else bench.run_direct
                result = run(q, model)
                yield dict(table=table, condition=condition, model=model, id=q["id"],
                           expected=q.get("expected", q.get("ground_truth")), **result)

def replay(source):
    """Replay the recorded Table 3 queries with the supported solution limit."""
    for line in source.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if (row["table"], row["condition"]) != (3, "C"):
            continue
        query = row["generated_query"]
        start = time.perf_counter()
        result = rbac_1000.reason(knowledge=rbac_1000.KB_FULL + "\n" + query, max_solutions=1000)
        elapsed = (time.perf_counter() - start) * 1000
        bindings = [s.substitutions for s in result.solutions]
        if result.error:
            answer = None
        elif isinstance(row["expected"], int):
            answer = len({s["who"] for s in bindings})
        else:
            answer = "Yes" if bindings else "No"
        yield dict(id=row["id"], query=query, expected=row["expected"], answer=answer,
                   correct=answer == row["expected"], error=result.error, bindings=bindings,
                   elapsed_ms=elapsed)

def cases():
    import demo

    for size in ("small", "large"):
        kb = demo.load_knowledge(use_small=size == "small")
        for q in demo.QUESTIONS + demo.DIAGNOSE_QUESTIONS + demo.WHAT_IF_SCENARIOS:
            query = q["query"]
            options = dict(query=query, max_solutions=50, max_depth=30)
            if "mode" in q:
                result = demo.diagnose(knowledge=kb, mode=q["mode"], **options)
                data = result.model_dump(exclude={"solutions"})
            elif "modifications" in q:
                result = demo.what_if(base_knowledge=kb, modifications=q["modifications"], **options)
                data = result.model_dump()
            else:
                result = demo.reason(knowledge=kb, **options)
                data = dict(error=result.error, bindings=[s.substitutions for s in result.solutions],
                            first_proof=result.solutions[0].proof.model_dump() if result.solutions and result.solutions[0].proof else None)
            yield dict(size=size, id=q["id"], query=query, result=data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("suite", choices=["benchmarks", "cases", "replay"])
    parser.add_argument("output", type=Path)
    parser.add_argument("--conditions", nargs="+", choices=list("ABC"), default=["A", "C"])
    parser.add_argument("--source", type=Path, help="Original benchmarks JSONL for replay")
    args = parser.parse_args()
    if args.suite == "replay" and args.source is None:
        parser.error("replay requires --source")
    rows = {"cases": cases, "benchmarks": lambda: benchmarks(args.conditions),
            "replay": lambda: replay(args.source)}[args.suite]()
    with args.output.open("x", encoding="utf-8") as output:
        for row in rows:
            print(json.dumps(row, ensure_ascii=False), file=output, flush=True)
            print(row.get("table", row.get("size")), row.get("condition", ""), row["id"], flush=True)
