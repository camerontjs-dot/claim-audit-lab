# CAL RC1 Receipt/Replay Evaluator Freeze Record

## Freeze basis

Production baseline: `e90f301cf6ca02c0c77b6e88c3b08f8b93b9a36a`.

Predecessor RC0B evaluator: `5d880110e39d0450af346fea91074eebaa2c2f96`.

The acceptance apparatus was completed before the candidate module existed. The apparatus content immediately before this record was commit:

`8c97165df5f8180f142f1014867660219d1c7b28`

Frozen apparatus blobs:

- acceptance specification: `677fbe44e02cd961109fb3c537e8c9b7285f354e`;
- frozen cases/regression manifest: `c0a78f5b715539f554072405ae88ab256394aa3d`;
- executable evaluator: `504143d819c06492bde1ffe79de1aed11317e4d9`;
- pytest acceptance entry point: `371b37f37de8799f57060cbe4353c84548df0bba`.

This record adds no new candidate expectation. Its commit is the evaluator-freeze identity for RC1.

## Pre-candidate self-check

The executable evaluator's intentionally weak control was run with `--self-test-weak` before candidate implementation.

Observed result: rejected.

Failed gates:

- `assessment_ladder`;
- `participation_reconstruction`;
- `policy_counterfactual`;
- `replay_derived_causal_basis`;
- `missing_required_state_fails_closed`.

The weak control therefore cannot clear the frozen gate by substituting source trust for explicit assessment state, defaulting missing receipt state, or echoing causal necessity without intervention.

## Candidate aperture

At this freeze point `docs/research/rc1_receipt_replay_candidate.py` does not exist on the branch. Candidate implementation begins only after this freeze record is committed.

## Stopping rule

If the bounded sidecar clears the frozen ten-gate evaluator with all frozen v1 trace identities, semantic measurements, and verdicts preserved, stop. No staged candidate is authorized for comparison.

If the frozen apparatus proves defective in the decisive run, preserve the deviation. Do not silently alter the apparatus and treat the repaired run as the same frozen experiment.
