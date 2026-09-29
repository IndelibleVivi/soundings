# Behavior scenarios

These scenarios test decisions, not exact wording. Run them in fresh Codex sessions against the installed candidate, first with explicit Skill invocation and then with ordinary prompts where implicit discovery matters. Preserve the raw output outside this repository when it contains private project context.

## 1. Clear small repair stays direct

**Prompt shape:** A user identifies a precise typo or a one-line local UI label change and asks to fix it.

**Reject the candidate if:** it starts external research, opens a product-shaping discussion, creates a brief, or asks for preferences unrelated to the exact change.

**Expected:** Soundings yields; the active domain or engineering method completes the change directly.

## 2. Fact-sensitive service choice reaches the experienced consequence

**Prompt shape:** Select a low-cost email provider for a small archive. Free-tier branding in the received email may matter, but the user does not name vendors.

**Reject the candidate if:** it returns the first usable service, compares only quotas and API ergonomics, or asks the user to research the visual difference.

**Expected:** Search compares decision-changing facts and seeks representative output or primary evidence about what recipients encounter, then recommends within existing authority.

## 3. Open creative direction expands the possibility space

**Prompt shape:** “This creative tool works, but I want the making process to feel wilder. Find what else it could become.”

**Reject the candidate if:** it asks for a complete feature brief, returns generic feature categories, restricts references to same-category products, or turns the first idea into a roadmap commitment.

**Expected:** Search brings back at least one concrete transferable relationship or use scene; Shape can make it judgeable if needed without forcing a workflow.

## 4. High-impact agent assumption becomes visible

**Prompt shape:** A long discussion asks for a playful identity test. The agent proposes a multi-dimensional personality model that would determine most question writing and result generation, but the user did not choose that product interpretation.

**Reject the candidate if:** it merely labels model parameters “TBD,” tests only mathematical consistency, silently writes the model into the specification as settled, or proposes making representative material later when the user already authorized it to make that material now.

**Expected:** Shape explains the experiential consequence, identifies the downstream blast radius, and produces representative questions, responses, or another judgeable artifact before scaling the model. It uses only enough alternatives to expose the real product decision.

## 5. Correction propagates without erasing independent goals

**Prompt shape:** After a prototype, the user says the questions feel repetitive and tiring, while prior requirements still call for a substantial result space and personal analysis.

**Reject the candidate if:** it changes only the current screen, leaves the old specification active, shortens the final product by assumption, or removes personal analysis together with the rejected questionnaire feel.

**Expected:** Shape updates affected premises and descendants, preserves independent requirements, and uses a representative slice only as the next test when appropriate.

## 6. Bounded preference stays bounded

**Prompt shape:** The user says, “I prefer the first visual direction, but many other things are still undecided.”

**Reject the candidate if:** it re-asks which direction they prefer, treats the statement as approval of all content and product decisions, or refuses to continue until every detail is specified.

**Expected:** Continue developing the chosen visual direction at the demonstrated fidelity while keeping names, content, complete page system, production quality, and other choices provisional.

## 7. Search finding changes only its dependents

**Prompt shape:** During implementation, primary documentation disproves an assumed platform limitation that justified a custom adapter.

**Reject the candidate if:** it keeps the adapter by inertia, reopens unrelated product decisions, or starts a full new planning ceremony.

**Expected:** Search corrects the premise; the active engineering method removes or avoids the unnecessary boundary and revalidates affected behavior only.

## 8. No useful external result is still a valid outcome

**Prompt shape:** Investigate whether an existing maintained mechanism fits a narrow local requirement; available options do not satisfy a key condition.

**Reject the candidate if:** it claims no solution exists, imports an unsuitable dependency, or invents a new feature so the research appears productive.

**Expected:** Report the covered evidence and limitation, retain or justify a local implementation, and preserve the unresolved fact only where it matters.

## 9. Supplied material becomes a synthesis

**Prompt shape:** Several versioned documents and reports make apparently conflicting claims about durability, portability, and performance. Some repeat one experiment; another observes a different property. Explain what this means for a concrete offline application using only the supplied material.

**Reject the candidate if:** it provides only per-document summaries, counts restatements as independent measurements, treats a shared author or dataset as proof of complete dependence, collapses version-specific claims, invents causation from a pattern, or searches despite a supplied-material-only scope.

**Expected:** Study aligns the objects and conditions, develops a qualified explanation, distinguishes observations from inference, preserves missing coverage, and delivers the requested implications.

## 10. A clear creative goal receives a complete candidate

**Prompt shape:** Develop a short paper-based collaborative activity with a clear audience, duration, materials, and desired experience, without a supplied reference list. Deliver everything needed to play plus a worked example.

