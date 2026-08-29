# CAL Epistemic Methodology RC0 — Phase 1 production path map and abstention matrix

## Status

**PHASE 1 / PRE-v2 EXPOSURE.** This record was produced without inspecting implementation, tests, comments, or detailed design from `feat/v2-epistemic-pipeline`. Only that branch's exact head identity was recorded.

This document describes the released CAL v0.5.0 semantic baseline and the current `main` path. It does not recommend an architecture.

## Exact live identities

- current CAL `main`: `e90f301cf6ca02c0c77b6e88c3b08f8b93b9a36a`
- immutable CAL tag `v0.5.0`: annotated tag -> `5533bbcf27a3ee3a7d901f7dfc44c241bc558e2c`
- `main` is exactly one commit ahead of v0.5.0; the only changed file is `.github/workflows/cal-v0.5.0-publication-recovery.yml`
- therefore no CAL semantic source/test/config file differs between v0.5.0 and current `main`
- immutable Contract C tag `contract-c-v1.0.0`: annotated tag -> `5fe55f9ed5d0ee9f026ca1b077e9d70ce0487ea1`
- historical v2 branch identity only: `b7254e713feb5556a81fb0c5b39649c415a949c6`
- RC0 research branch: `research/epistemic-methodology-rc0`
- Draft Research PR: #28

## Sources inspected during Phase 1

Production/released artifacts:

- `src/claim_audit_lab/v1/intake.py` blob `d8b304a4259ec128e656f07ca628d8a0a88ddd69`
- `src/claim_audit_lab/v1/pipeline.py` blob `dd67d0d35590d3052826ad697ce9fd11222fff6f`
- `src/claim_audit_lab/v1/models.py` blob `755e0ef...` (Git tree identity; exact file is pinned by baseline commit)
- `src/claim_audit_lab/v1/impl/aggregator.py` blob `b1f9e2309ae3d024bc609b83cc546acb30be6e9b`
- `src/claim_audit_lab/v1/impl/rules.py` blob `bc388d64a5a53db0d33610ab6ff84bd93a811b46`
- `src/claim_audit_lab/v1/evidence_state.py` blob `e873772588e8c6ac27ced79559812afc8f5e9cdc`
- `src/claim_audit_lab/contracts/cb_models.py` blob `a153787302824d76d67326f17a881899078cb6d6`
- `src/claim_audit_lab/contracts/contract_c.py` blob `d6b32a44ef11109fe0ee91efa212d3904badf58c`
- released Apparatus `contract-c-v1.0.0.md` blob `8c15f2e5f4047ccd17e204fb23aee1168781b9d5`
- released v1 frozen trace fixtures 13, 15, 16, 22
- `tests/v1/test_rules.py` blob `f3e163fad4c0ff6348055a428573c4e161a1c885`
- CAL issue #3 and its 2026-08-29 state-reconciliation comment

No old-v2 content was inspected.

---

# OBSERVED — current production epistemic path

## 1. Contract-B intake

`bundle_to_requests` normalizes every auditable `extracted_claim` against the bundle's **full passage set**. It does not pre-filter on the Contract-B claim's `evidence_passages` or `counterevidence_passages` nomination containers.

This is a direct current safeguard for upstream-role invariance at candidate selection: nomination lane does not determine which passages v1 can semantically measure.

At the same boundary, `_normalize_passages` copies each source profile's `trust_level` (`primary | secondary | background`) into `Passage.source_meta`.

The C-B model identifies `trust_level` as a source-profile field. It does not encode proposition-specific eligibility as a Contract-B fact.

## 2. Measurement path

For each claim, `run_audit` performs:

1. claim feature extraction;
2. retrieval over the full normalized passage set;
3. retrieval-floor admission;
4. NLI only for admitted passages;
5. aggregation of per-passage NLI results;
6. optional negation/complement probes;
7. deterministic rules;
8. `AuditTrace` construction.

