# Contract C Candidate A producer conformance RC0

**Classification:** Draft Research producer-conformance experiment. This is not a production CAL mutation, Contract C promotion, official version assignment, release, tag, Decision Engine change, Contract E / Authorization change, or execution authority.

## Exact frozen authorities

CAL producer authority under test:

- exact CAL V1 RC1 commit: `a902621e8baea3063dddd7f92ba975aade305464`
- engine blob: `636734fd1341d2ae721ae9697c7ac7652b89eecc`
- relation blob: `e9e9401c92ee11d25a50dbc36e80aeb4c4cd220d`
- existing falsified flat projection blob: `9bc152275759304be03b84014c56bd434549a64a`
- CAL RC1 qualification: `SUPPORTED_BOUNDED_RC1_QUALIFICATION` in Draft PR #105
- decisive predecessor producer falsifier: Draft PR #106, terminal `FALSIFIED`

Apparatus candidate authority:

- Candidate A RC1 exact freeze: `ba5f55b0fb6ca54e0461a688813b66fd81bf8c4c`
- candidate contract blob: `0ab62b7ceea1d56d6bc3b7cf8528769dd440ab7c`
- candidate schema blob: `0de83032e6d989225cf014d9a70035f634a5e003`
- candidate validator blob: `03dbb5b774af523d8e6235bca86b18af5ddad5b0`
- Candidate A RC1 terminal research status: `QUALIFIED_FOR_CAL_PRODUCER_CONFORMANCE_RESEARCH`

Frozen semantic authorities inherited by Candidate A:

- Phase 1 corpus commit: `175246ae16932f2f34a399560d7f76013213bf97`
- Phase 1 corpus blob: `0ff4f66bca00924755d42ed7f944c4dae8d10f66`
- Phase 2 representation freeze: `f5337dedaad045aa290e80f69dc83ac1a0f73436`
- Phase 2 oracle blob: `9f00cd332ad366b878f60d13440af639360928de`
- exact policy digest: `44ecc33519fa8911079595d322f5f0decbf0389af42e153ac32214931798e42c`
- immutable policy-resolver authority: `43b571464734325277374ee81098553fb7c1b944`

## Question

Can the exact frozen CAL RC1 producer boundary derive Candidate A RC1's minimal sufficient basis family from **already-authorized CAL result state** without adding a new semantic or causal judgment?

The decisive materializer may consume only:

- exact immutable `AuditContext`;
- exact frozen `AuditResult` and its `PassageTrace` / `BoundRelation` state;
- the unchanged CAL `compose()` operation for counterfactual subset replay.

After the full `AuditResult` exists, the materializer must **not** rerun measurement, source completion, authority evaluation, relation derivation, retrieval, NLI, or any learned/scalar decision procedure.

This experiment also tests whether exact Candidate A RC1 can represent the current CAL V1 public terminal surface needed by the bounded convergence decision. Structural candidate validity is not sufficient if a legitimate CAL result must be relabelled or compressed into a different public reason.

## Materialization hypothesis

For a completed proposition result, define the public terminal state from CAL-owned state only:

- `SUPPORTED` -> `supported / categorical_support`;
- `CONTRADICTED` -> `contradicted / categorical_refutation`;
- `NOT_CHECKABLE + MIXED_RELATIONS` -> `not_checkable / MIXED_RELATIONS`;
- `NOT_CHECKABLE + RELATION_UNRESOLVED` with at least one exact `UNRESOLVED` bound relation -> `not_checkable / unresolved_categorical_relation`;
- `NOT_CHECKABLE + RELATION_UNRESOLVED` with no exact unresolved relation -> `not_checkable / no_deciding_relation`.

No mapping is preregistered for a distinct top-level CAL failure such as `UNSUPPORTED_SEMANTIC_FAMILY`. If Candidate A cannot preserve such a legitimate V1 public reason without relabelling it as one of the six RC1 reasons, that is a representation falsifier, not permission to silently compress it.

For the representable cases, enumerate subsets of already-derived passage traces, replay only frozen `compose(context, subset)`, and retain the inclusion-minimal subsets whose **public terminal state** equals the full result. The resulting family is the proposed `basis_groups` normal form. The union of the groups determines causal participants; every other retained participant is residual.

## Preregistered positive controls

The exact producer/materializer must recover these current-CAL states:

