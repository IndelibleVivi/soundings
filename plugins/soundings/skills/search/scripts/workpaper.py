#!/usr/bin/env python3
"""Inspect, render, and trace an authored evidence-linked workpaper.

The workpaper is an optional task artifact. It records authored interpretation
and declared links to evidence.v1 snapshots; it does not observe reads, infer
semantic relationships, approve findings, or execute project actions.
"""

from __future__ import annotations

import argparse
from collections import defaultdict, deque
import html
import json
import os
from pathlib import Path
import re
import sys
import tempfile

import evidence


SCHEMA = "soundings.workpaper.v1"
KINDS = ("observation", "inference", "proposal", "judgment")
STATUSES = ("current", "superseded")
RELATIONS = ("supports", "challenges", "context")
FINDING_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
RECORD_KEYS = {"schema", "outcome", "question", "findings", "open_questions"}
RECORD_REQUIRED = {"schema", "outcome", "question", "findings"}
FINDING_KEYS = {"id", "kind", "text", "status", "conditions", "evidence", "depends_on"}
FINDING_CONTENT_FIELDS = ("kind", "text", "status", "conditions", "evidence", "depends_on")
EVIDENCE_KEYS = {"ref", "start_line", "end_line", "relation", "note"}
EVIDENCE_REQUIRED = {"ref", "start_line", "end_line", "relation"}
SNAPSHOT_CONTENT_FIELDS = (
    "source",
    "title",
    "representation",
    "captured_at",
    "content",
)


class WorkpaperError(evidence.EvidenceError):
    """The workpaper or a requested operation violates its declared contract."""


def _object(value, where: str, required: set[str], allowed: set[str]) -> dict:
    if not isinstance(value, dict):
        raise WorkpaperError(f"{where} must be a JSON object")
    missing = sorted(required - value.keys())
    if missing:
        raise WorkpaperError(f"{where} is missing required fields: {', '.join(missing)}")
    unknown = sorted(value.keys() - allowed)
    if unknown:
        raise WorkpaperError(f"{where} has unsupported fields: {', '.join(unknown)}")
    return value


def _string(value, where: str, *, nonempty: bool = True) -> str:
    if type(value) is not str:
        raise WorkpaperError(f"{where} must be a string")
    if nonempty and not value.strip():
        raise WorkpaperError(f"{where} must not be empty")
    return value


def _string_list(value, where: str) -> list[str]:
    if type(value) is not list:
        raise WorkpaperError(f"{where} must be an array of strings")
    result = []
    for index, item in enumerate(value):
        result.append(_string(item, f"{where}[{index}]"))
    return result


def _line_number(value, where: str) -> int:
    if type(value) is not int:
        raise WorkpaperError(f"{where} must be an integer, not a boolean or string")
    if value < 1:
        raise WorkpaperError(f"{where} must be a positive integer")
    return value