The entailer receives only `claim_text`, passage `text`, and `passage_id`. It does **not** receive source `trust_level`, upstream support/counterevidence nomination, or Decision-Engine policy.

Therefore, in the current implementation, source trust and upstream nomination cannot directly mutate the claim/passage NLI measurement call.

## 3. Retention before verdict policy

`AuditTrace` retains:

- full retrieval ranking, including sub-floor results;
- all entailment results actually measured;
- extracted claim features;
- the original aggregate `support_signal`;
- every `RuleFired` receipt;
- final `Verdict`;
- config hash and library version;
- optional negation probe.

The released `22-subfloor-contradict-filtered` trace demonstrates that a passage can remain in `retrieval` while being absent from `entailment` because it failed the retrieval floor. That exclusion is reconstructable from the score plus pinned config.

However, `AuditTrace` does **not** carry the input `Passage` objects or their `source_meta`; reconstructing source/trust facts requires the bound input artifact or another retained input record.

## 4. Raw measurement versus eligibility suppression

`VerdictRules.apply` can remove a measured result from the **deciding pool** and re-aggregate without deleting it from the original trace.

The strongest current example is `P1_eligibility_suppressed`:

- a measured adverse result from any passage with `trust_level` present and not `primary` is not allowed to solo-decide an adverse verdict;
- the result is removed from the internal eligibility pool;
- the remaining pool is re-aggregated;
- the original measured result remains in the trace's `entailment` list.

The current rule treats **missing `trust_level` as eligible**, specifically so directly constructed non-bundle passages do not trigger P1.

The released test `test_p1_lands_not_checkable_when_only_signal_is_ineligible` demonstrates a materially important collapse:

- semantic measurement: contradiction 0.99 exists;
- policy step: that result is suppressed because the source is background;
- terminal verdict: `not_checkable / no_entail_signal`;
- receipt: `P1_eligibility_suppressed` remains in `rules_fired`.

A plain neutral case also terminates `not_checkable / no_entail_signal`, but with `B5_degree` and no preceding P1 suppression.

Thus the final **verdict reason alone** collapses these two causes, while the fuller current trace can distinguish them by combining measurements and rule receipts.

## 5. The trace stores the pre-suppression aggregate, not the final internal aggregate

`run_audit` computes `support_signal` once and stores that exact object into `AuditTrace`.

`VerdictRules.apply` may subsequently suppress one or more contributions and internally re-aggregate a smaller pool, but it returns only `(verdict, rules_fired)`. The final internal re-aggregated signal/pool is not returned to `run_audit` and is therefore not stored as a typed post-policy state.

Consequences:

- removed evidence is preserved in the original measurement record;
- removal is represented by `RuleFired` prose/identity;
- the exact final deciding pool and final post-suppression support signal are not first-class typed trace fields;
- reconstruction is possible for some current paths by replaying the rules against the bound input and measurements, but not by reading a typed decision-basis object already present in `AuditTrace`.

## 6. Existing terminal distinctions are already richer than a generic abstention

Released production has `not_checkable` reasons:

- `out_of_scope`;
- `no_entail_signal`;
- `no_evidence`;
- `conflicting_evidence`;
- `absence_not_decidable` in the declared vocabulary.

Direct frozen traces demonstrate:

- `13-not-checkable-opinion`: evidence was retrieved/measured, but A1 returns `not_checkable/out_of_scope`;
- `15-not-checkable-no-evidence`: no passage clears retrieval floor -> `not_checkable/no_evidence`;
- `16-not-checkable-no-entail`: a passage clears retrieval and is measured neutral -> `not_checkable/no_entail_signal`.

Therefore the research concern is **not** accurately described as “CAL has one abstention state.” The live question is which materially distinct causes remain collapsed or require replay/prose parsing rather than explicit attributable state.

## 7. Other same-label/different-cause paths

Current rules demonstrate additional same-terminal/different-cause pairs:

