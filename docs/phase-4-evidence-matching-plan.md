# Phase 4 Evidence Matching Plan

status: complete
last_updated: 2026-04-30
phase: Phase 4

Purpose: record the implemented deterministic candidate-evidence matching contract. Phase 4 creates traceable evidence candidates only; it does not decide final support labels, rule flags, audit summaries, report rendering, or CLI behavior.

Implementation result: `src/claim_audit_lab/evidence_matching.py` and `tests/test_evidence_matching.py` are implemented. `CAL-REQ-005` is verified by numeric matching tests. `CAL-REQ-024` remains planned until the later rule/report portions are covered.

## Current Inputs

Use the existing typed contracts:

- `Claim`: extracted claim ID, text, claim type, and source location.
- `EvidenceBundle`: supplied sources and excerpts.
- `AuditConfig`: `min_overlap_score` and `max_candidate_evidence` control thresholding and result caps.
- `EvidenceCandidate`: candidate source/excerpt links with bounded scores and transparent rationales.

Primary fixtures:

- AI research memo: `examples/drafts/ai-research-note.md` and `examples/evidence/ai-research-evidence.yml`.
- Product README paragraph: `examples/drafts/product-readme-note.md` and `examples/evidence/product-readme-evidence.yml`.

## Implementation Contract

Primary files:

- `src/claim_audit_lab/evidence_matching.py`
- `tests/test_evidence_matching.py`
- `src/claim_audit_lab/models.py` only if needed to preserve source metadata on candidates.

Add these public functions:

```python
def match_evidence(
    claim: Claim,
    evidence_bundle: EvidenceBundle,
    config: AuditConfig | None = None,
) -> list[EvidenceCandidate]:
    ...

def match_claims_to_evidence(
    claims: list[Claim],
    evidence_bundle: EvidenceBundle,
    config: AuditConfig | None = None,
) -> dict[str, list[EvidenceCandidate]]:
    ...
```

Default `config` to `AuditConfig()` when omitted. Return candidates sorted by descending score, then `source_id`, then `excerpt_id`; cap each claim's candidates at `config.max_candidate_evidence`.

If the current `EvidenceCandidate` model cannot retain source quality metadata, add optional/defaulted fields rather than breaking existing tests:

- `source_reliability: SourceReliability = "unknown"`
- `source_date: Date | None = None`

Do not add support labels, rule flags, warnings, or final assessment fields in Phase 4.

## Matching Policy

Use deterministic local scoring only. No network calls, no LLM calls, no hidden current-state dependencies.

Normalize text by lowercasing and extracting alphanumeric tokens. Ignore common stopwords and apply the same light stemming style used in `claim_extraction.py` where useful.

Extract signals:

- Numbers: `52`, `18`, `11`, `12`, `9`, percentages, and decimal values.
- Dates: ISO dates and year-like values when present.
- Key terms: non-stopword tokens shared by claim and excerpt.
- Phrase overlap: exact normalized phrase fragments where practical.

Score each claim/excerpt pair with a bounded `0.0` to `1.0` score:

- Numeric agreement is a strong signal. A claim with matching numbers should outrank a claim with only term overlap.
- Numeric disagreement must not look fully supported. If a claim contains numbers and an excerpt has related terms but none of the claim's numbers, cap the score below `0.7`.
- Date agreement is a supporting signal, not a support assessment.
- Token overlap is useful for candidate discovery but should not override numeric mismatch.
- Reliability and freshness metadata should be carried through or preserved for lookup, but should not lower scores in Phase 4. Rule handling belongs to Phase 5.

Candidate rationales should be short and auditable, for example:

- `matched numbers: 52; overlapping terms: test, set, workflow, outputs; source reliability: medium`
- `overlapping terms: meridian, traceable, audit, summaries, research, notes; source reliability: medium`

Avoid wording such as `true`, `false`, `verified`, `proven`, or `fact checked`.

## Required Tests

Create `tests/test_evidence_matching.py`.

Minimum tests:

- Numeric match: the AI research claim `The test set included 52 workflow outputs.` links to `source-001` / `excerpt-002` with a high bounded score.
- Numeric mismatch: a claim such as `The test set included 99 workflow outputs.` does not receive a high score against the `52`-output excerpt.
- Reduction numbers: the AI research `18` to `11` claim links to `source-001` / `excerpt-001`.
- Product capability: the Meridian Notes capability claim links to `source-product-001` / `excerpt-product-001`.
- Product comparison: the faster-than-manual claim links to `source-product-001` / `excerpt-product-002`.
- Scope limitation candidate: the regulated-workflow scope claim can find `source-product-002` / `excerpt-product-003` as a candidate without deciding the claim is supported.
- Prediction limitation candidate: the `will always prevent` claim can find `source-product-002` / `excerpt-product-004` as a candidate without deciding final support.
- Multiple candidates are sorted deterministically and capped by `AuditConfig.max_candidate_evidence`.
- Empty evidence bundles return an empty list without crashing.
- Candidate scores are always bounded from `0.0` to `1.0`.
- Candidate links preserve `source_id`, `excerpt_id`, and source quality metadata or a documented lookup path.
- `match_claims_to_evidence(...)` returns a dictionary keyed by stable claim IDs.

Keep assertions behavior-level. Do not pin exact floating-point scores unless the score is part of the public contract; prefer threshold assertions such as `>= 0.7`, `< 0.7`, and sorted order checks.

## Acceptance Criteria

Phase 4 is complete when:

- `src/claim_audit_lab/evidence_matching.py` returns deterministic `EvidenceCandidate` objects.
- Matching stays separate from support assessment and rule checks.
- Numeric matches are discoverable and numeric mismatches are not presented as high-confidence candidates.
- Product README capability, comparative, scope, and prediction fixtures produce useful candidate links.
- Empty evidence bundles do not crash.
- Candidate ordering and capping are deterministic.
- `CAL-REQ-005` can be marked `verified`.
- `CAL-REQ-024` remains `planned` unless its rule/report portions are split or fully covered later.

## Verification Commands

Run from `portfolio/live-asset/claim-audit-lab/`:

```bash
.venv/bin/python -m compileall -q src tests
.venv/bin/python -m pytest
.venv/bin/python -m ruff format src/claim_audit_lab/evidence_matching.py tests/test_evidence_matching.py src/claim_audit_lab/models.py tests/test_models.py
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
.venv/bin/python -m mypy src
.venv/bin/python -m coverage run --branch -m pytest
.venv/bin/python -m coverage report
```

Only include `models.py` and `tests/test_models.py` in the formatting command if the candidate model changes.

## Documentation Updates After Implementation

After Phase 4 implementation:

- Update `docs/master-plan.md` Phase 4 status.
- Update `docs/verification.md` with commands and results.
- Update `docs/validation-matrix-reference.md`: mark `CAL-REQ-005` verified if tests pass; keep `CAL-REQ-024` planned unless later layers are covered.
- Update `README.md` if the implemented status changes.
- Update `/Users/gammaquantum/My Drive/projects/job-hunt/log/job-hunt-log.md`.
- Leave the next best step as Phase 4A runnable vertical slice planning.
