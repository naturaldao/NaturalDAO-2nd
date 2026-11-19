"""Run local Ollama direct judgments or constrained evidence extraction; no external services."""
import argparse
import hashlib
import json
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MODEL = "llama3.1:8b"
OPTIONS = {"seed": 42, "temperature": 0, "num_ctx": 2048, "num_predict": 160}
SYSTEM = {
    "direct": "Apply only the policy in the supplied case. Report one allowed label in JSON.",
    "extract": "Encode explicitly observed facts using only the candidate atoms. Match the exact subject. "
               "Exclude requests, proposals, absent evidence and inferred conclusions. "
               "Include supported candidate atoms even about other subjects. Return a JSON object with the facts list."
}

def request(base, path, data=None):
    payload = None if data is None else json.dumps(data).encode()
    req = urllib.request.Request(base + path, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=240) as response:
        return json.load(response)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="http://127.0.0.1:11434")
    parser.add_argument("--model", default=MODEL)
    parser.add_argument("--record-only", action="store_true", help="Diagnostic: give the extractor only the record, without policy.")
    args = parser.parse_args()
    cases = json.loads((ROOT/"cases.json").read_text())
    tags = request(args.base, "/api/tags")
    model_info = next(x for x in tags["models"] if x["name"] == args.model)
    metadata = dict(ollama=request(args.base, "/api/version"), model=model_info,
                    options=OPTIONS, cases_sha256=hashlib.sha256((ROOT/"cases.json").read_bytes()).hexdigest())
    prefix = "record_only_" if args.record_only else ""
    (ROOT/(prefix+"llm_meta.json")).write_text(json.dumps(metadata, indent=2)+"\n")
    extracted = []
    with (ROOT/(prefix+"llm_raw.jsonl")).open("w", encoding="utf-8") as out:
        for mode in (["extract"] if args.record_only else SYSTEM):
            for c in cases:
                if mode == "direct":
                    field = "label"
                    value_schema = {"type":"string", "enum":c["labels"]}
                    choices = c["labels"]
                else:
                    field = "facts"
                    value_schema = {"type":"array", "items":{"type":"string","enum":c["vocabulary"]}}
                    choices = c["vocabulary"]
                visible = c["text"].split("\nRecord: ", 1)[1] if args.record_only else c["text"]
                prompt = visible + "\nAllowed " + field + ": " + json.dumps(choices)
                schema = {"type":"object","properties":{field:value_schema},"required":[field],"additionalProperties":False}
                body = dict(model=args.model, messages=[{"role":"system","content":SYSTEM[mode]},
                            {"role":"user","content":prompt}], format=schema, options=OPTIONS, stream=False, keep_alive="5m")
                record = dict(id=c["id"],mode=mode,request=body)
                start = time.perf_counter()
                try:
                    raw = request(args.base, "/api/chat", body)
                    record["response"] = raw
                    if raw.get("done_reason") != "stop":
                        raise ValueError("incomplete generation")
                    answer = json.loads(raw["message"]["content"])[field]
                    if mode == "direct" and answer not in choices:
                        raise ValueError("invalid label")
                    if mode == "extract":
                        if not isinstance(answer, list) or any(x not in choices for x in answer):
                            raise ValueError("invalid facts")
                        facts = sorted(set(answer))
                        extracted.append(dict(c, facts=facts, knowledge="\n".join(c["rules"]+[x+"." for x in facts])))
                    record["answer"] = answer
                except (ValueError, KeyError, OSError) as exc:
                    record["error"] = str(exc)
                record["elapsed_ms"] = round(1000*(time.perf_counter()-start),2)
                out.write(json.dumps(record)+"\n")
                out.flush()
    (ROOT/(prefix+"extracted_cases.json")).write_text(json.dumps(extracted, indent=2)+"\n", encoding="utf-8", newline="\r\n")

if __name__ == "__main__":
    main()
