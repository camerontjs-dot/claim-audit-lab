# Real-claim comparison authoring RC0

`FALSIFIED_EXISTING_TARGET_FIELD_MODEL_INSUFFICIENT`.

All fourteen frozen `strict_comparison` claims authored. Forward/inverse pairs kept the sides the evaluator required, and harmless spacing kept those fields. The same authoring mapped every modifier collision onto identical `lhs_entity`, `rhs_entity`, and `comparison_direction`. Coverage of the fourteen claims does not support the field model.

## Question

Issue #193 asks whether those fourteen claims can be authored by one bounded mechanism without losing proposition-significant meaning and without changing the CAL semantic engine.

## Apparatus

The cases and evaluator were already frozen on this branch. I committed the authoring change before the decisive run and executed `evaluate.py` once. The runner exit was 1, the non-support exit. I did not rerun it.

- Scientific base: `6bb0d60f3e2286123f56de5657de4e97d6374c63`
- Cases commit: `7f2293f7b4d9507f268a4acea0635f0016492c52`
- Evaluator freeze: `872e3f3d753c4bf840a4c7b68c37f46d2fb2f144`
- `CASES.json` git blob: `b680f5a7723215ddd5fe81b406dc97743687c2c2`
- `CASES.json` SHA-256: `6baca64374413a253cc75534dc60971f829707ddffd9b5e6ca7bb537b6c9dcfb`
- `evaluate.py` git blob: `d20a2bdcb6ecb7e3d3e0b1a31412539817f1a5db`
- `evaluate.py` SHA-256: `e16887f0e8c682e29c9327910cafdf1dd5db6e70b9742ffca8818d6b537683a5`
- Implementation: `eb1de81c36683c4239ee5eef6a26ea1079b31ce2`, tree `69594da75ed6042bea7c91cf314da932095ecb85`
- Decisive result SHA-256: `768f9c79e3cfe4567ab37fb9714ddfdd5d1dd58dca0f519d78b29278cc271015`
- Cohort SHA-256 recorded by the runner: `3c6da6d24d0ddbaba817687f42ddd8e027840ed45173bb36c77ed1e1160e3339`

Preserved output: [decisive-result.json](evidence/decisive-run-01/decisive-result.json).

## Authoring change

`author_target` still emits only `lhs_entity`, `rhs_entity`, and `comparison_direction` for `strict_comparison`.

Three frames sit beside the closed #184 frame:

- copular: a nominal, `is`/`was`/`were`, a bound relation, and `than` plus the other nominal
- likelihood: a nominal, `was`/`were`, `more`/`less likely than`, the other nominal, and a `to` complement
- complex measure: a capitalized entity, `had a` bound relation, a multi-word measure, `than`, and another capitalized entity, with an optional trailing prepositional adjunct

One sentence-initial prepositional adjunct is recognized and left unstored. The likelihood complement, the multi-word measure, and any trailing adjunct are also recognized and left unstored. The closed single-measure frame stays end-bounded, so `Alpha had a higher rate than Beta in 2025.` still refuses.

I kept that residue out of the entity strings. Putting it there would have made the collision controls look distinct without giving the field model a slot for the difference.

## Fourteen-claim field readout

The decisive file records 14 authored claims and no authentic-claim failure. It does not store the field strings. This table is `author_target` on implementation `eb1de81`.

| Case | Direction | Left nominal | Right nominal |
| --- | --- | --- | --- |
| REAL-S01-F | `LESS_THAN` | The rate of firearm-related violent crime in Canada in 2023 | the rate in 2022 |
| REAL-S01-I | `MORE_THAN` | The rate of firearm-related violent crime in Canada in 2023 | the rate in 2022 |
| REAL-S02-F | `MORE_THAN` | The police-reported crime rate in provincial rural areas in 2023 | the rate in provincial urban areas in 2023 |
| REAL-S02-I | `LESS_THAN` | The police-reported crime rate in provincial rural areas in 2023 | the rate in provincial urban areas in 2023 |
| REAL-S03-F | `MORE_THAN` | The employment rate of fathers in 2023 | the employment rate of mothers in 2023 |
| REAL-S03-I | `LESS_THAN` | The employment rate of fathers in 2023 | the employment rate of mothers in 2023 |
| REAL-S04-F | `MORE_THAN` | the age- and sex-adjusted Indigenous incarceration rate in 2020/2021 | the corresponding non-Indigenous rate |
| REAL-S04-I | `LESS_THAN` | the age- and sex-adjusted Indigenous incarceration rate in 2020/2021 | the corresponding non-Indigenous rate |
| REAL-S05-F | `MORE_THAN` | women | men |
| REAL-S05-I | `MORE_THAN` | men | women |
| REAL-S08-F | `MORE_THAN` | Gumarey | Sogan-Godud |
| REAL-S08-I | `LESS_THAN` | Gumarey | Sogan-Godud |
| REAL-S10-F | `MORE_THAN` | the microbiological total count of water used by Diamond Wipes for manufacturing | its action limit |
| REAL-S10-I | `LESS_THAN` | the microbiological total count of water used by Diamond Wipes for manufacturing | its action limit |

