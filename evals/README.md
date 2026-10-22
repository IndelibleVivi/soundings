# Offline research slice

This source-only pack makes research conditions and failure modes inspectable.
It does not establish that Soundings improves inquiry, and it never starts a
target model. The four independent runtime Skills remain unchanged.

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
tasks with two repetitions: **32 planned task runs**, not 32 API requests or
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

The [example trace](examples/constructed-trace.jsonl) is entirely constructed.
It is not a private transcript or evidence from a model run. An annotation has
`schema: soundings.observations.v1`, the exact `trace_sha256`, and an `events`
array. Each event specifies `kind`, a one-based `trace_line`, a JSON `pointer`
to visible text, an exact nonempty `excerpt`, and a rationale in `note`.
`content.delivered` also labels its `representation` as `verbatim`, `extracted`,
`generated` or `unknown`.

Kinds cover `capability.catalog`, `acquisition.succeeded`, `acquisition.failed`,
`content.delivered`, `commitment`, `artifact.changed` and `feedback`. Delivery,
catalog and successful acquisition require completed successful tool outputs;
command arguments and agent messages cannot prove them. File-change annotations
require a completed file-change event. Annotations select the decisive visible
evidence and explain its meaning; they are not automatic semantic judgments.
Unsupported trace shapes need explicit inspection rather than a guessed parser.

Trace hashes reject drift, and excerpts must exist at their anchors. Output
bytes count the anchored returned text, not model tokens or original-document
line ranges. A delivered excerpt does not prove source authenticity, complete
reading, tool availability throughout a run, method selection or correct use.
The first **annotated** commitment is not a claim that all earlier commitments
were found. Missing observations stay unknown. Failed acquisition, feedback
meaning, source versions/lineage and causal application need reviewer judgment.

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

For descriptive comparison, explicitly select the receipts and native reviews:

```bash
python3 evals/observe.py compare \
  --receipt /path/to/attempt-a/receipt.json \
  --receipt /path/to/attempt-b/receipt.json \
  --review /path/to/native-review.json
```

Missing semantic reviews stay `pending`. Stale or unbound reviews, wrong
requirement keys, duplicate receipts/attempts, and conflicting unadjudicated
reviews are rejected. Execution outcome, delivery, semantic review and reported
usage remain separate. Repetitions are grouped within lab/task/subject; the tool
does not treat them as independent projects, compute a universal score, or hide
timeouts and errors. Reconcile the selected receipts with the pinned full plan
to account for missing runs before drawing conclusions.

## Research still open

This slice prepares controlled tests of discovery delivery/selection,
counterfactual evidence use, qualifier survival, mechanism transfer and bounded
correction. It does not run the proposed experiments. Open-ended question
discovery, actual visual/interactive reference inspection, repeated handoffs,
real author judgments and cross-host/language transfer remain separate studies.
Field Lab randomization/factorial extensions and ACP/API adapters remain outside
this source change. Existing fixed canary plans suffice to inspect this first
instrumentation boundary; they do not reproduce the historical ACP host.

Runtime schemas and Skill structure are unchanged. New `evals/` material follows
the existing [licensing map](../LICENSING.md): unlisted files remain all rights
reserved. Materialization uses local source trees without relicensing them or
adding those generated copies to this repository.
