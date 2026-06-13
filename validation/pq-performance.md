# PQ: Performance Qualification

status: verified for v0.2 engineering release; research qualification pending
last_updated: 2026-06-13

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
- synthetic C-B contract bundle audit output
- visible future gates for research-use calibration and real-world production data

Out of scope for v1: research-use human calibration, real-world production data, full Evidence Bundler retrieval/review quality, and production deployment claims. These are not failed v1 checks. They are future validation gates recorded in `deviation-log.md` and must be completed before testing real data fixtures or using the tool on real cases.

## Required Example Families

| Family | Claim types | Minimum evidence | Status |
| --- | --- | --- | --- |
| AI research memo | numeric, causal, scope, interpretive | `examples/drafts/ai-research-note.md`, `examples/evidence/ai-research-evidence.yml`, generated Markdown and JSON reports | representative run verified |
| Product README paragraph | capability, scope, comparative, prediction, stale-source behavior | `examples/drafts/product-readme-note.md`, `examples/evidence/product-readme-evidence.yml`, generated Markdown and JSON reports | representative run verified |
| C-B synthetic contract fixture | extracted C-B claim, source profile, passage provenance, null audit fields | `tests/fixtures/cb/evidence-bundle-minimal`; Evidence Bundler `tests/fixtures/scaffold-run-minimal`; audited C-B output copy | representative contract run verified |

## Protocol

| Step | Command or inspection | Expected result | Date run | Result | Evidence reference | Status |
| --- | --- | --- | --- | --- | --- | --- |
| PQ-001 | `claim-audit audit examples/drafts/ai-research-note.md --evidence examples/evidence/ai-research-evidence.yml --out build/reports/ai-research-note.md --json-out build/reports/ai-research-note.json` | Markdown and JSON reports are generated from checked-in data. | 2026-05-04 | Generated 4-claim report with 1 supported, 1 partially supported, 2 overstated, and 2 high-risk findings. | ignored `build/reports/`; `docs/verification.md` | verified |
| PQ-002 | `claim-audit audit examples/drafts/product-readme-note.md --evidence examples/evidence/product-readme-evidence.yml --out build/reports/product-readme-note.md --json-out build/reports/product-readme-note.json` | Reports exercise labels and rule checks not covered by the AI research memo. | 2026-06-13 | Generated 4-claim report with 2 unsupported, 2 overstated, and 2 high-risk findings. | checked-in and ignored generated reports; `docs/verification.md` | verified |
| PQ-003 | Inspect generated reports. | Reports include trace links, limitations, support labels, rule flags, and rewrite guidance where applicable. | 2026-05-04 | Reports include metadata, audit boundary, limitations, claim register, candidate evidence, rule flags, explanations, and rewrite guidance where useful. | generated Markdown reports | verified |
| PQ-004 | Validate JSON reports against typed report models. | JSON report output round-trips through `AuditReport`. | 2026-05-04 | Demo, AI research, and Product README JSON outputs validated with `AuditReport.model_validate_json(...)`. | command result; generated JSON reports | verified |
| PQ-005 | Review examples for private data and local-only paths. | No private application materials, tokens, or local-only paths appear. | 2026-05-04 | Existing report tests passed; public-copy scan found expected historical, protocol, prompt, and scan-pattern references only. | `tests/test_report.py`; public-copy scan in `docs/verification.md` | verified |
| PQ-006 | `claim-audit audit-bundle tests/fixtures/cb/evidence-bundle-minimal --out-dir build/unit6-cli-smoke` | Audited C-B output copy is generated from checked-in synthetic C-B data. | 2026-05-11 | Generated `build/unit6-cli-smoke/evidence-bundle-minimal-audited`; 1 claim audited; 0 retrieval seeds skipped. | ignored `build/unit6-cli-smoke/`; `docs/verification.md` | verified |
| PQ-007 | Evidence Bundler `verify-intake` and `build-fixture-bundle`, followed by CAL `audit-bundle`. | Synthetic C-A fixture can pass through Evidence Bundler into CAL audited output. | 2026-05-11 | C-A intake verified, C-B fixture bundle written, CAL audited copy written, and audited output reloaded through C-B fail-closed loader. | `docs/verification.md` C-B accommodation addendum | verified |
| PQ-008 | Inspect audited C-B output claim fields. | `audit.*` fields are populated without mutating source bundle semantics. | 2026-05-11 | Reload check showed `clm-001`, `supported`, `false_caution_flag=False`, `deviation_flag=False`. | `docs/verification.md`; `tests/test_cb_output_writer.py` | verified |
| PQ-009 | Regenerate both checked-in example families twice. | Markdown and JSON artifacts are byte-identical across runs. | 2026-06-13 | Both families regenerated twice with identical hashes. | `examples/reports/`; `docs/verification.md` | verified |
| PQ-010 | Run the full synthetic Harness -> Evidence Bundler -> CAL workflow. | Finalized supplied evidence reaches CAL, which writes a report and audited bundle. | 2026-06-13 | Three claims audited; zero retrieval seeds skipped; handoff completed. | Evidence Bundler ignored build output; `docs/verification.md` | verified |
| PQ-011 | Replay the sealed 98-claim pilot with pinned metadata. | All claims are preserved, a second replay is byte-identical, and changed verdicts are reviewed without unblinding. | 2026-06-13 | 15 bundles and 98 claims replayed; 68 changed verdicts recorded; blind labels remain untouched. | MainFrame `outputs/v0.2-pilot-replay/`; `docs/verification.md` | verified engineering replay |

## Acceptance Criteria

PQ passes for the v0.2 engineering release when both fictional example families run end
to end, outputs are stable and inspectable, generated JSON validates through
`AuditReport`, the apparatus round trip passes, and future-use gates remain visible.

## Future Validation Before Real Cases

Before Claim Audit Lab is used on real data fixtures, sensitive materials, production-like drafts, or research measurement outputs, PQ must be extended with:

- real-data or production-like fixture qualification
- representative Evidence Bundler retrieval/review qualification beyond synthetic fixtures
- human-review calibration and disagreement analysis
- privacy/sensitivity review for any non-fictional inputs
- neutral, adverse, and false-caution fixture families
- acceptance criteria for missed unsupported claims and excessive caution
- refreshed CLI/report evidence generated from the new fixture set

## Record

PQ passed for the public v0.2 engineering scope. The sealed pilot replay confirms
deterministic execution, not calibrated correctness. Real-data and research-use
qualification remain future gates before real-case use.
