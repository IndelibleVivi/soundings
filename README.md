# Inquiry

> Working title. Version `0.1.0` is a source candidate: implemented and locally validated as a plugin package, with a limited explicit worker forward-test completed. It is not yet installed, activated, or behavior-tested for implicit discovery in a fresh Codex session.

Inquiry is a small Codex skillset for a recurring gap between “the task is clear enough to execute” and “we need a formal research or requirements process.” It helps the agent decide what would make the work better understood next, without forcing every task through a workflow.

The plugin has two independently discoverable Skills:

| Skill | Responsibility | It should yield when |
| --- | --- | --- |
| `search` | Look outward for decision-changing facts, options, mechanisms, references, and adjacent possibilities; bring the result back to the active work. | Local context is sufficient, the task is a clear small change, or a specialized method can proceed without an external unknown. |
| `shape` | Make an incomplete or unstable direction judgeable by exposing consequential assumptions and producing the right recommendation, scenario, comparison, output, probe, or owner question. | The next meaningful action is supported and no unowned product or value choice blocks it. |

They are capabilities, not stages. Inquiry deliberately has no top-level router and no `Search → Shape → Spec → Build` pipeline.

## What changes in practice

- A fact-sensitive decision gets evidence about the consequence people will actually encounter, not only a feature table.
- An open creative direction may receive an unexpected but relevant reference even when the user did not supply one.
- A high-impact interpretation introduced by the agent is made visible before it silently organizes large downstream work.
- A useful response advances only the choices it actually resolves; it does not become accidental whole-project approval.
- A correction updates dependent specifications, tasks, and implementation while preserving goals the correction did not reject.

Inquiry does not replace engineering, frontend/design, legal, writing, or other domain methods. Those methods keep ownership of their complete outcomes. Inquiry supplies deeper outward exploration and problem shaping when the active work needs them, then returns control without creating a competing brief.

## Package layout

```text
.codex-plugin/plugin.json
skills/
  search/
    SKILL.md
    references/
  shape/
    SKILL.md
    references/
references/
  working-context.md
docs/
  design.md
  behavior-scenarios.md
```

The first version is instruction-only. It adds no MCP server, search backend, database, memory service, hooks, or fixed worker team. It uses the host's available tools under the authorization of the current task.

## Validate the source candidate

From the repository root:

```bash
skill-validate skills/search
skill-validate skills/shape
python3 ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
```

The structural validators do not establish that automatic triggering or behavioral judgment works. Use the scenarios in [`docs/behavior-scenarios.md`](docs/behavior-scenarios.md) in fresh sessions before describing the plugin as behavior-validated.

## Status boundaries

- **Source:** candidate implementation present in this repository.
- **Validation:** structural checks may verify package and Skill metadata.
- **Forward use:** a limited explicit read-only worker exercise covers non-triggering, evidence-to-choice, and high-impact assumption behavior; it is not an implicit host-discovery test.
- **Installation / activation:** not implied by source or validation.
- **Behavior:** requires fresh-session use with both explicit and implicit invocation.
- **Publication:** not authorized or configured by this repository.

No public license has been selected. Repository visibility, if it changes later, should not be treated as a grant of reuse rights.
