# Soundings

[简体中文](README.zh-CN.md)

> Version `0.1.0` is an early dogfood candidate. Its package and Skills are implemented; source validation, public installation, and fresh-session behavior are reported separately below.

Soundings is a small Codex skillset for finding what would make uncertain work better understood next—without turning every task into a research program, requirements interview, or mandatory workflow.

The name comes from taking soundings: making deliberate measurements and probes to learn the depth and shape of something that cannot yet be seen clearly. The plural matters. Soundings is not one central brain or a fixed process; it provides two independently discoverable capabilities that return control to the work already in progress.

| Skill | Responsibility | It should yield when |
| --- | --- | --- |
| `search` | Look outward for decision-changing facts, options, mechanisms, references, and adjacent possibilities; bring the result back to the active work. | Local context is sufficient, the task is a clear small change, or a specialized method can proceed without an external unknown. |
| `shape` | Make an incomplete or unstable direction judgeable by exposing consequential assumptions and producing the right recommendation, scenario, comparison, output, probe, or owner question. | The next meaningful action is supported and no unowned product or value choice blocks it. |

They are capabilities, not stages. Soundings deliberately has no top-level router and no `Search → Shape → Spec → Build` pipeline.

## Install

Install the public marketplace and plugin:

```bash
codex plugin marketplace add IndelibleVivi/soundings
codex plugin add soundings@soundings
```

Start a new Codex task after installation so the host can discover the Skills. Source presence and a successful install do not activate a plugin inside a task that was already running.

To refresh the Git marketplace later:

```bash
codex plugin marketplace upgrade soundings
```

The exact installed-version update behavior will be documented after the first public upgrade is exercised; the command above refreshes the marketplace snapshot, not necessarily an already cached plugin copy.

## Use

Invoke a Skill explicitly when you already know which capability you want:

```text
$search Compare the options that could materially change this decision, then bring the evidence back to the current work.
```

```text
$shape Make the most consequential uncertainty in this direction judgeable, then continue as far as the existing authority allows.
```

Both Skills also allow implicit invocation. The intended behavior is selective: a fact-sensitive choice or unstable framing may trigger Soundings, while a clear typo fix should remain a direct edit.

## What changes in practice

- A fact-sensitive decision seeks evidence about the consequence people will actually encounter, not only a feature table.
- An open creative direction may receive an unexpected but transferable reference even when the user did not supply one.
- A high-impact interpretation introduced by the agent is made visible before it silently organizes large downstream work.
- A useful response advances only the choices it actually resolves; it does not become accidental whole-project approval.
- A correction updates dependent specifications, tasks, and implementation while preserving goals the correction did not reject.

Soundings does not replace engineering, design, legal, writing, or other domain methods. Those methods keep ownership of their complete outcomes. Soundings supplies outward exploration and problem shaping when the active work needs them, then returns control without creating a competing brief.

## Package layout

```text
.agents/plugins/marketplace.json
plugins/soundings/
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

The first version is instruction-only. It adds no MCP server, search backend, database, memory service, hooks, or fixed worker team. It uses tools already available to the host and never expands the authorization of the current task.

## Validate

From the repository root:

```bash
skill-validate plugins/soundings/skills/search
skill-validate plugins/soundings/skills/shape
~/.local/share/codex-skill-tooling/.venv/bin/python \
  ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py \
  plugins/soundings
```

Structural validators do not establish useful automatic triggering or judgment. Use the cases in [`plugins/soundings/docs/behavior-scenarios.md`](plugins/soundings/docs/behavior-scenarios.md) in fresh tasks, first with explicit invocation and then with ordinary prompts where implicit discovery matters.

See [`plugins/soundings/docs/design.md`](plugins/soundings/docs/design.md) for the architecture and boundary rationale.
See [`docs/dogfood-0.1.0.md`](docs/dogfood-0.1.0.md) for the bounded fresh-task evidence behind the status below.

## Status

- **Source:** `0.1.0` candidate present in this repository.
- **Validation:** both Skills and the plugin manifest pass their structural validators; the marketplace manifest resolves as `soundings`.
- **Installation:** the two public commands above installed `soundings@soundings` from the Git marketplace; it is enabled, and the installed cache matched the canonical plugin package.
- **Activation:** a fresh ephemeral Codex CLI task resolved Shape from the public-Git installation; the broader behavior matrix also resolved both Skills from the equivalent local candidate.
- **Behavior:** bounded dogfood passed explicit Search, explicit Shape, implicit Search, implicit Shape, and a clear-small-task non-trigger. This is not yet the complete scenario suite.
- **Publication:** [`IndelibleVivi/soundings`](https://github.com/IndelibleVivi/soundings) is public on `main`; visibility, remote commit, README access, and anonymous GitHub API access were read back after publication.

The dogfood host emitted a warning that aggregate Skill descriptions were shortened to fit its Skill-context budget. Every Skill remained visible, and the tested explicit and implicit invocations still resolved correctly; behavior under other heavily saturated plugin sets remains an environment-dependent limitation.

## Privacy, network, and authority

Soundings itself sends nothing to an external service and stores no memory. A Search run may use web, browser, repository, or connector tools already available to the host; their own network and data boundaries still apply. The Skills do not grant permission to install software, modify accounts, publish material, spend money, expose private data, or perform destructive actions.

## License

Soundings uses a path-scoped license model:

- the functional marketplace, plugin, Skills, and runtime references are licensed under the [Sustainable Use License 1.0](LICENSE) (`SUL-1.0`);
- the READMEs, project documentation, and diagrams are licensed under [CC BY-NC-SA 4.0](LICENSE-DOCUMENTATION.md).

See [`LICENSING.md`](LICENSING.md) for the exact path map. Third-party material, if added later, remains under its own terms and must be identified separately.
