# Offline research slice

This source-only pack makes research conditions and failure modes inspectable.
It does not establish that Soundings improves inquiry, and it never starts a
target model. The four independent runtime Skills remain unchanged.

A separately authorized [live tools canary](../docs/tools-canary-2026-10-23.md)
has exercised Field Lab execution, annotations and plan-bound comparison. Its
host errors, interrupted delivery and original fixture failures remain explicit;
it is not evidence of causal benefit or completed proactive discovery. New
natural packs permit product-documentation edits and use task-family review
criteria; historical pack contracts and receipts remain unchanged.

## Build a fixed plan

Python 3.10+ and the standard library run the local checks:

```bash
python3 evals/check.py
```

To materialize the research pack, supply existing local Soundings, Servotab and
[Skill Field Lab](https://github.com/IndelibleVivi/skill-field-lab) checkouts.
Field Lab remains the runner, plan, input-pinning and receipt owner. There is no
Field Lab installation or live-run dependency for `evals/check.py`.

```bash
python3 evals/pack.py build \
  --soundings /path/to/soundings \
  --servotab /path/to/servotab \
  --fieldlab /path/to/skill-field-lab \
  --output /path/outside-git/new-research-pack \
  --model gpt-6.1-sol --effort high --control
```

The output must be a new directory outside Git. Model and effort are explicit
future-plan metadata, not invocation authority or a claim about returned model
identity. [Pack details](pack-README.md) describe the fixed component commits,
composition provenance, local corpus, oracles and output files. Do not publish
generated snapshots, plans with local paths, raw traces or completed reviews.

Four normal subjects compose historical/current Soundings and
historical/current Servotab. Four separate canary plans each enumerate four
guided mechanism probes with two repetitions: **32 planned task runs**, not 32 API requests or
32 independent projects. A separate true no-Skill control plan has eight runs;
it is not part of that 32. Historical subjects are not isolated controls.
The fixed order is descriptive instrumentation, not randomized experimental
assignment or a causal comparison. No `matched` contract is bypassed.

| Task family | Decision under inspection | Useful counterexample |
| --- | --- | --- |
| Engineering choice | Use applicable evidence before an important choice; carry a correction into dependent behavior. | Cite a source while retaining an invalid route or treating repeated reports as independent observations. |
| Creative transfer | Adapt a useful mechanism while retaining the local purpose and allowing different forms. | Copy an attractive but inapplicable reference detail. |
| Settled work | Complete substantial work under accepted rules and supplied information. | Replace accepted constraints or add unjustified research. |
| Direct repair | Finish a precise small correction. | Expand scope or damage still-valid behavior. |

These four cases contain task/query cues and explicit scope instructions. They test
guided mechanism use, not autonomous inquiry or natural research selectivity.
The separate [natural-task suite](natural/README.md) supplies ordinary prompts,
real runtime behavior and an actual reading/writing application.

Cases are constructed mechanism probes, not collected user tasks or a validated
benchmark. Field Lab selftest rejects each unresolved fixture and accepts a
constructed valid result; the separate counterexample checks challenge the
oracles. Deterministic answers do not establish autonomous inquiry, source
authenticity, creative value, or generalization. Human review remains necessary.
Reviewers can inspect expected/negative material; target workers receive only
the fixture. Hiding files from the initial workspace is not a sandbox against
an agent deliberately searching the host filesystem.

## Observe visible events

The observation helper consumes a Codex JSONL trace plus explicit annotations:

```bash
python3 evals/observe.py timeline \
  --trace evals/examples/constructed-trace.jsonl \
  --annotations evals/examples/annotations.json
```

The [example trace](examples/constructed-trace.jsonl) is entirely constructed,
not a private transcript or evidence from a model run. Its paired
[annotations](examples/annotations.json) use `soundings.observations.v2`.
Version1 annotations must migrate: replace `trace_line` with `stream` and `line`,
declare concrete `decisions`, classify deliveries and declare review coverage.
The old session-wide `delivery_before_commitment` boolean has been removed.

Each event has `kind`, `stream` (`trace` or `host_context`), a one-based `line`,
a JSON `pointer`, an exact nonempty `excerpt` and an explanatory `note`.
Deliveries also carry `source_id`, `representation`, `role`, `origin` and
`completeness`. Roles distinguish Skill guidance, task input, search summaries,
source bodies, interpretations and unknown content. Origin distinguishes fixed
corpus, live external, supplied and unknown material. These are explicit
annotations, not automatic source authentication. The anchored content hash
identifies the returned text; it does not authenticate the original source.

Declare a `decision_id` and concrete question for each decision. Commitment
annotations link to that identity; source `relations` identify supporting,
refuting, irrelevant or unknown applicability, with a rationale. A generic file
write is not automatically a design commitment. File-change annotations still
require a completed file-change trace event. Command arguments, failed tool
responses, MCP metadata and agent self-reports cannot prove content delivery.

`relevant_source_body_before_commitment` and
`external_source_body_before_commitment` are **yes/no/unknown**, per decision.
They concern annotated source bodies, not every possible form of information;
search summaries and Skill guidance remain separately visible. Supplied evidence
can support the first measure without being a new external acquisition. A source
is counted only when its declared relation is relevant and its visible position
precedes the selected commitment. Same-call internal order and unpositioned
content remain unknown. Absence becomes `no` only with explicit complete delivery
annotation/host coverage and continuous trace coverage through that commitment.
Coverage is an annotator's declared scope, not a sensor guarantee. A complete
trace alone does not prove initial host context was captured.

For an explicitly recorded initial catalog or injected source, supply a JSONL
host-context sidecar using `--host-context /private/output/context.jsonl` and bind
its exact bytes with `host_context_sha256`. Each record has `text` and, only when
actually recorded, `before_trace_line`. Host annotations select `/text` and are
labeled `recorded-host-context`; this does not install a hook or prove a host
injected that text. Missing timing information stays unknown. Trace hashes reject
drift, excerpts must match their anchors, and source/body byte counts cover
returned text rather than model tokens or original-document line ranges.

## Review a concrete receipt

After a separately authorized run, prepare a condition-light worksheet from an
actual Field Lab v2 receipt:

```bash
python3 evals/observe.py review-template --receipt /path/to/receipt.json
```

The worksheet omits subject/version metadata, binds the receipt bytes, and
starts every declared semantic requirement as `inconclusive`. It is not a
completed review. Inspect the sealed task artifacts, source conditions and
visible trace, independently of the implementer's completion claim. Full
artifact blinding is not guaranteed: artifacts can reveal their condition.
Random assignment and independent reviewers must be arranged before a live
study, not inferred from this worksheet.

Use Field Lab's existing `review` command with the actual receipt, rationale,
independence and exact requirement-outcome keys. Save only the worksheet's
`requirement_outcomes` object as the CLI outcomes file:

```bash
fieldlab review /path/to/new-research-pack/fieldlab.json \
  --review-id independent-review-01 --receipt /path/to/receipt.json \
  --independence separate-agent --judgment inconclusive \
  --rationale "Describe what the sealed artifacts support and what remains unresolved." \
  --requirement-outcomes /path/to/outcomes.json
```

For descriptive comparison use the canonical [plan-bound tool](compare-README.md).
The former `observe.py compare` entry has been retired. Explicit plans, run
summaries and an existing Field Lab checkout are now required:

```bash
python3 evals/compare.py --fieldlab-root /path/to/skill-field-lab \
  --plan /path/to/run.plan.json --summary /path/to/run/summary.json \
  --receipt /path/to/attempt-a/receipt.json --review /path/to/native-review.json
```

Native plan integrity, summary identity and receipt-sealed metadata identify each
planned repeat and logical attempt. Timestamp edits cannot create a new sample;
retries stay within their planned repeat and require adjudication. Missing planned
rows and integrity errors remain visible. Reviews retain identity, independence,
rationale and individual outcomes; implementer support is not independent support.
Missing semantic review remains pending. The tool checks the fields it consumes
and native artifact integrity; it explicitly does **not** claim full receipt JSON
Schema validation or signed provenance authentication. Execution outcome, delivery,
application, review and costs remain separate observations.

## Research still open

The natural suite prepares separate A/F/E/N interventions: ordinary selection,
an additional bounded-inquiry requirement, supplied factual evidence, and no
additional reference corpus. Production and verification tools remain available
in N, and direct source reads remain legitimate inquiry. F changes attention and
work allocation as well as retrieval; E changes information and salience;
F minus E does not isolate pure search cost. Comparing self-selected researchers
with nonresearchers inside A does not establish causal benefit.

| Open explanation | Distinguishing future intervention | Boundary |
| --- | --- | --- |
| Task construed as settled; question formation fails | Keep task/output fixed; separately expose openness, a discriminating question or a query. | Do not leak questions into natural conditions. |
| Method or tool not effectively visible | Deliver the same method at decision time, or clarify only the tool entry. | Confirm actual disclosure and successful access before attributing a selection failure. |
| Acquisition cost or implementation priority dominates | Vary stated/actual acquisition cost and useful information separately. | More calls do not establish better selectivity. |
| Early commitment changes evidence use | Same relevant or irrelevant evidence before/after a proposal. | Control remaining budget, context position and actual migration work; timing differences alone do not establish psychological fixation. |
| Applicability comparison or continuation fails | Paired runtime facts, then the same correct applicability conclusion with different continuation support. | Test implemented behavior and dependent artifacts, not rationale or solution names. |
| Added inquiry has little value for the task | Compare ordinary, bounded-inquiry, supplied-evidence and no-new-material conditions. | A direct plan can be correct; quality and cost must both be measured. |

These remain hypotheses, not diagnoses of the historical failure. Natural and
paired-world fixtures now support offline protocol checks, including a previously
settled task encountering a new obstacle. Actual policy effects, open-ended
question discovery, human experience judgments, timing rescue conditions,
repeated handoffs and cross-host/language transfer still require separate studies.
Field Lab randomization/factorial extensions and ACP/API adapters remain outside
this change; the new Codex pack does not reproduce the historical ACP host.

Before authorized live execution, fix the complete plan, retry policy, actual
runtime/model/tool preflight, primary task outcome and the minimum useful
improvement. Report research, production and verification costs separately,
including failed queries, interruption, rework and remaining user repair.
Equal total budget and extra research budget answer different questions. Analyze
paired differences within tasks, retain every planned/missing/error row, and
use repeats to describe task-level variability rather than inflate project count.
Blind condition labels and process reports where possible, record annotation
disagreements, and reserve holdout tasks for later validation. No live study or
minimum effect threshold is silently selected by building these tools.

Runtime Skill schemas and structure are unchanged; the optional observation
annotation schema has moved to v2 as described above. New `evals/` material follows
the existing [licensing map](../LICENSING.md): unlisted files remain all rights
reserved. Materialization uses local source trees without relicensing them or
adding those generated copies to this repository.
