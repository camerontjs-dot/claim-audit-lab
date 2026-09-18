# CAL Population + Deontic Applicability Discriminator RC0 — Terminal Result

Date: 2026-09-18

Classification: Draft Research / cross-family applicability discriminator.

## Frozen lineage

- terminal pressure parent: `b10adbb5f185c093bbe9b7e8e7759f666141cd0e`
- deontic Gate-1B subject: `60298c99e8eb16cdad01f3c652cead83cad02992`
- population Gate-1B subject: `5d72475a65c3b6cf4190a048040fad8ee8b91156`
- corrected pre-candidate freeze: `f28b2a8a784271b4e8e880cca55478497b79599e`
- clean freeze run: `35351781535`
- exact qualified candidate head: `1bf34e18c70f47fb952e63dc592523db536e7b60`
- frozen apparatus regression run: `35351914395`
- candidate qualification run: `35351914404`

## Disposition

**SUPPORTED_POPULATION_DEONTIC_APPLICABILITY_RC0.**

Direct member applicability is supported only when the composition seam establishes all of the following:

1. the norm contribution is warranted;
2. the membership contribution is warranted;
3. membership status is direct `MEMBER`;
4. the norm subject and membership population have exact canonical identity;
5. the norm subject is established as population-scoped;
6. the derived applied norm preserves mode, action, exceptions, condition, temporal relation, and temporal reference exactly;
7. only the population subject is replaced by the member entity.

## Discriminating result

Canonical string equality alone is insufficient.

The frozen same-string role-collision case falsifies a composer that joins only on `norm.subject == membership.population`: the same identifier may denote an entity in one semantic role and a population in another.

The supported property is therefore **typed deontic-subject applicability**.

This does not uniquely require a production `subject_kind` field. An independently established disjoint namespace or equivalent mechanically verified invariant could satisfy the same property.

## Preserved weak-strategy failures

The frozen evaluator discriminated strategies that:

- joined on strings alone;
- ignored membership status;
- ignored subject kind;
- dropped deontic modifiers;
- ignored warrant state.

The qualified candidate passed every frozen case without changing production `src/`, deontic measurement/authority, or population measurement/authority.

## Limits

Not established:

- population subset inheritance;
- exception resolution via membership in an excluded population;
- condition satisfaction;
- temporal-condition satisfaction;
- deontic conflict resolution;
- natural-language entity/population linking;
- Contract C shape;
- Decision Engine behavior;
- production wiring.

## Preserved pre-candidate deviations

Runs `35350034910`, `35350150711`, `35351622018`, and `35351704100` preserve apparatus/static-hygiene defects before clean freeze. No candidate was exposed before run `35351781535` passed.

No merge, release, or production mutation is authorized.
