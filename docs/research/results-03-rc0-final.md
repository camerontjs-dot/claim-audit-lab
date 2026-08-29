# CAL Epistemic Methodology RC0 — Terminal report

## Primary research disposition

**INCONCLUSIVE**

## Architecture disposition

**INCONCLUSIVE**

RC0 established several direct facts about current CAL abstention and evidence participation, and it exposed useful mechanisms in the historical v2 branch. It did **not** validly establish the smallest sufficient architecture because the frozen Phase 1 evaluator was discovered after candidate exposure to have omitted preregistered controls material to that decision.

The original frozen apparatus remains preserved. It was not repaired after exposure. A corrected fresh-context successor, RC0A, is preregistered separately.

---

# OBSERVED

## Repository and release state

- CAL current `main` at RC0 start was exactly `e90f301cf6ca02c0c77b6e88c3b08f8b93b9a36a`.
- Immutable CAL `v0.5.0` dereferenced to `5533bbcf27a3ee3a7d901f7dfc44c241bc558e2c`.
- `main` was exactly one commit ahead of v0.5.0, and the only changed file was `.github/workflows/cal-v0.5.0-publication-recovery.yml`. No semantic CAL source/test/config delta existed between the release and current main.
- Immutable Apparatus `contract-c-v1.0.0` dereferenced to `5fe55f9ed5d0ee9f026ca1b077e9d70ce0487ea1`.
- Historical `feat/v2-epistemic-pipeline` was at `b7254e713feb5556a81fb0c5b39649c415a949c6` and was materially diverged from v0.5.0: two commits ahead, seven behind, with merge base `f0c07e8981b3f883b2f0c12fb0c8be1e265b75f2`.

## Current CAL already has multiple non-decision causes

Current production is not a one-state abstention machine.

Released v0.5.0 artifacts directly demonstrate:

- `not_checkable / no_evidence` when no passage clears the retrieval floor;
- `not_checkable / no_entail_signal` when admitted evidence is measured but semantically neutral;
- `not_checkable / out_of_scope` for checkability/scope paths;
- `not_checkable / conflicting_evidence` when both measured channels clear their thresholds;
- an `absence_not_decidable` reason in the released vocabulary.

The frozen v0.5.0 trace for `e2e-15` has retrieval below the floor, no entailment rows, A2, and `no_evidence`. The frozen `e2e-16` trace has an admitted/measured neutral passage, B5, and `no_entail_signal`. Those causes are already distinguishable.

## Upstream nomination does not currently define v1 semantic measurement

`bundle_to_requests` sends the full normalized passage set to v1 rather than filtering semantic candidates from Contract-B support/counterevidence nomination containers.

The v1 entailer is called with claim text, passage text, and passage ID. It does not receive source `trust_level`, upstream support/counterevidence nomination, or downstream decision policy.

Thus the current v1 NLI measurement call already has an important measurement/provenance separation.

## Source trust later affects adverse-decision permission

Contract-B source `trust_level` is copied into `Passage.source_meta`.

Current P1 then treats a present non-`primary` trust level as an adverse-decision suppression condition. A missing trust level is treated as eligible.

A released unit control demonstrates the materially distinct path:

- a background passage is measured as contradiction 0.99;
- P1 suppresses that measured result from the deciding pool;
- the remaining pool becomes neutral/empty;
- terminal output is `not_checkable / no_entail_signal`;
- `P1_eligibility_suppressed` remains in the rule receipts.

This terminal label is the same label an ordinary measured-neutral case can produce, but the causal path is different.

## Non-deciding measured evidence is preserved, but final participation is not first-class

P1/P2 suppression removes an entailment row from the internal deciding pool and re-aggregates. The original `AuditTrace.entailment` still retains the measured row and `rules_fired` retains the suppression receipt.

However, `VerdictRules.apply` returns only the final verdict and rule receipts. The final post-suppression pool and final re-aggregated support signal are not emitted as typed `AuditTrace` fields.

