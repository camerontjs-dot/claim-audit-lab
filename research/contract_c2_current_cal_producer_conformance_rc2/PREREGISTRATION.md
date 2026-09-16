# Current CAL -> Contract C2 producer conformance RC2

**Classification:** Draft Research / final producer-authority binding gate.

## Frozen predecessors

CAL producer RC1:

- current semantic implementation `847cc970642bb648dc994b929c2053b5c9d4648c`;
- hard-bound materializer blob `ef32fa4fca52a2bb7fe2896b378f9b6fdef0dfde`;
- workflow run `35053229507`;
- artifact digest `sha256:28e0c1eea76129164135f69388910f32f218101ebb656e131b0e4ddd657cb43b`;
- disposition `SUPPORTED_FOR_APPARATUS_RESOLVER_SUCCESSOR_QUALIFICATION`.

Independent Apparatus resolver qualification:

- candidate resolver authority freeze `1d33e0612befcf8016816197c90c062373796df9`;
- resolver blob `1a408246fd3bef0758a958ae716b44ea74bc0689`;
- Contract C2 head `b42c827acb0a9fe65353354d709add0e27bab307`;
- workflow run `35053521021`;
- artifact digest `sha256:e7c9f2c482f7fa71ff46ee5df03ed407250d47c57149889d1f8fcb1d353717d7`;
- evaluation digest `sha256:ae569fe3dea04b19383585b735b41e08d765be13cdb3d66db858899ed155638e`;
- disposition `SUPPORTED_CURRENT_CAL_C2_RESOLVER_SUCCESSOR`.

## Objective

Prove that the exact current CAL producer can consume the independently selected resolver authority `1d33e061...` and emit C2 objects that pass all structural, Contract-B, producer-policy, and deterministic replay checks without changing CAL semantics or the hard-bound materializer.

This closes the specific pre-local blocker `BLOCKED_AT_CAL_TO_CONTRACT_C2_PRODUCER_AUTHORITY` if and only if all preregistered cases pass.

## Frozen cohort

Reuse the exact sixteen RC0/RC1 current-CAL semantic cases without changing expected public states:

1. strict support;
2. strict refutation;
3. two independent supports;
4. support + irrelevant;
5. minimal mixed;
6. alternative-joint mixed;
7. symmetric alternative-joint mixed;
8. four-way mixed;
9. irrelevant-only;
10. measurement-not-applicable;
11. direct-event support;
12. direct-event refutation;
13. negative-event unresolved;
14. support + unresolved;
15. event scope stress;
16. unsupported family.

## Required checks

For every case:

- CAL semantic implementation remains exactly `847cc970...`;
- hard-bound materializer blob remains exactly `ef32fa4f...`;
- emitted `producer.policy_resolver_commit_sha` equals exact independent authority `1d33e061...`;
- exact Contract C2 `b42c827...` validation passes;
- exact Contract-B reference verification passes;
- `verify_policy_resolution()` against resolver entries loaded from a separate checkout of `1d33e061...` passes;
- resolved row is exactly the current-CAL row;
- canonical repeat is byte-identical;
- terminal states and basis groups remain equal to the already-qualified RC1 producer outputs except for the expected resolver-commit-dependent C2 identities/hashes.

## Hostile controls

At minimum:

- predecessor resolver commit `43b571...` substituted into a current object must fail against independent authority `1d33e061...`;
- a candidate-resolver entry set with current row removed must fail;
- wrong policy digest must fail;
- current CAL materializer must still reject caller-selected semantic identity.

## Stop rule

Classify:

- `SUPPORTED_CURRENT_CAL_TO_C2_WITH_RESOLVER_AUTHORITY`;
- `FALSIFIED_CURRENT_CAL_TO_C2_AUTHORITY_BINDING`;
- `APPARATUS_FAILURE`.

Do not patch semantic code, C2 validation, materializer behavior, or resolver contents after reveal inside RC2.
