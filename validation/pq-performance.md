# PQ: Performance Qualification

status: verified
last_updated: 2026-05-04

Purpose: verify that Claim Audit Lab performs consistently in representative full audit runs using checked-in fictional or sanitized data.

This is a validation-inspired record for a non-regulated portfolio context. It is not intended to demonstrate FDA, EMA, GxP, GMP, CSV, or regulated-compliance status.

## Scope

PQ covers complete runs through the public workflow:

- draft input
- evidence bundle input
- claim extraction
- evidence matching
- rule checks
- report generation
- visible exclusions for research-use calibration and real-world production data

Out of scope for v1: research-use human calibration, real-world production data, and production deployment claims. These are deferred as accepted limitations in `deviation-log.md`.

## Required Example Families

| Family | Claim types | Minimum evidence | Status |
| --- | --- | --- | --- |
| AI research memo | numeric, causal, scope, interpretive | `examples/drafts/ai-research-note.md`, `examples/evidence/ai-research-evidence.yml`, generated Markdown and JSON reports | representative run verified |
| Product README paragraph | capability, scope, comparative, prediction, stale-source behavior | `examples/drafts/product-readme-note.md`, `examples/evidence/product-readme-evidence.yml`, generated Markdown and JSON reports | representative run verified |
| Neutral/adverse scaffold case | no-change, worse-output, false-caution behavior | future research-use fixture family if the tool is used as a measurement instrument | deferred outside v1 |

## Protocol

| Step | Command or inspection | Expected result | Date run | Result | Evidence reference | Status |
| --- | --- | --- | --- | --- | --- | --- |
| PQ-001 | `claim-audit audit examples/drafts/ai-research-note.md --evidence examples/evidence/ai-research-evidence.yml --out build/reports/ai-research-note.md --json-out build/reports/ai-research-note.json` | Markdown and JSON reports are generated from checked-in data. | 2026-05-04 | Generated 4-claim report with 1 supported, 1 partially supported, 2 overstated, and 2 high-risk findings. | ignored `build/reports/`; `docs/verification.md` | verified |
| PQ-002 | `claim-audit audit examples/drafts/product-readme-note.md --evidence examples/evidence/product-readme-evidence.yml --out build/reports/product-readme-note.md --json-out build/reports/product-readme-note.json` | Reports exercise labels and rule checks not covered by the AI research memo. | 2026-05-04 | Generated 4-claim report with 2 supported, 2 overstated, and 2 high-risk findings. | ignored `build/reports/`; `docs/verification.md` | verified |
| PQ-003 | Inspect generated reports. | Reports include trace links, limitations, support labels, rule flags, and rewrite guidance where applicable. | 2026-05-04 | Reports include metadata, audit boundary, limitations, claim register, candidate evidence, rule flags, explanations, and rewrite guidance where useful. | generated Markdown reports | verified |
| PQ-004 | Validate JSON reports against typed report models. | JSON report output round-trips through `AuditReport`. | 2026-05-04 | Demo, AI research, and Product README JSON outputs validated with `AuditReport.model_validate_json(...)`. | command result; generated JSON reports | verified |
| PQ-005 | Review examples for private data and local-only paths. | No private application materials, tokens, or local-only paths appear. | 2026-05-04 | Existing report tests passed; public-copy scan found expected historical, protocol, prompt, and scan-pattern references only. | `tests/test_report.py`; public-copy scan in `docs/verification.md` | verified |
| PQ-006 | Compare a calibration sample against human review before research use. | Disagreements are documented rather than hidden. | 2026-05-04 | Deferred outside v1; recorded as accepted limitation because v1 does not use the tool as a research measurement instrument. | `DEV-001` | deferred |

## Acceptance Criteria

PQ passes when both fictional example families run end to end, outputs are stable and inspectable, generated JSON validates through `AuditReport`, and known limitations are visible.

## Record

PQ passed on 2026-05-04 for v1 portfolio release. The research-use calibration step remains deferred outside v1 and is visible in `deviation-log.md`.
