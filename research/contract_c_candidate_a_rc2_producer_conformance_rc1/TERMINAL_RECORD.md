# Contract C Candidate A RC2 producer conformance RC1 terminal record

## Terminal disposition

**`SUPPORTED_RC2_PRODUCER_CONFORMANCE`**

Exact frozen CAL V1 RC1 can project the tested legitimate current result state into exact Candidate A RC2 without adding a new semantic/causal judgment at the exporter boundary.

This satisfies the bounded producer-conformance gate only. Independent-consumer conformance remains unresolved. No production promotion, official Contract C version, merge, release, Decision production change, Contract E / Authorization, or execution is authorized.

## Exact authorities

CAL:
- exact V1 RC1 `a902621e8baea3063dddd7f92ba975aade305464`
- engine blob `636734fd1341d2ae721ae9697c7ac7652b89eecc`
- relation blob `e9e9401c92ee11d25a50dbc36e80aeb4c4cd220d`

Apparatus:
- exact Candidate A RC2 freeze `3e1c44d6e264e2baa37324b66f78165b15a927f1`
- validator blob `ad5ed3ac71a8f8680188beb363c9d952c9922b15`
- schema blob `45ebaa1e5b7342422b4d6a19f897e72de4bb148f`
- qualification record commit `13c34ab04da9b332f8d6db11e2d77b389172ba86`
- qualification disposition `QUALIFIED_FOR_CAL_PRODUCER_CONFORMANCE_RESEARCH`

Frozen experiment:
- preregistration blob `4f1026b5d6e230611056dab2a24586280d46300a`
- compose-only materializer blob `f9b22abff561081fb22ade8d5d7227dbdb870d72`
- evaluator blob `510618e62755270888d4f342e18106ea5d49385b`
- freeze receipt commit `da9725bb6d06fde7c150d3353275b16d66ca575c`
- decisive workflow head `136acc646e8c6fbc07020b87dd76b2e3a5c49d97`

## Decisive execution

- Actions run `34799540259`
- job `103839229690`
- Actions conclusion `success` as apparatus execution
- artifact `10330289949`
- artifact digest `sha256:906ff08b9eb7892727c283952d04348951ac33b368226dd3c95a3abc753aa5f6`
- extracted `EVALUATION.json` SHA-256 `8f3492a34a8fa09a713e796404af6eff265d809a50a92b0a4ea4d354af2a4785`
- failures: none

## Supported observations

All preregistered producer controls passed:

- inherited current-CAL / frozen Phase-2 controls matched;
- deterministic repeated materialization;
- CAL #106 alternative-joint basis exactly `{{S1,R1},{S2,R1}}`;
- symmetric alternative-joint basis exactly `{{S1,R1},{S1,R2}}`;
- weak flat-all-causal strategy killed;
- direct-event-order support/refute/no-deciding controls preserved;
- exact current CAL `UNSUPPORTED_SEMANTIC_FAMILY` result preserved without relabelling;
- weak unsupported->no-deciding alias killed;
- exact RC1 predecessor still rejects the unsupported-family reason.

Observed interpretation:

- `basis_groups_derived_without_new_semantic_judgment = true`;
- `unsupported_family_preserved_without_relabelling = true`;
- `producer_gate_satisfied = true`;
- `independent_consumer_gate_satisfied = false`;
- `production_promotion_authorized = false`.

## Unsupported-family exact output

Exact CAL result:

`NOT_CHECKABLE / UNSUPPORTED_SEMANTIC_FAMILY`

Exact RC2 public projection:

- verdict `not_checkable`;
- reason `UNSUPPORTED_SEMANTIC_FAMILY`;
- empty basis groups;
- retained U1 and U2 as `non_polarized / residual`;
- result-set ID `sha256:b86deceefd16272dee94687948ead26fe0fb69b67eb5a7e3f6c854f393923260`;
- whole-object SHA-256 `sha256:71434a260eeb1af0fb40937031f76aed39fb9b27a47a7f0f9b19f4a4e4b45aee`.

## Epistemic boundary

The evidence now supports the narrower diagnosis that CAL #106 exposed an exporter causal-flattening defect plus a public causal-grammar insufficiency in the old successor, not a need for CAL to create new semantic authority at export time. Candidate A RC2's basis groups can be derived mechanically from already-authorized CAL relations/composition in the tested fragment.

The remaining programme gate is an independent consumer of a frozen RC2 handoff. Supervisor-context reimplementation is insufficient for an independence claim. This record must remain Draft Research.