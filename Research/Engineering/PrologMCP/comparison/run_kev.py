"""Run the NaturalDAO M10 seed-43 typed-choice checkpoint against cases.json.

Requires kev at 2074cc44256200bb37540103fa4572901faa10f3, the released
adapter and head, and Qwen/Qwen3.5-4B-Base at revision
1001bb4d826a52d1f399e183466143f4da7b741b in the Hugging Face cache.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import time

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--cases", type=Path, default=Path(__file__).with_name("cases.json"))
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("kev-m10.json"))
    parser.add_argument("--threads", type=int, default=6)
    args = parser.parse_args()
    import torch
    from kev.api import SystemOneRequest, to_record
    from kev.checkpoint import Checkpoint, LoadOptions

    torch.set_num_threads(args.threads)
    torch.manual_seed(0)
    from huggingface_hub import snapshot_download
    base = "Qwen/Qwen3.5-4B-Base"
    revision = "1001bb4d826a52d1f399e183466143f4da7b741b"
    snapshot = Path(snapshot_download(base, revision=revision, local_files_only=True))
    # The released head specifies no base revision. Verify HF's local main
    # resolves to the exact pinned snapshot before loading the original head.
    assert Path(snapshot_download(base, revision="main", local_files_only=True)).resolve() == snapshot.resolve()
    os.environ["HF_HUB_OFFLINE"] = "1"
    checkpoint = Checkpoint(str(args.checkpoint.resolve()))
    assert checkpoint.meta.base == base
    tok, model = checkpoint.load("cpu", LoadOptions(dtype=torch.bfloat16))
    model.eval()
    spec = json.loads(args.cases.read_text(encoding="utf-8-sig"))
    cases = spec if isinstance(spec, list) else spec["cases"]
    record = {"model": "NaturalDAO Kev PoL2 score-v2 M10 seed-43", "base": base,
              "base_revision": revision, "dtype": "bfloat16", "device": "cpu",
              "torch": torch.__version__, "threads": args.threads,
              "weights_sha256": {f: sha256(args.checkpoint / f) for f in ["head.pt", "adapter_model.safetensors"]},
              "cases_sha256": sha256(args.cases), "results": []}
    for case in cases:
        req = SystemOneRequest(state=case["text"], questions={"decision": {
            "type": "choice", "instructions": "Select the answer to the question in the state.",
            "criteria": {label: None for label in case["labels"]}}})
        encoded, meta = to_record(req)
        start = time.perf_counter()
        with torch.inference_mode():
            enc = model.encode(tok, encoded, max_state=4096, max_branch=4096, strict=True)
            logits = model.forward(enc)[0].float().cpu()
            probs = torch.softmax(logits, -1).tolist()
        keys = meta[0]["keys"]
        assert torch.isfinite(logits).all() and abs(sum(probs) - 1) < 1e-5
        row = {"id": case["id"], "prediction": keys[logits.argmax().item()],
               "probabilities": dict(zip(keys, probs)), "logits": dict(zip(keys, logits.tolist())),
               "tokens": len(enc["ids"]), "elapsed_s": round(time.perf_counter() - start, 3)}
        record["results"].append(row)
        print(row["id"], row["prediction"], row["elapsed_s"], flush=True)
    args.output.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()
