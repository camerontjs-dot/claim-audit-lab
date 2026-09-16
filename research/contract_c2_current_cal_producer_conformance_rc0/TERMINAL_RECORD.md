# Current CAL -> Contract C2 producer conformance RC0 — terminal record

## Disposition

`SUPPORTED_FOR_APPARATUS_RESOLVER_SUCCESSOR_QUALIFICATION`

This is producer-compatibility evidence only. It is not independent resolver authority, Contract C2 promotion/release authority, Decision qualification, Contract E authority, Authorization, or execution permission.

## Exact execution

- CAL research head: `0915e6a1d8e7241900e8403c64d5c0af493298be`
- CAL tree: `4fde2ad1b479709722c25672cfbb4958e109b770`
- semantic implementation: `847cc970642bb648dc994b929c2053b5c9d4648c`
- Contract C2 exact head: `b42c827acb0a9fe65353354d709add0e27bab307`
- predecessor resolver: `43b571464734325277374ee81098553fb7c1b944`
- current materializer blob: `1824b48fc979f24219acf3edf76a2477d87eab22`
- policy digest: `44ecc33519fa8911079595d322f5f0decbf0389af42e153ac32214931798e42c`
- workflow run: `35053024929`
- job: `104657282295`
- artifact: `10428814215`
- artifact digest: `sha256:4cf9dbb90bab6a7eae9468bda198f22c34594388ba1af3adb1154c722b42da18`
- `EVALUATION.json` digest: `sha256:8a4c3aaa9c1e83e98cd3cf48ba26a028b0a89eb372258c1617955b3b53e08a01`
- failures: `[]`

## Observed coverage

Sixteen preregistered current-CAL result classes were accepted by the exact Contract C2 validator and exact Contract-B reference checks:

- strict support and refutation;
- independent support alternatives;
- support plus retained irrelevant evidence;
- minimal mixed support/refutation;
- `(S1 OR S2) AND R` alternative-joint mixed basis;
- `S AND (R1 OR R2)` symmetric alternative-joint mixed basis;
- four-way mixed alternatives;
- irrelevant-only `NO_DECIDING_RELATION`;
- `MEASUREMENT_NOT_APPLICABLE` with no relation;
- direct-event support and refutation;
- negative-event `UNRESOLVED`;
- support plus unresolved, with unresolved correctly preventing a support winner;
- narrator/scope measurement miss;
- unsupported semantic family.

For every case:

- C2 structural validation passed;
- exact Contract-B world references passed;
- producer identity remained `847cc970...`;
- policy digest remained `44ecc335...`;
- public terminal state matched the preregistered abstraction;
- minimal basis groups were derived only by replaying frozen `compose()` over already-produced traces;
- retained participation and causal/residual partition were complete;
- deterministic repeat passed;
- canonical permutation invariance passed.

## New semantic-delta observations

Current CAL's more precise native failure localization remains available in its native receipt without being laundered into Contract C public implementation-control-flow vocabulary:

- `NO_DECIDING_RELATION` -> public `no_deciding_relation`;
- `MEASUREMENT_NOT_APPLICABLE` -> public `no_deciding_relation`;
- narrator/scope `MEASUREMENT_MISS` -> public `no_deciding_relation`;
- actual categorical `UNRESOLVED` -> public `unresolved_categorical_relation`.

In the support-plus-unresolved case, the unresolved passage alone was the minimal public basis for the terminal unresolved state; the supporting passage remained represented but residual. This preserves the current CAL precedence rule rather than silently allowing support to win.

## Negative controls

The experiment preserved all required negative boundaries:

- predecessor resolver rejected current CAL: `producer: unknown or ambiguous implementation/policy binding in immutable resolver`;
- duplicate participant rejected;
- duplicate equivalent basis group rejected;
- stale Contract-B evidence reference rejected;
- context/result substitution rejected.

## Resolver boundary

The CAL-side experiment emits only a non-authoritative successor-row proposal. Apparatus must independently decide whether to create a new immutable resolver authority for `847cc970...`.

The predecessor resolver commit `43b571...` must remain immutable and must not be edited or treated as implicitly widened.