- A1 scope failure and A7 semantic/scope mismatch can both emit `not_checkable/out_of_scope`; `rules_fired` distinguishes them.
- ordinary neutral B5 and an A4 negation-consistency demotion can both emit `not_checkable/no_entail_signal`; `rules_fired` distinguishes them.
- P1/P2/A6 suppression can remove a strong measured signal and later land on `not_checkable/no_entail_signal`; the suppression receipts distinguish this from a genuinely silent measurement, but no typed participation ledger does.

This is evidence for evaluating **causal reconstructability**, not evidence by itself for any particular stage architecture.

## 8. Conflicting evidence is already explicit but aggregation is still bounded

The aggregator retains per-passage results and records best entail/refute channels when measured. Rule A5 emits `not_checkable/conflicting_evidence` when both channels clear their thresholds.

Current production aggregation remains `max_entailment`; documented `concat_premise` and `matrix` strategies are deferred. CAL therefore does not presently establish general multi-passage composition semantics merely because multiple passages are retained.

## 9. Execution state is outside the v1 `AuditTrace`

`run_audit` returns an `AuditTrace` only if the invoked feature/retrieval/entailment/rules path returns successfully. Exceptions do not become a typed `AuditTrace` execution-failure state.

Contract C 1.0.0, separately, explicitly distinguishes:

- result-set `completed | failed | incomplete`;
- proposition `completed/assessed | completed/not_checkable | failed | incomplete`;
- assessment-stage `not_performed | performed/unknown | performed/adverse | not_applicable | failed`.

The current CAL Contract-C exporter is the promoted **v0.2 producer** and truthfully hard-codes its demonstrated result-set/proposition execution as completed and its four generic assessment slots as `not_performed`. It is not a v1 epistemic-state exporter.

Therefore “execution failure must be distinct from epistemic abstention” is already a released Contract-C semantic invariant, but current v1 trace architecture does not itself provide the full Contract-C execution/assessment state needed for a future v1 producer.

---

# Abstention causal matrix

