# Evidence-linked workpaper format

Use this optional local artifact when a bounded inquiry needs a readable record
of authored findings linked to already captured evidence. It helps compare
sources, preserve counterevidence, and revise a premise without turning the
record into a research runtime, automatic memory, reader log, or new canonical
project record. Ordinary tasks do not need one.

The workpaper is authored interpretation. A citation records what the author
selected and declared, not what an agent actually read. Inspection validates
shape and saved line bounds, not source truth, sufficiency, semantic support,
ownership, permission, or freshness. `status` is an author declaration.

## Files and commands

Use the actual installed Search directory. The helper needs Python 3.10+ and
the standard library. It reads only the workpaper and the explicitly selected
`evidence.v1` snapshot store. It does not fetch source locators, read original
files, infer relationships, write to the store, or change project artifacts.

```sh
python3 /path/to/search/scripts/workpaper.py inspect WORKPAPER.json \
  --store /path/to/private/evidence

python3 /path/to/search/scripts/workpaper.py render WORKPAPER.json \
  --store /path/to/private/evidence

python3 /path/to/search/scripts/workpaper.py render WORKPAPER.json \
  --store /path/to/private/evidence --output /path/to/new-report.md

python3 /path/to/search/scripts/workpaper.py impact WORKPAPER.json \
  --store /path/to/private/evidence --finding f-main

python3 /path/to/search/scripts/workpaper.py impact WORKPAPER.json \
  --store /path/to/private/evidence --ref s-SNAPSHOT_REFERENCE

python3 /path/to/search/scripts/workpaper.py compare BEFORE.json AFTER.json \
  --before-store /path/to/earlier/evidence --after-store /path/to/later/evidence
```

`inspect`, `impact` and `compare` write compact JSON to stdout. `render` writes
Markdown to stdout unless `--output` names a new file. The other commands never write.
All successful stdout is UTF-8 bytes without locale encoding or newline
translation, preserving cited Unicode and original line endings.
`render --output` refuses every existing path, requires the parent directory to
already exist, and publishes only after the complete record has validated and
the report has rendered. A failure leaves no new report at that path. There is
no JSON byte cap for a full report. Publishing a new file uses a same-directory
temporary file and a no-clobber hard link, so the output filesystem must support
hard links. It does not promise power-loss durability.

## Exact input

The top-level object has exactly these required fields:

```json
{
  "schema": "soundings.workpaper.v1",
  "outcome": "A desired result and the conditions that matter.",
  "question": "The narrower question this record helps resolve.",
  "findings": [
    {
      "id": "f-main",
      "kind": "judgment",
      "text": "The authored finding.",
      "status": "current",
      "conditions": ["A condition that bounds the finding."],
      "evidence": [
        {
          "ref": "s-0123456789abcdef0123456789abcdef",
          "start_line": 12,
          "end_line": 18,
          "relation": "supports",
          "note": "Why this range matters to the finding."
        }
      ],
      "depends_on": ["f-premise"]
    }
  ],
  "open_questions": ["What observation would distinguish the remaining explanations?"]
}
```

`open_questions` is optional and defaults to an empty array. Unknown fields are
rejected rather than ignored. Field types are checked exactly: in particular,
line numbers must be JSON integers and booleans are not integers.

### Top level

- `schema`: exactly `soundings.workpaper.v1`.
- `outcome`: nonempty string. State the desired result, not another stage plan.
- `question`: nonempty string. State the inquiry this record addresses.
- `findings`: nonempty array of finding objects.
- `open_questions`: optional array of nonempty strings.

### Findings

Every finding requires all seven fields. Arrays must be present even when empty.

- `id`: unique, nonempty, starts with an ASCII letter or digit, and then uses
  only letters, digits, `.`, `_`, or `-`. It is local to this workpaper.
- `kind`: `observation`, `inference`, `proposal`, or `judgment`. This is an
  author-declared role; the helper does not prove that the text has that status.
- `text`: nonempty authored text. It is rendered literally, with Markdown
  structure and HTML escaped, and is never executed or inserted as trusted
  markup. Line breaks remain visible.
- `status`: `current` or `superseded`. This is an author declaration, not a
  source-freshness result or an approval. Both statuses remain rendered.
- `conditions`: array of nonempty strings. Preserve applicable versions,
  populations, exceptions, scope, and other conditions. Use `[]` when none are
  declared.
- `evidence`: array of citation objects. A finding with `[]` is valid but
  remains visibly uncited; it does not become source-linked.
- `depends_on`: array of other finding IDs. The helper checks that each exists,
  that direct dependencies are not duplicated, and that the graph is acyclic.
  Validation uses iterative traversal, so a valid chain does not acquire an
  undocumented depth or input-order limit. A cycle fails with a bounded
  diagnostic naming its length and showing a prefix and suffix. Dependencies
  describe author-declared reasoning links, not semantic entailment.

