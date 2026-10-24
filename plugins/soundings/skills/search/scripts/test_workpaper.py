"""Observable behavior checks for authored evidence-linked workpapers."""

from __future__ import annotations

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
import packet
import workpaper


SCRIPT_DIR = Path(__file__).resolve().parent
EVIDENCE_CLI = SCRIPT_DIR / "evidence.py"
WORKPAPER_CLI = SCRIPT_DIR / "workpaper.py"
ENV = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}


class WorkpaperTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.store = self.root / "store"
        self.sources = self.root / "sources"
        self.sources.mkdir()

    def run_cli(self, script: Path, *args: object) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(script), *(str(arg) for arg in args)],
            capture_output=True,
            env=ENV,
        )

    def capture_cli(
        self,
        text: str,
        *,
        title: str = "Source",
        source: str = "https://example.org/source",
        representation: str = "verbatim",
    ) -> str:
        path = self.sources / f"source-{len(list(self.sources.iterdir()))}.md"
        path.write_bytes(text.encode("utf-8"))
        result = self.run_cli(
            EVIDENCE_CLI,
            "capture",
            path,
            "--store",
            self.store,
            "--source",
            source,
            "--title",
            title,
            "--representation",
            representation,
        )
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        return json.loads(result.stdout)["snapshot"]["ref"]

    def capture_api(
        self,
        text: str,
        *,
        title: str = "Source",
        source: str = "https://example.org/source",
        representation: str = "verbatim",
    ) -> str:
        path = self.sources / f"source-{len(list(self.sources.iterdir()))}.md"
        path.write_bytes(text.encode("utf-8"))
        result = evidence.capture(
            path, self.store, source, title, representation, 8192
        )
        return result["snapshot"]["ref"]

    def write_record(self, name: str, record: dict) -> Path:
        path = self.root / name
        path.write_text(
            json.dumps(record, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="",
        )
        return path

    @staticmethod
    def base_record(findings: list[dict], **overrides) -> dict:
        record = {
            "schema": workpaper.SCHEMA,
            "outcome": "Choose a safe image-export policy.",
            "question": "Is image export really paid-plan-only?",
            "findings": findings,
            "open_questions": ["Does the exception expire?"],
        }
        record.update(overrides)
        return record

    @staticmethod
    def finding(
        finding_id: str,
        *,
        kind: str = "observation",
        text: str | None = None,
        status: str = "current",
        conditions: list[str] | None = None,
        citations: list[dict] | None = None,
        depends_on: list[str] | None = None,
    ) -> dict:
        return {
            "id": finding_id,
            "kind": kind,
            "text": text or f"Authored {finding_id}.",
            "status": status,
            "conditions": conditions or [],
            "evidence": citations or [],
            "depends_on": depends_on or [],
        }

    @staticmethod
    def citation(
        ref: str,
        start: int,
        end: int,
        relation: str = "supports",
        note: str = "",
    ) -> dict:
        return {
            "ref": ref,
            "start_line": start,
            "end_line": end,
            "relation": relation,
            "note": note,
        }

    def test_cli_journey_relocates_renders_and_traces_declared_impact(self):
        policy = self.capture_cli(
            "# Export policy\n"
            "Public export is available.\n"
            "Images are not available on the free plan.\n",
            title="Export policy",
            source="https://example.org/export-policy",
            representation="extracted",
        )
        migration = self.capture_cli(
            "# Migration note\r\n\r\n"
            "Free plans may export images during migration.\r\n"
            "Only selected images are covered.\r\n",
            title="迁移说明",
            source="https://example.org/migration",
            representation="verbatim",
        )
        generated = self.capture_cli(
            "A supplied synthesis: migration may be temporary.\n",
            title="Earlier synthesis",
            source="generated://earlier-study",
            representation="generated",
        )
        findings = [
            self.finding(
                "f-policy",
                text="The guide currently says free plans cannot export images.",
                conditions=["Current public policy wording."],
                citations=[
                    self.citation(
                        policy, 2, 3, "supports", "The second line narrows the offer."
                    )
                ],
            ),
            self.finding(
                "f-migration",
                text="A migration note gives free plans a limited image exception.",
                conditions=["During migration."],
                citations=[
                    self.citation(
                        migration,
                        3,
                        4,
                        "challenges",
                        "This conflicts with the unqualified public wording.",
                    )
                ],
            ),
            self.finding(
                "f-synthesis",
                kind="inference",
                text="The apparent conflict may be limited to migration.",
                conditions=["Migration is temporary.", "Only selected images qualify."],
                citations=[
                    self.citation(
                        generated,
                        1,
                        1,
                        "context",
                        "Generated synthesis, not independent evidence.",
                    )
                ],
                depends_on=["f-policy", "f-migration"],
            ),
            self.finding(
                "f-unrelated",
                kind="proposal",
                text="Run a separate accessibility review.",
            ),
        ]
        record = self.base_record(findings)
        workpaper_path = self.write_record("workpaper.json", record)
        workpaper_before = workpaper_path.read_bytes()
        store_before = {
            path.name: path.read_bytes() for path in self.store.iterdir() if path.is_file()
        }

        inspected = self.run_cli(
            WORKPAPER_CLI, "inspect", workpaper_path, "--store", self.store
        )
        self.assertEqual(inspected.returncode, 0, inspected.stderr.decode())
        inventory = json.loads(inspected.stdout)
        self.assertEqual(inventory["cited_ranges"][0]["representation"], "extracted")
        self.assertEqual(inventory["representations"]["generated"], 1)
        generated_citations = [
            citation for citation in inventory["cited_ranges"]
            if citation["ref"] == generated
        ]
        self.assertTrue(generated_citations[0]["generated"])
        self.assertEqual(inventory["uncited_findings"], ["f-unrelated"])
        self.assertIn("cited and declared", inventory["cited_ranges"][0]["selection"])
        synthesis_inventory = {
            item["id"]: item for item in inventory["findings"]
        }["f-synthesis"]
        self.assertEqual(
            synthesis_inventory["conditions"],
            ["Migration is temporary.", "Only selected images qualify."],
        )
        self.assertEqual(
            synthesis_inventory["depends_on"], ["f-policy", "f-migration"]
        )

        rendered = self.run_cli(
            WORKPAPER_CLI, "render", workpaper_path, "--store", self.store
        )
        self.assertEqual(rendered.returncode, 0, rendered.stderr.decode())
        report = rendered.stdout.decode("utf-8")
        self.assertIn("## Desired outcome", report)
        self.assertIn("## Live question", report)
        self.assertIn("Images are not available on the free plan.", report)
        self.assertIn("Free plans may export images during migration.\r\n", report)
        self.assertIn("**Challenges** [e2](#soundings-evidence-e2)", report)
        self.assertIn("Generated representation", report)
        self.assertIn(
            "**Uncited finding.** It remains visible but is not source-linked.",
            report,
        )
        self.assertIn("https://example.org/export-policy", report)
        self.assertIn("representation: extracted", report)
        self.assertEqual(report.count("Public export is available.\n"), 1)
        self.assertEqual(
            report.count("Free plans may export images during migration.\r\n"), 1
        )
        self.assertNotIn("**Status:**", report)
        self.assertNotIn("**Applicable conditions**", report)
        self.assertNotIn("**Declared dependencies**", report)
        headings = [
            "## Desired outcome",
            "## Live question",
            "## Authored findings",
            "## Open questions",
            "## Cited evidence appendix",
            "## Artifact limits",
        ]
        positions = [report.index(heading) for heading in headings]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("> Choose a safe image-export policy.\n\n## Live question", report)
        self.assertIn(
            "> Is image export really paid-plan-only?\n\n## Authored findings", report
        )

        packet_dir = self.root / "packet"
        brief = self.root / "brief.md"
        brief.write_text("Continue this bounded inquiry.", encoding="utf-8")
        packet.create(
            self.store,
            [policy, migration, generated],
            brief,
            packet_dir,
        )
        relocated = self.root / "relocated"
        shutil.move(str(packet_dir), relocated)
        shutil.rmtree(self.store)
        relocated_record = relocated / "workpaper.json"
        shutil.copyfile(workpaper_path, relocated_record)

        relocated_render = self.run_cli(
            WORKPAPER_CLI,
            "render",
            relocated_record,
            "--store",
            relocated / "evidence",
        )
        self.assertEqual(relocated_render.returncode, 0, relocated_render.stderr.decode())
        self.assertEqual(relocated_render.stdout.decode("utf-8"), report)

        changed = copy.deepcopy(record)
        changed["findings"][0]["status"] = "superseded"
        changed["findings"][0]["text"] = "The old free-plan restriction was superseded."
        changed_path = self.write_record("changed-workpaper.json", changed)
        impact = self.run_cli(
            WORKPAPER_CLI,
            "impact",
            changed_path,
            "--store",
            relocated / "evidence",
            "--finding",
            "f-policy",
        )
        self.assertEqual(impact.returncode, 0, impact.stderr.decode())
        impact_payload = json.loads(impact.stdout)
        by_id = {
            item["id"]: item for item in impact_payload["affected_findings"]
        }
        self.assertEqual(by_id["f-policy"]["reason"], "selected-seed")
        self.assertTrue(by_id["f-policy"]["superseded"])
        self.assertNotIn("f-migration", by_id)
        self.assertEqual(
            by_id["f-synthesis"]["witness_path"],
            ["f-policy", "f-synthesis"],
        )
        self.assertNotIn("f-unrelated", by_id)
        self.assertFalse(impact_payload["project_artifacts_changed"])

        superseded_inventory = self.run_cli(
            WORKPAPER_CLI,
            "inspect",
            changed_path,
            "--store",
            relocated / "evidence",
        )
        self.assertEqual(superseded_inventory.returncode, 0)
        warnings = json.loads(superseded_inventory.stdout)["dependency_warnings"]
        self.assertEqual(
            [item["finding"] for item in warnings],
            ["f-synthesis"],
        )
        self.assertEqual(
            warnings[0]["witness_path"], ["f-synthesis", "f-policy"]
        )

        self.assertEqual(workpaper_path.read_bytes(), workpaper_before)
        self.assertFalse(self.store.exists())
        self.assertEqual(store_before, {
            path.name: path.read_bytes()
            for path in (relocated / "evidence").iterdir()
            if path.is_file()
        })

    def test_source_ref_impact_uses_support_challenge_and_context(self):
        source_ref = self.capture_api("one\ntwo\nthree\nfour\n")
        record = self.base_record([
            self.finding(
                "support",
                citations=[self.citation(source_ref, 1, 1, "supports")],
            ),
            self.finding(
                "challenge",
                citations=[self.citation(source_ref, 2, 2, "challenges")],
            ),
            self.finding(
                "context",
                citations=[self.citation(source_ref, 3, 3, "context")],
                depends_on=["challenge"],
            ),
            self.finding(
                "descendant",
                kind="judgment",
                depends_on=["support"],
            ),
            self.finding("unrelated", kind="proposal"),
        ])
        record_path = self.write_record("record.json", record)
        result = self.run_cli(
            WORKPAPER_CLI,
            "impact",
            record_path,
            "--store",
            self.store,
            "--ref",
            source_ref,
        )
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        affected = {
            item["id"]: item for item in json.loads(result.stdout)["affected_findings"]
        }
        self.assertEqual(set(affected), {"support", "challenge", "context", "descendant"})
        self.assertEqual(affected["support"]["relations"], ["supports"])
        self.assertEqual(affected["challenge"]["relations"], ["challenges"])
        self.assertEqual(affected["context"]["relations"], ["context"])
        self.assertEqual(affected["context"]["reason"], "cites-snapshot-ref")
        self.assertNotIn("unrelated", affected)
        self.assertEqual(affected["context"]["witness_path"], ["context"])
        self.assertEqual(
            affected["descendant"]["witness_path"], ["support", "descendant"]
        )

    def test_shared_range_is_one_appendix_entry_with_both_authored_relations(self):
        ref = self.capture_api(
            "First line.\nShared deciding line.\nThird line.\n",
            title="Shared source",
            representation="verbatim",
        )
        record = self.base_record([
            self.finding(
                "f-support",
                text="A short claim.",
                citations=[
                    self.citation(ref, 2, 2, "supports", "Used as direct support.")
                ],
            ),
            self.finding(
                "f-challenge",
                kind="judgment",
                text="A competing claim.",
                conditions=["Only while the shared condition applies."],
                citations=[
                    self.citation(ref, 2, 2, "challenges", "The same line also limits it.")
                ],
                depends_on=["f-support"],
            ),
        ])
        record_path = self.write_record("shared-range.json", record)

        result = self.run_cli(
            WORKPAPER_CLI, "render", record_path, "--store", self.store
        )
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        report = result.stdout.decode("utf-8")

        self.assertEqual(report.count("\n### Soundings evidence e1\n"), 1)
        self.assertNotIn("\n### Soundings evidence e2\n", report)
        self.assertEqual(report.count("Shared deciding line."), 1)
        self.assertIn(
            "**Supports** [e1](#soundings-evidence-e1) - Used as direct support.",
            report,
        )
        self.assertIn(
            "**Challenges** [e1](#soundings-evidence-e1) - The same line also limits it.", report
        )
        self.assertIn("### `f-support` - observation - CURRENT", report)
        self.assertIn("### `f-challenge` - judgment - CURRENT", report)
        self.assertIn(
                "- Only while the shared condition applies.", report
        )
        self.assertIn("**Depends on:** `f-support`", report)
        self.assertIn(f"**Selected ref/range:** `{ref}` lines 2-2", report)
        self.assertLess(report.index("### `f-support`"), report.index("## Cited evidence appendix"))
        self.assertLess(
            report.index("## Cited evidence appendix"),
            report.index("### Soundings evidence e1"),
        )

    def test_invalid_citations_fail_visibly_without_clipping(self):
        ref = self.capture_api("one\ntwo\nthree\n")
        base = self.finding(
            "f1",
            citations=[self.citation(ref, 1, 2)],
        )
        mutations = {
            "zero-start": {"start_line": 0},
            "end-beyond-source": {"end_line": 4},
            "inverted": {"start_line": 3, "end_line": 2},
            "boolean-start": {"start_line": True},
            "string-end": {"end_line": "2"},
        }
        for name, change in mutations.items():
            with self.subTest(name=name):
                finding = copy.deepcopy(base)
                finding["evidence"][0].update(change)
                path = self.write_record(f"{name}.json", self.base_record([finding]))
                result = self.run_cli(
                    WORKPAPER_CLI, "inspect", path, "--store", self.store
                )
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, b"")
                self.assertIn(b"workpaper:", result.stderr)
                self.assertIn(b"line", result.stderr)

        missing = self.finding(
            "missing",
            citations=[self.citation("s-" + "0" * 32, 1, 1)],
        )
        path = self.write_record("missing.json", self.base_record([missing]))
        result = self.run_cli(WORKPAPER_CLI, "inspect", path, "--store", self.store)
        self.assertEqual(result.returncode, 2)
        self.assertIn(b"snapshot not found", result.stderr)

    def test_malformed_schema_types_ids_dependencies_and_cycles_fail(self):
        path = self.root / "malformed.json"
        path.write_text('{"schema": "soundings.workpaper.v1",', encoding="utf-8")
        result = self.run_cli(WORKPAPER_CLI, "inspect", path, "--store", self.store)
        self.assertEqual(result.returncode, 2)
        self.assertIn(b"not valid JSON", result.stderr)
        self.assertIn(b"line 1", result.stderr)

        cases = {
            "wrong-schema": self.base_record(
                [self.finding("f1")], schema="soundings.workpaper.v2"
            ),
            "extra-field": self.base_record(
                [self.finding("f1")], extra="not allowed"
            ),
            "duplicate-id": self.base_record([
                self.finding("same"),
                self.finding("same"),
            ]),
            "unknown-dependency": self.base_record([
                self.finding("f1", depends_on=["absent"]),
            ]),
            "cycle": self.base_record([
                self.finding("f1", depends_on=["f2"]),
                self.finding("f2", depends_on=["f1"]),
            ]),
            "bad-kind": self.base_record([
                self.finding("f1", kind="fact"),
            ]),
            "bad-status": self.base_record([
                self.finding("f1", status="verified"),
            ]),
        }
        for name, record in cases.items():
            with self.subTest(name=name):
                record_path = self.write_record(f"{name}.json", record)
                result = self.run_cli(
                    WORKPAPER_CLI, "inspect", record_path, "--store", self.store
                )
                self.assertEqual(result.returncode, 2, result.stderr.decode())
                self.assertEqual(result.stdout, b"")

    def test_render_preserves_exact_markdown_and_escapes_authored_prose(self):
        source = (
            "# Source syntax\n"
            "```html\n"
            "<script>source-owned()</script>\n"
            "```\n"
            "No.\r\n"
            "A & B remains literal.\n"
        )
        ref = self.capture_api(source, title="Source *title*", representation="verbatim")
        finding = self.finding(
            "f1",
            text=(
                "[a misleading label](https://example.org) and **bold** and "
                "`code`\n- not a list\n+ not a list\n# not a heading\n> not a quote"
                "\nhttps://example.org\nperson@example.org\nwww.example.org"
            ),
            conditions=[
                "<b>Authored HTML must not become markup.</b>",
                "[condition link](https://example.org/condition) *emphasis* ``ticks``",
                "Keep the short qualifier.",
                "Wait for the later note...",
                "This qualifier ends with a semicolon;",
            ],
            citations=[
                self.citation(
                    ref,
                    1,
                    6,
                    "context",
                    "note [link](https://example.org/note) **strong** `tick`",
                )
            ],
        )
        record_path = self.write_record(
            "markdown.json",
            self.base_record(
                [finding],
                outcome="Literal [outcome](https://example.org) and **outcome bold**.",
                question="- literal question\n> not a quote",
                open_questions=["# question heading", "1. not an ordered item"],
            ),
        )
        result = self.run_cli(
            WORKPAPER_CLI, "render", record_path, "--store", self.store
        )
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        report = result.stdout.decode("utf-8")
        self.assertIn(
            "&lt;b&gt;Authored HTML must not become markup.&lt;/b&gt;", report
        )
        self.assertIn(
            r"\[a misleading label\]\(https\://example.org\) and "
            r"\*\*bold\*\* and \`code\`",
            report,
        )
        self.assertIn(r"- not a list", report)
        self.assertIn(r"\+ not a list", report)
        self.assertIn(r"\# not a heading", report)
        self.assertIn("&gt; not a quote", report)
        self.assertIn(
            r"\[condition link\]\(https\://example.org/condition\) "
            r"\*emphasis\* \`\`ticks\`\`",
            report,
        )
        self.assertIn(
            r"note \[link\]\(https\://example.org/note\) "
            r"\*\*strong\*\* \`tick\`",
            report,
        )
        self.assertIn(
            r"Literal \[outcome\]\(https\://example.org\) and "
            r"\*\*outcome bold\*\*.",
            report,
        )
        self.assertIn(r"- literal question", report)
        self.assertIn(r"\# question heading", report)
        self.assertIn(r"1\. not an ordered item", report)
        self.assertIn(r"person\@example.org", report)
        self.assertIn(r"www\.example.org", report)
        self.assertIn("- Wait for the later note...", report)
        self.assertIn("- This qualifier ends with a semicolon;", report)
        self.assertNotIn("[a misleading label](", report)
        self.assertNotIn("**bold**", report)
        self.assertIn("````text\n" + source, report)
        self.assertIn("No.\r\n", report)
        self.assertIn("A & B remains literal.", report)

    def test_output_is_refused_or_left_absent_until_validation_succeeds(self):
        ref = self.capture_api("safe\n")
        record_path = self.write_record(
            "valid.json",
            self.base_record([
                self.finding("f1", citations=[self.citation(ref, 1, 1)])
            ]),
        )
        existing = self.root / "existing.md"
        existing.write_bytes(b"owner content\n")
        result = self.run_cli(
            WORKPAPER_CLI,
            "render",
            record_path,
            "--store",
            self.store,
            "--output",
            existing,
        )
        self.assertEqual(result.returncode, 2)
        self.assertEqual(existing.read_bytes(), b"owner content\n")
        self.assertEqual(result.stdout, b"")

        invalid = self.base_record([
            self.finding("f1", citations=[self.citation(ref, 1, 2)])
        ])
        invalid_path = self.write_record("invalid.json", invalid)
        absent = self.root / "absent-output.md"
        result = self.run_cli(
            WORKPAPER_CLI,
            "render",
            invalid_path,
            "--store",
            self.store,
            "--output",
            absent,
        )
        self.assertEqual(result.returncode, 2)
        self.assertFalse(absent.exists())

        missing_parent = self.root / "missing" / "report.md"
        result = self.run_cli(
            WORKPAPER_CLI,
            "render",
            record_path,
            "--store",
            self.store,
            "--output",
            missing_parent,
        )
        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.root / "missing").exists())

        output = self.root / "report.md"
        result = self.run_cli(
            WORKPAPER_CLI,
            "render",
            record_path,
            "--store",
            self.store,
            "--output",
            output,
        )
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        self.assertEqual(result.stdout, b"")
        self.assertIn("# Research workpaper", output.read_text(encoding="utf-8"))

    def test_source_ref_seed_fails_when_ref_is_unknown_or_uncited(self):
        cited = self.capture_api("cited\n")
        uncited = self.capture_api("valid but not cited\n")
        record = self.base_record([
            self.finding("f1", citations=[self.citation(cited, 1, 1)])
        ])
        record_path = self.write_record("record.json", record)

        result = self.run_cli(
            WORKPAPER_CLI,
            "impact",
            record_path,
            "--store",
            self.store,
            "--ref",
            uncited,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(b"exists but no finding cites", result.stderr)

        result = self.run_cli(
            WORKPAPER_CLI,
            "impact",
            record_path,
            "--store",
            self.store,
            "--ref",
            "s-" + "f" * 32,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(b"snapshot not found", result.stderr)

        result = self.run_cli(
            WORKPAPER_CLI,
            "impact",
            record_path,
            "--store",
            self.store,
            "--finding",
            "absent",
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(b"unknown finding seed", result.stderr)

    def test_old_citation_band_does_not_change_when_new_capture_is_added(self):
        old = self.capture_api("version one\nold condition\n")
        record = self.base_record([
            self.finding(
                "f1",
                citations=[self.citation(old, 2, 2, "context")],
            )
        ])
        record_path = self.write_record("record.json", record)
        new = self.capture_api("version two\nnew condition\n")
        self.assertNotEqual(old, new)

        rendered = self.run_cli(
            WORKPAPER_CLI, "render", record_path, "--store", self.store
        )
        self.assertEqual(rendered.returncode, 0, rendered.stderr.decode())
        report = rendered.stdout.decode("utf-8")
        self.assertIn("old condition", report)
        self.assertNotIn("new condition", report)
        self.assertIn(old, report)

        impact = self.run_cli(
            WORKPAPER_CLI,
            "impact",
            record_path,
            "--store",
            self.store,
            "--ref",
            old,
        )
        self.assertEqual(impact.returncode, 0, impact.stderr.decode())
        self.assertEqual(
            [item["id"] for item in json.loads(impact.stdout)["affected_findings"]],
            ["f1"],
        )

    def test_empty_snapshot_has_no_citable_positive_line(self):
        ref = self.capture_api("")
        record_path = self.write_record(
            "empty.json",
            self.base_record([
                self.finding("f1", citations=[self.citation(ref, 1, 1)])
            ]),
        )
        result = self.run_cli(
            WORKPAPER_CLI, "inspect", record_path, "--store", self.store
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(b"has 0 lines", result.stderr)
        self.assertEqual(result.stdout, b"")

    def test_missing_store_fails_without_creating_directories(self):
        ref = self.capture_api("saved\n")
        record_path = self.write_record(
            "record.json",
            self.base_record([
                self.finding("f1", citations=[self.citation(ref, 1, 1)])
            ]),
        )
        shutil.rmtree(self.store)
        output = self.root / "report.md"
        result = self.run_cli(
            WORKPAPER_CLI,
            "render",
            record_path,
            "--store",
            self.store,
            "--output",
            output,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(b"snapshot not found", result.stderr)
        self.assertFalse(self.store.exists())
        self.assertFalse(output.exists())

    def test_cli_emits_utf8_bytes_independent_of_stdout_encoding(self):
        source = "来源。\r\n仅在提交后保留。\r\n"
        ref = self.capture_api(source, title="条件原文")
        record = self.base_record([
            self.finding("f1", text="保留原文条件。", citations=[self.citation(ref, 1, 2)])
        ], outcome="解释跨进程保存。", question="在哪个条件下成立？")
        path = self.write_record("研究稿.json", record)
        for command in ("inspect", "render", "impact"):
            with self.subTest(command=command):
                extra = ["--finding", "f1"] if command == "impact" else []
                result = subprocess.run(
                    [sys.executable, str(WORKPAPER_CLI), command, str(path),
                     "--store", str(self.store), *extra],
                    capture_output=True,
                    env={**ENV, "PYTHONIOENCODING": "ascii:strict"},
                )
                self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8"))
                if command == "render":
                    self.assertIn(source.encode("utf-8"), result.stdout)
                    self.assertIn("保留原文条件。".encode("utf-8"), result.stdout)
                else:
                    payload = json.loads(result.stdout.decode("utf-8"))
                    self.assertEqual(payload["record"], str(path))

    def test_deep_reverse_chain_validates_and_impacts_without_recursion(self):
        depth = 1100
        findings = [
            self.finding(f"f{index}", depends_on=[f"f{index - 1}"] if index else [])
            for index in reversed(range(depth))
        ]
        record_path = self.write_record(
            "deep-valid.json", self.base_record(findings)
        )

        inspected = self.run_cli(
            WORKPAPER_CLI, "inspect", record_path, "--store", self.store
        )
        self.assertEqual(inspected.returncode, 0, inspected.stderr.decode())
        self.assertEqual(len(json.loads(inspected.stdout)["findings"]), depth)

        rendered = self.run_cli(
            WORKPAPER_CLI, "render", record_path, "--store", self.store
        )
        self.assertEqual(rendered.returncode, 0, rendered.stderr.decode())
        self.assertIn(
            "### `f1099` - observation - CURRENT",
            rendered.stdout.decode("utf-8"),
        )

        impacted = self.run_cli(
            WORKPAPER_CLI,
            "impact",
            record_path,
            "--store",
            self.store,
            "--finding",
            "f0",
        )
        self.assertEqual(impacted.returncode, 0, impacted.stderr.decode())
        affected = json.loads(impacted.stdout)["affected_findings"]
        self.assertEqual(len(affected), depth)
        self.assertEqual(affected[-1]["id"], f"f{depth - 1}")
        self.assertEqual(len(affected[-1]["witness_path"]), depth)

    def test_long_cycle_fails_with_bounded_diagnostic(self):
        depth = 1100
        findings = [
            self.finding(f"f{index}", depends_on=[f"f{index - 1}"] if index else ["f1099"])
            for index in reversed(range(depth))
        ]
        record_path = self.write_record(
            "deep-cycle.json", self.base_record(findings)
        )
        result = self.run_cli(
            WORKPAPER_CLI, "inspect", record_path, "--store", self.store
        )
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, b"")
        stderr = result.stderr.decode("utf-8")
        self.assertIn("dependency cycle is not allowed (1100 findings)", stderr)
        self.assertIn(" -> ... -> ", stderr)
        self.assertNotIn("RecursionError", stderr)
        self.assertNotIn("Traceback", stderr)


if __name__ == "__main__":
    unittest.main()
