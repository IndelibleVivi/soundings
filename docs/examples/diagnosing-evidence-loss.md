# When evidence is available but does not reach the answer

**中文摘要：** 本例把“存过／找到了却用错”拆成可区分的故障位置。材料转换后的最终输入可能相同，失去区别的位置却不同；因此实验需要记录存储、返回与实际装配的相邻表示。它也展示如何把一个问题、来源及未决解释交给另一位研究助手，而不把研究助手的材料权限误当成被测系统的输入权限。

This is a worked research inquiry, not a memory-system benchmark. It combines a reproduced offline input audit, two bounded primary-source checks, and explicitly labeled inferences. The example does not add a universal memory schema or authorize system/provider execution.

## The commission

Explain how previously saved or retrieved material can still fail to influence a later answer correctly. Identify an experiment that distinguishes the failure locations, while preserving semantic retrieval as a useful candidate capability.

The useful question is narrower than “does the system remember?”: **at which observed boundary did the distinction required by the current task disappear, or cease to govern the result?**

## What the material establishes

Relata's public [RC-005 input audit](https://github.com/IndelibleVivi/Relata/blob/6685486a68e6e70b271668d026de4959aa11bbc6/experiments/continuity-input-audit.md) prepares a synthetic authorship case with two histories and three correlated checkpoints. The histories differ in who proposed and accepted a title. Re-running its canonical offline `continuity_inputs.py audit` gave:

| Literal projection | Equal inputs across the three contrast pairs |
| --- | ---: |
| Complete history | 0 / 3 |
| Speaker removed | 3 / 3 |
| Last two events | 2 / 3 |
| Last event or current request only | 3 / 3 |

These are literal input collisions in one development family. They are not three independent cases, reader scores, recall measurements, or proof that unequal inputs will be used correctly. The current case also distinguishes a newly imported old artifact from a new decision; import time alone cannot settle which title is current.

Two primary-source checks show why adjacent boundaries deserve inspection:

- At pinned Graphiti commit `16cdf704`, the [example agent's context conversion](https://github.com/getzep/graphiti/blob/16cdf7045378c8d53ae01f94e2fa60d238cb0f68/examples/langgraph-agent/agent.ipynb) joins `edge.fact` values. Structured edge information is not all automatically included by that conversion. This is one example caller's static path, not proof that every Graphiti application loses attribution, or that a fact string cannot express it.
- At pinned Letta Code commit `f5c5bbce`, [local memory compilation](https://github.com/letta-ai/letta-code/blob/f5c5bbce6e9394b30c626909315c2b3acc665672/src/backend/local/system-prompt-compilation.ts#L76-L115) reads committed Markdown from Git. A disk edit and the version selected for compilation are distinguishable states. This check does not execute a turn or establish how a model follows the compiled context.

The broader [Relata source studies](https://github.com/IndelibleVivi/Relata/blob/6685486a68e6e70b271668d026de4959aa11bbc6/systems/source-studies/README.md) supply useful hypotheses about retrieval paths, corrections, and compiled state. They remain generated research drafts based on pinned sources, not independent runtime replications of those sources.

## The new diagnostic inference

Consider the same raw history under two deliberately constructed transformations:

| Condition | Stored histories distinguish the worlds | Returned histories distinguish the worlds | Assembled contexts distinguish the worlds |
| --- | --- | --- | --- |
| Remove speaker before storage | No | No | No |
| Preserve speaker through return, remove it during assembly | Yes | Yes | No |

The final assembled contexts are identical across these two loss locations. Comparing only final contexts or answers cannot locate the loss. Keeping the intermediate representations can. This was checked as a literal transformation over the public inputs; no retrieval engine or model reader was run.

That finding suggests a diagnostic comparison: hold the selected evidence set fixed, capture the returned objects and the actual context handed to the reader, then compare the existing assembly with a relation-preserving assembly. Keep raw-history exposure as a separate control. The added representation may need speaker, source, relevant time, or adoption context depending on the question; the experiment should not require a universal field inventory.

If the deciding distinction was already absent before retrieval, changing assembly alone cannot restore it. If it survives assembly and the answer still misuses it, the assembly-loss explanation is insufficient and the reader/use boundary needs investigation. If the supposed distinction was never justified by the case, input engineering cannot repair case validity. These observations can reject the preferred explanation rather than merely decorate it.

## What a corpus service could contribute

Corpus search could help discover mechanisms without knowing a project name or exact terminology. It cannot infer a distinction removed from the indexed material, certify the validity of a case, or prove that a later reader uses retrieved evidence correctly.

Cloudflare's current [AI Search interface](https://developers.cloudflare.com/ai-search/api/search/workers-binding/) documents keyword, vector and hybrid retrieval, filtering and surrounding-chunk expansion. Its [metadata constraints](https://developers.cloudflare.com/ai-search/configuration/indexing/metadata/) reinforce a composition choice: use metadata for selection and keep full provenance in a rereadable source. These are documentation checks, not a live Cloudflare comparison or a reason to upload a private corpus. An informative future comparison would use unknown-name mechanism queries, exact phrases, paraphrases, stale derivatives, missing qualifications, and no-supported-answer questions while inspecting the deciding source passages.

## Hand off the inquiry without losing it

A selected packet for this inquiry contains a brief, research views of the public synthetic inputs, bounded source-study drafts labeled `generated`, and explicitly acquired primary-source text. The raw conversation log and private project continuity are excluded. The recipient uses the packet's copied `evidence` directory rather than an original store.

The commission asks for competing explanations, an experiment and counterevidence, with readable source locators and actual read coverage. It does not provide the expected answer as a research conclusion. A researcher may compare both histories; a tested memory system must receive only its assigned history and checkpoint. Packet portability is not experimental isolation or transfer permission.

Use [the portable packet method](../../plugins/soundings/skills/search/references/research-handoffs.md) when this selection needs to travel. Whether the receiver actually read, understood and usefully continued the inquiry belongs in the [versioned behavior evidence](../dogfood-0.3.0.md), separate from deterministic copying tests.

## What stays open

The next useful observation is the earliest available boundary where a real configured system loses or misuses the required distinction. The current evidence does not rank systems, accept the candidate case, or establish semantic retrieval quality. A different question may not need speaker identity at all, and a source string can carry relationships without dedicated metadata fields.

Keep this question and its evidence dependencies in the existing project record. Reopen the assembly hypothesis if actual returned objects and assembled context differ consequentially; reopen the reader hypothesis if the necessary material demonstrably reaches the reader. That residue is more useful than preserving every search step.
