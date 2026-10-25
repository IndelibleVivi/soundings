"""Revision review retains earlier grounds without inventing cross-version paths."""

import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import evidence
import workpaper


class ComparisonTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.before_store = self.root / "earlier-store"
        self.after_store = self.root / "later-store"
        self.before_store.mkdir()
        self.after_store.mkdir()
        self.before = self.root / "before.json"
        self.after = self.root / "after.json"

    def finding(self, identifier, *, deps=(), cites=(), text=None):
        return {"id": identifier, "kind": "judgment", "text": text or identifier,
                "status": "current", "conditions": [], "evidence": list(cites),
                "depends_on": list(deps)}

    def record(self, *findings):
        return {"schema": workpaper.SCHEMA, "outcome": "Keep a usable explanation.",
                "question": "Which grounds changed?", "findings": list(findings)}

    def write(self, before, after):
        for path, data in ((self.before, before), (self.after, after)):
            path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def compare(self, before, after):
        self.write(before, after)
        return workpaper.compare(self.before, self.after, self.before_store, self.after_store)

    def capture(self, store, text="限定 A。\r\nSecond line.\r\n"):
        source = self.root / "input.txt"
        source.write_bytes(text.encode())
        return evidence.capture(source, store, "https://example.org/release", "同一标题",
                                "verbatim", 8192)["snapshot"]["ref"]

    def cite(self, ref, **fields):
        return {"ref": ref, "start_line": 1, "end_line": 1, "relation": "supports", **fields}

    def effects(self, result, premise, version):
        return next(item for item in result["dependency_effects"]
                    if item["premise"] == premise and item["version"] == version)

    def tree(self):
        return {str(path.relative_to(self.root)): path.read_bytes()
                for path in self.root.rglob("*") if path.is_file()}

    def test_same_normalized_declarations_are_unchanged_and_read_only(self):
        ref = self.capture(self.before_store)
        shutil.copyfile(self.before_store / (ref + ".json"), self.after_store / (ref + ".json"))
        before = self.record(self.finding("same", cites=[self.cite(ref)]))
        after = copy.deepcopy(before)
        after["open_questions"] = []
        after["findings"][0]["evidence"][0]["note"] = ""
        self.write(before, after)
        original = self.tree()
        result = workpaper.compare(self.before, self.after, self.before_store, self.after_store)
        self.assertEqual(self.tree(), original)
        self.assertEqual(result["findings"]["changed"], [])
        self.assertEqual([item["id"] for item in result["findings"]["unchanged"]], ["same"])
        self.assertEqual(result["global_changes"]["changed_fields"], [])
        self.assertEqual(result["dependency_effects"], [])
        self.assertEqual(result["snapshot_conflicts"], [])
        self.assertFalse(result["project_artifacts_changed"])

    def test_every_finding_field_and_global_change_remains_explicit(self):
        ref = self.capture(self.before_store)
        shutil.copyfile(self.before_store / (ref + ".json"), self.after_store / (ref + ".json"))
        before = self.record(self.finding("premise", cites=[self.cite(ref)]),
                             self.finding("independent"), self.finding("guide", deps=["premise"]))
        after = copy.deepcopy(before)
        after.update(outcome="A revised outcome.", question="A different question.", open_questions=["Still unknown?"])
        changed = after["findings"][0]
        changed.update(kind="inference", text="New conditional interpretation.", status="superseded",
                       conditions=["Release B only."], depends_on=["independent"])
        changed["evidence"][0].update(end_line=2, relation="challenges", note="A deciding challenge.")
        result = self.compare(before, after)
        delta = result["findings"]["changed"][0]
        self.assertEqual(set(delta["changed_fields"]), {"kind", "text", "status", "conditions", "evidence", "depends_on"})
        self.assertEqual(delta["after"], changed)
        self.assertEqual(set(result["global_changes"]["changed_fields"]), {"outcome", "question", "open_questions"})
        self.assertEqual({x["id"] for x in result["findings"]["unchanged"]}, {"independent", "guide"})
        for version in ("before", "after"):
            self.assertEqual(self.effects(result, "premise", version)["descendants"][0]["witness_path"], ["premise", "guide"])

    def test_removed_intermediary_keeps_earlier_guide_path_after_rewiring(self):
        before = self.record(self.finding("premise", text="Old grounds."),
                             self.finding("middle", deps=["premise"]),
                             self.finding("guide", deps=["middle"], text="An actual guide still needs review."),
                             self.finding("offline"))
        after = self.record(self.finding("premise", text="New grounds."),
                            self.finding("guide", text="An actual guide still needs review."),
                            self.finding("offline"))
        result = self.compare(before, after)
        old_paths = self.effects(result, "premise", "before")["descendants"]
        self.assertEqual(next(x for x in old_paths if x["id"] == "guide")["witness_path"], ["premise", "middle", "guide"])
        self.assertEqual(self.effects(result, "premise", "after")["descendants"], [])
        self.assertEqual(self.effects(result, "middle", "before")["descendants"][0]["id"], "guide")
        self.assertEqual([x["id"] for x in result["findings"]["removed"]], ["middle"])
        self.assertIn("offline", [x["id"] for x in result["findings"]["unchanged"]])
        self.assertFalse(any(x["premise"] == "offline" for x in result["dependency_effects"]))
        self.assertFalse(result["project_artifacts_changed"])

    def test_no_path_or_cycle_can_be_invented_by_mixing_versions(self):
        before = self.record(self.finding("root", text="Before"), self.finding("bridge", deps=["root"]),
                             self.finding("leaf"))
        after = self.record(self.finding("root", text="After"), self.finding("bridge"),
                            self.finding("leaf", deps=["bridge"]))
        result = self.compare(before, after)
        self.assertEqual([x["id"] for x in self.effects(result, "root", "before")["descendants"]], ["bridge"])
        self.assertEqual(self.effects(result, "root", "after")["descendants"], [])
        before = self.record(self.finding("a", deps=["b"]), self.finding("b"))
        after = self.record(self.finding("a"), self.finding("b", deps=["a"]))
        result = self.compare(before, after)
        self.assertEqual(self.effects(result, "b", "before")["descendants"][0]["witness_path"], ["b", "a"])
        self.assertEqual(self.effects(result, "a", "after")["descendants"][0]["witness_path"], ["a", "b"])

    def test_shared_ref_conflict_reaches_dependents_despite_unchanged_findings(self):
        ref = self.capture(self.before_store)
        payload = json.loads((self.before_store / (ref + ".json")).read_text())
        payload.update(content="限定 B。\r\nChanged line.\r\n", title="Different title", source="constructed:changed",
                       representation="generated", captured_at="2026-10-25T00:00:00+00:00")
        (self.after_store / (ref + ".json")).write_text(json.dumps(payload), encoding="utf-8")
        paper = self.record(self.finding("premise", cites=[self.cite(ref)]), self.finding("guide", deps=["premise"]))
        result = self.compare(paper, copy.deepcopy(paper))
        self.assertEqual(result["findings"]["changed"], [])
        conflict = result["snapshot_conflicts"][0]
        self.assertEqual(set(conflict["changed_fields"]), {"content", "title", "source", "representation", "captured_at"})
        self.assertEqual(conflict["after"]["content"], payload["content"])
        self.assertEqual(conflict["before_citations"][0]["finding"], "premise")
        for version in ("before", "after"):
            effect = self.effects(result, "premise", version)
            self.assertEqual(effect["change"], "snapshot_conflict")
            self.assertEqual(effect["conflicting_refs"], [ref])
            self.assertEqual(effect["descendants"][0]["witness_path"], ["premise", "guide"])

    def test_ids_and_refs_are_not_matched_by_equal_text_title_or_locator(self):
        first = self.capture(self.before_store)
        second = self.capture(self.after_store, "A different snapshot of the same URL.\n")
        before = self.record(self.finding("premise", cites=[self.cite(first)]), self.finding("old-id", text="Same authored text."))
        after = self.record(self.finding("premise", cites=[self.cite(second)]), self.finding("new-id", text="Same authored text."),
                            self.finding("new-dependent", deps=["new-id"]))
        result = self.compare(before, after)
        self.assertEqual(result["snapshot_conflicts"], [])
        self.assertEqual([x["id"] for x in result["findings"]["removed"]], ["old-id"])
        self.assertEqual([x["id"] for x in result["findings"]["added"]], ["new-id", "new-dependent"])
        self.assertEqual(result["findings"]["changed"][0]["changed_fields"], ["evidence"])
        self.assertEqual(self.effects(result, "new-id", "after")["descendants"][0]["id"], "new-dependent")

    def test_ordering_is_separate_from_content_and_new_questions_are_not_reorders(self):
        before = self.record(self.finding("a"), self.finding("b"))
        before["open_questions"] = ["A?", "B?"]
        after = copy.deepcopy(before)
        after["findings"].reverse()
        after["open_questions"].reverse()
        result = self.compare(before, after)
        self.assertEqual(result["findings"]["changed"], [])
        self.assertEqual(result["dependency_effects"], [])
        self.assertTrue(result["ordering"]["findings"]["common_reordered"])
        self.assertTrue(result["ordering"]["open_questions"]["reordered"])
        after["findings"] = [self.finding("new"), *before["findings"]]
        after["open_questions"] = ["A?", "New question?"]
        result = self.compare(before, after)
        self.assertFalse(result["ordering"]["findings"]["common_reordered"])
        self.assertTrue(result["ordering"]["findings"]["moved_common"])
        self.assertTrue(result["ordering"]["open_questions"]["sequence_changed"])
        self.assertFalse(result["ordering"]["open_questions"]["reordered"])

    def test_both_revisions_must_validate_before_comparison(self):
        ref = self.capture(self.before_store)
        shutil.copyfile(self.before_store / (ref + ".json"), self.after_store / (ref + ".json"))
        valid = self.record(self.finding("a", cites=[self.cite(ref)]))
        invalid = []
        value = copy.deepcopy(valid)
        value["findings"][0]["evidence"][0]["end_line"] = 200
        invalid.append(value)
        invalid.append(self.record(self.finding("a", deps=["b"]), self.finding("b", deps=["a"])))
        invalid.append(self.record(self.finding("a", deps=["absent"])))
        value = copy.deepcopy(valid)
        value["findings"][0]["evidence"][0]["ref"] = "s-" + "0" * 32
        invalid.append(value)
        for index, bad in enumerate(invalid):
            for side in ("before", "after"):
                with self.subTest(case=index, side=side):
                    self.write(bad if side == "before" else valid, bad if side == "after" else valid)
                    with self.assertRaises(evidence.EvidenceError):
                        workpaper.compare(self.before, self.after, self.before_store, self.after_store)

    def test_reversed_deep_chain_retains_shortest_paths_without_recursion(self):
        count = 1100
        findings = [self.finding(f"f{i}", deps=[f"f{i-1}"] if i else []) for i in range(count)]
        before = self.record(*reversed(findings))
        after = copy.deepcopy(before)
        after["findings"][-1]["text"] = "The root changed."
        result = self.compare(before, after)
        for version in ("before", "after"):
            paths = self.effects(result, "f0", version)["descendants"]
            self.assertEqual(len(paths), count - 1)
            self.assertEqual(paths[-1]["witness_path"], [f"f{i}" for i in range(count)])

    def test_cli_utf8_crlf_read_only_and_clean_validation_failure(self):
        before = self.record(self.finding("a", text="旧判断。\r\n原条件。"))
        after = self.record(self.finding("a", text="新判断。\r\n保留界限。"))
        self.write(before, after)
        original = self.tree()
        command = [sys.executable, str(Path(workpaper.__file__)), "compare", str(self.before), str(self.after),
                   "--before-store", str(self.before_store), "--after-store", str(self.after_store)]
        result = subprocess.run(command, capture_output=True,
                                env={**os.environ, "PYTHONIOENCODING": "ascii:strict"})
        self.assertEqual(result.returncode, 0, result.stderr)
        delta = json.loads(result.stdout)["findings"]["changed"][0]
        self.assertEqual(delta["before"]["text"], before["findings"][0]["text"])
        self.assertEqual(delta["after"]["text"], after["findings"][0]["text"])
        self.assertEqual(self.tree(), original)
        after["findings"][0]["depends_on"] = ["unknown"]
        self.write(before, after)
        result = subprocess.run(command, capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, b"")
        self.assertNotIn(b"Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
