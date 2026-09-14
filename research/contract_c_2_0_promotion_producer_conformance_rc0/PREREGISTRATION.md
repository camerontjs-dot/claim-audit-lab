# Contract C 2.0 Promotion Producer Conformance RC0

Classification: Draft Research / promotion-gate evidence. Do not merge into production CAL.

## Decision sentence

If exact frozen CAL V1 RC1, using the exact previously qualified RC2 materializer, emits objects that are byte/identity-equivalent under the frozen Candidate A RC2 reference and the exact locally-green Contract C 2.0 promotion head, while preserving the exercised CAL terminal/basis/participant semantics and fail-closed version authority, record `SUPPORTED_C2_PROMOTION_PRODUCER_CONFORMANCE`.

If the production adapter accepts a materially different object, rejects legitimate previously-qualified CAL output, changes canonical bytes/identity, launders an exercised terminal distinction, or requires a new CAL semantic judgment, record `FALSIFIED` and stop Contract C promotion.

Harness/evaluator faults are `INCONCLUSIVE_EVALUATOR_INVALID`, not evidence against RC2.

## Frozen authorities

CAL producer:

- exact CAL V1 RC1: `a902621e8baea3063dddd7f92ba975aade305464`;
- prior exact RC2 materializer blob: `f9b22abff561081fb22ade8d5d7227dbdb870d72`;
- prior CAL producer terminal: `85ff90a40e967309de4293df930c95cdc2936f47` (`SUPPORTED_RC2_PRODUCER_CONFORMANCE`).

Apparatus production candidate:

- Draft promotion PR #98;
- exact locally-green promotion head: `b42c827acb0a9fe65353354d709add0e27bab307`;
- promotion gate run: `34804396671`;
- Python 3.11/3.12/3.13 jobs all successful;
- frozen-reference differential suite: green;
- full Apparatus regression suite: green;
- static hygiene: green;
- public candidate version: `2.0.0`;
- current canonical discovery remains `1.0.0` during pre-merge qualification;
- exact wire profile remains `contract-c-successor-candidate-a-rc2-research`.

Frozen RC2 source lineage retained inside that head:

- wire spec blob `960df40619f0fbeb630c4ea8b1042ed3a293a7a3`;
- schema blob `45ebaa1e5b7342422b4d6a19f897e72de4bb148f`;
- RC1 reference validator blob `03dbb5b774af523d8e6235bca86b18af5ddad5b0`;
- RC2 reference validator blob `ad5ed3ac71a8f8680188beb363c9d952c9922b15`.

## Study type and unit

Study type: regression / promotion conformance.

Unit of analysis: one legitimate CAL result projected into one Contract C handoff object.

This is not a semantic-quality study and does not re-evaluate whether CAL's underlying judgment is correct.

## Aperture and non-use

The evaluator may use:

- exact CAL V1 RC1 public/runtime APIs already used by the prior producer gate;
- exact frozen `materialize.py` in this experiment;
- exact files from Apparatus promotion head `b42c827...`;
- the frozen RC1/RC2 reference validator source copied inside that promotion head;
- explicit test fixtures created before scoring.

It must not:

- edit the materializer after results are visible;
- import old CAL v0.5 fallback/projector behavior;
- infer new relation semantics;
- change `compose()`;
- change the Contract C production candidate;
- make C2 canonical in global discovery;
- treat Decision Engine policy or Authorization as Contract C semantics.

## Required controls

Exercise at minimum:

1. single support;
2. single refutation;
3. two independent supports;
4. support plus neutral residual;
5. minimal mixed support/refute;
6. alternative-joint mixed `(S1 OR S2) AND R1`;
7. symmetric alternative-joint mixed `S1 AND (R1 OR R2)`;
8. four-way alternative mixed;
9. completed no-deciding result;
10. direct-event-order support, refutation, and reporting-scope no-deciding result;
11. exact `UNSUPPORTED_SEMANTIC_FAMILY` result.

For every legitimate case require:

- the unchanged materializer uses exact CAL result state;
- production C2 validation succeeds;
- exact bound Contract-B evidence references validate;
- exact producer/policy/resolver identity validates against the preregistered resolver entry;
- frozen RC2 reference validation succeeds;
- production and frozen reference canonical objects are equal;
- canonical bytes are equal;
- local result-set identity is equal;
- whole-object SHA-256 is equal;
- emitted basis groups equal CAL's deterministic compose-only minimal basis derivation;
- emitted terminal state equals CAL's public terminal state.

Additional discriminators:

- the old flat alternative-joint strategy must disagree with the correct minimal basis family;
- replacing exact unsupported-family reason with `no_deciding_relation` must change result identity/object hash;
- public `2.0.0` compatibility version must remain external to the frozen wire profile;
- global production discovery must still report C1 during this pre-merge gate.

## Stop conditions

Stop and preserve `FALSIFIED` on any semantic/identity mismatch attributable to the exact production candidate.

Stop and preserve `INCONCLUSIVE_EVALUATOR_INVALID` if the evaluator cannot prove it tested the exact CAL/materializer/Apparatus authorities above.

Do not patch CAL semantics or Contract C architecture inside this gate.