S01 through S04, S08, and S10 keep both nominals and flip direction. S05 swaps the nominals and keeps `MORE_THAN`.

## Modifier collisions

Each mutation authored. `fields_changed` is false. The result file names the failure kind `target_field_collision`.

| Control | Unstored difference | Fields that stayed identical |
| --- | --- | --- |
| COLLIDE-S04-SCOPE | sentence-initial scope, `In the five provinces studied` versus `In all provinces` | S04 left nominal, `the corresponding non-Indigenous rate`, `MORE_THAN` |
| COLLIDE-S05-MEASURE | measured-property complement, `report COPD` versus `report asthma` | `women`, `men`, `MORE_THAN` |
| COLLIDE-S08-SCOPE | trailing age-group restriction, `in almost all age groups` versus `in all age groups` | `Gumarey`, `Sogan-Godud`, `MORE_THAN` |
| COLLIDE-S10-QUANTIFIER | instance count, `eight` versus `two` reported instances | S10 left nominal, `its action limit`, `MORE_THAN` |

`age- and sex-adjusted` remains inside the S04 left nominal. This cohort does not mutate that premodifier, so the run does not show whether adjustment needs its own slot.

## Negative and metamorphic controls

Refused as an unsupported claim form:

- `NEG-EQUALITY`
- `NEG-MULTIPLE-CUES`
- `NEG-MISSING-RHS`
- `NEG-AMBIGUOUS-PAIR`
- `NEG-UNBOUND-DIRECTION`

`NEG-OTHER-FAMILY` authored as `direct_event_order`. `BASE-HIGHER` and `BASE-LOWER` stayed Alpha/Beta with `MORE_THAN` and `LESS_THAN`. `META-BASE-SWAP` swapped the sides and flipped the direction. Nothing in the negative set was accepted as `strict_comparison`.

## Regressions

The #184 authoring qualification passed on the second invocation. Python 3.11.15. Frozen CAL `e24e405f5336ee024674f39dba97255bb58a2dd9`. Evidence Bundler `4e1f6fe00e7c350b28f52bfea14f1f8988847884`. C1 and C2 were byte-identical to the frozen trusted targets, and both runs concluded `supported`. Eight weak controls were accepted by the existing structural validator and rejected by conformance. Five out-of-aperture claims refused, including `Alpha had a higher rate than Beta in 2025.` Qualification receipt SHA-256: `d86a09040ed54a5bea3a34595ffbf083ed04fcd6ad1b5b9dc3e593fed82fc4d7`.

The first qualification attempt used the workbench virtualenv. That environment cannot import `evidence_bundler`, so the frozen fixture skipped before the qualification body ran. I reran with the existing convergence 3.11 environment. No authoring code changed between the attempts.

`pytest -q` from this worktree, same Python 3.11.15: 985 passed, 5 skipped, 48 deselected. An earlier invocation collected tests from outside the worktree and stopped during collection. The passing run is the one rooted in this worktree.

`ruff check src tests` passed. `ruff format --check src` passed, 72 files already formatted. `mypy` reported no issues in 71 source files.

From `6bb0d60` through `eb1de81`, the semantic package, Contract B, Contract C, parent composition, package metadata, frozen cases, and frozen evaluator are unchanged. The implementation diff is `src/claim_audit_lab/production_v1/targeting.py` and `tests/test_production_v1_targeting.py`.

## Inference

These claims can be reduced to two nominals and a direction. That reduction drops the four differences the collision controls change: initial scope, a measured-property complement, a trailing age restriction, and an instance count. The identical fields are the preregistered falsifier for the existing target field model.

## Non-claims

- This does not say the fourteen claims are unauthorable under another representation.
- This does not change measurement, source completion, relation derivation, or conclusion logic.
- This does not establish end-to-end audit behavior on these real claims.
- This does not integrate the authoring change into the polarity successor.
- This does not open a held-out cohort. That step was for a supported result.
- Package version stays `0.6.0`. This branch stays unmerged.

## Next experiment

Stop extending this grammar. The next experiment needs a new representation candidate, with its cases frozen before the implementation, that can distinguish these four mutations without sentence-specific exceptions. The open question is whether one added slot can carry all four differences, or whether scope, property complement, trailing restriction, and instance cardinality have to be separate. I would not answer that by editing `eb1de81`.

Adjustment is still untested as its own mutation. A later case can change `age- and sex-adjusted` while holding the rest of the S04 nominal fixed, if we need to know whether leaving it inside the nominal is enough.
