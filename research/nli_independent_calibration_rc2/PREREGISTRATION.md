# Independent NLI Disagreement + Calibration Cohort RC2 — Preregistration

## Classification

Research Infrastructure / semantic-measurement calibration and externalized disagreement replication.

This successor is stacked only on NLI Ensemble / Disagreement RC1. It is independent of the operator-authority and local-v2 reconciliation lines.

It does not authorize production model replacement, production ensemble implementation, threshold tuning against evaluation gold, semantic-operator changes, Contract C changes, aggregation changes, or downstream decision-policy changes.

## Questions

1. Does the RC1 finding that inter-model disagreement is enriched for semantic error reproduce on a new balanced cohort?
2. Does model-specific post-hoc calibration make three-way NLI score vectors more comparable on held-out data?
3. Does equal-weight averaging of calibrated distributions improve held-out semantic measurement versus:
   - the incumbent;
   - majority vote;
   - RC1 adverse-conservative categorical consensus;
   - equal-weight averaging of uncalibrated distributions?
4. Do calibration gains preserve CAL's critical neutral-versus-contradiction boundary?

## Frozen authority

- production main observed before branch creation: `53f0885b111676794d1bd20e10b91aa58b07e9d4`
- RC1 terminal parent: `7ce57893eada43de9d4ee77281854f78a07ad0c2`
- RC1 accepted run: `33288443965`
- RC1 artifact: `9725192045`
- RC1 frozen measurement projection: `sha256:a575966ca1089d43d7fdf162e01d15bfa2f06b8ab8afec95a826aa121dc132b7`
- RC1 evaluator result: `sha256:bc806409d776de70324865642b6d582f8f33341de8173b06e26fbfddab3143df`

## Models

Use the exact three RC0/RC1 model revisions:

1. `MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli@6f5cf0a2b59cabb106aca4c287eed12e357e90eb`
2. `MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli@0de4830e69aa5710af98b05f2c4d001d0edc0e52`
3. `tasksource/deberta-base-long-nli@d6e08f68489c9ac015ba3071f90ac0976cbc1fff`

All must expose an unambiguous three-way entailment / neutral / contradiction label map.

## Independent cohort design

Freeze **72 new premise-hypothesis cases before any model execution**.

No case may reuse an RC0/Cohort-A claim or decisive passage text.

### Labels

Exactly:

- 24 entailment;
- 24 neutral;
- 24 contradiction.

### Splits

Exactly:

- 36 calibration cases;
- 36 evaluation cases.

Each split contains:

- 12 entailment;
- 12 neutral;
- 12 contradiction.

The evaluation split is untouched by calibration fitting, calibration-model selection, temperature fitting, or rule revision.

### Semantic families

Exactly 12 cases per family, balanced 4/4/4 across entailment / neutral / contradiction, with 6 calibration and 6 evaluation cases per family:

1. quantifier and scope;
2. explicit exceptions;
3. modality / deontic force;
4. entity and population scope;
5. temporal qualifiers;
6. conditionals and causal language.

Typed arithmetic, numeric bounds, source-completeness claims, evidence-set conjunction, and multi-hop composition are excluded from this RC because they have separate semantic-owner questions.

## Cohort freeze protocol

1. Commit this preregistration.
2. Commit the complete 72-case cohort plus validator.
3. Run a cohort-only validation workflow with no model dependencies and no model execution.
4. Record the exact cohort SHA256 and validation run.
5. Only then add/execute model scoring and calibration apparatus pinned to that cohort SHA.

Any change to premise, hypothesis, label, family, or split after first model execution invalidates the experiment.

## Model scoring

For every case/model record:

- raw logits;
- native three-way softmax;
- argmax relation;
- untruncated token count;
- encoded token count;
- truncation state.

Primary RC2 cases must fit within 512 tokens so that the comparison tests semantics/calibration rather than aperture. Any case truncated by either 512-position model is excluded as an apparatus failure and reported.

Run a deterministic sentinel repetition before interpretation.

## Calibration

Fit **one positive scalar temperature per model** using only the 36 calibration cases.

Objective: minimize multiclass negative log likelihood over calibration logits.

