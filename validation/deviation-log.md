# Validation Deviation Log

status: closed for v0.2 engineering release; research-use gates recorded; three entries
opened 2026-08-22 by a qualification pass over the v2 branch
last_updated: 2026-08-22

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

## 2026-08-22 qualification pass over the v2 branch

The experimental v2 decision layer was run against this package before merge. It changes no
shipped-engine file, is reachable from no CLI command, and alters no dependency, so **no
revalidation trigger in `qualification-plan.md` fires** and the v0.2 IQ/OQ/PQ records are not
invalidated by it. It does add 486 statements to `src/`, which puts it inside CAL-REQ-054.

That check failed on arrival (DEV-006, now closed). The pass also found two pre-existing
currency gaps in the package itself (DEV-007, DEV-008), which are recorded rather than fixed:
both need a release verification run this pass could not perform.

## Log

| ID | Date | Reference | Area | Description | Impact | Decision | Rationale | Owner/status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DEV-000 | 2026-04-30 | validation package | package setup | Placeholder row created before protocol execution. | none | closed | IQ/OQ/PQ-inspired records replaced the placeholder state with current evidence. | Codex/closed |
| DEV-001 | 2026-06-13 | future validation gate | research-use calibration | Blind human calibration is `0/98` completed. Qualification requires coarse-label agreement >=80%, Cohen's kappa >=0.60, adverse-claim recall >=85%, and per-condition adverse-rate error <=10 percentage points. | The tool must not be presented as a calibrated research measurement instrument until this gate is complete. | gate before research use | v0.2 validates deterministic engineering behavior; human verdicts remain primary, and CAL remains exploratory if any calibration bar is missed. | Cameron/open research-use gate |
| DEV-002 | 2026-05-04 | future validation gate | real data fixtures | Public validation uses checked-in fictional examples, not real-world production data. | Representative behavior is visible, but production or real-case behavior is not claimed. | gate before real data use | Public portfolio validation should avoid private or sensitive materials; real-data fixture qualification requires a separate intended-use decision. | Cameron/future real-data validation |
| DEV-003 | 2026-06-13 | future validation gate | apparatus qualification | The synthetic retrieval, review, refinement, finalize, and CAL round trip passes, but retrieval quality and human evidence review are not calibrated on real work. | The engineering handoff is verified, but apparatus measurement validity is not claimed. | gate before qualified apparatus use | The v0.2 round trip proves component compatibility; research measurement still depends on DEV-001 and intended-use fixture qualification. | Cameron/open apparatus gate |
| DEV-004 | 2026-06-13 | sealed pilot replay | unclassified boundary | The v0.2 replay returns 56 of 98 claims as `not_checkable` under the sole classifier. | Condition-level rates differ materially from v0.1 and cannot be interpreted as improved or degraded accuracy without blind labels. | accepted engineering behavior; calibration required | Preserving unclassified claims is safer than forcing a support verdict, but classifier adequacy must be judged against blind human labels. | Cameron/open calibration review |
| DEV-008 | 2026-08-22 | `validation/iq-installation.md`, `validation/oq-operational.md`, `validation/pq-performance.md`, `validation/README.md` | package currency | The validation package is stamped `verified for v0.2 engineering release`, `last_updated: 2026-06-13`. IQ-010 records the version as `0.2.0` and the dependency boundary as excluding `rich`; the tree is `0.4.0`, the default engine is `v1-retrieve-entail`, and the decision layer is `cal-rules-v1.13.0`. The OQ record cites "the 213-test suite"; the suite now collects 1,085. IQ-004 expects `--help` to show `audit` and `demo`; the CLI now also carries `audit-bundle`, `calibrate`, and `explain`. | Every IQ and OQ row reads `verified` against evidence two releases old, which is the exact condition the deviation rules name ("a matrix row is marked `verified` without current evidence"). The v0.2 findings may well still hold — the point is that nothing in the tree shows they were re-checked. | open | Pre-existing; found by running this package against the current tree rather than by any v2 change. Re-running IQ/OQ/PQ for `0.4.0` needs network access to the pinned models and a clean-wheel build, neither of which this pass could perform. Recorded rather than silently re-stamped. | Cameron/open |
| DEV-007 | 2026-08-22 | `docs/verification.md` | traceability | `docs/verification.md` is cited 18 times as the evidence reference for IQ and PQ steps and in the validation package map (IQ ×6, PQ ×9, OQ ×1, `validation/README.md` ×2). The file is not in the tree. | Protocol steps recorded `verified` point at a document a reviewer cannot open, so the evidence chain for IQ-001/003/004/007/008/009 and the PQ record is not followable from a clean clone. | open | Pre-existing. The README's own Verification section carries a dated results table that covers much of the same ground, so the content largely exists — under a different path than every protocol row names. Either restore the document or repoint the rows; both need the release verification figures. | Cameron/open |
| DEV-006 | 2026-08-22 | `feat/v2-epistemic-pipeline` @ `b7254e7` | engineering gate (CAL-REQ-054) | The v2 branch added 439 statements to `src/` behind 19 tests. Measured branch coverage was 74% (`interval_algebra.py`) and 79% (`impl/pipeline_rules.py`) against the ≥95% gate, dropping the `src/` total from 93% to 91% under identical conditions. The resolution table's `R1`, `R4`, `R5`, `R6` and `R8`, the whole `qualify_union` path, and `V2Verdict.as_dict` had no test at all. | A decision layer whose precedence table is its policy shipped with that table unpinned, and the branch would have taken the repo's headline coverage figure below its own gate. | corrected | 41 tests added across `test_interval_algebra.py`, `test_pipeline_rules.py` and a new `test_pipeline_rules_resolution.py`. Both v2 modules are now at **100%** branch coverage and the `src/` total sits above the pre-branch baseline measured the same way. Coverage here is measured with the pinned-model tests network-blocked, which suppresses the total by ~2 points on every tree equally; the gate figure must still be read from a CI run. | Claude/closed |
| DEV-005 | 2026-08-20 | `outputs/2026-08-19-construction-gold/` | sealed output integrity | The construction-gold directory was re-run in place, overwriting its sealed `audit_results.json` and all 33 traces without regenerating `SHA256SUMS`. 34 of 39 files now fail their manifest. The overwritten outputs came from a working tree partway through the `v1.11.0` work and are not attributable to any released rules version. | The `22/33` figure published from that directory lost its provenance chain; the outputs backing it cannot be recovered. Inputs (`corpus.json`, `gold.json`) verify against the original manifest and are intact. | corrected; manifest left failing on purpose | Re-sealing would make the manifest agree with contents no rules version accounts for, turning a visible failure into a silent one. The corpus was re-run on the shipped `cal-rules-v1.12.0` into `outputs/2026-08-20-construction-gold-v1.12.0/` (sealed 38/38) and the published figure updated to `26/33`. `scripts/audit_construction_gold.py` gained `--corpus` and `--out` so a re-run cannot overwrite a sealed directory. | Cameron/closed |
