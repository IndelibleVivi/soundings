"""Behavior checks for exact snapshots, honest coverage, and wire-byte budgets."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

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


if __name__ == "__main__":
    unittest.main()
