# Production Trace → Explicit Decision Model Shadow — Results

## Status

**Experiment class:** Research Infrastructure / epistemic-machinery

**Terminal disposition:** `SHADOW_COMPATIBLE_WITH_GAPS`

This record does not authorize production promotion, replacement of the released CAL decision substrate, threshold tuning, validation/test optimization, or release/version changes.

## Exact authority and frozen objects

- repository: `camerontjs-dot/claim-audit-lab`
- exact production base: `53f0885b111676794d1bd20e10b91aa58b07e9d4`
- preregistration commit: `0db9f18f40117c274df32dba999cba176752281b`
- frozen diagnostic corpus: `tests/v1/test_pipeline_e2e.py::CASES`
- corpus git blob: `48a22cfab82ea0a2abd8d1c80d0da32a3dacd260`
- frozen replay adapter: `scripts/decision_model_replay.py`
- replay adapter git blob: `cb26ba5a5ba9174dedbd686ea10dffcaae1a80db`
- frozen explicit decision model: `src/claim_audit_lab/v1/decision_model.py`
- decision-model git blob: `f0d9d3bc061d966ed9c8c16b3424b3dd5c3bb339`
- frozen evidence-state projection git blob: `e873772588e8c6ac27ced79559812afc8f5e9cdc`
- frozen semantic-operator git blob: `ae64056d2cbec4ed7fd615fe3f4fa6f2bebb177f`

The protected-surface workflow verified that `src/`, the frozen replay/eligibility/operator scripts, `tests/v1/test_pipeline_e2e.py`, and `pyproject.toml` remained unchanged from the exact production base during the experiment.

## Corpus aperture and leakage control

The experiment used the complete 25-case `CASES` collection from the existing production E2E fixture as a synthetic diagnostic text surface.

Only claim IDs/text, passage IDs/text, and passage `source_meta` were used as inputs. The fixture's stub retrieval scores, stub NLI values, expected verdicts, expected rules, and golden trace expectations were not consumed for candidate scoring, threshold selection, calibration, or disagreement repair.

Every retrieval and NLI measurement reported below was regenerated through the exact current `run_default_audit` path with the pinned real retriever and pinned real DeBERTa entailer.

The fixture contains pre-existing software-regression expectations, not scientific human/LLM gold. Those expectations were not used as evaluation or tuning labels in this experiment.

## Frozen shadow policy

No threshold search was performed.

- evidence-state signal floor: `0.20`
- candidate support threshold: `0.70`
- candidate refutation threshold: `0.70`

The 0.70/0.70 thresholds were frozen before execution because they match both the current production supported/contradicted thresholds and the existing decision-model replay test policy.

## Adapter construction

The experiment reused the existing machinery rather than implementing a second decision function:

1. `run_default_audit` generated the real current production `AuditTrace`.
2. The original `AuditRequest` was separately receipt-bound because production `AuditTrace` drops passage `source_meta` needed by the existing eligibility replay.
3. `scripts/evidence_state_eligibility_shadow.py` projected raw and eligible channel state.
4. `scripts/evidence_state_operator_shadow.py` projected recorded semantic-operator judgments and preserved missing judgments as unknown.
5. `scripts/decision_model_replay.py` built the existing contribution ledger, channel aperture assessments, ordered stage receipts, and explicit decide-or-abstain trace.
6. A thin research-only orchestrator compared the two paths and applied the preregistered disagreement taxonomy.

No candidate decision semantics were changed after observation.

## Execution receipts

### Primary valid execution

- workflow run: `33275184773`
- execution head: `2f8f9e1447ab1f52d2c43caafb4505e436142969`
- `RESULTS.json` SHA-256: `sha256:57eb3e5445b3887a8ffd105f72d30ba2e0779d644dba4d25512c119d850d1090`
- artifact ID: `9721292244`
- artifact ZIP SHA-256: `sha256:b84ab780c6cd0d1475a4ca969ee595c09e069025b376eaa505600595cb06d439`
- artifact files: 128

### Independent repeat