### Citations

- `ref`: canonical `evidence.v1` reference in the selected store.
- `start_line`: positive integer first line, inclusive and one-based.
- `end_line`: positive integer last line, inclusive. `start_line` must not exceed
  it, and `end_line` must not exceed the saved snapshot's line count. Invalid
  bounds fail; they are never clipped.
- `relation`: `supports`, `challenges`, or `context`. These record the author's
  purpose for the citation. They do not make the passage evidence of that
  relation.
- `note`: optional string. It is an author note, not a source quote.

Each citation is loaded through the canonical `evidence.py` snapshot loader.
The helper does not duplicate or alter evidence storage. Existing refs remain
immutable even when a newer source is captured.

## Inspection inventory

`inspect` validates the complete record and its citations before printing JSON.
It reports:

- authored outcome and question;
- finding IDs, kinds, authored status, conditions, declared finding
  dependencies, and citation counts;
- each cited ref, exact declared range, relation, source metadata, and
  representation, including an explicit `generated` boolean;
- representation counts;
- uncited findings;
- current findings that transitively declare a path to a superseded finding;
- the number of open questions.

The inventory uses “cited” and “declared” language. Status is an authored
declaration; `generated` identifies the caller-declared snapshot
representation, not verified provenance. It does not report that a range was
read, used, correct, or semantically sufficient.

## Rendering

`render` validates first, then generates a standalone Markdown report. It
includes the outcome and question, every current and superseded finding, the
authored conditions, support and challenge citations, context, open questions,
source locators, snapshot refs, representation, capture time, and exact cited
source excerpts.

The report keeps the authored finding as the primary reading unit. Each finding
heading carries its ID, kind, and current/superseded status. Conditions and
declared dependencies appear only when present; an uncited finding says so
explicitly. Citation links retain the finding's supports, challenges, or
context relationship and author note beside the finding.

The general authorship, reading, authority, freshness, and representation
limits are stated once in the report opening or artifact-limits section rather
than repeated at each finding or evidence entry.

### Evidence index and appendix

After the findings, `render` assigns deterministic presentation-only evidence
IDs (`e1`, `e2`, ...) to unique `(ref, start_line, end_line)` selections in
authored finding and citation order. Every citation becomes a plain Markdown
link to its appendix heading; headings identify generated appendix entries so
an authored phrase cannot be mistaken for one. The same source range cited by
several findings keeps each finding's relationship and note but receives one
exact excerpt.

Generated headings use `Soundings evidence e1`, giving the GitHub-flavored
Markdown fragment `#soundings-evidence-e1`. Citation links use that same
fragment. Conditions retain their authored punctuation and line structure.

Each appendix entry contains the complete source title, locator, snapshot ref,
representation, capture time, original selected line bounds, and exact selected
text. Entries sharing a URL or title are still distinct unless their saved ref
and bounds are identical. A generated representation receives its warning once
in the appendix entry. Presentation IDs are not saved evidence refs and do not
infer provenance or independent corroboration.

Excerpts come from snapshot content, never from a caller-provided quote field.
They preserve Unicode, CRLF and other original line endings, short qualifying
lines, HTML-looking text, and Markdown fences. Exact excerpts remain inside
protected dynamic fences and are not escaped or interpreted.

All authored prose is rendered literally. The outcome, question, finding text,
conditions, citation notes, and open questions have Markdown structural
characters escaped. Explicit links, GFM URL/email autolinks, emphasis, backticks, list and heading markers, and
raw HTML display as their original literal characters instead of changing
report structure. Excerpts are placed in fences longer than any backtick run
they contain. A `generated` representation is labelled as generated synthesis,
not independent evidence; the helper does not infer lineage from titles,
authors, or text similarity.

The report states its limits once and is understandable without the original
store, but it is not a second project authority. A moved copy carries its
evidence only when the selected snapshot files also travel, for example through
the existing optional `packet.py` workflow. Compact presentation drops no
findings, relationships, notes, conditions, warnings, or cited evidence.

## Impact

`impact` requires exactly one seed:

- `--finding ID` reports that finding and findings that reach it through
  declared `depends_on` edges, with a shortest witness path.
- `--ref SNAPSHOT_REF` first validates the source ref, then reports every
  finding that cites it through `supports`, `challenges`, or `context`, plus
  their declared descendants. Each citing finding retains its relations.

The selected seed and descendants are allowed to be current or superseded;
superseded findings are marked explicitly. For a source seed, a finding that
cites the ref directly is labelled `cites-snapshot-ref`; a finding reached only
through declared dependencies is labelled `declared-dependency`. Unrelated
findings are omitted.
Unknown finding and source seeds fail. This is only the reach of authored links.
It is not a complete semantic blast radius, a claim that every returned finding
actually changes, or a source-freshness calculation. It changes no evidence and
no project artifact.