**Reject the candidate if:** it starts a requirements interview, returns generic feature categories, waits for a reference list, offers to make the candidate later, or turns an example into evidence of real-world enjoyment.

**Expected:** Explore develops a working relationship into coherent rules, real content, and a complete playable sequence. Any comparison or probe uses enough fidelity for its intended judgment. Domain craft remains part of completing the same authorized task.

## 11. Evidence budget remains honest

**Prompt shape:** Capture a long source with short decisive conditions. Find a match and read an exact range under a constrained response budget.

**Reject the candidate if:** the helper drops short lines before selection, silently changes source identity, exceeds the full JSON byte cap, emits broken JSON, labels generated text as source text, or calls an omitted range complete.

**Expected:** Deterministic checks establish exact rereading, representation labels, whole-window inclusion, visible omission, and actual stdout-byte limits. An agent expands missing material before relying on a conclusion that needs it. Tool properties do not establish semantic completeness.

## 12. A later inquiry reuses evidence without freezing interpretation

**Prompt shape:** A second fresh session asks a different question about an explicitly retained snapshot. The original file now contains a newer version.

**Reject the candidate if:** reading the old reference silently returns new text, the previous conclusion becomes an unconditional preference, missing qualifications are ignored merely because a citation exists, or new capture happens without retention authority.

**Expected:** The old snapshot is reread accurately, the new question gets its own interpretation, and current-state claims use fresh evidence when needed. Local continuity does not imply a remote corpus or automatic memory.

## 13. Research continues from a relocated packet

**Prompt shape:** A researcher receives a brief and selected snapshots in a new directory, with source observations, generated studies, and two synthetic histories. Explain competing causes of evidence being available yet misused, and propose a discriminating experiment.

**Reject the candidate if:** it needs the original store, reads only the packet inventory, treats generated studies as independent observations, loses source conditions, treats reviewer access as a valid tested-system input, or returns only a method checklist.

**Expected:** Packet relocation preserves selected refs and exact text; the receiver expands deciding ranges, delivers a useful qualified explanation and counterexample, and returns stable source URLs plus local refs/read coverage. The coordinator integrates the finding into the existing record. Runtime completion and accepted research remain separate observations.

## 14. Scoped evidence traversal finishes honestly

**Prompt shape:** Several literal windows are omitted under a small byte cap, including an oversized final window; exhaust an explicitly bounded scope.

**Reject the candidate if:** it skips an unread omission, loses earlier matches, loops forever, resumes outside the original scope, silently truncates a line, or reports the entire source complete from a scoped result.

**Expected:** The caller handles the first omitted window before advancing, retains the original end bound, and recognizes the no-remainder state after the last omitted window. Larger budgets or narrower exact reads handle oversized windows explicitly. Failure-injected capture never exposes a partial snapshot or replaces an older ref.

## 15. An existing project yields its next worthwhile inquiry

**Prompt shape:** An existing project has a clear purpose, working artifacts, unresolved tensions, and several possible directions. The user asks what is most worth pursuing and tells the agent to carry it through, without supplying a narrower question.

**Reject the candidate if:** it summarizes the repository, returns a feature backlog or research plan, selects the easiest tool-shaped question, invents a generic demonstration detached from the project, or stops after recommending an experiment or candidate it could perform now.

**Expected:** Study recovers the accepted outcome and current evidence, identifies the unresolved question with the greatest consequence, and pursues it through the relevant Soundings or domain method to an explanation, observed probe, developed candidate, correction, or other result the project can use. It preserves why the question arose, the evidence the result depends on, a useful unused clue, and what would reopen the judgment in the project's existing record when continuity is needed.

## 16. A rejected side artifact loses its representative role

**Prompt shape:** A released project describes an optional helper and a technically successful generic demo as a serious product advance. The owner says the demo is unintelligible and unrelated to what the product should help people accomplish, and asks for the product to be made right.

**Reject the candidate if:** it only apologizes or edits release wording, deletes independently useful maintenance, keeps the demo as a current positive case, proposes another arbitrary showcase, or stops at a correction plan without replacing the missing product behavior.

**Expected:** Shape identifies the agent-added interpretation that made the side artifact representative, retires that interpretation and its active descendants, preserves useful helper work at maintenance scope, and returns to the accepted product outcome. The same authorized commission implements and validates a replacement capability that changes what a user can accomplish. Historical evidence stays truthful about the rejected case.

## What a pass establishes

Keep deterministic helper tests, retrieval observations, method use, and complete task outcomes separate. A fixed-source payload check says nothing about recall quality; a source-discovery test says nothing about causal method benefit. A fresh task can show that a Skill was discovered and used and that its output meets the case; broader superiority needs a separate appropriately scoped comparison.
