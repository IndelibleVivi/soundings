#!/usr/bin/env python3
"""Explicit portable inquiry packets: a brief and selected evidence snapshots.

Python 3.10+, standard library only. No network, discovery, upload, or execution
of packet contents. Read snapshots with the adjacent evidence.py and --store
PACKET/evidence. A packet is ordinary local data, never task authorization.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

from evidence import EvidenceError, encode, load, metadata


SCHEMA = "soundings.packet.v1"


def write_new(path: Path, content: str) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as stream:
        stream.write(content)


def create(store: Path, refs: list[str], brief: Path, output: Path,
           max_bytes: int = 8192) -> dict:
    """Copy only selected snapshots. Publish the manifest last; never overwrite."""
    if not refs or len(set(refs)) != len(refs):
        raise EvidenceError("select at least one snapshot reference, without duplicates")
    snapshots = [load(store, ref) for ref in refs]
    with brief.open(encoding="utf-8", newline="") as stream:
        text = stream.read()
    if not text.strip():
        raise EvidenceError("the inquiry brief must not be empty")
    result = {"operation": "create", "packet": str(output), "snapshots": len(refs),
              "brief": "brief.md", "evidence_store": "evidence", "created": True}
    encode(result, max_bytes)  # Do not write a packet whose receipt cannot fit.
    output.mkdir(mode=0o700)  # Existing output, including an empty directory, is refused.
    (output / "evidence").mkdir(mode=0o700)
    write_new(output / "brief.md", text)
    for snapshot in snapshots:
        write_new(output / "evidence" / (snapshot["ref"] + ".json"),
                  json.dumps(snapshot, ensure_ascii=False, separators=(",", ":")) + "\n")
    # This file is the completion marker. An interrupted create has no valid manifest.
    write_new(output / "manifest.json",
              json.dumps({"schema": SCHEMA, "refs": refs}, separators=(",", ":")) + "\n")
    return result


def inspect(folder: Path, max_bytes: int = 8192) -> dict:
    """Check membership and readability, not source truth or research quality."""
    try:
        manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise EvidenceError("packet manifest missing; the packet may be incomplete") from exc
    except json.JSONDecodeError as exc:
        raise EvidenceError("packet manifest is not valid JSON") from exc
    if not isinstance(manifest, dict) or manifest.get("schema") != SCHEMA:
        raise EvidenceError("unsupported packet schema")
    refs = manifest.get("refs")
    if (not isinstance(refs, list) or not refs or
            any(not isinstance(ref, str) for ref in refs) or len(set(refs)) != len(refs)):
        raise EvidenceError("packet references are invalid")
    snapshots = [load(folder / "evidence", ref) for ref in refs]
    if {p.name for p in folder.iterdir()} != {"manifest.json", "brief.md", "evidence"}:
        raise EvidenceError("packet has unexpected or missing members; inspect before transfer")
    if {p.name for p in (folder / "evidence").iterdir()} != {ref + ".json" for ref in refs}:
        raise EvidenceError("packet evidence differs from its explicit selection")
    with (folder / "brief.md").open(encoding="utf-8", newline="") as stream:
        brief = stream.read()
    if not brief.strip():
        raise EvidenceError("the inquiry brief must not be empty")
    result = {"operation": "inspect", "schema": SCHEMA, "readable": True,
              "brief": "brief.md", "brief_bytes": len(brief.encode("utf-8")),
              "evidence_store": "evidence",
              "snapshots": [{**metadata(s), "line_count": len(s["content"].splitlines()),
                             "content_bytes": len(s["content"].encode("utf-8"))}
                            for s in snapshots]}
    encode(result, max_bytes)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("create", help="copy an explicit brief and selected snapshots")
    build.add_argument("--store", required=True, type=Path)
    build.add_argument("--ref", required=True, action="append", dest="refs")
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
            result = create(args.store, args.refs, args.brief, args.output, args.max_bytes)
        else:
            result = inspect(args.packet, args.max_bytes)
        sys.stdout.buffer.write(encode(result, args.max_bytes))
    except (EvidenceError, OSError, UnicodeError) as exc:
        print(f"packet: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
