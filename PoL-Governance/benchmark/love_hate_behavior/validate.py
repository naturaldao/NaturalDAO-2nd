# /// script
# dependencies = ["jsonschema[format]==4.26.0"]
# ///
"""Validate a self-contained EVAL-05 v0.2 JSONL bundle offline."""

import argparse
import json
from functools import partial
from pathlib import Path

from jsonschema import Draft202012Validator


SCHEMA = Path(__file__).with_name("schema.v0.2.json")
ID_FIELDS = {
    "scenario": ("scenario_id",),
    "response": ("response_id",),
    "annotation": ("annotation_id",),
    "engine_assessment": ("response_id", "engine_run_id"),
    "adjudication": ("response_id", "adjudicator_id"),
}


def strict_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON object key")
        result[key] = value
    return result


def reject_constant(_value):
    raise ValueError("non-finite JSON constant")


def read_records(paths, validators, errors):
    records = {kind: {} for kind in ID_FIELDS}
    for path in paths:
        try:
            with path.open(encoding="utf-8") as stream:
                for line_number, line in enumerate(stream, 1):
                    location = f"{path}:{line_number}"
                    try:
                        row = json.loads(line, object_pairs_hook=strict_object,
                                         parse_constant=reject_constant)
                    except ValueError as exc:
                        errors.append(f"{location}: invalid JSON ({exc})")
                        continue
                    kind = row.get("record_type") if isinstance(row, dict) else None
                    if not isinstance(kind, str) or kind not in validators:
                        errors.append(f"{location}: unknown or missing record_type")
                        continue
                    violations = list(validators[kind].iter_errors(row))
                    if violations:
                        for violation in violations:
                            field = ".".join(map(str, violation.absolute_path)) or "<record>"
                            errors.append(f"{location}: {field}: schema check failed ({violation.validator})")
                        continue
                    key = tuple(row[field] for field in ID_FIELDS[kind])
                    if key in records[kind]:
                        previous, _ = records[kind][key]
                        errors.append(f"{location}: duplicate {kind} identity (first at {previous})")
                        continue
                    records[kind][key] = (location, row)
        except (OSError, UnicodeError) as exc:
            errors.append(f"{path}: {exc}")
    return records


def check_evidence(row, response, scenario, report):
    spans = [(f"evidence_spans[{i}]", span)
             for i, span in enumerate(row["evidence_spans"])]
    fact_ids = set()
    for i, fact in enumerate(row["facts"]):
        if fact["fact_id"] in fact_ids:
            report(f"facts[{i}].fact_id: duplicate fact identity")
        fact_ids.add(fact["fact_id"])
        spans.extend((f"facts[{i}].evidence_spans[{j}]", span)
                     for j, span in enumerate(fact["evidence_spans"]))

    for field, span in spans:
        if span["source"] == "response":
            text = response["response_text"]
        else:
            context = scenario["conversation_context"]
            index = span["message_index"]
            if index >= len(context):
                report(f"{field}: message_index outside conversation_context")
                continue
            text = context[index]
        start, end = span["start_char"], span["end_char"]
        if text is None or not 0 <= start < end <= len(text):
            report(f"{field}: invalid Unicode code point range")
        elif text[start:end] != span["quote"]:
            report(f"{field}: quote differs from source text")


def add_error(errors, location, message):
    errors.append(f"{location}: {message}")


def check_bundle(records, errors):
    splits = {"family_id": {}, "pair_id": {}}
    for location, scenario in records["scenario"].values():
        for field, split_by_id in splits.items():
            identity = scenario[field]
            if identity is None:
                continue
            first_split, first_location = split_by_id.setdefault(
                identity, (scenario["split"], location))
            if first_split != scenario["split"]:
                errors.append(f"{location}: {field} crosses splits (first at {first_location})")

    scenarios = records["scenario"]
    responses = records["response"]
    for location, row in responses.values():
        if (row["scenario_id"],) not in scenarios:
            errors.append(f"{location}: response references missing scenario")

    annotation_ids = set(records["annotation"])
    for kind in ("annotation", "engine_assessment", "adjudication"):
        for location, row in records[kind].values():
            report = partial(add_error, errors, location)

            response_entry = responses.get((row["response_id"],))
            if response_entry is None:
                report(f"{kind} references missing response")
                continue
            _, response = response_entry
            if response["execution_status"] != "ok":
                report(f"{kind} references failed response")
                continue
            scenario_entry = scenarios.get((response["scenario_id"],))
            if scenario_entry is None:
                continue
            _, scenario = scenario_entry
            evidence_record = row
            if kind == "adjudication":
                evidence_record = row["resolved_annotation"]
                identity = (evidence_record["annotation_id"],)
                if identity in annotation_ids:
                    report("resolved_annotation.annotation_id duplicates an annotation identity")
                annotation_ids.add(identity)
                if evidence_record["response_id"] != row["response_id"]:
                    report("resolved_annotation references a different response")
                annotators = set()
                for annotation_id in row["source_annotation_ids"]:
                    source = records["annotation"].get((annotation_id,))
                    if source is None or source[1]["response_id"] != row["response_id"]:
                        report("source annotation missing or references a different response")
                        continue
                    annotators.add(source[1]["annotator_id"])
                if len(annotators) < 2:
                    report("adjudication requires at least two distinct source annotators")
                if row["adjudicator_id"] in annotators:
                    report("adjudicator also supplied a source annotation")
            actions = evidence_record.get("response_actions", [])
            if "none" in actions and len(actions) > 1:
                report("response_actions: none must appear alone")
            check_evidence(evidence_record, response, scenario, report)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("jsonl", nargs="+", type=Path)
    args = parser.parse_args()
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validators = {
        kind: Draft202012Validator(
            {"$ref": f"#/$defs/{kind}", "$defs": schema["$defs"]},
            format_checker=Draft202012Validator.FORMAT_CHECKER,
        )
        for kind in ID_FIELDS
    }
    errors = []
    records = read_records(args.jsonl, validators, errors)
    check_bundle(records, errors)
    counts = {kind: len(rows) for kind, rows in records.items()}
    if not sum(counts.values()) and not errors:
        errors.append("bundle contains no records")
    print(json.dumps({"valid": not errors, "counts": counts, "errors": errors},
                     ensure_ascii=False, indent=2))
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
