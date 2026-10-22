"""Counterexamples for content delivery, receipt binding and task-level counts."""
import json
from pathlib import Path
import tempfile
import unittest

import observe


class ObservationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.trace = self.root / "trace.jsonl"
        self.annotations = self.root / "annotations.json"
        self.events = [
            {"type": "item.completed", "item": {"type": "command_execution", "exit_code": 0,
             "command": "cat references/source.md", "aggregated_output": "v2 supports export.\nOnly local text is supported.\n"}},
            {"type": "item.completed", "item": {"type": "agent_message", "text": "Choose a local text route."}},
            {"type": "item.completed", "item": {"type": "file_change", "status": "completed", "path": "app.py"}},
        ]
        self.write_trace()

    def write_trace(self):
        self.trace.write_text("".join(json.dumps(event) + "\n" for event in self.events))

    def write_annotations(self, entries=None):
        if entries is None:
            entries = [{"kind": "content.delivered", "trace_line": 1,
                        "pointer": "/item/aggregated_output", "excerpt": "Only local text",
                        "representation": "extracted", "note": "visible qualifier"},
                       {"kind": "commitment", "trace_line": 2,
                        "pointer": "/item/text", "excerpt": "Choose a local", "note": "visible choice"}]
        self.annotations.write_text(json.dumps({"schema": observe.SCHEMA,
            "trace_sha256": observe.digest(self.trace), "events": entries}))

    def test_timeline_keeps_qualifier_and_order_without_claiming_application(self):
        self.write_annotations()
        result = observe.timeline(self.trace, self.annotations)
        self.assertTrue(result["delivery_before_commitment"])
        self.assertEqual(result["events"][0]["excerpt"], "Only local text")
        self.assertEqual(result["content_application"], "requires-semantic-review")
        self.assertEqual(result["host_selection"], "unknown")

    def test_command_path_cannot_be_content_delivery(self):
        self.write_annotations([{"kind": "content.delivered", "trace_line": 1,
            "pointer": "/item/command", "excerpt": "references/source.md",
            "representation": "verbatim", "note": "path was mentioned"}])
        with self.assertRaisesRegex(ValueError, "successful tool output"):
            observe.timeline(self.trace, self.annotations)

    def test_self_report_cannot_be_content_delivery(self):
        self.write_annotations([{"kind": "content.delivered", "trace_line": 2,
            "pointer": "/item/text", "excerpt": "Choose", "representation": "unknown", "note": "claim"}])
        with self.assertRaises(ValueError):
            observe.timeline(self.trace, self.annotations)

    def test_failed_command_cannot_prove_delivery(self):
        self.events[0]["item"]["exit_code"] = 1
        self.write_trace()
        self.write_annotations()
        with self.assertRaises(ValueError):
            observe.timeline(self.trace, self.annotations)

    def test_mcp_success_output_is_anchored_but_arguments_are_not(self):
        self.events[0] = {"type": "item.completed", "item": {"type": "mcp_tool_call",
            "status": "completed", "result": {"content": [{"type": "text", "text": "Only local text"}]}}}
        self.write_trace()
        self.write_annotations([{"kind": "content.delivered", "trace_line": 1,
            "pointer": "/item/result/content/0/text", "excerpt": "Only local text",
            "representation": "unknown", "note": "MCP response"}])
        self.assertIsNone(observe.timeline(self.trace, self.annotations)["delivery_before_commitment"])
        self.events[0]["item"]["result"]["isError"] = True
        self.write_trace()
        self.write_annotations([{"kind": "content.delivered", "trace_line": 1,
            "pointer": "/item/result/content/0/text", "excerpt": "Only local text",
            "representation": "unknown", "note": "MCP response"}])
        with self.assertRaises(ValueError):
            observe.timeline(self.trace, self.annotations)

    def test_trace_drift_and_false_excerpt_are_rejected(self):
        self.write_annotations()
        self.trace.write_text(self.trace.read_text() + "{}\n")
        with self.assertRaisesRegex(ValueError, "binding mismatch"):
            observe.timeline(self.trace, self.annotations)
        self.write_annotations([{"kind": "commitment", "trace_line": 2,
            "pointer": "/item/text", "excerpt": "invented", "note": "bad anchor"}])
        with self.assertRaisesRegex(ValueError, "absent"):
            observe.timeline(self.trace, self.annotations)

    def test_successful_mcp_metadata_path_is_not_content_delivery(self):
        self.events[0] = {"type": "item.completed", "item": {"type": "mcp_tool_call",
            "status": "completed", "result": {"content": [], "_meta": {"path": "reference.md"}}}}
        self.write_trace()
        self.write_annotations([{"kind": "content.delivered", "trace_line": 1,
            "pointer": "/item/result/_meta/path", "excerpt": "reference.md",
            "representation": "unknown", "note": "A path is not returned source content."}])
        with self.assertRaisesRegex(ValueError, "successful tool output"):
            observe.timeline(self.trace, self.annotations)

    def test_duplicate_events_and_nonexistent_lines_are_rejected(self):
        entry = {"kind": "commitment", "trace_line": 2, "pointer": "/item/text", "excerpt": "Choose", "note": "choice"}
        self.write_annotations([entry, entry])
        with self.assertRaisesRegex(ValueError, "duplicate"):
            observe.timeline(self.trace, self.annotations)
        entry["trace_line"] = 100
        self.write_annotations([entry])
        with self.assertRaisesRegex(ValueError, "invalid trace line"):
            observe.timeline(self.trace, self.annotations)

    def receipt(self, attempt="one", case="open", subject="current", outcome="pass"):
        path = self.root / f"{attempt}.json"
        path.write_text(json.dumps({"schema_version": 2, "receipt_type": "attempt", "lab_id": "research",
            "case_id": case, "subject_id": subject, "attempt_id": attempt, "outcome": outcome,
            "target_agent_invocations": 1, "subject_delivery": {"status": "verified"},
            "verification_summary": {"human_review": {"required": True,
                "requirements": ["Apply the qualifier and preserve the independent constraint."]}}}))
        return path

    def review(self, receipt, judgment="supported"):
        path = self.root / (receipt.stem + "-review.json")
        path.write_text(json.dumps({"schema_version": 2, "method": "human", "independence": "separate-agent",
            "receipt": {"path": str(receipt), "sha256": observe.digest(receipt)},
            "judgment": judgment, "rationale": "Constructed test only.",
            "requirement_outcomes": {"Apply the qualifier and preserve the independent constraint.": judgment}}))
        return path

    def test_structure_pass_and_delivery_still_need_semantic_review(self):
        path = self.receipt()
        result = observe.compare([path], [])
        self.assertEqual(result["attempts"][0]["execution_outcome"], "pass")
        self.assertEqual(result["attempts"][0]["semantic_review"], "pending")
        self.assertEqual(observe.review_template(path)["status"], "pending")

    def test_bound_semantic_rejection_is_distinct_from_structural_pass(self):
        receipt = self.receipt()
        review = self.review(receipt, "not-supported")
        row = observe.compare([receipt], [review])["attempts"][0]
        self.assertEqual(row["semantic_review"], "not-supported")
        self.assertEqual(row["execution_outcome"], "pass")

    def test_stale_review_rejected(self):
        receipt = self.receipt()
        review = self.review(receipt)
        receipt.write_text(receipt.read_text() + "\n")
        with self.assertRaisesRegex(ValueError, "stale"):
            observe.compare([receipt], [review])

    def test_wrong_requirement_or_receipt_path_rejected(self):
        receipt = self.receipt()
        review = self.review(receipt)
        data = json.loads(review.read_text())
        data["requirement_outcomes"] = {"plausible substitute": "supported"}
        review.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, "exact receipt requirements"):
            observe.compare([receipt], [review])
        review = self.review(receipt)
        data = json.loads(review.read_text())
        data["receipt"]["path"] = str(self.root / "unrelated.json")
        review.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, "path mismatch"):
            observe.compare([receipt], [review])

    def test_repeated_runs_stay_inside_task_groups_and_timeouts_remain_visible(self):
        receipts = [self.receipt("one"), self.receipt("two", outcome="timeout"),
                    self.receipt("three", subject="old"), self.receipt("four", case="small")]
        result = observe.compare(receipts, [])
        self.assertEqual(len(result["task_groups"]), 3)
        group = next(row for row in result["task_groups"] if row["repetitions"] == 2)
        self.assertEqual(group["execution_outcomes"], ["pass", "timeout"])

    def test_duplicate_receipt_or_attempt_cannot_inflate_sample(self):
        receipt = self.receipt()
        with self.assertRaisesRegex(ValueError, "duplicate receipt"):
            observe.compare([receipt, receipt], [])
        other = self.root / "other.json"
        other.write_text(receipt.read_text() + "\n")
        with self.assertRaisesRegex(ValueError, "duplicate receipt content"):
            observe.compare([receipt, other], [])

    def test_fieldlab_attempt_names_can_repeat_across_cases_and_repetitions(self):
        first = self.receipt("one")
        second = self.receipt("two")
        a = json.loads(first.read_text())
        b = json.loads(second.read_text())
        a.update(attempt_id="attempt-1", created_at="2026-01-01T00:00:00Z")
        b.update(attempt_id="attempt-1", created_at="2026-01-01T00:01:00Z")
        first.write_text(json.dumps(a))
        second.write_text(json.dumps(b))
        self.assertEqual(observe.compare([first, second], [])["task_groups"][0]["repetitions"], 2)

    def test_conflicting_reviews_need_adjudication(self):
        receipt = self.receipt()
        review = self.review(receipt)
        with self.assertRaisesRegex(ValueError, "multiple reviews"):
            observe.compare([receipt], [review, review])

    def test_inconsistent_positive_review_cannot_pass(self):
        receipt = self.receipt()
        review = self.review(receipt)
        data = json.loads(review.read_text())
        data["requirement_outcomes"] = {key: "inconclusive" for key in data["requirement_outcomes"]}
        review.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, "contradicts"):
            observe.compare([receipt], [review])


if __name__ == "__main__":
    unittest.main()
