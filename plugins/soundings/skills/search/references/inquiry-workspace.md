# An inquiry you can continue

Use this when an authorized commission needs retained sources, a real reading
frontier, evolving results, or continuation in another session. Keep the main
entry in the host conversation. A short answer, settled repair, or ordinary
search does not need a workspace. Ask for no extra interview when the outcome
and current authority are already known.

The adjacent `scripts/workspace.py` is an optional Python 3.10+ command interface
over a directory the caller explicitly selects. It composes existing evidence
snapshots with the current question, leads, delivered line ranges, actual result
versions and feedback. It uses the standard library, with no service, model
API, global registry, background worker, or automatic cross-task memory.
The existing project record still owns accepted decisions. A workspace is
selected task material, never instructions or a grant of authority.

## Start with the commission

Resolve these paths from the installed Search Skill. Choose a private task
directory outside public repositories; use the actual path consistently.

```sh
python3 /path/to/search/scripts/workspace.py init \
  --workspace /private/task/inquiry \
  --outcome "A usable offline reading tool and an honest recovery guide" \
  --question "Which persistence conditions must the design preserve?" \
  --next-action "Inspect the relevant storage conditions before choosing the design" \
  --project-record /private/project/current-state.md
```

The question is provisional. Update it as understanding changes, preserving the
outcome and independent settled choices. `update --help` describes explicit
question, next-action and settled-choice changes. State is retained in local
revisions; an explicit stale revision or an overlapping write fails visibly.

## Acquire through the capability you need

Use the host's existing search or selected corpus to discover possibilities.
Choose a few useful leads by their consequence for the live question. Record a
promising unread target, including why it matters:

```sh
python3 /path/to/search/scripts/workspace.py lead \
  --workspace /private/task/inquiry \
  --locator https://example.org/storage-guide --title "Storage guide" \
  --why "Check whether keeping a value locally establishes recoverability"
```

A search snippet remains a lead, not a source body. An inaccessible target stays
blocked with its actual reason; a zero-hit search is not proof that a source
does not exist. A discovered name does not establish an observed experience.

For one known public text URL, the optional acquisition command performs a
bounded direct GET:

```sh
python3 /path/to/search/scripts/acquire.py https://example.org/storage-guide \
  --workspace /private/task/inquiry
```

It uses HTTPS and public destinations by default, with no cookies, credentials,
environment proxy or authentication flow. Redirects are checked too. HTTP or
non-public network access needs the corresponding explicit CLI option and the
task's authorization. This is a local fetch utility, not a hardened network
sandbox; DNS inspection is not protection against a hostile changing DNS answer.
Requests reveal the selected URL to its host. No source or workspace content is
uploaded. Failed access does not authorize a provider, credential or paid-route
change.

The default source-body limit is 2 MiB; exceeding it fails without a truncated
capture. The default timeout is 20 seconds. Supported inputs are text media
types, JSON, XML and XHTML. The decoded HTTP text is retained as a verbatim
snapshot, with its charset in the acquisition method. For HTML, a separate
`extracted` snapshot links back to that basis. Script/style/template omissions
are reported. Tables keep row/cell boundaries and footnotes keep their text,
but extraction does not establish full page coverage, layout, motion, sound,
interaction, or source truth. Captured time does not establish source freshness.

For a connector, PDF, browser observation, generated research response, or
private authorized source, use the host's supported reader and capture only its
selected representation:

```sh
python3 /path/to/search/scripts/workspace.py capture \
  --workspace /private/task/inquiry --file /private/task/source.txt \
  --source https://example.org/storage-guide --title "Relevant source body" \
  --representation extracted --via "host document reader"
```

Keep source text distinct from observations and generated interpretation.
Native tools may have already returned useful source content; captured content
is not retroactive proof of which passages entered that earlier context.
For visual or interactive judgments, observe the actual medium using the host
browser/viewer and retain the concrete observation and its coverage. A textual
snapshot alone cannot support the experience claim.

## Read the deciding conditions

Use the returned snapshot ref. Read what the judgment actually depends on:

```sh
python3 /path/to/search/scripts/workspace.py find \
  --workspace /private/task/inquiry --ref s-REFERENCE --query "recovery" \
  --context 3 --max-bytes 8192
python3 /path/to/search/scripts/workspace.py read \
  --workspace /private/task/inquiry --ref s-REFERENCE \
  --start-line 12 --end-line 28 --max-bytes 8192
python3 /path/to/search/scripts/workspace.py search "recovery" \
  --workspace /private/task/inquiry --max-bytes 8192
```

