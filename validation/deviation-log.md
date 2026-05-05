# Validation Deviation Log

status: open
last_updated: 2026-05-04

Purpose: track validation failures, accepted limitations, and follow-up actions. Gaps should be visible here instead of silently disappearing from the validation matrix.

## Deviation Rules

Add an entry when:

- a validation protocol step fails
- a public capability claim lacks a matrix row
- a matrix row is marked `verified` without current evidence
- a report overclaims truth verification
- a test, fixture, or report is removed without updating traceability
- a known limitation is accepted for public release

## Log

| ID | Date | Reference | Area | Description | Impact | Decision | Rationale | Owner/status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DEV-000 | 2026-04-30 | validation package | package setup | Placeholder row created before protocol execution. | none | closed | IQ/OQ/PQ-inspired records replaced the placeholder state with current evidence. | Codex/closed |
| DEV-001 | 2026-05-04 | `PQ-006` | research-use calibration | Human-review calibration and disagreement analysis are not complete for v1. | The tool should not be presented as a calibrated research measurement instrument yet. | defer | V1 validates the portfolio CLI workflow against fictional fixtures; research measurement rules remain outside the v1 shipping path. | Cameron/future research-use phase |
| DEV-002 | 2026-05-04 | `PQ` scope | production data | Public validation uses checked-in fictional examples, not real-world production data. | Representative behavior is visible, but production deployment behavior is not claimed. | accept for v1 | Public portfolio validation should avoid private or sensitive materials; real production-data qualification would require a separate intended-use decision. | Cameron/accepted limitation |
