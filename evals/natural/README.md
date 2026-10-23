# Natural-task offline suite

This suite is an independent constructed research surface beside the historical
32-row guided composition and its optional eight-row isolated control. It does
not replace or relabel their evidence. It starts no target model, makes no
provider calls, and does not establish implicit host selection or research benefit.

Five task families ask for ordinary usable outcomes:

| Family | Outcome | Executable acceptance |
| --- | --- | --- |
| Open engineering | Finish a restart-safe local notes tool | Separate-process put/get, uncommitted-stage recovery, overwrite, missing keys, Unicode and directory relocation |
| Open reading desk improvement | Work from two sources into an attributed argument and return/export | Actual browser collection, writing, reload, browser-context restore and downloaded export |
| Substantial settled work | Complete a fixed 120-record transformation | Independent full filtering, ordering, labels and group totals |
| Precise local repair | Repair caseless identifier normalization | Executed CLI, blanks, stable deduplication and Unicode casefold |
| Settled work with a new factual obstacle | Repair the notes integration after a dependency release change | Same recovery contract as engineering, exercised against both runtime worlds |

The A prompt gives the task and accepted constraints without directing research,
query words, answer-key declarations or preferred implementation mechanisms. N
has the identical prompt, production code and verification capabilities, with no
additional reference corpus. F appends a bounded inquiry requirement to A. E
appends relevant factual evidence with role/version/lineage identity to A; its
optional corpus remains available. Fixed CLI, report schema and browser hooks
are compatibility constraints, not research answers. A and N neither require nor
prohibit research. Direct reads of production code remain legitimate inquiry in
all conditions.

Engineering and obstacle each have `local` and `durable` runtime worlds with
identical task prompts and public `Store` API. These are real synthetic runtime
implementations: `local` holds values only in the process even after `commit`;
`durable` atomically writes committed snapshots and reloads them in new
processes. Uncommitted sets disappear in both. Documentation follows actual
world semantics. The initial application fails recovery in both; a native
runtime solution passes in `durable`, while an adaptive application-owned
committed store passes in both. Acceptance evaluates behavior, never whether an
implementation name flips between worlds. This permits correct adaptive
implementations without assuming evidence must force a different architecture.

There are 28 cases: seven family/world combinations × four conditions. A future
A/E pilot plan has 14 rows with one repetition; it is a plan only. F changes an
instruction and time allocation; E changes information availability and salience;
N removes material affordances. World variants change runtime facts and their
documentation together. These interventions are explicit causal confounds, not
exchangeable observations of a single isolated mechanism. No scores or benefit
claims are published here.

Human review criteria are task-family specific and identical across A/F/E/N
within each family. Functional outcome, evidence acquisition/use, and method
selection/causal benefit are separate judgments. Engineering and obstacle review
check current runtime applicability and the dependent implementation; obstacle
review also checks the release-related diagnosis. Settled-work and precise-repair
review allow correct direct work and assess any acquired evidence conditionally;
consultation itself is not a pass/fail criterion. Reading review assesses its
attributed workflow and applicable reference mechanisms, with a separate quality
criterion that leaves aesthetic acceptance unverified by functional checks.
Passing artifacts, citations and acquisition events alone establish neither method
use nor causal benefit; benefit claims require comparison evidence. Prompt
interventions remain as described above and do not change these outcome criteria.

The canonical `corpus.py` supports lexical natural-language query ranking,
query-dependent snippets and complete page reads. Every result identifies role,
version and observation lineage. The corpus includes old releases, same-lineage
mirrors, irrelevant material and inapplicable cloud deployment details. Use `--corpus-variant irrelevant` to build a separate pack with only the
unrelated page and no reference demos; task prompts, production tools and
functional acceptance stay identical. E still supplies its direct relevant
evidence. Keep that intervention separate when comparing outcomes; the default
`mixed` corpus includes applicable and distracting pages. Its two
original runnable reference mini-experiences have different mechanisms: attach
an annotation to a selected source passage, or collect and reorder evidence
cards around a claim. Both preserve attribution and local draft state. Their
layout, controls and deployment details are examples, never normative design.
Aesthetic quality and applicability judgment require human review.

Use `python3 corpus.py --log /private/output/access.jsonl search "your question"`
and `... read PAGE_ID` from a materialized fixture. The log destination must be
explicit and outside the fixture. Logs describe tool access only. Direct reads,
code inspection and other acquisitions are not exhaustively logged; absence of
a log entry does not prove absence of inquiry. This is a deterministic local
CLI, with no backend or automatic network fetch/upload.

Build a **new Git-external** pack using an existing pinned public subject
snapshot whose root contains `skills/<name>/SKILL.md` and shared `references/`:

```bash
python3 evals/natural/build.py \
  --output /private/output/new-natural-pack \
  --subject /existing/pinned-subject-snapshot \
  --subject-pin 'explicit source commits or snapshot identity' \
  --subject-label 'public runtime snapshot provenance' \
  --fieldlab /existing/skill-field-lab-checkout \
  --node /existing/bundled/node \
  --playwright /existing/bundled/node_modules/playwright
```

