# Independent NLI Disagreement + Calibration Cohort RC2 — Results

## Terminal disposition

**SUPPORTED FOR SUCCESSOR RESEARCH**

RC2 independently reproduces the core RC1 finding that **inter-model disagreement is enriched for semantic error**, and separately establishes that simple model-specific temperature scaling materially improves held-out reliability metrics for all three entailers.

RC2 does **not** support probability averaging as a better CAL ensemble decision rule. The calibrated and uncalibrated equal-weight probability means produced exactly the same held-out labels, and both produced more false-adverse neutral→contradiction errors than the incumbent or adverse-conservative categorical ensemble.

No production change is authorized.

## Frozen authority

- production main at experiment start: `53f0885b111676794d1bd20e10b91aa58b07e9d4`
- RC1 terminal parent: `7ce57893eada43de9d4ee77281854f78a07ad0c2`
- RC2 preregistration: `3fc060228406b52aa65d4a3eb35579ffc7dff335`
- accepted cohort freeze head: `53b1a9d1de4fac86445bfd85bb3a4ae3bf3cbbf9`
- accepted cohort freeze run: `33288951809`
- frozen cohort artifact: `9725345054`
- frozen cohort SHA256: `c5f64d6ad73d198aef575b5274280363bb71fc99aac78197e3abf13b13599f2d`
- accepted science execution head: `1c057c1aeb7c6501704efb347c46fc9c56d20e3a`
- accepted science run: `33289051885`
- accepted science artifact: `9725451970`
- artifact digest: `sha256:6e4e0c97b72d8295072b6cc157786186ce9912dff3d2a6233b644c515431734f`
- frozen measurement SHA256: `1751b4fd16eefbcea114cca406302e05d66d2c73848c078d7d96153e9aac0ae3`
- frozen result SHA256: `48d57996666b9ecf3176ee270fd20201acca56a2c1ca61d1ac149de2983e26ed`

## Independent cohort

The cohort was frozen before any model execution.

- 72 new premise/hypothesis pairs;
- 24 entailment / 24 neutral / 24 contradiction;
- 36 calibration-only / 36 untouched evaluation;
- each split contains 12 entailment / 12 neutral / 12 contradiction;
- six semantic families:
  - quantifier / scope;
  - explicit exceptions;
  - modality / deontic force;
  - entity / population scope;
  - temporal qualifiers;
  - conditional / causal language.

Typed arithmetic, source completeness, evidence-set conjunction and multi-hop composition were excluded.

All primary inputs fit within the ordinary 512-token aperture. RC2 therefore measures semantic relation and calibration rather than the aperture effect already isolated in RC0/RC1.

## Individual model performance on untouched evaluation

| Model | Correct | Accuracy | Macro-F1 | Neutral→contradiction | False adverse |
|---|---:|---:|---:|---:|---:|
| incumbent base | 26/36 | 72.2% | 0.714 | 3 | 3 |
| same-family large | **30/36** | **83.3%** | **0.830** | **2** | **2** |
| long-context base | 27/36 | 75.0% | 0.745 | 4 | 4 |

### OBSERVED

The larger same-family model is the strongest individual model on this independent held-out cohort.

It correctly classified all 12 contradiction targets, 9/12 entailment targets, and 9/12 neutral targets.

### INFERENCE

The RC0 short-context signal for the larger Laurer model reproduces more convincingly here. Capacity/training breadth is a real candidate improvement for ordinary short-context semantic measurement.

This still does not justify production replacement. In particular, it retains two neutral→contradiction false-adverse errors.

## Disagreement replication

On the 36 untouched evaluation cases:

- unanimous model labels: 27 cases;
- disagreement: 9 cases;
- incumbent error rate conditional on unanimity: **14.8%**;
- incumbent error rate conditional on disagreement: **66.7%**;
- relative risk of incumbent error under disagreement: **4.5×**;
- polar entailment-vs-contradiction conflicts: 2;
- incumbent error rate on polar conflicts: **100%**;
- the correct label appeared among the three model votes on 32/36 cases.

Disagreement case IDs:

`IC2-008, IC2-011, IC2-015, IC2-020, IC2-023, IC2-043, IC2-052, IC2-063, IC2-067`

### RC1 replication criterion

**SUPPORTED.**

1. incumbent error rate is materially higher under disagreement than under unanimity;
2. adverse-conservative selective accuracy is 84.4%, above incumbent overall accuracy of 72.2%;
3. adverse-conservative false-adverse decisions fall from 3 to 2 rather than increasing.

The exact RC1 pattern did not reproduce, nor was it expected to: disagreement is not a perfect error detector.

### COUNTEREXAMPLE — unanimous error

Four unanimous evaluation cases were wrong:

