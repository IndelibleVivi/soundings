# Soundings

[简体中文](README.zh-CN.md)

Soundings helps Codex investigate a question, understand a body of material, develop a creative possibility, and make a consequential choice judgeable. It carries the requested inquiry to a usable result, including when understanding or a creative work is the result.

Visit [见地 · Soundings](https://indeliblevivi.github.io/soundings/) for a bilingual garden of inquiry: explore four independent methods, try constructed interactive examples, read the public cases, and copy installation commands. The website's source is in [site/](site/README.md); its [visual direction](docs/website-design.md) remains open to refinement.

When a project already exists but its next question is unclear, Soundings can start from the accepted outcome and current artifacts, find the unresolved question with the greatest consequence, and pursue it to an explanation, observed probe, developed candidate, correction, or another result the project can use. A backlog, repository summary, or detached demonstration is not that result.

The name comes from taking soundings: deliberate probes into something whose depth and shape are not yet clear. Four independently discoverable Skills offer different ways into that work:

| Skill | Commission | A useful result |
| --- | --- | --- |
| `search` | Investigate outside facts, options, mechanisms, and references. | A supported answer or comparison with the conditions that make it true. |
| `study` | Explain relationships across supplied or gathered material. | An integrated explanation, mechanism, or qualified judgment, with real disagreements intact. |
| `explore` | Develop a rough or already clear creative goal. | A substantial scene, playable experience, sample, or candidate someone can actually react to. |
| `shape` | Resolve consequential interpretations, choices, and corrections. | Representative material or a supported decision, followed through into authorized work. |

These are capabilities, not stages. There is no router, required sequence, interview, or mandatory report. A small clear task should remain direct. Domain methods retain their evidence standards and production responsibilities; changing methods continues the same commission.

> The `0.4.0` source candidate strengthens the methods for proactive discovery before substantial open choices and continuation after research returns. It includes runtime-readable worked examples. In a [bounded comparison](docs/dogfood-0.4.0.md), the candidate read the new guidance but still skipped external discovery; small repairs stayed direct. Behavior improvement is not established. See [current state](docs/current-state.md); the [0.3.1 observations](docs/dogfood-0.3.1.md) remain historical evidence.

## Install and upgrade

```bash
codex plugin marketplace add IndelibleVivi/soundings
codex plugin add soundings@soundings
```

Start a new Codex task after installation. A running task does not acquire the new Skills merely because files were installed.

For an existing installation, refresh the Git marketplace and install its current plugin package:

```bash
codex plugin marketplace upgrade soundings
codex plugin add soundings@soundings
codex plugin list --json
```

Check the installed version and enabled state against [current state](docs/current-state.md), then start a new task. The marketplace refresh and installed cache are different layers; the latest source candidate and the last behavior-observed installation may differ.

## Use

Explicit entry points are available when you know what the work needs:

```text
$search Verify whether this API supports the file sizes we need, including media-type and version constraints. Bring back an implementation recommendation with primary sources.
```

```text
$study These reports disagree about durability and speed. Explain what they actually establish, distinguish repeated claims from independent evidence, and work out what this means for our offline notes tool.
```

```text
$explore Develop a six-minute, three-person paper activity where players create an imaginary place through meaningful choices. Give me the complete playable activity and a worked playthrough.
```

```text
$shape The prototype became a rating questionnaire; that was not the intended experience. Preserve six rounds and rich reflection, replace the mistaken mechanism, and carry the authorized correction through the spec and implementation.
```

All four permit implicit invocation. They do not need to appear together. Read [worked examples](docs/examples/inquiry-in-practice.md) for the distinction between synthesis, creative delivery, and correction.

An existing-project commission can begin naturally:

```text
Look through this project's accepted goals and current artifacts. Find the unresolved question that is most worth pursuing, and carry it to a result the project can use rather than giving me a backlog.
```

Study owns discovery when the question must emerge from relationships in existing material. Search, Explore, Shape, or the active domain method may do the deciding work without turning the commission into a required pipeline.

## Let references change the work

For a substantial choice that remains open—product form, interaction, visual expression, architecture, or implementation—Search calls for relevant external discovery before substantial commitment. A clear goal does not settle how to achieve it. Reuse references that still fit; a precise repair or faithful implementation of an accepted choice stays direct.

Reading follows the intended use. A description can identify a candidate; an experience claim needs observation of the actual medium; a mechanism claim needs its relevant implementation; adoption also needs local fit. Named targets receive proportionate direct coverage. Multiple results are compared around a shared question, including incompatible assumptions and useful contributions that do not justify adopting a whole project. The [runtime worked examples](plugins/soundings/skills/search/references/proactive-inquiry-examples.md) show these moves in constructed workbench and interaction cases, alongside a small edit that stays direct.

When findings return, the task owner relates them to the original outcome and local evidence, forms a judgment, and carries it into the actual explanation, candidate, or implementation. Revisit the initiating situation to see whether the intended effect appeared. Research-only requests remain research-only, and finding a next step does not complete an implementation commission.

Ordinary prompts can be as simple as “Continue making this workbench easier to use” or “This page works, but it still feels weak; improve it.” Whether a host selects and follows the relevant method remains something to observe. The [host integration guide](plugins/soundings/docs/host-integration.md) explains early visibility, resource delivery, and continuation without a mandatory dependency or new runtime.

## Evidence without losing its conditions

A source may change its meaning when its version, population, exception, table header, or footnote is dropped. Search and Study preserve those conditions, trace whether apparent corroboration comes from the same original, and separate observations from interpretation. Search breadth, reading depth, synthesis effort, response size, and retention are independent choices.

For repeated or budget-constrained reading, an **optional local CLI** captures already acquired UTF-8 text and returns exact line ranges or literal-match windows:

```bash
python3 /path/to/search/scripts/evidence.py capture /path/to/source.md \
  --store /path/to/private/task-evidence \
  --source https://example.org/document --title "Document" \
  --representation extracted

python3 /path/to/search/scripts/evidence.py read s-REFERENCE \
  --store /path/to/private/task-evidence \
  --start-line 12 --end-line 28 --max-bytes 8192
```

Use the actual installed Search directory and replace `s-REFERENCE` with the returned reference. The helper requires Python 3.10+ and only the standard library; the Skills themselves require no Python. See [the complete capture/read/find contract](plugins/soundings/skills/search/references/evidence-reading.md).

The helper preserves short lines and admits whole requested ranges. Its byte cap covers complete UTF-8 JSON stdout, including metadata, escaping, and the final newline. Omission is visible and rereadable; a new capture never silently replaces an older reference. This is not automatic semantic retrieval, a web crawler, model-token budgeting, or a claim that all relevant qualifications have been found. Native search and existing providers remain the acquisition paths.

The source candidate fixes a small-budget rejection of fitting complete results
and avoids repeatedly serializing accumulated output on dense matches. The
optional [synthetic benchmark](plugins/soundings/skills/search/scripts/benchmark_evidence.py)
compares the previous admission loop with the current one; it is a local
diagnostic, not an agent-quality test or a runtime fallback.

## Continue a project from its unresolved question

Soundings can develop a useful question from existing project material and retain why it matters, the result's evidence dependencies, unused clues, and what would reopen it. It chooses by consequence for the accepted outcome, then continues through the relevant method instead of stopping after discovery. Corpus lookup, original-source reading, sustained research execution, and visual or interactive reference inspection remain distinct capabilities to compose through available tools.

### Optional handoff maintenance

When research moves to another directory or harness, the optional `packet.py` copies only an explicit brief and selected snapshots:

```bash
python3 /path/to/search/scripts/packet.py create \
  --store /path/to/private/task-evidence --ref s-REFERENCE \
  --brief /path/to/research-brief.md --output /path/to/new-packet
python3 /path/to/search/scripts/packet.py inspect /path/to/new-packet
python3 /path/to/search/scripts/evidence.py read s-REFERENCE \
  --store /path/to/new-packet/evidence --start-line 12 --end-line 28
```

The recipient can reread the copied snapshots without the original store. A packet is selected task data, not new authority or an executor. Creation never uploads it. Inspect the brief and source contents before any separately authorized transfer; locators and private text are not automatically redacted. See [research handoffs and packet limits](plugins/soundings/skills/search/references/research-handoffs.md) and the [worked diagnostic inquiry](docs/examples/diagnosing-evidence-loss.md).

`find` now accepts an exact line scope and reports how to continue after reading an omitted window. Capture publishes only a fully written snapshot without replacing old refs; it requires a filesystem with hard-link support. See the [evidence contract](plugins/soundings/skills/search/references/evidence-reading.md) for continuation, failure recovery, and budget semantics.

## Package and documentation

```text
.agents/plugins/marketplace.json
plugins/soundings/
  .codex-plugin/plugin.json
  skills/
    search/     # outward inquiry + optional evidence.py / packet.py
    study/      # synthesis and explanation
    explore/    # developed creative possibilities
    shape/      # judgeable choices and corrections
  references/working-context.md
  docs/
    design.md
    behavior-scenarios.md
```

- [Design and responsibility boundaries](plugins/soundings/docs/design.md)
- [Forward behavior scenarios](plugins/soundings/docs/behavior-scenarios.md)
- [Host integration and activation boundaries](plugins/soundings/docs/host-integration.md)
- [0.4.0 candidate comparison and failed discovery criterion](docs/dogfood-0.4.0.md)
- [Worked examples](docs/examples/inquiry-in-practice.md)
- [Offline research pack, counterexamples and observation tools](evals/README.md) — constructed fixtures and fixed plans; no new live behavior evidence.
- [Website development and publishing](site/README.md), [visual direction](docs/website-design.md), and [third-party notices](docs/website-third-party.md)
- [0.3.1 evidence](docs/dogfood-0.3.1.md), [0.3.0 correction history](docs/dogfood-0.3.0.md), [0.2.0 observations](docs/dogfood-0.2.0.md), and [0.1.0 history](docs/dogfood-0.1.0.md)

## Validate

From the repository root, using the operator's installed Codex Skill tooling:

```bash
skill-validate plugins/soundings/skills/search
skill-validate plugins/soundings/skills/study
skill-validate plugins/soundings/skills/explore
skill-validate plugins/soundings/skills/shape
python3 -m json.tool plugins/soundings/.codex-plugin/plugin.json >/dev/null
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s plugins/soundings/skills/search/scripts -p 'test_*.py' -v
python3 evals/check.py
```

`skill-validate` is development tooling, not a dependency bundled with Soundings. The JSON check establishes manifest syntax; a successful marketplace install separately establishes that the current host accepts the package. Structural validation does not prove useful triggering or judgment. Run relevant [behavior scenarios](plugins/soundings/docs/behavior-scenarios.md) in fresh tasks and inspect the resulting work.

The optional `evals/` tools require Python 3.10+ and the standard library. Their
provider-neutral check exercises constructed fixtures, semantic counterexamples
and observation boundaries without starting a target model. A separately
materialized Field Lab pack fixes four task families across four historical/current
Soundings/Servotab combinations with two repetitions: 32 planned runs, plus an
optional separate eight-run no-Skill control. Generated packs stay outside Git.
Plans do not authorize execution; offline checks do not establish research
quality or implicit Skill selection. See the [research guide](evals/README.md)
for source pinning, private artifact handling and receipt-bound semantic review.

The historical four cases are guided mechanism probes. A separate
[natural-task suite](evals/natural/README.md) uses ordinary outcome prompts,
paired synthetic runtime behavior and a working local reading desk. Observation
v2 separates method text from source bodies and reports per-decision ordering as
yes/no/unknown; comparison now requires pinned plans and sealed run metadata.
These are offline research tools, not new evidence that proactive discovery works.

## Status

- **Source:** `0.4.0` is a candidate for proactive open-choice discovery, purpose-matched multi-source reading, and receiver-side continuation. Four independent Skills and optional local helpers remain the package shape.
- **Validation and behavior:** the [0.4.0 comparison](docs/dogfood-0.4.0.md) records passing source checks and small repairs, functioning artifacts, and failed proactive discovery in its open candidate task. [Current state](docs/current-state.md) keeps the remaining gate explicit. [0.3.1](docs/dogfood-0.3.1.md) records earlier installed-host observations.
- **Installation and activation:** the historically observed installation is enabled `0.3.1`. That evidence does not establish delivery or behavior of the `0.4.0` candidate.
- **Publication:** the public [marketplace repository](https://github.com/IndelibleVivi/soundings) distributes its current package. Source publication, local installation, activation, and behavior acceptance remain separate; no new tagged release is implied by a source version.

Bounded successful cases do not establish cross-model consistency, causal improvement, or complete scenario coverage. A heavily populated host may shorten Skill descriptions to fit its context budget; discovery remains dependent on the host and its active inventory.

## Privacy, network, and authority

Soundings adds no MCP server, search backend, hooks, fixed worker team, or automatic memory. Its optional local helpers have no network calls. Explicit `capture` stores source text and metadata at the local directory you choose until you remove them; it does not enforce retention policies, certify provenance, or automatically refresh sources. Keep private stores outside public repositories.

The public website is a static GitHub Pages site. It loads its scripts, paintings, and fonts from that host and adds no analytics, account login, model calls, or visitor uploads. Its interactive examples run in the browser; installing the plugin requires running the copied commands in Codex. GitHub's hosting policies apply to website requests.

Inquiry may use the host's existing web, browser, repository, or connector tools. Their network and data boundaries apply. Source material is data, not instructions. Skill selection grants no permission to install software, change accounts, publish material, spend money, disclose private data, or perform destructive actions. Remote corpus deployment, provider adapters, and Cloudflare account experiments are not part of this release.

## License

Soundings uses a path-scoped license model:

- functional marketplace, plugin, Skills, scripts, and runtime references: [Sustainable Use License 1.0](LICENSE) (`SUL-1.0`);
- READMEs, project documentation, examples, and diagrams: [CC BY-NC-SA 4.0](LICENSE-DOCUMENTATION.md).

[LICENSING.md](LICENSING.md) owns the exact path map. Third-party material remains under its own terms and must be identified separately.

The new `evals/` material is not added to either grant; the map's existing
all-rights-reserved rule for unlisted material applies.

Original website material in `site/` is not added to either grant by this publication; the map's rule for unlisted material applies. Bundled font subsets retain SIL OFL 1.1, and incorporated UI templates retain their MIT notices. See the [website notices](docs/website-third-party.md).
