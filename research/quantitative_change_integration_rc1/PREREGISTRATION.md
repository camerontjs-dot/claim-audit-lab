# CAL Quantitative Change Integration RC1 — Preregistration

Date: 2026-09-18

Classification: Draft Research / paired composition-vs-integration discriminator.

Parent: M4 terminal `607ec560fd53bd56279193a8d39a48b6f80e1012`.

Upstream evidence:
- scalar Gate-1B authority terminal: PR #152, exact qualified candidate `c33b656819e91ac38a85c48921b84ea20ec090bc`;
- quantitative-change Gate-0 composition: PR #129, exact qualified candidate `309f9ccbb91a24096f3f825e9dc2d8f8ee6aa88a`.

## Question

Does exact quantitative change require a specialized atomic semantic family, or is a provenance-bearing integration receipt over two already-warranted scalar states plus explicit temporal bindings sufficient?

## Load-bearing gap

The current warranted scalar atom carries entity, metric, unit, interval bounds, and exactness, but no temporal identity. Gate-0 quantitative change assumed time was already present in each state.

RC1 therefore tests the smallest explicit seam:

```
WarrantedScalar(old) + TemporalBinding(old)
WarrantedScalar(new) + TemporalBinding(new)
+ ChangeQuery
→ ChangeReceipt
```

The integration layer may derive only from exact singleton scalar atoms with matching entity/metric/unit and two distinct explicit temporal ordinals. It may not infer time from input order or source wording.

## Paired discriminator

The frozen evaluator distinguishes:

1. relation-only composition, which can match arithmetic but cannot satisfy provenance reconstruction;
2. input-order composition, which changes result when inputs are reversed;
3. exactness-blind composition, which upgrades approximate evidence;
4. provenance-bearing integration, which must preserve both authority identities, both temporal bindings, the exact delta, and deterministic receipt identity.

## Frozen bounds

Qualified:
- INCREASED;
- DECREASED;
- UNCHANGED;
- exact absolute DELTA;
- deterministic reordering by explicit temporal ordinal.

Fail closed / UNRESOLVED:
- approximate or interval-valued scalar state;
- same temporal ordinal;
- missing/mismatched temporal binding;
- entity/metric/unit mismatch;
- unsupported percent-change / ratio / rate semantics.

## Acceptance

A candidate is supported only if it matches the relation oracle and its receipt independently verifies every input identity and temporal binding. Frozen weak strategies must be detected.

No production `src/` mutation, atomic family registration, merge, release, Contract C, or Decision Engine change is authorized.
