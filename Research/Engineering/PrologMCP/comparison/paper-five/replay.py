"""Run paper Table 2 gold programs using the shared, pinned stdio clients."""
import argparse
import ast
import asyncio
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import mcp_runner

SOURCE = "benchmarks/reasoning_benchmark.py"
EXPECTED_IDS = ["Q1", "Q2", "Q3", "Q4", "Q5"]


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def extract_cases(root):
    source_bytes = (root / SOURCE).read_bytes().replace(b"\r\n", b"\n")
    assignments = [n for n in ast.parse(source_bytes).body if isinstance(n, ast.Assign)
                   and any(isinstance(v, ast.Name) and v.id == "QUESTIONS" for v in n.targets)]
    if len(assignments) != 1:
        raise ValueError("Expected one QUESTIONS literal")
    problems = ast.literal_eval(assignments[0].value)
    if [row["id"] for row in problems] != EXPECTED_IDS:
        raise ValueError("Unexpected case IDs")
    cases = []
    oracle = {}
    for row in problems:
        lines = row["gold_euclid"].strip().splitlines()
        query = lines.pop()
        if not query.startswith("? ") or row["expected"] not in ("Yes", "No"):
            raise ValueError(f"Unexpected query or expected answer in {row['id']}")
        program = "\n".join(
            re.sub(r"\$([a-z]+)", lambda m: m[1].capitalize(), line)
            .replace(" IF ", " :- ").replace(" AND ", ", ") + "." for line in lines
        )
        if mcp_runner.euclid_program(program) != "\n".join(lines):
            raise ValueError("Literal round trip changed the Euclid program")
        cases.append({"id": row["id"], "knowledge": program, "goals": [query[2:]],
                      "decode": {"1": "Yes", "0": "No"}})
        oracle[row["id"]] = row["expected"]
    return cases, oracle, hashlib.sha256(source_bytes).hexdigest()


async def run(args):
    cases, oracle, source_hash = extract_cases(args.euclid_repo)
    args.output.mkdir(exist_ok=True, parents=True)
    args.cases = args.output / "cases.json"
    write_json(args.cases, cases)
    await mcp_runner.main(args)
    results = {}
    for server in args.servers:
        rows = json.loads((args.output / (server + ".json")).read_text(encoding="utf-8"))["cases"]
        if [r["id"] for r in rows] != EXPECTED_IDS:
            raise ValueError("Incomplete execution")
        results[server] = {r["id"]: {"predicted": r["predicted"], "expected": oracle[r["id"]],
                                     "correct": r["predicted"] == oracle[r["id"]],
                                     "error": r.get("error") or r.get("cleanup_error")}
                           for r in rows}
    write_json(args.output / "scores.json", {"benchmark_commit": mcp_runner.PINS["euclid"],
               "benchmark_path": SOURCE, "source_sha256_lf": source_hash, "results": results})


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    for server in mcp_runner.PINS:
        p.add_argument("--" + server + "-repo", required=True, type=Path)
        p.add_argument("--" + server + "-python", required=True, type=Path)
    p.add_argument("--swipl", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    options = p.parse_args()
    options.servers = list(mcp_runner.PINS)
    asyncio.run(run(options))