- `IC2-016` — exceptions, target entailment, all three neutral;
- `IC2-019` — exceptions, target neutral, all three entailment;
- `IC2-044` — entity/population scope, target neutral, all three contradiction;
- `IC2-056` — temporal qualifier, target neutral, all three contradiction.

**INFERENCE.** Agreement is useful evidence about measurement stability, not correctness authority.

## Ensemble systems on untouched evaluation

| System | Correct/all | Decided | Selective accuracy | Wrong decided | Neutral→contradiction | False adverse |
|---|---:|---:|---:|---:|---:|---:|
| S0 incumbent | 26/36 | 36 | 72.2% | 10 | 3 | 3 |
| S1 majority | 28/36 | 35 | 80.0% | 7 | 3 | 3 |
| S2 adverse-conservative | 27/36 | 32 | **84.4%** | **5** | **2** | **2** |
| S3 native probability mean | 28/36 | 36 | 77.8% | 8 | 4 | 4 |
| S4 calibrated probability mean | 28/36 | 36 | 77.8% | 8 | 4 | 4 |

### Majority vote

**INFERENCE.** Majority vote improves raw correctness over the incumbent, but does not improve the false-adverse boundary. It preserves three neutral→contradiction errors.

This remains too eager for CAL's epistemic semantics.

### Adverse-conservative categorical consensus

**SUPPORTED FOR SUCCESSOR RESEARCH.**

It provides the strongest selective behavior:

- 32/36 decided;
- 27 correct;
- 84.4% selective accuracy;
- 5 wrong decided;
- 2 false-adverse outputs;
- 4 unresolved.

It is not the highest full-coverage accuracy system. The large individual model reaches 83.3% at full coverage versus S2's 75.0% when unresolved is counted as wrong.

Its value is narrower: it uses disagreement to trade coverage for lower decided error and lower adverse error.

## Calibration

One scalar temperature was fit per model using only the 36 calibration cases.

Fitted temperatures:

| Model | Temperature |
|---|---:|
| incumbent base | 2.658 |
| same-family large | 2.210 |
| long-context base | 1.739 |

All are greater than 1.0, consistent with overconfident native logits on the calibration cohort.

### Calibration split reliability

| Model | Native NLL | Cal NLL | Native Brier | Cal Brier | Native ECE | Cal ECE |
|---|---:|---:|---:|---:|---:|---:|
| incumbent | 1.065 | **0.710** | 0.574 | **0.434** | 0.269 | **0.182** |
| large | 0.768 | **0.554** | 0.413 | **0.339** | 0.206 | **0.178** |
| long | 0.632 | **0.538** | 0.326 | **0.298** | 0.175 | **0.108** |

### Untouched evaluation reliability

| Model | Native NLL | Cal NLL | Native Brier | Cal Brier | Native ECE | Cal ECE |
|---|---:|---:|---:|---:|---:|---:|
| incumbent | 0.896 | **0.630** | 0.451 | **0.366** | 0.215 | **0.103** |
| large | 0.663 | **0.478** | 0.306 | **0.269** | 0.152 | **0.116** |
| long | 0.695 | **0.576** | 0.408 | **0.353** | 0.183 | **0.136** |

### H1 — calibration validity

**SUPPORTED ON THIS COHORT.**

Model-specific scalar temperature scaling improves held-out NLL, Brier and 10-bin ECE for all three models.

Calibration also lowers mean confidence on both correct and incorrect predictions, rather than changing class decisions. Scalar temperature preserved every individual-model argmax as required.

### Important semantic limit

**FACT.** Better calibration does not make a wrong semantic label correct.

For example, a calibrated model may become appropriately less confident about a neutral→contradiction mistake while retaining the contradiction argmax.

Calibration therefore belongs in the measurement receipt, not as a substitute for semantic validity.

## Probability averaging

### S3 — uncalibrated mean

28/36 correct, but with 4 false-adverse / neutral→contradiction errors.

### S4 — calibrated mean

Exactly the same 28/36 labels and the same four false-adverse errors.

### H2 — calibrated averaging

**FALSIFIED IN RC2.**

Calibration improved individual reliability, but did not improve the equal-weight ensemble's held-out classification at all.

S4:

- did not improve over S3;
- did not improve over the large individual model;
- increased false-adverse count versus the incumbent (4 vs 3);
- increased false-adverse count versus the adverse-conservative categorical rule (4 vs 2).

Raw or calibrated score averaging is therefore not supported as CAL's semantic aggregation rule by RC2.

### H3 — score comparability

**INCONCLUSIVE / WEAKLY NOT SUPPORTED.**

There is evidence that model-specific temperature scaling makes each model's confidence more reliable on this cohort.

There is no evidence that this improved reliability makes equal-weight cross-model probability averaging a better semantic decision surface.

The strongest supported use of calibration is therefore **per-model reliability metadata**, not probability fusion.