- workflow run: `33275342888`
- execution head: `e864f3e12942bf3f47306ba895b8b965b638dae0`
- `RESULTS.json` SHA-256: `sha256:a2bab28e138fbadc8343d4efce29d8e42823bf8ee97f1a41fa094b9f45da9bdf`
- artifact ID: `9721337978`
- artifact ZIP SHA-256: `sha256:ff99e54b5b3f5b0ab81acc70d1f1a6a84c1c83b5fcb7093b84983e45bf797b59`
- artifact files: 128

The raw result hashes differ because `RESULTS.json` embeds the execution head SHA. After removing only `execution_head_sha`, the two `RESULTS.json` objects are exactly equal. All 25 per-case rows, quantitative summaries, metamorphic reports, output-coverage matrices, and underlying case artifacts are exactly equal. Across the two 128-file artifact trees, only `RESULTS.json`, `RESULTS.sha256`, and `summary.json` differ, transitively because of the execution-head/result checksum metadata.

See `RESULT_RECEIPT.json` for the compact frozen receipt.

## Preserved apparatus failures and deviations

Failures were not erased from the research history.

1. **Run `33274969229`: masked execution failure.** The scientific script failed before case execution with `ModuleNotFoundError: No module named 'research'`. The workflow piped through `tee` without `pipefail`, so the job status incorrectly appeared green. The same run independently showed six metamorphic controls passing and 56 existing decision/evidence/operator tests passing. Ruff also rejected research-harness style. No scientific result from this run is accepted.
2. **Run `33275106892`: truthful bootstrap failure.** After adding `pipefail` and module invocation, the dynamic import of the frozen E2E fixture failed during Python 3.11 dataclass processing because the module had not been registered in `sys.modules`. The failure occurred before case execution or model measurement. No scientific result from this run is accepted.
3. **Run `33275184773`: first valid scientific result.** All 25 real-model cases executed and the shadow replay completed. The separate protected-surface job passed its semantic checks, metamorphic controls, existing tests, and Ruff lint, but an experiment-authored Ruff formatting check remained red. That formatting gate did not affect the scientific job.
4. **Run `33275342888`: fully green repeat.** The non-semantic format-only check was removed; protected surfaces, six metamorphic controls, 56 existing tests, lint, and real-model shadow execution all passed. Scientific outputs reproduced exactly as described above.

The only post-preregistration changes were apparatus corrections required to make execution status truthful and fixture loading mechanically valid. No corpus content, production code, frozen adapter code, candidate decision logic, taxonomy, thresholds, or disagreement outcomes were changed.

## Quantitative comparison

| Measure | Result |
|---|---:|
| Total claims | 25 |
| Legacy `supported` | 10 |
| Legacy `contradicted` | 5 |
| Legacy `unsupported` | 1 |
| Legacy `not_checkable` | 9 |
| Candidate `supported` | 10 |
| Candidate `contradicted` | 4 |
| Candidate `abstain` | 11 |
| Terminal agreements | 23 |
| Terminal agreement rate | 0.92 |
| Terminal disagreements | 2 |
| Support → adverse transitions | 0 |
| Adverse → support transitions | 0 |
| Raw evidence present but excluded downstream | 5 |
| Valid evidence blocked by aperture | 0 |
| Valid mixed support/refutation states | 0 |
| Adapter-excluded claims | 0 |
| Unclassifiable claims | 0 |

### Disagreements by preregistered taxonomy

| Taxonomy | Count |
|---|---:|
| `semantic_validity_operator_difference` | 1 |
| `unmeasured_state` | 1 |
| all other categories | 0 |

### First material divergence across all claims

This count includes internal state divergences even when terminal outcomes still agree.

| First divergence stage | Count |
|---|---:|
| `semantic_validity` | 5 |
| `aggregate` | 1 |
| no material divergence | 19 |

For terminal disagreements only, both first diverged at `semantic_validity`.

## Exact disagreement explanations

### `e2e-08` — semantic-validity/operator difference

Claim: `The service meets 95 percent uptime and 40 percent capacity.`

Evidence: `The service meets 95 percent uptime and 70 percent capacity.`

**Legacy path**

