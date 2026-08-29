# Shadow Reconciliation, Semantic-Operator Falsification, and Parallel Epistemic Artifact RC — Results

## Classification

**Research Infrastructure / epistemic-machinery successor experiment.**

This is an evidence record, not production authorization. It does not replace the production CAL decision path, tune NLI thresholds, replace the pinned DeBERTa model, change Contract C, or authorize a generalized redesign.

**Terminal research disposition:** `PARALLEL_RESEARCH_ARTIFACT_JUSTIFIED_WITH_OPERATOR_GAPS`

That disposition means only that the current explicit machinery can truthfully emit a **parallel, non-authoritative research observation artifact** from the real CAL shadow path while preserving observed unknowns. It does not authorize production emission or promotion of the explicit decision substrate.

---

## 1. Live authority record

### OBSERVED

Live GitHub was inspected before implementation and again before terminalization.

- repository: `camerontjs-dot/claim-audit-lab`
- production `main` HEAD: `53f0885b111676794d1bd20e10b91aa58b07e9d4`
- open PRs at terminal sweep:
  - `#35` — Research Infrastructure: CAL machinery audit baseline
  - `#36` — Research Infrastructure: production trace → explicit decision shadow
  - `#37` — Research: reconcile production-trace shadow and falsify semantic-operator authority
- machinery-audit PR `#35` head: `8c7cb29f6251f4f6566ab5fcc501cddc791e3539`
- predecessor shadow PR `#36` head: `b487d1dce4cc1a076e3705b0a7ef457e7d438814`
- successor preregistration commit: `87304482dfa8792fda3ed035c98538603280c3ab`
- accepted successor science branch head: `0d8e67a2cf96e1d6eb665dae2cf9dc11629cfcc8`
- accepted successor Actions run: `33281047763`

The successor is intentionally stacked on the exact #36 head rather than on `main` because it audits and reuses #36's frozen research apparatus.

### Exact frozen/relevant blobs at #36 head

| Surface | Blob SHA |
|---|---|
| `tests/v1/test_pipeline_e2e.py` | `48a22cfab82ea0a2abd8d1c80d0da32a3dacd260` |
| `src/claim_audit_lab/v1/runner.py` | `db53f49745876b6158da0c233fb80916bbeaabaf` |
| production retriever implementation | `279a287e10f5466b8d2985291080bc0183c72a52` |
| production entailer implementation | `aaf9415e74ec2f04357ecf5346491d92f3e2d0d3` |
| production aggregator | `b1f9e2309ae3d024bc609b83cc546acb30be6e9b` |
| production rules | `bc388d64a5a53db0d33610ab6ff84bd93a811b46` |
| production trace models | `755e0ef1757055905f3c8b76b7edc5e8ddc1fefd` |
| `src/claim_audit_lab/v1/decision_model.py` | `f0d9d3bc061d966ed9c8c16b3424b3dd5c3bb339` |
| `src/claim_audit_lab/v1/evidence_state.py` | `e873772588e8c6ac27ced79559812afc8f5e9cdc` |
| `src/claim_audit_lab/v1/semantic_operators.py` | `ae64056d2cbec4ed7fd615fe3f4fa6f2bebb177f` |
| `scripts/decision_model_replay.py` | `cb26ba5a5ba9174dedbd686ea10dffcaae1a80db` |
| `scripts/evidence_state_eligibility_shadow.py` | `46d485f6a2d5f322b5acb860c69cce9896522a2a` |
| `scripts/evidence_state_operator_shadow.py` | `11fedf036a208d94cd7516efdad4a17daa3374c8` |
| Contract C exporter | `d6b32a44ef11109fe0ee91efa212d3904badf58c` |
| #36 `RESULTS.md` | `d6fed3e43ae24cf5125fc5295775571ff9c8d35a` |
| #36 `RESULT_RECEIPT.json` | `97195f0f59a3a8d0adb69e816e902fdc5fc4b38c` |
| #36 shadow runner | `2493ff38c3baa1bad528b125989482175c2aa810` |
| #36 fixture-load/bootstrap entry | `1a0c461c661422669f4b30c93c3db95fff76623f` |
| #36 metamorphic controls | `a121d7560c57991d7e419947cd2115d0e797495e` |

