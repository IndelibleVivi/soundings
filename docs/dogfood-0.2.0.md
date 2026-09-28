# Soundings 0.2.0 evidence

Observed on 2026-09-28. This is a bounded development and dogfood record, not a benchmark or a claim of general improvement. Raw prompts, traces, and private continuity remain outside Git. Public examples use constructed material.

## Source and deterministic checks

- Four independently discoverable Skills: Search, Study, Explore, Shape. Each passed `skill-validate` after its final runtime edits.
- The `0.2.0` plugin passed the installed `plugin-creator` validator.
- The optional standard-library Python helper passed 12 tests covering exact Unicode/CRLF capture, stable old references after new capture, short neighboring qualifiers, merged find windows, visible whole-range omission, later windows fitting after an oversized window, full JSON stdout byte accounting, insufficient-budget failure without a capture, empty/no-match reads, representation metadata, invalid ranges/missing references, and actual CLI output/error behavior.
- No new provider, MCP server, network service, remote store, database, or production dependency was added.

These checks establish package structure and helper behavior. They do not establish automatic discovery, semantic completeness, source freshness, or inquiry quality.

## Fresh source-candidate observations

Environment: Codex CLI `0.147.0`, ephemeral sessions, `gpt-5.6-sol` with high reasoning, source-candidate Skills exposed through project-local discovery. Web was disabled except for the Search case. The first model-availability probe using `gpt-6-sol` failed before a task ran because that CLI account did not support it; it contributes no behavior evidence.

| Case | Observed result | Scope and limit |
| --- | --- | --- |
| Explicit Search: 80 MB GitHub Contents retrieval | Read Search and its evidence references, searched current official documentation, retained the raw/object media-type distinction, and gave a usable implementation recommendation. | Documentation-based verification, not an 80 MB transfer test. Primary-source content was independently read back. |
| Explicit Study: five conflicting synthetic materials | Read all supplied material and Study references. Explained version/object differences; distinguished a repeated timing claim from a separate portability observation; retained an unavailable appendix and same-OS condition; developed design implications. | One supplied-material synthesis. No real product, cross-model study, or causal comparison. |
| Explicit Explore: a six-minute shared paper activity | Read Explore and its references, then wrote the complete activity, facilitator wording, consequential choices, and a full worked playthrough. | Complete inspectable creative candidate; timing, enjoyment, and human group use remain untested. |
| Explicit Shape: correct a rating-questionnaire interpretation | Read Shape, revised both specification and runnable local prototype, kept six rounds and rich reflection, and removed numeric trait scoring. Ran a complete demo and four local checks. | Bounded propagation through spec and code; not all possible story branches or human reception. |
| Archived evidence reused for a different question | Read Search's evidence-reading reference and invoked the packaged helper on the saved snapshot after the original file had changed. Reconsidered an old rejection under the new project's conditions and identified the source as synthetic. | Explicit local retention and reuse, not automatic memory, current-product verification, or a remote corpus. |

[Worked examples](examples/inquiry-in-practice.md) show the Study reasoning and correction scope; [Six Minutes to Elsewhere](examples/six-minutes-to-elsewhere.md) contains the complete creative artifact.

The source-candidate cases used explicit Skill invocation. Installed implicit discovery and clear-small-task behavior are pending the public upgrade; earlier `0.1.0` observations remain historical evidence in [their own record](dogfood-0.1.0.md).

## Installation, activation, and publication

At this source-validation point, the existing installed Git-marketplace copy is still `0.1.0`. Publication of `0.2.0`, version-to-version upgrade, installed-cache comparison, and fresh installed discovery are pending. Successful source cases are not presented as installed activation.

## What remains unproven

- The entire behavior-scenario suite, cross-model consistency, and comparative or causal benefit.
- Whether the methods improve retrieval recall, end-to-end cost, or user judgment effort in broader work.
- Automatic grouping of claims with distant qualifications. The helper preserves requested ranges and reports omissions; the reader still decides where to expand.
- Real-player pacing, enjoyment, and owner acceptance of generated creative work.
- Long-running correction propagation across large production repositories.

The host emitted a Skill-description budget warning in some runs; successful discovery here does not guarantee behavior with other saturated inventories. Unrelated connector-startup warnings did not prevent the observed local tasks. A separate browser-based independent review could not confirm a committed turn and could not recover its prior turns, so it produced no usable review and is not counted as validation.
