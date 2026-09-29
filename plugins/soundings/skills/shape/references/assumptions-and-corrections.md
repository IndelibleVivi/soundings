# Assumptions and corrections

Use this reference when an agent-added interpretation supports substantial downstream work, feedback invalidates the current frame, or a correction must be carried through specifications, tasks, and implementation.

## Expose assumptions by consequence

Surface an agent-added assumption when all are true:

- it was not already settled by the user or an authoritative project contract;
- it materially changes the product, experience, architecture, or evaluation basis; and
- downstream work would become expensive or misleading if it were wrong.

Explain the observable consequence, not only the abstract label. State what the assumption makes the artifact do, what work it will demand, and what evidence could show it is wrong.

This is not a universal approval gate. Reversible work already authorized may continue with the assumption kept provisional and exposed to the right test.

## Propagate a correction precisely

When feedback or evidence changes an assumption:

1. Identify the exact interpretation that failed.
2. Find plans, specifications, worker orders, acceptance criteria, content, code, and tests that depend on it.
3. Update those descendants and retire superseded instructions or paths.
4. Preserve goals and decisions that do not depend on the rejected interpretation.
5. Re-evaluate only decisions whose premises changed.

Do not keep an old active path “just in case” after its behavior has been replaced. Version control and explicit candidate artifacts provide recovery; stale parallel instructions recreate the same misunderstanding later.

If the user says a candidate is unintelligible, unrelated to the goal, or not a meaningful product advance, treat that as evidence that its representative role failed. Trace that role back to the agent proposal that created it. Remove the candidate from current claims, acceptance scenarios, and dependent plans; do not merely improve its presentation or run more tests on it. Preserve independently useful maintenance at its honest scope, then return to the accepted outcome and produce the replacement result the commission still requires. Historical evidence may record that the rejected candidate existed, but it must remain visibly rejected rather than current proof of value.

## Bound feedback to what it establishes

- A rejection establishes that the current result is not accepted; diagnosing and repairing the cause remains the agent's work.
- A preference establishes the next relevant direction at the fidelity shown.
- A complaint about repetition does not automatically change total length, scope, or result diversity.
- A technical pass does not establish experiential acceptance, and experiential approval does not replace technical verification.

Continue all work supported by the feedback and existing authority. Ask again only if the correction reveals a genuinely new owner-held choice.
