# Changelog

## 0.2.0 - 2026-06-13

Claim Audit Lab v0.2 stabilizes the public package and binds the C-B research-apparatus
path to one deterministic policy.

### Added

- Packaged contract resources and demo fixtures loaded through `importlib.resources`.
- Clean-wheel verification for `--help`, `demo`, and `audit-bundle`.
- `ClaimType.unclassified`, with native extraction skipping it and C-B audits returning
  `not_checkable`.
- Public `audit_claims(...)` orchestration and shared contract serialization helpers.
- Claim-scoped C-B evidence and separately linked counterevidence.
- Default human-readable reports from `audit-bundle`.
- `--audit-run-id` and `--audited-at` for byte-identical audited bundles.
- Threshold, strong-wording, counterevidence, config-drift, classifier-parity, and
  reproducibility tests.

### Changed

- Replaced duplicate classifiers with one governed priority:
  prediction, scope, causal, comparative, credential, capability, numeric,
  interpretive, unclassified.
- Consolidated tokenization, stemming, stopwords, date/number handling, and trigger
  vocabularies.
- Bound C-B audit intake to the exact frozen `cal-rules-v1.2.0` profile.
- Defined the support signal as `max_support - 0.3 * max_counterevidence`, clamped to
  `[0, 1]`.
- Froze candidate, partial, sourced, and false-caution boundaries at `0.40`, `0.55`,
  `0.80`, and `0.85`.
- Made linked counterevidence prevent a clean `supported` verdict.
- Made strong-wording suppression require the same trigger in direct evidence and no
  conflicting counterevidence.
- Replaced `ClaimAssessment.suggested_rewrite` with populated
  `rewrite_guidance: list[str]`.
- Regenerated checked-in examples and documented scores as supplied-evidence signals,
  never truth probabilities.
- Made Ruff formatting part of the release gate.

### Removed

- Dead `AuditConfig.strictness`.
- Cross-module use of private audit helpers.
- Redundant direct `rich` dependency.
- Internal phase-number language and stale workspace paths from public output.

### Verification

- 213 tests pass.
- Ruff lint and formatting, strict mypy, and compileall pass.
- Source branch coverage is 96%.
- A clean wheel passes `--help`, `demo`, and `audit-bundle`.
- Checked-in examples regenerate byte-identically.
- The synthetic Harness -> Evidence Bundler -> Claim Audit Lab round trip passes.
- The sealed 98-claim pilot replay is byte-identical with pinned run metadata.

Research qualification remains open. Blind calibration is `0/98`; human verdicts remain
primary until the documented agreement, kappa, adverse-recall, and per-condition error
gates pass.

## 0.1.0 - 2026-05-05

Initial CLI-first public release.

- Added deterministic supplied-evidence claim auditing.
- Added Markdown and plain-text draft loading.
- Added YAML and JSON evidence-bundle loading.
- Added conservative claim extraction and evidence matching.
- Added support labels, risk labels, rule flags, Markdown reports, and typed JSON.
- Added `claim-audit audit`, `claim-audit demo`, and the first C-B `audit-bundle` path.
- Added two fictional example families and validation-inspired IQ/OQ/PQ records.
- Added MIT licensing and public package metadata.

Known v0.1 limits included no source discovery, no live model calls, no web UI, no
research calibration, and no regulated-compliance claim.
