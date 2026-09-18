# CAL Attribute State + Temporal Applicability RC0 — Preregistration

Date: 2026-09-18

Classification: Draft Research / modifier-vs-family discriminator.

Base: terminal semantic-family unseen-pressure RC2 head `b10adbb5f185c093bbe9b7e8e7759f666141cd0e`.

Exact qualified attribute-state subject:
- Gate-1B authority candidate `9f74ac0a2d0054cec1683cea96691b744bbb2067`.

## Decision

Determine whether temporal applicability must become attribute-state semantic state, or whether a generic authority-bound temporal-scope wrapper can safely gate the already-qualified attribute-state relation semantics.

## Competing hypotheses

### H1 — timeless/latest-state carry-forward is sufficient

Once a state is warranted, it may be applied to later target times unless superseded.

### H2 — explicit authority-bound temporal applicability is required

A warranted state may decide a time-indexed query only when an explicit temporal scope:
- is bound to that exact authority contribution;
- covers the target time;
- leaves the state atom itself unchanged.

The scope mechanism should be generic modifier/integration state rather than a new attribute-state family if no attribute-specific temporal semantics are needed.

## Frozen behavior

The candidate may decide only when:
- the state contribution is warranted;
- the temporal scope is bound to the same authority id;
- the target ordinal lies inside the explicit closed scope;
- entity, attribute, and domain match exactly.

Inside scope:
- same value => SUPPORTS;
- different value => REFUTES only when the state attribute is functional;
- different value on non-functional attributes => UNRESOLVED.

Outside scope or with missing/mismatched scope => UNRESOLVED.

No persistence may be inferred from source order, input order, or “latest known state.”

## Falsifiers

Weak strategies deliberately:
- ignore temporal scope;
- treat latest observation as persisting indefinitely;
- ignore scope-to-authority binding;
- treat every attribute as functional;
- erase warrant state;
- emit relation-only output without provenance.

## Interpretation

If a generic authority-bound temporal wrapper passes, temporal applicability remains a cross-cutting modifier/integration concern under these bounds.

A separate attribute-temporal family or attribute-specific time field requires a concrete semantic or provenance failure.

## Non-scope

Not qualified:
- extracting time from natural language;
- interval overlap from uncertain dates;
- state-transition/event causality;
- multiple competing state observations;
- supersession rules;
- production wiring;
- Contract C / Decision Engine behavior;
- merge or release.