The builder copies that subject without changing it and mounts the copy at
`.agents`; it does not resolve a moving branch or claim the caller's identity
label verifies source provenance. It records the supplied pin and label in
`composition.json`. Only an existing snapshot is accepted. Output must be new;
source trees and existing outputs cannot be overwritten. There are no installs.
Python 3.10+ and an existing Field Lab checkout are required. Browser checks need
an already provisioned Playwright Chromium binary; the supported launch uses
Playwright's bundled testing browser, without everyday Chrome profiles, custom
debug flags or a stable-channel override. The builder runs current Field Lab
`validate` and `selftest`. A missing browser is an explicit failed check, not a
functional pass. Add `--model EXPLICIT_MODEL --effort high` to prepare the
14-row A/E pilot plan without starting it.

`sealed/` and case `expected/` overlays remain outside worker fixtures. Command
assertions run the sealed Python verifier with `-I`; no worker code is imported
into the verifier. Submitted production programs execute in child processes.
Accepted runtime, record and source inputs, `MATERIALS.md`, corpus tool, corpus
pages and reference demos must match sealed copies exactly;
drift is rejected even with an otherwise valid program. `INTERFACE.md` is editable
product documentation: a worker may document completed behavior there. Actual CLI
and browser acceptance are defined by the sealed executable oracle; changing the
document cannot make a broken program pass. This applies to newly built packs;
previously frozen packs retain their original fixed-input and review contracts.
The builder never edits or migrates historical packs or run records. Production programs
execute with `-B` in a separate temporary tree containing sealed accepted inputs.
The verifier never writes into the final verifier workspace, including bytecode.
The settled task checks both the delivered report and a fresh executable run. Field Lab
executes command assertions in separate copies of the sealed final workspace;
scratch execution effects are verification effects, not worker deliverables. Keep the
pack's sealed files inaccessible to target workers using the runner's existing
isolation boundary. A filesystem location alone is not a security sandbox.
Worker assertions such as `result.json` never satisfy these functional oracles.
The suite is designed against accidental answer-only and input-tampering passes,
not malicious code execution beyond the runner's existing trust boundary.

Run deterministic source checks without Field Lab or a browser:

```bash
python3 -m unittest discover -s evals/natural -p 'test_*.py' -v
```

After materialization, repeat runner validation explicitly:

```bash
PYTHONPATH=/existing/skill-field-lab-checkout python3 -m fieldlab validate /private/output/new-natural-pack/fieldlab.json
PYTHONPATH=/existing/skill-field-lab-checkout python3 -m fieldlab selftest /private/output/new-natural-pack/fieldlab.json
PYTHONPATH=/existing/skill-field-lab-checkout python3 evals/natural/fieldlab_copy_check.py /private/output/new-natural-pack
python3 evals/natural/browser_adversarial_check.py /private/output/new-natural-pack
/existing/bundled/node evals/natural/static_server_check.cjs
/existing/bundled/node evals/natural/demo_check.cjs /private/output/new-natural-pack/cases/reading-ordinary-a/fixture /existing/bundled/node_modules/playwright
```

Runnable `assets/*_initial.*`, `*_valid.*` and `*_bad.*` variants keep baseline,
positive and negative implementations inspectable. The optional native copy check uses the current Field Lab command assertion,
workspace-copy and tree-identity APIs directly, including a valid HTML-only
reading implementation and a valid CSS/JS split with an intermediate Save
button. Browser adversarial checks reject losing restored source evidence or
requesting external sync only after reopening. It checks both assertion success and no verifier-copy
mutation without invoking any target adapter.

The unit suite rejects unresolved applications, declarations without execution,
input tampering and premature stage commits. It accepts a valid notes program
with a product-documentation extension while rejecting the same documentation
extension paired with the original broken program. Task-fit checks keep review
roles distinct, conditions aligned and reading-only quality criteria out of other
families. It verifies real differences
between runtime worlds, accepts a native durable solution and an adaptive
solution, and checks prompt matching, corpus rank/version/lineage and fixture
separation. Field Lab selftest additionally executes baseline and valid browser
applications. Browser checks cover narrow viewport, reduced-motion setting and
bounded Tab traversal and keyboard activation of export. Both desktop and
restored narrow contexts enforce offline/error observation and re-export the
complete argument, passages, titles, authors, URLs and qualifiers. Local CSS,
JavaScript and other regular assets are served from the workspace with MIME
types; path traversal and symlink escape are rejected. These checks do not establish comprehensive accessibility or aesthetic
acceptance. Source attribution, qualifiers, duplicate lineage handling,
mechanism applicability and the relationship between inquiry and delivered
work remain independent human review responsibilities. Generated packs, plans,
raw traces, screenshots, access logs and reviews stay outside Git.
