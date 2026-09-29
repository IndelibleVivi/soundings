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
import tempfile
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


def publish(store: Path, ref: str, snapshot: dict) -> None:
    """Write one snapshot without ever exposing a partially written final file.

    The payload is staged in a same-directory temporary file and then published
    with a no-clobber hard link, so an existing reference is preserved and an
    interrupted write cannot reach the final name. This is not a durability or
    tamper-proofing guarantee; it only prevents partial content from being
    published under a snapshot reference.
    """
    path = store / (ref + ".json")
    payload = (json.dumps(snapshot, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
    descriptor, temp_name = tempfile.mkstemp(dir=str(store), prefix=".tmp-", suffix=".json")
    temp = Path(temp_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.link(temp, path)
        except FileExistsError as exc:
            raise EvidenceError("snapshot reference already exists; the existing capture was preserved") from exc
    finally:
        try:
            temp.unlink()
        except FileNotFoundError:
            pass


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
    publish(store, snapshot["ref"], snapshot)
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


def pack(snapshot: dict, operation: str, windows: list[dict], max_bytes: int,
         *, scope: dict | None = None, continuation: bool = False, **details) -> dict:
    """Admit whole windows. Report omissions, the first omission, and where to resume.

    ``complete`` is true only when every window produced for the requested scope
    was returned. ``first_omitted`` is the earliest merged window that did not
    fit. When that window is not the last one, ``continuation.next_start_line``
    is the line after it, from which a new scoped search can resume once the
    window has been read separately. When it ends at the scope boundary there is
    no remainder, so ``next_start_line`` is null and the caller finishes after
    handling that window.
    """
    def response(selected: list[dict], omitted: set[int]) -> dict:
        first = windows[min(omitted)] if omitted else None
        result = {
            "operation": operation, "snapshot": metadata(snapshot),
            "line_count": len(snapshot["content"].splitlines()),
            **details,
        }
        if scope is not None:
            result["scope"] = scope
        result["ranges"] = selected
        result["omitted_ranges"] = len(omitted)
        result["first_omitted"] = ({"start_line": first["start_line"], "end_line": first["end_line"]}
                                   if first else None)
        if continuation:
            if first is None:
                result["continuation"] = None
            elif scope is not None and first["end_line"] >= scope["end_line"]:
                result["continuation"] = {"next_start_line": None}
            else:
                result["continuation"] = {"next_start_line": first["end_line"] + 1}
        result["complete"] = not omitted
        return result

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
         case_sensitive: bool = False, start: int = 1, end: int | None = None) -> dict:
    if not query or "\n" in query or "\r" in query:
        raise EvidenceError("find requires a nonempty single-line literal query")
    if context < 0:
        raise EvidenceError("context must not be negative")
    snapshot = load(store, ref)
    lines = snapshot["content"].splitlines(keepends=True)
    total = len(lines)
    if total == 0:
        if start != 1 or end is not None:
            raise EvidenceError("line range must fall within 1..0")
        scope = {"start_line": 1, "end_line": 0}
    else:
        scope_end = total if end is None else end
        if not 1 <= start <= scope_end <= total:
            raise EvidenceError(f"line range must fall within 1..{total}")
        scope = {"start_line": start, "end_line": scope_end}
    needle = query if case_sensitive else query.casefold()
    matches = [i + 1 for i, line in enumerate(lines)
               if scope["start_line"] <= i + 1 <= scope["end_line"]
               and needle in (line if case_sensitive else line.casefold())]
    spans: list[list[int]] = []
    for match in matches:
        span_start = max(scope["start_line"], match - context)
        span_end = min(scope["end_line"], match + context)
        if spans and span_start <= spans[-1][1] + 1:
            spans[-1][1] = max(spans[-1][1], span_end)
        else:
            spans.append([span_start, span_end])
    return pack(snapshot, "find", [window(lines, span_start, span_end) for span_start, span_end in spans],
                max_bytes, scope=scope, continuation=True,
                query=query, matching_lines=len(matches), context_lines=context)


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
    locate.add_argument("--start-line", type=int, default=1, help="first line of the search scope (default: 1)")
    locate.add_argument("--end-line", type=int, help="last line of the search scope (default: last line)")
    args = parser.parse_args()
    try:
        if args.command == "capture":
            result = capture(args.file, args.store, args.source, args.title, args.representation, args.max_bytes)
        elif args.command == "read":
            result = read(args.store, args.ref, args.start_line, args.end_line, args.max_bytes)
        else:
            result = find(args.store, args.ref, args.query, args.context, args.max_bytes,
                          args.case_sensitive, args.start_line, args.end_line)
        sys.stdout.buffer.write(encode(result, args.max_bytes))
    except (EvidenceError, OSError, UnicodeError) as exc:
        print(f"evidence: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
