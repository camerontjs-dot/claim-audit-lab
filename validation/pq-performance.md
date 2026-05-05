# PQ: Performance Qualification

status: verified for v1 public release
last_updated: 2026-05-05

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
- visible future gates for research-use calibration and real-world production data

Out of scope for v1: research-use human calibration, real-world production data, and production deployment claims. These are not failed v1 checks. They are future validation gates recorded in `deviation-log.md` and must be completed before testing real data fixtures or using the tool on real cases.

## Required Example Families

| Family | Claim types | Minimum evidence | Status |
| --- | --- | --- | --- |
| AI research memo | numeric, causal, scope, interpretive | `examples/drafts/ai-research-note.md`, `examples/evidence/ai-research-evidence.yml`, generated Markdown and JSON reports | representative run verified |
| Product README paragraph | capability, scope, comparative, prediction, stale-source behavior | `examples/drafts/product-readme-note.md`, `examples/evidence/product-readme-evidence.yml`, generated Markdown and JSON reports | representative run verified |

## Protocol

| Step | Command or inspection | Expected result | Date run | Result | Evidence reference | Status |
| --- | --- | --- | --- | --- | --- | --- |
| PQ-001 | `claim-audit audit examples/drafts/ai-research-note.md --evidence examples/evidence/ai-research-evidence.yml --out build/reports/ai-research-note.md --json-out build/reports/ai-research-note.json` | Markdown and JSON reports are generated from checked-in data. | 2026-05-04 | Generated 4-claim report with 1 supported, 1 partially supported, 2 overstated, and 2 high-risk findings. | ignored `build/reports/`; `docs/verification.md` | verified |
| PQ-002 | `claim-audit audit examples/drafts/product-readme-note.md --evidence examples/evidence/product-readme-evidence.yml --out build/reports/product-readme-note.md --json-out build/reports/product-readme-note.json` | Reports exercise labels and rule checks not covered by the AI research memo. | 2026-05-04 | Generated 4-claim report with 2 supported, 2 overstated, and 2 high-risk findings. | ignored `build/reports/`; `docs/verification.md` | verified |
| PQ-003 | Inspect generated reports. | Reports include trace links, limitations, support labels, rule flags, and rewrite guidance where applicable. | 2026-05-04 | Reports include metadata, audit boundary, limitations, claim register, candidate evidence, rule flags, explanations, and rewrite guidance where useful. | generated Markdown reports | verified |
| PQ-004 | Validate JSON reports against typed report models. | JSON report output round-trips through `AuditReport`. | 2026-05-04 | Demo, AI research, and Product README JSON outputs validated with `AuditReport.model_validate_json(...)`. | command result; generated JSON reports | verified |
| PQ-005 | Review examples for private data and local-only paths. | No private application materials, tokens, or local-only paths appear. | 2026-05-04 | Existing report tests passed; public-copy scan found expected historical, protocol, prompt, and scan-pattern references only. | `tests/test_report.py`; public-copy scan in `docs/verification.md` | verified |

## Acceptance Criteria

PQ passes for v1 when both fictional example families run end to end, outputs are stable and inspectable, generated JSON validates through `AuditReport`, and future-use gates are visible.

## Future Validation Before Real Cases

Before Claim Audit Lab is used on real data fixtures, sensitive materials, production-like drafts, or research measurement outputs, PQ must be extended with:

- real-data or production-like fixture qualification
- human-review calibration and disagreement analysis
- privacy/sensitivity review for any non-fictional inputs
- neutral, adverse, and false-caution fixture families
- acceptance criteria for missed unsupported claims and excessive caution
- refreshed CLI/report evidence generated from the new fixture set

## Record

PQ passed for the public v1 fictional-fixture CLI scope. No open v1 PQ failures remain. Real-data and research-use validation remains a future gate before real-case use.