Pinned model revisions and the frozen `0.70 / 0.70` support/refutation thresholds were not changed.

### UNKNOWN

This experiment did not independently re-establish an external truth standard for any fixture verdict. It deliberately did not need one for the operator-authority and unknown-preservation questions under test.

---

## 2. #36 reproduction and audit

### OBSERVED

The accepted successor run regenerated all **25** diagnostic cases through #36's exact real `run_default_audit` production-shadow apparatus.

The fresh predecessor result object had raw SHA:

`sha256:38a92ac641c39000cf20f52feae788a1bbd178912d926d0eae29759068cb1c00`

The frozen fully-green #36 repeat, run `33275342888` at execution head `e864f3e12942bf3f47306ba895b8b965b638dae0`, had raw `RESULTS.json` SHA:

`sha256:a2bab28e138fbadc8343d4efce29d8e42823bf8ee97f1a41fa094b9f45da9bdf`

The raw hashes differ because `RESULTS.json` embeds execution-head metadata. Removing **only** `execution_head_sha` and canonicalizing sorted compact JSON produced the same hash for the frozen repeat and the accepted successor rerun:

`sha256:db6ac4dac26045c0b489cf28a704376b659522979759e33f704706c61472c51d`

The verifier therefore recorded `exact_scientific_object_reproduced: true`.

The reproduced object records:

- 25 total claims;
- 23 terminal agreements and 2 terminal disagreements;
- 0 support → adverse transitions;
- 0 adverse → support transitions;
- all 6 preregistered predecessor metamorphic controls passing;
- `threshold_tuning_performed: false`;
- `production_behavior_changed: false`;
- 0 adapter-excluded claims;
- 0 unclassifiable cases;
- 5 cases with raw evidence excluded before valid basis;
- first internal divergence stage counts of `semantic_validity: 5` and `aggregate: 1`.

The successor workflow also diff-protected the whole `src/` tree, the frozen replay/eligibility/operator scripts, the 25-case E2E corpus, and `pyproject.toml` against the exact #36 head. That protection passed.

### OBSERVED: expected fixture verdicts were not a decision input

The #36 apparatus regenerates model measurements from the real CAL path and constructs explicit contributions from measurements/receipts. The predecessor record states fixture stub scores and expected verdicts/rules were not used for candidate scoring or threshold selection, and the accepted successor reproduction preserved that apparatus unchanged. No threshold search or repair loop exists in the successor.

### INFERENCE

The important success criterion is not the 23/25 terminal agreement. The stronger evidence is:

1. the scientific object reproduced exactly modulo execution-head metadata;
2. support/adverse polarity did not flip across the shadow boundary;
3. the six predecessor metamorphic controls and nine successor invariants held;
4. the two terminal disagreements remained attributable to typed internal-state differences rather than being patched into parity.

### UNKNOWN

The 25-case diagnostic corpus is not broad enough to estimate population-level operator coverage, calibration, or downstream utility.

---

## 3. Research-apparatus cleanup audit

### OBSERVED

PR #36 changed research/workflow apparatus only. No production source file was changed by that PR.

The audit found **no predecessor file whose deletion was demonstrably justified**:

- `run_shadow_experiment_entry.py` is not obsolete. It preserves the Python 3.11 dynamic-module registration behavior required after the truthful fixture-loading failure exposed by run `33275106892`.
- `RESULTS.md` and `RESULT_RECEIPT.json` are evidence records, not disposable generated output.
- #36's scoped Ruff configuration remains tied to the frozen research harness.
- the 25-case fixture loader remains necessary to reproduce the exact diagnostic aperture.
- no committed generated artifact directory was found that should be purged from the evidence branch.
- no accidental production-path mutation was found.

