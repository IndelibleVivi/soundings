![Soundings — Find the question worth pursuing.](docs/visuals/banner.svg)

[简体中文](README.zh-CN.md) · **English**

# Soundings

**Research and creative inquiry for Codex.** Use it to check an outside fact, make sense of several sources, develop a creative idea, or work through a consequential choice. It can also start with an existing project and find a worthwhile question you have not yet narrowed down.

The result should be useful in the work itself: an explanation, a supported comparison, a concrete candidate, a correction, or an implementation already covered by your request. You do not have to turn every task into a research programme.

> **Early demo · runtime version 0.3.1.** The methods and product direction are still evolving. This documentation and visual study does not change the runtime or create a new release. Useful bounded cases exist; reliable implicit selection across projects and an improvement over the same host without Soundings have not been established. [Read the evidence and its limits](docs/dogfood-0.3.1.md).

## Start here

Install from the public Git marketplace:

```sh
codex plugin marketplace add IndelibleVivi/soundings
codex plugin add soundings@soundings
```

Start a **new Codex task** after installation. An existing task does not acquire the new instructions just because the package changed on disk.

Then ask normally, or name one of the four skills:

| What you need | Entry point | Example |
| --- | --- | --- |
| Outside facts or references | `$search` | Check whether this service supports our file size and format. Include the restrictions that affect the choice. |
| Understanding across material | `$study` | These reports disagree. Explain which differences are real and what the evidence means for this project. |
| A stronger creative candidate | `$explore` | Develop this activity into a complete playable version, with the actual material and a worked playthrough. |
| A consequential choice or correction | `$shape` | The prototype implements the wrong interpretation. Show the meaningful difference and carry the authorised correction through. |

These are **independent methods, not four stages**. Use one, combine a few, or let a small clear task proceed directly. A domain method still owns its professional evidence and implementation standards.

For an existing project, try:

```text
Read the project's goals and current work. Find one unresolved question worth
pursuing, explain why it matters, and carry it to a useful result within this
request. Do not stop at a repository summary or a feature backlog.
```

This is the intended project-inquiry behaviour, not a promise of reliable automatic activation. In the current Relata observations, ordinary prompts used specialised repository methods twice without selecting Study; explicit `$study` then produced a useful installed-skill result. [Exact observations](docs/dogfood-0.3.1.md).

## How it fits

![Responsibility map: the host reads independent Soundings methods, uses existing tools and delivers one task.](docs/visuals/01-responsibilities.svg)

Codex chooses and reads the needed instructions, uses its existing tools, and remains responsible for the result. Soundings does not start four agents or run its own scheduler. Goals, decisions, provisional ideas, evidence and current authority remain in the conversation or the project's existing records.

[Read the architecture](docs/architecture.md) for the responsibility map, local evidence flow, installation path, source anchors and editable Mermaid diagrams. The diagrams show the current demo, not a future hosted product.

## Evidence you can return to

Ordinary use needs no new storage. When a task calls for retained evidence, two optional **local Python 3.10+** helpers are available:

`evidence.py` captures a selected UTF-8 text file, then reads exact line ranges or finds literal matches. Old references keep their captured text. Responses report omitted ranges and cap the complete JSON stdout in bytes, not model tokens. A complete range is not the same thing as a complete source or a completed investigation.

`packet.py` copies an explicit brief and selected snapshots into a new directory. A recipient can inspect and reread that copy without the original store. It does not transfer the directory, run a worker or certify the sources.

[Capture, read and find](plugins/soundings/skills/search/references/evidence-reading.md) · [Portable handoffs](plugins/soundings/skills/search/references/research-handoffs.md). Python is required only for these optional helpers, not for the skills themselves.

## Upgrade an existing installation

```sh
codex plugin marketplace upgrade soundings
codex plugin add soundings@soundings
codex plugin list --json
```

Check the installed version and enabled state, then start a new task. Refreshing the marketplace, installing the package, discovering a skill and using it successfully are separate observations. These commands were exercised in the [0.3.1 record](docs/dogfood-0.3.1.md); host behaviour may change.

## What is here — and what is not

The package contains four skills, conditional reading references and the two optional helpers. It does not bundle a web-search backend, Cloudflare corpus, MCP server, model subscription, automatic memory or worker runtime. Search may use tools already available in the host. More capable integrations remain possible; they are not deployed features of this demo.

Instructions do not enlarge your authorisation. A research request does not silently grant permission to install services, spend money, publish work or upload source material. Local capture is an explicit retention action; keep private stores and packets outside public repositories. Source text is reference material, not an instruction to execute.

## Read further

[Architecture and source map](docs/architecture.md) · [Worked examples](docs/examples/inquiry-in-practice.md) · [Evidence-loss investigation](docs/examples/diagnosing-evidence-loss.md) · [Design rationale](plugins/soundings/docs/design.md) · [Behaviour scenarios](plugins/soundings/docs/behavior-scenarios.md) · [Visual system](docs/visuals/README.md)

Current evidence is in [0.3.1](docs/dogfood-0.3.1.md). Earlier [0.3.0](docs/dogfood-0.3.0.md), [0.2.0](docs/dogfood-0.2.0.md) and [0.1.0](docs/dogfood-0.1.0.md) records preserve their original scope and corrections; they are not fresh validation of today's package.

## Development checks

```sh
skill-validate plugins/soundings/skills/search
skill-validate plugins/soundings/skills/study
skill-validate plugins/soundings/skills/explore
skill-validate plugins/soundings/skills/shape
python3 -m json.tool plugins/soundings/.codex-plugin/plugin.json >/dev/null
python3 -m unittest discover -s plugins/soundings/skills/search/scripts -p 'test_*.py' -v
```

`skill-validate` is operator-installed tooling. JSON parsing proves syntax, not host compatibility. Tests check local helpers; relevant fresh-task scenarios check behaviour. [Repository contract](AGENTS.md).

## License

Functional plugin files, skills, scripts and runtime references use [SUL-1.0](LICENSE). READMEs, documentation and independent diagrams use [CC BY-NC-SA 4.0](LICENSE-DOCUMENTATION.md). See the existing [path-level licensing map](LICENSING.md); third-party material keeps its own terms and no trademark rights are granted.
