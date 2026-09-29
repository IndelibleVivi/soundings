"""Behavior checks for exact snapshots, honest coverage, and wire-byte budgets."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import evidence


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.store = self.root / "store"
        self.input = self.root / "source.md"

    def capture(self, text, representation="extracted", budget=8192):
        self.input.write_bytes(text.encode("utf-8"))
        result = evidence.capture(self.input, self.store, "https://example.org/source", "Source",
                                  representation, budget)
        return result["snapshot"]["ref"]

    def test_exact_unicode_and_crlf_round_trip(self):
        text = "# 导出\r\n\r\nRemove the badge.\r\n仅限付费方案。\r\nLast line"
        ref = self.capture(text)
        result = evidence.read(self.store, ref)
        self.assertTrue(result["complete"])
        self.assertEqual(result["ranges"][0]["text"], text)

    def test_new_capture_does_not_change_old_reference(self):
        old = self.capture("Release one\nOnly paid plans.\n")
        new = self.capture("Release two\nAll plans.\n")
        self.assertNotEqual(old, new)
        self.assertEqual(evidence.read(self.store, old)["ranges"][0]["text"],
                         "Release one\nOnly paid plans.\n")

    def test_find_keeps_short_qualifier_and_exact_neighboring_lines(self):
        ref = self.capture("# Export\n\nRemove the badge.\n\nOnly on paid plans.\n\nOther text.\n")
        result = evidence.find(self.store, ref, "remove", context=2)
        self.assertEqual(result["matching_lines"], 1)
        self.assertIn("Only on paid plans.", result["ranges"][0]["text"])
        self.assertEqual((result["ranges"][0]["start_line"], result["ranges"][0]["end_line"]), (1, 5))

    def test_overlapping_find_context_is_not_duplicated(self):
        ref = self.capture("one\nmatch A\nthree\nmatch B\nfive\n")
        result = evidence.find(self.store, ref, "match", context=1)
        self.assertEqual(result["matching_lines"], 2)
        self.assertEqual(len(result["ranges"]), 1)
        self.assertEqual(result["ranges"][0]["text"], self.input.read_text())

    def test_oversized_read_is_omitted_without_truncating_text(self):
        ref = self.capture("猫" * 900 + "\n仅限付费方案。\n")
        result = evidence.read(self.store, ref, max_bytes=700)
        self.assertFalse(result["complete"])
        self.assertEqual(result["ranges"], [])
        self.assertEqual(result["first_omitted"], {"start_line": 1, "end_line": 2})
        self.assertLessEqual(len(evidence.encode(result, 700)), 700)
        self.assertEqual(evidence.read(self.store, ref, 2, 2, 700)["ranges"][0]["text"], "仅限付费方案。\n")

    def test_oversized_find_window_does_not_hide_later_fitting_window(self):
        ref = self.capture("match " + "X" * 900 + "\nother\nmatch small\n")
        result = evidence.find(self.store, ref, "match", context=0, max_bytes=700)
        self.assertEqual(result["ranges"], [{"start_line": 3, "end_line": 3, "text": "match small\n"}])
        self.assertFalse(result["complete"])
        self.assertEqual(result["omitted_ranges"], 1)
        self.assertEqual(result["first_omitted"], {"start_line": 1, "end_line": 1})

    def test_byte_accounting_includes_unicode_json_and_final_newline(self):
        payload = {"text": "猫\n\"quoted\"", "ranges": [1, 2]}
        wire = evidence.encode(payload, 8192)
        self.assertEqual(json.loads(wire), payload)
        self.assertTrue(wire.endswith(b"\n"))
        self.assertEqual(evidence.encode(payload, len(wire)), wire)
        with self.assertRaises(evidence.EvidenceError):
            evidence.encode(payload, len(wire) - 1)

    def test_too_small_capture_budget_creates_no_store(self):
        with self.assertRaises(evidence.EvidenceError):
            self.capture("original", budget=20)
        self.assertFalse(self.store.exists())

    def test_empty_source_and_no_literal_match_are_complete(self):
        empty = self.capture("")
        self.assertTrue(evidence.read(self.store, empty)["complete"])
        ref = self.capture("Actual evidence\n")
        result = evidence.find(self.store, ref, "absent")
        self.assertEqual(result["matching_lines"], 0)
        self.assertTrue(result["complete"])

    def test_representation_survives_reads(self):
        ref = self.capture("A model summary.\n", representation="generated")
        self.assertEqual(evidence.read(self.store, ref)["snapshot"]["representation"], "generated")

    def test_invalid_ranges_and_missing_references_fail(self):
        ref = self.capture("one\ntwo\n")
        for start, end in ((0, 1), (2, 1), (1, 3)):
            with self.assertRaises(evidence.EvidenceError):
                evidence.read(self.store, ref, start, end)
        for bad in ("../source", "s-" + "0" * 32):
            with self.assertRaises(evidence.EvidenceError):
                evidence.read(self.store, bad)

    def test_cli_cap_applies_to_actual_stdout_and_error_is_not_broken_json(self):
        ref = self.capture("事实。\n" * 80)
        command = [sys.executable, str(Path(evidence.__file__)), "read", ref, "--store", str(self.store)]
        result = subprocess.run(command + ["--max-bytes", "700"], capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertLessEqual(len(result.stdout), 700)
        self.assertFalse(json.loads(result.stdout)["complete"])
        result = subprocess.run(command + ["--max-bytes", "20"], capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, b"")
        self.assertIn(b"byte budget", result.stderr)

    # Scoped find and explicit continuation. The previous helper had no scope
    # parameters, so these cases reject the earlier behavior directly: the
    # keyword arguments did not exist and no response carried ``continuation``.

    def test_find_scope_restricts_matches_and_reports_scope(self):
        ref = self.capture("match one\nplain\nmatch two\nplain\nmatch three\n")
        result = evidence.find(self.store, ref, "match", context=0, start=3, end=5)
        self.assertEqual(result["scope"], {"start_line": 3, "end_line": 5})
        self.assertEqual(result["matching_lines"], 2)
        self.assertEqual([r["start_line"] for r in result["ranges"]], [3, 5])
        self.assertTrue(result["complete"])
        self.assertIsNone(result["continuation"])
        self.assertEqual(result["ranges"][1]["text"], "match three\n")

    def test_find_scope_boundaries_are_inclusive_and_invalid_scopes_fail(self):
        ref = self.capture("a\nmatch b\nc\nd\n")
        single = evidence.find(self.store, ref, "match", context=0, start=2, end=2)
        self.assertEqual(single["ranges"], [{"start_line": 2, "end_line": 2, "text": "match b\n"}])
        full = evidence.find(self.store, ref, "match", context=0, start=1, end=4)
        self.assertEqual(full["scope"], {"start_line": 1, "end_line": 4})
        self.assertTrue(full["complete"])
        for start, end in ((0, 4), (3, 2), (1, 5), (2, 0)):
            with self.assertRaises(evidence.EvidenceError):
                evidence.find(self.store, ref, "match", start=start, end=end)

    def test_find_context_is_clipped_to_the_requested_scope(self):
        ref = self.capture("l1\nl2\nmatch l3\nl4\nl5\n")
        result = evidence.find(self.store, ref, "match", context=5, start=3, end=3)
        self.assertEqual(result["ranges"],
                         [{"start_line": 3, "end_line": 3, "text": "match l3\n"}])
        self.assertTrue(result["complete"])

    def test_find_scope_still_merges_overlapping_contexts(self):
        ref = self.capture("one\nmatch A\nthree\nmatch B\nfive\n")
        scoped = evidence.find(self.store, ref, "match", context=1, start=2, end=4)
        self.assertEqual(len(scoped["ranges"]), 1)
        self.assertEqual(scoped["ranges"][0]["text"], "match A\nthree\nmatch B\n")
        self.assertEqual(scoped["matching_lines"], 2)
        self.assertTrue(scoped["complete"])

    def test_find_continuation_exhausts_a_multi_omission_result(self):
        total = 8
        body = "".join(f"match {index:02d} " + "p" * 60 + "\nseparator\n" for index in range(total))
        expected = {index * 2 + 1: f"match {index:02d} " + "p" * 60 + "\n" for index in range(total)}
        ref = self.capture(body)
        budget = 900

        collected: dict[int, str] = {}
        cursor = 1
        guard = 0
        while True:
            guard += 1
            self.assertLess(guard, total + 5, "continuation did not terminate")
            result = evidence.find(self.store, ref, "match", context=0, max_bytes=budget, start=cursor)
            self.assertEqual(result["scope"]["start_line"], cursor)
            for item in result["ranges"]:
                collected[item["start_line"]] = item["text"]
            if result["complete"]:
                self.assertIsNone(result["continuation"])
                break
            # Account for the earliest omitted window before advancing the scope.
            omitted = result["first_omitted"]
            reread = evidence.read(self.store, ref, omitted["start_line"], omitted["end_line"], budget)
            self.assertTrue(reread["complete"])
            for item in reread["ranges"]:
                collected[item["start_line"]] = item["text"]
            self.assertEqual(result["continuation"]["next_start_line"], omitted["end_line"] + 1)
            cursor = result["continuation"]["next_start_line"]

        self.assertEqual(sorted(collected), sorted(expected))
        for line, text in collected.items():
            self.assertEqual(text, expected[line])

    def test_line_exceeding_the_budget_cannot_be_returned_and_needs_a_larger_budget(self):
        huge = "match " + "Z" * 900 + "\n"
        ref = self.capture("small match\nseparator\n" + huge)
        result = evidence.find(self.store, ref, "match", context=0, max_bytes=700)
        self.assertEqual([r["start_line"] for r in result["ranges"]], [1])
        self.assertFalse(result["complete"])
        self.assertEqual(result["first_omitted"], {"start_line": 3, "end_line": 3})
        self.assertEqual(result["continuation"], {"next_start_line": None})
        # Reading the exact oversized window is whole-or-omitted, not truncated.
        too_big = evidence.read(self.store, ref, 3, 3, 700)
        self.assertFalse(too_big["complete"])
        self.assertEqual(too_big["ranges"], [])
        self.assertEqual(too_big["first_omitted"], {"start_line": 3, "end_line": 3})
        # Only a larger budget can carry that single line, and it stays exact.
        raised = evidence.read(self.store, ref, 3, 3, 6000)
        self.assertTrue(raised["complete"])
        self.assertEqual(raised["ranges"][0]["text"], huge)

    def test_continuation_stops_at_the_scope_boundary_when_the_last_window_is_omitted(self):
        huge = "match " + "Z" * 900 + "\n"
        ref = self.capture("small match\nseparator\n" + huge)
        result = evidence.find(self.store, ref, "match", context=0, max_bytes=700, end=3)
        self.assertEqual(result["scope"], {"start_line": 1, "end_line": 3})
        self.assertFalse(result["complete"])
        self.assertEqual([r["start_line"] for r in result["ranges"]], [1])
        self.assertEqual(result["first_omitted"], {"start_line": 3, "end_line": 3})
        # No remainder exists after the last in-scope window, so the caller finishes
        # here instead of resuming past the scope end.
        self.assertEqual(result["continuation"], {"next_start_line": None})
        last = evidence.read(self.store, ref, 3, 3, 6000)
        self.assertTrue(last["complete"])
        self.assertEqual(last["ranges"][0]["text"], huge)

    def test_continuation_is_null_when_the_only_window_is_omitted(self):
        huge = "match " + "Y" * 900 + "\n"
        ref = self.capture(huge)
        result = evidence.find(self.store, ref, "match", context=0, max_bytes=700)
        self.assertEqual(result["scope"], {"start_line": 1, "end_line": 1})
        self.assertEqual(result["ranges"], [])
        self.assertEqual(result["first_omitted"], {"start_line": 1, "end_line": 1})
        self.assertEqual(result["continuation"], {"next_start_line": None})

    def test_cli_scoped_find_reports_scope_and_keeps_stdout_bounded(self):
        ref = self.capture("a\nmatch b\nc\n" + "match " + "q" * 900 + "\n")
        command = [sys.executable, str(Path(evidence.__file__)), "find", ref, "match",
                   "--store", str(self.store), "--context", "0", "--start-line", "1", "--max-bytes", "700"]
        result = subprocess.run(command, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertLessEqual(len(result.stdout), 700)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["scope"], {"start_line": 1, "end_line": 4})
        self.assertFalse(payload["complete"])
        self.assertEqual(payload["first_omitted"], {"start_line": 4, "end_line": 4})
        self.assertEqual(payload["continuation"], {"next_start_line": None})

    # Capture publication. These exercise the real write path with injected
    # faults and confirm a partial or failed write never appears as a snapshot.

    def test_publish_stages_complete_content_in_store_before_linking(self):
        original_link = evidence.os.link
        observed: dict[str, object] = {}

        def spy(source, destination):
            observed["source_dir"] = Path(source).parent
            observed["payload"] = Path(source).read_bytes()
            observed["published_at_link"] = Path(destination).exists()
            return original_link(source, destination)

        self.input.write_bytes("atomic body\n".encode("utf-8"))
        with mock.patch.object(evidence.os, "link", side_effect=spy):
            result = evidence.capture(self.input, self.store, "https://example.org/s", "T", "verbatim", 8192)
        ref = result["snapshot"]["ref"]
        self.assertEqual(observed["source_dir"], self.store)
        self.assertFalse(observed["published_at_link"])
        self.assertTrue(observed["payload"].endswith(b"\n"))
        self.assertEqual(observed["payload"], (self.store / (ref + ".json")).read_bytes())
        self.assertEqual(evidence.read(self.store, ref)["ranges"][0]["text"], "atomic body\n")
        self.assertEqual(sorted(p.name for p in self.store.iterdir()), [ref + ".json"])

    def test_failed_publish_leaves_no_snapshot_and_cleans_the_temp_file(self):
        self.input.write_bytes("data\n".encode("utf-8"))
        with mock.patch.object(evidence.os, "link", side_effect=OSError("link failed")):
            with self.assertRaises(OSError):
                evidence.capture(self.input, self.store, "s", "t", "extracted", 8192)
        self.assertEqual(sorted(p.name for p in self.store.iterdir()), [])

    def test_interrupted_write_is_cleaned_and_publishes_nothing(self):
        self.input.write_bytes("data\n".encode("utf-8"))
        with mock.patch.object(evidence.os, "fsync", side_effect=OSError("fsync failed")):
            with self.assertRaises(OSError):
                evidence.capture(self.input, self.store, "s", "t", "extracted", 8192)
        self.assertEqual(sorted(p.name for p in self.store.iterdir()), [])

    def test_partial_write_is_never_published_and_preserves_older_snapshots(self):
        good = self.capture("kept evidence\n")
        original_fdopen = evidence.os.fdopen

        class PartialStream:
            def __init__(self, stream):
                self._stream = stream

            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return self._stream.__exit__(*exc)

            def write(self, data):
                self._stream.write(data[: max(1, len(data) // 2)])
                raise OSError("disk full after a partial write")

            def flush(self):
                return self._stream.flush()

            def fileno(self):
                return self._stream.fileno()

        def partial_fdopen(descriptor, *args, **kwargs):
            return PartialStream(original_fdopen(descriptor, *args, **kwargs))

        self.input.write_bytes("doomed partial\n".encode("utf-8"))
        with mock.patch.object(evidence.os, "fdopen", side_effect=partial_fdopen):
            with self.assertRaises(OSError):
                evidence.capture(self.input, self.store, "s", "t", "extracted", 8192)
        names = sorted(p.name for p in self.store.iterdir())
        self.assertEqual(names, [good + ".json"])
        self.assertFalse(any(name.startswith(".tmp-") for name in names))
        self.assertEqual(evidence.read(self.store, good)["ranges"][0]["text"], "kept evidence\n")

    def test_existing_reference_is_preserved_and_never_overwritten(self):
        fixed = mock.Mock()
        fixed.hex = "0" * 32
        self.input.write_bytes("first\n".encode("utf-8"))
        with mock.patch.object(evidence.uuid, "uuid4", return_value=fixed):
            ref = evidence.capture(self.input, self.store, "s", "t", "extracted", 8192)["snapshot"]["ref"]
        stored = (self.store / (ref + ".json")).read_bytes()
        self.input.write_bytes("second\n".encode("utf-8"))
        with mock.patch.object(evidence.uuid, "uuid4", return_value=fixed):
            with self.assertRaises(evidence.EvidenceError):
                evidence.capture(self.input, self.store, "s", "t", "extracted", 8192)
        self.assertEqual((self.store / (ref + ".json")).read_bytes(), stored)
        self.assertEqual(sorted(p.name for p in self.store.iterdir()), [ref + ".json"])
        self.assertEqual(evidence.read(self.store, ref)["ranges"][0]["text"], "first\n")

    def test_failed_capture_keeps_older_snapshots_readable(self):
        good = self.capture("kept evidence\n")
        self.input.write_bytes("doomed\n".encode("utf-8"))
        with mock.patch.object(evidence.os, "link", side_effect=OSError("boom")):
            with self.assertRaises(OSError):
                evidence.capture(self.input, self.store, "s", "t", "extracted", 8192)
        self.assertEqual(sorted(p.name for p in self.store.iterdir()), [good + ".json"])
        self.assertEqual(evidence.read(self.store, good)["ranges"][0]["text"], "kept evidence\n")

    def test_snapshot_written_in_the_previous_format_stays_readable(self):
        text = "legacy body\nsecond line\n"
        ref = "s-" + "1" * 32
        snapshot = {"schema": evidence.SCHEMA, "ref": ref, "source": "https://example.org/old",
                    "title": "Old", "representation": "extracted",
                    "captured_at": "2024-01-01T00:00:00+00:00", "content": text}
        self.store.mkdir(parents=True, exist_ok=True)
        (self.store / (ref + ".json")).write_bytes(
            (json.dumps(snapshot, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8"))
        result = evidence.read(self.store, ref)
        self.assertTrue(result["complete"])
        self.assertEqual(result["ranges"][0]["text"], text)


if __name__ == "__main__":
    unittest.main()
