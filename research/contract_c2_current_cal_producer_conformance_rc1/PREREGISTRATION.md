# Current CAL -> Contract C2 producer conformance RC1

**Classification:** Draft Research / producer-boundary hardening successor.

## Predecessor

RC0 executed successfully on exact current CAL and classified:

`SUPPORTED_FOR_APPARATUS_RESOLVER_SUCCESSOR_QUALIFICATION`

Preserved RC0 execution:

- workflow run `35053024929`;
- job `104657282295`;
- artifact `10428814215`;
- artifact digest `sha256:4cf9dbb90bab6a7eae9468bda198f22c34594388ba1af3adb1154c722b42da18`;
- evaluation digest `sha256:8a4c3aaa9c1e83e98cd3cf48ba26a028b0a89eb372258c1617955b3b53e08a01`;
- failures `[]`.

RC0 demonstrated representability, compose-only basis derivation, deterministic C2 materialization, canonical permutation invariance, and correct rejection by the predecessor resolver.

## New pressure finding

RC0's research materializer requires callers to pass `semantic_implementation_sha`. The preregistered evaluator always supplied the correct current CAL identity `847cc970642bb648dc994b929c2053b5c9d4648c`, so this did not falsify RC0's compatibility result.

However, producer identity is CAL-owned authority. A reusable CAL -> C2 producer adapter must not permit a caller to relabel a current CAL result as another semantic implementation merely by supplying a different 40-hex value.

## Exact RC1 delta

RC1 may change only the producer-identity binding surface:

- import current CAL's immutable `SEMANTIC_IMPLEMENTATION_SHA` from `claim_audit_lab.production_v1`;
- remove caller selection of semantic implementation identity from the materialization API;
- always emit the exact runtime authority `847cc970642bb648dc994b929c2053b5c9d4648c`;
- keep `policy_resolver_commit_sha` as an explicit argument because resolver authority is independently owned by Apparatus and cannot be guessed by CAL;
- retain RC0 terminal mapping, participant mapping, compose-only minimal-basis derivation, public policy digest, and all case expectations unchanged.

No CAL semantic code or Contract C2 validator may change.

## Required successor checks

RC1 must rerun the same 16-case RC0 cohort and all RC0 negative controls, plus:

1. materializer output always identifies `847cc970...`;
2. the materializer API has no caller-selectable semantic implementation parameter;
3. an attempted legacy call supplying `semantic_implementation_sha=a902621...` fails before C2 materialization;
4. policy digest remains `44ecc335...`;
5. predecessor resolver still rejects the correctly bound current producer;
6. current materializer Git blob is frozen for downstream Apparatus resolver qualification.

## Stop rule

Preserve the first execution. If any prior RC0 case changes or semantic identity substitution remains possible, classify `FALSIFIED_PRODUCER_IDENTITY_BINDING` and do not create an Apparatus resolver successor.
