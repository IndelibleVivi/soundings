---
name: shape
description: "Develop an incomplete, unstable, or consequentially ambiguous idea into a judgeable next step when the relevant material is already present but its meaning is not settled. Use when materially different interpretations lead to different outcomes, feedback invalidates the current frame, research opens a product-level branch, or an agent-added assumption is about to govern substantial downstream work. Shape with recommendations, scenarios, comparisons, real outputs, or permitted probes before defaulting to questions. Do not trigger for retrieving outside facts or references, a clear request ready for direct execution, or ordinary local decisions owned by an active domain skill."
---

# Shape

Help the person and the work discover what is worth pursuing next. Shape is not a requirements interview, a specification generator, or an approval gate. It participates in forming the understanding and lets execution continue as soon as the next meaningful action is supported.

## Reconstruct the live understanding

Before asking anything, recover:

- the outcome being pursued and the qualities it must preserve;
- choices the user has actually settled;
- mechanisms, defaults, or interpretations introduced by the agent;
- evidence that supports or threatens the current direction;
- the authority already granted and the next action under consideration.

Do not convert an unspecified dimension into a hidden requirement. Do not treat an agent proposal as a user decision because it appeared in a polished plan or specification. Use [shared working context](../../references/working-context.md) when another Skill or worker is part of the same task.

## Trigger only where the understanding changes the result

Shape when:

- two or more plausible interpretations would produce materially different products, experiences, or implementation commitments;
- feedback shows that improving the current implementation would still solve the wrong problem;
- external inquiry reveals a new product-level possibility or a deciding trade-off;
- an agent-added assumption is about to organize substantial downstream design, content, code, or evaluation;
- the goal is deliberately exploratory and a concrete possibility can be developed from the material already present.

Do not start a shaping exercise for a clear small change, an implementation detail already delegated to the agent, or a local design decision that the active domain method can resolve without reframing the goal. Questions are not evidence of care; use them only when the answer controls a real owner-held choice.

If the missing material is outside the current context and finding it could change the choice, yield to Search. Shape may resume after the evidence creates a product-level branch; it does not need to accompany every Search result.

## Find the uncertainty with the largest downstream effect

Look for the interpretation or assumption that, if wrong, would invalidate the most meaningful work. Distinguish internal correctness from experiential or product validity. A model can be consistent, a build can pass, and a service can integrate while the result still fails the intended experience.

When an agent-added assumption materially changes the experience or implementation and will support a large body of work, expose it in practical terms:

> I am currently interpreting X as Y. That makes the work behave like Z and will require A downstream. The next artifact or probe should let us tell whether that interpretation is right.

This disclosure does not automatically pause execution. If the user already authorized a reversible probe or implementation, continue while making the assumption judgeable.

## Make the decision easy to experience

Choose the least costly material that can reveal the meaningful difference:

- a grounded recommendation with the concrete trade-off;
- a usage scene or worked example;
- comparable samples that differ on the actual decision;
- a representative output or interaction;
- a permitted probe in the real environment;
- one focused question when the missing information is genuinely the user's to supply.

Read [making-it-judgeable](references/making-it-judgeable.md) when choosing or producing that material. The artifact need not be minimal when a thin fragment would hide the difference; it needs enough fidelity to test the assumption without silently becoming the final product.

When the current request authorizes you to produce the material and it fits in the current task, produce it now. Do not stop at a plan saying that representative questions, samples, comparisons, or outputs should be made later. Planning the evidence is not the same as giving the person something they can judge.

## Treat feedback as bounded evidence

A response is sufficient when it resolves the dependency for the next action. “The first direction is closer” may select what to develop without approving names, content, all screens, or release quality. “This feels repetitive” rejects the observed experience without necessarily changing the intended length, result space, or other unaffected goals.

Use [assumptions-and-corrections](references/assumptions-and-corrections.md) when feedback changes the current frame, a plan or specification contains agent-added product meaning, or the correction must propagate across artifacts. Update affected descendants and preserve independent goals. Do not over-correct by removing wanted behavior that the feedback did not reject.

## Continue as soon as the work is decision-ready

Stop shaping when the next meaningful action no longer depends on an unowned product or value choice. Preserve useful openness that does not block the current action. Continue under the active engineering, design, writing, or domain method instead of creating a second plan, handoff ritual, or competing brief.

Authorization follows the user's request, not the Skill name. A shaping conversation does not authorize edits; an authorized implementation does not require a new approval merely because Shape exposed a provisional assumption. Keep implementation, successful verification, and user acceptance distinct.
