# Soundings 0.1.0 dogfood evidence

This is a bounded public evidence summary for the `0.1.0` candidate. The raw CLI traces live outside the repository because host diagnostics and local paths are not public product documentation.

## Environment and scope

- Date: 2026-09-26
- Host: Codex CLI `0.147.0`
- Installation source: local marketplace candidate at the canonical checkout
- Installed plugin: `soundings@soundings`, version `0.1.0`, enabled
- Session type: fresh ephemeral CLI task for every case
- Authorization: read-only prompts; web search enabled only for the open-discovery Search case

This evidence establishes installation, fresh-task discovery, and the bounded behaviors below. It does not establish the complete scenario suite, public Git installation, upgrade behavior, or usefulness across models and plugin combinations.

## Observations

| Case | Expected behavior | Observed evidence | Result |
| --- | --- | --- | --- |
| Clear spelling repair | Stay direct; do not start research or shaping. | Returned only the corrected sentence. No Soundings Skill was loaded. | Pass |
| Explicit `$search` | Load the installed Search contract, verify a narrow external fact, state the evidence limit, and avoid mutation. | Read `soundings/0.1.0/skills/search/SKILL.md` from the installed cache; checked local CLI help; returned the supported syntax and what the help did not prove. | Pass |
| Explicit `$shape` | Make a consequential architecture choice judgeable with one real counterform and a recommendation, without turning it into a questionnaire. | Read the installed Shape contract and relevant references; compared independent Skills with a mandatory four-stage pipeline through equivalent usage scenes; recommended the independent form. | Pass |
| Implicit Shape | Discover Shape without the invocation token when an agent-added product model would govern substantial downstream work. | Announced `soundings:shape`, read the installed contract, produced two representative playable forms, and kept the four-axis model provisional. | Pass |
| Implicit Search | Discover Search when a repetitive solution space needs a concrete adjacent reference and current evidence. | Announced `soundings:search`, read the installed contract and references, used a current Forum Theatre practice, separated source from transfer, and proposed one testable interaction. | Pass |
| Specialized owner precedence | Yield when a more specific method owns the evidence standard. | A Codex CLI documentation question used `openai-docs` rather than Soundings Search and stayed within local help, matching Soundings' domain-owner boundary. | Pass |

## Observed limitation

The host warned that aggregate descriptions for all installed Skills were shortened to fit its Skill-context budget. Codex also stated that every Skill remained visible. The tested explicit and implicit Soundings cases still resolved from the installed cache, but discovery quality under other heavily saturated plugin sets is not established.

## Still unverified

- the remaining cases in `plugins/soundings/docs/behavior-scenarios.md`;
- installation from the public Git marketplace rather than the local checkout;
- behavior after a marketplace upgrade and plugin version change;
- cross-model consistency;
- long-running project corrections that must propagate through real plans, code, and docs.