For some paths a reviewer can reconstruct participation by replaying the pinned rules against the bound input and measurement trace. The final deciding/residual classification is not already a first-class v1 state object.

## Current execution failure is not a v1 subject-matter trace state

`run_audit` returns an `AuditTrace` only when the invoked path completes. An exception is not encoded as a subject-matter `not_checkable` trace, but neither does v1 `AuditTrace` itself provide the released Contract-C-style proposition execution state.

Released Contract C 1.0.0 explicitly separates:

- result-set `completed | failed | incomplete`;
- proposition `completed/assessed | completed/not_checkable | failed | incomplete`;
- generic assessment state `not_performed`, performed `unknown`, performed `adverse`, `not_applicable`, or `failed`.

This execution/epistemic distinction is therefore already a released handoff invariant, even though the current promoted Contract-C producer is the bounded v0.2 producer rather than a v1 epistemic-state exporter.

## Historical v2 contains useful mechanisms

Only after Phase 1 freeze commit `9b28df7298257218ec0c9f33163fb60dde71d2a6` was the old branch inspected.

Observed useful mechanisms include:

- explicit `Removal` records with passage, predicate, stage, reason, and details;
- per-passage `eligible_for` roles rather than one global eligible bit;
- retained ineligibility/removal records;
- explicit `deciding_passages`;
- distinct null reasons such as no evidence, all ineligible, no signal, and not resolvable;
- semantic measurements supplied before later qualification/policy handling;
- no upstream nomination role passed into the decision surface.

## Historical v2 does not itself satisfy several RC0 requirements

Direct code inspection also found:

- `_q1_provenance` still treats absent trust as eligible and maps non-primary source class directly to refutation-role ineligibility;
- no generic state distinguishes performed-positive, performed-adverse, performed-unknown, not-performed, not-applicable, and failed proposition-specific assessments;
- `V2Verdict` identifies deciding passages but does not state intervention-derived independent versus joint causal sufficiency;
- no result record represents execution failure when the pipeline raises;
- despite commentary describing a total pipeline with no stage-skipping early return, `run_v2` returns immediately for out-of-form claims and again when all held evidence has no eligible role;
- the branch commentary that v1 never reads the two semantic channels is stale relative to v0.5.0, whose aggregator/rules retain and use best entail/refutation channels for A5 conflict handling;
- the branch's interval algebra, union semantics, and claim-mode machinery introduce additional semantic hypotheses beyond the minimum state-representation question.

## Phase 1 evaluator was frozen before v2 exposure

The first apparatus freeze was commit `9b28df7298257218ec0c9f33163fb60dde71d2a6`.

Frozen identities included:

- fixture blob `1a528e89cb5c6b1354904b2a0fb3323c18b1dd28`;
- evaluator blob `ccd394338dcfa9c12f2a60a5597777653f972335`;
- evaluator-control-test blob `f67371afdc55d923afdf91fc74f8e9398e9d8be7`;
- Phase 1 production-map blob `d6c5823d6a5cf0a83cecaefe1dbdf5db2fd77cee`.

It included two pre-exposure weak controls: a generic abstention collapse and a richer-terminal-reason-only methodology.

## Phase 1 evaluator was later falsified as complete

After v2 exposure, protocol conformance review found that the frozen apparatus omitted material controls explicitly required by the original RC0 task:

1. performed-positive eligibility;
2. the `secondary` value in the primary/secondary/background trust mutation;
3. a complete explicit evidence-presence ladder including zero passages under one fixed claim;
4. separate applicability/temporal/authority unknown-state controls;
5. actual candidate replay under one-at-a-time evidence removal, rather than accepting declared causal form;
6. a policy counterfactual where the named policy is required to change the derived participation/conclusion while measurement remains frozen.

These omissions are recorded in `deviation-03-rc0-phase1-evaluator-coverage.md`.

The frozen evaluator was not modified after this discovery.

## Exploratory architecture adapters are preserved but non-decisive

Before the apparatus defect was recognized, research-only adapters compared:

- current v0.5 observable state;
- terminal-reason-only augmentation;
- a small additive epistemic receipt;
- the historical v2 observable surface;
- an internally staged ledger with the same proposed observable state.

Under the **deficient** evaluator, the additive receipt and staged-ledger shadow candidates were intentionally observationally equivalent, while current/reason-only/v2 surfaces missed different state families.

That is useful hypothesis generation. It is not a valid terminal architecture result because the evaluator did not cover the full preregistered decision surface.

---

# INFERENCE

## What the direct observations support now

RC0 supports a **lower bound** on CAL's required epistemic machinery, not a complete minimum architecture.

At minimum, any future methodology must preserve these distinctions if it claims reconstructability:

1. **semantic measurement versus later policy/permission**: a measured relation must not be rewritten merely because later policy excludes it from deciding;
2. **retained versus deciding evidence**: measured evidence may become residual/non-deciding without being erased;
3. **missing/performed assessment state**: a proposition-specific assessment that did not run cannot be silently represented as a positive/eligible assessment;
4. **execution versus epistemic conclusion**: failed/incomplete execution must remain distinct from completed `not_checkable`;
5. **causal multiplicity when claimed**: exact basis claims require intervention/replay evidence or an explicit unavailable state rather than an arbitrary winner;
6. **policy identity and replay binding**: changing policy must not mutate upstream measurement/evidence facts;
7. **unresolved aggregation remains unresolved** when CAL lacks validated multi-passage composition semantics.

These are state-boundary requirements. They do not imply one software stage per distinction.

## Most important live semantic-policy concern

Current P1 is best described, from the observed code, as a **named source-class adverse-decision policy**. The current record does not establish that source `trust_level` is itself a performed proposition-specific eligibility assessment.

That means a future representation should keep at least three things separable:

- upstream source fact: `trust_level`;
- CAL/named policy effect: which decision roles the evidence may exercise under that policy;
- proposition-specific eligibility/authority assessment: only present as performed when an explicit assessor actually performed it.

RC0 does not establish that trust must cease to affect CAL policy. It establishes that using trust in policy is not the same fact as having assessed proposition eligibility.

## Contract C compatibility is only partial/conceptual at this point

Many RC0 lower-bound concepts already resemble Contract C 1.0.0 state families:

- execution state;
- retained contributions;
- basis versus residual contributions;
- causal multiplicity;
- generic eligibility/semantic-validity/aperture/temporal assessment slots;
- producer/policy identity.

But exact compatibility is **not established**.

Most importantly, Contract C 1.0.0's generic assessment vocabulary does not encode a performed-positive value, while the original RC0 protocol explicitly requires positive/adverse/unknown/not-performed/not-applicable discrimination when eligibility is actually evaluated.

Authority/applicability ownership may also require state not represented by Contract C 1.0.0's exact closed schema.

That is evidence about a future producer/contract-conformance question, not authorization to change Contract C.

---

# FALSIFIED ALTERNATIVES

## “CAL currently collapses all abstention into one generic state”

**FALSIFIED by released traces and vocabulary.**

No-evidence, read-silent/no-entail-signal, out-of-scope, and conflicting-evidence paths are already distinct in current production artifacts.

## “Upstream support/counterevidence nomination is the current v1 semantic label”

**FALSIFIED for the inspected v1 intake/entailer path.**

The full passage set is normalized for v1 and nomination containers are not passed into the NLI call.

## “Historical v2 is a total pipeline in which every stage always executes”

**FALSIFIED as a literal implementation claim.**

`run_v2` contains stage-skipping early returns for out-of-form and all-ineligible paths.

## “The old-v2 commentary is current production truth”

**FALSIFIED.**

The branch is seven production commits behind v0.5.0, and at least one architectural claim, that current v1 never reads both semantic channels, is stale relative to released A5 behavior.

## “The first frozen RC0 evaluator is sufficient for the requested architecture disposition”

**FALSIFIED by protocol audit.**

Required controls were omitted. It is preserved as a failed apparatus rather than repaired after exposure.

---