| Path / trigger | Evidence present? | Evidence measured? | Strong semantic signal present? | Evidence excluded/non-deciding? | Required assessment missing? | Execution successful? | Aggregation resolved? | Exact current terminal | Reconstructable today? | Distinct state justified? | Minimal representation question |
|---|---:|---:|---|---|---|---:|---|---|---|---|---|
| A2: nothing clears retrieval floor | yes, but sub-floor | no | unknown | floor-filtered | no | yes | n/a | `not_checkable / no_evidence` | yes from retrieval + config | **OBSERVED distinct** from read-silent | existing reason + retrieval may already suffice |
| B5: admitted evidence is neutral | yes | yes | no | no | no | yes | yes under current max rule | `not_checkable / no_entail_signal` | yes | **OBSERVED distinct** from no-evidence | existing trace may already suffice |
| A1: input is opinion/question/imperative/too short | case-dependent | current pipeline may measure before gate | case-dependent | evidence becomes irrelevant to terminal basis | checkability adverse by rule | yes | irrelevant | `not_checkable / out_of_scope` | yes via A1 receipt | **OBSERVED distinct** from semantic silence | may need only typed branch/basis, not new verdict enum |
| A5: strong support and contradiction channels both clear | yes | yes | yes, opposed | neither side uniquely decides | governing scope unresolved | yes | unresolved by current evidence | `not_checkable / conflicting_evidence` | yes | **OBSERVED distinct** | current reason already explicit; preserve both contributions |
| P1: only strong adverse signal is source-class suppressed | yes | yes | **yes** | yes, P1 | proposition-specific eligibility was **not** separately performed | yes | re-aggregates to empty/neutral | `not_checkable / no_entail_signal` | partially: measurement + P1 receipt + input replay | **OBSERVED materially distinct** from B5 silence | explicit participation/assessment state may be warranted |
| P1: louder suppressed adverse + eligible support remains | yes | yes | yes | one residual/non-deciding | proposition-specific eligibility not separately performed | yes | yes after suppression | e.g. `supported` in frozen unit control | partially: requires replay/receipts to recover final deciding pool | **OBSERVED causal-basis distinction** | typed deciding/residual roles may be warranted |
| P2: self-negating contradiction is suppressed | yes | yes | apparent adverse signal | yes, semantic-validity guard | explicit generic semantic-validity stage absent | yes | depends on remaining pool | often non-adverse / may land `no_entail_signal` | partially via receipt + replay | **OBSERVED mechanism; representation need under test** | could be typed removal reason rather than a new terminal state |
| A4: hard contradiction unconfirmed by stronger negation probe | yes | yes + probe | primary contradiction exists | contradiction is demoted | semantic-validity-like check performed by rule | yes | yes | `not_checkable / no_entail_signal` | yes via probe + A4 receipt | **OBSERVED distinct** from B5 silence | explicit assessment/participation may reduce replay dependence |
| A7: contradicting passage is about different site/subject | yes | yes | apparent adverse signal | signal blocked by scope mismatch | applicability/scope adverse | yes | yes | `not_checkable / out_of_scope` | yes via A7 receipt | **OBSERVED distinct** from A1 | no evidence yet that a new verdict label is needed |
| model/parser/rule execution exception | may vary | may vary | unknown | n/a | n/a | **no** | unknown | no v1 `AuditTrace` | no subject-matter trace; outer run receipt required | **OBSERVED architecture boundary**, exact production handling varies by caller | execution state must remain separate somewhere; ownership still open |
| distributed partial evidence with no validated composition rule | yes | yes/partial | unknown | should not be erased | aggregation semantics absent | yes | **unknown** | current result depends on max-entailment behavior | contributions retained, intended joint meaning not established | **HYPOTHESIS** that distinct unresolved aggregation state is needed | preserve contributions + unresolved aggregation without inventing semantics |

The matrix deliberately does not create one enum value per row. It identifies where causes are already recoverable, where they are recoverable only through replay/prose receipts, and where the state is not yet established.

---

# Phase 1 interpretation before architecture exposure

## Directly supported requirements

1. **Do not collapse all non-decisions into one abstention.** Current production already correctly distinguishes several causes.
2. **Measurement must remain separate from decision permission.** Current code already measures without trust/nomination inputs, then applies trust-related policy later.
3. **Non-deciding measured evidence must remain retained.** Current P1/P2 loop already preserves the original entailment rows while removing them from the deciding pool.
4. **The final causal/participation state is not first-class in v1 `AuditTrace`.** It currently must be reconstructed from raw measurements, rule receipts, policy, and bound inputs.
5. **Execution failure and epistemic non-decision are different concepts.** Contract C 1.0.0 already requires this distinction.
6. **Source trust and proposition-specific eligibility are not the same recorded fact.** Current P1 directly uses `trust_level` as its eligibility precondition; issue #3 explicitly leaves this semantic promotion unresolved.

## Not established in Phase 1

- that CAL needs five software stages;
- that the historical v2 implementation is correct;
- that every generic Contract-C assessment slot must be executed by CAL v1;
- that a new production verdict enum is required;
- that multi-passage composition should be added;
- that `trust_level` must become irrelevant to policy;
- that model quality rather than representation/policy contributes nothing to current abstention behavior.

## Strongest current alternative explanations

Current abstention/non-decision behavior could arise from several independent mechanisms rather than one architectural defect:

- representation loss at the final basis/participation layer;
- a policy choice that promotes source-class metadata into adverse-decision eligibility;
- missing proposition-specific context (eligibility/applicability/authority/completeness);
- bounded aggregation semantics (`max_entailment`);
- model measurement quality / calibration;
- gate ordering / early returns;
- caller-level execution-failure handling.

Phase 2 must discriminate these rather than attributing all symptoms to pipeline structure.
