# CAL Population + Deontic Applicability Discriminator RC0 — Preregistration

Date: 2026-09-18

Classification: Draft Research / cross-family applicability discriminator.

Base: terminal semantic-family unseen pressure RC2 head `b10adbb5f185c093bbe9b7e8e7759f666141cd0e`.

Exact qualified subjects:
- deontic norm Gate-1B: `60298c99e8eb16cdad01f3c652cead83cad02992`
- population membership Gate-1B: `5d72475a65c3b6cf4190a048040fad8ee8b91156`

## Decision

Determine whether a warranted population-scoped deontic norm can be instantiated safely to a warranted member entity by exact canonical identifier equality alone, or whether the composition seam also needs an established subject-kind / namespace invariant.

This experiment does not reopen deontic or population measurement, authority, or relation semantics.

## Competing hypotheses

### H1 — canonical string equality is sufficient

If the deontic subject identifier equals the membership population identifier, direct member substitution is safe without any additional typing state.

### H2 — subject role must be established

A bare identifier can denote different semantic roles unless the namespace is mechanically guaranteed disjoint. Safe applicability therefore requires either:
- explicit evidence that the norm subject denotes a population; or
- an independently established equivalent namespace/type invariant.

## Frozen behavior

The candidate may instantiate only direct positive membership.

It must:
- require warranted norm and membership contributions;
- require direct `MEMBER` status;
- require exact population identity;
- require the deontic subject to be established as population-scoped;
- preserve mode, action, exceptions, condition, temporal relation, and temporal reference exactly;
- replace only the population subject with the member entity in the derived applied norm.

It must fail closed for:
- non-membership or unknown membership;
- population mismatch;
- entity mismatch in the query;
- unwarranted inputs;
- a same-string deontic subject established as an entity rather than a population;
- dropped or changed deontic modifiers;
- subset inheritance, which is outside RC0.

## Falsifiers

Weak strategies deliberately:
- join on the subject/population string alone;
- ignore membership status;
- ignore subject-kind state;
- drop deontic modifiers;
- ignore warrant state.

The evaluator is frozen before candidate exposure.

## Interpretation rule

If the string-only strategy survives all frozen cases, the stronger subject-kind requirement remains `INCONCLUSIVE`.

If it fails the deliberate role-collision case and a typed candidate later passes without apparatus changes, the supported property is **typed deontic-subject applicability**, not necessarily a new production field. A proven disjoint namespace could satisfy the same requirement.

## Non-scope

Not qualified here:
- population subset chains;
- exception resolution against a second population membership;
- condition satisfaction;
- temporal-condition satisfaction;
- deontic conflict resolution;
- natural-language entity or population linking;
- production wiring;
- Contract C or Decision Engine changes;
- merge or release.
