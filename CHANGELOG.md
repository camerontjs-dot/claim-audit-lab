# Changelog

## Unreleased - 2026-05-11

Claim Audit Lab C-B accommodation for the research apparatus.

- Added locked C-B v1.0.0 read models, vocabulary pinning, and fail-closed C-B bundle intake.
- Added `claim-audit audit-bundle <bundle-dir> --out-dir <dir>` for synthetic C-B bundle auditing.
- Added C-B adapter logic that audits only `extracted_claim` records and derives CAL semantic claim types from claim text.
- Added audited C-B output-copy writing that leaves sealed input bundles unchanged.
- Added typed intake deviations for malformed, tampered, version-drifted, or hash-invalid C-B bundles.
- Added synthetic C-A -> Evidence Bundler C-B -> CAL audited-output verification notes.

Known limits for the C-B path:

- The current round trip uses synthetic contract fixtures.
- Evidence Bundler Phase 0 fixture output does not perform retrieval, review, or support scoring.
- C-B accommodation verifies engineering handoff behavior, not real retrieval quality or research-measurement calibration.

## 0.1.0 - 2026-05-05

Initial CLI-first release candidate.

- Added deterministic supplied-evidence claim auditing.
- Added Markdown and plain-text draft loading.
- Added YAML and JSON evidence-bundle loading.
- Added conservative claim extraction.
- Added deterministic evidence matching, rule checks, support labels, risk labels, and rule flags.
- Added human-review Markdown reports and typed JSON reports.
- Added `claim-audit audit` and `claim-audit demo` commands.
- Added two checked-in fictional draft/evidence/report fixture families.
- Added validation-inspired IQ/OQ/PQ records under `validation/`.
- Closed v1 validation for the public fictional-fixture CLI scope, with future gates recorded for real-data and research-use validation.
- Added MIT license, package metadata, GitHub pin copy, and social-card source.

Known v1 limits:

- No source discovery.
- No live LLM or provider calls.
- No web UI.
- No support-score or assessment-confidence scoring.
- No research-use calibration claim.
- No real-data fixture qualification claim.
- No regulated-compliance claim.
