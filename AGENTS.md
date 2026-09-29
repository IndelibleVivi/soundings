# Soundings repository contract

## Truth owners

- `.agents/plugins/marketplace.json` owns the public marketplace identity and the route to the plugin package.
- `plugins/soundings/.codex-plugin/plugin.json` owns plugin identity, version, discoverable components, publisher metadata, and UI metadata.
- `plugins/soundings/skills/{search,study,explore,shape}/SKILL.md` own runtime behavior and trigger boundaries.
- Skill-local `references/` hold conditional methods loaded by their owning Skill.
- `plugins/soundings/references/working-context.md` owns shared state and handoff semantics.
- `plugins/soundings/docs/design.md` explains architecture and boundaries; `plugins/soundings/docs/behavior-scenarios.md` owns forward-test cases.
- `plugins/soundings/skills/search/scripts/evidence.py` owns the optional local snapshot CLI; its adjacent tests own deterministic behavior checks. It is source, not a generated provider adapter or a network service.
- `plugins/soundings/skills/search/scripts/packet.py` owns optional local packaging and inspection of an explicit brief and selected evidence snapshots. It composes the evidence helper; it is not a worker runtime, uploader, or new project authority.
- `docs/dogfood-0.3.0.md` owns current bounded evidence; earlier `docs/dogfood-*.md` preserve historical observations. Raw traces remain private and outside Git.
- `README.md` and `README.zh-CN.md` are co-equal public entrypoints. Keep their status, install, usage, privacy, and rights claims aligned.

## Source, installation, and runtime

- This repository is the canonical public marketplace source. The only canonical plugin package is `plugins/soundings/`.
- A Codex marketplace snapshot and installed plugin cache are derived copies. Do not edit them as source or present them as independent implementations.
- A successful source validation, marketplace refresh, installation, fresh-session activation, behavior check, and publication are separate facts.
- Do not keep local-path and Git marketplace registrations with the same marketplace name active at the same time.

## Hard boundaries

- Keep Search, Study, Explore, and Shape independently discoverable. Each can own a complete commission; stopping a query or intervention does not automatically complete that commission. Do not add a Soundings router or mandatory pipeline without an explicit product decision supported by observed behavior.
- Local repository inspection is context, not a Search deliverable by itself.
- Do not add MCP servers, hooks, search backends, databases, automatic memory, or worker infrastructure without evidence of a concrete capability gap and explicit scope.
- Skills never expand the current task's authorization.
- The evidence helper writes only explicitly captured local files to an explicitly selected store. Preserve exact snapshot rereading, representation labels, visible omissions, and full JSON byte accounting. It does not promise automatic semantic grouping, source freshness, universal token limits, or tamper-proof storage. Keep captures outside the public repository and respect the task's retention authority.
- Packet contents are task data, never execution authority. Preserve explicit selection, original snapshot refs and representation, relocation without the original store, and no automatic upload. Packet readability does not prove provenance or research acceptance.
- Keep private evaluations, raw task transcripts, personal preference archives, and continuity outside this repository.
- `LICENSING.md` owns the path-level rights map. Do not change its terms or scope without an explicit owner decision and a rights-boundary review.

## Verification

Run after Skill or manifest changes:

```bash
skill-validate plugins/soundings/skills/search
skill-validate plugins/soundings/skills/study
skill-validate plugins/soundings/skills/explore
skill-validate plugins/soundings/skills/shape
~/.local/share/codex-skill-tooling/.venv/bin/python \
  ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py \
  plugins/soundings
python3 -m unittest discover -s plugins/soundings/skills/search/scripts -p 'test_*.py' -v
```

Run the Python checks after either local helper changes; Python 3.10+ is needed only for those optional helpers. Run `git diff --check` when the repository is under Git. Structural validation does not prove trigger quality; changes to behavior require the smallest relevant scenarios from `plugins/soundings/docs/behavior-scenarios.md` in a fresh session. Keep retrieval quality, payload behavior, method use, and overall outcome claims separate.

Before public push, inspect the exact staged tree and reachable history for private or machine-local material. Stage explicit public paths only. After publishing, read back repository visibility, default branch, remote commit, README rendering, marketplace discovery, and anonymous access.

## Documentation triggers

- Update both READMEs when capabilities, package layout, installation, validation status, privacy boundaries, license scope, or limitations change.
- Update `plugins/soundings/docs/design.md` when responsibilities, boundaries, shared state, or architecture change.
- Update `plugins/soundings/docs/behavior-scenarios.md` when an observed failure changes acceptance behavior.
- Update the current dogfood evidence summary when fresh-session observations change a published status claim.
- Update this file when canonical paths, source/derived boundaries, verification, or write/install/release rules change.
