"""Public synthetic execution-protocol stress test; no neural/biological model."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import random
from pathlib import Path

ARMS = ("raw", "physical", "start_only", "full_typed", "generic_matched")
SPLITS = {"dev": (128, 53170000), "eval": (1024, 94190000)}
STEPS = 16


def scenarios(split):
    count, base_seed = SPLITS[split]
    for number in range(count):
        rng = random.Random(base_seed + number)
        events = []
        for tick in range(STEPS):
            obj = rng.choice(("A", "B"))
            kind = rng.choices(("move", "recover", "complete", "wait"), (6, 2, 2, 1))[0]
            action = {"kind": kind, "object": obj, "dx": rng.choice((0.1, 0.15))}
            if kind == "recover":
                action["dx"] = -action["dx"]
            plan = {"permission": rng.choices(("GRANTED", "DENIED", "UNKNOWN"), (6, 2, 2))[0],
                    "permit_object": rng.choices((obj, "B" if obj == "A" else "A", "UNKNOWN"), (7, 2, 1))[0],
                    "fresh": rng.random() > 0.15, "recovery": rng.choice(("RECOVERY_ONLY", "UNKNOWN", "DENIED")),
                    "recovery_object": rng.choice((obj, "A", "B")), "version": tick * 2}
            latest = dict(plan)
            if rng.random() < 0.4:
                latest["permission"] = rng.choice(("GRANTED", "DENIED", "UNKNOWN"))
                latest["permit_object"] = rng.choice(("A", "B", "UNKNOWN"))
                latest["version"] += 1
            if rng.random() < 0.2:
                latest["fresh"] = not latest["fresh"]
            if rng.random() < 0.2:
                latest["recovery"] = rng.choice(("RECOVERY_ONLY", "DENIED", "UNKNOWN"))
            # An identical clean prefix provides actual, reachable legal progress.
            # It is a deliberately constructed anchor, not independent natural data.
            if tick < 3:
                action = {"kind": "move" if tick < 2 else "complete", "object": "A", "dx": 0.15}
                plan.update(permission="GRANTED", permit_object="A", fresh=True)
                latest = dict(plan)
            events.append({"tick": tick, "action": action, "decision": plan, "execution": latest})
        yield {"id": number, "seed": base_seed + number,
               "initial": {"A": rng.choice((0.7, 0.75, 0.8)), "B": rng.choice((0.0, 0.2))}, "events": events}


def guard(action, facts, positions):
    """Executable contract, independently implemented from the scoring oracle."""
    kind, obj = action["kind"], action["object"]
    if kind == "wait":
        return True
    if kind == "complete":
        return positions[obj] >= 1.0 - 1e-9
    dx = action["dx"]
    if not facts["fresh"] or not 0 <= positions[obj] + dx <= 1.2:
        return False
    if kind == "recover":
        return (facts["recovery"] == "RECOVERY_ONLY" and facts["recovery_object"] == obj
                and -0.15 <= dx < 0 and positions[obj] > 0)
    return (kind == "move" and 0 < dx <= 0.15 and facts["permission"] == "GRANTED"
            and facts["permit_object"] == obj)


def oracle(action, facts, positions):
    """Judge the proposed/executed action using latest facts and true position.

    This does not call guard(), inspect an arm, or read an execution reason.
    It is an independent implementation of the same documented finite contract,
    not independent human annotation or an independent normative justification.
    """
    obj, kind = action["object"], action["kind"]
    errors = []
    if kind == "wait":
        return errors
    if kind == "complete":
        return ["false_completion"] if positions[obj] < 1.0 - 1e-9 else []
    if positions[obj] + action["dx"] < 0 or positions[obj] + action["dx"] > 1.2:
        errors.append("physical_bounds")
    if not facts["fresh"]:
        errors.append("expired_evidence")
    if kind == "recover":
        if facts["recovery"] != "RECOVERY_ONLY" or facts["recovery_object"] != obj:
            errors.append("recovery_authority")
        if not -0.15 <= action["dx"] < 0 or positions[obj] <= 0:
            errors.append("recovery_direction_or_bound")
    else:
        if facts["permission"] != "GRANTED":
            errors.append("task_permission")
        if facts["permit_object"] != obj:
            errors.append("object_scope")
        if not 0 < action["dx"] <= 0.15:
            errors.append("task_direction_or_bound")
    return errors


def step(arm, positions, event):
    action, plan, latest = event["action"], event["decision"], event["execution"]
    kind, obj = action["kind"], action["object"]
    admitted = True
    if arm in ("start_only", "full_typed", "generic_matched"):
        admitted = guard(action, plan, positions)
    if admitted and arm in ("full_typed", "generic_matched"):
        admitted = guard(action, latest, positions)
        # Re-evaluate current facts; a version change alone is not authority.
    if arm != "raw" and kind in ("move", "recover"):
        admitted = admitted and 0 <= positions[obj] + action["dx"] <= 1.2
    proposal_errors = oracle(action, latest, positions)
    after = dict(positions)
    executed = admitted and kind != "wait"
    if executed and kind in ("move", "recover"):
        after[obj] += action["dx"]
    return after, {"executed": executed, "proposal_errors": proposal_errors,
                   "execution_errors": proposal_errors if executed else [],
                   "legal_opportunity": kind != "wait" and not proposal_errors,
                   "false_block": kind != "wait" and not proposal_errors and not executed}


def run_scenario(scenario, arm):
    positions, trace = dict(scenario["initial"]), []
    counts = {key: 0 for key in ("nonwait_proposals", "unsafe_proposals", "executed_actions",
                               "execution_violations", "legal_opportunities", "legal_executed", "false_blocks")}
    error_counts = {}
    for event in scenario["events"]:
        after, outcome = step(arm, positions, event)
        counts["nonwait_proposals"] += event["action"]["kind"] != "wait"
        counts["unsafe_proposals"] += bool(outcome["proposal_errors"])
        counts["executed_actions"] += outcome["executed"]
        counts["execution_violations"] += bool(outcome["execution_errors"])
        counts["legal_opportunities"] += outcome["legal_opportunity"]
        counts["legal_executed"] += outcome["legal_opportunity"] and outcome["executed"]
        counts["false_blocks"] += outcome["false_block"]
        for error in outcome["execution_errors"]:
            error_counts[error] = error_counts.get(error, 0) + 1
        trace.append({**event, "before": positions, "after": after, **outcome})
        positions = after
    return {"scenario": scenario["id"], "seed": scenario["seed"], "arm": arm,
            **counts, "violation_categories": error_counts, "final_positions": positions}, trace


def evaluate(split):
    summaries, failures, total = [], [], {}
    input_hash = hashlib.sha256()
    retained = {arm: 0 for arm in ARMS}
    for scenario in scenarios(split):
        input_hash.update(json.dumps(scenario, sort_keys=True).encode())
        matched = []
        for arm in ARMS:
            summary, trace = run_scenario(scenario, arm)
            summaries.append(summary)
            counts = total.setdefault(arm, {key: 0 for key, value in summary.items()
                                           if isinstance(value, int) and key not in ("scenario", "seed")})
            for key in counts:
                counts[key] += summary[key]
            if summary["execution_violations"] and retained[arm] < 3:
                failures.append({"scenario": scenario["id"], "arm": arm, "trace": trace})
                retained[arm] += 1
            if arm in ("full_typed", "generic_matched"):
                matched.append(trace)
        assert matched[0] == matched[1], "Content-matched governance arms diverged"
    for counts in total.values():
        counts["legal_execution_rate"] = counts["legal_executed"] / counts["legal_opportunities"]
    return {"summary": total, "scenario_summaries": summaries, "failure_traces": failures,
            "inputs_sha256": input_hash.hexdigest()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", choices=SPLITS, required=True)
    parser.add_argument("--output", type=Path, required=True, help="New output directory; never overwritten")
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("Choose a new --output directory; historical runs are immutable")
    result = evaluate(args.split)
    result["metadata"] = {"split": args.split, "scenario_count": SPLITS[args.split][0],
        "seed_start": SPLITS[args.split][1], "seed_stop_exclusive": SPLITS[args.split][1] + SPLITS[args.split][0],
        "steps": STEPS, "arms": ARMS, "configuration": {"splits": SPLITS, "steps": STEPS},
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "scope": "public synthetic interface test; no neural model or biological behavior",
        "contract": "typed PoL2 operationalization; generic_matched shares identical executable rules",
        "false_block_definition": "nonwait proposal legal at execution facts but not executed; includes decision/execution information changes",
        "limits": "one generator with constructed clean prefix; oracle shares normative contract, separately implemented; no independent labels or population inference"}
    args.output.mkdir(parents=True)
    (args.output / "results.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    rows = [{"arm": arm, **counts} for arm, counts in result["summary"].items()]
    with (args.output / "summary.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({"metadata": result["metadata"], "summary": result["summary"]}, indent=2))


if __name__ == "__main__":
    main()
