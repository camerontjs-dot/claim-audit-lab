# CAL Spatial Composition Discriminator RC1 — Preregistration

Date: 2026-09-18

Classification: Draft Research / generic relation-composition versus spatial-specialization discriminator.

Parent: M4 terminal `607ec560fd53bd56279193a8d39a48b6f80e1012`.

Upstream evidence:
- typed-binary Gate-1B authority terminal: PR #157, exact qualified candidate `1641d349e4740bf439e90e12953fffa7439ee986`;
- Gate-0 typed/spatial discriminator: PR #127, exact qualified candidate `7463ada3358f24fa5bb53fe82631a69064346bf3`.

## Question

Does bounded spatial composition require a spatial-specific module, or can a generic provenance-bearing typed-relation chain composer handle only explicitly declared compositional laws while failing closed elsewhere?

## Hypothesis

A generic relation-chain module is sufficient if:
- each predicate declares its inverse/symmetry/composition law explicitly;
- only predicates with a frozen transitive law may chain;
- every derived receipt preserves both input authority identities;
- mixed-predicate spatial inheritance is refused.

Under RC1, only containment `IN` / `CONTAINS` is eligible for transitive chain composition.

`ADJACENT_TO`, `NORTH_OF`, `SOUTH_OF`, ownership, and mixed containment/direction chains are not authorized for composition.

## Frozen discriminator

Positive:
- nested `IN`;
- nested `CONTAINS`;
- inverse query over a valid containment chain;
- negative query refutation over a valid containment chain.

Fail closed:
- adjacency chaining;
- north/south chaining;
- ownership chaining;
- containment-to-direction inheritance;
- mixed predicates;
- broken middle-node identity;
- unknown predicates.

## Paired strategies

Frozen weak controls:
- all predicates transitive;
- no predicate transitive;
- spatial inheritance from container to contained object;
- provenance-free relation-only output.

A generic declared-law candidate is supported only if it matches the frozen relation oracle and emits a verifiable provenance-bearing chain receipt.

## Acceptance

If generic declared-law composition passes, a separate spatial-specific integration module is not justified under these bounds.

A concrete semantic/provenance failure is required before promoting specialized spatial machinery.

No production mutation, metric geometry, routing, frame-of-reference inference, merge, or release.
