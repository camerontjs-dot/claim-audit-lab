# RC0B Corrected Evaluator Specification

Status: PRE-FREEZE PREREGISTRATION

This evaluator scores behavior, not architectural resemblance.

## Required properties

A. State distinguishability.
B. Measurement-policy separation.
C. Evidence retention.
D. Participation state: retained, deciding, residual/non-deciding, excluded, unresolved.
E. Assessment execution: performed-positive, performed-adverse, performed-unknown, not-performed, not-applicable, failed.
F. Execution state distinct from epistemic state.
G. Exact causal basis only when supported by one-at-a-time removal replay; otherwise unavailable.
H. Strong policy counterfactual with identical evidence facts and semantic measurements, changed policy, and changed participation/conclusion.
I. Upstream nomination-role invariance.
J. Trust/source fact distinct from proposition-specific assessment state.
K. Aggregation honesty: retain partial evidence and allow unresolved aggregation when no validated composition semantics exist.

## Mandatory controls

Evidence presence ladder: zero passages; available but none admitted; admitted semantic-silent; admitted weak below signal; supportive; contradictory; mixed.

Nomination mutation: hold claim, passage identity/text, and semantic measurement fixed while changing only support/counter nomination metadata. Semantic measurement must remain invariant.

Trust mutation: hold claim, passage, and semantic measurement fixed across primary, secondary, background. Record source fact, assessment state, policy participation effect, terminal result separately.

Eligibility ladder: performed-positive, performed-adverse, performed-unknown, not-performed, not-applicable where legitimate, failed. No positive state may be inferred from trust or absence of rejection.

Temporal ladder: not-performed, performed-unknown, performed-adverse, not-applicable.

Authority/applicability: not-performed and performed-unknown. No positive authority judgment may be invented.

Distributed evidence: retain two partial relevant passages for which no validated composition rule is supplied; aggregation must remain unresolved.

Execution controls: completed+assessed; completed+not-checkable; assessment failure; incomplete execution; parser/rule/model failure.

Causal replay: if a candidate claims exact decision basis, remove evidence items one at a time and rerun. Derive necessary contributor, independently sufficient alternatives, joint/co-sufficiency, redundant contribution, or unavailable.

Strong policy counterfactual: evidence identity, facts, and semantic measurements remain identical. Policy ALLOW_PRIMARY_OR_SECONDARY permits primary+secondary participation; policy PRIMARY_ONLY permits only primary. A fixed secondary-source adverse measurement must change participation and, absent another deciding item, terminal conclusion.

## Weak controls

W1 one generic abstention state.
W2 richer terminal reasons but no typed participation/assessment state.
W3 primary=eligible and secondary/background=adverse without performed proposition-specific assessment.
W4 declares causal necessity/sufficiency without removal replay.
W5 changes only policy_id while strong-counterfactual derived behavior remains unchanged.

## Gate

Each A-K is PASS/FAIL/N-A with evidence. E, G, H, I cannot be N-A. Architecture-relevant clearance requires PASS on A-K except legitimate fixture-level N-A.

Every weak control must fail at least one of A, D, E, G, H, I, J, K for its preregistered defect. If any weak control clears the same architecture-relevant gate, RC0B is INCONCLUSIVE.

## Falsifiers

- nomination-only mutation changes semantic measurement;
- failed/not-performed becomes performed-positive or performed-unknown;
- trust is treated as a performed proposition assessment;
- execution failure is represented only as semantic insufficiency;
- suppressed evidence disappears from retained evidence;
- participation requires post-hoc guessing;
- exact causal basis is asserted without replay;
- strong policy counterfactual changes only policy_id;
- distributed partial evidence is combined by an unsupported rule;
- a weak control clears the architecture gate.

## Disposition

Firewall failure before freeze: FALSIFIED.
Material evaluator defect discovered after candidate exposure, or weak-control leakage: INCONCLUSIVE.
Current production state passes all frozen properties: CURRENT ARCHITECTURE SUFFICIENT.
Bounded additive/replay state passes without changing production semantic logic: MINIMAL STATE/POLICY CHANGE SUPPORTED.
Only partial execution-time decomposition passes because required state is otherwise destroyed/unobserved: PARTIAL STAGED DECOMPOSITION SUPPORTED.
Only fuller staging passes: STAGED PIPELINE SUPPORTED WITH BOUNDS.
Another uniquely sufficient mechanism: ALTERNATIVE ARCHITECTURE SUPPORTED WITH BOUNDS.
Otherwise: INCONCLUSIVE.

Model quality, threshold calibration, retrieval, parsing, source-policy semantics, missing upstream information, and stale policy are controlled as alternative explanations and do not count as architecture evidence.
