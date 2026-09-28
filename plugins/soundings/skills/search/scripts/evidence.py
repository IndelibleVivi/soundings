#!/usr/bin/env python3
"""Explicit local source snapshots with exact-range reads and bounded JSON output.

Python 3.10+, standard library only. This program makes no network requests and
does not infer semantic relationships between passages.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys
import uuid


SCHEMA = "soundings.evidence.v1"
REPRESENTATIONS = ("verbatim", "extracted", "generated")


class EvidenceError(Exception):
    """An input or requested response cannot satisfy the evidence contract."""


def encode(payload: dict, max_bytes: int) -> bytes:
    """Measure the complete successful stdout response, including its newline."""
    if max_bytes < 1:
        raise EvidenceError("max-bytes must be positive")
    wire = (json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
    if len(wire) > max_bytes:
        raise EvidenceError("byte budget cannot fit the complete response metadata; increase --max-bytes")
    return wire


def metadata(snapshot: dict) -> dict:
    return {key: snapshot[key] for key in ("ref", "source", "title", "representation", "captured_at")}


def capture(file: Path, store: Path, source: str, title: str, representation: str, max_bytes: int) -> dict:
    if representation not in REPRESENTATIONS:
        raise EvidenceError("representation must be verbatim, extracted, or generated")
    with file.open(encoding="utf-8", newline="") as stream:
        content = stream.read()
    snapshot = {
        "schema": SCHEMA,
        "ref": "s-" + uuid.uuid4().hex,
        "source": source,
        "title": title,
        "representation": representation,
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "content": content,
    }
    result = {"snapshot": metadata(snapshot), "line_count": len(content.splitlines()),
              "content_bytes": len(content.encode("utf-8")), "stored": True}
    encode(result, max_bytes)  # An impossible response must not create an orphan snapshot.
    store.mkdir(parents=True, exist_ok=True, mode=0o700)
    path = store / (snapshot["ref"] + ".json")
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as stream:
        json.dump(snapshot, stream, ensure_ascii=False, separators=(",", ":"))
        stream.write("\n")
    return result


def load(store: Path, ref: str) -> dict:
    if not re.fullmatch(r"s-[0-9a-f]{32}", ref):
        raise EvidenceError("invalid snapshot reference")
    path = store / (ref + ".json")
    try:
        snapshot = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise EvidenceError("snapshot not found in the selected store; capture a new source explicitly") from exc
    except json.JSONDecodeError as exc:
        raise EvidenceError("snapshot is not valid JSON") from exc
    if not isinstance(snapshot, dict) or snapshot.get("schema") != SCHEMA or snapshot.get("ref") != ref:
        raise EvidenceError("snapshot schema or reference does not match")
    if any(not isinstance(snapshot.get(key), str) for key in
           ("source", "title", "representation", "captured_at", "content")):
        raise EvidenceError("snapshot fields are incomplete")
    if snapshot["representation"] not in REPRESENTATIONS:
        raise EvidenceError("snapshot representation is unsupported")
    return snapshot


def window(lines: list[str], start: int, end: int) -> dict:
    return {"start_line": start, "end_line": end, "text": "".join(lines[start - 1:end])}


def pack(snapshot: dict, operation: str, windows: list[dict], max_bytes: int, **details) -> dict:
    """Admit whole windows. Report omissions and retain a locator for the first."""
    def response(selected: list[dict], omitted: set[int]) -> dict:
        first = windows[min(omitted)] if omitted else None
        return {
            "operation": operation, "snapshot": metadata(snapshot),
            "line_count": len(snapshot["content"].splitlines()),
            **details, "ranges": selected, "omitted_ranges": len(omitted),
            "first_omitted": ({"start_line": first["start_line"], "end_line": first["end_line"]}
                              if first else None),
            "complete": not omitted,
        }

    selected: list[dict] = []
    omitted = set(range(len(windows)))
    result = response(selected, omitted)
    encode(result, max_bytes)
    for index, item in enumerate(windows):
        candidate = response(selected + [item], omitted - {index})
        try:
            encode(candidate, max_bytes)
        except EvidenceError:
            continue
        selected.append(item)
        omitted.remove(index)
        result = candidate
    return result


def read(store: Path, ref: str, start: int = 1, end: int | None = None, max_bytes: int = 8192) -> dict:
    snapshot = load(store, ref)
    lines = snapshot["content"].splitlines(keepends=True)
    if not lines and start == 1 and end is None:
        return pack(snapshot, "read", [], max_bytes, requested_range=None)
    end = len(lines) if end is None else end
    if not 1 <= start <= end <= len(lines):
        raise EvidenceError(f"line range must fall within 1..{len(lines)}")
    return pack(snapshot, "read", [window(lines, start, end)], max_bytes,
                requested_range={"start_line": start, "end_line": end})


def find(store: Path, ref: str, query: str, context: int = 2, max_bytes: int = 8192,
         case_sensitive: bool = False) -> dict:
    if not query or "\n" in query or "\r" in query:
        raise EvidenceError("find requires a nonempty single-line literal query")
    if context < 0:
        raise EvidenceError("context must not be negative")
    snapshot = load(store, ref)
    lines = snapshot["content"].splitlines(keepends=True)
    needle = query if case_sensitive else query.casefold()
    matches = [i + 1 for i, line in enumerate(lines)
               if needle in (line if case_sensitive else line.casefold())]
    spans: list[list[int]] = []
    for match in matches:
        start, end = max(1, match - context), min(len(lines), match + context)
        if spans and start <= spans[-1][1] + 1:
            spans[-1][1] = max(spans[-1][1], end)
        else:
            spans.append([start, end])
    return pack(snapshot, "find", [window(lines, start, end) for start, end in spans],
                max_bytes, query=query, matching_lines=len(matches), context_lines=context)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--store", required=True, type=Path, help="explicit local snapshot directory")
    common.add_argument("--max-bytes", type=int, default=8192, help="entire JSON stdout cap (default: 8192 bytes)")
    commands = parser.add_subparsers(dest="command", required=True)
    save = commands.add_parser("capture", parents=[common], help="explicitly retain a UTF-8 source locally")
    save.add_argument("file", type=Path)
    save.add_argument("--source", required=True, help="original URL or source locator; never fetched")
    save.add_argument("--title", required=True)
    save.add_argument("--representation", required=True, choices=REPRESENTATIONS)
    show = commands.add_parser("read", parents=[common], help="read one exact, whole line range")
    show.add_argument("ref")
    show.add_argument("--start-line", type=int, default=1)
    show.add_argument("--end-line", type=int)
    locate = commands.add_parser("find", parents=[common], help="locate literal matches with neighboring lines")
    locate.add_argument("ref")
    locate.add_argument("query")
    locate.add_argument("--context", type=int, default=2)
    locate.add_argument("--case-sensitive", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "capture":
            result = capture(args.file, args.store, args.source, args.title, args.representation, args.max_bytes)
        elif args.command == "read":
            result = read(args.store, args.ref, args.start_line, args.end_line, args.max_bytes)
        else:
            result = find(args.store, args.ref, args.query, args.context, args.max_bytes, args.case_sensitive)
        sys.stdout.buffer.write(encode(result, args.max_bytes))
    except (EvidenceError, OSError, UnicodeError) as exc:
        print(f"evidence: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
