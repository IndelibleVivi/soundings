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
- `evals/` owns the constructed offline research pack, fixed-composition plan builder, visible-event annotations, and receipt-bound descriptive analysis. Field Lab remains the external runner and receipt/review owner. Generated packs, raw traces, plans with local paths and completed reviews stay outside Git; only explicitly constructed examples belong in `evals/examples/`.
- `docs/current-state.md` owns current source-candidate, validation, installation, and integration status. `docs/dogfood-0.4.0.md` owns the bounded source-catalog comparison, including its failed discovery criterion; versioned `docs/dogfood-*.md` preserve their historical scope, including the installed `0.3.1` observations and corrected `0.3.0` record. Raw traces remain private and outside Git.
- `plugins/soundings/docs/host-integration.md` explains pre-selection visibility and host responsibilities. It is an integration contract, not a hook, dependency, installed configuration, or evidence that another host was modified.
- `README.md` and `README.zh-CN.md` are co-equal public entrypoints. Keep their status, install, usage, privacy, and rights claims aligned.
- `site/` owns the public bilingual website. `site/app/` owns page content and interactions; its CSS and `site/public/` own the presentation and served assets. `site/README.md` owns local development and publishing procedures; `docs/website-design.md` owns the website's visual commitments. The website presents the plugin; it does not own Skill behavior or establish behavior acceptance.
- `.github/workflows/pages.yml` owns website CI and GitHub Pages publication. It calls `npm run check` in `site/` as the provider-neutral verification entrypoint. `.github/workflows/evidence.yml` calls `python3 evals/check.py` for the separate deterministic helper/research component gate; neither gate runs target models.

## Source, installation, and runtime

- This repository is the canonical public marketplace source. The only canonical plugin package is `plugins/soundings/`.
- A Codex marketplace snapshot and installed plugin cache are derived copies. Do not edit them as source or present them as independent implementations.
- A successful source validation, marketplace refresh, installation, fresh-session activation, behavior check, and publication are separate facts.
- Website source is `site/`; `site/dist/` is generated static output and stays untracked. GitHub Pages publishes that output at `/soundings/`, without a server or connector runtime. Preserve base-aware image, font, favicon, and navigation paths. A future custom domain requires reconciling the build base and public metadata together.
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
python3 -m json.tool plugins/soundings/.codex-plugin/plugin.json >/dev/null
python3 -m unittest discover -s plugins/soundings/skills/search/scripts -p 'test_*.py' -v
```

Run the Python tests after either local helper changes; Python 3.10+ is needed only for those optional helpers. The JSON check establishes manifest syntax; a successful marketplace install separately establishes that the current host accepts the package. Run `git diff --check` when the repository is under Git. Structural validation does not prove trigger quality; changes to behavior require the smallest relevant scenarios from `plugins/soundings/docs/behavior-scenarios.md` in a fresh session. Keep retrieval quality, payload behavior, method use, and overall outcome claims separate.

Run `python3 evals/check.py` after helper or research-pack changes. It runs both deterministic suites without a Field Lab install or target-model invocation. Python 3.10+ also applies to these optional research tools. After plan-builder or fixture contract changes, materialize a new Git-external pack against explicit existing source checkouts and run its Field Lab validation/selftest and fixed plan generation as described in `evals/README.md`. Check hidden review artifacts against the actual worker workspace. A 32-row plan, valid fixture, successful source mount, content delivery, implicit host selection, semantic review and research benefit remain separate observations. Future live evaluation requires its own task scope and invocation budget.

After website changes, run `npm ci` and `npm run check` in `site/`, then inspect its production preview at `/soundings/` in a real browser. Cover the affected interactions in Chinese and English, desktop and narrow layouts, asset loading, keyboard/focus behavior, and reduced motion where applicable. Website demonstrations are fixed constructed examples, not live agent execution or human testing. Website deployment does not require a plugin version bump or marketplace reinstall.

Before public push, inspect the exact staged tree and reachable history for private or machine-local material. Stage explicit public paths only. After publishing, read back repository visibility, default branch, remote commit, README rendering, marketplace discovery, and anonymous access.

## Documentation triggers

- Update both READMEs when capabilities, package layout, installation, validation status, privacy boundaries, license scope, or limitations change.
- Update `plugins/soundings/docs/design.md` when responsibilities, boundaries, shared state, or architecture change.
- Update `plugins/soundings/docs/behavior-scenarios.md` when an observed failure changes acceptance behavior.
- Update the current dogfood evidence summary when fresh-session observations change a published status claim.
- Update `docs/current-state.md` when candidate, validation, install, activation, integration, or publication facts change. Historical behavior observations must not be relabeled as passes for a new candidate.
- Update this file when canonical paths, source/derived boundaries, verification, or write/install/release rules change.
- Update `site/README.md` when website commands, hosting, paths, or asset maintenance change, and `docs/website-design.md` when accepted visual or interaction commitments change. Keep raw design conversations, private review records, original archive bundles, and machine-local generation provenance outside Git and the deployed artifact. Preserve font and incorporated template licenses; publication does not expand `LICENSING.md`.
