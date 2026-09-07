# RC0 prereveal development notes

These observations occurred before the implementation/evaluator freeze and are not counted as fresh smoke evidence.

- The first local 12-case seam run produced 11/12 test assertions even though all 12 candidate behaviors were fail-closed.
- `INCOMPLETE-ATOM-NO-SCORE-REPAIR` expected the stop to occur at `ATOM_INCOMPLETE`. Exact RC7F-B1 instead returned `UNRESOLVED` for the lexical-number surface `four units`, so the runtime correctly classified the case as `MEASUREMENT_MISS_SAFE` and abstained.
- The evaluator assertion was narrowed to the actual falsifier: either safe pre-authority stop (`MEASUREMENT_MISS_SAFE` or `ATOM_INCOMPLETE`) is acceptable; any deciding result remains a failure.
- No runtime semantic rule or frozen predecessor dependency was changed in response.
