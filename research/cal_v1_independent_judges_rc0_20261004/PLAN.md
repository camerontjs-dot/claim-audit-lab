# CAL V1: uniform original-input independent-judge audit pipeline

Status: operator-approved product requirement; research implementation and usefulness unqualified.
Date: 2026-10-04. Programme: CAL #205. First execution gate: CAL #206.

## Product decision

CAL V1 is an audit of the supplied ordinary claim against a defined evidence world. Every valid claim receives the same overall process catalogue. Each process independently reads the original claim and original authorized evidence, evaluates its own applicability and semantic question, and emits a bounded conclusion. The final CAL synthesis compares these sealed conclusions with explicit claim-type, relevance, reliability and dependence-aware weighting.

A prevalidated-target, single-family kernel is a reusable component, not completion of CAL V1. The kernel-only release suggestion in earlier #185 commentary is superseded as a product direction. Historical support and failures retain their original scope.

This is not a promise to decide every claim, implement every conceivable family, or discover universal truth. Fewer abstentions is a hypothesis. Success requires more correct evidence-grounded decisions, not more confident errors. Ordinary claim auditing remains a V1 requirement; it must not be removed to pass a release gate.

## Uniform process, independent inputs

1. Validate and freeze the original claim bytes, complete authorized evidence envelope, provenance references, process catalogue, policy and invocation identity. Admission and source custody remain explicit upstream facts; they are not semantic support.
2. Dispatch every registered process on that same envelope. A process may conclude not applicable, unknown, unsupported or failed, but a single failed parser must not prevent the other processes from inspecting the claim. Invalid input is a distinct early stop, not an epistemic contradiction.
3. Each process makes its own local representation and semantic judgment. It records input availability, actual consumption, transformations, information loss, measurements, warrant/basis, applicability and local conclusion. Mechanical checks need not manufacture a semantic opinion beyond their remit.
4. Seal all first-pass process receipts before exposing any lane to another lane's interpretation or conclusion. Scheduling can be sequential or parallel; independent input authority is the invariant. Each process must be independently inspectable and testable.
5. Reconcile exact proposition, evidence-world, scope and measurement basis. Apply the frozen synthesis policy, including relevance and reliability weights and dependence handling, and preserve disagreement. Produce one audit result with recoverable contribution/exclusion reasons and all receipts.

A typed view is a process-local hypothesis, not a shared replacement for the original. Claim-only interpretation is not silently rewritten to fit evidence. Source-only extraction may be a separate sub-process. Every lossy stage needs its own analysis/receipt and retained original input; a model reading an upstream summary is not an independent original-input judge.

## What originals mean

All lanes have the same immutable authorized evidence world available. Record exact source representations, admitted passages and retained context that are actually available at intake. If full raw source bytes or additional context are unavailable, say so; do not pretend a passage bundle is a complete source archive. Each lane declares what it consumed and why. Truncation, retrieval within the fixed world, chunk selection, normalization, decomposition and summarization are local observable processes. No hidden internet search or silent evidence-world expansion is allowed. A request for additional evidence creates a new explicit world/run.

## Late synthesis and proper weights

Separate process execution state, applicability, semantic scope, warrant and reliability. A process's self-reported confidence is a measurement, not an entitlement to decide. Claim profiling runs as another original-input assessment; it cannot route away other judges. A precommitted policy maps qualified profile/context observations to relevance and required semantic obligations only after first-pass receipts are sealed. Profile disagreement is preserved; test outcome sensitivity under each plausible profile rather than selecting the one that yields a decision.

Weights are meaningful only for comparable claims and qualified observations. Two results about different periods, measures or populations are not two votes about the same proposition. Guards such as scope, negation and binding can disqualify a local conclusion or establish a material unresolved obligation. Required unresolved obligations cannot be averaged away; an unrelated not-applicable process or an optional failed instrument must not veto otherwise sufficient evidence.

Keep support and refutation evidence separately. A material warranted conflict cannot be erased by a weighted majority. Repeated runs, duplicated sources, shared parsers and shared models do not supply independent votes. Identify dependence groups and test clone invariance; a dependency label alone does not prove statistical independence.

The RC0 mechanical suite uses artificial rational weights solely to test these mechanics. It does not select the final synthesis algorithm or calibrated weights. Empirical reliability, relevance mappings, conflict rules and thresholds require development-only qualification and a frozen held-out evaluation. No test-label access, desired-outcome optimization or after-the-fact reweighting.

## Existing evidence and reuse