- admitted passage: `p-1`
- `p_entail = 0.0015592575073242188`
- `p_contradict = 0.9970703125`
- aggregate label: `contradict`
- rule fired: `A4_hard_contradiction`
- legacy verdict: `contradicted`

**Explicit path**

- raw state: `refutation_only`
- eligible state: `refutation_only`
- contribution: `direct:refutation:p-1`
- contribution score: `0.9970703125`
- contribution eligibility: `eligible`
- recorded semantic validity: `unknown`
- operator: `A4_negation_consistency`
- recorded reason: the structural negator abstained, therefore unknown may not decide
- valid state: `read_silent`
- candidate disposition: `abstained`
- candidate reason: `semantic_validity_unknown`
- exact decision-basis contribution ID: `direct:refutation:p-1`
- first material divergence: `semantic_validity`
- taxonomy: `semantic_validity_operator_difference`

**What explains the mismatch:** the two paths consume the same admitted passage and the same NLI measurement. Legacy policy treats the high contradiction probability as sufficient for a hard contradiction. The explicit replay gives the same refutation contribution an explicit `unknown` validity state because the recorded A4 structural check abstained, and unknown validity is non-deciding.

**Important alternative explanation:** this case may expose a limitation in how the existing operator replay applies/interprets the A4 structural-negation receipt for a numeric mismatch that is not itself a simple lexical-negation claim. The experiment does not decide that the candidate or legacy interpretation is correct. It preserves the counterexample. A smaller follow-up can falsify the replay assumption by testing the operator contract on receipt-bound non-negation contradictions versus true structural-negation contradictions, without changing thresholds or using benchmark gold.

### `e2e-09` — unmeasured state

Claim: `All submitted records pass schema validation.`

Evidence: `Most submitted entries satisfy the schema checks.`

**Legacy path**

- admitted passage: `p-1`
- `p_entail = 0.0168914794921875`
- `p_contradict = 0.673828125`
- aggregate label: `contradict`
- rule fired: `B5_degree`
- legacy rule reason: contradiction `0.67 < 0.70` so evidence leans against
- legacy verdict: `unsupported`

**Explicit path**

- raw state: `refutation_only`
- eligible state: `refutation_only`
- contribution: `direct:refutation:p-1`
- contribution score: `0.673828125`
- contribution eligibility: `eligible`
- semantic validity: `unknown`
- operator: `refutation_operator_unmeasured`
- recorded reason: no explicit semantic-validity judgment covers this refutation
- valid state: `read_silent`
- candidate disposition: `abstained`
- candidate reason: `semantic_validity_unknown`
- exact decision-basis contribution ID: `direct:refutation:p-1`
- first material divergence: `semantic_validity`
- taxonomy: `unmeasured_state`

**What explains the mismatch:** this is not a threshold disagreement. The legacy degree rule turns a sub-threshold contradiction measurement into the five-valued reporting outcome `unsupported`. The explicit machinery refuses to treat that refutation contribution as valid because no semantic-validity operator measured it. The missing measurement is preserved as unknown rather than reconstructed from the legacy verdict.

## Internal divergences without terminal mismatch

Four additional claims exposed useful internal distinctions while preserving terminal agreement:

- `e2e-22`: raw `mixed` → eligible `mixed` → valid `support_only`; the supportive contribution remains valid while the strong refutation contribution has unmeasured validity. Candidate abstains with `semantic_validity_unknown`. Legacy also returns `not_checkable` through its conflicting-evidence rule. This shows that terminal `not_checkable` hides a materially richer evidence state.
- `e2e-25`: raw/eligible `refutation_only` → valid `read_silent`; A4 explicitly invalidates the contradiction contribution. Candidate abstains `no_valid_contribution`; legacy returns `not_checkable` after its unconfirmed-contradiction rule.
- `e2e-24`: raw/eligible `refutation_only` → valid `read_silent`, but the claim is out of scope. Candidate abstains `out_of_scope`; legacy returns `not_checkable` from the scope rule.
- `e2e-21`: no passage cleared retrieval admission. Candidate records `no_evidence`; legacy returns `not_checkable` via `A2_retrieval_empty`. The comparison marks an aggregation-stage representation difference even though both terminally abstain/not-checkable.

