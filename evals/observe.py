#!/usr/bin/env python3
"""Offline, explicitly annotated observations; never a model runner or grader.

Annotations identify visible trace evidence, not hidden reasoning. Review records
use Field Lab v2's existing receipt binding. No network or third-party imports.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys


SCHEMA = "soundings.observations.v2"
KINDS = {"capability.catalog", "acquisition.succeeded", "acquisition.failed",
         "content.delivered", "commitment", "artifact.changed", "feedback"}


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


def timeline(trace_path, annotations_path, host_context_path=None):
    annotations = read_json(annotations_path)
    require(isinstance(annotations, dict) and annotations.get('schema') == SCHEMA,
            'unsupported annotation schema; migrate v1 annotations to v2')
    trace_hash = digest(trace_path)
    require(annotations.get('trace_sha256') == trace_hash, 'trace binding mismatch')
    trace = [json.loads(line) for line in Path(trace_path).read_text(encoding='utf-8').splitlines()]
    require(all(isinstance(event, dict) for event in trace), 'trace events must be objects')
    host = []
    if host_context_path is not None:
        require(annotations.get('host_context_sha256') == digest(host_context_path),
                'host context binding mismatch')
        host = [json.loads(line) for line in Path(host_context_path).read_text(encoding='utf-8').splitlines()]
        require(all(isinstance(event, dict) and isinstance(event.get('text'), str) for event in host),
                'host context must contain explicit text records')
    else:
        require(not annotations.get('host_context_sha256'), 'bound host context file required')
    decisions = annotations.get('decisions')
    require(isinstance(decisions, list), 'decisions must be an array')
    decision_map = {}
    for decision in decisions:
        require(isinstance(decision, dict), 'decision must be an object')
        identity, question = decision.get('decision_id'), decision.get('question')
        require(isinstance(identity, str) and identity and identity not in decision_map,
                'unique nonempty decision_id required')
        require(isinstance(question, str) and question.strip(), 'concrete decision question required')
        decision_map[identity] = decision
    entries = annotations.get('events')
    require(isinstance(entries, list), 'events must be an array')
    roles = {'skill_guidance', 'task_input', 'search_summary', 'source_body', 'interpretation', 'unknown'}
    origins = {'fixed_corpus', 'live_external', 'supplied', 'unknown'}
    result, seen = [], set()
    for annotation in entries:
        require(isinstance(annotation, dict), 'event annotation must be an object')
        kind, line = annotation.get('kind'), annotation.get('line')
        stream = annotation.get('stream', 'trace')
        require(kind in KINDS and stream in {'trace', 'host_context'}, 'unsupported observation kind/stream')
        records = trace if stream == 'trace' else host
        require(type(line) is int and 1 <= line <= len(records), 'invalid stream line')
        pointer = annotation.get('pointer')
        key = (stream, line, pointer, kind)
        require(key not in seen, 'duplicate observation')
        seen.add(key)
        event = records[line - 1]
        value = pointer_value(event, pointer)
        excerpt, note = annotation.get('excerpt'), annotation.get('note')
        require(isinstance(excerpt, str) and excerpt and excerpt in value,
                'excerpt is absent from the anchored text')
        require(isinstance(note, str) and note.strip(), 'annotation rationale required')
        if stream == 'trace' and kind in {'content.delivered', 'capability.catalog', 'acquisition.succeeded'}:
            require(tool_output(event, pointer), 'observation needs successful tool output, not a path or self-report')
        if stream == 'host_context':
            require(kind in {'content.delivered', 'capability.catalog', 'feedback'} and pointer == '/text',
                    'host sidecar supports only explicit recorded content/catalog/feedback text')
        if kind == 'content.delivered':
            require(annotation.get('representation') in {'verbatim', 'extracted', 'generated', 'unknown'},
                    'delivery representation must be explicit')
            require(annotation.get('role') in roles and annotation.get('origin') in origins,
                    'content role and origin must be explicit')
            require(annotation.get('completeness') in {'full', 'excerpt', 'unknown'},
                    'content completeness must be explicit')
            require(isinstance(annotation.get('source_id'), str) and annotation['source_id'],
                    'content source identity required (a label, not provenance authentication)')
        if kind == 'commitment':
            require(annotation.get('decision_id') in decision_map, 'commitment needs declared decision_id')
        if kind == 'artifact.changed':
            require(stream == 'trace' and event.get('type') == 'item.completed'
                    and event.get('item', {}).get('type') == 'file_change'
                    and event['item'].get('status') == 'completed', 'artifact change needs completed file_change')
        relations = annotation.get('relations', [])
        require(isinstance(relations, list), 'relations must be an array')
        for relation in relations:
            require(isinstance(relation, dict) and relation.get('decision_id') in decision_map,
                    'relation needs declared decision_id')
            require(relation.get('relevance') in {'supports', 'refutes', 'irrelevant', 'unknown'},
                    'explicit evidence relevance required')
            require(isinstance(relation.get('note'), str) and relation['note'].strip(),
                    'evidence relation rationale required')
        position = line if stream == 'trace' else event.get('before_trace_line')
        require(position is None or (type(position) is int and 1 <= position <= len(trace) + 1),
                'invalid recorded host position')
        observed = {**annotation, 'stream': stream,
                       'basis': 'annotated-visible-evidence' if stream == 'trace' else 'recorded-host-context',
                       'anchored_output_bytes': len(value.encode('utf-8')),
                       'position': [position, 0 if stream == 'trace' else -1] if position is not None else None}
        if kind == 'content.delivered':
            observed['content_sha256'] = hashlib.sha256(value.encode('utf-8')).hexdigest()
        result.append(observed)
    coverage = annotations.get('coverage', [])
    require(isinstance(coverage, list), 'coverage must be an array')
    coverage_map = {}
    for item in coverage:
        identity = item.get('decision_id')
        require(identity in decision_map and identity not in coverage_map, 'coverage needs unique decision_id')
        require(item.get('delivery_annotations') in {'complete', 'partial', 'unknown'}
                and item.get('host_context') in {'complete', 'partial', 'unknown'}, 'explicit coverage scope required')
        intervals = item.get('trace_ranges', [])
        require(isinstance(intervals, list), 'trace coverage ranges required')
        last = 0
        for interval in intervals:
            require(isinstance(interval, list) and len(interval) == 2
                    and all(type(x) is int for x in interval)
                    and last < interval[0] <= interval[1] <= len(trace), 'coverage ranges must be valid, sorted and disjoint')
            last = interval[1]
        coverage_map[identity] = item
    outputs = []
    for identity, definition in decision_map.items():
        commits = [entry for entry in result if entry['kind'] == 'commitment' and entry.get('decision_id') == identity]
        positions = [entry['position'] for entry in commits if entry['position'] is not None]
        first = min(positions) if positions else None
        scope = coverage_map.get(identity, {})
        # A negative result requires coverage of every trace record before and
        # including the selected commitment, complete host coverage, and explicit
        # delivery annotation coverage. These are annotator claims, not sensors.
        covered = set()
        for begin, end in scope.get('trace_ranges', []):
            covered.update(range(begin, end + 1))
        fully_reviewed = (first is not None and set(range(1, first[0] + 1)) <= covered
                          and scope.get('delivery_annotations') == 'complete'
                          and scope.get('host_context') == 'complete')
        sources = [entry for entry in result if entry['kind'] == 'content.delivered' and entry['role'] == 'source_body']
        def status(external_only):
            yes, uncertain = False, first is None
            for entry in result:
                if entry['kind'] == 'content.delivered' and entry['role'] == 'unknown':
                    if first is None or entry['position'] is None or entry['position'] <= first:
                        uncertain = True
            for entry in sources:
                relationships = [relation for relation in entry.get('relations', []) if relation['decision_id'] == identity]
                if not relationships:
                    uncertain = True
                    continue
                relevant = any(relation['relevance'] in {'supports', 'refutes'} for relation in relationships)
                unknown = any(relation['relevance'] == 'unknown' for relation in relationships)
                if external_only and entry['origin'] not in {'fixed_corpus', 'live_external'}:
                    uncertain |= relevant and entry['origin'] == 'unknown'
                    continue
                position = entry['position']
                if unknown and (first is None or position is None or position <= first):
                    uncertain = True
                if relevant and first is not None and position is not None and position < first:
                    yes = True
                elif (relevant or unknown) and (first is None or position is None or position == first):
                    uncertain = True
            if yes:
                return 'yes'
            return 'no' if fully_reviewed and not uncertain else 'unknown'
        outputs.append({'decision_id': identity, 'question': definition['question'],
                        'first_annotated_commitment_position': first,
                        'relevant_source_body_before_commitment': status(False),
                        'external_source_body_before_commitment': status(True),
                        'negative_coverage_sufficient': fully_reviewed,
                        'coverage': scope or 'unknown'})
    return {'schema': SCHEMA, 'trace_sha256': trace_hash,
            'host_context_sha256': digest(host_context_path) if host_context_path is not None else None,
            'events': result, 'decisions': outputs,
            'host_selection': 'unknown', 'content_application': 'requires-semantic-review',
            'coverage_basis': 'explicit annotator scope; no automatic completeness or absence inference'}


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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    time = sub.add_parser("timeline")
    time.add_argument("--trace", type=Path, required=True)
    time.add_argument("--annotations", type=Path, required=True)
    time.add_argument("--host-context", type=Path)
    template = sub.add_parser("review-template")
    template.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "timeline":
            result = timeline(args.trace, args.annotations, args.host_context)
        else:
            result = review_template(args.receipt)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, OSError, KeyError, IndexError, TypeError) as exc:
        print(f"observe: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
