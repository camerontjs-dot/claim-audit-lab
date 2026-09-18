# CAL Attribute State + Temporal Applicability RC0 — Terminal Result

Date: 2026-09-18

Classification: Draft Research / modifier-vs-family discriminator.

## Frozen lineage

- terminal semantic-family pressure parent: `b10adbb5f185c093bbe9b7e8e7759f666141cd0e`
- attribute-state Gate-1B subject: `9f74ac0a2d0054cec1683cea96691b744bbb2067`
- corrected pre-candidate freeze: `d6ef40df3de2fe44ca6104c2e5b434ca2b103abc`
- clean freeze run: `35352742591`
- exact qualified candidate head: `861435078d7a91ddaaa21d373549e2cc66f078f1`
- frozen-discriminator rerun: `35352876504`
- candidate qualification run: `35352876632`

## Disposition

**SUPPORTED_ATTRIBUTE_STATE_TEMPORAL_APPLICABILITY_RC0.**

Under the tested bounds, temporal applicability is sufficiently represented as a generic authority-bound scope wrapper around an already-warranted attribute-state contribution.

The evidence does not justify adding temporal state to the atomic `attribute_state` family.

## Supported property

A time-indexed attribute-state query may decide only when:

1. the state contribution is warranted;
2. an explicit temporal scope exists;
3. that scope is bound to the exact state authority identity;
4. the target ordinal falls within the explicit closed scope;
5. entity, attribute, and domain match exactly.

Inside the established scope:

- same value => `SUPPORTS`;
- different value => `REFUTES` only for functional attributes;
- alternate value on a non-functional attribute => `UNRESOLVED`.

Outside the scope, or with missing/mismatched scope, the result is `UNRESOLVED`.

## Discriminating result

The frozen evaluator falsified strategies that:

- ignored temporal scope;
- treated the latest known state as persisting indefinitely;
- ignored scope-to-authority binding;
- treated every attribute as functional;
- erased warrant state;
- emitted only the relation while dropping temporal/provenance state.

The qualified candidate passed all frozen cases while preserving the frozen apparatus bytes and production `src/`.

## Architecture consequence

The supported architecture is:

```
warranted attribute-state contribution
        +
authority-bound temporal applicability scope
        ↓
generic applicability gate
        ↓
existing attribute-state relation semantics
```

This keeps temporal applicability as cross-cutting modifier/integration state rather than embedding time into the atomic state family.

A separate attribute-temporal family or attribute-specific time field would require a concrete future semantic or provenance failure.

## Preserved deviations

Two pre-candidate setup deviations are preserved:

1. a candidate workflow was created prematurely with a placeholder freeze SHA and then removed before clean freeze;
2. the first corrected freeze passed semantic controls but failed only static E501/I001 checks.

Those corrections did not change cases, expected relations, weak strategies, or evaluator semantics.

No candidate was exposed before clean freeze run `35352742591`.

## Limits

Not established:

- temporal extraction from natural language;
- uncertain or fuzzy intervals;
- supersession among multiple state observations;
- transition/event causality;
- interval conflict resolution;
- production runtime wiring;
- Contract C representation;
- Decision Engine behavior.

No merge, release, or production mutation is authorized.
