"""Run the 20 public cases against TypeSafe Jev. Requires TYPESAFE_API_KEY.
Usage: python run_jev.py --model <versioned-id> --output <new-results.jsonl>
A rerun uses a new output file; partial files preserve successful responses.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, help="Versioned Jev model, e.g. jev-1.14.0")
    parser.add_argument("--cases", type=Path, default=Path(__file__).with_name("cases.json"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"jev-\d+(?:\.\d+){2}", args.model):
        parser.error("Supply a versioned model id, not a floating alias.")
    key = os.environ.get("TYPESAFE_API_KEY")
    if not key:
        parser.error("TYPESAFE_API_KEY is missing.")
    raw_cases = args.cases.read_bytes()
    cases = json.loads(raw_cases.decode("utf-8-sig"))
    digest = hashlib.sha256(raw_cases).hexdigest()
    with args.output.open("x", encoding="utf-8") as out:
        for case in cases:
            payload = {"model": args.model, "state": case["text"], "questions": {"decision": {
                "type": "choice", "instructions": "Select the answer to the question in the state.",
                "criteria": dict.fromkeys(case["labels"])}}}
            req = Request("https://api.typesafe.ai/v1/systemone",
                          data=json.dumps(payload).encode("utf-8"),
                          headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"})
            start = time.perf_counter()
            try:
                with urlopen(req, timeout=60) as response:
                    raw = json.load(response)
            except HTTPError as err:
                raise SystemExit(f"Case {case['id']} received HTTP {err.code}; partial rows preserved.") from None
            seconds = time.perf_counter() - start
            if raw["model"] != args.model:
                raise ValueError("Server model id differed from the requested pin.")
            answer = raw["answers"]["decision"]
            probs = answer["probabilities"]
            if (answer["type"] != "choice" or answer["choice"] not in case["labels"]
                    or set(probs) != set(case["labels"])
                    or any(not math.isfinite(p) or not 0 <= p <= 1 for p in probs.values())
                    or abs(sum(probs.values()) - 1) > 0.02):
                raise ValueError(f"Invalid typed response for {case['id']}.")
            row = {"id": case["id"], "cases_sha256": digest, "request_model": args.model,
                   "prediction": answer["choice"], "elapsed_s": round(seconds, 3), "response": raw}
            out.write(json.dumps(row, ensure_ascii=False) + "\n")
            out.flush()

if __name__ == "__main__":
    main()
