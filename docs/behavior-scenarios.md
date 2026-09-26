# Behavior scenarios

These scenarios test decisions, not exact wording. Run them in fresh Codex sessions against the installed candidate, first with explicit Skill invocation and then with ordinary prompts where implicit discovery matters. Preserve the raw output outside this repository when it contains private project context.

## 1. Clear small repair stays direct

**Prompt shape:** A user identifies a precise typo or a one-line local UI label change and asks to fix it.

**Reject the candidate if:** it starts external research, opens a product-shaping discussion, creates a brief, or asks for preferences unrelated to the exact change.

**Expected:** Inquiry yields; the active domain or engineering method completes the change directly.

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
