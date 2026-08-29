# CAL Epistemic Methodology RC1 — Frozen Production-Facing Receipt/Replay Acceptance Specification

## Status

Research-only acceptance specification. This file freezes the gate before candidate implementation.

Production baseline: `e90f301cf6ca02c0c77b6e88c3b08f8b93b9a36a`.

Predecessor: CAL PR #31 / RC0B, frozen evaluator `5d880110e39d0450af346fea91074eebaa2c2f96`.

## Question

Can a research-only producer around current CAL v1 emit the minimum typed epistemic receipt/replay state supported by RC0B while preserving the existing v1 trace, semantic measurements, and production verdict exactly?

## Protected surfaces

The candidate must not modify:

- `src/claim_audit_lab/v1/pipeline.py`;
- `src/claim_audit_lab/v1/models.py`;
- semantic measurement implementations;
- verdict/rule implementations;
- Contract B intake;
- Contract C implementation/schema/export surface;
- model IDs, thresholds, configs, rules files, release metadata, or historical v2.

The candidate is a research-side sidecar only.

## Frozen candidate interface

The candidate module path is:

`docs/research/rc1_receipt_replay_candidate.py`

It must expose:

```python
def emit_receipt(trace, state, *, replay=None) -> dict:
    ...
```

Inputs:

- `trace`: a JSON-shaped current CAL v1 `AuditTrace` record. It is authoritative for existing measurement and verdict state and must remain unchanged.
- `state`: explicit research-side state owned by this experiment. Required keys are `execution`, `assessments`, `source_facts`, `policy`, and `aggregation`.
- `replay`: optional callable `active_passage_ids -> terminal_result`. It is the only authorized source for exact causal-basis claims.

Output:

```text
{
  "trace": <exact unchanged trace>,
  "receipt": {
    "semantic_measurement_hash": <stable hash>,
    "production_verdict_hash": <stable hash>,
    "execution": ...,
    "assessments": ...,
    "participation": ...,
    "policy": ...,
    "aggregation": ...,
    "causal_basis": ...
  }
}
```

Missing required receipt state must raise explicitly. No silent defaults are allowed.

## Required typed assessment states

The experiment-owned assessment vocabulary is exactly:

- `performed-positive`;
- `performed-adverse`;
- `performed-unknown`;
- `not-performed`;
- `not-applicable`;
- `failed`.

This is research-side state only. It does not modify Contract C 1.0.0.

## Required participation states

Exactly:

- `deciding`;
- `residual`;
- `excluded`;
- `unresolved`.

The producer may derive participation only from explicit assessment state plus the named policy. Source metadata such as trust tier is not itself an assessment.

## Policy semantics for this bounded experiment

Each case supplies a named policy with an explicit `allowed_trust` list. For a passage with an eligibility assessment:

- `performed-positive` + allowed trust => `deciding`;
- `performed-positive` + disallowed trust => `residual`;
- `performed-adverse` => `excluded`;
- `performed-unknown`, `not-performed`, or `failed` => `unresolved`;
- `not-applicable` => `residual`.

These rules are frozen research-harness semantics, not production CAL semantics.

## Causal-basis rule

If `replay` is absent, exact causal form must be `unavailable`.

If `replay` is present, the producer may call it on the baseline deciding set and one-at-a-time removal sets. A passage may be named `necessary` only when removing that passage changes the replay terminal result. Otherwise it must not be called necessary.

No co-sufficiency or broader causal form is inferred by this experiment.

## Frozen gate

The candidate clears only if all ten properties pass:

1. **Measurement stability:** semantic measurement hash is unchanged by receipt production and by irrelevant metadata mutation.
2. **Verdict stability:** every trace in the frozen regression manifest is returned unchanged and its verdict hash is unchanged.
3. **Assessment ladder:** all six explicit assessment states round-trip distinctly.
4. **Participation reconstruction:** deciding/residual/excluded/unresolved are all reconstructable under the frozen policy semantics.
5. **Policy counterfactual:** with trace/evidence/semantic measurement fixed, changing only named policy changes participation where specified, while semantic hash stays fixed.
6. **Execution distinction:** outer execution failure remains distinct from an epistemic non-decision/completed result.
7. **Unresolved distributed evidence:** unresolved aggregation remains explicit and no composition result is invented.
8. **Replay-derived causal basis:** necessary basis is emitted only where removal replay changes terminal result; without replay exact basis is unavailable.
9. **Irrelevant metadata invariance:** metadata declared irrelevant by the case does not change semantic hash, assessment state, or participation.
10. **Fail-closed receipt:** missing any required top-level receipt state raises rather than defaulting.

## Weak control

The evaluator contains an intentionally weak producer that:

- derives eligibility from source trust instead of preserving explicit assessment state;
- silently defaults missing state;
- declares deciding evidence causally necessary without replay.

The frozen gate must reject it for those epistemic defects. A harness that lets it pass is defective.

## Frozen regression set

The exact existing v1 trace fixtures and Git blob identities are listed in `docs/research/rc1-receipt-replay-cases.json`. The evaluator verifies those identities before using them.

## Stopping rule

If the bounded sidecar clears all ten properties while the frozen production trace/measurement/verdict surfaces remain unchanged, stop. Do not build a staged pipeline candidate.

If it fails, record the exact state that cannot be observed or reconstructed. Only that failure can justify a stronger decomposition experiment.

## Non-authorization

A passing RC1 result does not authorize production merge, CAL v2, Contract B/C changes, Evidence Bundler changes, Decision Engine changes, threshold/model/config changes, or a release/version change.
