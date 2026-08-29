# Cross-Corpus Parallel Epistemic Artifact Shadow — Preregistration

## Status

**DESIGN ONLY. DO NOT EXECUTE AS PART OF THIS RC.**

This preregistration follows the semantic-operator reconciliation result that a parallel, non-authoritative epistemic artifact is justified for research observation. It does not authorize production emission, threshold tuning, model replacement, Contract C changes, or a new production decision path.

## Research question

Does the parallel epistemic artifact preserve and expose internal epistemic distinctions on a corpus that is larger and more heterogeneous than the 25-case E2E diagnostic fixture, without converting unknowns into terminal conclusions or creating support↔adverse polarity transitions?

The study is not an accuracy contest against legacy CAL. Terminal agreement is descriptive only.

---

## Frozen predecessor authority

At preregistration design time:

- production `main`: `53f0885b111676794d1bd20e10b91aa58b07e9d4`
- predecessor production-trace shadow head: `b487d1dce4cc1a076e3705b0a7ef457e7d438814`
- accepted successor science head: `0d8e67a2cf96e1d6eb665dae2cf9dc11629cfcc8`
- 25-case E2E fixture blob: `48a22cfab82ea0a2abd8d1c80d0da32a3dacd260`
- Construction Invariant Gold builder blob on production main: `2c677ee29fd121cf1c76b1476664474aa09dc982`
- production decision-history blob recording the 33-case construction surface: `600ba1577ea703bee99be72dedc7f93b5c89f442`

The existing production decision record reports a 33-case Construction Gold surface. That surface is immediately larger than the 25-case diagnostic fixture and contains regulatory-prose perturbations not represented by a single terminal-label balance.

---

## Corpus design

### Cohort A — Construction Invariant Gold input surface

Use **all 33 frozen construction cases** as the primary new corpus, subject to an input-only manifest freeze before execution.

The manifest may contain only fields necessary to reproduce the input and preregistered phenomenon stratum, for example:

- stable case ID;
- claim text;
- evidence/source passages and passage IDs;
- declared source-boundary/input metadata needed by the current runner;
- construction group / perturbation identifier where it is input-side metadata;
- source blob/manifest receipts;
- preregistered semantic-phenomenon stratum.

The execution aperture must not expose expected verdicts, expected rule IDs, expected hashes, historical CAL outputs, or construction-gold pass/fail state to the adapter, artifact emitter, threshold selection, operator selection, or repair process.

### Cohort B — Simple Logic Gold DEV input slice, gated

Add a second corpus only after a **separate pre-execution freeze** establishes:

1. exact source-corpus SHA/receipt;
2. deterministic DEV-only selection procedure that does not inspect CAL outputs;
3. input-only manifests with expected labels removed from the execution aperture;
4. family coverage known before CAL execution.

Selection should target at least one case from each **available** declared logic family, not a fixed N chosen after observing results. If a family is absent from the frozen source, record a coverage hole. Do not synthesize replacement cases after seeing CAL behavior.

If those prerequisites are not available, Cohort B is omitted and the study reports that cross-corpus execution is blocked. Cohort A may still run as the larger heterogeneous shadow, but must not be described as cross-corpus evidence.

### Sentinel cohort — predecessor 25

The original 25 E2E cases may be rerun as a reproducibility sentinel but are not counted as new-corpus evidence. Their normalized scientific object must continue to match the frozen predecessor receipt before larger-corpus results are interpreted.

---

## Phenomenon strata

Cases are analyzed by semantic phenomenon rather than only total N. Classification must be frozen before any successor/legacy comparison is examined.

Required strata, allowing multi-tagging where genuinely applicable:

1. direct entailment / identity support;
2. direct contradiction;
3. explicit lexical or structural negation;
4. numeric equality/mismatch;
5. inequality / threshold / bound relation;
6. quantity and unit relation;
7. categorical incompatibility;
8. quantifier relation (`all`, `some`, `none`, `every`, existential/universal forms);
9. degree/partial-support relation;
10. scope/location/entity mismatch;
11. source-boundary / absence / completeness claim;
12. multi-passage composition or conjunction;
13. mixed support and refutation;
14. irrelevant/distractor evidence;
15. ineligible evidence;
16. no applicable semantic operator / unmeasured validity;
17. no evidence / retrieval silence;
18. execution failure, if one occurs.

If a case cannot be assigned without looking at model output or expected verdict, classify it as `phenomenon_unresolved` before execution. Do not post-hoc force it into the stratum that best explains the result.

---

## Frozen machinery

Before execution, record exact SHAs for:

- production main;
- runner;
- retriever and model revision;
- entailer and model revision;
- aggregator;
- rules;
- trace models;
- explicit decision model;
- evidence state;
- semantic operators;
- eligibility/operator replay machinery;
- parallel-artifact emitter;
- corpus input manifests;
- thresholds/configuration.

### Hard freeze

- support threshold remains `0.70`;
- refutation threshold remains `0.70`;
- pinned DeBERTa model remains unchanged;
- no threshold sweep, calibration search, or disagreement-driven operator patch is permitted during the run;
- Contract C is not part of the artifact path and must remain unchanged.

