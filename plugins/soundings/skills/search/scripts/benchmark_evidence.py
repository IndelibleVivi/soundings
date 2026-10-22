#!/usr/bin/env python3
"""Compare legacy and current evidence admission on one synthetic workload.

This is a local diagnostic, not an acceptance test or a general performance
claim. It uses only the standard library and a temporary snapshot store.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import sys
import tempfile
import time

import evidence


def legacy_pack(snapshot: dict, operation: str, windows: list[dict], max_bytes: int,
                *, scope: dict | None = None, continuation: bool = False, **details) -> dict:
    """The previous admission loop, retained only for this comparison."""
    def response(selected: list[dict], omitted: set[int]) -> dict:
        first = windows[min(omitted)] if omitted else None
        result = {
            "operation": operation, "snapshot": evidence.metadata(snapshot),
            "line_count": len(snapshot["content"].splitlines()),
            **details,
        }
        if scope is not None:
            result["scope"] = scope
        result["ranges"] = selected
        result["omitted_ranges"] = len(omitted)
        result["first_omitted"] = (
            {"start_line": first["start_line"], "end_line": first["end_line"]}
            if first else None
        )
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
    evidence.encode(result, max_bytes)
    for index, item in enumerate(windows):
        candidate = response(selected + [item], omitted - {index})
        try:
            evidence.encode(candidate, max_bytes)
        except evidence.EvidenceError:
            continue
        selected.append(item)
        omitted.remove(index)
        result = candidate
    return result


def synthetic_lines(line_count: int, hit_count: int) -> str:
    if hit_count > (line_count + 1) // 2:
        raise ValueError("hit_count must fit on non-adjacent lines")
    lines = ["separator\n"] * line_count
    for index in range(hit_count):
        lines[index * 2] = f"match {index:05d}\n"
    return "".join(lines)


def timed_find(pack, store: Path, ref: str, budget: int, repeats: int) -> tuple[dict, list[float]]:
    current = evidence.pack
    evidence.pack = pack
    try:
        evidence.find(store, ref, "match", context=0, max_bytes=budget)
        samples = []
        result = None
        for _ in range(repeats):
            started = time.perf_counter()
            result = evidence.find(store, ref, "match", context=0, max_bytes=budget)
            samples.append(time.perf_counter() - started)
    finally:
        evidence.pack = current
    assert result is not None
    return result, samples


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lines", type=int, default=8000)
    parser.add_argument("--hits", type=int, default=4000)
    parser.add_argument("--max-bytes", type=int, default=1024)
    parser.add_argument("--repeats", type=int, default=5)
    args = parser.parse_args()
    if args.lines < 1 or args.hits < 1 or args.max_bytes < 1 or args.repeats < 1:
        parser.error("lines, hits, max-bytes, and repeats must be positive")
    if args.hits > (args.lines + 1) // 2:
        parser.error("hits must fit on non-adjacent lines")

    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        source = root / "synthetic.txt"
        source.write_text(synthetic_lines(args.lines, args.hits), encoding="utf-8")
        capture = evidence.capture(
            source, root / "store", "synthetic:benchmark", "Synthetic benchmark",
            "verbatim", 8192,
        )
        ref = capture["snapshot"]["ref"]
        new_result, new_samples = timed_find(
            evidence.pack, root / "store", ref, args.max_bytes, args.repeats
        )
        old_result, old_samples = timed_find(
            legacy_pack, root / "store", ref, args.max_bytes, args.repeats
        )

    new_median = statistics.median(new_samples)
    old_median = statistics.median(old_samples)
    report = {
        "python": sys.version.split()[0],
        "workload": {
            "lines": args.lines,
            "matching_lines": args.hits,
            "context_lines": 0,
            "max_bytes": args.max_bytes,
            "repeats": args.repeats,
        },
        "output_equal": old_result == new_result,
        "wire_bytes": len(evidence.encode(new_result, 8192)),
        "admitted_ranges": len(new_result["ranges"]),
        "omitted_ranges": new_result["omitted_ranges"],
        "new_seconds": new_samples,
        "legacy_seconds": old_samples,
        "new_median_seconds": new_median,
        "legacy_median_seconds": old_median,
        "median_ratio": old_median / new_median,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["output_equal"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