1. single support -> `{{S1}}`;
2. single refutation -> `{{R1}}`;
3. two independently sufficient supports -> `{{S1},{S2}}`;
4. two independently sufficient refutations -> `{{R1},{R2}}`;
5. support + irrelevant/non-polarized residual -> `{{S1}}` with `N1` residual;
6. minimal mixed -> `{{S1,R1}}`;
7. CAL #106 alternative-joint mixed -> `{{S1,R1},{S2,R1}}`;
8. symmetric alternative-joint mixed -> `{{S1,R1},{S1,R2}}`;
9. four-way mixed generalization -> `{{S1,R1},{S1,R2},{S2,R1},{S2,R2}}` as a non-promotion generalization pressure control;
10. irrelevant-only / no deciding relation -> empty causal family with retained residual non-polarized evidence;
11. direct-event-order support and refutation must derive the same basis semantics without strict-comparison-specific logic;
12. direct-event-order reporting/scope refusal must remain completed `not_checkable` with no invented deciding basis;
13. repeated materialization of the same exact producer state must produce byte-identical canonical Candidate A objects and the same local result identity.

Where a case corresponds to a frozen Phase 2 specimen, its reconstructed terminal semantics and basis family must match the exact frozen Phase 2 oracle rather than a hand-edited post-result expectation.

## Decisive falsifiers

### F1 — new semantic judgment is required

If the claimed basis family cannot be derived from the frozen result/traces plus unchanged `compose()` alone and requires rerunning measurement, source completion, authority or relation derivation, the materialization hypothesis is falsified.

### F2 — #106 causal overstatement survives

For `S1 SUPPORTS`, `S2 SUPPORTS`, `R1 REFUTES`, the derived family must be exactly `{{S1,R1},{S2,R1}}`. Flat `{{S1,S2,R1}}` or one selected pair is false.

### F3 — symmetry failure

For `S1 SUPPORTS`, `R1 REFUTES`, `R2 REFUTES`, the derived family must be exactly `{{S1,R1},{S1,R2}}`.

### F4 — residual laundering

Irrelevant/non-deciding retained evidence must remain non-polarized residual when it is not in any minimal sufficient basis. It must not become support/refutation or causal merely to satisfy candidate coverage rules.

### F5 — weak flat control is not killed

The frozen predecessor heuristic / equivalent weak flat-all-causal control must fail at least the alternative-joint case for the intended causal reason. If the apparatus cannot distinguish the target materializer from that weak strategy, the result is `INCONCLUSIVE`.

### F6 — Candidate A structural validity hides semantic mismatch

A candidate object that validates structurally but disagrees with the frozen semantic oracle or CAL's exact public terminal state is a producer-conformance failure.

### F7 — legitimate current V1 public result is unrepresentable

Exercise the exact current `UNSUPPORTED_SEMANTIC_FAMILY` fail-closed producer result. If Candidate A RC1 cannot encode that distinct CAL-owned public reason without dropping or relabelling it, exact RC1 is falsified as the complete current producer surface. This falsifier does not by itself falsify basis groups as the causal representation.

## Static apparatus controls

The workflow must verify the exact frozen CAL source blobs and exact Candidate A RC1 blobs before evaluation.

The research-only materializer source must be mechanically checked to contain no imports/calls to measurement, source completion/authority, relation derivation, the legacy v0.5 engine, or the old Contract C projector. `compose()` is the only CAL semantic operation permitted after receipt of an `AuditResult`.

No `src/**` file may change from exact CAL RC1.

## Primary dispositions

- `SUPPORTED FOR PROMOTION`: all decisive controls pass, including the complete current-V1 public terminal surface exercised here. This authorizes only the next Contract C research gate, not production promotion.
- `FALSIFIED`: any decisive semantic/materialization/representation falsifier fires while the apparatus remains valid.
- `INCONCLUSIVE`: the apparatus, frozen authority, or weak-control discrimination is invalid or insufficient.
- `SUPERSEDED`: a pinned producer or Candidate A authority changes before disposition.

## Nonclaims

A supported result would not establish universal CAL-family coverage, independent-consumer conformance, a production Contract C version, SemVer class, Decision Engine production support, Contract E / Authorization, or operational execution. Prior unresolved/non-polarized causal evidence from CAL #99/#100 remains inherited evidence unless separately materialized by this exact producer; this experiment does not silently reclassify those historical states as current RC1 outputs.