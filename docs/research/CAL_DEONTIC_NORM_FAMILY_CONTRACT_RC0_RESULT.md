# CAL Deontic Norm Family Contract RC0 — Terminal Result

Date: 2026-09-17

Classification: Draft Research / Gate-0 semantic-family discrimination.

## Frozen lineage

- parent M4 terminal result: `607ec560fd53bd56279193a8d39a48b6f80e1012`
- frozen apparatus/falsifier head: `20640b8f3dd1895c1bfe9b69e99ca549ebb3269c`
- exact qualified candidate head: `791cd59fa47ba8e7a709f289584468aa9e255334`
- dedicated full-history qualification run: `35276294013`

## Disposition

**SUPPORTED FOR PROMOTION, bounded to the typed Gate-0 deontic family contract.**

The frozen possible-assignment oracle and direct candidate consumer support one conservative typed family containing:

- `PERMITTED`;
- `PROHIBITED`;
- `OBLIGATORY`;
- `PERMISSION_RESTRICTED_TO`.

Exception, condition, and temporal bindings remain proposition-scope fields rather than separate semantic families in this result.

## Evidence

On exact head `791cd59f…`:

- 6/6 frozen evaluator-control tests passed;
- 5/5 frozen candidate-falsifier tests passed;
- full repository suite passed;
- focused Ruff lint passed;
- candidate Ruff format passed;
- strict mypy passed;
- production `src/` remained unchanged from M4.

Preserved red runs include capability absence before the candidate existed, frozen-apparatus Ruff hygiene, and a candidate-format-only failure. None was silently discarded.

## Semantic boundary

The qualified RC0 contract intentionally does **not** infer:

- `OBLIGATORY -> PERMITTED`;
- `PERMISSION_RESTRICTED_TO -> PERMITTED`;
- implication across different subjects/actions;
- implication across changed exception, condition, temporal relation, or temporal reference bindings.

Permission/prohibition and obligation/prohibition are explicit conflicts under identical scope. Other cross-mode relations remain unresolved unless separately qualified later.

## Non-claims

This result does not establish natural-language extraction, source-completion warrant, operational authorization, complete deontic logic, nested rules, population overlap, a production plugin, Contract C/Decision behavior, release readiness, or independent reproduction.

The ordinary Public suite remains affected by the inherited shallow-history issue and is not the authority for this full-history research qualification.