Control kernel: `64b6c7702696c851057c1cf0b2c105b1c81db543`, tree `62c32ab15489e6c3b20e63efb500c0fa26d0084d`; semantic implementation `caa0048f8f511ec3c4aa1ce713766f2219a04bc1`. Current `main` observed at `32275a239b68af383a56bca843e28cbc1e343976`.

The kernel has immutable contexts, measurement/authority/relation receipts and bounded comparison/event-order behavior worth reusing. Its engine selects a single plugin from a preselected typed proposition. Shadow instruments collect observations without their own deciding path. Those properties do not meet the product decision above.

Historical family roadmap #121 records nine bounded atomic families; #176 records separate quantitative composition; #177 records exact declared-root recomposition; #179 bounds definition/equivalence and existence reuse. These are research results, not proof that all families have source-completion, judges, runtime or pipeline integration.

#193/#202 preserves four real-claim modifier collisions. #203/#204 preserves pressure and independent review of the old kernel, not accuracy on 26 refused public claims. EB #131 records a reported local paired source-digest test through a particular verifier/fixture path, without committed experiment bytes. Do not upgrade this to verified custody for arbitrary resealed Contract B objects or all EB entrypoints. Keep exact-path provenance and public-interface qualification separate.

## Ownership and loss boundaries

CAL owns evidence-relative semantic measurements, eligibility/validity/applicability/aperture judgments, local interpretations and final epistemic synthesis. Upstream Proposition Authoring/Contract A retains authority over supplied roots and declared decomposition. A CAL decomposition judge can assess a diagnostic alternative and compare it with direct root analysis; it cannot rewrite Contract A declarations. Such child analyses get the same catalogue and preserve root bindings, with explicit resource limits rather than infinite recursion.

Contracts B/C remain transport/representation authorities, not weighted judges. Decision Engine retains materiality, risk, effects and operational routing. CAL weighting does not move into Decision. All internal process receipts must remain recoverable, but that does not require dumping every trace into Contract C: test minimum public result obligations with an independent consumer before any contract change.

## Evidence programme and acceptance

| Phase | Work | Required evidence / boundary |
|---|---|---|
| P0 | Inventory families, methods, assessment roles, losses and qualification state | Exact historical source/result links; active vs research vs missing explicitly distinguished; no exhaustive taxonomy claim |
| P1 / #206 | Original-input fan-out, isolated first-pass judgments, late synthesis research vertical | Mechanical tests and seeded weak controls; real lane isolation; semantic vertical; at least one correct scoped case beyond old authoring, plus preserved safe abstentions |
| P2 | Qualify real judges and local representations | Modifier, measure, time, polarity, attribution, unit and binding challenges; necessary losses exposed; learned models and deterministic methods each tested within their domain |
| P3 | Frozen comparative experiment | Routed kernel vs shared-lossy vs uniform original-input; same judges/evidence/budgets where meaningful; separate topology from better representation or better instruments |
| P4 | Empirical synthesis calibration and held-out usefulness | Source-disjoint development/calibration/test splits; claimed applicable domain fixed first; correct-decision yield and false deciding rate, conditional accuracy and abstention causes, profile/dependence sensitivity, cost and uncertainty |
| P5 | Exact integration / pressure / independent review | All receipts recoverable, native producer and independent consumer, actual Contract C/Decision compatibility, artifacts and deterministic fixed-receipt replay, ordinary natural claims, false-support/falsifier stop |

Do not treat a mechanical fan-out pass, a stub judge, or an all-abstain run as P1 semantic success. On exposed RC0 seeds require zero wrong deciding results, all safety cases preserved, and at least one correct scope-preserving gain outside the old grammar. That is a minimal experimental discriminator, not a sufficient product usefulness threshold. Before held-out P4 exposure, freeze a meaningful target-use-case coverage/error gate; do not choose one after seeing scores. #193 and #203 claims are exposed regression material, never relabeled blind gold.

## Authority of this package

Authorized now: plans and research-only P1 implementation/qualification in an isolated worktree. Candidate code belongs in a new research subtree; frozen `src/`, previous experiments, existing workflows, EB/Contracts/Decision and release metadata remain untouched. Do not assign a version, merge, repin consumers or promote. A supported phase authorizes the next bounded evidence-producing question, not automatic CAL V1 readiness.

GitHub preparation supplies the protocol, executable contract tests, semantic seeds, freeze and handoff. The local agent supplies actual candidate implementation, instrument/runtime isolation, retained semantic outputs and comparison receipts. No local experiment has been run merely because this package is published.