These cases are evidence that terminal agreement alone is insufficient to establish representational equivalence.

## Legacy `not_checkable` split by explicit state

The nine legacy `not_checkable` cases separate as follows:

| Raw → eligible → valid | Candidate reason | Count |
|---|---|---:|
| `mixed → mixed → support_only` | `semantic_validity_unknown` | 1 |
| `no_evidence → no_evidence → no_evidence` | `no_evidence` | 1 |
| `read_silent → read_silent → read_silent` | `evidence_read_no_signal` | 3 |
| `read_silent → read_silent → read_silent` | `out_of_scope` | 1 |
| `refutation_only → refutation_only → read_silent` | `no_valid_contribution` | 1 |
| `refutation_only → refutation_only → read_silent` | `out_of_scope` | 1 |
| `support_only → support_only → support_only` | `out_of_scope` | 1 |

This is a direct demonstration of semantic compression in the legacy terminal outcome.

## All 25 case outcomes

| Claim | Legacy | Candidate | Raw | Eligible | Valid | Candidate reason | First divergence | Taxonomy |
|---|---|---|---|---|---|---|---|---|
| `e2e-01` | supported | supported | support_only | support_only | support_only | support_above_threshold | none | none |
| `e2e-02` | not_checkable | abstain | read_silent | read_silent | read_silent | evidence_read_no_signal | none | none |
| `e2e-03` | supported | supported | support_only | support_only | support_only | support_above_threshold | none | none |
| `e2e-04` | supported | supported | support_only | support_only | support_only | support_above_threshold | none | none |
| `e2e-05` | contradicted | contradicted | refutation_only | refutation_only | refutation_only | refutation_above_threshold | none | none |
| `e2e-06` | contradicted | contradicted | refutation_only | refutation_only | refutation_only | refutation_above_threshold | none | none |
| `e2e-07` | not_checkable | abstain | read_silent | read_silent | read_silent | evidence_read_no_signal | none | none |
| `e2e-08` | contradicted | abstain | refutation_only | refutation_only | read_silent | semantic_validity_unknown | semantic_validity | semantic_validity_operator_difference |
| `e2e-09` | unsupported | abstain | refutation_only | refutation_only | read_silent | semantic_validity_unknown | semantic_validity | unmeasured_state |
| `e2e-10` | contradicted | contradicted | refutation_only | refutation_only | refutation_only | refutation_above_threshold | none | none |
| `e2e-11` | supported | supported | support_only | support_only | support_only | support_above_threshold | none | none |
| `e2e-12` | supported | supported | support_only | support_only | support_only | support_above_threshold | none | none |
| `e2e-13` | not_checkable | abstain | read_silent | read_silent | read_silent | out_of_scope | none | none |
| `e2e-14` | not_checkable | abstain | support_only | support_only | support_only | out_of_scope | none | none |
| `e2e-15` | supported | supported | support_only | support_only | support_only | support_above_threshold | none | none |
| `e2e-16` | supported | supported | support_only | support_only | support_only | support_above_threshold | none | none |
| `e2e-17` | contradicted | contradicted | refutation_only | refutation_only | refutation_only | refutation_above_threshold | none | none |
| `e2e-18` | supported | supported | support_only | support_only | support_only | support_above_threshold | none | none |
| `e2e-19` | not_checkable | abstain | read_silent | read_silent | read_silent | evidence_read_no_signal | none | none |
| `e2e-20` | supported | supported | support_only | support_only | support_only | support_above_threshold | none | none |
| `e2e-21` | not_checkable | abstain | no_evidence | no_evidence | no_evidence | no_evidence | aggregate | none |
| `e2e-22` | not_checkable | abstain | mixed | mixed | support_only | semantic_validity_unknown | semantic_validity | none |
| `e2e-23` | supported | supported | support_only | support_only | support_only | support_above_threshold | none | none |
| `e2e-24` | not_checkable | abstain | refutation_only | refutation_only | read_silent | out_of_scope | semantic_validity | none |
| `e2e-25` | not_checkable | abstain | refutation_only | refutation_only | read_silent | no_valid_contribution | semantic_validity | none |

