# Current CAL -> Contract C2 producer conformance RC1 — terminal record

## Disposition

`SUPPORTED_FOR_APPARATUS_RESOLVER_SUCCESSOR_QUALIFICATION`

RC1 supersedes RC0 as the preferred producer projection subject because it removes caller selection of CAL semantic implementation identity while preserving exact RC0 C2 bytes for correctly bound current-CAL results.

This remains CAL-side producer evidence only. It is not independent resolver authority, Contract C2 release authority, Decision qualification, Contract E authority, Authorization, or execution permission.

## Exact execution

- CAL research head: `c4974388e9a40a87661ed80af9271b9625b7c093`
- semantic implementation: `847cc970642bb648dc994b929c2053b5c9d4648c`
- Contract C2 exact head: `b42c827acb0a9fe65353354d709add0e27bab307`
- predecessor resolver: `43b571464734325277374ee81098553fb7c1b944`
- hard-bound materializer blob: `ef32fa4fca52a2bb7fe2896b378f9b6fdef0dfde`
- policy digest: `44ecc33519fa8911079595d322f5f0decbf0389af42e153ac32214931798e42c`
- workflow run: `35053229507`
- job: `104657905279`
- artifact: `10429439212`
- artifact digest: `sha256:28e0c1eea76129164135f69388910f32f218101ebb656e131b0e4ddd657cb43b`
- evaluation digest: `sha256:673200cd89f5378083e17ca023c05498cc7ec00160576d28d8222f2fa2aece05`
- failures: `[]`

## Observed successor equivalence

All sixteen preregistered current-CAL result classes produced C2 canonical bytes exactly equivalent to RC0 when RC0 was supplied the correct `847cc970...` identity.

This includes:

- supported and contradicted strict comparisons;
- independent support alternatives;
- retained irrelevant evidence;
- minimal and alternative mixed bases;
- `NO_DECIDING_RELATION`;
- `MEASUREMENT_NOT_APPLICABLE`;
- direct-event support/refutation;
- negative-event unresolved state;
- support plus unresolved, where unresolved retains precedence;
- scope/narrator measurement miss;
- unsupported semantic family.

## Producer-identity hardening

Three negative controls passed:

1. legacy caller relabeling attempt using `semantic_implementation_sha=a902621...` was rejected because the RC1 API no longer accepts a semantic-implementation argument;
2. simulated runtime semantic-identity drift was rejected with `unexpected CAL semantic implementation authority`;
3. the immutable predecessor resolver still rejected the correctly bound current producer as unknown/ambiguous.

The RC1 producer adapter therefore owns the CAL semantic identity it emits. Apparatus remains responsible for independently selecting and freezing resolver authority.

## Next gate

Apparatus may independently qualify a resolver successor containing a new exact mapping for current CAL `847cc970...` and projection blob `ef32fa4f...`, while preserving the old `a902621...` row exactly and leaving predecessor resolver commit `43b571...` immutable.