# HYPOTHESES STILL LIVE

## H1. Additive typed epistemic receipt/state ledger may be sufficient

A small mechanism layered around current measurements/rules could potentially record:

- assessment execution/value;
- retained/deciding/non-deciding evidence;
- named policy effect;
- execution state;
- replay-derived causal basis.

This remains a live hypothesis because the deficient first evaluator did not validly establish sufficiency.

## H2. Partial staged decomposition may be useful without a full pipeline rewrite

Old-v2's explicit removals and per-role participation may be worthwhile mechanisms even if a five-stage software architecture is not necessary.

The corrected evaluator must determine whether these are behaviorally necessary or merely one implementation form.

## H3. A fuller staged pipeline may still be justified

It remains possible that the corrected positive/unknown/applicability/causal-intervention controls expose coupling that a small receipt cannot faithfully reconstruct after the fact.

RC0 did not falsify that possibility.

## H4. Some apparent abstention defects may be primarily policy or measurement problems

Representation is not the only live explanation. Current outcomes may also depend materially on:

- P1 source-class policy;
- NLI/model quality and calibration;
- bounded max-entailment aggregation;
- early-return/control-flow ordering;
- missing upstream proposition-specific context.

The corrected experiment must avoid attributing all symptoms to architecture.

---

# UNKNOWNS

1. Can a real v1 research-only producer derive a complete minimal receipt from frozen v0.5.0 trace + exact Contract-B input + exact policy without changing production verdict behavior?
2. What is the correct representation of **performed-positive** eligibility, and is it CAL-owned for all cases?
3. Does source `trust_level` belong only as retained provenance plus named policy input, or is a separate source-authority assessor required for some propositions?
4. Where should proposition authority/applicability live when it is decision-relevant but not supplied or measured?
5. Can exact deciding/residual/causal state be reconstructed deterministically from current P1/P2 re-aggregation for all relevant paths?
6. Which multi-passage semantics, if any, are justified beyond retaining unresolved partial contributions?
7. Does a corrected strong policy counterfactual expose a state boundary that current traces cannot reconstruct?
8. Does a corrected causal-removal evaluator distinguish a small receipt from a staged internal ledger?
9. Can all minimum methodology state fit Contract C 1.0.0 without semantic loss? Current evidence says this is not established and identifies performed-positive assessment as a concrete compatibility question.

---

# DISPOSITION

## Architecture

**INCONCLUSIVE**

RC0 does not justify merging old v2, building “CAL v2,” promoting a staged pipeline, or promoting the additive receipt hypothesis.

The direct evidence does justify retaining a narrower project belief:

> CAL needs explicit reconstruction of measurement, participation, missing/performed assessment state, execution state, and causal basis wherever those distinctions materially affect interpretation. The software factoring required to achieve that remains unresolved.

## Research-governance disposition

**INCONCLUSIVE**

No production promotion is authorized from RC0.

---

# NON-CLAIMS

RC0 does not establish:

- that current CAL verdicts are semantically correct;
- that v0.5.0 thresholds or the NLI model should change;
- that current production architecture is inadequate as a whole;
- that old v2 is the right or wrong architecture as a whole;
- that an additive receipt is sufficient;
- that five stages are necessary;
- that trust level should be ignored;
- that proposition authority is automatically CAL-owned;
- that multi-passage aggregation semantics should be added;
- that Contract C 1.0.0 should change;
- that a new CAL release is justified;
- that any research branch should merge.

---

# Required adversarial questions

## 1. What else could explain current abstention behavior besides pipeline structure?

Policy choices, model measurement quality, retrieval-floor admission, aggregation limits, missing proposition-specific context, early-return ordering, and caller-level execution handling can all produce similar terminal symptoms.

## 2. Is the largest problem representation, policy, measurement quality, aggregation, eligibility, control flow, or missing upstream context?

RC0 cannot rank these globally. It directly identifies a **representation/reconstructability gap around final participation** and a **semantic-policy ambiguity around trust versus proposition eligibility**, while leaving measurement and aggregation contributors live.

