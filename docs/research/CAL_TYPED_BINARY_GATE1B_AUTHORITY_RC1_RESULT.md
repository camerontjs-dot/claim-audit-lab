# CAL Typed Binary Relation Gate-1B Authority RC1 — Terminal Result

Date: 2026-09-17

Classification: Draft Research / independent source-completion and warrant qualification.

## Frozen lineage

- terminal Gate-1A RC1 parent: `a3f8c810116c13d04b21347885404bbb08347b8c`
- evaluator-invalid Gate-1B RC0: PR #155 / run `35297443712`
- RC1 pre-candidate apparatus head: `829ff492bb4b648436c46bfa332d3375c518ae99`
- exact qualified RC1 candidate head: `1641d349e4740bf439e90e12953fffa7439ee986`
- dedicated qualification run: `35297750568`

## Disposition

**SUPPORTED_GATE1B_TYPED_BINARY_RC1.**

The independent source completer reconstructs the exact closed-world relation atom and warrants only exact agreement with Gate-1A measurement.

## Qualified state

Authority preserves:
- subject;
- predicate identity;
- object;
- positive vs negative relation polarity.

The qualified closed predicate inventory remains:
- `OWNS` / `OWNED_BY`;
- `ADJACENT_TO`;
- `NORTH_OF` / `SOUTH_OF`;
- `IN` / `CONTAINS`.

The selected Gate-1A safe extensions for `belongs to`, `lies north of`, and `lies within` remain qualified.

## Falsifiers

The frozen evaluator mutates subject, object, predicate, inverse/directional predicate, and polarity. Every mutation is refused. A weak trust-measurement authority is rejected.

## Preserved evaluator invalidity

RC0 incorrectly admitted `A and B are adjacent` as a clean authority case even though the selected conservative measurement path leaves that coordinated surface unresolved. RC0 remains preserved as `INCONCLUSIVE_EVALUATOR_INVALID`; RC1 starts fresh from the exact Gate-1A parent and excludes the unearned surface.

## Machinery consequence

```
closed-world relation measurement
  -> RelationAtom
  -> independent source reconstruction
  -> exact atom equality
  -> typed-relation warrant
  -> Gate-0 predicate/inverse/symmetry algebra
```

No transitivity, geometric inference, nesting inference, or arbitrary predicate expansion is established.

## Boundary

Research qualification only. No production wiring, merge, or release.

All nine currently targeted atomic family machinery paths are now finalized through bounded measurement + independent source completion/warrant. The end-stage pressure campaign may begin.
