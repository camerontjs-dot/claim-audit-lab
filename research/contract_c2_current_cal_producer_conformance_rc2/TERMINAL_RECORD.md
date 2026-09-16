# Current CAL -> Contract C2 producer conformance RC2 — terminal record

## Disposition

`SUPPORTED_CURRENT_CAL_TO_C2_WITH_RESOLVER_AUTHORITY`

This closes the pre-local scientific blocker `BLOCKED_AT_CAL_TO_CONTRACT_C2_PRODUCER_AUTHORITY` for the exact frozen subjects below. It does not authorize Contract C2 merge/release, Decision release, Contract E production authority, Authorization, or execution.

## Exact execution

- CAL research head: `8204417f478cfbd891499145a7edec5ee33405ad`;
- CAL semantic implementation: `847cc970642bb648dc994b929c2053b5c9d4648c`;
- hard-bound materializer blob: `ef32fa4fca52a2bb7fe2896b378f9b6fdef0dfde`;
- Contract C2 exact head: `b42c827acb0a9fe65353354d709add0e27bab307`;
- independent resolver authority: `1d33e0612befcf8016816197c90c062373796df9`;
- resolver blob: `1a408246fd3bef0758a958ae716b44ea74bc0689`;
- policy digest: `44ecc33519fa8911079595d322f5f0decbf0389af42e153ac32214931798e42c`;
- workflow run: `35053664704`;
- job: `104659194017`;
- artifact: `10430120937`;
- artifact digest: `sha256:57a199bbea8726401f1d6430469b65be08cdc504c74dfd560c56aeead8a3f064`;
- evaluation digest: `sha256:9372282dff0fc68733573d1635411ad1d4af548a2f04bf43d6e95f25b09c9a9e`;
- failures: `[]`.

## Observed cohort

All sixteen previously qualified current-CAL public result classes passed under the independently selected resolver authority.

For every case:

- exact Contract C2 validation passed;
- exact Contract-B reference validation passed;
- policy resolution against exact resolver freeze `1d33e061...` passed;
- producer tuple was exactly current semantic implementation + policy digest + new resolver authority;
- terminal state and basis groups remained semantically unchanged from the predecessor-resolver objects;
- deterministic repeat passed.

The expected C2 result-set IDs and whole-object hashes changed where the resolver-commit binding changed, while proposition semantics, Contract-B binding, terminal public state, participation, relation/role, and basis groups remained unchanged.

## Hostile controls

All required authority attacks were rejected:

- predecessor resolver-commit substitution;
- removal of current CAL resolver row;
- wrong policy digest;
- caller attempt to select a different semantic implementation identity.

## Programme consequence

The exact CAL -> Contract C2 producer-policy authority seam is no longer a blocker for bounded prototype integration testing.

Downstream Decision and whole-pipeline qualification must still rerun against exact C2 objects carrying resolver authority `1d33e061...`, because their exact object identities differ from the predecessor-resolver pressure objects.
