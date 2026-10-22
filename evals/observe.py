#!/usr/bin/env python3
"""Offline, explicitly annotated observations; never a model runner or grader.

Annotations identify visible trace evidence, not hidden reasoning. Review records
use Field Lab v2's existing receipt binding. No network or third-party imports.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import sys


SCHEMA = "soundings.observations.v1"
KINDS = {"capability.catalog", "acquisition.succeeded", "acquisition.failed",
         "content.delivered", "commitment", "artifact.changed", "feedback"}
JUDGMENTS = {"supported", "not-supported", "inconclusive"}


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def digest(path):
    # Used only to bind annotations/reviews to the exact bytes they assessed.
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def pointer_value(event, pointer):
    require(isinstance(pointer, str) and pointer.startswith("/"), "JSON pointer required")
    value = event
    for part in pointer[1:].split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        value = value[int(part)] if isinstance(value, list) else value[part]
    require(isinstance(value, str), "anchor must select visible text")
    return value


def tool_output(event, pointer):
    """Recognize only explicit completed Codex outputs, never command arguments."""
    item = event.get("item", {})
    if event.get("type") != "item.completed":
        return False
    if item.get("type") == "command_execution":
        return pointer == "/item/aggregated_output" and item.get("exit_code") == 0
    if item.get("type") == "mcp_tool_call":
        result = item.get("result")
        parts = pointer.split("/")
        if (item.get("status") != "completed" or item.get("error")
                or not isinstance(result, dict) or result.get("isError")
                or len(parts) != 6 or parts[1:4] != ["item", "result", "content"]
                or not parts[4].isdigit() or parts[5] != "text"):
            return False
        content = result.get("content")
        index = int(parts[4])
        return (isinstance(content, list) and index < len(content)
                and isinstance(content[index], dict) and content[index].get("type") == "text")
    return False


def timeline(trace_path, annotations_path):
    annotations = read_json(annotations_path)
    require(annotations.get("schema") == SCHEMA, "unsupported annotation schema")
    trace_hash = digest(trace_path)
    require(annotations.get("trace_sha256") == trace_hash, "trace binding mismatch")
    trace = [json.loads(line) for line in Path(trace_path).read_text(encoding="utf-8").splitlines()]
    require(all(isinstance(event, dict) for event in trace), "trace events must be objects")
    entries = annotations.get("events")
    require(isinstance(entries, list), "events must be an array")
    result, seen = [], set()
    for annotation in entries:
        kind, line = annotation.get("kind"), annotation.get("trace_line")
        require(kind in KINDS, "unsupported observation kind")
        require(type(line) is int and 1 <= line <= len(trace), "invalid trace line")
        pointer = annotation.get("pointer")
        key = (line, pointer, kind)
        require(key not in seen, "duplicate observation")
        seen.add(key)
        event = trace[line - 1]
        value = pointer_value(event, pointer)
        excerpt = annotation.get("excerpt")
        require(isinstance(excerpt, str) and excerpt and excerpt in value,
                "excerpt is absent from the anchored trace text")
        note = annotation.get("note")
        require(isinstance(note, str) and note.strip(), "annotation rationale required")
        if kind in {"content.delivered", "capability.catalog", "acquisition.succeeded"}:
            require(tool_output(event, pointer), "observation needs successful tool output, not a path or self-report")
        if kind == "content.delivered":
            require(annotation.get("representation") in {"verbatim", "extracted", "generated", "unknown"},
                    "delivery representation must be explicit")
        if kind == "artifact.changed":
            require(event.get("type") == "item.completed"
                    and event.get("item", {}).get("type") == "file_change"
                    and event["item"].get("status") == "completed",
                    "artifact change needs a completed file_change event")
        result.append({**annotation, "basis": "annotated-visible-evidence",
                       "anchored_output_bytes": len(value.encode("utf-8"))})
    result.sort(key=lambda entry: entry["trace_line"])
    commitments = [entry["trace_line"] for entry in result if entry["kind"] == "commitment"]
    first = min(commitments) if commitments else None
    delivered = [entry for entry in result if entry["kind"] == "content.delivered"]
    return {"schema": SCHEMA, "trace_sha256": trace_hash, "events": result,
            "first_annotated_commitment_line": first,
            "delivery_before_commitment": (None if first is None else
                any(entry["trace_line"] < first for entry in delivered)),
            "host_selection": "unknown", "content_application": "requires-semantic-review",
            "coverage": "selected annotations; absent events are unknown, not proof of absence"}


def receipt_requirements(receipt):
    require(receipt.get("schema_version") == 2, "Field Lab v2 receipt required")
    human = receipt.get("verification_summary", {}).get("human_review", {})
    requirements = human.get("requirements", [])
    require(isinstance(requirements, list)
            and all(isinstance(item, str) and item for item in requirements)
            and len(set(requirements)) == len(requirements), "invalid receipt requirements")
    require(human.get("required", bool(requirements)) is bool(requirements), "inconsistent review requirement flag")
    return requirements


def review_template(receipt_path):
    receipt = read_json(receipt_path)
    return {"receipt_sha256": digest(receipt_path), "status": "pending",
            "requirement_outcomes": {item: "inconclusive" for item in receipt_requirements(receipt)},
            "instructions": "Review sealed task artifacts and source conditions. Pass only requirement_outcomes to fieldlab review; this worksheet is not a completed review."}


def review_status(receipt_path, receipt, reviews):
    requirements = receipt_requirements(receipt)
    sha = digest(receipt_path)
    matching = []
    for review in reviews:
        binding = review.get("receipt", {})
        if binding.get("sha256") != sha:
            continue
        require(Path(binding.get("path", "")).resolve() == Path(receipt_path).resolve(),
                "review receipt path mismatch")
        require(review.get("schema_version") == 2 and review.get("method") == "human",
                "Field Lab v2 review required")
        require(review.get("independence") in {"implementer-run", "separate-agent", "external-reviewer"},
                "review independence required")
        require(isinstance(review.get("rationale"), str) and review["rationale"].strip(),
                "review rationale required")
        outcomes = review.get("requirement_outcomes", {})
        require(isinstance(outcomes, dict) and set(outcomes) == set(requirements)
                and all(value in JUDGMENTS for value in outcomes.values()),
                "review must cover the exact receipt requirements")
        judgment = review.get("judgment")
        require(judgment in JUDGMENTS, "invalid review judgment")
        if judgment == "supported":
            require(all(value == "supported" for value in outcomes.values()),
                    "supported judgment contradicts requirement outcomes")
        matching.append(judgment)
    require(len(matching) <= 1, "multiple reviews need adjudication before comparison")
    return matching[0] if matching else ("pending" if requirements else "not-required")


def compare(receipt_paths, review_paths):
    reviews = [read_json(path) for path in review_paths]
    rows, seen, bound_reviews, contents = [], set(), set(), set()
    for path in receipt_paths:
        sha = digest(path)
        require(sha not in seen, "duplicate receipt would double-count a run")
        seen.add(sha)
        receipt = read_json(path)
        normalized = json.dumps(receipt, sort_keys=True, ensure_ascii=False)
        require(normalized not in contents, "duplicate receipt content would double-count a run")
        contents.add(normalized)
        for key in ("lab_id", "case_id", "subject_id", "attempt_id"):
            require(isinstance(receipt.get(key), str) and receipt[key], f"attempt receipt needs {key}")
        require(receipt.get("receipt_type") == "attempt", "only attempt receipts are comparable here")
        semantic = review_status(path, receipt, reviews)
        bound_reviews.update(review["receipt"]["sha256"] for review in reviews
                             if review.get("receipt", {}).get("sha256") == sha)
        rows.append({"receipt_sha256": sha, "lab_id": receipt["lab_id"], "case_id": receipt["case_id"],
                     "run_id": receipt.get("run_id"),
                     "subject_id": receipt["subject_id"], "attempt_id": receipt["attempt_id"],
                     "execution_outcome": receipt.get("outcome", "unknown"),
                     "delivery": receipt.get("subject_delivery", {}).get("status", "unknown"),
                     "semantic_review": semantic,
                     "usage": receipt.get("verification_summary", {}).get("usage"),
                     "target_agent_invocations": receipt.get("target_agent_invocations")})
    require(all(review.get("receipt", {}).get("sha256") in bound_reviews for review in reviews),
            "unbound or stale review supplied")
    groups = defaultdict(list)
    for row in rows:
        groups[(row["lab_id"], row["case_id"], row["subject_id"])].append(row)
    tasks = [{"lab_id": lab, "case_id": case, "subject_id": subject,
              "repetitions": len(values),
              "execution_outcomes": [row["execution_outcome"] for row in values],
              "semantic_reviews": [row["semantic_review"] for row in values]}
             for (lab, case, subject), values in sorted(groups.items())]
    return {"schema": "soundings.comparison.v1", "attempts": rows, "task_groups": tasks,
            "analysis": "descriptive within task; repetitions are not independent projects; no causal or population estimate",
            "missingness": "No supplied receipt proves nothing about an unreported scheduled run. Reconcile with the pinned plan before analysis."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    time = sub.add_parser("timeline")
    time.add_argument("--trace", type=Path, required=True)
    time.add_argument("--annotations", type=Path, required=True)
    template = sub.add_parser("review-template")
    template.add_argument("--receipt", type=Path, required=True)
    summary = sub.add_parser("compare")
    summary.add_argument("--receipt", type=Path, action="append", required=True)
    summary.add_argument("--review", type=Path, action="append", default=[])
    args = parser.parse_args()
    try:
        if args.command == "timeline":
            result = timeline(args.trace, args.annotations)
        elif args.command == "review-template":
            result = review_template(args.receipt)
        else:
            result = compare(args.receipt, args.review)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, OSError, KeyError, IndexError, TypeError) as exc:
        print(f"observe: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
