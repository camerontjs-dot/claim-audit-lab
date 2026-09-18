# CAL Occurrence + Order Binding Discriminator RC0 - Preregistration

Date: 2026-09-18

Classification: Draft Research / cross-family recombination discriminator.

Base: terminal semantic-family unseen pressure RC2 head `b10adbb5f185c093bbe9b7e8e7759f666141cd0e`.

Exact qualified subjects already frozen in that lineage:
- event occurrence Gate-1B: `7cd54f9fb28afa6f5fc0fa2d1e9905cd916e0efe`
- direct event order Gate-1B RC3: `b163f0faf58c8fe7e2c74e8d9e8618aa2147a359`
- fresh nine-family unseen-pressure run: `35299962120`

## Decision

Determine whether independently warranted event-occurrence and direct-event-order atoms can be recombined safely by semantic field equality alone, or whether cross-family composition requires an explicit shared event-binding identity.

This experiment is about the composition boundary. It does not reopen either atomic family's measurement or authority qualification.

## Competing hypotheses

### H1 - field equality is sufficient

If actor/action/object/polarity fields agree across the occurrence and order atoms, CAL can safely join them without additional event identity.

### H2 - explicit event binding is required

Repeated same-shaped events can make field equality ambiguous. A safe composer therefore needs an explicit binding identity that links each occurrence atom to the corresponding order endpoint.

## Frozen evaluator

The evaluator includes:
- clean positive joins;
- BEFORE/AFTER normalization;
- occurrence contribution input-order invariance;
- duplicate same-shaped events with different binding identities;
- binding/field inconsistency;
- missing binding state;
- unwarranted occurrence and order inputs;
- binding reuse that would collapse two distinct events.

Weak strategies deliberately:
- join by semantic fields only;
- join by binding identity while ignoring semantic-field consistency;
- ignore warrant state;
- infer order from occurrence call order.

The evaluator is frozen before any candidate implementation is added.

## Acceptance / falsification

Support for explicit binding requires:
- the field-only strategy to fail a duplicate-event aliasing case for the intended reason;
- every other weak strategy to fail a meaningful gate;
- a later candidate to pass without modifying this preregistration, apparatus, evaluator, or frozen apparatus test.

If field-only composition survives the frozen discriminator, the explicit-binding claim remains `INCONCLUSIVE`.

If a binding-aware candidate cannot pass without changing the frozen evaluator, the experiment stops rather than repairing the apparatus around the result.

## Boundary

In scope:
- typed recombination only;
- positive occurrence identities;
- exact actor/action/object/polarity preservation;
- direct BEFORE/AFTER normalization;
- explicit event-binding identity as composition metadata.

Out of scope:
- extracting event bindings from natural language;
- coreference resolution;
- event deduplication policy;
- temporal reasoning beyond direct BEFORE/AFTER;
- negative-event temporal semantics;
- production registration;
- Contract C or Decision Engine changes;
- merge or release.
