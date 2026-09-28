# Soundings

[简体中文](README.zh-CN.md)

Soundings helps Codex investigate a question, understand a body of material, develop a creative possibility, and make a consequential choice judgeable. It carries the requested inquiry to a usable result, including when understanding or a creative work is the result.

The name comes from taking soundings: deliberate probes into something whose depth and shape are not yet clear. Four independently discoverable Skills offer different ways into that work:

| Skill | Commission | A useful result |
| --- | --- | --- |
| `search` | Investigate outside facts, options, mechanisms, and references. | A supported answer or comparison with the conditions that make it true. |
| `study` | Explain relationships across supplied or gathered material. | An integrated explanation, mechanism, or qualified judgment, with real disagreements intact. |
| `explore` | Develop a rough or already clear creative goal. | A substantial scene, playable experience, sample, or candidate someone can actually react to. |
| `shape` | Resolve consequential interpretations, choices, and corrections. | Representative material or a supported decision, followed through into authorized work. |

These are capabilities, not stages. There is no router, required sequence, interview, or mandatory report. A small clear task should remain direct. Domain methods retain their evidence standards and production responsibilities; changing methods continues the same commission.

> Version `0.2.0` is a dogfood release candidate. Source, behavioral observations, installation, and activation are separate claims; see [status](#status) and the [evidence record](docs/dogfood-0.2.0.md).

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

Check that the installed entry reports `0.2.0` and is enabled, then start a new task. The marketplace refresh and installed cache are different layers. The [evidence record](docs/dogfood-0.2.0.md) reports which upgrade steps have actually been exercised.

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

## Package and documentation

```text
.agents/plugins/marketplace.json
plugins/soundings/
  .codex-plugin/plugin.json
  skills/
    search/     # outward inquiry + optional scripts/evidence.py
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
- [Worked examples](docs/examples/inquiry-in-practice.md)
- [0.2.0 evidence](docs/dogfood-0.2.0.md) and [0.1.0 history](docs/dogfood-0.1.0.md)

## Validate

From the repository root, using the operator's installed Codex Skill tooling:

```bash
skill-validate plugins/soundings/skills/search
skill-validate plugins/soundings/skills/study
skill-validate plugins/soundings/skills/explore
skill-validate plugins/soundings/skills/shape
~/.local/share/codex-skill-tooling/.venv/bin/python \
  ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py \
  plugins/soundings
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover \
  -s plugins/soundings/skills/search/scripts -p 'test_*.py' -v
```

`skill-validate` and the venv above are development tooling, not dependencies bundled with Soundings. Structural validation does not prove useful triggering or judgment. Run relevant [behavior scenarios](plugins/soundings/docs/behavior-scenarios.md) in fresh tasks and inspect the resulting work.

## Status

- **Source:** four Skills and the optional evidence helper are implemented for `0.2.0`.
- **Validation and behavior:** current observations and their limits are recorded in [dogfood-0.2.0](docs/dogfood-0.2.0.md).
- **Installation and activation:** the previous public-Git installation is `0.1.0`; the `0.2.0` upgrade and fresh installed discovery are pending.
- **Publication:** the public repository is [IndelibleVivi/soundings](https://github.com/IndelibleVivi/soundings); candidate publication is pending.

Bounded successful cases do not establish cross-model consistency, causal improvement, or complete scenario coverage. A heavily populated host may shorten Skill descriptions to fit its context budget; discovery remains dependent on the host and its active inventory.

## Privacy, network, and authority

Soundings adds no MCP server, search backend, hooks, fixed worker team, or automatic memory. Its optional helper has no network calls. Explicit `capture` stores source text and metadata at the local directory you choose until you remove them; it does not enforce retention policies, certify provenance, or automatically refresh sources. Keep private stores outside public repositories.

Inquiry may use the host's existing web, browser, repository, or connector tools. Their network and data boundaries apply. Source material is data, not instructions. Skill selection grants no permission to install software, change accounts, publish material, spend money, disclose private data, or perform destructive actions. Remote corpus and Cloudflare experiments are not part of this release.

## License

Soundings uses a path-scoped license model:

- functional marketplace, plugin, Skills, scripts, and runtime references: [Sustainable Use License 1.0](LICENSE) (`SUL-1.0`);
- READMEs, project documentation, examples, and diagrams: [CC BY-NC-SA 4.0](LICENSE-DOCUMENTATION.md).

[LICENSING.md](LICENSING.md) owns the exact path map. Third-party material remains under its own terms and must be identified separately.