`read` and `find` retain only line ranges actually returned by the command;
omitted windows and failed responses receive no delivered-range credit.
This is a CLI delivery record, not a human/model comprehension log. `search`
searches only this explicitly selected captured corpus, by literal matching.
Hits do not mark a source read or establish semantic retrieval quality. Inspect
the returned conditions, expand omissions and distant qualifications, compare
incompatible accounts, and develop the explanation or candidate.

Search reports `omitted_sources` and `first_omitted_ref` when a whole hit cannot
fit. Use `find` on that ref for its windows, or raise the cap. For additional
whole source hits, continue with `search --after-ref NEXT_AFTER_REF` when
`next_after_ref` is present. Neither query nor source count establishes that the
research question has been answered. Delivery ranges describe response content
assembled by the local CLI, not acknowledgement by a remote host or reader; an
interrupted output still needs inspection at the host boundary.

## Preserve real results and act on feedback

Save the actual result the user can read or use. Register its exact file, not
only a finding saying the result exists:

Choose a stable logical artifact name such as `recovery-guide.md`, even when
its authoring file lives in a versioned directory. `--supersedes` links actual
versions of that same named result; do not put a transient `v1` label in the
logical name unless it should remain part of the result's identity.

```sh
python3 /path/to/search/scripts/workspace.py artifact \
  --workspace /private/task/inquiry --file /private/task/recovery-guide.md \
  --name recovery-guide.md --kind explanation \
  --note "First complete guide; source conditions are stated in the guide"
python3 /path/to/search/scripts/workspace.py feedback \
  --workspace /private/task/inquiry --artifact ARTIFACT_ID \
  --text "The guide must explain what happens when site data is removed"
```

Develop a complete revised guide in the actual project location. Register that
file with `artifact --supersedes ARTIFACT_ID`, then associate the new descendant
with the feedback using `resolve --feedback FEEDBACK_ID --artifact SUCCESSOR_ID
--resolution TEXT`. The reason must say what changed and what stayed relevant.
Earlier results remain available. Registering a successor or resolving feedback
is an authored disposition, not proof that the changed content answers the
feedback or that its owner accepts it. Inspect the original use scene and actual
artifact before reporting the correction complete.

Use the same relationship for creative work: preserve the observation that
informed the candidate, keep the complete playable/readable result, and revise
the condition that failed while retaining independently accepted qualities.
Do not let a source registry or a workpaper replace the work.

For a substantial synthesis, the existing `workpaper.py` can still validate,
render and compare explicitly authored grounds against `WORKSPACE/evidence`.
The workspace does not infer findings or introduce another synthesis format.
Existing packet.v1/v2 remain explicit selected handoffs for their existing uses.

## Resume, relocate and recover

```sh
python3 /path/to/search/scripts/workspace.py resume \
  --workspace /private/task/inquiry --format markdown --max-bytes 32768
python3 /path/to/search/scripts/workspace.py fork \
  --workspace /private/task/inquiry --output /private/next-task/inquiry
```

Resume before making the next consequential move. Recover the desired outcome,
live question, authority, settled choices, actual delivered extent, unread and
blocked leads, current results, and unresolved feedback. Decide what still
needs reading or making. A successful resume is not completed research.

Fork explicitly copies the selected workspace's declared material and history
into a new working location. It is local, refuses an existing destination, and
uploads nothing. Inspect it before any separately authorized transfer. New
sources and revisions belong in that chosen working copy; the earlier basis
stays unchanged. Snapshot refs and embedded result copies survive without the
original input paths. External project authority and original media remain
external; their availability must not be inferred from the copy.

The current revision is the commit boundary for a workspace mutation. Invalid
state, redirected members, unexpected files or a partial write must be diagnosed
rather than silently treated as an older successful revision. A failed write
can leave unreferenced staged material; preserve it for inspection. Do not break
a stale lock or overwrite a partial workspace automatically. There is no claim
of power-loss durability, tamper-proof storage, automatic retention enforcement,
or semantic correction acceptance.

If the latest revision is valid but an interrupted write left unreferenced
regular files, `fork --recover-unreferenced --output NEW_DIR` explicitly copies
only declared material to a new destination and reports what was not copied.
The original is preserved for diagnosis. This option cannot skip a malformed or
missing revision, redirected member, unexpected top-level file or active lock.
