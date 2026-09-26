# Soundings repository contract

## Truth owners

- `.agents/plugins/marketplace.json` owns the public marketplace identity and the route to the plugin package.
- `plugins/soundings/.codex-plugin/plugin.json` owns plugin identity, version, discoverable components, publisher metadata, and UI metadata.
- `plugins/soundings/skills/search/SKILL.md` and `plugins/soundings/skills/shape/SKILL.md` own runtime behavior and trigger boundaries.
- Skill-local `references/` hold conditional methods loaded by their owning Skill.
- `plugins/soundings/references/working-context.md` owns shared state and handoff semantics.
- `plugins/soundings/docs/design.md` explains architecture and boundaries; `plugins/soundings/docs/behavior-scenarios.md` owns forward-test cases.
- `docs/dogfood-0.1.0.md` owns the public evidence summary for the current dogfood candidate. Raw traces remain private and outside Git.
- `README.md` and `README.zh-CN.md` are co-equal public entrypoints. Keep their status, install, usage, privacy, and rights claims aligned.

## Source, installation, and runtime

- This repository is the canonical public marketplace source. The only canonical plugin package is `plugins/soundings/`.
- A Codex marketplace snapshot and installed plugin cache are derived copies. Do not edit them as source or present them as independent implementations.
- A successful source validation, marketplace refresh, installation, fresh-session activation, behavior check, and publication are separate facts.
- Do not keep local-path and Git marketplace registrations with the same marketplace name active at the same time.

## Hard boundaries

- Keep Search and Shape independently discoverable. Do not add a Soundings router or mandatory pipeline without an explicit product decision supported by observed behavior.
- Local repository inspection is context, not a Search deliverable by itself.
- Do not add MCP servers, hooks, search backends, databases, automatic memory, or worker infrastructure without evidence of a concrete capability gap and explicit scope.
- Skills never expand the current task's authorization.
- Keep private evaluations, raw task transcripts, personal preference archives, and continuity outside this repository.
- `LICENSING.md` owns the path-level rights map. Do not change its terms or scope without an explicit owner decision and a rights-boundary review.

## Verification

Run after Skill or manifest changes:

```bash
skill-validate plugins/soundings/skills/search
skill-validate plugins/soundings/skills/shape
~/.local/share/codex-skill-tooling/.venv/bin/python \
  ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py \
  plugins/soundings
```

Run `git diff --check` when the repository is under Git. Structural validation does not prove trigger quality; changes to behavior require the smallest relevant scenarios from `plugins/soundings/docs/behavior-scenarios.md` in a fresh session.

Before public push, inspect the exact staged tree and reachable history for private or machine-local material. Stage explicit public paths only. After publishing, read back repository visibility, default branch, remote commit, README rendering, marketplace discovery, and anonymous access.

## Documentation triggers

- Update both READMEs when capabilities, package layout, installation, validation status, privacy boundaries, license scope, or limitations change.
- Update `plugins/soundings/docs/design.md` when responsibilities, boundaries, shared state, or architecture change.
- Update `plugins/soundings/docs/behavior-scenarios.md` when an observed failure changes acceptance behavior.
- Update the current dogfood evidence summary when fresh-session observations change a published status claim.
- Update this file when canonical paths, source/derived boundaries, verification, or write/install/release rules change.
