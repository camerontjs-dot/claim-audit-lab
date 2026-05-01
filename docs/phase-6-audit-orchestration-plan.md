# Phase 6 Audit Orchestration Plan

status: planned
last_updated: 2026-05-01
phase: Phase 6

Purpose: harden `audit_document(draft, evidence_bundle, config=None) -> AuditReport` after the Phase 5 rule-assessed slice. Phase 6 should make the audit pipeline coherent, resilient, and easy to validate before full report rendering and CLI behavior are built.

## Phase 5 Tie-Off Baseline

Phase 5 is complete and rechecked as of 2026-05-01.

Current verified baseline:

- `assess_claim_support(...)` returns deterministic support labels, risk labels, explanations, limitations, and rule flags.
- `AuditConfig.reference_date` makes stale-source checks deterministic and opt-in.
- `EvidenceCandidate` preserves source reliability, source date, and source URL metadata.
- `audit_document(...)` returns rule-assessed `AuditReport` values for the current slice.
- The AI research fixture labels are `overstated`, `supported`, `partially_supported`, and `overstated`.
- Empty evidence bundles return `needs_source` assessments with an evidence-bundle warning.
- Full local verification passes: compileall, pytest, ruff, mypy, and coverage.

Known limits to preserve until later phases:

- The Markdown renderer is still a minimal Phase 5 slice renderer.
- The public CLI workflow is not implemented.
- The second fixture family does not yet have generated Markdown/JSON reports.
- Candidate evidence scores are ranking signals only, not support scores.

## Requirements Owned

Phase 6 owns or prepares these validation rows:

- `CAL-REQ-012`: Phase 6 covers the auditor-level empty-evidence behavior. Keep the matrix row `planned` until report-level evidence also exists, or split the row before marking any auditor-only portion `verified`.
- `CAL-REQ-025`: the audit pipeline must return a structured report with trace links and limitations.
- `CAL-REQ-016`: high-risk findings must be treated as completed audit results, not runtime failures. The CLI-specific part should remain planned until Phase 8 unless the row is split.

Related rows to avoid overclaiming:

- `CAL-REQ-024` remains broader than Phase 6 because full report polish for support-quality differences is later work.
- `CAL-REQ-029` remains broader than Phase 6 because public label documentation and report coverage are not complete.
- `CAL-REQ-039` can gain auditor-level tests for deterministic output, but report-anchor coverage belongs with report hardening.

## Primary Files

- `src/claim_audit_lab/auditor.py`
- `tests/test_auditor.py`
- `src/claim_audit_lab/models.py` only if traceability requires a small contract addition.
- Existing fixtures under `examples/drafts/`, `examples/evidence/`, and `tests/fixtures/`.

Do not move report rendering, CLI behavior, or new rule taxonomy into Phase 6.

## Orchestration Contract

`audit_document(...)` should coordinate existing layers:

1. Extract deterministic claims from a draft.
2. Match candidate evidence using `AuditConfig`.
3. Assess each claim with the Phase 5 rule layer.
4. Flatten claim-level rule flags into report-level rule flags.
5. Build summary counts from the final `ClaimAssessment` list only.
6. Attach evidence-bundle warnings and report limitations.
7. Return a typed `AuditReport` without treating audit findings as exceptions.

The coordinator may be refactored into private helpers if that improves testability:

- `_build_assessments(...)`
- `_collect_rule_flags(...)`
- `_build_summary(...)`
- `_build_evidence_bundle_warnings(...)`
- `_build_report_limitations(...)`

Keep helper names private unless a public API is clearly needed.

## Required Behavior

