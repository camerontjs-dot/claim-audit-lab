# CAL Epistemic Methodology RC0A — Corrected isolation successor

## Why this successor exists

RC0's first frozen evaluator was discovered post-exposure to have omitted several controls explicitly required by the original protocol. See `deviation-03-rc0-phase1-evaluator-coverage.md`.

RC0A is the **next smallest discriminating experiment**. It must execute in a genuinely fresh context. This file is a handoff/preregistration record only; do not execute RC0A in the contaminated RC0 context that created it.

## Decision

Determine whether CAL requires more than its current trace/result semantics to preserve:

- materially distinct non-decision causes;
- fail-closed proposition-specific assessment state;
- retained versus deciding evidence participation;
- causal multiplicity;
- execution failure versus epistemic non-decision;
- policy counterfactuals without rewriting semantic measurement.

Then determine whether a minimal additive state/receipt mechanism is behaviorally sufficient or whether some stronger internal decomposition is necessary.

## Authority and baseline

At RC0 termination, live identities were:

- CAL production `main`: `e90f301cf6ca02c0c77b6e88c3b08f8b93b9a36a`
- immutable CAL v0.5.0 release: `5533bbcf27a3ee3a7d901f7dfc44c241bc558e2c`
- immutable Contract C 1.0.0: `5fe55f9ed5d0ee9f026ca1b077e9d70ce0487ea1`
- historical v2 branch: `b7254e713feb5556a81fb0c5b39649c415a949c6`

A fresh RC0A execution must re-verify live GitHub state rather than trust these mutable pointers.

## Isolation rule

Before inspecting old-v2 implementation or RC0 exploratory candidate adapters, RC0A must freeze its corrected evaluator.

Allowed pre-freeze inputs:

- original RC0 task protocol;
- durable CAL Pipeline governance;
- current/released production CAL and tests/traces;
- released Contract B/C artifacts;
- CAL issue #3;
- RC0's direct production-path observations;
- RC0 apparatus deviation record.

Forbidden pre-freeze inputs:

- `src/claim_audit_lab/v1/impl/pipeline_rules.py` from old v2;
- `tests/research/rc0_candidate_adapters.py`;
- `tests/research/test_epistemic_methodology_rc0_candidates.py`;
- any RC0 candidate gate vector or preferred-architecture conclusion.

## Corrected mandatory controls

### 1. Evidence-presence ladder under one fixed claim

Freeze a single claim and vary only evidence state:

1. zero passages available;
2. passages available but none admitted;
3. admitted irrelevant/semantic-silent passage;
4. admitted weakly related passage below decision signal;
5. clearly supportive passage;
6. clearly contradictory passage;
7. mixed support/refutation.

The evaluator must distinguish only the causes that are materially needed; it must not predeclare a new enum per row.

### 2. Upstream nomination-role mutation

Hold exact passage identity/text and semantic measurement fixed. Mutate support/counterevidence nomination metadata only. Measurement must remain invariant unless the released contract explicitly makes the field semantic.

### 3. Full trust metadata mutation

Hold claim, passage, and semantic measurement fixed. Exercise exactly:

- primary;
- secondary;
- background.

Record separately:

- source fact;
- proposition-specific assessment execution/value;
- participation/policy effect;
- terminal conclusion.

A source-class policy may read trust, but it may not masquerade as a performed proposition-specific eligibility assessment.

### 4. Eligibility state ladder

Hold semantic evidence fixed. Exercise:

- performed-positive;
- performed-adverse;
- performed-unknown;
- not-performed;
- not-applicable where legitimate;
- failed assessment execution.

Do not infer performed-positive from `trust_level=primary` or from absence of an adverse result.

### 5. Applicability, temporal, and authority unknowns

Use controlled records that keep semantic support fixed while varying only named assessment state.

At minimum test:

- temporal applicability not-performed versus performed-unknown versus performed-adverse versus not-applicable;
- proposition authority/applicability not-performed versus performed-unknown where a legitimate assessor is absent.

Do not invent a positive authority judgment. The experiment may conclude that authority belongs outside CAL or requires a separate owner. The requirement is to preserve missing/unknown state without laundering it into permission.

### 6. Actual causal removal replay

For retained contributions, the evaluator must invoke the candidate under one-at-a-time removal interventions where the candidate claims an exact causal basis.

Derive, rather than accept by declaration:

- necessary contributor;
- independently sufficient alternatives;
- jointly/co-sufficient contributors;
- redundant/non-deciding contributors;
- unavailable/not-testable causal structure.

If the candidate cannot replay the outcome from frozen state, it may report causal structure unavailable. It may not invent a winner.

### 7. Multi-passage unresolved control

Include a distributed-evidence case where current rules lack validated composition semantics. A candidate passes by retaining the partial contributions and explicit unresolved aggregation state. It must not pass merely by inventing a new aggregation rule.

### 8. Execution/early-return controls

Distinguish:

- completed not-checkable;
- proposition assessment failure;
- incomplete execution;
- parser/rule/model failure where applicable.

A failure may not be relabeled as subject-matter abstention.

### 9. Strong policy counterfactual

Freeze semantic measurements, input evidence identity, and source facts. Apply two named downstream/eligibility policies that are intentionally defined to produce different participation or terminal outcomes.

Required invariant:

- measurement/evidence facts remain byte-identical;
- policy identity changes;
- derived participation/conclusion changes in the preregistered direction.

This is stronger than merely recording two different policy IDs.

## Corrected weak controls

At minimum preregister and require rejection of:

1. one generic abstention state;
2. richer terminal-reason taxonomy with no participation/assessment ledger;
3. a trust-shortcut methodology that maps `primary -> eligible/positive` and `secondary/background -> adverse` without a performed proposition-specific assessment;
4. a causal-basis echoer that outputs a basis label but does not survive the removal intervention;
5. a policy-recording control that changes `policy_id` while leaving the derived result unchanged in the strong counterfactual case.

If a sophisticated candidate and any of these plausible weak systems both clear the architecture-relevant gate, disposition is `INCONCLUSIVE`.

## Candidate construction rule

Only after evaluator freeze, choose the smallest credible set. Do not force a current-versus-v2 binary.

Expected *classes* to consider, without importing RC0 expected results:

- current production observable surface;
- current semantics plus bounded explicit state/receipt;
- historical staged mechanisms decomposed into individual ideas;
- another smaller/differently factored method if the corrected failures suggest one;
- at least one weak control.

Do not treat this list as expected winners.

## Contract C compatibility test

After methodology sufficiency is established, map the minimum required state to released Contract C 1.0.0 exactly.

Classify each required item as:

- already representable without semantic loss;
- representable only by producer convention/replay, not explicit schema state;
- not representable in 1.0.0;
- ownership unresolved.

Specially test performed-positive assessment state and any authority/applicability state. Contract C must not be changed in RC0A.

## Stop / disposition

Stop when:

- corrected evaluator discriminates the smallest candidate set;
- a preregistered weak control clears the same gate;
- another evaluator defect is found;
- the result requires changing frozen fixtures after candidate exposure;
- a new semantic experiment is needed.

Allowed architecture dispositions remain:

- CURRENT ARCHITECTURE SUFFICIENT
- MINIMAL STATE/POLICY CHANGE SUPPORTED
- PARTIAL STAGED DECOMPOSITION SUPPORTED
- STAGED PIPELINE SUPPORTED WITH BOUNDS
- ALTERNATIVE ARCHITECTURE SUPPORTED WITH BOUNDS
- INCONCLUSIVE
- FALSIFIED

No promotion, merge, version, or Contract-C mutation occurs in RC0A.
