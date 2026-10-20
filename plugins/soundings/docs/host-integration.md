# Host integration

Soundings supplies methods. A host supplies discovery, readable resources, tools, permission enforcement, and an opportunity to continue after tools or workers return. This guide describes an integration contract; the plugin does not install a hook, edit another Skill, or configure a harness.

## Before a Skill is selected

The four descriptions are the first discovery surface. Put the important use case early and keep the entries independently selectable. Codex initially exposes metadata and reads the full Skill when selected; a crowded catalog can shorten descriptions or omit entries. A rule buried in an unselected body cannot be assumed to affect selection. See the [official Skill guide](https://learn.chatgpt.com/docs/build-skills).

For a host deliberately configured to use proactive inquiry, make the open-choice condition visible in its existing engineering or task guidance. A concise integration cue is:

> When a substantial product, interaction, visual, architecture, or implementation choice remains open, use Soundings Search's open-choice policy before committing substantial work. Reuse relevant, still-applicable references. After inquiry, keep responsibility for the original task and continue within its authorization. Settled small changes stay direct.

This is a host-side cue to the [canonical Search method](../skills/search/SKILL.md), not a fifth Skill or a new research stage. Keep the detailed policy there. A host that adopts the cue should reconcile it when that source changes, rather than maintaining another copy of the research method.

For Servotab, the useful integration points are its router's pre-implementation search guidance and its Design method's handling of open choices. Its incorporation and execution methods continue the same commission after findings return. In Servotab's source layout, the router body is generated from `scripts/build_skills.py`, and method bodies are owned by `methods/*.md`; edit those owners and regenerate, rather than patching an installed or generated Skill. Soundings has no required Servotab dependency.

## Deliver the method and continue the task

- Expose the selected package identity, readable Skill path, and supporting resources. Load conditional references when relevant instead of injecting every example into every task.
- Keep a useful record of what content actually entered the task. An enabled-plugin badge, an activation request, a file-path mention, and a successful content read establish different things.
- Provide the tools the work needs: source discovery, original-text reading, relevant code inspection, and observation of images, audio, sequences, or interactions where applicable. Report missing observation coverage rather than treating text extraction as an experience test.
- Keep the [shared working context](../references/working-context.md) available across method changes, worker returns, and context compression. Preserve the original outcome, accepted choices, provisional explanations, evidence, authority, and remaining work.
- Return tools and worker results to the owner of that commission and allow it to continue. The receiver must form the judgment and advance the work; scheduling another turn does not establish that the problem was solved.

The [Agent Skills integration guide](https://agentskills.io/client-implementation/adding-skills-support) describes file-based or tool-based activation, on-demand resources, and preservation and deduplication of active Skill content. These are possible host mechanisms, not components shipped by Soundings. Use the host's existing facilities before adding infrastructure.

## Diagnose the missing effect

| Observation | Next boundary to inspect |
| --- | --- |
| A relevant method was not visible or readable | Catalog, package version, paths, and resource access |
| It was visible but not selected at an open choice | Description and the active domain method's selection context |
| It was read but actions stayed superficial | The first missed observation, comparison, or development decision |
| Findings were useful but the original work stayed unchanged | Receiver judgment, local applicability, and translation into the actual object |
| The learned relationship reached the work but the effect did not appear | Problem explanation, production quality, and the original use scene |
| The task already succeeded without Soundings | Retain the successful path; invocation alone is not an improvement target |

Changing models or harnesses can change any of these boundaries. Keep the desired outcome and evidence standard stable while adjusting delivery only where observations justify it. No model-specific score, universal reminder density, or cross-model benefit is established by this guide.

## Verify an adopted integration

Use fresh tasks with the candidate package and ordinary prompts. Keep task inputs, model, tool access, and other relevant instructions comparable when comparing configurations. If selection is unclear, a separate explicit invocation can help diagnose delivery; it is not an implicit-discovery pass.

Inspect the resulting work before interpreting the loading trace. Check whether the agent independently found useful possibilities, read enough for its intended use, formed a local judgment, continued authorized work, and revisited the initiating situation. Include a settled small change to detect unnecessary research or questions. More links, more prose, or a longer run do not establish benefit.

The [behavior scenarios](behavior-scenarios.md) own acceptance cases. Live model runs, installation, external host edits, and publication require their applicable authority; this document grants none of them.
