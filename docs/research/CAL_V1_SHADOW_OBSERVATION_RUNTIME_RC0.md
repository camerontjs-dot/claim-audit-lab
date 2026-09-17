# CAL V1 Shadow Observation Runtime RC0 — Preregistration

Date: 2026-09-17

Classification: Draft Research / runtime measurement isolation.

This experiment is stacked on terminal M3 result record `5b16313855b83940f8b09ffaed4baccc15f4a51f`. It is not independent evidence and does not authorize merge, release, production promotion, learned-instrument authority, new semantic families, Contract C/Decision changes, or automatic action.

## Question

Can CAL collect additional shadow measurement receipts during the live per-passage semantic runtime, before warrant and relation, while keeping warrant, relation, composition, and verdict causally dependent only on the existing qualified primary family instrument?

## Frozen parent

- M3 terminal result head: `5b16313855b83940f8b09ffaed4baccc15f4a51f`
- M3 exact qualified implementation: `0e573d9f1426b5db1e01beb979e246f4cdd626b2`
- M3 qualified tree: `1253feaeca3322935f1356c636ba0302c64ae74e`
- current engine blob: `67a519958bcf06b289b8a13cb0246d22ccf53c5c`
- current plugin blob: `a2b96f192a4acafb2471785f0b51d2c656e03afc`
- current measurement ledger successor blob: `5e01c0a3246a90fcc42219da78b7d8a1ed5d5f74`
- current authority successor blob: `09761aab9e04deca724fd213a9295fc93cc3be52`

## Bounded architecture hypothesis

Introduce an observed-runtime path that executes the existing primary family measurement exactly as before. Immediately after that primary receipt is produced, a shadow-observation controller may run zero or more additional measurement functions for the same admitted passage and append valid receipts to the M3 `MeasurementLedger`.

Only the primary plugin receipt may enter `warrant()` and `relate()`. Shadow receipts are observation records only.

The observed-runtime result should expose:

- the ordinary `AuditResult`;
- the immutable `MeasurementLedger` containing the primary measurements plus accepted shadow measurements;
- deterministic shadow-observation failure records for shadow functions that raise or return invalid receipts.

Existing `audit()` remains the compatibility path and must preserve current behavior.

## Causal isolation invariant

For one fixed `AuditContext`, primary registry, and primary implementation:

> Adding, removing, reordering, failing, or returning invalid data from shadow measurement functions must not change the primary `AuditResult`, any primary `AuthorityReceipt`, any primary `BoundRelation`, deciding/non-deciding passage identity, composition outcome, or terminal CAL conclusion.

This invariant is stronger than ledger storage. Shadows execute before warrant/relation inside the runtime but have no authority path.

## Frozen falsifiers

Before implementation, freeze tests covering at least these cases:

1. no-shadow observed execution is exactly equivalent to ordinary `audit()`;
2. a valid foreign-family shadow receipt is collected in the ledger while the primary result and trace authority/relation objects remain identical;
3. two valid shadow instruments in opposite order produce the same primary result and the same canonical ledger identity;
4. a shadow receipt with stale/tampered identity is rejected from the ledger and recorded as a shadow failure while the primary result is unchanged;
5. a shadow function that raises is quarantined and recorded while the primary result is unchanged;
6. a same-family shadow receipt using an unqualified instrument identity cannot become the receipt used for primary warrant or relation;
7. shadow receipts with `CLAIMED`, `UNRESOLVED`, or `NOT_APPLICABLE` measurement status cannot alter the primary verdict;
8. no shadow receipt ID appears in any primary authority or relation object;
9. repeated execution with the same shadows is deterministic for ledger identity and shadow-failure records;
10. existing M1/M2/M3 semantic, Contract B, compiler, authority, full-repository, Ruff, and mypy gates remain green.

## Success conditions

RC0 is supported only if one exact successor head demonstrates all of the following:

- shadows execute at the live measurement seam before primary warrant/relation;
- primary semantics are byte/behavior compatible except for the explicit engine/runtime successor wiring needed to expose observation state;
- shadow observations cannot enter warrant, relation, composition, or verdict paths;
- invalid or failing shadows are quarantined rather than changing or aborting the primary semantic result;
- accepted shadows remain fully bound to the exact audit context and full evidence aperture through the M3 ledger;
- shadow ordering cannot change canonical ledger identity;
- current semantic/verdict fixtures are unchanged;
- full-history qualification and static gates pass.

## Falsifiers / stop rules

Preserve a negative result if any of these occur:

- any shadow changes primary conclusion, failure code, traces, authority IDs, relation IDs, deciding passages, or non-deciding passages;
- a shadow receipt reaches `warrant()` or `relate()`;
- shadow exception or invalid receipt prevents the primary result from being produced;
- maintaining isolation requires weakening M3 ledger or authority validation;
- success requires changing family semantics, composition rules, or expected verdict fixtures;
- success requires adding NLI, LLMs, learned parsers, retrieval, or a new semantic family.

## Alternative explanations to pressure-test

- shadow collection may still be operationally useless even if safe;
- post-measurement shadow execution can consume latency/resources despite semantic isolation;
- a same-process shadow could theoretically have side effects outside the immutable CAL objects; RC0 tests dataflow authority isolation, not hostile-process sandboxing;
- deterministic storage does not establish that any shadow instrument is accurate or useful enough for later promotion.

## Non-goals

RC0 does not test or authorize:

- voting, consensus, confidence thresholds, ranking, or instrument selection;
- any shadow receipt becoming semantic authority;
- NLI/LLM authority or new learned models;
- new semantic families;
- claim decomposition;
- retrieval/evidence-selection changes;
- scoreless composition changes;
- Contract C or Decision Engine changes;
- automatic action.

## Promotion boundary

A supported RC0 would justify only this next architectural step:

> CAL may execute bounded shadow measurement instruments at the live measurement seam and preserve their observations/failures without allowing them to affect the existing qualified semantic decision path.

Any rule that lets a secondary instrument influence warrant formation, relation selection, composition, or verdict requires a separate successor experiment.