---

## Information aperture and anti-leakage controls

### Before execution

The runner and adapter may see:

- claim and evidence inputs;
- input-side source-boundary/eligibility metadata legitimately required by the current CAL call;
- frozen semantic-phenomenon tags;
- frozen model/configuration authority.

They may not see:

- expected legacy verdicts as gold;
- construction-gold expected verdicts;
- expected fired rules;
- prior target-system result summaries for these exact cases;
- hidden/held-out scientific labels;
- any post-run disagreement list.

### After all artifacts are frozen

Reference/expected outcomes may be revealed for descriptive comparison where authorized, but no implementation or threshold repair may occur in the same experiment after reveal.

---

## Primary measurements

For every case, record:

1. terminal legacy outcome;
2. parallel explicit outcome;
3. **first divergence stage**;
4. raw → eligible state transition;
5. eligible → semantic-valid state transition;
6. contribution-ledger cardinality and channel composition;
7. state compression, defined as distinctions present in one representation but collapsed in the other;
8. unknowns created by the explicit projection;
9. unknowns removed or silently resolved;
10. support → adverse transitions;
11. adverse → support transitions;
12. semantic-operator applicability;
13. semantic-operator terminal coverage;
14. unmeasured semantic-validity states;
15. aperture/completeness status and failures;
16. execution/assessment failures;
17. exact causal basis contribution IDs and source passage IDs;
18. exact direct model measurements and operator receipts.

### Descriptive secondary measurements

- terminal agreement count/rate;
- outcome-frequency distributions;
- counts by corpus and phenomenon stratum.

These are secondary and may not be used as a tuning objective.

---

## Predeclared invariants

The larger shadow must preserve at least these invariants:

1. unknown semantic validity cannot decide;
2. inapplicable operator state cannot be treated as a terminal validity measurement;
3. missing operator receipt cannot strengthen a conclusion;
4. irrelevant evidence cannot strengthen causal basis;
5. ineligible evidence remains observable but non-deciding;
6. mixed valid evidence remains mixed unless a separately preregistered resolver has legitimate authority;
7. execution failure remains distinct from epistemic abstention;
8. absence of applicable operator is not contradiction;
9. no support → adverse transition may be introduced by projection without an independently receipt-bound adverse contribution;
10. no adverse → support transition may be introduced analogously;
11. removing evidence or a receipt cannot strengthen the causal basis;
12. adding a distractor cannot increase operator authority;
13. Contract C output and semantics remain unchanged because the parallel artifact is outside that path.

---

## Falsifiers / stop conditions

The study is **invalid for interpretation** if any of the following occurs and is not separately frozen before scientific execution:

- production or explicit semantic machinery changes after corpus reveal;
- any threshold is changed based on case outcomes;
- expected labels are used to choose an operator, repair an adapter, or select cases;
- the artifact reads legacy terminal verdicts to reconstruct missing semantic state;
- a missing/inapplicable operator becomes a terminal semantic conclusion;
- exact source-passage/model/operator receipts cannot be recovered;
- execution failure is counted as epistemic abstention;
- corpus selection is changed after observing CAL results;
- the predecessor 25-case normalized scientific object no longer reproduces and the difference is unexplained.

A scientific disagreement is not itself a stop condition. Preserve it and localize it.

---

## Planned analysis

Analyze each corpus separately first, then compare strata across corpora.

For each phenomenon stratum report:

- N and corpus provenance;
- operator-applicable N;
- operator-terminal N;
- operator-inapplicable N;
- semantic-validity-unknown N;
- first divergence stages;
- unknown creation/removal;
- raw/eligible/valid compression patterns;
- polarity-transition counts;
- aperture and execution failure counts.

Do not collapse these into a single score before the per-stratum record exists.

---

## Decision rule after the study

Possible dispositions are intentionally narrow:

### `ARTIFACT_GENERALIZES_AS_RESEARCH_OBSERVATION`

Supported only if the artifact remains truthful across strata, unknowns stay explicit, no hidden state reconstruction is needed, and failures remain localizable.

### `ARTIFACT_REQUIRES_TYPED_OPERATOR_EXTENSION`

Use when the artifact is structurally truthful but material strata remain non-deciding because a specific semantic family lacks an authorized operator. This is not a failure to match legacy labels.

### `ARTIFACT_PROJECTION_UNTRUSTWORTHY`

Use if the projection itself invents/removes state, loses provenance, violates monotonicity/invariants, or cannot distinguish execution from epistemic outcomes.

### `STUDY_BLOCKED`

Use if corpus receipts, blind input manifests, source metadata, or reproducibility prerequisites cannot be established.

None of these dispositions authorize production promotion.

---

## External NLI boundary

Do not introduce alternative NLI models in this study.

If a case diverges, classify the earliest plausible failure source among:

- retrieval;
- NLI measurement;
- operator applicability;
- semantic-validity measurement;
- aggregation;
- policy;
- missing state;
- aperture/completeness;
- execution.

Only after a phenomenon has an independently defined semantic target should a separate model-comparison preregistration be written. The larger shadow is a localization study, not a model bake-off.
