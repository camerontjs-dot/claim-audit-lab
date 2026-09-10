# Evidence-World-Bound Temporal Successor — Results

## Classification

Draft Research Infrastructure. This is a successor to two preserved provenance falsifiers. It does not authorize production use, merge, release, tag, promotion, Contract C changes, Decision Engine changes, Contract E, or operational authorization.

## Exact frozen candidate

- candidate freeze before decisive cohort: `10ce0894a56f265434b24963bf0543765c453996`
- `bound_relation.py` blob: `94b44f3b0b2b3f077c17ca55eb944117ffa22b77`
- `bound_projection.py` blob: `77fed3e7a7273b13e6dfb89e0ffee7fce1503c6c`
- failed first projector retained unchanged: `projection.py` blob `57d389f8b39d458388a6aed7c99c620ea165354a`
- Phase-3 relation candidate retained unchanged: freeze `94ea0c7531aeb852520f34bd56393b63a4b5ac75`
- Contract C 1.0 authority: `5fe55f9ed5d0ee9f026ca1b077e9d70ce0487ea1`
- Contract C validator blob: `9c75ccfbf2223578a8d1a7bf0c39673b394fbea4`

## Decisive execution

- run: `34434782626`
- artifact: `10135769621`
- artifact digest: `sha256:4667d7c9328d034f32e92822229f625f8d15acba45dfc51257270b148826f67c`
- disposition: `SUPPORTED_WITH_BOUNDS_AND_CONTRACT_C_PROVENANCE_GAP`

Terminal summary:

```json
{
  "cross_bundle_composition_refused": true,
  "cross_bundle_projection_refused": true,
  "falsifier_failures": [],
  "positive_failures": [],
  "research_disposition": "SUPPORTED_WITH_BOUNDS_AND_CONTRACT_C_PROVENANCE_GAP",
  "same_world_mixed_order_invariant": true,
  "unresolved_contract_c_provenance_gap_preserved": true
}
```

## OBSERVED

### Common evidence-world binding

The successor re-verifies every proof from the original immutable `AuditContext`, reconstructs the event atom from the exact MeasurementReceipt, verifies the atom warrant and proposition binding, re-derives the Phase-3 relation, and exposes:

`(audit_context_sha256, contract_b_version, bundle_id, bundle_hash)`.

Composition rejects any relation whose verified tuple differs.

The two previously successful attacks were repeated against the successor:

- support proof from one bundle + refute proof from another -> refused `COMMON_EVIDENCE_WORLD_MISMATCH`;
- the same cross-world pair presented to the Contract C bound projector -> refused `COMMON_EVIDENCE_WORLD_MISMATCH`.

### Same-world conflict remains available

A new mixed control placed both passages inside one immutable `AuditContext`:

- one passage warranted `SUPPORTS`;
- one passage warranted `REFUTES`;
- both MeasurementReceipts named the same complete available-context set;
- both proofs reverified against the same Contract-B version/id/hash and context SHA;
- composition returned `abstained / mixed_categorical_relations`;
- reversing proof order produced the identical conclusion and Contract C object.

This is stronger evidence than the original Phase-3 mixed case because common evidence-world identity is now an explicit enforced precondition rather than an unstated assumption.

### Stale/forged boundaries fail closed

The successor refused all preregistered mutation controls:

- same bundle ID with changed bundle hash under stale MeasurementReceipt;
- changed passage text/hash under stale MeasurementReceipt;
- stale atom warrant under a fresh different evidence world;
- stale proposition binding under changed exact proposition semantics;
- caller-modified relation record that disagreed with re-derivation;
- measurement/passage substitution;
- cross-bundle composition;
- cross-bundle projection.

The bound projector API has no caller parameter for `contract_b_binding`, `bundle_id`, `bundle_hash`, or `evidence_index`. These values are derived from the verified AuditContext.

### Unchanged Contract C validation

Exact released Contract C 1.0 validation passed for:

- temporal supported;
- temporal contradicted;
- same-world mixed conflict / not-checkable;
- unresolved temporal / not-checkable.

No Contract C schema change was required for those terminal result shapes.

### Contract C provenance compression remains real

The unresolved negative-event relation is semantically warranted as `UNRESOLVED`, but Contract C 1.0 has only `support` and `counterevidence` contribution channels.

The projector therefore does not mislabel the relation. It emits a `state:` terminal basis for `not_checkable`, omits the unresolved relation from evidence contributions, and explicitly records the omitted relation ID in the research projection receipt.

Observed projection status:

`VALID_WITH_PROVENANCE_COMPRESSION`.

This is a bounded information-loss finding, not a validator failure.

## INFERENCE

The evidence supports adding **common evidence-world identity** as a required invariant between authenticated proposition-relative relation derivation and multi-relation composition / Contract C projection.

The smallest supported architecture now is:

`AuditContext -> measurement receipt -> source completion -> atom warrant -> exact proposition binding -> rederived relation -> explicit evidence-world binding -> composition -> Contract C projection`.

A naked Phase-3 relation record is not sufficient input to cross-boundary composition or Contract C projection.

## NOT ESTABLISHED

- arbitrary temporal language;
- negative-event deciding semantics;
- cross-passage temporal inference/transitivity;
- event coreference;
- evidence completeness;
- lossless Contract C representation of unresolved/irrelevant evidence relations;
- Decision Engine conformance for these temporal Contract C objects;
- Contract E / Authorization;
- production authentication/key management;
- production promotion.

## Next gate

Use the exact validated Contract C outputs from this bound successor to test the unchanged maintained Decision Engine. Do not modify Decision policy first. The decisive question is whether the existing Contract C ingress + policy consumes the temporal terminal state without hidden strict-comparison assumptions, while preserving the separate unresolved-provenance compression limitation.