The successor made only narrow research-apparatus corrections:

1. it added a preregistered operator-applicability layer without editing the frozen explicit machinery;
2. it added exact normalized-result reproduction verification;
3. after an initial successor run used a different output directory, it restored #36's exact artifact path so evidence-path receipts were reproduced truthfully;
4. it fixed successor-only Ruff annotations/style after the first science-complete but lint-red run.

### Preserved deviations

The record intentionally retains:

- predecessor run `33274969229`: incorrect module invocation plus `tee` without `pipefail` masked the script failure;
- predecessor run `33275106892`: Python 3.11 fixture-loader failure before scientific execution;
- predecessor run `33275184773`: valid science with formatting-only red status;
- predecessor run `33275342888`: fully-green frozen repeat;
- successor run `33280935112`: science and all falsifiers completed, but successor Ruff failed and the predecessor output path was not yet exact;
- successor run `33281047763`: accepted branch-head execution with exact-path reproduction and all jobs green.

### INFERENCE

Deleting or rewriting any of those failed/deviant records would reduce the evidentiary value of the experiment. The smallest justified cleanup was to repair the harness forward and preserve the record.

---

## 4. e2e-08 falsifier result

### Receipt-bound observations

**Claim:** `The service meets 95 percent uptime and 40 percent capacity.`

**Evidence:** `The service meets 95 percent uptime and 70 percent capacity.`

- request receipt: `sha256:c44be2b4fff60a474bc515e4f4261388b7599a4321f9aaed4eef73a909ba9d9e`
- trace receipt: `sha256:3f4e19e6e628d48a788efbde9bc9270acc0a34c9163fdc91922ebb199eb688fc`
- retrieved passage: `p-1`
- direct NLI label: `contradiction`
- `p_contradict = 0.9970703125`
- `p_entail = 0.0015592575073242188`
- recorded structural-negation probe: `negated_claim = null`, `abstained = true`, `result = null`
- legacy production rule path: A4 hard contradiction
- predecessor explicit raw state: `refutation_only`
- predecessor explicit eligible state: `refutation_only`
- predecessor explicit semantic-valid state: `read_silent`
- predecessor explicit validity: `unknown`, labeled as `A4_negation_consistency`
- predecessor explicit terminal result: abstain / `semantic_validity_unknown`

### HYPOTHESIS

The predecessor replay was giving an abstained A4 structural-negation probe generic authority over a refutation contribution even when A4 had produced no canonical semantic target for this claim.

### FALSIFIER RESULT: `SUPPORTED_WITH_BOUNDS`

The research-only applicability projection calls the existing guarded `project_negation()` first. For this exact claim it returns:

- applicability: `inapplicable`
- projection kind: `unknown`
- canonical hypothesis: none
- reason: `claim is outside the guarded semantic-operator grammar`

Therefore the A4 receipt contains **no semantic measurement over this numeric/compound mismatch**. Treating A4's abstention as if A4 had measured the refutation's validity is not warranted.

The bound matters. This does **not** establish that the refutation is semantically valid and does not authorize an explicit `contradicted` decision. No typed numeric/quantity relation receipt exists in the frozen object. Once A4 is correctly identified as inapplicable, semantic validity remains unknown unless another applicable operator supplies authority.

### Counterexample that limits the claim

Not every numeric or quantity mismatch is outside A4. Other claims in the diagnostic fixture can produce a canonical complement and a completed A4 probe. The result is therefore **claim/projection/receipt-specific**, not a blanket rule that numeric text can never use structural negation.

### INFERENCE

The first localized failure for e2e-08 is **operator applicability / missing typed semantic assessment**, not retrieval. The relevant passage was retrieved and measured. The NLI measurement may itself still be right or wrong, but this experiment does not need to settle that to show that the existing A4 receipt is not authorized to adjudicate this semantic family.

