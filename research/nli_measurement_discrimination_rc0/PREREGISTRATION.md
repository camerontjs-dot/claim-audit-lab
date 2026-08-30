# NLI Measurement Discrimination RC0 — Preregistration

## Classification

Research Infrastructure / semantic-measurement discrimination experiment.

This experiment is downstream of the frozen Construction Cohort A shadow. It does not authorize model replacement, threshold tuning, production-path changes, Contract C changes, semantic-operator changes, or decision-policy changes.

## Claim under review

After CAL's current retrieval, eligibility, semantic-operator, aperture, aggregation, and policy failures are kept separate, does an alternative NLI model materially improve **plain textual relation measurement** over the pinned production entailer?

The experiment tests three narrower explanations:

1. **capacity / NLI-training breadth:** a larger same-family Laurer checkpoint improves short-context textual relation measurement;
2. **aperture:** a long-context NLI checkpoint preserves the correct relation when decisive evidence is moved beyond the 512-token aperture;
3. **non-NLI ownership:** cases whose truth depends on source boundary, typed numeric semantics, or multi-passage composition should not be treated as evidence for replacing the entailer.

## Frozen authority

- production main: `53f0885b111676794d1bd20e10b91aa58b07e9d4`
- frozen Cohort A science head / branch point: `ba1310d73ab63adf7c83de2f1e130f7f00a665af`
- frozen Cohort A Actions run: `33286159031`
- frozen Cohort A artifact: `9724541749`
- frozen blind 33-case manifest SHA256: `e86374c6ca12342c56a8640b5124073278179ac6379bb88bdadebeb25f57ccad`
- frozen Cohort A RESULTS SHA256: `38cd6f29eab0ea6e0f50e737814b993aaf45a3919cacb5e02296289516e112d7`
- canonical construction builder blob: `2c677ee29fd121cf1c76b1476664474aa09dc982`
- incumbent entailer: `MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli@6f5cf0a2b59cabb106aca4c287eed12e357e90eb`

## Frozen candidate models

### A — incumbent
`MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli@6f5cf0a2b59cabb106aca4c287eed12e357e90eb`

### B — capacity / training-breadth probe
`MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli@0de4830e69aa5710af98b05f2c4d001d0edc0e52`

### C — aperture probe
`tasksource/deberta-base-long-nli@d6e08f68489c9ac015ba3071f90ac0976cbc1fff`

Every model must expose a three-way label set containing entailment, neutral, and contradiction. Any incompatible or ambiguous label map is a stop condition, not something to patch after execution.

## Target construction

The scientific target is derived only after Cohort A was frozen, from the already-frozen construction relation.

### Primary plain-NLI slice

Only relations with a defensible ordinary NLI target are used for model comparison:

- `restates` → entailment
- `weakens` → entailment
- `contradicts` → contradiction
- `overgeneralizes` → neutral

The case's stipulated **support-role passages only** form the ordinary premise. Distractor-role passages are not allowed to redefine the target.

### Excluded from primary model ranking

These relations remain diagnostic controls only:

- `absent_from` — depends on source-boundary / completeness authority;
- `instantiates_bound` — typed numeric / threshold reasoning;
- `conjunction` and `partial_conjunction` — evidence-set composition;
- `chains` — multi-hop composition.

Their outputs may be recorded, but they cannot count as evidence for or against model replacement in RC0.

## Aperture mutation

For every primary case, build a second premise deterministically:

1. prepend irrelevant regulatory passages drawn from other frozen construction sources;
2. repeat them only as needed to place the decisive support passage after token position 512 under the incumbent tokenizer while keeping total target length below 1280 where possible;
3. append the unchanged decisive support-role passage(s);
4. keep the claim unchanged.

The target relation is invariant because the added material is stipulated irrelevant and the decisive evidence is unchanged.

Record each model's native maximum-position limit, untruncated token count, truncation status, predicted label, logits, and three-way probabilities.

## Primary measurements

Report separately for short and aperture-stress inputs:

- exact three-way relation match;
- entailment recall;
- contradiction recall;
- neutral recall;
- neutral→contradiction false-adverse count;
- contradiction→neutral loss count;
- short→stress correctness retention;
- short→stress label stability;
- cases where only the long-context model retains the correct relation.

Do not collapse these into one promotion score before per-case and per-class results exist.

Raw softmax values are measurements, not posterior probabilities. No calibration or threshold search is performed in RC0.

## Determinism / controls

- run each model twice on a frozen sentinel subset and require identical argmax labels and numerically equal logits within a fixed tolerance;
- require the Cohort A branch-point protected production surfaces to remain unchanged;
- require the construction builder blob to remain unchanged;
- require the generated 33-case construction corpus to validate before selecting the primary slice;
- preserve all candidate failures and download/model-load deviations.

## Falsifiers

### Capacity hypothesis falsified

If the large same-family model does not reduce short-context primary measurement errors without worsening neutral→contradiction false-adverse errors, scale/training breadth is not supported as the next entailer change.

### Aperture hypothesis supported

Only if the long-context model materially preserves correct relations on the preregistered >512-token stress inputs where 512-token models lose them, while not degrading the corresponding short cases.

### Replacement hypothesis remains unsupported

If most errors in the frozen Cohort A remain outside the primary plain-NLI slice, or candidates improve only operator-owned/compositional cases without a valid NLI target.

## Stop conditions

Stop scientific interpretation if:

- a frozen model revision cannot be loaded;
- a model's three-way label semantics cannot be established from its config;
- the construction builder no longer validates;
- the target mapping is changed after candidate outputs are observed;
- cases are added/removed after observing candidate behavior;
- thresholds, production config, operators, aggregation, or decision policy are changed;
- an operator-owned case is used to rescue a model-ranking conclusion.

## Allowed terminal dispositions

Use the repository governance disposition vocabulary:

- **SUPPORTED FOR PROMOTION**
- **FALSIFIED**
- **INCONCLUSIVE**
- **SUPERSEDED**

A model can be supported only for a separately scoped promotion proposal. RC0 itself does not change production.

## Competing explanations to check before disposition

Before attributing a gain to model quality, check:

- whether the candidate simply had a larger visible context;
- whether label ordering differed;
- whether a case actually required a typed operator or evidence-set composition;
- whether a distractor became decision-relevant rather than remaining irrelevant;
- whether the incumbent's apparent error was caused by truncation rather than semantic measurement;
- whether one class improved by collapsing neutral into contradiction.