## 3. Which assumption carries the most weight in the preferred design?

For the additive-receipt hypothesis, the heaviest assumption is that all promotion-relevant final participation/assessment/causal state can be reconstructed faithfully from frozen current measurements, bound inputs, policy identity, and replay without changing the internal decision architecture.

## 4. What would falsify the need for a staged pipeline?

A corrected pre-exposure evaluator in a fresh context showing that a smaller non-staged mechanism reconstructs every required state and survives strong policy/cause interventions while weak controls fail.

That observation was **not validly obtained in RC0** because the evaluator was incomplete.

## 5. Could a smaller explicit state ledger solve the same defects?

Plausibly, yes. RC0 produced a small research adapter demonstrating the shape, but sufficiency remains a live hypothesis pending corrected evaluation.

## 6. Could better semantic measurement solve apparent abstention problems without architecture change?

Some, yes. It cannot by itself represent execution failure, not-performed assessment, policy exclusion, or causal multiplicity, but it could reduce paths currently caused by neutral/misread semantic signals.

## 7. Are candidate states downstream policy concerns rather than CAL epistemic concerns?

Materiality, risk tolerance, routing, and operational authorization remain downstream. Source facts are upstream. Proposition-specific semantic/eligibility/applicability assessments belong to CAL only when CAL or an explicitly named assessor actually performs them. Authority ownership remains partly unresolved.

## 8. Would the candidate still appear better if old v2 had never existed?

The lower-bound need for retained non-deciding evidence and explicit missing/execution state follows from current production traces, Contract C, issue #3, and the product boundary, not from old v2. The specific staged mechanism does not have independent support from RC0.

## 9. Can a deliberately weak implementation pass the evaluator?

The original evaluator had weak controls and was intended to reject them, but the evaluator itself omitted required protocol controls. Therefore weak-control rejection under that apparatus cannot establish full RC0 decision discrimination.

RC0A preregisters additional weak controls for trust-shortcut, causal-echo, and policy-ID-only gaming.

## 10. What remains unknown after the experiment?

The central architecture choice remains unknown. What improved is the precision of the question and the identification of exactly which controls a decisive evaluator must contain.

---

# State ownership classification

| State / concern | RC0 classification | Basis |
|---|---|---|
| Contract-B nomination role | upstream fact retained by CAL | current v1 does not treat nomination as NLI relation |
| Source trust level | upstream fact retained by CAL; may be named policy input | source-profile field copied into CAL input state |
| Claim/passage semantic measurement | CAL-owned | current entailer/rules boundary |
| Proposition eligibility assessment | CAL-owned only when explicitly evaluated, otherwise not-performed/unknown | issue #3 + product boundary + Contract C state model |
| Semantic-validity assessment | CAL-owned when explicitly evaluated | current rules include semantic-validity-like checks; Contract C slot exists |
| Temporal applicability | CAL/explicit assessor when actually evaluated; ownership case-dependent | Product North Star and Contract C slot |
| Authority/applicability | **unknown ownership / separate experiment** | original RC0 concern; not safely derivable from source class |
| Aperture/completeness | CAL or explicit named assessment where justified | product boundary; cannot be inferred from retrieval count |
| Retained/non-deciding participation | CAL-attributable derived state | current suppression behavior already creates the distinction |
| Exact causal basis | CAL-attributable only when intervention/replay supports it | epistemic record convention + Contract C causal form |
| Epistemic terminal conclusion | CAL-owned | product boundary |
| Materiality/risk/routing/action | downstream Decision Engine policy | product boundary |
| Execution/orchestration authority | MainFrame/Conduit/human as explicitly authorized | outside epistemic conclusion |

---

# Historical v2 idea registry

