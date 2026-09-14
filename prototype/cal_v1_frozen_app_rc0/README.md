# CAL V1 Frozen App Prototype RC0

Classification: Research Infrastructure / frozen testing prototype. Not a production release, not a Contract C promotion, and not operational authorization.

## Decision sentence

Freeze the exact qualified CAL V1 RC1 semantic implementation at `a902621e8baea3063dddd7f92ba975aade305464` behind a minimal deterministic packet runner so real typed claims can be exercised without changing CAL semantics or importing unresolved downstream authority.

## Semantic authority

The prototype semantic authority is exactly:

`a902621e8baea3063dddd7f92ba975aade305464`

The prototype MUST NOT modify the qualified semantic core. In particular, changes to these surfaces invalidate RC0 rather than becoming part of it:

- `src/claim_audit_lab/cal_v1_candidate/engine.py`
- `src/claim_audit_lab/cal_v1_candidate/relations.py`
- `src/claim_audit_lab/cal_v1_candidate/measurements.py`
- `src/claim_audit_lab/cal_v1_candidate/authority.py`
- `src/claim_audit_lab/cal_v1_candidate/authority_validation.py`
- `src/claim_audit_lab/cal_v1_candidate/models.py`

The runner may reuse the already-qualified exact packet-to-context parser in `cal_v1_candidate.cli` and the existing report renderer.

## Input

One JSON packet representing one typed proposition and one admitted evidence world:

- `original_claim`;
- proposition identity, text hash, semantic family and typed fields;
- exact Contract B version / bundle identity / bundle hash;
- aperture observation;
- admitted passages with source, passage, text and content hashes.

RC0 does not perform retrieval and does not infer proposition typing from arbitrary prose. Those are upstream responsibilities.

## Output

The runner emits:

1. JSON result receipt with exact prototype and semantic implementation identities;
2. original claim / proposition identity;
3. evidence-world and audit-context identities;
4. aperture observation;
5. CAL conclusion and localized failure code;
6. per-passage measurement / authority / categorical-relation trace state;
7. non-deciding passage IDs;
8. explicit downstream stop states.

## Downstream stop state

RC0 deliberately does **not** emit Contract C. The exact qualified CAL producer path now targets Candidate A RC2 / proposed Contract C 2.0, while the older maintained `cal_v1_candidate.projection` still emits the historical `research-non-deciding-rc0` shape.

Until canonical Contract C 2 authority is frozen into the app profile, RC0 records:

`contract_c_handoff.state = not_emitted`

This is a safety boundary, not a missing CAL result.

RC0 also records that Authorization was not evaluated and automatic action is not allowed.

## Study use

The intended next use is a fixed 10-claim smoke cohort followed, only after an explicit review, by a larger frozen real-claim cohort. No semantic tuning is permitted mid-cohort. Failures, abstentions, unsupported semantic families, malformed packets and operator corrections are retained as data.

The prototype is suitable for learning about:

- supported / contradicted / not-checkable distributions;
- semantic-family coverage;
- failure localization;
- relation and authority traces;
- evidence consumption;
- aperture observations;
- deterministic replay;
- human disagreement and correction burden.

It does not establish retrieval completeness, automatic proposition typing, universal semantic coverage, Contract C release readiness, Decision policy, Authorization, or execution safety.
