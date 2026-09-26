# Inquiry repository contract

## Truth owners

- `.codex-plugin/plugin.json` owns plugin identity, version, discoverable components, and UI metadata.
- `skills/search/SKILL.md` and `skills/shape/SKILL.md` own runtime behavior and trigger boundaries.
- Skill-local `references/` hold conditional methods loaded by their owning Skill.
- `references/working-context.md` owns the shared state and handoff semantics.
- `docs/design.md` explains architecture and boundaries; `docs/behavior-scenarios.md` owns forward-test cases.
- `README.md` owns public status, package map, validation commands, and present limitations.

## Hard boundaries

- Keep Search and Shape independently discoverable. Do not add an Inquiry router or mandatory pipeline without an explicit product decision supported by observed behavior.
- Local repository inspection is context, not a Search deliverable by itself.
- Do not add MCP servers, hooks, search backends, databases, automatic memory, or worker infrastructure without evidence of a concrete capability gap and explicit scope.
- Skills never expand the current task's authorization.
- Keep private evaluations, raw task transcripts, personal preference archives, and continuity outside this repository.
- Do not add a public license until the owner chooses the exact license and scope.

## Verification

Run after Skill or manifest changes:

```bash
skill-validate skills/search
skill-validate skills/shape
python3 ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
```

Run `git diff --check` when the repository is under Git. Structural validation does not prove trigger quality; changes to behavior require the smallest relevant scenarios from `docs/behavior-scenarios.md` in a fresh session.

## Documentation triggers

- Update `README.md` when capabilities, package layout, installation status, validation commands, or limitations change.
- Update `docs/design.md` when responsibilities, boundaries, shared state, or architecture change.
- Update `docs/behavior-scenarios.md` when an observed failure changes the acceptance behavior.
- Update this file when canonical paths, generated/source boundaries, verification, or write/install/release rules change.