Constraints:

- no class-specific temperatures;
- no per-domain temperatures;
- no learned ensemble weights;
- no evaluation labels during fitting;
- no model selection based on evaluation outputs.

Optimization may use a deterministic one-dimensional bounded numerical search over a preregistered interval `T ∈ [0.05, 20.0]`.

Record fitted temperature and calibration-split NLL before/after.

## Held-out evaluation systems

Evaluate these fixed systems on the 36 evaluation cases:

### S0 incumbent
Incumbent argmax.

### S1 majority
Majority vote over the three native argmax labels.

### S2 adverse-conservative categorical consensus
Same RC1 R4 rule:
- contradiction only at 3/3 contradiction;
- entailment at >=2 entailment with zero contradiction;
- neutral at >=2 neutral with zero contradiction;
- otherwise unresolved.

### S3 uncalibrated probability mean
Arithmetic mean of the three native softmax vectors, equal model weight, then argmax.

### S4 calibrated probability mean
Apply each model's calibration-only fitted temperature to its logits, compute softmax, arithmetic mean the three calibrated vectors with equal weight, then argmax.

No evaluation-set abstention threshold is permitted for S3/S4.

## Evaluation metrics

Per model and system, on held-out evaluation only:

- exact accuracy;
- macro-F1;
- confusion matrix;
- neutral→contradiction count;
- entailment→contradiction count;
- false-adverse count where target != contradiction and output == contradiction;
- contradiction→neutral count;
- contradiction→entailment count.

For S2 also report:
- coverage;
- selective accuracy;
- unresolved count;
- errors avoided versus incumbent;
- incumbent-correct cases discarded.

For each individual model before/after calibration:
- NLL;
- multiclass Brier score;
- ECE with fixed 10 equal-width confidence bins;
- classwise mean confidence on correct and incorrect predictions.

Calibration is not allowed to change argmax labels for a single model because scalar temperature preserves logit ordering; if observed otherwise, stop.

## Disagreement replication metrics

On evaluation cases only report:

- number of unanimous cases;
- unanimous error rate;
- number of disagreement cases;
- incumbent error rate conditional on disagreement;
- incumbent error rate conditional on unanimity;
- relative risk of incumbent error under disagreement versus unanimity where denominator is defined;
- whether the correct label appears among the three model votes;
- polar entailment-vs-contradiction conflict count and error enrichment.

### RC1 replication criterion

The disagreement-as-signal hypothesis is supported for successor research only if:

1. incumbent error rate on disagreement cases is greater than incumbent error rate on unanimous cases; and
2. S2 selective accuracy exceeds incumbent overall accuracy; and
3. S2 does not increase false-adverse decisions.

Exact RC1 perfection is not required and should not be expected.

## Calibration hypotheses / falsifiers

### H1 calibration validity
Supported if model-specific temperature scaling improves held-out NLL or Brier score for at least two models without material ECE degradation.

Falsified if calibration improvement exists only on the fitting split and held-out reliability is unchanged or worse across models.

### H2 calibrated averaging
Supported if S4 improves over S3 and S0 on a preregistered combination of:
- fewer wrong outputs;
- no increase in false-adverse count;
- neutral accuracy not worse than S0.

A raw accuracy gain that increases neutral→contradiction errors does not support H2.

### H3 score comparability
Only weakly supported if separately calibrated models show improved held-out reliability and S4 improves over S3.

Temperature scaling does not establish that model probabilities are epistemic posteriors or universally comparable across domains.

## Competing explanations

Before any positive disposition, check:

- disagreement may simply reflect model-family diversity rather than uncertainty;
- models share substantial architecture/training ancestry, so agreement can be correlated error;
- template families may induce lexical regularities;
- calibration/evaluation halves share semantic families and may still be easier than real domain shift;
- scalar calibration can improve average reliability while hiding class-specific neutral failures;
- equal-weight averaging may merely approximate the strongest individual model.

## Allowed disposition

- **SUPPORTED FOR SUCCESSOR RESEARCH**
- **FALSIFIED**
- **INCONCLUSIVE**
- **SUPERSEDED**

No production promotion is possible from RC2 alone.
