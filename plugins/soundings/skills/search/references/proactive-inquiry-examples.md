# Proactive inquiry examples

Use this reference when a multiple-reference decision needs a complete walkthrough, or when repeated rejection makes it useful to trace failed output, accepted local state, reference observation, a rejected path, and discriminating candidate together. These are constructed hypotheticals, not live runs, real-project facts, or a required template. Use [proactive inquiry and reference choice](proactive-inquiry.md) for the concise method.

## CONSTRUCTED example: task, session, and recovery

**Initial request:** "Continue making this workbench easier to use." No task model, search term, failure, or vendor is supplied.

**Local material and observation:** The constructed workbench fixtures show that a task can collect several edits before a change is accepted. A session currently ends when the pane closes; reopening loses the active pane layout but not the saved task. A task can be abandoned, and the saved task and recent attempt are shown without a clear relation. Replaying an interrupted-edit scene and a share-after-restart scene makes the ambiguity visible. A reasonable local baseline is the existing saved task and accepted edits; the open dimension is how attempts and sessions should relate to it, not whether the product must add another durable runtime.

**Hypothetical reference observation:** Three constructed workbenches use the words differently. Pallet treats a task as a shared canvas, ends a session when its pane closes, and restores the last saved canvas. Ledgerline attaches attempts to a durable conversation and recovers by replaying every attempt, including rejected ones. Mosaic owns state per task, treats a session as a temporary view, and distinguishes an accepted checkpoint from a saved attempt. Their descriptions alone do not establish the behavior; the constructed scene replay is the observation.

**Own conditional judgment:** The local evidence and fixture behavior support separating the task's accepted state from the transient pane session. Mosaic's state relationship is the closest starting clue. Ledgerline's full-history recovery would make abandoned attempts look current, while Pallet's session ending makes it harder to recover the working relation. This supports a local state-and-recovery relationship, not adoption of Mosaic as a system or a new runtime.

**Rejected path:** Replay the full history because it appears most recoverable. In the share-after-restart scene, it resurfaces an abandoned attempt as if it belonged to the current task. The recovery benefit does not erase that conflict with the local accepted state.

**Candidate change:** Keep the existing saved task and accepted edits. Reopening restores the previous pane context as session state; a recent unaccepted attempt stays visibly separate and can be continued or discarded. A share action uses the accepted task state and does not silently merge the attempt.

**Return to the initiating scene:** A person who had an interrupted edit reopens the workbench, resumes the pane context, can inspect the attempted change, and can share only the accepted task. That observed scene is the judgment; the example does not establish a need for every workbench to store attempts separately.

The nearby clear small edit "Rename Save to Store mix and update its test" stays direct. Its scope and applicable evidence are already settled.

## CONSTRUCTED example: repeated rejection

**Initial request:** "The seed picker still feels like a form, and I have rejected the last two attempts. Make the selection feel touchable without losing the species cards, keyboard navigation, or the chosen planting order."

**Local material and observation:** The hypothetical rejected candidates and the existing accepted species cards, keyboard controls, and planting order form the local baseline. At realistic viewport sizes, the first candidate made twelve seed tiles spring upward on hover, but selection immediately reshuffled the tray and obscured which seed had been placed. The second reduced motion but retained the automatic reshuffle, so it still delayed and hid the consequence of a deliberate choice. No human testing is claimed.

**Tempting reference and counterevidence:** A constructed reference wheel offers pleasant flick-and-snap selection. Direct hypothetical interaction shows that it assigns a seed automatically and makes a repeated deliberate placement awkward. The physical feedback is useful; automatic assignment conflicts with the accepted card and planting-order relationship and with keyboard reuse.

**Own conditional judgment:** The repeat complaint has a supported interaction-relationship explanation, not merely an execution-quality explanation. The user wants selection with a visible local consequence while preserving deliberate placement. The wheel is not rejected as a whole; its feedback clue is separable from its automatic assignment.

**Rejected path:** Add richer physics or randomized motion to the stable tray. A third version could look livelier while preserving the same allocation relationship, so it would not discriminate the suspected cause. One rejection does not ban all motion; it does not justify treating motion as the solution.

**Candidate change:** Keep each species card, its keyboard actions, and the chosen planting order. The tray remains spatially stable. Choosing a seed moves a visible token toward the next planting slot, its numbered path shows the new order, and undo returns it to the same tray position. This candidate varies the interaction relationship while holding accepted content and input steady.

**Return to the initiating scene:** The person can select several seeds repeatedly, compare the resulting order, correct one placement, and continue by keyboard. The scene now distinguishes touchable from merely animated through the visible local consequence, without approving final art or plant names. Failure of this candidate would reopen the interpretation, relationship, execution, or fidelity rather than the whole inquiry.

## Preserve boundaries

These examples do not require a new candidate pipeline, durable store, reference audit, or output format. A clear small repair still proceeds directly. A supplied-material-only synthesis remains within its supplied boundary. Research-only work can complete through a useful explanation.