## Family-level findings

Held-out accuracy by family exposes substantial heterogeneity.

### Incumbent

- conditional/causal: 5/6;
- entity/population: 4/6;
- exceptions: **2/6**;
- modality: 6/6;
- quantifier/scope: 4/6;
- temporal: 5/6.

### Adverse-conservative ensemble

Counting unresolved as not correct:

- conditional/causal: 6/6;
- entity/population: 4/6;
- exceptions: **1/6**;
- modality: 6/6;
- quantifier/scope: 5/6;
- temporal: 5/6.

### Probability means

Both S3 and S4:

- conditional/causal: 6/6;
- entity/population: 4/6;
- exceptions: **1/6**;
- modality: 6/6;
- quantifier/scope: 6/6;
- temporal: 5/6.

### INFERENCE

Explicit exception semantics are the clearest hard family in RC2.

Neither multi-model agreement, calibrated averaging, nor simple voting solves the family. Two of the four unanimous errors are exception cases.

A smaller next test should target exception/scope interpretation directly rather than adding more generic ensemble complexity.

## Competing explanations

### “Disagreement only looked useful because RC1 was tiny”

Disfavored, not eliminated.

The effect reproduces on 36 untouched balanced evaluation cases, with a 4.5× incumbent error-risk ratio under disagreement.

The cohort remains constructed and shares semantic-family design between calibration and evaluation, so real-domain generalization is still unknown.

### “Unanimity can be used as truth”

Rejected.

Four held-out cases are unanimously wrong.

### “Calibration makes model probabilities interchangeable”

Not established.

Reliability improves per model; probability averaging does not.

### “The ensemble beats every individual model”

Rejected.

The large same-family model is the strongest full-coverage classifier at 30/36.

The conservative ensemble's advantage is selective-risk behavior, not full-coverage accuracy.

### “All hard cases are neutral”

Rejected.

Neutral remains the weakest critical boundary, but errors also occur on entailment and contradiction. Exception handling is a cross-label failure family.

## Preserved deviations

### Cohort freeze attempt 1 — run `33288935143`

The cohort builder validated and materialized the exact eventual accepted cohort SHA, but the standalone unittest invocation discovered zero pytest-style test functions.

No model executed.

Repair: convert only the validation test harness to real `unittest.TestCase` methods.

Accepted freeze run `33288951809` ran 2/2 tests and reproduced the exact same cohort SHA.

### Science attempt 1 — run `33289016892`

Stopped before any model execution at Ruff.

The frozen cohort source contained intentionally dense tuple literals that violated line-length style, plus minor post-freeze scorer/test style findings.

The sealed cohort source was **not reformatted**.

Repair:
- fix scorer/test formatting only;
- scope lint to post-freeze scoring apparatus rather than sealed cohort authority.

### Intermediate repair runs — `33289048748`, `33289050411`

Both stopped at the same pre-science lint stage while sequential repair commits were landing. Science was skipped.

Accepted science run: `33289051885`.

## Architectural implication

The evidence now supports keeping three concepts separate:

1. **native semantic measurement**
   - model identity;
   - native logits;
   - native probabilities;
   - relation label;

2. **measurement reliability**
   - model-specific calibration map;
   - calibrated confidence vector;
   - evidence/aperture eligibility;

3. **cross-model comparison**
   - unanimity;
   - disagreement;
   - polar conflict;
   - conservative unresolved state.

A calibrated probability average should not replace these explicit fields.

A candidate research object remains closer to:

```
semantic_measurement_set:
  measurements:
    - model_id
      relation
      native_scores
      calibrated_scores
      evidence_visible
  comparison:
    unanimous
    disagreement_class
    polar_conflict
    conservative_measurement_state
```

than to a single averaged confidence scalar.

## Next smallest discriminating work

1. **Exception / scoped-rule RC.**
   Build matched exception cases that separate:
   - exception means opposite;
   - exception means unspecified;
   - alternate process;
   - temporary exception;
   - exception to one obligation versus broader exemption.

2. **Real-trace disagreement incidence.**
   Shadow the three entailers on frozen real CAL evidence pairs and measure how often disagreement occurs, without changing production decisions.

3. **Cost-aware cascade.**
   Test whether the incumbent can run first and invoke large/long specialists only when phenomenon or measurement-risk signals justify it, versus always paying for all three.

4. **Calibration preservation.**
   Keep model-specific temperature scaling as research reliability metadata and test it under domain shift before treating calibrated confidence as operationally comparable.

## Non-authorization

RC2 does not authorize:

- production entailer replacement;
- production multi-entailer execution;
- majority voting;
- unanimity as truth;
- probability averaging;
- Contract C changes;
- semantic-operator changes;
- threshold changes;
- downstream policy changes;
- treating calibrated model confidence as a posterior probability of truth.
