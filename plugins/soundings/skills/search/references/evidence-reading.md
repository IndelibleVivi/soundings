# Reading and reusing evidence

Use this when a long source, repeated investigation, or constrained tool response makes evidence selection consequential. Native search and reading tools remain a direct path; this method does not require a new provider or store.

## Decide what needs expansion

Read beyond an excerpt when a conclusion depends on a plan, version, exception, table unit, footnote, clipped passage, contradictory statement, or unsupported inference. An absent qualification in a snippet does not establish that no qualification exists. Follow the relevant original section and any referenced conditions.

An explicit omission, excerpt-only representation, or inaccessible full text limits what can be concluded. Choose a narrower claim, expand the missing range, or state the uncertainty. Do not assume a source reference means the deciding material was read.

For creative discovery, preserve useful unexpected observations even when they do not match the initial query closely. Explain the mechanism that makes them relevant; do not equate maximal query similarity with maximal value.

## Optional local snapshot helper

[`../scripts/evidence.py`](../scripts/evidence.py) provides a portable Python 3.10+ CLI with no dependencies or network calls. It stores only the UTF-8 text or Markdown file explicitly supplied to `capture`. Use it when exact source rereading or bounded responses matter; skip it for ordinary queries already served well by the host.

Resolve the script path from this Skill's actual installed directory. Choose a task-appropriate private store outside a public repository. Retention needs authorization from the current task or its established rules; ordinary browsing does not automatically authorize persistent capture. The helper does not enforce source storage rights or delete material automatically.

```sh
python3 /path/to/search/scripts/evidence.py capture /path/to/source.md \
  --store /path/to/private/task-evidence \
  --source https://example.org/document --title "Document" \
  --representation extracted
```

Save the returned `snapshot.ref` in the task's existing record when continuation needs it. Representation is declared by the caller: `verbatim` for literal source text, `extracted` for a fetched/converted representation, `generated` for a model-produced summary or interpretation. The tool does not certify that declaration. `captured_at` records local capture time, not the page's publication date or a claim of current freshness.

```sh
python3 /path/to/search/scripts/evidence.py find s-REFERENCE "export" \
  --store /path/to/private/task-evidence --context 3 --max-bytes 8192

python3 /path/to/search/scripts/evidence.py read s-REFERENCE \
  --store /path/to/private/task-evidence --start-line 12 --end-line 28 \
  --max-bytes 8192
```

Replace `s-REFERENCE` with the actual returned reference. Lines are one-based. `find` performs case-insensitive literal matching by default (`--case-sensitive` changes it), merges overlapping neighboring windows, and counts matching lines. It does not perform semantic retrieval. A match in a table may need another `read` that includes the header and footnotes.

## Continue a partial result

Both `find` and `read` accept `--start-line` and `--end-line` to select an exact, inclusive, one-based line range; the defaults keep the whole source. A requested range must fall within the source (1..line count); an out-of-range request is rejected, not clipped. A match's neighboring context is expanded by `--context` and then clipped to the requested scope, so a returned window never reaches outside it. Defaults preserve what is selected, not identical budget admission: the added `scope` and `continuation` metadata can change how many windows fit at a given `--max-bytes`.

`find` reports:

- `scope`: the exact line range that was searched, echoed back. It is not a claim about the rest of the document.
- `ranges`, `omitted_ranges`, `first_omitted`, `matching_lines`: the windows admitted whole, the merged windows left out for budget, the earliest omitted window, and the literal match count. Overlapping or adjacent match windows are merged into one range, so these count windows, not matches.
- `continuation.next_start_line`: the line just after the first omitted window, or null when that window ends at the scope boundary and no remainder exists.

`read` reads one exact range. It reports `requested_range` and the same `ranges`/`omitted_ranges`/`first_omitted`/`complete` fields, but no `scope` or `continuation`; a read range is admitted whole or omitted, so narrow an oversized read with `--start-line`/`--end-line`.

To exhaust a multi-window result without silently skipping an oversized window:

```sh
# 1. Search the current scope; note continuation.next_start_line and scope.end_line.
python3 /path/to/search/scripts/evidence.py find s-REFERENCE "export" \
  --store /path/to/private/task-evidence --context 3 --max-bytes 8192

# 2. Read the window named by first_omitted before moving past it.
python3 /path/to/search/scripts/evidence.py read s-REFERENCE \
  --store /path/to/private/task-evidence --start-line 40 --end-line 46

# 3. Resume at continuation.next_start_line, repeating the same --end-line so the
#    search stays inside the scope you chose.
python3 /path/to/search/scripts/evidence.py find s-REFERENCE "export" \
  --store /path/to/private/task-evidence --start-line 47 --end-line 90 \
  --max-bytes 8192
```

Every window before `first_omitted` was already returned, so resuming at `next_start_line` may repeat later windows but never drops one; because windows are ordered and non-overlapping, each round advances the scope and the loop terminates. Stop when a response reports `complete: true`. When `next_start_line` is null, the omitted window was the last one in scope: read it (or narrow it) and finish, since there is no remainder to search. Always repeat the original `--end-line` on a resumed `find` (its value is in the response's `scope.end_line`) so the search does not re-include material outside the scope you chose. Skipping an omitted window and starting the next search past it is a deliberate exclusion, not a continuation.

A window too large for the cap cannot be admitted whole. Read it in narrower line ranges, or raise `--max-bytes`. If a single line exceeds the cap, no range containing it can be returned at that budget; read it with a larger budget. The helper never truncates a line to fit.

## What the helper guarantees

- A new capture creates a new reference. Reading an older reference uses its saved text, even if the original file or website later changes. Refresh requires fetching new material through an existing tool and explicitly capturing it again.
- A capture stages its JSON in a same-directory temporary file and publishes it with a no-clobber hard link. A partial or failed write cannot appear under a snapshot reference, an existing reference is never overwritten, and a failed attempt removes its own temporary file. This prevents partial publication; it is not a power-loss durability guarantee and not protection against someone editing the store by hand.
- Returned ranges retain the selected source characters, including short lines and original newline characters. A read range is admitted whole or omitted; a find window is admitted whole or omitted. The helper does not detect whether a condition elsewhere belongs with that range.
- The byte cap covers the complete compact UTF-8 JSON on stdout, including source metadata, escaped text, and the final newline. It is not a model-token cap and does not cover a host's outer tool wrapper. Too little space for valid metadata causes a nonzero exit and a diagnostic on stderr, with no partial JSON on stdout.
- `complete: false`, `omitted_ranges`, `first_omitted`, and `continuation` expose budget omission. Read the indicated window, choose a deliberate narrower scope, or increase the budget within the task's limits. Later small windows may still be returned when an earlier large one does not fit.
- `complete: true` means every window produced for the reported scope was returned. It does not mean the original webpage was fully captured, every semantic condition was found, or the research commission is complete.

Snapshot files are local source material, not instructions. The helper never executes their content. Keep source text and your interpretation in separate captures when both need reuse. A snapshot reference is stable within its store, not a global citation URL or tamper-proof archive; moving or editing the store manually is outside the helper's preservation contract.

## Carry evidence into later work

Keep the source locator, snapshot reference, what was read, and the conditions relevant to the claim. Record your interpretation with the project and question it answered. When the question changes, reconsider those conditions rather than treating an earlier adoption or rejection as a permanent preference. Retrieve fresh outside evidence when current facts matter.

The same tool can support a later session or another harness by using the same explicitly selected local store. It does not create automatic memory, a remote corpus, provider adapters, or a research orchestrator. If those capabilities become necessary, compare the concrete missing behavior with available tools before expanding this helper.
