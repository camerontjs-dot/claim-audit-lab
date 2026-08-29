# Production Trace → Explicit Decision Model Shadow — Preregistration

## Classification

Research Infrastructure / epistemic-machinery experiment only.

This record does not authorize production CAL changes, decision-model promotion, threshold tuning, validation/test optimization, release/version changes, or reinterpretation of scientific gold.

## Frozen authority

- repository: `camerontjs-dot/claim-audit-lab`
- exact production base: `53f0885b111676794d1bd20e10b91aa58b07e9d4`
- machinery-audit predecessor: draft PR #35, base `53f0885b111676794d1bd20e10b91aa58b07e9d4`, head `8c7cb29f6251f4f6566ab5fcc501cddc791e3539`
- diagnostic corpus object: `tests/v1/test_pipeline_e2e.py`, blob `48a22cfab82ea0a2abd8d1c80d0da32a3dacd260`
- replay adapter: `scripts/decision_model_replay.py`, blob `cb26ba5a5ba9174dedbd686ea10dffcaae1a80db`
- explicit decision model: `src/claim_audit_lab/v1/decision_model.py`, blob `f0d9d3bc061d966ed9c8c16b3424b3dd5c3bb339`
- evidence-state projection: `src/claim_audit_lab/v1/evidence_state.py`, blob `e873772588e8c6ac27ced79559812afc8f5e9cdc`
- semantic operators: `src/claim_audit_lab/v1/semantic_operators.py`, blob `ae64056d2cbec4ed7fd615fe3f4fa6f2bebb177f`

## Research question

Can evidence actually produced by the current real CAL execution path be projected into the existing explicit contribution-ledger decision machinery without guessing away evidence state, and can every legacy/candidate disagreement be localized to a typed stage or preserved as projection insufficiency / unknown?

A terminal verdict mismatch is not an explanation.

## Frozen corpus aperture

Use the existing `CASES` text fixtures from `tests/v1/test_pipeline_e2e.py` as a diagnostic input surface.

Use only:

- claim ID / claim text;
- passage ID / passage text;
- existing passage `source_meta`;
- existing request-level source-boundary fields when present.

The fixture's stub retrieval scores, stub NLI outputs, expected legacy verdicts, expected rules, and golden trace expectations are not candidate inputs and are not used to tune, calibrate, or select thresholds.

The corpus is synthetic and contains no human or LLM scientific labels. Its test expectations are pre-existing software-regression expectations. In this experiment they are not used as evaluation gold. All retrieval and NLI measurements are regenerated through the current real pinned production components.

If the module cannot be loaded without changing its semantic contents, or fewer than the complete existing `CASES` collection can be executed for apparatus reasons, record the exclusion and do not silently substitute new cases.

## Frozen policy

No threshold search is permitted.

- retrieval/admission: current production config from the exact base;
- shadow signal floor: `0.20`, the existing evidence-state shadow default;
- candidate support threshold: `0.70`;
- candidate refutation threshold: `0.70`.

The 0.70/0.70 candidate thresholds are frozen before execution because they equal the current production supported/contradicted thresholds and the existing `test_decision_model_replay.py` replay policy. They are not fitted to this corpus.

## Existing adapter rule

Reuse `scripts/decision_model_replay.py`, `scripts/evidence_state_eligibility_shadow.py`, and `scripts/evidence_state_operator_shadow.py` wherever their contracts are satisfied. Do not create a second decision implementation.

A thin orchestration adapter may:

1. execute `run_default_audit` on each frozen case;
2. persist the exact resulting `AuditTrace`;
3. bind request metadata lost by `AuditTrace` as an immutable request-side receipt;
4. invoke the existing eligibility/operator/replay builders per claim;
5. combine their outputs without changing candidate semantics;
6. classify disagreements and audit output coverage.

If a required state is not present in production trace or a legitimate request/sidecar receipt, classify it as adapter/projection insufficiency or unmeasured state. Do not infer it from the desired verdict.

## Preregistered disagreement taxonomy

Exactly one primary category is assigned to each material disagreement. Secondary observations may be retained separately.