- Claims, candidate evidence, rule flags, summary counts, warnings, and limitations remain traceable from the returned `AuditReport`.
- Report-level `rule_flags` exactly flatten claim-level rule flags in deterministic order.
- Every report-level rule flag points to an assessed claim ID.
- Summary counts are derived from assessments, not maintained separately by hand.
- High-risk claims increase `summary.high_risk_claims` and do not cause runtime failure.
- Empty evidence bundles return completed audit output with a clear bundle warning.
- Drafts with no extractable claims return a valid zero-claim report.
- Config-driven candidate thresholding and capping continue to flow through the audit layer.
- Report limitations include the supplied-evidence boundary and candidate-score boundary.
- Normal tests and demo runs remain local-only: no network calls, no API keys, no live LLM calls.

## Required Tests

Create `tests/test_auditor.py`.

Minimum tests:

- `audit_document(...)` returns a typed `AuditReport` with one `ClaimAssessment` per extracted claim.
- Report-level rule flags exactly equal the flattened claim-level rule flags.
- Every rule flag `claim_id` belongs to a claim in the report.
- Summary counts match the labels and risk labels in `report.claims`.
- The AI research fixture keeps the Phase 5 target labels and high-risk count.
- Empty evidence bundles return `needs_source` assessments and a useful warning.
- High-risk findings return successfully and are counted, not raised as errors.
- A draft with no extractable claims returns a valid zero-claim report.
- `AuditConfig(min_overlap_score=..., max_candidate_evidence=...)` still affects candidate evidence through the audit layer.
- Repeated runs with the same inputs produce the same structured report data.
- Report limitations contain no forbidden capability language and preserve supplied-evidence wording.

Keep `tests/test_vertical_slice.py` focused on the reviewer-facing slice and renderer/demo behavior. Move pure auditor-contract assertions into `tests/test_auditor.py` when practical.

## Non-Goals

- Do not add a support score or assessment-confidence score.
- Do not expand deterministic rule taxonomy.
- Do not build full Markdown report rendering.
- Do not build CLI input/output behavior.
- Do not generate the second fixture report family.
- Do not add source discovery, search, web calls, or LLM calls.
- Do not implement research-use paired-draft metrics.

## Acceptance Criteria

Phase 6 is complete when:

- `tests/test_auditor.py` covers the orchestration contract.
- `audit_document(...)` is resilient for empty evidence bundles, no-claim drafts, high-risk findings, and config-threaded candidate matching.
- Structured trace links among claims, candidates, rule flags, summary counts, warnings, and limitations are tested.
- Summary consistency is enforced by tests.
- Candidate scores remain ranking signals and are not presented as support labels.
- `CAL-REQ-025` can be marked `verified` if trace-link and limitation tests pass.
- `CAL-REQ-012` remains `planned` unless report coverage exists too, or the matrix row is split to isolate the auditor-level empty-evidence behavior.
- `CAL-REQ-016` is either left `planned` for CLI coverage or split so the auditor-level behavior can be marked separately.
- The next best step is Phase 7 report rendering hardening.

## Verification Commands

Run from `portfolio/live-asset/claim-audit-lab/`:

```bash
.venv/bin/python -m compileall -q src tests
.venv/bin/python -m pytest
.venv/bin/python -m ruff format src/claim_audit_lab/auditor.py tests/test_auditor.py tests/test_vertical_slice.py
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
.venv/bin/python -m mypy src
.venv/bin/python -m coverage run --branch -m pytest
.venv/bin/python -m coverage report
```

Only include `models.py` or report files in the formatting command if Phase 6 changes those files.

## Documentation Updates After Implementation

After Phase 6 implementation:

- Update `docs/master-plan.md` Phase 6 status and next step.
- Update `docs/verification.md` with checks run and outcomes.
- Update `docs/validation-matrix-reference.md` for `CAL-REQ-025`, and for `CAL-REQ-012` or `CAL-REQ-016` only if the rows are intentionally split or their full acceptance criteria are met.
- Update `README.md` if the implemented status or public instructions change.
- Update `/Users/gammaquantum/My Drive/projects/job-hunt/log/job-hunt-log.md`.
- Refresh `docs/handoff-prompt.md` so the next session starts Phase 7 report rendering hardening.
