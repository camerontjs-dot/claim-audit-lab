# Changelog

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
- Added MIT license, package metadata, GitHub pin copy, and social-card source.

Known v1 limits:

- No source discovery.
- No live LLM or provider calls.
- No web UI.
- No support-score or assessment-confidence scoring.
- No research-use calibration claim.
- No regulated-compliance claim.
