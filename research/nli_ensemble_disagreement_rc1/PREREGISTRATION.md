# NLI Ensemble / Disagreement RC1 — Preregistration

## Classification

Research Infrastructure / semantic-measurement aggregation experiment.

This experiment consumes only the frozen outputs of NLI Measurement Discrimination RC0. It does not re-run, retrain, recalibrate, fine-tune, replace, or otherwise alter any entailer.

It does not authorize production model replacement, threshold changes, semantic-operator changes, aggregation-policy changes, Contract C changes, or decision-policy changes.

## Question

Can a small, explicit multi-entailer rule improve CAL's semantic measurement behavior by using **agreement and disagreement as evidence**, without collapsing neutral into contradiction or pretending raw model softmax values share a common probabilistic scale?

## Frozen authority

- production main: `53f0885b111676794d1bd20e10b91aa58b07e9d4`
- frozen Cohort A science head: `ba1310d73ab63adf7c83de2f1e130f7f00a665af`
- NLI RC0 branch terminal head / RC1 parent: `b316d115c82fb635b0e089d43342b4b6e75c326e`
- NLI RC0 accepted execution head: `8e4267e42e2be0615c20da79b74988e4f1747668`
- NLI RC0 accepted Actions run: `33286762938`
- NLI RC0 artifact ID: `9724863795`
- artifact ZIP SHA256: `4a1653aca619921eaa1393b7085a33a031342f969ae0284134a3d1c58cf60a36`
- frozen RC0 INPUTS SHA256: `6c1780a05c5720d0f8c2d20b0109198939846a8f6ea6d47ef6c79afeaa73c5ab`
- frozen RC0 RESULTS SHA256: `07eb1a99927226779e5071959c527f7a7d280afebe23855e1f1ae058cc425caf`

The three frozen measurement instruments are:

1. `incumbent_base`
2. `same_family_large`
3. `long_context_base`

## No score normalization in RC1

Raw softmax values are not assumed comparable across models.

RC1 therefore does **not**:

- average raw probabilities;
- z-score or min-max normalize probabilities;
- fit temperature scaling;
- fit isotonic/logistic calibration;
- learn model weights;
- choose thresholds from the 14 evaluation targets.

Reason: the frozen primary slice has only 14 cases and only one neutral target. Fitting a normalization or weighting layer to this same target set would leak evaluation labels into the aggregator.

A later calibration experiment requires a separately frozen calibration cohort.

## Frozen evaluation surfaces

RC1 evaluates the exact 14 primary RC0 cases and their exact three frozen input variants:

- `short`
- `stress_head`
- `stress_tail`

Targets remain unchanged from RC0:

- `restates` → entailment
- `weakens` → entailment
- `contradicts` → contradiction
- `overgeneralizes` → neutral

No operator-owned, source-boundary, numeric-bound, conjunction, partial-conjunction, or chain relation may enter the ensemble ranking.

## Ensemble rules

Every rule returns one of:

- `entailment`
- `neutral`
- `contradiction`
- `unresolved`

### R0 — incumbent baseline

Return the frozen incumbent label.

Purpose: reference.

### R1 — simple majority vote

Return any label receiving at least two of three votes.

Purpose: test ordinary ensemble voting.

### R2 — unanimity-only

Return a semantic label only if all three models agree. Otherwise return `unresolved`.

Purpose: maximum agreement conservatism.

### R3 — polar-conflict abstention

If at least one model predicts entailment and at least one predicts contradiction, return `unresolved`. Otherwise return the majority label.

Purpose: test whether direct positive/adverse disagreement is a useful abstention signal while retaining majority resolution for neutral-vs-one-pole disagreement.

### R4 — adverse-conservative consensus

Rules in order:

1. return `contradiction` only if all three models predict contradiction;
2. return `entailment` if at least two models predict entailment and none predicts contradiction;
3. return `neutral` if at least two models predict neutral and none predicts contradiction;
4. otherwise return `unresolved`.

Purpose: protect against invented adverse conclusions. This rule is intentionally asymmetric.

### R5 — aperture-aware specialist routing

If either 512-position model is truncated on the frozen input variant and the long-context model is not truncated, return the long-context model's frozen label.

Otherwise apply R4.

Purpose: test whether context visibility should control model routing rather than be averaged into an ensemble.

No performance-derived routing thresholds are permitted.

## Primary metrics

For every rule and input variant report:

- decided coverage = decided / 14;
- exact matches among all 14, counting unresolved as not exact;
- selective accuracy = correct / decided;
- total wrong decided outputs;
- false-adverse count = target != contradiction AND output == contradiction;
- neutral→contradiction count;
- contradiction→neutral count;
- contradiction→entailment count;
- entailment→contradiction count;
- unresolved count;
- per-target decided/correct counts.

Because there is only one neutral target, the neutral false-adverse metric is reported as a counterexample count, not as a reliable rate estimate.

## Disagreement diagnostics

For each case/variant record:

- vote pattern;
- number of distinct labels;
- whether there is entailment-vs-contradiction polar conflict;
- whether all models agree;
- whether majority is correct;
- whether disagreement contains the correct label;
- whether abstention would avoid an incumbent error;
- whether abstention would discard an incumbent-correct result.

## Preregistered questions / falsifiers

### Majority-vote hypothesis

Supported only if R1 reduces wrong decided outputs versus R0 **without increasing false-adverse outputs**.

Falsified if majority voting preserves or creates a confident consensus error in the neutral/overgeneralization case or otherwise increases adverse error.

### Disagreement-as-signal hypothesis

Supported if R2/R3/R4 materially increase selective accuracy by abstaining on errors more often than on correct cases.

Falsified if disagreement is not enriched for error and conservative abstention mainly throws away correct measurements.

### Adverse-conservative hypothesis

Supported if R4 eliminates or reduces false-adverse outputs while retaining useful decided coverage.

Its purpose is not maximum raw accuracy.

### Aperture-routing hypothesis

Supported if R5 materially outperforms non-routed rules on `stress_tail` without harming `short` and `stress_head`, using only the frozen truncation state as the router.

Falsified if long-context routing fails to recover the known aperture degradation or creates offsetting semantic errors.

## Promotion boundary

RC1 can support a **research design** for a multi-entailer measurement object.

RC1 cannot support production implementation because:

- the cohort is small;
- neutral coverage is one case;
- all rules are evaluated on the same construction family that motivated them;
- calibration/normalization has not been independently tested;
- runtime/cost incidence is not evaluated here.

## Stop conditions

Stop interpretation if:

- RC0 artifact hashes do not match;
- any per-model frozen output is missing;
- any target or model output is regenerated or changed;
- any ensemble rule is changed after outputs are inspected;
- operator-owned cases are added to improve an ensemble score;
- learned weights, calibrated probabilities, or thresholds are fitted on the 14 evaluation targets.

## Allowed disposition

- **SUPPORTED FOR SUCCESSOR RESEARCH**
- **FALSIFIED**
- **INCONCLUSIVE**
- **SUPERSEDED**
