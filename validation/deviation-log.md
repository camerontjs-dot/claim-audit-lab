# Validation Deviation Log

status: closed for v0.2 engineering release; research-use gates recorded
last_updated: 2026-08-20

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
- a sealed output directory is modified without regenerating its manifest

## v0.2 Outcome

No open engineering-release failures remain. The entries below either closed setup
issues or record gates that must be completed before real data, sensitive materials,
production-like drafts, or research measurement runs.

DEV-005 (2026-08-20) is closed but is left visible rather than folded away: it is the one
case where this project's own integrity mechanism caught a real loss.

## Log

| ID | Date | Reference | Area | Description | Impact | Decision | Rationale | Owner/status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DEV-000 | 2026-04-30 | validation package | package setup | Placeholder row created before protocol execution. | none | closed | IQ/OQ/PQ-inspired records replaced the placeholder state with current evidence. | Codex/closed |
| DEV-001 | 2026-06-13 | future validation gate | research-use calibration | Blind human calibration is `0/98` completed. Qualification requires coarse-label agreement >=80%, Cohen's kappa >=0.60, adverse-claim recall >=85%, and per-condition adverse-rate error <=10 percentage points. | The tool must not be presented as a calibrated research measurement instrument until this gate is complete. | gate before research use | v0.2 validates deterministic engineering behavior; human verdicts remain primary, and CAL remains exploratory if any calibration bar is missed. | Cameron/open research-use gate |
| DEV-002 | 2026-05-04 | future validation gate | real data fixtures | Public validation uses checked-in fictional examples, not real-world production data. | Representative behavior is visible, but production or real-case behavior is not claimed. | gate before real data use | Public portfolio validation should avoid private or sensitive materials; real-data fixture qualification requires a separate intended-use decision. | Cameron/future real-data validation |
| DEV-003 | 2026-06-13 | future validation gate | apparatus qualification | The synthetic retrieval, review, refinement, finalize, and CAL round trip passes, but retrieval quality and human evidence review are not calibrated on real work. | The engineering handoff is verified, but apparatus measurement validity is not claimed. | gate before qualified apparatus use | The v0.2 round trip proves component compatibility; research measurement still depends on DEV-001 and intended-use fixture qualification. | Cameron/open apparatus gate |
| DEV-004 | 2026-06-13 | sealed pilot replay | unclassified boundary | The v0.2 replay returns 56 of 98 claims as `not_checkable` under the sole classifier. | Condition-level rates differ materially from v0.1 and cannot be interpreted as improved or degraded accuracy without blind labels. | accepted engineering behavior; calibration required | Preserving unclassified claims is safer than forcing a support verdict, but classifier adequacy must be judged against blind human labels. | Cameron/open calibration review |
| DEV-005 | 2026-08-20 | `outputs/2026-08-19-construction-gold/` | sealed output integrity | The construction-gold directory was re-run in place, overwriting its sealed `audit_results.json` and all 33 traces without regenerating `SHA256SUMS`. 34 of 39 files now fail their manifest. The overwritten outputs came from a working tree partway through the `v1.11.0` work and are not attributable to any released rules version. | The `22/33` figure published from that directory lost its provenance chain; the outputs backing it cannot be recovered. Inputs (`corpus.json`, `gold.json`) verify against the original manifest and are intact. | corrected; manifest left failing on purpose | Re-sealing would make the manifest agree with contents no rules version accounts for, turning a visible failure into a silent one. The corpus was re-run on the shipped `cal-rules-v1.12.0` into `outputs/2026-08-20-construction-gold-v1.12.0/` (sealed 38/38) and the published figure updated to `26/33`. `scripts/audit_construction_gold.py` gained `--corpus` and `--out` so a re-run cannot overwrite a sealed directory. | Cameron/closed |