### UNKNOWN

A correct typed operator for numeric equality, quantities, inequalities, or compound propositions has not been established here. That is a separate experiment.

---

## 5. e2e-09 interpretation result

### Receipt-bound observations

**Claim:** `All submitted records pass schema validation.`

**Evidence:** `Most submitted entries satisfy the schema checks.`

- direct adverse NLI measurement: `p_contradict = 0.673828125`
- frozen refutation decision threshold: `0.70`
- legacy terminal/reporting state: `unsupported`
- legacy fired rule: `B5_degree`
- explicit operator-judgment count: **0**
- explicit refutation eligibility: `eligible`
- explicit refutation validity: `unknown`
- explicit validity operator marker: `refutation_operator_unmeasured`
- explicit terminal result: abstain / `semantic_validity_unknown`

### HYPOTHESIS

`unsupported` is functioning in this case as a legacy degree-of-support/reporting category derived from a sub-threshold adverse NLI signal, not as proof that an adverse proposition has been independently semantically validated.

### FALSIFIER RESULT: `SUPPORTED_WITH_BOUNDS`

The frozen trace contains no independent semantic-validity judgment for this refutation. The adverse information available is the NLI channel measurement plus B5's reporting rule. Reusing the terminal legacy word `unsupported` as if it were a validated adverse epistemic state would manufacture assessment state that does not exist in the receipts.

### What information is actually required to distinguish the states

| State to distinguish | Required observed information |
|---|---|
| evidence read with weak/no support | admitted evidence + support measurement(s) + eligibility/aperture state; no adverse validity may be inferred from low support alone |
| evidence leaning adverse but not semantically validated | adverse NLI measurement, possibly sub-threshold, plus explicit absence/unknown of a terminal semantic-validity receipt |
| validated weak refutation | an applicable receipt-bound semantic operator returns `valid` for the refutation, while the validated contribution remains below the decision threshold |
| genuine contradiction | eligible refutation + applicable terminal semantic-validity receipt + required aperture/completeness satisfied + decision measurement meeting the frozen contradiction threshold |
| unknown semantic validity | operator missing, inapplicable, abstained, receipt-mismatched, or otherwise unresolved, with no other applicable operator supplying authority |

### INFERENCE

For e2e-09, the disagreement localizes primarily to **policy/reporting vocabulary plus missing semantic assessment state**, not to evidence retrieval. It is not evidence that the NLI model should be replaced.

### UNKNOWN

Whether a future semantic operator would validate, invalidate, or leave this quantifier/degree relation unresolved remains unknown.

---

## 6. Semantic-operator applicability matrix

The matrix below records the authority supported by the current measured surfaces. `May decide?` means only under the explicit decision machinery's independent eligibility/aperture requirements.

