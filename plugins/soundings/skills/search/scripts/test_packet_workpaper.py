"""A receiver can continue an authored inquiry using only an explicit packet."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import evidence
import packet
import workpaper


class WorkpaperPacketTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.store = self.root / "original-store"
        self.brief = self.root / "brief.md"
        self.brief.write_bytes("# 同一委托\r\nCheck the release boundary before changing the guide.\r\n".encode())
        self.out = self.root / "packet"
        self.paper = self.root / "authored.json"
        self.ref = self.capture("旧版仅限单进程。\r\nRelease B survives restart.\r\n")
        self.generated = self.capture("A generated interpretation.\n", "generated")
        self.excluded = self.capture("Unselected private material.\n")
        self.record = {
            "schema": workpaper.SCHEMA, "outcome": "有条件的建议", "question": "Which release?",
            "findings": [
                self.finding("old", status="superseded", citations=[self.cite(self.ref)]),
                self.finding("recommendation", dependencies=["old"],
                             citations=[self.cite(self.generated, "challenges")]),
                self.finding("independent"),
            ],
            "open_questions": ["Which version is deployed?"],
        }
        self.save()

    def capture(self, content, representation="verbatim"):
        path = self.root / "input.txt"
        path.write_bytes(content.encode())
        return evidence.capture(path, self.store, "https://example.org/release", "版本边界",
                                representation, 8192)["snapshot"]["ref"]

    def finding(self, identifier, *, status="current", dependencies=None, citations=None):
        return {"id": identifier, "kind": "judgment", "text": "保留条件和原文。\r\nNext line.",
                "status": status, "conditions": ["Only after a restart."],
                "evidence": citations or [], "depends_on": dependencies or []}

    def cite(self, ref, relation="supports"):
        return {"ref": ref, "start_line": 1, "end_line": 1, "relation": relation}

    def save(self):
        self.paper.write_text(json.dumps(self.record, ensure_ascii=False), encoding="utf-8")

    def build(self, *, refs=None, cited_only=True):
        return packet.create(self.store, refs or [], self.brief, self.out,
                             workpaper_path=self.paper, cited_only=cited_only)

    def test_complete_inquiry_survives_relocation_without_originals(self):
        original_report = workpaper.render(self.paper, self.store)
        original_brief = self.brief.read_bytes()
        original_inputs = {p.name: p.read_bytes() for p in self.store.iterdir()}
        paper_bytes = self.paper.read_bytes()
        receipt = self.build()
        self.assertEqual(receipt["schema"], "soundings.packet.v2")
        self.assertEqual(receipt["snapshots"], 2)
        self.assertEqual(original_inputs, {p.name: p.read_bytes() for p in self.store.iterdir()})
        self.assertEqual(self.paper.read_bytes(), paper_bytes)
        moved = self.root / "receiver"
        shutil.move(self.out, moved)
        shutil.rmtree(self.store)
        self.paper.unlink()
        self.brief.unlink()
        self.assertEqual(workpaper.render(moved / "workpaper.json", moved / "evidence"), original_report)
        self.assertEqual((moved / "brief.md").read_bytes(), original_brief)
        inventory = packet.inspect(moved)
        self.assertEqual(inventory["workpaper"]["finding_count"], 3)
        self.assertEqual(inventory["workpaper"]["cited_refs"], [self.ref, self.generated])
        self.assertEqual(inventory["workpaper"]["uncited_findings"], ["independent"])
        self.assertEqual(inventory["workpaper"]["dependency_warnings"][0]["finding"], "recommendation")
        self.assertEqual(inventory["snapshots"][1]["representation"], "generated")
        self.assertFalse((moved / "evidence" / (self.excluded + ".json")).exists())

    def test_explicit_selection_can_include_context_but_never_omit_citations(self):
        with self.assertRaisesRegex(evidence.EvidenceError, "omit workpaper citations"):
            self.build(refs=[self.ref], cited_only=False)
        self.assertFalse(self.out.exists())
        self.build(refs=[self.generated, self.excluded, self.ref], cited_only=False)
        result = packet.inspect(self.out)
        self.assertEqual([item["ref"] for item in result["snapshots"]],
                         [self.generated, self.excluded, self.ref])
        self.assertEqual(result["workpaper"]["cited_refs"], [self.ref, self.generated])

    def test_invalid_workpaper_and_receipt_budget_do_not_start_writing(self):
        self.record["findings"][0]["evidence"][0]["end_line"] = 200
        self.save()
        with self.assertRaises(evidence.EvidenceError):
            self.build()
        self.assertFalse(self.out.exists())
        self.record["findings"][0]["evidence"][0]["end_line"] = 1
        self.save()
        with self.assertRaises(evidence.EvidenceError):
            packet.create(self.store, [], self.brief, self.out, 10,
                          workpaper_path=self.paper, cited_only=True)
        self.assertFalse(self.out.exists())

    def test_uncited_authored_inquiry_is_explicit_without_fake_evidence(self):
        self.record["findings"] = [self.finding("proposal")]
        self.save()
        self.build()
        result = packet.inspect(self.out)
        self.assertEqual(result["snapshots"], [])
        self.assertEqual(result["workpaper"]["cited_refs"], [])
        self.assertEqual(result["workpaper"]["uncited_findings"], ["proposal"])
        self.assertEqual(list((self.out / "evidence").iterdir()), [])

    def test_workpaper_write_failure_has_no_completion_marker_or_implicit_repair(self):
        real_write = packet.write_new

        def fail_workpaper(path, content):
            if path.name == "workpaper.json":
                raise OSError("simulated interruption")
            real_write(path, content)

        with patch.object(packet, "write_new", side_effect=fail_workpaper):
            with self.assertRaisesRegex(OSError, "interruption"):
                self.build()
        self.assertFalse((self.out / "manifest.json").exists())
        with self.assertRaisesRegex(evidence.EvidenceError, "manifest missing"):
            packet.inspect(self.out)
        retained = sorted(p.name for p in self.out.iterdir())
        with self.assertRaises(FileExistsError):
            self.build()
        self.assertEqual(sorted(p.name for p in self.out.iterdir()), retained)

    def test_packet_member_cannot_redirect_the_workpaper_or_depend_on_links(self):
        self.build()
        manifest_path = self.out / "manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["workpaper"] = "../authored.json"
        manifest_path.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(evidence.EvidenceError, "manifest fields"):
            packet.inspect(self.out)
        manifest["workpaper"] = "workpaper.json"
        manifest_path.write_text(json.dumps(manifest))
        members = [self.out / "workpaper.json", self.out / "brief.md", manifest_path,
                   self.out / "evidence" / (self.ref + ".json")]
        for member in members:
            with self.subTest(member=member.name):
                content = member.read_bytes()
                external = self.root / "external"
                external.write_bytes(content)
                member.unlink()
                member.symlink_to(external)
                with self.assertRaisesRegex(evidence.EvidenceError, "regular file"):
                    packet.inspect(self.out)
                member.unlink()
                member.write_bytes(content)
        store = self.out / "evidence"
        moved = self.root / "linked-store"
        store.rename(moved)
        store.symlink_to(moved, target_is_directory=True)
        with self.assertRaisesRegex(evidence.EvidenceError, "local directory"):
            packet.inspect(self.out)

    def test_inspection_revalidates_citations_and_refuses_unselected_members(self):
        self.build()
        copied = self.out / "workpaper.json"
        changed = json.loads(copied.read_text())
        changed["findings"][0]["evidence"][0]["end_line"] = 999
        copied.write_text(json.dumps(changed))
        with self.assertRaises(evidence.EvidenceError):
            packet.inspect(self.out)
        copied.write_text(self.paper.read_text())
        extra = self.out / "unselected.txt"
        extra.write_text("Must not transfer.")
        with self.assertRaisesRegex(evidence.EvidenceError, "unexpected"):
            packet.inspect(self.out)

    def test_cli_explicit_selection_utf8_output_and_full_json_budget(self):
        cli = [sys.executable, str(Path(packet.__file__)), "create", "--store", str(self.store),
               "--brief", str(self.brief), "--output", str(self.out), "--cited"]
        bad = subprocess.run(cli, capture_output=True)
        self.assertEqual(bad.returncode, 2)
        self.assertEqual(bad.stdout, b"")
        self.assertFalse(self.out.exists())
        result = subprocess.run(cli + ["--workpaper", str(self.paper)], capture_output=True,
                                env={**os.environ, "PYTHONIOENCODING": "ascii:strict"})
        self.assertEqual(result.returncode, 0, result.stderr)
        show = [sys.executable, str(Path(packet.__file__)), "inspect", str(self.out)]
        result = subprocess.run(show, capture_output=True,
                                env={**os.environ, "PYTHONIOENCODING": "ascii:strict"})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["workpaper"]["outcome"], "有条件的建议")
        size = len(result.stdout)
        exact = subprocess.run(show + ["--max-bytes", str(size)], capture_output=True)
        self.assertEqual(exact.stdout, result.stdout)
        short = subprocess.run(show + ["--max-bytes", str(size - 1)], capture_output=True)
        self.assertEqual(short.returncode, 2)
        self.assertEqual(short.stdout, b"")

    def test_v1_recipient_still_needs_only_the_original_two_scripts(self):
        scripts = self.root / "two-scripts"
        scripts.mkdir()
        for module in (packet, evidence):
            shutil.copyfile(module.__file__, scripts / Path(module.__file__).name)
        command = [sys.executable, str(scripts / "packet.py")]
        created = subprocess.run(command + ["create", "--store", str(self.store),
                                 "--brief", str(self.brief), "--ref", self.ref,
                                 "--output", str(self.out)], capture_output=True,
                                 cwd=scripts, env={**os.environ, "PYTHONPATH": ""})
        self.assertEqual(created.returncode, 0, created.stderr)
        result = subprocess.run(command + ["inspect", str(self.out)], capture_output=True,
                                cwd=scripts, env={**os.environ, "PYTHONPATH": ""})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["schema"], "soundings.packet.v1")
        v2 = self.root / "v2"
        packet.create(self.store, [], self.brief, v2,
                      workpaper_path=self.paper, cited_only=True)
        missing = subprocess.run(command + ["inspect", str(v2)], capture_output=True,
                                 cwd=scripts, env={**os.environ, "PYTHONPATH": ""})
        self.assertEqual(missing.returncode, 2)
        self.assertEqual(missing.stdout, b"")
        self.assertIn(b"require adjacent workpaper.py", missing.stderr)
        self.assertNotIn(b"Traceback", missing.stderr)


if __name__ == "__main__":
    unittest.main()
