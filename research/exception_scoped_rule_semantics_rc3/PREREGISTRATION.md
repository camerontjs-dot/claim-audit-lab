# Exception and Scoped-Rule Semantics RC3 — Preregistration

## Classification

Research Infrastructure / semantic-measurement discrimination experiment.

This RC is a successor to NLI measurement-discrimination RC0, ensemble/disagreement RC1, and Independent NLI Disagreement + Calibration RC2 (Draft PR #44). It is an evidence record only. It does not authorize production changes.

## Research question

RC2 localized explicit exception semantics as a concentrated failure family that was not repaired by three-model voting, an adverse-conservative categorical ensemble, or model-specific temperature calibration. RC3 asks what smaller semantic machinery, if any, is actually required to preserve exclusion, opposite requirements, alternate procedures, temporal scope, narrow exemptions, nested qualifications, and `only` constructions without collapsing absence from a rule into its opposite.

Competing explanations remain live:

1. ordinary NLI model weakness;
2. ambiguity in exception semantics;
3. missing explicit rule-scope representation;
4. exclusion-versus-negation confusion;
5. exemption-versus-alternate-procedure confusion;
6. temporal qualification;
7. modality/deontic scope;
8. lexical/template artifact;
9. evaluator/gold error;
10. decomposition before NLI;
11. typed semantic representation;
12. specialist verification;
13. a smaller mechanism.

No typed operator is assumed to be the answer.

## Frozen live authority at preregistration

- production `main`: `53f0885b111676794d1bd20e10b91aa58b07e9d4`
- production entailer implementation blob: `aaf9415e74ec2f04357ecf5346491d92f3e2d0d3`
- production default NLI config blob: `99c88213ef680d8612504349a7beb2491501fd89`
- production guarded semantic-operator blob: `ae64056d2cbec4ed7fd615fe3f4fa6f2bebb177f`
- NLI measurement-discrimination RC0 head: `b316d115c82fb635b0e089d43342b4b6e75c326e` (Draft PR #40)
- NLI ensemble/disagreement RC1 head: `7ce57893eada43de9d4ee77281854f78a07ad0c2` (Draft PR #42)
- RC1 adverse-conservative evaluator blob: `dd965b2079224bf449eb2ad1174b350f77ebd113`
- Independent NLI Disagreement + Calibration RC2 current head at preregistration: `b4ba3fd049812a480c7cb315d43d918ed463f3c3` (Draft PR #44)
- RC2 accepted science head: `1c057c1aeb7c6501704efb347c46fc9c56d20e3a`
- RC2 accepted science Actions run: `33289051885`
- RC2 frozen cohort SHA256: `c5f64d6ad73d198aef575b5274280363bb71fc99aac78197e3abf13b13599f2d`
- RC2 frozen measurement SHA256: `1751b4fd16eefbcea114cca406302e05d66d2c73848c078d7d96153e9aac0ae3`

RC2 frozen scientific artifacts are predecessor evidence and MUST NOT be modified by RC3.

## Frozen models

S0 incumbent:
`MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli@6f5cf0a2b59cabb106aca4c287eed12e357e90eb`

S1 larger same-family:
`MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli@0de4830e69aa5710af98b05f2c4d001d0edc0e52`

S2 long-context:
`tasksource/deberta-base-long-nli@d6e08f68489c9ac015ba3071f90ac0976cbc1fff`

S3 is the exact RC1/RC2 adverse-conservative rule:

- contradiction only under 3/3 contradiction;
- entailment under >=2 entailment and zero contradiction;
- neutral under >=2 neutral and zero contradiction;
- otherwise unresolved.

No scores, weights, calibration maps, thresholds, or label repairs enter S3.

## Fresh cohort

The full cohort is authored and frozen before any RC3 model execution.

Frozen file: `research/exception_scoped_rule_semantics_rc3/COHORT.json`

Expected SHA256: `01b0d436ccf9ed812f9bb26d64f4ddd1a656e26175ee007f1fe9594a2a203785`

Primary scientific slice:

- 84 cases;
- seven semantic families;
- exactly 12 cases per family;
- exactly 4 entailment / 4 neutral / 4 contradiction per family;
- therefore 28 / 28 / 28 overall.

Families:

1. explicit opposite exception;
2. bare exception / exclusion;
3. separate-process exception;
4. temporary exception;
5. narrow obligation exemption;
6. nested / qualified exception;
7. `only` and exclusion constructions.

Diagnostic slice:

- 20 cases in ten frozen metamorphic pairs;
- six evaluator-ambiguous cases with no forced three-way target.

The ambiguous cases are preserved as evidence and excluded from accuracy/F1.

Every scored case contains a short machine-readable semantic rationale. Gold labels are determined from the premise semantics before model reveal.

## Critical semantic distinctions

The following are primary failure metrics, not optional anecdotes:

- `exception_not_negation`: exclusion from a rule incorrectly converted into the opposite behavior/obligation;
- `narrow_to_broad`: narrow exemption generalized to a broader exemption;
- `alternate_to_no_process`: explicit alternate process converted into absence of any process;
- `temporary_to_permanent`: bounded temporal exception generalized beyond its interval.

## Metamorphic probes

The ten frozen pairs test:

1. remove exception;
2. add explicit opposite;
3. add alternate process;
4. alternate process versus no process;
5. narrow versus broad exemption;
6. temporary versus permanent exemption;
7. swap exempt/governed entity;
8. `may` versus `must`;
9. move exception clause without semantic change;
10. convert exception into an explicit equivalent without semantic change.

Mutation success requires the exact preregistered before/after relation, not merely label stability.

## S4 — deterministic decomposition + incumbent NLI

S4 is a frozen, research-only deterministic rewriter. It may expose only scope information stated in the premise. Its intended behavior is to split or surface:

- named exclusion from the immediately governing rule;
- explicit opposite requirement;
- explicit alternate process;
- explicit temporal boundary/restoration;
- explicit narrow exemption.

It must not infer an opposite from bare exclusion, infer a broader exemption, infer no process from an alternate process, or invent a temporal state.

S4 then runs the unchanged incumbent NLI model on the decomposed premise and unchanged hypothesis.

The decomposition implementation is frozen before cohort execution. No case-specific rewrite may be added after outputs are observed.

## S5 — typed scoped-rule interpretation candidate

S5 is a bounded, deterministic, research-only high-precision interpreter. It is not a production semantic operator and it does not decide CAL's epistemic state.

It may expose only typed facts it can recognize with a frozen grammar:

- `rule_exclusion`;
- `explicit_opposite`;
- `alternate_process`;
- `temporal_scope`;
- `narrow_exemption`;
- `only_permission`;
- `restored_rule`.

Unsupported or ambiguous input MUST produce unknown/unresolved.

For direct three-way comparison, a frozen conservative query adapter may project a typed state against the natural-language hypothesis. The adapter may return entailment, neutral, contradiction, or unresolved. It may not use case IDs, gold labels, family labels, critical-error tags, or mutation metadata.

## Measurements

For S0-S5 report, where applicable:

- primary accuracy;
- macro-F1;
- per-family accuracy;
- neutral -> contradiction;
- entailment -> contradiction;
- contradiction -> neutral;
- false-adverse count/rate;
- unresolved/abstention rate;
- selective accuracy;
- ten-pair mutation consistency;
- matched-family consistency;
- three-model unanimity/error;
- three-model disagreement incidence.

Report the four critical semantic error families separately.

For S5 also report recognized-state coverage and reasons for unresolved.

## Falsifiers

### Typed-representation hypothesis

Falsified if the deterministic scoped-rule representation cannot materially reduce the four critical semantic errors and mutation failures without introducing comparable new errors, or if useful coverage is too low to distinguish it from a narrow template recognizer.

### Decomposition hypothesis

Falsified if decomposition + incumbent NLI does not materially improve exception/scoped-rule semantics, or if gains are offset by comparable false-adverse regressions or mutation inconsistency.

### Specialist-model hypothesis

Disfavored if the larger/alternate NLI models retain the same systematic scoped-rule errors after the matched design removes class imbalance and includes paraphrase/adversarial controls.

### Ensemble hypothesis

Further weakened for this family if disagreement remains an error-risk signal but S3 still cannot recover the correct scoped semantics.

### Gold/evaluator hypothesis

Supported to the extent independent semantic review identifies cases whose premise does not determine a unique three-way target. Such cases remain preserved and excluded, never relabeled to make the evaluator easier.

## Strong alternative explanations to answer before disposition

- Could apparent success be template memorization?
- Could decomposition merely make sentences easier while failing to represent scope?
- Does the mechanism survive paraphrase, polarity reversal, entity swap, and temporal mutation?
- Is S5 encoding policy rather than semantics?
- Is absence from a rule being treated as evidence for its opposite?
- Could a downstream consumer interpret the typed state without hidden evaluator context?
- Does the candidate simply exploit the constructed cohort's vocabulary?
- Would a smaller mechanism explain the same gains?

## Stop condition

Scientific interpretation stops when the evidence supports one bounded RC3 state:

- `A_NLI_SUFFICIENT_WITH_BOUNDED_IMPROVEMENTS`;
- `B_DECOMPOSITION_REQUIRED`;
- `C_TYPED_REPRESENTATION_REQUIRED`;
- `D_UNRESOLVED`.

The repository terminal disposition remains one of the governance vocabulary values: **SUPPORTED FOR PROMOTION**, **FALSIFIED**, **INCONCLUSIVE**, or **SUPERSEDED**. RC3 itself cannot authorize production promotion.

## Frozen-boundary rules

Stop and preserve the deviation if any of the following occurs:

- any RC3 model executes before the cohort and candidate mechanisms are frozen;
- the cohort, gold labels, rationales, mutation expectations, S4, or S5 change after model reveal;
- a model revision or three-way label map differs from the pins above;
- an evaluator-ambiguous case is forced into primary scoring;
- production `src/`, Contract C, aggregation, thresholds, or production semantic operators change in this RC;
- PR #44 frozen artifacts are modified;
- a failure is repaired by changing scientific targets after model output.

No production behavior is changed by this experiment.