| Evidence/claim phenomenon | Measurement available | Semantic operator applicable | Operator authority | Unknown behavior | May decide? |
|---|---|---|---|---|---|
| direct entailment | direct NLI `p_entail` per admitted passage | direct claim identity | support contribution can be semantically direct without polarity transform | missing measurement, eligibility, or aperture remains unknown | yes, conditionally |
| direct contradiction | direct NLI `p_contradict` per admitted passage | none generically; A4 only when a canonical complement exists and an exact probe is receipt-bound | the NLI score is a measurement, not by itself a generic semantic-validity receipt in the explicit machinery | no applicable terminal operator leaves validity unknown | no, absent applicable validation |
| explicit negation | direct NLI plus structural/quantifier-aware complement probe when constructible | A4 / guarded quantifier-aware negation | terminal only for the exact canonical complement, contribution passage set, and completed receipt | ambiguous scope, abstention, or receipt mismatch remains unknown | conditional |
| numeric mismatch | direct NLI; production also extracts quantities | A4 only if canonical complement actually exists; otherwise typed numeric relation machinery is required | structural-negation abstention has no numeric authority | unvalidated numeric relation remains unknown | conditional |
| threshold mismatch | direct NLI plus extracted bound language | structural negation only if it provides an exact target; otherwise interval/bound semantics required | generic negator may not invent inequality semantics | unvalidated bound relation remains unknown | conditional |
| quantity mismatch | direct NLI plus extracted values/units | requires quantity comparability; structural negation can only be auxiliary when canonical | value/unit comparability must be measured, not assumed | incomparable/unmeasured quantity relation remains unknown | conditional |
| categorical incompatibility | direct NLI | A4 may test canonical `not-P`; category exclusivity is not a generic built-in theorem | only exact receipt-bound complement probe has authority | unmodeled exclusivity remains unknown | conditional |
| scope mismatch | direct NLI plus current narrow scope detector where applicable | semantic operator cannot override scope/eligibility mismatch | scope/eligibility gate precedes contribution decision authority | unresolved scope remains abstention | no while scope unresolved/mismatched |
| quantifier mismatch | direct NLI; limited guarded negative-existential projection | quantifier-aware negation only inside pinned grammar | there is no general quantifier theorem prover | unsupported/ambiguous quantifier scope remains unknown | conditional inside guarded grammar |
| degree mismatch | direct NLI plus legacy B5 degree mapping | no generic typed degree operator observed in explicit path | legacy reporting degree is not a semantic-validity receipt | weak/adverse measurement without validation remains unknown | no adverse epistemic decision from B5 alone |
| multi-passage composition | per-passage channel measurements; research set operators exist | only explicit set/composition operators with exact passage-set receipts | no scalar aggregate or composition theorem may be invented when method is absent | unmeasured composition/incomplete passage set remains unknown | conditional |
| mixed support/refutation | independent support/refutation channels | operators assess contributions independently | score ordering may not erase the opposite valid channel | valid mixed state remains mixed | no under current explicit resolver |
| out-of-scope evidence | measurements may remain observable | scope/eligibility gate precedes semantic decision authority | semantic measurement cannot override out-of-scope status | unresolved scope remains abstention | no |
| no applicable semantic operator | possibly a direct NLI measurement only | none | none | semantic validity remains unknown; absence is not contradiction or invalidity | no |

### INFERENCE

A useful contract distinction is therefore:

`operator applicability` ≠ `semantic validity`

An operator can be inapplicable without having measured anything. An applicable operator can also return an unresolved/unknown assessment. Neither state grants decision authority.

---

## 7. Mutation/metamorphic receipts

### OBSERVED

Accepted Actions run `33281047763` passed all successor and predecessor invariant checks on unchanged explicit machinery.

Successor checks:

1. `e2e-08` numeric contradiction does not silently inherit A4 authority when no canonical A4 target exists;
2. unknown semantic validity cannot decide;
3. removing a semantic-validity receipt cannot strengthen a conclusion;
4. replacing an applicable operator with an inapplicable operator removes decision authority;
5. adding irrelevant evidence cannot strengthen the decision basis;
6. ineligible evidence remains observable in raw state but cannot decide;
7. mixed valid support/refutation remains mixed and abstains;
8. execution failure remains distinct from epistemic abstention;
9. operator-contract matrix covers all preregistered phenomenon families.

All **9/9** passed.

The predecessor's six preregistered metamorphic controls were rerun and all **6/6** passed.

The existing explicit decision-model, evidence-state, eligibility-shadow, operator-shadow, and semantic-operator test surfaces also passed. Successor Ruff passed. The protected-surface diff passed.

### INFERENCE

These invariants are stronger evidence for the intended unknown-preserving behavior than terminal legacy-label parity because they make specific kinds of semantic strengthening costly to fake.

---

## 8. Parallel epistemic artifact recommendation

### OBSERVED

The successor emitted **25** typed parallel research artifacts from the freshly regenerated real CAL shadow objects.

