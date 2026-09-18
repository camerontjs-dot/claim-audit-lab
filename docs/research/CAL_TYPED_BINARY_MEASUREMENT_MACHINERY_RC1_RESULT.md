# CAL Typed Binary Relation Measurement Machinery RC1 — Terminal Result

Date: 2026-09-17

Classification: Draft Research / Gate-1A measurement-machinery discrimination.

## Frozen lineage

- terminal Gate-0 parent: `22bc5c1d97b78cfe6f9e2f57e52f69d528069b9a`
- exact Gate-0 typed-contract authority: `7463ada3358f24fa5bb53fe82631a69064346bf3`
- predecessor RC0: `INCONCLUSIVE_EVALUATOR_INVALID`
- RC1 pre-candidate apparatus: `eb199ffc5439664159987ccb4905b886ce7b2168`
- exact qualified RC1 head: `0ba3223fad357f25c8a321e61a4cf8bfcfdfec0e`
- dedicated qualification run: `35291444330`

## Disposition

**SUPPORTED FOR GATE-1B WITH BOUNDS.**

RC1 corrects the predecessor evaluator defect by treating reversed ownership as a valid diagnostic atom rather than a fail-closed surface.

## Machinery comparison

### `direct_relation_grammar`

- MUST_HANDLE failures: **0**
- FAIL_CLOSED unsafe claims: **0**
- metamorphic failures: **0**
- diagnostic exact: RD01
- diagnostic unresolved: RD02–RD05

The direct grammar preserved exact argument order on `B owns A`.

### `broad_relation_extractor`

- MUST_HANDLE failures: **0**
- diagnostic exact: **RD01–RD05**
- diagnostic wrong claims: **0**
- FAIL_CLOSED unsafe claims: **RF01, RF02, RF03, RF04, RF05, RF07, RF08**
- metamorphic failures on reporting, metric geometry, and relation-chain composition

The broad extractor bought surface recall but overreached on unknown predicates, unqualified spatial composition/transitivity, metric geometry, reporting, disjunction, and conjunction.

### `conservative_relation_hybrid`

- MUST_HANDLE failures: **0**
- diagnostic exact: **RD01–RD04**
- diagnostic unresolved: RD05
- FAIL_CLOSED unsafe claims: **0**
- metamorphic failures: **0**

The hybrid safely added closed alternate relation surfaces while refusing the symmetric conjunction form `A and B are adjacent` in this RC1.

## Evaluator correction evidence

RC0 had classified `B owns A` as unsafe, which could not distinguish correct argument reversal from argument erasure. RC1 froze the sentence as an exact diagnostic. The weak argument-erasure strategy now fails by emitting the wrong diagnostic atom.

That correction is part of the qualification evidence, not an implementation detail.

## Architecture consequence

Typed-binary measurement should retain a closed predicate inventory and exact argument identity:

```
passage
  -> relation-family / composition / metric guard
  -> direct closed-predicate grammar
       OR
     explicitly gated relation extensions
  -> RelationAtom(subject, predicate, object, polarity)
  -> MeasurementReceipt
  -> [Gate-1B independent source completion / warrant: NOT YET QUALIFIED]
  -> Gate-0 declared symmetry/inverse relation algebra
```

No spatial transitivity, metric geometry, containment nesting, routing, or general spatial reasoning is authorized.

## Non-claims

No open predicate ontology, general spatial semantics, source-completion warrant, production plugin behavior, Contract C/Decision behavior, independent reproduction, merge, or release is established.
