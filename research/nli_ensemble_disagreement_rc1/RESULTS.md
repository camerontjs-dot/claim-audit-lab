# NLI Ensemble / Disagreement RC1 — Results

## Terminal disposition

**SUPPORTED FOR SUCCESSOR RESEARCH**

The frozen RC0 measurements provide a strong seed result for a multi-entailer measurement architecture, but do **not** justify production implementation.

Two distinct mechanisms are supported:

1. on clean short inputs, **inter-model disagreement is strongly enriched for semantic error**;
2. when decisive evidence can fall outside a 512-token aperture, **visibility-aware routing to a long-context specialist sharply outperforms voting among truncated models**.

Neither unanimity nor majority vote is safe enough to become semantic truth authority.

## Frozen authority

- production main: `53f0885b111676794d1bd20e10b91aa58b07e9d4`
- NLI RC0 terminal parent: `b316d115c82fb635b0e089d43342b4b6e75c326e`
- RC1 preregistration commit: `bcd110de783cafaf7fc705480746466940f13e3a`
- accepted RC1 execution head: `aca0f84fd16d7dad128c038b139cb7ab00b232a3`
- accepted Actions run: `33288443965`
- accepted artifact ID: `9725192045`
- artifact digest: `sha256:3659dfcddcf6fe2b4c4155768736cf0bde0b09e7bc165209df622ec45184e405`
- frozen measurement projection SHA256: `a575966ca1089d43d7fdf162e01d15bfa2f06b8ab8afec95a826aa121dc132b7`
- frozen evaluator RESULTS SHA256: `bc806409d776de70324865642b6d582f8f33341de8173b06e26fbfddab3143df`

No entailer was re-run. No raw score normalization, learned weighting, calibration, threshold tuning, production model change, operator change, Contract C change, aggregation change, or decision-policy change occurred.

## Frozen rules

- **R0** incumbent baseline
- **R1** simple majority vote
- **R2** unanimity-only, otherwise unresolved
- **R3** entailment-vs-contradiction polar conflict → unresolved, otherwise majority
- **R4** adverse-conservative consensus:
  - contradiction requires 3/3 contradiction;
  - entailment requires >=2 entailment and no contradiction;
  - neutral requires >=2 neutral and no contradiction;
  - otherwise unresolved
- **R5** aperture-aware specialist routing:
  - if a 512-position model is truncated and the 1280-position model is not, use the long-context model;
  - otherwise apply R4

## Short-input results

| Rule | Decided | Correct | Selective accuracy | Wrong decided | False adverse | Unresolved |
|---|---:|---:|---:|---:|---:|---:|
| R0 incumbent | 14/14 | 11 | 78.6% | 3 | 2 | 0 |
| R1 majority | 14/14 | 12 | 85.7% | 2 | 1 | 0 |
| R2 unanimity | 11/14 | 11 | **100%** | **0** | **0** | 3 |
| R3 polar abstain | 12/14 | 11 | 91.7% | 1 | 0 | 2 |
| R4 adverse-conservative | 11/14 | 11 | **100%** | **0** | **0** | 3 |
| R5 aperture route | 11/14 | 11 | **100%** | **0** | **0** | 3 |

### OBSERVED — disagreement concentration

Exactly three short cases have non-unanimous model labels:

| Case | Target | Incumbent | Large | Long | Majority | R4 |
|---|---|---|---|---|---|---|
| CG-18 | neutral | contradiction | contradiction | entailment | contradiction | unresolved |
| CG-19 | contradiction | neutral | contradiction | neutral | neutral | unresolved |
| CG-20 | entailment | contradiction | entailment | entailment | entailment | unresolved |

These are also **exactly the three incumbent short-input errors**.

The other 11 short cases are unanimous and all 11 are correct.

### INFERENCE

On this frozen seed cohort, disagreement is a much better error signal than incumbent softmax confidence.

This is particularly important for CG-18. Two models vote contradiction and one votes entailment while the stipulated target is neutral. Majority voting therefore turns disagreement into an adverse error. R2/R4 instead preserve the measurement conflict.

### Majority-vote hypothesis

**PARTIALLY SUPPORTED, BUT NOT SAFE FOR CAL.**

R1 improves 11/14 → 12/14 and removes the incumbent's entailment→contradiction error on CG-20.

But it preserves the critical CG-18 neutral→contradiction false-adverse error and misses the exception contradiction CG-19 by voting neutral 2:1.

Raw accuracy improvement is therefore insufficient to justify majority voting.

### Disagreement-as-signal hypothesis

**SUPPORTED ON THE SHORT SEED COHORT.**

R2 and R4 abstain on all three incumbent errors and on no incumbent-correct short case:

- decided coverage: 78.6%;
- selective accuracy: 100%;
- false-adverse: 0;
- wrong decided: 0.

This is unusually clean but remains a 14-case construction result, not a production estimate.

## Stress-head results

All 14 stress-head inputs exceed the 512-position limit for the two ordinary DeBERTa models, but decisive evidence appears before the irrelevant appendix.

| Rule | Decided | Correct | Selective accuracy | Wrong decided | False adverse | Unresolved |
|---|---:|---:|---:|---:|---:|---:|
| R0 incumbent | 14 | 11 | 78.6% | 3 | 1 | 0 |
| R1 majority | 14 | 12 | 85.7% | 2 | 0 | 0 |
| R2 unanimity | 12 | 11 | 91.7% | 1 | 0 | 2 |
| R3 polar abstain | 13 | 11 | 84.6% | 2 | 0 | 1 |
| R4 adverse-conservative | 12 | 11 | 91.7% | 1 | 0 | 2 |
| R5 aperture route | 14 | 12 | 85.7% | 2 | 0 | 0 |

