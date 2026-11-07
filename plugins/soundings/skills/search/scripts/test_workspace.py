"""End-to-end continuation, exact data and failure boundaries."""

from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import evidence
from evidence import EvidenceError, encode
import workspace as w


SCRIPT = Path(w.__file__)


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.root = self.folder / "inquiry"
        w.init(self.root, "完整说明与作品", "什么条件决定方向？", "观察原材料", "project/current-state.md")
        self.input = self.folder / "source.txt"
        self.input.write_bytes("短\r\n决定条件\n\n例外：不在范围内\r\n".encode())

    def capture(self, **options):
        return w.capture_source(self.root, self.input, "https://example.org/source", "条件", "extracted", **options)["ref"]

    def files(self, root=None):
        root = root or self.root
        return {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}

    def cli(self, command, *args, root=None, ok=True):
        result = subprocess.run([sys.executable, str(SCRIPT), command, "--workspace", str(root or self.root), *args],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
        if ok:
            self.assertEqual(result.returncode, 0, result.stderr.decode())
        else:
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, b"")
        return result

    def test_cli_full_commission_in_new_processes(self):
        lead = json.loads(self.cli("lead", "--locator", "https://example.org/source", "--title", "正文", "--why", "决定方向").stdout)["id"]
        ref = json.loads(self.cli("capture", "--file", str(self.input), "--source", "https://example.org/source", "--title", "正文",
                                  "--representation", "extracted", "--via", "host reader", "--lead", lead).stdout)["ref"]
        self.cli("read", "--ref", ref, "--start-line", "2", "--end-line", "4")
        self.cli("update", "--question", "如何保留这项限定？", "--next-action", "写成完整说明", "--settled", "离线使用")
        result_file = self.folder / "guide.md"
        result_file.write_text("# 说明\n离线使用；保留限定。\n")
        first = json.loads(self.cli("artifact", "--file", str(result_file), "--name", "guide.md", "--kind", "explanation", "--ref", ref).stdout)["id"]
        feedback = json.loads(self.cli("feedback", "--artifact", first, "--text", "解释恢复路径").stdout)["id"]
        result_file.write_text("# 说明\n离线使用；保留限定。\n恢复：先检查本地导出，再导入。\n")
        second = json.loads(self.cli("artifact", "--file", str(result_file), "--name", "guide.md", "--kind", "explanation", "--supersedes", first).stdout)["id"]
        receipt = json.loads(self.cli("resolve", "--feedback", feedback, "--artifact", second, "--resolution", "补上恢复步骤，离线要求仍保留").stdout)
        self.assertFalse(receipt["semantic_correction_verified"])
        state = json.loads(self.cli("resume", "--max-bytes", "32768").stdout)["state"]
        self.assertEqual(state["sources"][ref]["delivered"], [[2, 4]])
        self.assertEqual(state["leads"][lead]["status"], "partial")
        self.assertEqual(state["settled"], ["离线使用"])
        self.assertEqual(state["feedback"][feedback]["successor"], second)
        self.assertEqual(len(state["artifacts"]), 2)
        text = self.cli("resume", "--format", "markdown", "--max-bytes", "32768").stdout.decode()
        self.assertIn("如何保留这项限定？", text)
        self.assertIn("[2, 4]", text)
        self.assertIn("恢复步骤", text)

    def test_only_returned_windows_count_and_exact_unicode_survives(self):
        ref = self.capture()
        payload = w.read_source(self.root, ref, start_line=1, end_line=4)
        self.assertEqual(payload["ranges"][0]["text"], self.input.read_bytes().decode())
        self.input.write_text("hit " + "大" * 1200 + "\nspacer\nhit small\n")
        other = self.capture()
        found = w.read_source(self.root, other, query="hit", context=0, max_bytes=850)
        self.assertFalse(found["complete"])
        returned = [[r["start_line"], r["end_line"]] for r in found["ranges"]]
        self.assertEqual(w.load_state(self.root)["sources"][other]["delivered"], returned)
        self.assertNotIn([1, 1], returned)
        self.assertLessEqual(len(encode(found, 850)), 850)

    def test_corpus_search_never_changes_reading(self):
        ref = self.capture()
        before = self.files()
        found = w.search(self.root, "决定")
        self.assertEqual(found["matching_sources"], 1)
        self.assertEqual(found["hits"][0]["snapshot"]["ref"], ref)
        self.assertFalse(found["reading_recorded"])
        self.assertEqual(self.files(), before)

    def test_failed_budget_and_invalid_input_do_not_change_workspace(self):
        ref = self.capture()
        before = self.files()
        for action in [lambda: w.read_source(self.root, ref, max_bytes=1),
                       lambda: w.capture_source(self.root, self.input, "url", "title", "verbatim", max_bytes=1),
                       lambda: w.update(self.root, {"question": "changed"}, max_bytes=1),
                       lambda: w.read_source(self.root, ref, start_line=999),
                       lambda: w.lead(self.root, locator="url", title="blocked", why="reason", status="blocked")]:
            with self.subTest(action=action), self.assertRaises(EvidenceError):
                action()
            self.assertEqual(self.files(), before)

    def test_stale_revision_and_writer_lock_preserve_state(self):
        before = self.files()
        with self.assertRaisesRegex(EvidenceError, "stale"):
            w.update(self.root, {"question": "wrong"}, expect_revision=0)
        self.assertEqual(self.files(), before)
        (self.root / ".lock").write_text("an owner must be inspected")
        with self.assertRaisesRegex(EvidenceError, "lock"):
            w.update(self.root, {"question": "wrong"})
        self.assertEqual((self.root / ".lock").read_text(), "an owner must be inspected")
        self.assertEqual(w.load_state(self.root)["question"], "什么条件决定方向？")

    def test_two_processes_cannot_commit_the_same_expected_revision(self):
        processes = [subprocess.Popen([sys.executable, str(SCRIPT), "update", "--workspace", str(self.root),
                                       "--expect-revision", "1", "--question", question],
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                     for question in ("one", "two")]
        results = [(process.communicate(), process.returncode) for process in processes]
        self.assertEqual(sorted(code for _, code in results), [0, 2])
        state = w.load_state(self.root)
        self.assertEqual(state["revision"], 2)
        self.assertIn(state["question"], ("one", "two"))

    def test_relocation_preserves_basis_and_allows_new_work(self):
        ref = self.capture()
        result = w.artifact(self.root, self.input, "piece.txt", "creative")["id"]
        lead = w.lead(self.root, locator="https://example.org/unread", title="未读", why="不同机制")["id"]
        w.read_source(self.root, ref, start_line=2, end_line=2)
        original = self.files()
        target = self.folder / "receiver"
        w.fork(self.root, target)
        self.assertEqual(self.files(target), original)
        moved = self.folder / "unavailable-original"
        self.root.rename(moved)
        self.input.rename(self.folder / "unavailable-input")
        data = json.loads(self.cli("resume", root=target, *["--max-bytes", "32768"]).stdout)["state"]
        self.assertEqual(data["leads"][lead]["status"], "unread")
        self.assertEqual(data["sources"][ref]["delivered"], [[2, 2]])
        self.assertEqual((target / "artifacts" / data["artifacts"][result]["path"]).read_bytes(), "短\r\n决定条件\n\n例外：不在范围内\r\n".encode())
        w.update(target, {"next_action": "继续尚未完成的作品"})
        self.assertEqual(self.files(moved), original)

    def test_feedback_requires_actual_descendant_and_retains_old_result(self):
        first = w.artifact(self.root, self.input, "piece.txt", "creative")["id"]
        item = w.feedback(self.root, first, "保留结尾，但改变选择关系")["id"]
        unrelated = w.artifact(self.root, self.input, "another.txt", "creative")["id"]
        before = self.files()
        for successor in (first, unrelated, "unknown"):
            with self.assertRaises(EvidenceError):
                w.resolve(self.root, item, successor, "changed")
            self.assertEqual(self.files(), before)
        with self.assertRaisesRegex(EvidenceError, "unchanged"):
            w.artifact(self.root, self.input, "piece.txt", "creative", supersedes=first)
        self.input.write_bytes(b"new relationship; same ending\x00\xff")
        second = w.artifact(self.root, self.input, "piece.txt", "creative", supersedes=first)["id"]
        w.resolve(self.root, item, second, "Changed the actual relationship; retained ending")
        state = w.load_state(self.root)
        self.assertNotEqual((self.root / "artifacts" / state["artifacts"][first]["path"]).read_bytes(), self.input.read_bytes())
        self.assertEqual((self.root / "artifacts" / state["artifacts"][second]["path"]).read_bytes(), self.input.read_bytes())

    def test_malformed_latest_revision_is_not_hidden_by_old_success(self):
        path = self.root / "revisions" / "00000002.json"
        path.write_text('{"revision":2')
        self.cli("resume", ok=False)
        with self.assertRaises(EvidenceError):
            w.fork(self.root, self.folder / "bad-copy", recover_unreferenced=True)
        self.assertFalse((self.folder / "bad-copy").exists())

    def test_loaded_declarations_cannot_redirect_paths_or_invent_reading(self):
        ref = self.capture()
        result = w.artifact(self.root, self.input, "guide.md", "explanation")["id"]
        original = w.load_state(self.root)
        path = self.root / "revisions" / w._revision_name(original["revision"])
        for mutate in (lambda state: state["artifacts"][result].update(path="../../outside"),
                       lambda state: state["sources"][ref].update(delivered=[[1, 999]]),
                       lambda state: state.update(revision=True),
                       lambda state: state["sources"][ref].update(derived_from=ref)):
            altered = deepcopy(original)
            mutate(altered)
            path.write_bytes(w._json_bytes(altered))
            with self.assertRaises(EvidenceError):
                w.load_state(self.root)
        path.write_bytes(w._json_bytes(original))
        self.assertEqual(w.load_state(self.root), original)

    def test_symlink_and_path_redirection_rejected(self):
        ref = self.capture()
        source = self.root / "evidence" / (ref + ".json")
        external = self.folder / "external.json"
        source.rename(external)
        source.symlink_to(external)
        with self.assertRaises(EvidenceError):
            w.load_state(self.root)
        for name in ("../escape", "/absolute", ".hidden", "a/b", "a\\b"):
            with self.subTest(name=name), self.assertRaises(EvidenceError):
                w.artifact(self.root, self.input, name, "other")
        self.assertFalse((self.folder / "escape").exists())

    def test_orphan_recovery_is_an_explicit_copy_without_deletion(self):
        self.capture()
        orphan = self.root / "artifacts" / "uncommitted.txt"
        orphan.write_bytes(b"preserve for diagnosis")
        with self.assertRaisesRegex(EvidenceError, "unreferenced"):
            w.resume(self.root)
        output = self.folder / "recovered"
        receipt = w.fork(self.root, output, recover_unreferenced=True)
        self.assertEqual(receipt["not_copied_unreferenced"], ["artifacts/uncommitted.txt"])
        self.assertTrue(orphan.exists())
        w.load_state(output)
        existing = self.folder / "existing"
        existing.mkdir()
        with self.assertRaises(FileExistsError):
            w.fork(output, existing)

    def test_publish_failure_rolls_back_only_new_uncommitted_members(self):
        before = self.files()
        publish = w._publish
        def fail_revision(path, content):
            if path.parent.name == "revisions":
                raise OSError("injected revision write failure")
            publish(path, content)
        with patch.object(w, "_publish", side_effect=fail_revision), self.assertRaises(OSError):
            self.capture()
        self.assertEqual(self.files(), before)

    def test_fork_must_not_create_a_member_inside_original(self):
        before = self.files()
        with self.assertRaises(EvidenceError):
            w.fork(self.root, self.root / "nested")
        self.assertFalse((self.root / "nested").exists())
        self.assertEqual(self.files(), before)


if __name__ == "__main__":
    unittest.main()
