# RC8C — Admitted-Evidence Source Anchor Falsifier

## Parent state

RC8B is frozen at candidate blob `edf84bb5aae0dd217e3f780e7a49767440b7c1e5` and passed its 50-case prospective bound-receipt cohort with zero unsafe warranted atoms.

RC8B established internal same-subject receipt consistency. It did not establish that the opaque subject token is anchored to the admitted evidence source identified by `raw_source_id`.

## Scientific question

Can the frozen RC8B candidate distinguish an internally consistent authority bundle that belongs to one admitted raw source from the same bundle attached to a different raw-source identity?

## Positive control

Use one fully warranted RC8B receipt bundle for synthetic source A.

All semantic proposal values, field warrants, operator jurisdiction, assertion state, composition/aperture requirements, source span, instrument IDs, and reader counts remain fixed.

## Frozen mutations

1. **Raw-source substitution:** change only `raw_source_id` from source A to source B. Keep the entire authority-subject bundle unchanged. Expected: `REJECTED / AUTHORITY_EVIDENCE_SOURCE_MISMATCH`.
2. **Missing raw-source binding:** remove `raw_source_id` while leaving `evidence_admitted = true` and all authority receipts otherwise valid. Expected: `UNRESOLVED / AUTHORITY_EVIDENCE_SOURCE_BINDING_UNRESOLVED`.
3. **Positive control:** unchanged source A bundle. Expected: `WARRANTED / ALL_REQUIRED_WARRANT_ESTABLISHED`.

## Hard falsifier

The frozen RC8B candidate is insufficient as an evidence-to-authority binding gate if either raw-source mutation is `WARRANTED`.

`unsafe_warranted_atoms` must be zero to survive this falsifier.

## Interpretation rule

A failure localizes a missing evidence-source anchor. It does not invalidate RC8B's demonstrated partial-receipt consistency behavior.

If falsified, preserve RC8B unchanged. A successor may add only the smallest explicit binding needed to relate the authority subject to the admitted evidence source. Do not repair this with confidence, reader agreement, instrument agreement, or a heuristic parse of arbitrary source text.

## Threat-model boundary

This test checks accidental or structural bundle misattachment. It does not claim cryptographic authenticity, receipt-producer trust, or resistance to an adversary able to rewrite every provenance field consistently.
