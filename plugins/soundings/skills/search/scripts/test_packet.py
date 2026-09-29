"""Portable inquiry evidence must survive relocation without widening selection."""

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import evidence
import packet


class PacketTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.store = self.root / "store"
        self.brief = self.root / "question.md"
        self.brief.write_bytes("# 问题\r\nInterpretation remains provisional.\r\n".encode())
        self.out = self.root / "packet"

    def capture(self, text, representation="verbatim"):
        source = self.root / "source.txt"
        source.write_bytes(text.encode())
        return evidence.capture(source, self.store, "https://example.org/pinned", "Source",
                                representation, 8192)["snapshot"]["ref"]

    def test_selected_sources_survive_relocation_and_source_change(self):
        original = "Speaker: A\r\n仅用于旧版本。\r\n"
        ref = self.capture(original)
        omitted = self.capture("Do not transfer this source.")
        generated = self.capture("A provisional interpretation.", "generated")
        packet.create(self.store, [ref, generated], self.brief, self.out)
        moved = self.root / "elsewhere"
        shutil.move(str(self.out), moved)
        shutil.rmtree(self.store)
        self.brief.write_text("Changed after capture.")
        result = packet.inspect(moved)
        self.assertEqual([s["ref"] for s in result["snapshots"]], [ref, generated])
        self.assertEqual(result["snapshots"][1]["representation"], "generated")
        self.assertFalse((moved / "evidence" / (omitted + ".json")).exists())
        self.assertEqual(evidence.read(moved / "evidence", ref)["ranges"][0]["text"], original)
        self.assertIn(b"\r\n", (moved / "brief.md").read_bytes())
        self.assertEqual(result["snapshots"][0]["source"], "https://example.org/pinned")

    def test_missing_selected_source_and_small_receipt_write_nothing(self):
        with self.assertRaises(evidence.EvidenceError):
            packet.create(self.store, ["s-" + "0" * 32], self.brief, self.out)
        self.assertFalse(self.out.exists())
        ref = self.capture("Text")
        with self.assertRaises(evidence.EvidenceError):
            packet.create(self.store, [ref], self.brief, self.out, 10)
        self.assertFalse(self.out.exists())

    def test_existing_destination_is_never_replaced(self):
        ref = self.capture("Text")
        self.out.mkdir()
        with self.assertRaises(FileExistsError):
            packet.create(self.store, [ref], self.brief, self.out)
        self.assertEqual(list(self.out.iterdir()), [])

    def test_partial_write_cannot_be_inspected_as_complete(self):
        ref = self.capture("Text")
        real_write = packet.write_new
        def fail_snapshot(path, content):
            if path.parent.name == "evidence":
                raise OSError("simulated write failure")
            return real_write(path, content)
        with patch.object(packet, "write_new", side_effect=fail_snapshot):
            with self.assertRaises(OSError):
                packet.create(self.store, [ref], self.brief, self.out)
        self.assertFalse((self.out / "manifest.json").exists())
        with self.assertRaisesRegex(evidence.EvidenceError, "manifest missing"):
            packet.inspect(self.out)

    def test_unlisted_material_or_missing_evidence_is_reported(self):
        ref = self.capture("Text")
        packet.create(self.store, [ref], self.brief, self.out)
        extra = self.out / "private-notes.md"
        extra.write_text("Unselected")
        with self.assertRaisesRegex(evidence.EvidenceError, "unexpected"):
            packet.inspect(self.out)
        extra.unlink()
        (self.out / "evidence" / (ref + ".json")).unlink()
        with self.assertRaisesRegex(evidence.EvidenceError, "snapshot not found"):
            packet.inspect(self.out)

    def test_manifest_cannot_redirect_reads_outside_packet(self):
        ref = self.capture("Text")
        packet.create(self.store, [ref], self.brief, self.out)
        (self.out / "manifest.json").write_text(json.dumps({"schema": packet.SCHEMA,
                                                            "refs": ["../../outside"]}))
        with self.assertRaisesRegex(evidence.EvidenceError, "invalid snapshot reference"):
            packet.inspect(self.out)

    def test_cli_stdout_budget_and_relocated_read(self):
        ref = self.capture("猫\n")
        packet.create(self.store, [ref], self.brief, self.out)
        command = [sys.executable, str(Path(packet.__file__)), "inspect", str(self.out)]
        result = subprocess.run(command + ["--max-bytes", "1024"], capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertLessEqual(len(result.stdout), 1024)
        self.assertTrue(json.loads(result.stdout)["readable"])
        result = subprocess.run(command + ["--max-bytes", "10"], capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, b"")
        result = subprocess.run([sys.executable, str(Path(evidence.__file__)), "read", ref,
                                 "--store", str(self.out / "evidence")], capture_output=True)
        self.assertEqual(json.loads(result.stdout)["ranges"][0]["text"], "猫\n")


if __name__ == "__main__":
    unittest.main()
