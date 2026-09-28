# Inquiry in practice

These examples explain the work each capability can carry. Docknote and the activity are constructed fixtures, not real product research. The outcomes below were observed in fresh 0.2.0 source-candidate sessions and edited into a public explanation; raw task traces remain private. See the [evidence record](../dogfood-0.2.0.md) for the environment and limits.

## Study: a useful explanation across five materials

**Commission:** decide what apparently conflicting durability, portability, and speed claims mean for offline field notes. Notes must survive between sessions and occasionally move to another laptop on the same OS. Export writes can be serialized; undo history is not required.

The complete synthetic evidence set was:

| Material | What it says |
| --- | --- |
| A — version 1.4 guide | A preview cache lasts 24 hours. Editable notes are separate. This version has no snapshot export. |
| B — version 2.0 contract | Snapshot bundles retain selected notes and attachments until deletion; a second installation can open them offline. The preview cache remains disposable. Concurrent export writers are unsupported. |
| C — engineering note | On one laptop, 20 bundles had median warm preview time 7 ms and cold preview time 170 ms. One of 25 simultaneous-write trials produced an incomplete bundle. No other OS or device was tested; the raw timing appendix is unavailable. |
| D — newsletter | Repeats C's 7 ms and calls bundles permanent; mentions another lab without a link or data. |
| E — separate operator observation | One bundle moved from laptop A to laptop B on the same OS and opened offline with selected notes and attachments. Undo history was absent. Speed and simultaneous writes were not tested. |

**Synthesis:** the apparent durability disagreement concerns different objects and versions. A disposable acceleration cache can coexist with durable editable notes and explicitly retained transfer snapshots. The compatible design is local working files, replaceable preview cache, and serialized snapshot export.

The session did more than summarize five documents. It connected the observed write failure to the contract's concurrency boundary, kept the cross-device observation separate from same-laptop timings, and recognized that the newsletter adds no new timing measurement. It proposed immutable completed transfer artifacts as a design inference; the sources do not themselves prove crash recovery, backup safety, or future compatibility.

The judgment is qualified: same-OS transfer has one supporting observation, speed describes preview medians on one machine, and an unavailable appendix remains unavailable. Neither “permanent” nor “universally portable” follows. The lack of undo history is compatible with this commission, rather than automatically a defect.

## Explore: deliver the creative work

**Commission:** make a six-minute activity for three adults waiting for a train, with paper and pencils, no acting or personal disclosure, and choices that create an imaginary place. Deliver facilitator wording, all play material, and one whole playthrough.

Explore produced [Six Minutes to Elsewhere](six-minutes-to-elsewhere.md), a complete printable activity. A through-or-around route changes the next landmark; choosing shelter or a view changes what appears; a bridge or barrier changes the final marks and traversal. The mechanism is shared authorship through consequences that become material for the next person.

This is a result someone can try, rather than an offer to make a prototype later. The playthrough shows one coherent route through the rules. It does not establish real group pacing or enjoyment; those need actual play. A thin or awkward first play would need diagnosis before rejecting the mechanism itself.

## Shape: propagate a precise correction

**Commission:** a six-round local reflection experience has become a 1–5 trait questionnaire with an averaged personality score. Replace that unwanted mechanism while preserving six rounds and substantial reflection. Update both the specification and executable prototype, then show a complete run.

The fresh session replaced the rating path with six connected scenes at a fictional flooded signal station, A–C actions with consequences, optional notebook details, and a reflection grounded in the chosen events. Both specification and implementation changed. The generated demo completed all six rounds; four local checks covered scene structure, scripted choice validity, recall in reflection, and the complete demo.

The observation supports bounded correction propagation: rejecting ratings did not erase the accepted length or reflection goal, and the agent continued through implementation. It does not establish deep branch coherence across every possible run, psychological validity, or owner acceptance of the writing. Shape makes the corrected experience available to judge; domain craft still owns its quality.

## Where Search and the evidence helper fit

A separate Search case checked an 80 MB file against GitHub's official Repository Contents documentation. The deciding condition was the raw media representation; the large-file object response does not contain the file body. The method preserved this condition rather than treating a size limit alone as the answer. See the [primary documentation](https://docs.github.com/en/rest/repos/contents#get-repository-content) for current behavior.

The [optional helper](../../plugins/soundings/skills/search/references/evidence-reading.md) supports a different claim: preserving already acquired text for explicit later rereading. It does not improve provider recall by itself, make the creative activity enjoyable, or validate a synthesis. Keep the evidence for those outcomes separate.
