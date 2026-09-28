# Soundings 0.2.0 evidence

Observed on 2026-09-28–29 (Asia/Singapore). This is a bounded development and dogfood record, not a benchmark or a claim of general improvement. Raw prompts, traces, and private continuity remain outside Git. Public examples use constructed material.

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

The source-candidate cases used explicit Skill invocation. Earlier `0.1.0` observations remain historical evidence in [their own record](dogfood-0.1.0.md).

## Fresh installed observations

A metadata-only check under the ordinary host configuration exposed all four Skills from the installed `soundings/0.2.0/skills/` package. These fresh tasks had no project-local Skill copies or invocation tokens. They used the same CLI/model, with the host configuration loaded and the built-in OpenAI provider selected for the ChatGPT-authenticated run.

- **Implicit Study:** naturally selected the installed Study contract and its alignment/explanation references, then delivered the supplied-material synthesis with version, object, independent-evidence, concurrency, and portability conditions intact.
- **Implicit Explore:** naturally read the installed Explore contract and candidate reference, then wrote a complete two-person impossible-museum activity with four consequential building moves, facilitator script, exhibit material, and a full playthrough. It repaired a reachability-rule inconsistency before completion and explicitly left human timing/playtesting unverified.
- **Clear small task:** changed only the requested spelling and retained the original newline. No Soundings Skill was loaded; the host's general engineering method remained independent.

Earlier test-launch attempts using `--ignore-user-config` did not expose Soundings in the task metadata, even with selected registration/enablement overrides. Their outputs are retained privately but are not counted as plugin behavior. Loading the ordinary host configuration resolved the metadata gap; no package edit or cache patch was required. No causal quality comparison is inferred from these attempts.

## Installation, activation, and publication

The implementation was published to public `main` in commit `c0bac6a`. The documented sequence was exercised against the existing `0.1.0` Git installation:

```bash
codex plugin marketplace upgrade soundings
codex plugin add soundings@soundings
codex plugin list --json
```

Marketplace refresh reported no errors; plugin installation returned `0.2.0`, and listing showed it installed and enabled with a Git marketplace source. All 24 installed package files matched the canonical source byte-for-byte. No parallel local marketplace registration was added.

Anonymous readback confirmed the public repository, default branch `main`, the remote implementation commit, rendered README HTML, and marketplace discovery manifest. Fresh installed method use is recorded above. These observations do not hot-reload a task that was already running, and owner acceptance remains separate.

## What remains unproven

- The entire behavior-scenario suite, cross-model consistency, and comparative or causal benefit.
- Whether the methods improve retrieval recall, end-to-end cost, or user judgment effort in broader work.
- Automatic grouping of claims with distant qualifications. The helper preserves requested ranges and reports omissions; the reader still decides where to expand.
- Real-player pacing, enjoyment, and owner acceptance of generated creative work.
- Long-running correction propagation across large production repositories.

The host emitted a Skill-description budget warning in some runs; successful discovery here does not guarantee behavior with other saturated inventories. Unrelated connector-startup warnings did not prevent the observed local tasks. A separate browser-based independent review could not confirm a committed turn and could not recover its prior turns, so it produced no usable review and is not counted as validation.