| Mechanism | RC0 evidence status | Why |
|---|---|---|
| Explicit removals | **SUPPORTED AS A USEFUL REPRESENTATION HYPOTHESIS** | directly addresses current replay/prose dependence for suppressed evidence; not yet promotion-tested |
| Per-role participation | **SUPPORTED AS A USEFUL REPRESENTATION HYPOTHESIS** | matches the fact P1 gates adverse/refuting use rather than all evidence use; actual trust policy remains unvalidated |
| Separate measurement then qualification/policy | **SUPPORTED WITH BOUNDS / partly already current** | current NLI already excludes trust/nomination inputs; old v2 makes later participation more explicit |
| Distinct null causes | **SUPPORTED WITH BOUNDS** | current production already has several; old v2 adds `all_ineligible`/`not_resolvable`, but exact taxonomy is not established |
| Every admitted passage receives every qualification predicate | **HYPOTHESIS** | may improve auditability but necessity was not tested by corrected evaluator |
| Total pipeline / every stage always runs | **FALSIFIED as implemented claim** | old `run_v2` contains early returns |
| Five-stage internal architecture | **INCONCLUSIVE** | first evaluator was invalid for decisive comparison |
| Claim mode declaration/fallback | **INCONCLUSIVE / separate semantic hypothesis** | not required to answer minimum state question |
| Interval algebra | **OUTSIDE RC0 architecture decision** | may address numeric operator defects but is a separate semantic capability |
| Passage unions | **OUTSIDE RC0 architecture decision** | introduces unvalidated aggregation semantics |
| Trust-derived refute ineligibility | **INCONCLUSIVE as policy; not a proposition assessment** | current and old v2 both use source class, but issue #3 leaves semantic legitimacy open |
| Generic assessment execution/value state | **NOT PROVIDED by old v2** | no performed-positive/adverse/unknown/not-performed/not-applicable/failed vocabulary |
| Intervention-derived causal multiplicity | **NOT PROVIDED by old v2 surface** | deciding passages do not distinguish independent vs joint sufficiency |
| Execution failure state | **NOT PROVIDED by old v2 verdict surface** | exceptions have no typed failed proposition result |

---

# NEXT SMALLEST TEST

Execute `CAL Epistemic Methodology RC0A` from `docs/research/brief-04-epistemic-methodology-rc0a-successor.md` in a genuinely fresh context.

The decisive additions are deliberately narrow:

1. complete evidence-presence ladder under a fixed claim;
2. full primary/secondary/background trust mutation;
3. performed-positive eligibility plus adverse/unknown/not-performed/not-applicable/failed;
4. temporal/applicability/authority missing-state controls;
5. actual one-at-a-time candidate replay for causal basis;
6. a strong policy counterfactual that must change the derived result without changing measurement/evidence facts;
7. weak controls for trust-shortcut, causal-basis echoing, and policy-ID-only gaming;
8. exact Contract C 1.0.0 representability check after methodology sufficiency, including performed-positive state.

Do not expose RC0A to old-v2 implementation or RC0 exploratory candidate gate vectors before that corrected evaluator is frozen.

---

# Receipts and deviations

## Research PR

- PR: `https://github.com/camerontjs-dot/claim-audit-lab/pull/28`
- branch: `research/epistemic-methodology-rc0`
- production baseline: `e90f301cf6ca02c0c77b6e88c3b08f8b93b9a36a`
- immutable v0.5.0: `5533bbcf27a3ee3a7d901f7dfc44c241bc558e2c`
- first Phase 1 freeze: `9b28df7298257218ec0c9f33163fb60dde71d2a6`

## Preserved execution/tool deviations

1. Local container `git clone` could not resolve `github.com`; authenticated GitHub connector/API was used for repository inspection/mutation, with hosted Actions as execution receipt.
2. Several earlier hosted workflow runs were superseded/cancelled by subsequent research commits while the apparatus was still being assembled. These cancellations are workflow-history events, not scientific passes or failures.
3. Phase 1 evaluator coverage defect was discovered after candidate exposure. This is the decisive apparatus deviation and is preserved separately rather than repaired.

## Production impact

**None.**

No production semantic file, Contract B, Contract C, Evidence Bundler, Decision Engine, tag, release, threshold, model, or main branch state was changed by RC0.
