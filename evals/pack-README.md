# Offline research pack

`pack.py build` (alias `materialize`) requires explicit `--output`, `--soundings`,
`--servotab`, `--fieldlab`, `--model`, and `--effort`. Output must be new and
outside Git. No target model is started. Model and effort describe a future
plan; they grant no invocation authority. The four combinations are normal
canary subjects, never isolated controls. The aggregate contains 32 rows.

Runtime trees come from fixed Git commits through `git ls-tree` and `git show`.
Full commits are recorded in `composition.json`; source repositories remain
untouched. Old/current defaults are explicit in `pack.py`. Field Lab plans pin
its source and the actual runtime layouts. Generated snapshots stay outside Git.

Cases are constructed, offline examples, not collected user tasks. Agent-facing
`lookup.py` returns a fixed ranked local record and page. Expected artifacts and
negative examples are outside fixtures and must remain hidden from workers.
Selftest validates deterministic workspace oracles, not semantic research quality.
Human review must assess causal use, applicability, qualifiers, lineage and
constraint preservation. Citation presence alone is insufficient. Creative
visual diversity is accepted by invariant checks and further assessed by human review.

Run `python3 -m unittest discover -s evals -p test_pack.py`. Set
`FIELDLAB_SOURCE=/path/to/skill-field-lab` to exercise its actual workspace,
command and runner paths against these cases; without it those integration
tests skip. Field Lab validate and selftest execute during materialization.
Plans are not live execution.
New eval files retain the repository default all-rights-reserved terms.

The snapshot mount is `.agents`, with direct `.agents/skills/<name>/SKILL.md`
entries and package-level `.agents/references`. This preserves the original
`../../references` links. Field Lab's safe relative mount contract accepts this
layout; actual implicit host selection remains unobserved. Materialization
checks relative Markdown links throughout the copied runtime tree, rejecting missing or escaping
local targets. Each Skill's local references are copied in full.

`--control` additionally creates a true `isolated-control` canary plan with eight
rows. Those rows are deliberately excluded from the 32-row composition.
No `matched` label is used for the four factorial combinations.

All four cases are guided mechanism probes: their agent-facing prompts disclose
the mechanism under inspection. They are not natural proactivity evidence and
do not show that a worker would discover the mechanism without that cue.
Composition remains 32 normal task runs plus eight optional isolated-control
runs, with fixed source refs and separate control plans.

The settled task transforms 90 records with fixed filtering, labels, order and
aggregation. Its hidden assertion carries the evaluator-owned canonical digest
for the expected result and the original `records.json`; it does not recompute
expected answers from mutable worker input. Altering the supplied input is
rejected as task-input drift, and exact changed-file checks reject added or
modified collateral. Engineering
lookup separates a historical benchmark, current v2 benchmark and same-lineage
mirror. Creative lookup separates mechanism from incidental cloud deployment.
Search returns deterministic query-specific rank/snippets; page reads return
complete local records. No network is used.

Hidden command assertions run Python in isolated mode and evaluate
evaluator-owned values separately from the file-existence and exact
changed-file gates. Workspace modules cannot replace `json`, and altering input,
tests or adding hidden/collateral files fails the workspace checks.
Counterexamples include citation without use, remote fallback despite offline
constraints, false observation independence, stale dependent route after
correction, lost independent constraints, wrong reference applicability and
partial settled transformation. The three creative forms are explicitly tested
as valid. Human review still judges whether the claimed rationale and actual
process used evidence; passing artifacts alone cannot establish method use or
host selection.

The engineering prompt makes the local corpus available without requiring a
lookup. Its human review asks whether evidence preceded the consequential
choice; offline expected-artifact selftest does not establish autonomous inquiry.
Settled-work and direct-repair prompts do not instruct retrieval. Review rubrics
are case-specific. Sealed review material is the worker's `result.json`, never
the hidden negative artifact; regression tests resolve every declared review
path against the fixture plus expected overlay before a run can be proposed.
