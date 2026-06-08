# Validation Deviation Log

status: closed for v1 public release; future-use gates recorded
last_updated: 2026-05-11

Purpose: track validation failures, accepted limitations, future-use gates, and follow-up actions. Gaps should be visible here instead of silently disappearing from the validation matrix.

## Deviation Rules

Add an entry when:

- a validation protocol step fails
- a public capability claim lacks a matrix row
- a matrix row is marked `verified` without current evidence
- a report overclaims truth verification
- a test, fixture, or report is removed without updating traceability
- a known limitation is accepted for public release
- a validation activity is required before expanding beyond the v1 intended use

## V1 Outcome

No open v1 validation failures remain for the public fictional-fixture CLI scope. The entries below either closed setup issues or record future validation gates that must be completed before real data, sensitive materials, production-like drafts, or research measurement runs.

## Log

| ID | Date | Reference | Area | Description | Impact | Decision | Rationale | Owner/status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DEV-000 | 2026-04-30 | validation package | package setup | Placeholder row created before protocol execution. | none | closed | IQ/OQ/PQ-inspired records replaced the placeholder state with current evidence. | Codex/closed |
| DEV-001 | 2026-05-04 | future validation gate | research-use calibration | Human-review calibration and disagreement analysis are not part of the v1 public release. | The tool must not be presented as a calibrated research measurement instrument until this gate is complete. | gate before research use | V1 validates the portfolio CLI workflow against fictional fixtures; research measurement requires a separate calibration pass. | Cameron/future research-use phase |
| DEV-002 | 2026-05-04 | future validation gate | real data fixtures | Public validation uses checked-in fictional examples, not real-world production data. | Representative behavior is visible, but production or real-case behavior is not claimed. | gate before real data use | Public portfolio validation should avoid private or sensitive materials; real-data fixture qualification requires a separate intended-use decision. | Cameron/future real-data validation |
| DEV-003 | 2026-05-11 | future validation gate | full C-B retrieval/review path | C-B accommodation is verified with a synthetic Evidence Bundler fixture writer, not a full retrieval, review, or human-curation workflow. | The engineering handoff is verified, but retrieval quality and real evidence review are not claimed. | gate before full apparatus use | Evidence Bundler Phase 0 intentionally emits fixture-only C-B artifacts. Full apparatus validation must include retrieval/review fixture qualification and human-review calibration before research measurement. | Cameron/future apparatus validation |