Each completed artifact can preserve, where observed:

- exact request and AuditTrace receipts;
- exact source passage IDs from the separately hash-bound `AuditRequest`;
- exact direct model/NLI measurements;
- raw evidence state;
- eligible evidence state;
- semantic-valid evidence state;
- contribution ledger;
- aperture records;
- ordered stage receipts;
- explicit decision or abstention basis;
- operator/validity receipts;
- explicit unknowns;
- causal basis contribution IDs where represented.

A separate typed failure envelope was mutation-tested so execution failure cannot masquerade as epistemic abstention.

The artifact:

- does not replace `AuditTrace`;
- does not call or change Contract C;
- does not mutate production state;
- is emitted only by research code;
- does not read `AuditTrace.verdict` to manufacture explicit epistemic state.

### Recommendation

**YES, with a narrow boundary:** the parallel epistemic artifact is justified as a **non-authoritative research observation surface** for larger shadow studies.

It is **not** justified as:

- a production output contract;
- a second hidden production decision path;
- a replacement for `AuditTrace`;
- a Contract C revision;
- evidence that the explicit decision machinery should be promoted.

### INFERENCE

The value of the artifact is precisely that it exposes distinctions that the legacy terminal vocabulary compresses. Promotion would destroy the experimental separation that currently makes those distinctions auditable.

### UNKNOWN

- whether a real independent downstream consumer finds these fields sufficient;
- whether operator coverage remains adequate on heterogeneous real corpora;
- whether aperture/completeness state can be truthfully populated outside the diagnostic fixture;
- whether causal multiplicity is represented richly enough for future consumers;
- whether the artifact should ever become a production contract.

---

## 9. Larger shadow study

A larger heterogeneous study is justified **for design, not execution in this RC**.

See `CROSS_CORPUS_PREREGISTRATION.md`.

The preregistration uses phenomenon strata rather than a single total-N target and explicitly seals expected labels from the adaptation/tuning path. The smallest immediately available larger input surface is the 33-case Construction Invariant Gold registry on the frozen production main, but its expected outcomes are not authorized as threshold/operator repair signals.

---

## 10. External NLI research boundary

### OBSERVED

The pinned DeBERTa model and thresholds were unchanged.

For both focal disagreements, the relevant evidence passage was retrieved and measured. The unresolved distinction occurs downstream of retrieval.

### INFERENCE

- e2e-08 is first localized to **operator applicability / missing typed relation state**. The NLI contradiction measurement exists, but A4 did not semantically adjudicate this claim.
- e2e-09 is first localized to **legacy reporting policy plus missing semantic-validity state**. A sub-threshold adverse NLI score is not an operator receipt.

Neither result is evidence that a model replacement is the smallest next test.

### UNKNOWN

The NLI measurement itself may still be wrong in either case. A future model-comparison study becomes justified only after an input set and typed semantic target can distinguish NLI measurement error from operator/policy error without tuning on disagreements.

---

## Terminal interpretation

### OBSERVED

The real 25-case scientific object reproduced exactly modulo execution-head metadata. Protected semantic surfaces remained unchanged. Fifteen preregistered/predecessor invariant controls passed. The two material disagreements remain visible rather than repaired.

### INFERENCE

The successor resolves the smallest ambiguity needed for the next step:

- **operator inapplicability is not a measurement of semantic invalidity;**
- **an adverse NLI measurement is not, by itself, a semantic-validity receipt;**
- **legacy `unsupported` must not be reverse-engineered into missing epistemic state.**

### HYPOTHESIS FOR NEXT STUDY

A larger phenomenon-stratified shadow will show that the parallel artifact improves failure localization by exposing first divergence stage, state compression, operator coverage, and unknown creation/removal without increasing support↔adverse polarity transitions.

### UNKNOWN

That hypothesis has not yet been tested outside the 25-case diagnostic fixture. No promotion follows from this RC.