def _load_json(path: Path) -> dict:
    try:
        with path.open(encoding="utf-8", newline="") as stream:
            value = json.load(stream)
    except FileNotFoundError as exc:
        raise WorkpaperError(f"workpaper not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise WorkpaperError(
            f"workpaper is not valid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc
    except OSError as exc:
        raise WorkpaperError(f"cannot read workpaper {path}: {exc}") from exc
    return _object(value, "workpaper", RECORD_REQUIRED, RECORD_KEYS)


def _validate_dependencies(findings: list[dict], by_id: dict[str, dict]) -> None:
    for finding in findings:
        seen: set[str] = set()
        for dependency in finding["depends_on"]:
            if dependency not in by_id:
                raise WorkpaperError(
                    f"finding {finding['id']} depends on unknown finding {dependency}"
                )
            if dependency in seen:
                raise WorkpaperError(
                    f"finding {finding['id']} declares duplicate dependency {dependency}"
                )
            seen.add(dependency)

    colors: dict[str, int] = {}
    for finding in findings:
        root = finding["id"]
        if colors.get(root, 0):
            continue
        path = [root]
        colors[root] = 1
        frames: list[tuple[str, list[str], int]] = [
            (root, by_id[root]["depends_on"], 0)
        ]
        while frames:
            current, dependencies, index = frames[-1]
            if index == len(dependencies):
                colors[current] = 2
                frames.pop()
                path.pop()
                continue
            dependency = dependencies[index]
            frames[-1] = (current, dependencies, index + 1)
            color = colors.get(dependency, 0)
            if color == 0:
                colors[dependency] = 1
                path.append(dependency)
                frames.append((dependency, by_id[dependency]["depends_on"], 0))
            elif color == 1:
                cycle = path[path.index(dependency):] + [dependency]
                if len(cycle) <= 13:
                    shown = " -> ".join(cycle)
                else:
                    shown = (
                        " -> ".join(cycle[:6])
                        + " -> ... -> "
                        + " -> ".join(cycle[-3:])
                    )
                raise WorkpaperError(
                    f"dependency cycle is not allowed ({len(cycle) - 1} findings): "
                    + shown
                )


def _validate_citation_bounds(
    records: list[tuple[str, str, int, int]],
    lines_by_ref: dict[str, list[str]],
) -> None:
    for where, ref, start, end in records:
        total_lines = len(lines_by_ref[ref])
        if start > end:
            raise WorkpaperError(f"{where} cites inverted line bounds {start}-{end}")
        if end > total_lines:
            raise WorkpaperError(
                f"{where} cites lines {start}-{end}, but snapshot {ref} "
                f"has {total_lines} lines; ranges are not clipped"
            )


def load(record_path: Path, store: Path) -> dict:
    """Validate a workpaper against exact saved snapshot lines.

    The returned structure contains only validated author declarations and
    canonical evidence metadata/content loaded through evidence.load().
    """
    record = _load_json(record_path)
    schema = _string(record["schema"], "workpaper.schema")
    if schema != SCHEMA:
        raise WorkpaperError(f"unsupported workpaper schema {schema!r}; expected {SCHEMA!r}")
    outcome = _string(record["outcome"], "workpaper.outcome")
    question = _string(record["question"], "workpaper.question")

    raw_findings = record["findings"]
    if type(raw_findings) is not list or not raw_findings:
        raise WorkpaperError("workpaper.findings must be a nonempty array")

    findings: list[dict] = []
    by_id: dict[str, dict] = {}
    snapshots: dict[str, dict] = {}
    lines_by_ref: dict[str, list[str]] = {}
    citation_bounds: list[tuple[str, str, int, int]] = []

    for finding_index, raw in enumerate(raw_findings):
        where = f"workpaper.findings[{finding_index}]"
        item = _object(raw, where, FINDING_KEYS, FINDING_KEYS)
        finding_id = _string(item["id"], f"{where}.id")
        if not FINDING_ID.fullmatch(finding_id):
            raise WorkpaperError(
                f"{where}.id must start with a letter or digit and contain only "
                "letters, digits, dots, underscores, or hyphens"
            )
        if finding_id in by_id:
            raise WorkpaperError(f"duplicate finding id {finding_id}")
        kind = _string(item["kind"], f"{where}.kind")
        if kind not in KINDS:
            raise WorkpaperError(
                f"{where}.kind must be one of: {', '.join(KINDS)}"
            )
        status = _string(item["status"], f"{where}.status")
        if status not in STATUSES:
            raise WorkpaperError(
                f"{where}.status must be one of: {', '.join(STATUSES)}"
            )
        text = _string(item["text"], f"{where}.text")
        conditions = _string_list(item["conditions"], f"{where}.conditions")
        depends_on = _string_list(item["depends_on"], f"{where}.depends_on")
        for dependency in depends_on:
            if not FINDING_ID.fullmatch(dependency):
                raise WorkpaperError(
                    f"{where}.depends_on contains invalid finding id {dependency!r}"
                )

        raw_evidence = item["evidence"]
        if type(raw_evidence) is not list:
            raise WorkpaperError(f"{where}.evidence must be an array")
        citations: list[dict] = []
        for evidence_index, raw_citation in enumerate(raw_evidence):
            citation_where = f"{where}.evidence[{evidence_index}]"
            citation = _object(
                raw_citation, citation_where, EVIDENCE_REQUIRED, EVIDENCE_KEYS
            )
            ref = _string(citation["ref"], f"{citation_where}.ref")
            start = _line_number(citation["start_line"], f"{citation_where}.start_line")
            end = _line_number(citation["end_line"], f"{citation_where}.end_line")
            relation = _string(citation["relation"], f"{citation_where}.relation")
            if relation not in RELATIONS:
                raise WorkpaperError(
                    f"{citation_where}.relation must be one of: {', '.join(RELATIONS)}"
                )
            note = citation.get("note", "")
            note = _string(note, f"{citation_where}.note", nonempty=False)
            if ref not in snapshots:
                snapshots[ref] = evidence.load(store, ref)
                lines_by_ref[ref] = snapshots[ref]["content"].splitlines(keepends=True)
            citation_bounds.append((citation_where, ref, start, end))
            citations.append({
                "ref": ref,
                "start_line": start,
                "end_line": end,
                "relation": relation,
                "note": note,
            })

        finding = {
            "id": finding_id,
            "kind": kind,
            "text": text,
            "status": status,
            "conditions": conditions,
            "evidence": citations,
            "depends_on": depends_on,
        }
        findings.append(finding)
        by_id[finding_id] = finding

    _validate_dependencies(findings, by_id)
    _validate_citation_bounds(citation_bounds, lines_by_ref)
    open_questions = []
    if "open_questions" in record:
        open_questions = _string_list(
            record["open_questions"], "workpaper.open_questions"
        )

    reverse: dict[str, list[str]] = defaultdict(list)
    for finding in findings:
        for dependency in finding["depends_on"]:
            reverse[dependency].append(finding["id"])

    return {
        "record": {
            "schema": schema,
            "outcome": outcome,
            "question": question,
            "findings": findings,
            "open_questions": open_questions,
        },
        "by_id": by_id,
        "snapshots": snapshots,
        "lines": lines_by_ref,
        "reverse": dict(reverse),
        "has_superseded": any(
            finding["status"] == "superseded" for finding in findings
        ),
    }


def _ancestor_paths(finding_id: str, by_id: dict[str, dict]) -> dict[str, list[str]]:
    """Find shortest declared paths to each transitive ancestor."""
    found: dict[str, list[str]] = {}
    queue = deque([(finding_id, [finding_id])])
    visited = {finding_id}
    while queue:
        current, path = queue.popleft()
        for dependency in by_id[current]["depends_on"]:
            if dependency in found:
                continue
            next_path = path + [dependency]
            found[dependency] = next_path
            if dependency not in visited:
                visited.add(dependency)
                queue.append((dependency, next_path))
    return found


def _dependency_warnings(data: dict) -> list[dict]:
    if not data["has_superseded"]:
        return []
    warnings = []
    for finding in data["record"]["findings"]:
        if finding["status"] != "current":
            continue
        ancestors = _ancestor_paths(finding["id"], data["by_id"])
        for ancestor_id, path in ancestors.items():
            ancestor = data["by_id"][ancestor_id]
            if ancestor["status"] == "superseded":
                warnings.append({
                    "finding": finding["id"],
                    "depends_on_superseded": ancestor_id,
                    "witness_path": path,
                    "semantics": "declared dependency, not semantic impact",
                })
    order = {finding["id"]: index for index, finding in enumerate(data["record"]["findings"])}
    warnings.sort(key=lambda item: (
        order[item["finding"]],
        order[item["depends_on_superseded"]],
    ))
    return warnings


def _citation_inventory(finding: dict, data: dict) -> list[dict]:
    inventory = []
    for citation in finding["evidence"]:
        snapshot = data["snapshots"][citation["ref"]]
        inventory.append({
            "finding": finding["id"],
            "ref": citation["ref"],
            "start_line": citation["start_line"],
            "end_line": citation["end_line"],
            "relation": citation["relation"],
            "title": snapshot["title"],
            "source": snapshot["source"],
            "representation": snapshot["representation"],
            "generated": snapshot["representation"] == "generated",
            "captured_at": snapshot["captured_at"],
            "selection": "cited and declared, not read or verified",
        })
    return inventory


def inspect(record_path: Path, store: Path) -> dict:
    """Return a compact inventory without changing the workpaper or evidence."""
    data = load(record_path, store)
    findings = data["record"]["findings"]
    cited_ranges = []
    representations: dict[str, int] = {}
    uncited = []
    finding_inventory = []
    for finding in findings:
        citations = _citation_inventory(finding, data)
        cited_ranges.extend(citations)
        if not finding["evidence"]:
            uncited.append(finding["id"])
        finding_inventory.append({
            "id": finding["id"],
            "kind": finding["kind"],
            "status": finding["status"],
            "conditions": finding["conditions"],
            "depends_on": finding["depends_on"],
            "cited_range_count": len(citations),
        })
        for citation in citations:
            representation = citation["representation"]
            representations[representation] = representations.get(representation, 0) + 1
    return {
        "schema": SCHEMA,
        "operation": "inspect",
        "record": str(record_path),
        "semantics": (
            "authored interpretation and declared citations; not an observed read log, "
            "source verification, semantic proof, owner approval, or execution authority"
        ),
        "outcome": data["record"]["outcome"],
        "question": data["record"]["question"],
        "findings": finding_inventory,
        "cited_ranges": cited_ranges,
        "representations": representations,
        "uncited_findings": uncited,
        "dependency_warnings": _dependency_warnings(data),
        "open_question_count": len(data["record"]["open_questions"]),
    }


def _fence(content: str, label: str = "") -> str:
    longest = max((len(match.group(0)) for match in re.finditer(r"`+", content)), default=0)
    fence = "`" * max(3, longest + 1)
    ending = "" if content.endswith("\n") else "\n"
    return f"{fence}{label}\n{content}{ending}{fence}\n"


def _safe_text(text: str) -> str:
    """Escape authored text so Markdown and HTML remain literal characters."""
    escaped = html.escape(text, quote=False)
    escaped = re.sub(r"([\\`*_\[\]{}()#+!|~<=$:@])", r"\\\1", escaped)
    # GFM can autolink plain URLs/emails even after link brackets are escaped.
    escaped = re.sub(r"(?i)(\bwww)(?=\.)", r"\1\\", escaped)
    escaped = re.sub(r"(?m)^( *)(?=[-+])", r"\1\\", escaped)
    return re.sub(r"(?m)^( *)(\d+)(?=\. )", r"\1\2\\", escaped)


def _quote(text: str) -> str:
    lines = _safe_text(text).splitlines() or [""]
    return "\n".join("> " + line if line else ">" for line in lines) + "\n"


def _bullets(items: list[str]) -> str:
    if not items:
        return "_None._\n"
    blocks = []
    for item in items:
        lines = _safe_text(item).splitlines() or [""]
        blocks.append("- " + lines[0] + "".join("\n  " + line for line in lines[1:]))
    return "\n".join(blocks) + "\n"


def _source_metadata(snapshot: dict) -> str:
    return (
        f"title: {snapshot['title']}\n"
        f"source: {snapshot['source']}\n"
        f"snapshot: {snapshot['ref']}\n"
        f"representation: {snapshot['representation']}\n"
        f"captured_at: {snapshot['captured_at']}\n"
    )


def _evidence_index(data: dict) -> tuple[dict[tuple[str, int, int], str], list[tuple[str, str, int, int]]]:
    """Assign stable presentation IDs in authored finding/citation order."""
    ids: dict[tuple[str, int, int], str] = {}
    ordered: list[tuple[str, str, int, int]] = []
    for finding in data["record"]["findings"]:
        for citation in finding["evidence"]:
            key = (citation["ref"], citation["start_line"], citation["end_line"])
            if key not in ids:
                evidence_id = f"e{len(ids) + 1}"
                ids[key] = evidence_id
                ordered.append((evidence_id, *key))
    return ids, ordered


def _evidence_link(evidence_id: str) -> str:
    return f"[{evidence_id}](#soundings-evidence-{evidence_id})"


def _render_evidence_entry(
    evidence_id: str, ref: str, start: int, end: int, data: dict
) -> str:
    snapshot = data["snapshots"][ref]
    excerpt = evidence.window(data["lines"][ref], start, end)["text"]
    result = [
        f"### Soundings evidence {evidence_id}",
        "",
        "Generated appendix entry.",
        "",
        _fence(_source_metadata(snapshot), "text"),
        f"**Selected ref/range:** `{ref}` lines {start}-{end}",
        "",
    ]
    if snapshot["representation"] == "generated":
        result.extend([
            "**Generated representation.** This is authored or model-produced "
            "synthesis, not independent evidence. The representation label is a "
            "caller declaration, not a lineage proof.",
            "",
        ])
    result.extend([
        "**Exact cited excerpt**",
        "",
        _fence(excerpt, "text"),
    ])
    return "\n".join(result).rstrip() + "\n"


def _compact_reference(citation: dict, ids: dict[tuple[str, int, int], str]) -> str:
    evidence_id = ids[(citation["ref"], citation["start_line"], citation["end_line"])]
    text = f"- **{citation['relation'].capitalize()}** {_evidence_link(evidence_id)}"
    if citation["note"]:
        text += " - " + _safe_text(citation["note"]).replace("\n", " ")
    return text


def _render_finding(
    finding: dict,
    data: dict,
    ids: dict[tuple[str, int, int], str],
) -> str:
    label = finding["status"].upper()
    result = [
        f"### `{finding['id']}` - {finding['kind']} - {label}",
        "",
        _quote(finding["text"]).rstrip(),
        "",
    ]
    if finding["conditions"]:
        result.extend([
            "**Conditions**",
            "",
            _bullets(finding["conditions"]).rstrip(),
            "",
        ])
    if finding["depends_on"]:
        result.extend([
            "**Depends on:** "
            + ", ".join(f"`{item}`" for item in finding["depends_on"]),
            "",
        ])

    if finding["status"] == "current" and data["has_superseded"]:
        ancestors = _ancestor_paths(finding["id"], data["by_id"])
        superseded = [
            (ancestor_id, path)
            for ancestor_id, path in ancestors.items()
            if data["by_id"][ancestor_id]["status"] == "superseded"
        ]
    else:
        superseded = []
    if finding["status"] == "current" and superseded:
        result.extend(["**Dependency warnings**", ""])
        for _, path in superseded:
            result.append(
                "- Declared path to a superseded finding: "
                + " -> ".join(f"`{item}`" for item in path)
                + ". Revisit this finding; no automatic impact is assumed."
            )
        result.append("")

    if not finding["evidence"]:
        result.extend([
            "**Uncited finding.** It remains visible but is not source-linked.",
            "",
        ])
        return "\n".join(result).rstrip() + "\n"

    result.extend(["**Cited evidence**", ""])
    for citation in finding["evidence"]:
        result.append(_compact_reference(citation, ids))
    result.append("")
    return "\n".join(result).rstrip() + "\n"


def render(record_path: Path, store: Path) -> str:
    """Render a standalone Markdown report after complete validation."""
    data = load(record_path, store)
    record = data["record"]
    current = [finding for finding in record["findings"] if finding["status"] == "current"]
    superseded = [
        finding for finding in record["findings"] if finding["status"] == "superseded"
    ]
    warnings = _dependency_warnings(data)
    ids, evidence_entries = _evidence_index(data)

    result = [
        "# Research workpaper",
        "",
        "> **Authored interpretation.** Citations below are saved-source references "
        "declared by the author. They are not an observed read log, proof of source "
        "truth or coverage, owner approval, or execution authority.",
        ">",
        "> Representation labels are author declarations. Generated material is not "
        "independent evidence, and no lineage is inferred from it.",
        "",
        "## Desired outcome",
        "",
        _quote(record["outcome"]).rstrip(),
        "",
        "## Live question",
        "",
        _quote(record["question"]).rstrip(),
        "",
    ]

    if warnings:
        result.extend([
            "## Dependency warnings",
            "",
            "> These warnings follow only dependencies declared by the author. They are "
            "not a complete semantic blast radius.",
            "",
        ])
        for warning in warnings:
            result.append(
                "- Current finding "
                + " -> ".join(f"`{item}`" for item in warning["witness_path"])
                + " reaches superseded finding "
                + f"`{warning['depends_on_superseded']}`."
            )
        result.append("")

    result.extend(["## Authored findings", "", "### Current", ""])
    if current:
        for finding in current:
            result.extend([_render_finding(finding, data, ids), ""])
    else:
        result.extend(["_No current findings are declared._", ""])

    result.extend(["### Superseded", ""])
    if superseded:
        for finding in superseded:
            result.extend([_render_finding(finding, data, ids), ""])
    else:
        result.extend(["_No superseded findings are declared._", ""])

    result.extend([
        "## Open questions",
        "",
        _bullets(record["open_questions"]).rstrip(),
        "",
        "## Cited evidence appendix",
        "",
        "Each unique selected snapshot range appears once. Evidence IDs follow "
        "first citation order; relationship and author notes remain on the findings.",
        "",
    ])
    if evidence_entries:
        for evidence_id, ref, start, end in evidence_entries:
            result.extend([
                _render_evidence_entry(evidence_id, ref, start, end, data),
                "",
            ])
    else:
        result.extend(["_No cited evidence ranges are declared._", ""])

    result.extend([
        "## Artifact limits",
        "",
        "- This workpaper is an optional bounded task artifact, not another canonical "
        "project record.",
        "- Citations are authored declarations, not an observed read log, proof of "
        "source truth or coverage, owner approval, or execution authority.",
        "- Conditions must not be inferred as verified; current/superseded status is an "
        "author declaration, not source freshness.",
        "- Representation labels are author declarations. Generated material is not "
        "independent evidence, and no lineage is inferred from it.",
        "- Exact excerpts were generated from the selected local snapshots at render time.",
        "- No network fetch, original-file read, semantic inference, project edit, or "
        "automatic memory was performed.",
        "",
    ])
    return "\n".join(result).rstrip() + "\n"


def _write_new(path: Path, content: str) -> None:
    parent = path.parent
    if not parent.is_dir():
        raise WorkpaperError(f"output parent directory does not exist: {parent}")
    descriptor, temp_name = tempfile.mkstemp(
        dir=str(parent), prefix=".workpaper-", suffix=".md"
    )
    temp = Path(temp_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.link(temp, path)
        except FileExistsError as exc:
            raise WorkpaperError(
                f"output already exists; refusing to replace it: {path}"
            ) from exc
    finally:
        try:
            temp.unlink()
        except FileNotFoundError:
            pass


def impact(
    record_path: Path,
    store: Path,
    *,
    finding_id: str | None = None,
    ref: str | None = None,
) -> dict:
    """Trace declared reverse dependencies from one finding or saved source ref."""
    if (finding_id is None) == (ref is None):
        raise WorkpaperError("select exactly one impact seed: --finding or --ref")
    data = load(record_path, store)
    if finding_id is not None:
        if finding_id not in data["by_id"]:
            raise WorkpaperError(f"unknown finding seed {finding_id}")
        seeds = [finding_id]
        seed_type = "finding"
        seed_value = finding_id
    else:
        evidence.load(store, ref)
        seeds = [
            finding["id"] for finding in data["record"]["findings"]
            if any(citation["ref"] == ref for citation in finding["evidence"])
        ]
        if not seeds:
            raise WorkpaperError(
                f"source seed {ref} exists but no finding cites that snapshot"
            )
        seed_type = "ref"
        seed_value = ref

    affected: dict[str, dict] = {}
    queue: deque[tuple[str, list[str]]] = deque()
    if seed_type == "ref":
        for seed in seeds:
            finding = data["by_id"][seed]
            relations = [
                citation["relation"] for citation in finding["evidence"]
                if citation["ref"] == ref
            ]
            affected[seed] = {
                "id": seed,
                "status": finding["status"],
                "superseded": finding["status"] == "superseded",
                "reason": "cites-snapshot-ref",
                "relations": relations,
                "witness_path": [seed],
            }
            queue.append((seed, [seed]))
    else:
        finding = data["by_id"][seeds[0]]
        affected[seeds[0]] = {
            "id": seeds[0],
            "status": finding["status"],
            "superseded": finding["status"] == "superseded",
            "reason": "selected-seed",
            "relations": [],
            "witness_path": [seeds[0]],
        }
        queue.append((seeds[0], [seeds[0]]))

    while queue:
        current, path = queue.popleft()
        for dependent_id in data["reverse"].get(current, []):
            if dependent_id in affected:
                continue
            dependent = data["by_id"][dependent_id]
            next_path = path + [dependent_id]
            affected[dependent_id] = {
                "id": dependent_id,
                "status": dependent["status"],
                "superseded": dependent["status"] == "superseded",
                "reason": "declared-dependency",
                "relations": [],
                "witness_path": next_path,
            }
            queue.append((dependent_id, next_path))

    order = {finding["id"]: index for index, finding in enumerate(data["record"]["findings"])}
    if seed_type == "finding":
        selected_seed = seeds[0]
        result_findings = sorted(
            [
                item for item in affected.values()
                if item["id"] == selected_seed
                or selected_seed in item["witness_path"][:-1]
            ],
            key=lambda item: (len(item["witness_path"]), order[item["id"]]),
        )
    else:
        result_findings = sorted(
            affected.values(),
            key=lambda item: (len(item["witness_path"]), order[item["id"]]),
        )
    return {
        "schema": SCHEMA,
        "operation": "impact",
        "record": str(record_path),
        "seed": {
            "type": seed_type,
            "value": seed_value,
            "findings": seeds,
        },
        "affected_findings": result_findings,
        "semantics": (
            "declared dependency reach only; not complete semantic blast radius, "
            "source verification, or project execution"
        ),
        "project_artifacts_changed": False,
    }


def _citations_by_ref(data: dict) -> dict[str, list[dict]]:
    citations_by_ref: dict[str, list[dict]] = defaultdict(list)
    for finding in data["record"]["findings"]:
        for index, citation in enumerate(finding["evidence"]):
            citations_by_ref[citation["ref"]].append({
                "finding": finding["id"],
                "citation_index": index,
                "ref": citation["ref"],
                "start_line": citation["start_line"],
                "end_line": citation["end_line"],
                "relation": citation["relation"],
                "note": citation["note"],
            })
    return dict(citations_by_ref)


def _descendant_paths(premise: str, data: dict) -> list[dict]:
    """Find shortest declared dependent paths within one validated revision."""
    descendants = []
    visited: set[str] = set()
    queue: deque[tuple[str, list[str]]] = deque(
        (dependent, [premise, dependent])
        for dependent in data["reverse"].get(premise, [])
    )
    while queue:
        current, path = queue.popleft()
        if current in visited:
            continue
        visited.add(current)
        finding = data["by_id"][current]
        descendants.append({
            "id": current,
            "status": finding["status"],
            "witness_path": path,
        })
        for dependent in data["reverse"].get(current, []):
            if dependent not in visited:
                queue.append((dependent, path + [dependent]))
    return descendants


def _finding_order(before: dict, after: dict) -> dict:
    before_ids = [finding["id"] for finding in before["record"]["findings"]]
    after_ids = [finding["id"] for finding in after["record"]["findings"]]
    before_positions = {finding_id: index for index, finding_id in enumerate(before_ids)}
    after_positions = {finding_id: index for index, finding_id in enumerate(after_ids)}
    common_before = [finding_id for finding_id in before_ids if finding_id in after_positions]
    common_after = [finding_id for finding_id in after_ids if finding_id in before_positions]
    moved_common = [
        {
            "id": finding_id,
            "before_position": before_positions[finding_id],
            "after_position": after_positions[finding_id],
        }
        for finding_id in common_before
        if before_positions[finding_id] != after_positions[finding_id]
    ]
    return {
        "before": before_ids,
        "after": after_ids,
        "common_before": common_before,
        "common_after": common_after,
        "common_reordered": common_before != common_after,
        "moved_common": moved_common,
    }


def compare(
    before_path: Path,
    after_path: Path,
    before_store: Path,
    after_store: Path,
) -> dict:
    """Compare two validated authored revisions without merging their graphs.

    Stable authored finding IDs are the only correspondence. Each revision is
    loaded against its own explicitly selected snapshot store.
    """
    before = load(before_path, before_store)
    after = load(after_path, after_store)
    before_record = before["record"]
    after_record = after["record"]
    before_ids = [finding["id"] for finding in before_record["findings"]]
    after_ids = [finding["id"] for finding in after_record["findings"]]
    before_positions = {finding_id: index for index, finding_id in enumerate(before_ids)}
    after_positions = {finding_id: index for index, finding_id in enumerate(after_ids)}

    added_findings = [
        {
            "id": finding_id,
            "position": after_positions[finding_id],
            "finding": after["by_id"][finding_id],
        }
        for finding_id in after_ids
        if finding_id not in before["by_id"]
    ]
    removed_findings = [
        {
            "id": finding_id,
            "position": before_positions[finding_id],
            "finding": before["by_id"][finding_id],
        }
        for finding_id in before_ids
        if finding_id not in after["by_id"]
    ]

    changed_findings = []
    unchanged_findings = []
    for finding_id in before_ids:
        if finding_id not in after["by_id"]:
            continue
        old = before["by_id"][finding_id]
        new = after["by_id"][finding_id]
        changed_fields = [
            field for field in FINDING_CONTENT_FIELDS
            if old[field] != new[field]
        ]
        if changed_fields:
            changed_findings.append({
                "id": finding_id,
                "before_position": before_positions[finding_id],
                "after_position": after_positions[finding_id],
                "changed_fields": changed_fields,
                "before": old,
                "after": new,
            })
        else:
            unchanged_findings.append({
                "id": finding_id,
                "status": new["status"],
                "before_position": before_positions[finding_id],
                "after_position": after_positions[finding_id],
            })

    global_changes: dict[str, dict] = {}
    for field in ("outcome", "question", "open_questions"):
        if before_record[field] != after_record[field]:
            global_changes[field] = {
                "before": before_record[field],
                "after": after_record[field],
            }

    before_citations = _citations_by_ref(before)
    after_citations = _citations_by_ref(after)
    snapshot_conflicts = []
    for ref in before_citations:
        if ref not in after_citations:
            continue
        old = before["snapshots"][ref]
        new = after["snapshots"][ref]
        changed_fields = [
            field for field in SNAPSHOT_CONTENT_FIELDS
            if old[field] != new[field]
        ]
        if not changed_fields:
            continue
        snapshot_conflicts.append({
            "ref": ref,
            "changed_fields": changed_fields,
            "before": {field: old[field] for field in changed_fields},
            "after": {field: new[field] for field in changed_fields},
            "before_citations": before_citations[ref],
            "after_citations": after_citations[ref],
            "semantics": (
                "same snapshot ref name in separately selected stores; these are "
                "loaded local values, not an authenticity or freshness finding"
            ),
        })

    # A saved source can change even when its citations and authored finding
    # fields do not. Keep that review reason separate from the literal diff.
    conflict_seeds: dict[str, dict[str, list[str]]] = {
        "before": defaultdict(list), "after": defaultdict(list),
    }
    for conflict in snapshot_conflicts:
        for version in ("before", "after"):
            for citation in conflict[version + "_citations"]:
                refs = conflict_seeds[version][citation["finding"]]
                if conflict["ref"] not in refs:
                    refs.append(conflict["ref"])
    changed_ids = {finding["id"] for finding in changed_findings}
    effects = []
    for finding_id in before_ids + [item for item in after_ids if item not in before["by_id"]]:
        for version, data, other in (("before", before, after), ("after", after, before)):
            if finding_id not in data["by_id"]:
                continue
            change = None
            if finding_id not in other["by_id"]:
                change = "removed" if version == "before" else "added"
            elif finding_id in changed_ids:
                change = "changed"
            refs = conflict_seeds[version].get(finding_id, [])
            if change is None and not refs:
                continue
            effects.append({
                "premise": finding_id,
                "change": change or "snapshot_conflict",
                "version": version,
                "conflicting_refs": refs,
                "descendants": _descendant_paths(finding_id, data),
            })

    questions_before = before_record["open_questions"]
    questions_after = after_record["open_questions"]
    return {
        "schema": SCHEMA,
        "operation": "compare",
        "before": {
            "record": str(before_path),
            "store": str(before_store),
        },
        "after": {
            "record": str(after_path),
            "store": str(after_store),
        },
        "global_changes": {
            "changed_fields": list(global_changes),
            "changes": global_changes,
        },
        "findings": {
            "added": added_findings,
            "removed": removed_findings,
            "changed": changed_findings,
            "unchanged": unchanged_findings,
        },
        "ordering": {
            "findings": _finding_order(before, after),
            "open_questions": {
                "before": questions_before,
                "after": questions_after,
                "sequence_changed": questions_before != questions_after,
                "reordered": (
                    questions_before != questions_after and
                    sorted(questions_before) == sorted(questions_after)
                ),
            },
        },
        "dependency_effects": effects,
        "snapshot_conflicts": snapshot_conflicts,
        "semantics": (
            "structural comparison by stable authored finding IDs, with each "
            "revision's dependency graph and selected snapshot store loaded "
            "separately; not semantic equivalence, source authentication, "
            "freshness, correction, acceptance, or execution authority"
        ),
        "project_artifacts_changed": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name, help_text in (
        ("inspect", "validate and inventory declared findings and citations"),
        ("render", "render a standalone Markdown workpaper"),
    ):
        command = commands.add_parser(name, help=help_text)
        command.add_argument("workpaper", type=Path)
        command.add_argument("--store", required=True, type=Path,
                             help="explicit local evidence.v1 snapshot directory")
        if name == "render":
            command.add_argument("--output", type=Path,
                                 help="new Markdown file; defaults to stdout")
    trace = commands.add_parser("impact", help="trace declared reverse dependencies")
    trace.add_argument("workpaper", type=Path)
    trace.add_argument("--store", required=True, type=Path,
                       help="explicit local evidence.v1 snapshot directory")
    seed = trace.add_mutually_exclusive_group(required=True)
    seed.add_argument("--finding")
    seed.add_argument("--ref")
    comparison = commands.add_parser(
        "compare", help="compare two revisions using stable authored finding IDs"
    )
    comparison.add_argument("before", type=Path)
    comparison.add_argument("after", type=Path)
    comparison.add_argument(
        "--before-store", required=True, type=Path,
        help="evidence.v1 store selected for the before revision",
    )
    comparison.add_argument(
        "--after-store", required=True, type=Path,
        help="evidence.v1 store selected for the after revision",
    )
    args = parser.parse_args(argv)

    try:
        if args.command == "inspect":
            result = inspect(args.workpaper, args.store)
            sys.stdout.buffer.write((evidence.compact_json(result) + "\n").encode("utf-8"))
        elif args.command == "render":
            report = render(args.workpaper, args.store)
            if args.output is None:
                sys.stdout.buffer.write(report.encode("utf-8"))
            else:
                _write_new(args.output, report)
        elif args.command == "impact":
            result = impact(
                args.workpaper,
                args.store,
                finding_id=args.finding,
                ref=args.ref,
            )
            sys.stdout.buffer.write((evidence.compact_json(result) + "\n").encode("utf-8"))
        else:
            result = compare(
                args.before,
                args.after,
                args.before_store,
                args.after_store,
            )
            sys.stdout.buffer.write((evidence.compact_json(result) + "\n").encode("utf-8"))
    except (evidence.EvidenceError, OSError, UnicodeError) as exc:
        print(f"workpaper: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