## Preregistered metamorphic controls

All six required controls passed on the unmodified explicit decision model in both valid executions.

| Control | Observed result |
|---|---|
| Irrelevant-evidence addition | PASS. Added below-floor evidence did not enter the basis or change the supported decision. |
| Ineligible-support mutation | PASS. Raw support remained observable; eligible/valid state became `read_silent`; candidate abstained `no_eligible_contribution`. |
| Unknown-validity mutation | PASS. Support remained raw/eligible; valid state became `read_silent`; unknown did not become refutation; candidate abstained `semantic_validity_unknown`. |
| Refutation-channel mutation | PASS. Support remained present; valid state became `mixed`; terminal policy returned `mixed_valid_evidence`. |
| Passage-set mutation | PASS. Complete supporting set could decide; removing a required member plus incomplete aperture prevented unary evidence from masquerading as complete set support. |
| Execution-failure mutation | PASS. Missing a required stage receipt raised `ValidationError` before any `EvidenceDecisionTrace` existed; it did not become an epistemic abstention. |

The required invariants therefore do not falsify the explicit decision model in this experiment.

## Output-coverage audit

| Intended output distinction | Current source | Direct from explicit machinery after legitimate projection? | Legacy trace sufficient? | Gap / finding |
|---|---|---|---|---|
| Current verdict, reason, flags, citation status, confidence | `AuditTrace.verdict` | No | Yes | Explicit decision model does not represent flags, citation status, or audit confidence. |
| Five-valued support degree | `AuditTrace.verdict.support_verdict` | No | Yes | Candidate terminal vocabulary is supported/contradicted/abstain. One observed real case (`e2e-09`) requires legacy `unsupported`; it is not representable as a candidate terminal degree. |
| Retrieval/admission and NLI measurements | `AuditTrace.retrieval` + `AuditTrace.entailment` | Yes | Yes | Same admitted passage IDs and exact channel probabilities are receipt-bound into candidate inputs. |
| Raw support/refutation evidence state | `EvidenceDecisionTrace.raw` | Yes | Yes for recorded channel probabilities | Deterministic at the preregistered signal floor. |
| Eligibility state | request receipt + explicit eligibility projection | Yes | No | Production `AuditTrace` drops passage `source_meta`; replay needs the separately bound `AuditRequest` receipt. |
| Semantic validity/operator state | contribution validity + `EvidenceDecisionTrace.valid` | Yes | Partial | Recorded A3/A4 outcomes can be translated; three cases contain explicit unknown validity, including unmeasured refutation semantics. |
| Aperture/completeness | `EvidenceDecisionInput.apertures` | Yes, but only for the replay's bounded aperture | No | Existing replay can prove only preserved at-floor contribution status. General source/passage-set completeness is not measured by normal production trace. One case has non-complete/unknown replay aperture. |
| Contribution ledger + exact basis IDs | `EvidenceDecisionInput.contributions` + `DecisionOutcome.basis_contribution_ids` | Yes | Partial | Direct NLI contributions are trace-derived. Set/operator contributions require explicit receipts and are not fabricated. |
| Ordered stage receipts | `EvidenceDecisionInput.stage_receipts` | Yes | No | Existing replay receipt-binds handoffs, but several early stages share the same production trace receipt rather than independent execution-state receipts. |
| Execution failure vs epistemic insufficiency | construction/runtime boundary | Not as a typed terminal state | No | Missing receipt fails distinctly, but normal `AuditTrace` and `EvidenceDecisionTrace` have no typed execution-failure outcome. |

## What the experiment establishes

### OBSERVED

- The current real CAL execution path can generate evidence that the existing explicit decision machinery consumes without changing production behavior.
- Admission identity and NLI channel values are preserved exactly across the production-to-shadow boundary in this corpus.
- No adapter exclusions occurred.
- The contribution ledger and exact basis IDs are usable for real production-generated measurements.
- The explicit states split legacy `not_checkable` into materially distinct states such as no evidence, evidence read/no signal, mixed unresolved evidence, out-of-scope evidence, and explicit semantic invalidity.
- Five cases contained raw evidence that was excluded before valid decision basis.
- Two terminal disagreements were completely localized, one to an explicit operator-validity disagreement and one to genuinely unmeasured semantic validity.
- Six label-free metamorphic invariants passed.
- Two valid real-model executions reproduced all scientific rows and case artifacts exactly.

