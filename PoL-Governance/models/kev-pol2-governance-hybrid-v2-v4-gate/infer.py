#!/usr/bin/env python3
import argparse, json
from pathlib import Path
from kev.api import question_keys
from kev.data import load_records
from kev.predictors import LocalPredictor

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--run-v2", required=True, type=Path)
    p.add_argument("--run-v4", required=True, type=Path)
    p.add_argument("--input", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--device", default="cuda")
    p.add_argument("--unknown-threshold", type=float, default=0.60)
    a = p.parse_args()
    ctx = {"max_state": 4096, "max_branch": 4096, "max_packed": 8192}
    v2 = LocalPredictor(str(a.run_v2), a.device, context=ctx)
    v4 = LocalPredictor(str(a.run_v4), a.device, context=ctx)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    with a.output.open("x", encoding="utf-8") as h:
        for rec in load_records(a.input):
            p2, p4 = v2(rec), v4(rec)
            ans = {}
            for qid, q in rec["questions"].items():
                keys = question_keys(q["type"], q.get("criteria"))
                pr2, pr4 = p2["probabilities"][qid], p4["probabilities"][qid]
                label = max(keys, key=lambda k: pr2[k])
                if "unknown" in keys and float(pr4.get("unknown", 0.0)) > a.unknown_threshold:
                    label = "unknown"
                ans[qid] = {"answer": label, "probabilities": {k: pr2[k] for k in keys}, "unknown_gate_p": float(pr4.get("unknown", 0.0)) if "unknown" in keys else None}
            h.write(json.dumps({"case_id": rec.get("case_id"), "unit_id": rec.get("unit_id"), "answers": ans, "execution_status": "ok"}, ensure_ascii=False) + "
")

if __name__ == "__main__":
    main()