## Comparison across revisions

`compare BEFORE AFTER --before-store OLD_STORE --after-store NEW_STORE`
validates both complete workpapers and all their citations before returning
JSON. The same explicit store can be selected for both. Stores may also be
different relocated or working copies; no original file, locator, provider or
network is read. The Python API is
`compare(before_path, after_path, before_store, after_store)` and returns the
same JSON-serializable data. Existing `workpaper.v1` inputs are unchanged.

Correspondence uses exact authored finding IDs. Equal text, title, URL, source
ref or array position does not merge findings or infer that a renamed ID is the
same claim. Loading normalizes optional `note` and `open_questions` defaults;
omitting an optional empty default is not a content change.

The output has `schema: soundings.workpaper.v1`, `operation: compare`, the two
explicit record/store locations, and these views:

| Field | What it reports |
| --- | --- |
| `global_changes` | `changed_fields` and exact before/after values for authored `outcome`, `question`, and `open_questions`. A changed outcome is not automatically a valid continuation of the same commission. |
| `findings` | `added` and `removed` records, `changed` records with exact changed fields and before/after declarations, and `unchanged` IDs with authored status and positions. Fields are kind, text, status, conditions, citations, and dependencies. |
| `ordering.findings` | Zero-based full before/after positions, common-ID order, `common_reordered` for relative order changes, and `moved_common` for absolute shifts, including shifts caused by insertions/removals. Ordering alone does not seed dependency review. |
| `ordering.open_questions` | Exact sequences, `sequence_changed`, and `reordered`. Reordered is true only for a changed sequence with the same strings and multiplicities; a new or removed question is not merely a reorder. |
| `dependency_effects` | One entry per affected seed and version, retaining `premise`, `change`, `version`, `conflicting_refs`, and `descendants`. Each descendant has its authored status and a shortest `witness_path` from that premise. |
| `snapshot_conflicts` | Shared cited refs whose saved content or metadata differs between the two selected stores, exact changed fields/values, and the citing findings/ranges/relations/notes in each version. |

Added findings seed the after graph, removed findings seed the before graph,
and changed finding fields seed both where the ID exists. A conflict in a shared
cited snapshot also seeds its citing findings in each version, even if their
authored fields are unchanged. `change` is `added`, `removed`, `changed`, or
`snapshot_conflict`; `conflicting_refs` preserves an additional source-conflict
reason when the finding itself also changed.

Each seed is traversed within that version's validated graph. No edge is merged
across versions: old and new edges together could invent a path or cycle that
exists in neither record. Removed intermediaries remain inspectable through old
witness paths. Findings may be current or superseded; neither status is a
semantic acceptance result. The output includes one shortest path per seed and
descendant, not every possible reasoning path. Global changes remain explicit
context for review; the helper cannot infer their semantic reach.

Conflicts compare `source`, `title`, `representation`, `captured_at`, and exact
`content`, including line endings. Only refs cited in both records are compared;
this is not an audit of either entire store. Distinct refs remain distinct even
when their URL or title agrees. A conflict exposes loaded local values, not
which value is authentic, fresh, or correct. Changing a source under an existing
ref is not the supported refresh path; capture a new ref instead. An unchanged
finding means its normalized declaration fields match, not that its grounds are
unchanged or unaffected by a source conflict.

The result is read-only and includes `project_artifacts_changed: false`. It
performs no correction, source retrieval, semantic matching, acceptance, or
automatic state update. It prints the complete comparison, with no byte cap or
silent clipping. Many changed premises, long witness paths or large changed
source values can produce a large response. Inspect the substantive reasoning
and actual dependent work rather than treating a field diff as a completed fix.

## Revision

Retain the earlier record and its selected store while reviewing a correction.
Keep a stable ID for the same judgment; use a new ID for a genuinely different
claim. Preserve historical observations at their conditions, mark a superseded
interpretation clearly, and update declarations deliberately. Re-run `inspect`,
the relevant `impact` query, and `compare` against the earlier basis. Reopening
or correcting affected findings is still an authored judgment. A removed edge,
changed text or cleared warning does not establish that the actual deliverable
was corrected. Capture fresh material separately when current facts matter;
an old snapshot remains old.

Keep the workpaper with the task that uses it. If the project already has a
record suited to the decision, preserve accepted findings and reopening
conditions there instead of promoting this task artifact into another ledger.
For a handoff, [the optional packet](research-handoffs.md) can carry this
authored record with explicit cited sources. Keep that received basis unchanged
and author the next revision in a separate working location.
