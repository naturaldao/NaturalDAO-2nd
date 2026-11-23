# /// script
# dependencies = ["jsonschema[format]==4.26.0"]
# ///
"""Replay saved EVAL-05 responses into two independent blind review packets."""

import argparse
import json
from collections import Counter
from pathlib import Path
from random import SystemRandom
from shutil import rmtree
from uuid import uuid4

from validate import check_bundle, load_validators, read_records


def write_jsonl(path, rows):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")


def prepare_packets(records):
    scenarios = records["scenario"]
    packets = []
    mapping = []
    statuses = Counter()
    for _, response in records["response"].values():
        status = response["execution_status"]
        statuses[status] += 1
        if status != "ok":
            continue
        scenario = scenarios[(response["scenario_id"],)][1]
        blind_id = uuid4().hex
        packet = {
            "blind_response_id": blind_id,
            "user_prompt": scenario["user_prompt"],
            "conversation_context": scenario["conversation_context"],
            "response_text": response["response_text"],
        }
        if "messages" in scenario:
            packet["messages"] = [
                {"role": message["role"], "content": message["content"]}
                for message in scenario["messages"]
            ]
        packets.append(packet)
        mapping.append({
            "blind_response_id": blind_id,
            "response_id": response["response_id"],
        })
    return packets, mapping, dict(statuses)


def export(output, packets, mapping, statuses):
    output.mkdir(mode=0o700)
    try:
        for name in ("reviewer-a", "reviewer-b"):
            reviewer = output / name
            reviewer.mkdir(mode=0o700)
            ordered = packets.copy()
            SystemRandom().shuffle(ordered)
            write_jsonl(reviewer / "inputs.jsonl", ordered)

        coordinator = output / "coordinator"
        coordinator.mkdir(mode=0o700)
        write_jsonl(coordinator / "blind-map.jsonl", mapping)
        metrics = {"exported": len(packets), "execution_status": statuses}
        with (coordinator / "summary.json").open("x", encoding="utf-8") as stream:
            json.dump(metrics, stream, indent=2)
            stream.write("\n")
    except BaseException:
        rmtree(output, ignore_errors=True)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("jsonl", nargs="+", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    errors = []
    records = read_records(args.jsonl, load_validators(), errors)
    check_bundle(records, errors)
    if errors:
        parser.exit(1, "\n".join(errors) + "\n")

    packets, mapping, statuses = prepare_packets(records)
    if not packets:
        parser.exit(1, "No successful responses to export.\n")
    try:
        export(args.out, packets, mapping, statuses)
    except OSError as exc:
        parser.exit(1, f"Cannot export blind packets: {exc}\n")
    print(json.dumps({"exported": len(packets), "execution_status": statuses}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