### COUNTEREXAMPLE

CG-18 becomes a **unanimous entailment prediction** under stress-head despite target neutral.

Thus unanimity is not a correctness proof. Context/distraction can induce correlated model error.

R5 also demonstrates that sequence truncation alone is too coarse a router: decisive evidence remains visible in this variant, so routing every >512-token input to the long model buys coverage but sacrifices the conservative abstention behavior of R4.

### INFERENCE

A successor router should use a stronger **evidence visibility / decisive-span aperture receipt**, not merely total sequence length.

## Stress-tail results

The same irrelevant material is moved before the unchanged decisive evidence. The two 512-position models truncate the decisive tail; the long-context model does not.

| Rule | Decided | Correct | Selective accuracy | Wrong decided | False adverse | Unresolved |
|---|---:|---:|---:|---:|---:|---:|
| R0 incumbent | 14 | 3 | 21.4% | 11 | 0 | 0 |
| R1 majority | 10 | 7 | 70.0% | 3 | 0 | 4 |
| R2 unanimity | 3 | 2 | 66.7% | 1 | 0 | 11 |
| R3 polar abstain | 9 | 7 | 77.8% | 2 | 0 | 5 |
| R4 adverse-conservative | 9 | 7 | 77.8% | 2 | 0 | 5 |
| R5 aperture route | **14** | **12** | **85.7%** | **2** | **0** | **0** |

### Aperture-routing hypothesis

**SUPPORTED AS A RESEARCH MECHANISM.**

R5 recovers full coverage and 12/14 correctness versus 3/14 for the incumbent.

It does not achieve perfect semantics. The two remaining errors are inherited from the long-context model:

- CG-18: neutral target, long model entailment;
- CG-19: contradiction target, long model neutral.

### INFERENCE

The data support a hierarchy:

1. establish which models actually saw the necessary evidence;
2. exclude or down-rank measurements whose aperture omitted necessary material;
3. then evaluate semantic agreement/disagreement among eligible measurements.

Blind voting treats a truncated model vote as equal to a model that actually saw the decisive evidence. That is not defensible when visibility is known.

## What normalization can and cannot do

RC1 deliberately did not normalize softmax scores.

### FACT

The useful signal in RC1 exists already at the categorical/structural level:

- model identity;
- predicted relation;
- disagreement pattern;
- polar conflict;
- evidence visibility/truncation.

### INFERENCE

Score calibration may add useful information later, but it should be a **second-stage experiment**, not a prerequisite for using multiple entailers.

A defensible future normalized score would require:

- a separately frozen calibration cohort;
- enough examples of all three labels, especially neutral;
- model-specific calibration;
- calibration evaluated under domain and operator shift;
- held-out testing of any learned weighting;
- preservation of per-model measurements after aggregation.

Raw probability averaging remains unsupported.

## Strongest candidate architecture after RC1

The evidence now favors an explicit measurement object rather than a scalar ensemble score.

Conceptually:

```
semantic_measurement_set
  ├─ incumbent
  │    ├─ label
  │    ├─ native score vector
  │    └─ evidence_visible?
  ├─ large
  │    ├─ label
  │    ├─ native score vector
  │    └─ evidence_visible?
  ├─ long
  │    ├─ label
  │    ├─ native score vector
  │    └─ evidence_visible?
  └─ comparison
       ├─ unanimous?
       ├─ polar_conflict?
       ├─ disagreement_class
       └─ ensemble_measurement_state
```

The ensemble measurement state should remain distinct from the eventual CAL evidence state and decision policy.

## Preregistered falsifiers

### R1 majority

**Not sufficient.** It improves raw accuracy but retains the adverse CG-18 error.

### R2/R4 disagreement abstention

**Supported on short inputs, not universally supported.** The clean short slice is perfect at 11/14 coverage, but stress-head and stress-tail contain unanimous wrong cases.

### R5 aperture routing

**Supported as a mechanism, not as final policy.** It strongly recovers stress-tail performance, but total-length truncation is too crude when the decisive evidence remains before the cutoff.

## Preserved deviation

Initial RC1 run `33288414448` stopped before evaluator execution because Ruff required `Callable` to be imported from `collections.abc`.

Repair commit `aca0f84fd16d7dad128c038b139cb7ab00b232a3` changed that import only.

No frozen data, rule, target, metric, or decision boundary changed.

## Next smallest discriminating tests

1. **Independent disagreement cohort.**
   Freeze a larger set with materially more neutral, overgeneralization, exception, quantifier, modality, and scope cases before testing whether the short-input disagreement enrichment reproduces.

2. **Evidence-visibility routing.**
   Replace raw total-length routing with an independently determined receipt that says whether each model's actual encoded premise contains every stipulated necessary evidence span.

3. **Calibration RC.**
   Only after a separate calibration cohort exists, fit model-specific temperature/calibration maps and test whether calibrated score information improves over categorical disagreement without increasing adverse false positives.

4. **Cost-aware execution.**
   Test cascade designs such as incumbent first → second/third entailer only on high-risk phenomena or disagreement, versus always running all models.

## Non-authorization

RC1 does not authorize:

- production ensemble implementation;
- replacing the current entailer;
- majority vote as a production rule;
- unanimity as truth;
- raw softmax averaging;
- score normalization without independent calibration;
- changing CAL semantic operators;
- changing Contract C;
- changing downstream decision policy.
