# Plan-bound descriptive comparison

`compare.py` reads explicitly supplied plans, summaries, attempt receipts and
reviews. It never starts an agent. Use an explicit existing Field Lab source
checkout; the integration imports native `validate_plan` and the current private
`fieldlab.explain._artifact_report`, so compatibility is checked against that
checkout rather than promised across arbitrary Field Lab versions.

```bash
python3 evals/compare.py --fieldlab-root /path/to/skill-field-lab \
  --plan /private/lab/first.plan.json --plan /private/lab/second.plan.json \
  --summary /private/lab/runs/first/summary.json \
  --summary /private/lab/runs/second/summary.json \
  --receipt /private/lab/runs/first/subject/case/repeat-001/attempt-001/receipt.json
```

Repeat `--plan`, `--summary`, `--receipt`, and `--review` for all selected inputs.
Four factorial plans must each have their explicit summary. The Python entry is
`compare(receipt_paths, review_paths, plan_paths, fieldlab_root, summary_paths)`.
Output retains errors and missing planned rows. An invalid receipt is not a usable
observation; a known zero-invocation attempt differs from a row with no valid
receipt. Multiple attempts within one planned repeat require adjudication; the
analysis never silently picks a successful retry or counts attempts as repeats.
Reviews retain their identities and independence. Implementer-run support is not
independent support. No supplied receipt proves that an unreported run never
started; missing rows therefore mean missing valid evidence, not zero spending.

Validation is explicitly `comparison-fields-and-native-integrity` and full
receipt JSON Schema validation is `not-performed`. This tool validates the
fields it consumes, native plan integrity, summary identity binding, sealed
metadata, receipt artifacts, selected execution settings and exact review
requirements. It is descriptive analysis rather than a general receipt-acceptance
or cryptographic authentication service. Source availability, actual host Skill
selection, content application and research benefit remain separate claims.

Ordinary tests use constructed records and injected native functions, with no
Field Lab install:

```bash
python3 -m unittest discover -s evals -p 'test_compare.py' -v
```

An optional explicit source integration uses the native plan builder and receipt
constructor, without running a target or fake target executable:

```bash
FIELDLAB_SOURCE=/path/to/skill-field-lab python3 -m unittest discover -s evals -p 'test_compare.py' -v
```

`python3 evals/check.py` discovers these tests automatically; the native check is
skipped unless `FIELDLAB_SOURCE` is set. Generated plans, summaries and receipts
must remain outside Git.

For invoked attempts, semantic requirements must exactly match the sealed case;
removing them from a receipt cannot turn pending into not-required. Native
zero-invocation preflight receipts may legitimately carry no requirements and
remain explicitly known-no-invocation. Invoked attempts require completed,
quiescent process metadata; pass additionally requires verification support.
Rows preserve runtime, process/execution boundaries, delivery, unknown/observed
host selection, content-application review status and usage independently of the
execution outcome. Every supplied plan without a validated summary is an error,
even when no receipt was supplied for that plan.
