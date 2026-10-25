#!/usr/bin/env python3
"""Explicit portable inquiry packets: brief, snapshots, and optional workpaper.

Python 3.10+, standard library only. No network, discovery, upload, or execution
of packet contents. Read snapshots with the adjacent evidence.py and --store
PACKET/evidence. V1 operations need evidence.py; authored workpaper operations
also need adjacent workpaper.py. A packet is local data, never task authorization.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

from evidence import EvidenceError, encode, load, metadata


SCHEMA = "soundings.packet.v1"
WORKPAPER_SCHEMA = "soundings.packet.v2"
WORKPAPER_NAME = "workpaper.json"


def _workpaper_module():
    try:
        import workpaper
    except ModuleNotFoundError as exc:
        if exc.name != "workpaper":
            raise
        raise EvidenceError("workpaper operations require adjacent workpaper.py and evidence.py") from exc
    return workpaper


def write_new(path: Path, content: str) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as stream:
        stream.write(content)


def create(store: Path, refs: list[str], brief: Path, output: Path,
           max_bytes: int = 8192, *, workpaper_path: Path | None = None,
           cited_only: bool = False) -> dict:
    """Copy only selected snapshots. Publish the manifest last; never overwrite."""
    if cited_only and (workpaper_path is None or refs):
        raise EvidenceError("--cited requires --workpaper and cannot be combined with --ref")
    paper = None
    if workpaper_path is not None:
        paper = _workpaper_module().load(workpaper_path, store)
    refs = list(paper["snapshots"]) if cited_only else list(refs)
    if (not refs and not cited_only) or len(set(refs)) != len(refs):
        raise EvidenceError("select at least one snapshot reference, without duplicates")
    if paper is not None:
        missing = [ref for ref in paper["snapshots"] if ref not in refs]
        if missing:
            raise EvidenceError("selected snapshots omit workpaper citations: " + ", ".join(missing))
    snapshots = [(paper["snapshots"][ref] if paper and ref in paper["snapshots"]
                  else load(store, ref)) for ref in refs]
    with brief.open(encoding="utf-8", newline="") as stream:
        text = stream.read()
    if not text.strip():
        raise EvidenceError("the inquiry brief must not be empty")
    result = {"operation": "create", "packet": str(output), "snapshots": len(refs),
              "brief": "brief.md", "evidence_store": "evidence", "created": True}
    manifest = {"schema": SCHEMA, "refs": refs}
    if paper is not None:
        manifest = {"schema": WORKPAPER_SCHEMA, "refs": refs, "workpaper": WORKPAPER_NAME}
        result.update(schema=WORKPAPER_SCHEMA, workpaper=WORKPAPER_NAME,
                      selection="workpaper citations" if cited_only else "explicit references")
    encode(result, max_bytes)  # Do not write a packet whose receipt cannot fit.
    output.mkdir(mode=0o700)  # Existing output, including an empty directory, is refused.
    (output / "evidence").mkdir(mode=0o700)
    write_new(output / "brief.md", text)
    for snapshot in snapshots:
        write_new(output / "evidence" / (snapshot["ref"] + ".json"),
                  json.dumps(snapshot, ensure_ascii=False, separators=(",", ":")) + "\n")
    if paper is not None:
        # Normalize only validated declarations; retain exact source text in snapshots.
        write_new(output / WORKPAPER_NAME,
                  json.dumps(paper["record"], ensure_ascii=False, separators=(",", ":")) + "\n")
    # A create interrupted before this completion marker is not a valid packet.
    write_new(output / "manifest.json",
              json.dumps(manifest, separators=(",", ":")) + "\n")
    return result


def _regular_file(path: Path) -> None:
    if path.is_symlink() or not path.is_file():
        raise EvidenceError(f"packet member must be a regular file: {path.name}")


def inspect(folder: Path, max_bytes: int = 8192) -> dict:
    """Check membership and readability, not source truth or research quality."""
    try:
        manifest_path = folder / "manifest.json"
        if manifest_path.exists() or manifest_path.is_symlink():
            _regular_file(manifest_path)
        manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise EvidenceError("packet manifest missing; the packet may be incomplete") from exc
    except json.JSONDecodeError as exc:
        raise EvidenceError("packet manifest is not valid JSON") from exc
    if not isinstance(manifest, dict) or manifest.get("schema") not in (SCHEMA, WORKPAPER_SCHEMA):
        raise EvidenceError("unsupported packet schema")
    has_paper = manifest["schema"] == WORKPAPER_SCHEMA
    keys = {"schema", "refs", "workpaper"} if has_paper else {"schema", "refs"}
    if set(manifest) != keys or (has_paper and manifest["workpaper"] != WORKPAPER_NAME):
        raise EvidenceError("invalid packet manifest fields or workpaper member")
    refs = manifest.get("refs")
    if (not isinstance(refs, list) or (not refs and not has_paper) or
            any(not isinstance(ref, str) for ref in refs) or len(set(refs)) != len(refs)):
        raise EvidenceError("packet references are invalid")
    evidence_dir = folder / "evidence"
    if evidence_dir.is_symlink() or not evidence_dir.is_dir():
        raise EvidenceError("packet evidence must be a local directory")
    # Ref syntax is checked by the canonical loader. Reject links before following them.
    for member in evidence_dir.iterdir():
        _regular_file(member)
    snapshots = [load(folder / "evidence", ref) for ref in refs]
    members = {"manifest.json", "brief.md", "evidence"}
    if has_paper:
        members.add(WORKPAPER_NAME)
    if {p.name for p in folder.iterdir()} != members:
        raise EvidenceError("packet has unexpected or missing members; inspect before transfer")
    if {p.name for p in (folder / "evidence").iterdir()} != {ref + ".json" for ref in refs}:
        raise EvidenceError("packet evidence differs from its explicit selection")
    for name in members - {"evidence"}:
        _regular_file(folder / name)
    for member in evidence_dir.iterdir():
        _regular_file(member)
    with (folder / "brief.md").open(encoding="utf-8", newline="") as stream:
        brief = stream.read()
    if not brief.strip():
        raise EvidenceError("the inquiry brief must not be empty")
    result = {"operation": "inspect", "schema": manifest["schema"], "readable": True,
              "brief": "brief.md", "brief_bytes": len(brief.encode("utf-8")),
              "evidence_store": "evidence",
              "snapshots": [{**metadata(s), "line_count": len(s["content"].splitlines()),
                             "content_bytes": len(s["content"].encode("utf-8"))}
                            for s in snapshots]}
    if has_paper:
        inventory = _workpaper_module().inspect(folder / WORKPAPER_NAME, evidence_dir)
        cited_refs = list(dict.fromkeys(item["ref"] for item in inventory["cited_ranges"]))
        if any(ref not in refs for ref in cited_refs):
            raise EvidenceError("workpaper cites a snapshot outside the packet selection")
        result["workpaper"] = {
            "path": WORKPAPER_NAME, "schema": inventory["schema"],
            "outcome": inventory["outcome"], "question": inventory["question"],
            "finding_count": len(inventory["findings"]), "cited_refs": cited_refs,
            "uncited_findings": inventory["uncited_findings"],
            "dependency_warnings": inventory["dependency_warnings"],
        }
    encode(result, max_bytes)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("create", help="copy an explicit brief and selected snapshots")
    build.add_argument("--store", required=True, type=Path)
    selection = build.add_mutually_exclusive_group(required=True)
    selection.add_argument("--ref", action="append", dest="refs")
    selection.add_argument("--cited", action="store_true",
                           help="select only refs cited by an explicit --workpaper")
    build.add_argument("--workpaper", type=Path,
                       help="validate and include authored findings as packet.v2")
    build.add_argument("--brief", required=True, type=Path)
    build.add_argument("--output", required=True, type=Path, help="new directory; parent must exist")
    show = commands.add_parser("inspect", help="check local packet readability and selection")
    show.add_argument("packet", type=Path)
    for command in (build, show):
        command.add_argument("--max-bytes", type=int, default=8192,
                             help="entire JSON stdout cap; does not limit packet size")
    args = parser.parse_args()
    try:
        if args.command == "create":
            result = create(args.store, args.refs or [], args.brief, args.output, args.max_bytes,
                            workpaper_path=args.workpaper, cited_only=args.cited)
        else:
            result = inspect(args.packet, args.max_bytes)
        sys.stdout.buffer.write(encode(result, args.max_bytes))
    except (EvidenceError, OSError, UnicodeError) as exc:
        print(f"packet: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
