# Current CAL -> Contract C2 producer conformance RC0

**Classification:** Draft Research / producer-conformance evidence.

This experiment does not modify CAL runtime semantics, Contract C2 validators, Decision Engine, Contract E, Authorization, release state, or production discovery.

## Objective

Determine whether the exact current CAL V1 integration candidate can be projected into the exact frozen Contract C2 promotion subject without adding semantic judgment, laundering internal failure telemetry into public semantic state, or inheriting producer authority from the older CAL RC1 subject.

## Exact authorities

Current CAL integration candidate:

- records head: `d03d0e960ad82d889e6763fd4fb53cd24babd187`;
- frozen implementation: `80835a57e121c66d22c68f349abf8e318de0e232`;
- semantic implementation identity: `847cc970642bb648dc994b929c2053b5c9d4648c`;
- qualified predecessor: `a902621e8baea3063dddd7f92ba975aade305464`;
- profile: `cal-v1-integration-candidate-v1`;
- supported semantic families: `strict_comparison`, `direct_event_order`.

Contract C2 promotion subject:

- repository: `camerontjs-dot/apparatus-contracts`;
- exact head: `b42c827acb0a9fe65353354d709add0e27bab307`;
- compatibility version: `2.0.0`;
- wire profile: `contract-c-successor-candidate-a-rc2-research`.

Existing policy authority:

- immutable resolver commit: `43b571464734325277374ee81098553fb7c1b944`;
- existing resolver maps only semantic implementation `a902621e8baea3063dddd7f92ba975aade305464`;
- policy digest: `44ecc33519fa8911079595d322f5f0decbf0389af42e153ac32214931798e42c`;
- policy profile: `cal-v1-candidate-2026-09`;
- policy semantics: `typed-source-grounded-scoreless-categorical`;
- policy supported families: `direct_event_order`, `strict_comparison`;
- projection provenance blob recorded by that resolver: `9bc152275759304be03b84014c56bd434549a64a`.

The old resolver row is **not** authority for `847cc970...` and may not be treated as inherited.

## Public projection rule under test

The candidate projection is allowed to use only the current immutable `AuditContext`, current immutable `AuditResult`, and exact Contract-B evidence-world binding. It may not re-measure, reinterpret passages, rerun semantic authority, add evidence, drop admitted participants, choose a downstream policy, or call Decision.

Public terminal mapping is preregistered as an abstraction over the native CAL result:

- `SUPPORTED` -> `supported / categorical_support`;
- `CONTRADICTED` -> `contradicted / categorical_refutation`;
- `MIXED_RELATIONS` -> `not_checkable / MIXED_RELATIONS`;
- `UNSUPPORTED_SEMANTIC_FAMILY` -> `not_checkable / UNSUPPORTED_SEMANTIC_FAMILY`;
- any completed result containing a categorical `UNRESOLVED` relation -> `not_checkable / unresolved_categorical_relation`;
- every other completed result with no deciding public relation -> `not_checkable / no_deciding_relation`.

The final row intentionally keeps producer-local failure localization such as `MEASUREMENT_NOT_APPLICABLE`, `MEASUREMENT_MISS`, and `NO_DECIDING_RELATION` in the native CAL receipt rather than promoting implementation-control-flow detail into Contract C public reason vocabulary. This is valid only if exact retained participation, public relation state, causal/residual classification, terminal verdict/reason, proposition binding, and Contract-B binding remain reconstructable.

## Causal basis rule under test

Basis groups must be derived only by replaying the existing frozen CAL `compose()` function over subsets of the already-produced immutable passage traces. No measurement, authority, or relation derivation may be rerun.

A basis group is minimal when replaying exactly that subset yields the same **public Contract C terminal state** and no strict subset does. All co-minimal groups must be preserved. Causal participants are the union of all minimal groups. Other retained participants remain residual.

For `no_deciding_relation` and `UNSUPPORTED_SEMANTIC_FAMILY`, basis groups must be empty and all participants residual/non-polarized.

## Frozen cases

The evaluator must exercise at least these classes before any result is revealed:

1. strict comparison single support;
2. strict comparison single refutation;
3. two independently sufficient supports;
4. support plus irrelevant retained evidence;
5. minimal support/refute conflict;
6. alternative-joint mixed basis `(S1 OR S2) AND R`;
7. symmetric alternative-joint mixed basis `S AND (R1 OR R2)`;
8. four-way mixed alternatives;
9. irrelevant-only `NO_DECIDING_RELATION`;
10. strict-comparison measurement-not-applicable with no relation;
11. direct-event support;
12. direct-event refutation;
13. negative-event polarity producing `UNRESOLVED`;
14. support plus unresolved event evidence, where unresolved must prevent a support winner;
15. narrator/scope stress within the current direct-event envelope;
16. unsupported semantic family.

## Required checks

For every representable case:

- current CAL runtime identity equals `847cc970...`;
- exact Contract C2 validator accepts the sealed object structurally;
- exact Contract-B world references validate;
- producer semantic implementation in C2 is `847cc970...`;
- policy digest remains exactly `44ecc335...`;
- terminal public state matches the preregistered mapping;
- basis groups equal compose-only minimal-basis derivation;
- all admitted traces remain represented exactly once as participants;
- causal/residual partition is complete and non-overlapping;
- canonical bytes, result-set identity, and whole-object hash are deterministic under repeat;
- semantically unordered participant and basis-group permutations canonicalize identically;
- duplicate participants/basis members fail closed;
- stale/tampered Contract-B references fail closed;
- proposition/result/context mismatches fail closed.

## Resolver discriminator

The exact existing resolver `43b571...` must reject the current semantic implementation `847cc970...`. A candidate successor resolver row may be emitted only as a **proposal artifact** after all producer compatibility checks pass. It is not authority until independently frozen in `apparatus-contracts`.

No evaluator in this CAL repository may claim that supplying its own proposed resolver row constitutes independent producer-policy authority.

## Stop rule

Classify the experiment as one of:

- `SUPPORTED_FOR_APPARATUS_RESOLVER_SUCCESSOR_QUALIFICATION`;
- `FALSIFIED_CURRENT_CAL_TO_C2_PROJECTION`;
- `BLOCKED_BY_UNREPRESENTABLE_CURRENT_CAL_STATE`;
- `APPARATUS_FAILURE`.

Preserve all failing cases. Do not patch CAL semantics, Contract C2, or the resolver after reveal inside this RC0. Any correction requires a separately preregistered successor.