1. `retrieval_admission_difference` — passage identity/admission differs before measurement.
2. `measurement_nli_difference` — the candidate consumes a different measured channel value than the real trace.
3. `eligibility_difference` — explicit eligibility changes participation before semantic validity.
4. `semantic_validity_operator_difference` — an explicit validity/operator assessment changes participation or remains unknown.
5. `aperture_completeness_difference` — completeness/aperture blocks or changes the candidate outcome.
6. `aggregation_composition_difference` — the same eligible/valid measured material is represented differently by channel/set aggregation before terminal policy.
7. `final_decision_policy_difference` — upstream material is aligned, but the legacy degree/rules and candidate decide-or-abstain policy resolve it differently.
8. `adapter_projection_insufficiency` — a required mapping cannot be made without information absent from legitimate trace/request/operator receipts.
9. `unmeasured_state` — a required semantic/eligibility/aperture/execution state was never measured.
10. `unknown_unclassified` — evidence is insufficient to assign another category without speculation.

First-divergence stage order is frozen as:

`retrieve_admit → measure → eligibility → semantic_validity → aperture → aggregate → resolve`.

## Agreement rule

Agreement is intentionally narrow:

- legacy `supported` ↔ candidate `supported`;
- legacy `contradicted` ↔ candidate `contradicted`;
- legacy `not_checkable` ↔ candidate `abstain` only when the candidate reason does not assert a contradictory stronger state than the legacy trace.

Legacy `partially_supported` and `unsupported` are not silently collapsed into candidate abstention. They are recorded as output-policy/representation disagreements unless an earlier typed divergence explains the case.

## Required quantitative outputs

Report:

- total claims and adapter exclusions;
- legacy verdict counts;
- candidate decision/abstention counts;
- agreement count/rate;
- disagreements by taxonomy;
- first-divergence stage counts;
- legacy `not_checkable` split by candidate raw/eligible/valid state and candidate reason;
- support-to-adverse and adverse-to-support transitions;
- raw evidence present but excluded;
- valid evidence present but aperture blocked;
- mixed support/refutation cases;
- unclassifiable cases.

No single accuracy number is a sufficient result.

## Required metamorphic controls

These controls use receipt-bound synthetic state and no benchmark label.

1. **Irrelevant-evidence addition**: add an admitted/measured passage below the signal floor. Expected: it cannot enter decision basis or alter the decision.
2. **Ineligible-support mutation**: change otherwise supportive contribution eligibility to `ineligible`. Expected: raw support remains observable; eligible/valid basis excludes it; it cannot decide.
3. **Unknown-validity mutation**: change validity from `valid` to `unknown`. Expected: unknown is preserved and cannot become negative evidence.
4. **Refutation-channel mutation**: add valid refutation while support is fixed. Expected: support remains visible and the valid state becomes mixed before policy resolution.
5. **Passage-set mutation**: remove one required member of a valid supporting set and mark aperture incomplete. Expected: remaining unary measurements cannot masquerade as complete set support.
6. **Execution-failure mutation**: remove a required stage receipt. Expected: construction/execution fails distinctly rather than producing an epistemic abstention.

A failed expectation falsifies shadow compatibility for the tested invariant. Do not repair the decision model in this experiment.

## Output-coverage audit rule

For each intended output distinction, record whether it is:

- directly emitted by current production trace;
- directly emitted by existing explicit machinery after legitimate projection;
- reconstructable only from a separate legitimate receipt;
- reconstructable only by inference/guessing;
- not representable in the current typed model.

Do not add a new state in this experiment. A missing typed state is justified as a follow-up only by an observed counterexample or an already-required output distinction.

## Stopping / falsification rules

Stop and preserve the result if:

- the real pinned production models cannot execute on the frozen corpus;
- a required source artifact is unavailable;
- the adapter must inspect expected test verdicts to decide a mapping;
- candidate semantics would need modification to complete the comparison;
- thresholds would need tuning after observation;
- the available receipts cannot support a non-speculative disagreement classification.

## Terminal disposition vocabulary

- `SHADOW_COMPATIBLE`: all required distinctions and controls are representable without reconstructive guessing.
- `SHADOW_COMPATIBLE_WITH_GAPS`: the core shadow path is executable and disagreements are localizable, but one or more required outputs/states require an explicit additive receipt/state not present today.
- `DECISION_MODEL_FALSIFIED`: a preregistered invariant of the explicit machinery fails on the observed controls/evidence.
- `APERTURE_INSUFFICIENT`: available legitimate corpus/receipts cannot answer the research question.
- `BLOCKED`: execution cannot complete for an external or apparatus reason.

No disposition authorizes production promotion.