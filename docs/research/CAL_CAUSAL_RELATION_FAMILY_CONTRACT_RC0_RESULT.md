# CAL Causal Relation Family Contract RC0 — Terminal Result

Date: 2026-09-17

Classification: Draft Research / Gate-0 semantic-family discrimination.

## Frozen lineage

- parent M4 terminal result: `607ec560fd53bd56279193a8d39a48b6f80e1012`
- frozen candidate-test apparatus: `00a6c50b1a34542c5a6c52085f179d390152f899`
- exact qualified head: `0bfcfe532bd7dcbe0d9049c0e73173f40d05a415`
- dedicated full-history qualification run: `35279704215`

## Disposition

**SUPPORTED FOR PROMOTION, bounded only to a typed explicit-causal-assertion Gate-0 family contract.**

The tested contract distinguishes `CAUSES`, `CONTRIBUTES_TO`, `PREVENTS`, `CORRELATES_WITH`, `PRECEDES`, and `CO_OCCURS`. It does not promote correlation, precedence, co-occurrence, or contribution into stronger causation. `CAUSES` and `PREVENTS` on the same endpoints are explicit conflicts; other cross-kind relations remain unresolved unless independently qualified.

## Evidence

Frozen evaluator controls, candidate falsifiers, full repository tests, candidate Ruff lint/format, and strict mypy all passed. Production `src/` remained unchanged from M4.

The apparatus explicitly killed precedence-to-cause, correlation-to-cause, contribution-to-cause, and cause-to-contribution shortcuts.

## Boundary

This is a contract for interpreting explicit typed causal assertions. It is **not** evidence that CAL can infer causation from observational data, experiments, temporal ordering, statistical association, model confidence, or multiple evidence passages. Causal inference machinery remains a separate and much stronger research problem.
