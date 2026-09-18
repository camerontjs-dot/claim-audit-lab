# CAL Quantitative Change Warranted Composition RC1 — Preregistration

Date: 2026-09-17

Classification: Draft Research / post-authority composition qualification.

Parent: exact qualified scalar Gate-1B candidate `c33b656819e91ac38a85c48921b84ea20ec090bc`.

Prior Gate-0 authority:
- Quantitative Change Composition RC0 PR #129
- exact qualified Gate-0 head `309f9ccbb91a24096f3f825e9dc2d8f8ee6aa88a`
- disposition: composition-first supported for exact scalar states.

## Question

Are two independently warranted point-valued scalar atoms plus a separate established temporal binding sufficient to derive bounded exact quantitative-change relations without creating a new atomic semantic family?

## Frozen composition contract

A contribution contains:
- one scalar atom;
- one authority receipt identity;
- explicit `warranted` state;
- one temporal binding with label, rank, and establishment state.

A change query contains:
- entity;
- metric;
- unit;
- kind: `INCREASED`, `DECREASED`, `UNCHANGED`, or exact absolute `DELTA`;
- optional exact delta amount.

## Required behavior

The candidate must:
- use temporal rank, not input order;
- require distinct established temporal points;
- require two distinct warranted authority identities;
- require exact point scalar atoms, not intervals or approximations;
- preserve entity/metric/unit identity;
- return `SUPPORTS`, `REFUTES`, or `UNRESOLVED`.

## Explicit non-scope

Not qualified here:
- relative percent change;
- percentage-vs-percentage-point normalization beyond the scalar unit itself;
- rates;
- compound change;
- uncertainty propagation;
- unit conversion;
- extraction of temporal bindings from text;
- production wiring.

## Falsifiers

The frozen evaluator includes weak strategies that:
- trust call order rather than temporal order;
- erase scalar identity;
- use interval midpoints;
- ignore warrant state.

The apparatus is frozen before candidate exposure.
