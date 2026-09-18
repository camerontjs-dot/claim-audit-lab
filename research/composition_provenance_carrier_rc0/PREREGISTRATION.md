# CAL Composition Provenance Carrier RC0 — Preregistration

Date: 2026-09-18

Classification: Draft Research / cross-composition audit-carrier discriminator.

Base: terminal semantic-family unseen-pressure RC2 head `b10adbb5f185c093bbe9b7e8e7759f666141cd0e`.

Qualified composition evidence already exists for:

- quantitative change — PR #166;
- typed-binary spatial composition — PR #167;
- occurrence + order binding — PR #168;
- population + deontic applicability — PR #169;
- attribute state + temporal applicability — PR #172.

## Question

Can one generic composition receipt bind the audit-critical state from all five qualified composition seams without changing their semantic logic, or is module-specific output schema required?

## Observed gap

Four qualified research candidates return only a bare relation result. Attribute-state temporal applicability already emits a provenance-bearing receipt.

A bare relation is insufficient for an independent downstream consumer to determine which:

- composition module ran;
- warranted authority inputs participated;
- semantic input state was consumed;
- cross-cutting modifier state controlled the decision;
- query was answered.

## Candidate contract

A generic composition receipt must bind:

- `module_id`;
- exact ordered `input_authority_ids`;
- digest of canonical semantic input state;
- digest of canonical modifier/integration state;
- digest of the exact query;
- relation result;
- deterministic receipt identity over all of the above.

The carrier does not recompute module semantics. It makes a module decision independently auditable when the referenced immutable inputs are available.

## Frozen module shapes

The apparatus includes representative observations for:

1. quantitative change with temporal bindings;
2. spatial composition with frame metadata;
3. occurrence/order with event-instance binding ids;
4. population/deontic applicability with subject-kind and membership state;
5. attribute-state temporal applicability with authority-bound temporal scope;
6. an `UNRESOLVED` composition attempt.

## Falsifiers

Weak carriers deliberately:

- preserve only relation;
- erase input authorities;
- erase modifier state;
- erase query identity;
- erase module identity.

Metamorphic verification mutates each bound field independently and must invalidate the receipt.

## Interpretation

If one carrier satisfies every module shape, the next prototype should keep module-specific semantics behind a common provenance-bearing composition envelope.

This does not authorize a final wire schema. Cross-repository Contract C representation remains a separate qualification problem.

No production mutation, merge, or release.