### INFERENCE

- The smallest production-adjacent shape justified by this evidence is **A: retain the current legacy trace/verdict behavior and emit a parallel epistemic artifact**.
- That shape exposes information currently compressed by terminal verdicts while preserving current flags, citation semantics, confidence, and five-valued reporting behavior.
- A later additive trace change may be justified for specific observed gaps, especially retaining request/source metadata needed by eligibility and adding explicit receipts for generic aperture/execution state. That is a separate authorization.

### HYPOTHESIS

- A bounded trace-extension experiment could eliminate the request-side metadata sidecar and make execution/aperture receipts first-class without replacing current decision semantics.
- The `e2e-08` counterexample may be resolved by a more precise semantic-operator contract that distinguishes true negation consistency from other contradiction forms such as numeric mismatch. This is not established here and must not be repaired post hoc.

### UNKNOWN

- The correct general semantic-validity operator for refutation shapes not measured by the current production trace.
- Whether A4's existing recorded abstention should semantically gate the numeric mismatch in `e2e-08`, or whether the replay's use of that receipt is overbroad.
- General source/passage-set completeness outside the replay's bounded at-floor aperture.
- Whether a future explicit reporting layer should model legacy `partially_supported`/`unsupported` as terminal degrees or keep those degrees separate from epistemic decide-or-abstain state.
- Whether adding explicit states directly to `AuditTrace` provides enough incremental value to justify shape B after a parallel-artifact trial.

## Migration decision

### A. Keep legacy trace and emit a parallel epistemic artifact

**Supported as the smallest next change.**

Why:

- preserves released verdict semantics and current reporting fields;
- surfaces the observed evidence-state distinctions without reconstructive guessing;
- permits continued shadow comparison;
- contains the risk of unresolved validity/aperture semantics;
- does not require treating 92% terminal agreement as proof of equivalence.

### B. Add required explicit states to the existing trace

**Plausible follow-up, not authorized by this result.**

Observed reasons it may become useful:

- `AuditTrace` drops source metadata needed for current eligibility replay;
- generic aperture/completeness is not measured;
- execution failure is not a typed output state;
- stage receipts are not independently represented for every stage.

The experiment does not justify adding every imaginable epistemic field. Any trace extension should be limited to states required by an observed counterexample or intended output.

### C. Replace the legacy decision substrate while retaining measurement components

**Not supported by this experiment.**

Why:

- two real terminal disagreements remain substantively meaningful;
- the explicit substrate does not directly represent all current reporting outputs;
- one observed production case uses legacy `unsupported`, which the candidate terminal vocabulary cannot emit;
- validity and general aperture remain partially unmeasured;
- architectural cleanliness is not evidence of production equivalence.

## Smallest discriminating next work

If further research is authorized, the smallest high-value sequence is:

1. prototype **A** as a non-promotional parallel epistemic artifact emitted from the real production trace/request boundary;
2. freeze an operator-contract micro-test that distinguishes non-negation contradictions, true structural-negation contradictions, and unmeasured refutations, specifically to test the `e2e-08` replay assumption without threshold tuning;
3. measure whether the parallel artifact can be emitted without a request-side metadata sidecar; if not, add only the minimal typed provenance/eligibility receipt required by the observed gap;
4. keep C out of scope until output-coverage gaps and semantic-validity unknowns have independent evidence.

## Terminal disposition

`SHADOW_COMPATIBLE_WITH_GAPS`

The experiment achieved the intended research objective in the bounded corpus: evidence flow can be shadowed into the explicit contribution-ledger machinery, disagreements can be localized, and semantic compression becomes observable. The remaining gaps are real representation/measurement gaps and are preserved rather than inferred away.

This disposition does **not** authorize production promotion.
