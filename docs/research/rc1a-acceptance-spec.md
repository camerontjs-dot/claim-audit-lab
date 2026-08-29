# CAL Epistemic Methodology RC1A — Acceptance Specification

Status: **PRE-FREEZE APPARATUS** until a designated evaluator-freeze commit records the exact blobs for this specification, the executable evaluator, the regression manifest, and the acceptance entry point.

## Scientific question

Can a thin research-only wrapper around unchanged current CAL v1 capture the minimum RC0B epistemic state during real execution, including genuine failure paths, while producing exactly the same successful v1 semantic measurements, trace semantics, and verdict as direct `run_audit`?

If one bounded wrapper clears the frozen apparatus, stop. No staged decomposition, CAL v2, historical-v2 comparison, Contract C change, or production promotion belongs to RC1A.

## Live base and protected surface

Exact live `main` observed before branch creation:

`e90f301cf6ca02c0c77b6e88c3b08f8b93b9a36a`

The executable evaluator verifies exact Git object identities for the current v1 runner, pipeline, intake, models, aggregator, entailer, retriever, rules, rules file, Contract C exporter, current v1 end-to-end regression test/stubs, the complete current v1 trace-corpus tree, and the current minimal Contract-B fixture tree.

Any drift is an explicit apparatus failure. RC1A does not modify those objects.

## Chronological isolation

Before evaluator freeze, admitted information is limited to governance, exact current production CAL v1, current Contract-B intake, current public production tests/fixtures, RC0B's durable result, and RC1's terminal apparatus-failure result.

Before freeze, no RC1A candidate, exact-task experimental wrapper, candidate result, or historical-v2 implementation mechanism may be inspected or implemented.

Candidate implementation may begin only after:

1. the designated freeze commit exists;
2. the frozen weak controls have been executed against that commit; and
3. W1-W6 are all rejected for their preregistered defects.

If any weak control clears its forbidden property, terminate RC1A for apparatus defect. If any evaluator defect is discovered after freeze, preserve the evaluator unchanged and terminate RC1A. Repair requires a separately named successor.

## Candidate scientific interface

The smallest allowed candidate is a research-only module at `docs/research/rc1a_candidate.py` with:

`run_captured_audit(request, *, audit_runner, assessment_plan, assessor, policy_id, aggregation_mode, causal_replay_ids, failure_injector, feature_extractor, retriever, entailer, aggregator, rules)`

The primary scientific input is the exact current `AuditRequest` boundary, not a finished trace.

`assessment_plan` contains execution instructions, not completed assessment outcomes:

- `perform`: execute the supplied assessor during this run;
- `not-performed`: explicitly record that assessment was not performed;
- `not-applicable`: explicitly record that assessment does not apply.

For `perform`, the assessor returns `positive`, `adverse`, or `unknown`, or raises. Thus performed state must be observed during the wrapped execution rather than supplied post hoc.

A successful result has exactly `trace` and `receipt`. The successful `trace` must be the exact `AuditTrace` object returned by the supplied observable delegate to unchanged current `claim_audit_lab.v1.pipeline.run_audit`. Merely returning a byte-identical reconstructed trace fails Gate 1.

## Frozen successful execution set

The wrapper-specific normalized-request lane freezes these current-v1 behaviors:

1. supported;
2. partially supported;
3. unsupported;
4. contradicted;
5. not-checkable due to no evidence;
6. not-checkable with evidence but no entailment signal;
7. conflicting evidence;
8. filtered/non-deciding sub-floor evidence;
9. inference-shaped support;
10. exhaustive source-boundary/absence behavior.

These use the exact current `AuditRequest` model at the normalized v1 request boundary, the real current feature extractor, aggregator, and verdict rules, and deterministic retriever/entailer adapters over the same production protocols used by the current end-to-end regression suite. The adapters isolate wrapper transparency from heavyweight model availability; they do not substitute a finished trace.

Gate 13 separately loads the frozen current Contract-B fixture through the actual `load_bundle` plus `bundle_to_requests` path and requires the candidate to accept the exact resulting `AuditRequest` object and pass that same object into unchanged `run_audit`.

The entire current committed v1 trace corpus is frozen by Git tree identity and remains independently exercised by the ordinary public production regression suite on the research PR.

## Frozen invariance surfaces

**Semantic measurement:** canonical sorted compact JSON, with one trailing newline, over every explicit measurement-bearing field currently serialized in `AuditTrace`: `features`, `retrieval`, `entailment`, `support_signal`, and `negation_probe` when present. Direct and wrapped SHA-256 identities are recorded.

**Verdict:** canonical sorted compact JSON of the complete current `Verdict` object must be byte-identical direct versus wrapped.

**Full trace:** exact bytes of `trace.model_dump_json(indent=2) + "\n"` must be identical direct versus wrapped. Gate 1 separately requires object identity with the actual observed `run_audit` return.

These invariants are frozen before candidate behavior is observed.

## Frozen gates

### Gate 1 — real execution identity

Every successful wrapper case must invoke the supplied delegate to unchanged current `run_audit` exactly once for the baseline run. The delegate must receive the exact request object passed into the wrapper, and the wrapper must return the exact `AuditTrace` object returned by that invocation. A precomputed-trace sidecar fails.

### Gate 2 — semantic measurement invariance

Direct and wrapped semantic-measurement bytes must be identical for every frozen successful case.

### Gate 3 — verdict invariance

Direct and wrapped complete verdict bytes must be identical for every frozen successful case.

### Gate 4 — full trace preservation

Direct and wrapped complete serialized trace bytes must be identical for every frozen successful case. The research receipt remains separate.

### Gate 5 — assessment ladder

All six states must remain distinct: `performed-positive`, `performed-adverse`, `performed-unknown`, `not-performed`, `not-applicable`, `failed`.

Performed states require actual assessor invocation. The failed state requires an actual assessor exception. Primary/secondary/background source metadata cannot stand in for an assessor observation.

### Gate 6 — participation reconstruction

A frozen four-item case must reconstruct `deciding`, `residual`, `excluded`, and `unresolved` from explicit assessment state plus named research policy.

### Gate 7 — policy counterfactual

With request, evidence, semantic measurements, and current-v1 trace fixed, switch only between `ALLOW_PRIMARY_OR_SECONDARY` and `PRIMARY_ONLY`.

A secondary performed-positive item must move from `deciding` to `residual`. The receipt must preserve policy identity, relevant policy inputs, and derived effects. Production trace and semantic measurements must remain unchanged.

### Gate 8 — execution failure versus epistemic non-decision

A supplied `failure_injector` raises `RuntimeError("RC1A_INJECTED_WRAPPER_FAILURE")` at the wrapper-owned `pre_run` stage.

Require actual injector invocation, zero `run_audit` calls, no normal trace, execution state `wrapper_failure`, explicit stage/type/message, and null/absent epistemic conclusion. This must remain distinct from successful CAL `not_checkable`, performed-unknown, not-performed, and unresolved aggregation.

### Gate 9 — unresolved distributed evidence

A two-passage case with no authorized composition semantics must retain both passage identities, set aggregation to `unresolved`, and emit no composed result.

### Gate 10 — causal intervention

Without replay, exact causal basis must be unavailable. With replay requested for two passages, baseline plus both one-at-a-time removals must invoke unchanged `run_audit`. Removing the support-bearing passage changes the terminal result and may be marked necessary; removing the irrelevant passage does not change the result and must not be marked necessary.

### Gate 11 — irrelevant metadata invariance

Mutating only irrelevant source metadata while holding semantic content, trust tier, assessment facts, and policy fixed must not change semantic measurements, verdict, assessment result, participation, or causal attribution.

### Gate 12 — fail closed

Missing required assessment-plan state for a passage must raise explicitly. Silent epistemic defaults fail.

### Gate 13 — real input boundary

Load the current frozen Contract-B fixture through the actual current Contract-B loader and `bundle_to_requests`. The candidate must begin from the exact resulting current `AuditRequest` object and pass that exact object into unchanged `run_audit`.

An interface equivalent to `emit_receipt(trace, supplied_state)` fails.

## Frozen weak controls

- **W1, RC1-style post-hoc sidecar:** precomputed trace, no observed `run_audit`. Expected failures: Gates 1 and 13.
- **W2, trust-as-assessment:** source trust substituted for actually executed proposition assessment. Expected failure: Gate 5.
- **W3, terminal-reason-only:** no typed assessment/participation state. Expected failures: Gates 5, 6, 12.
- **W4, causal echoer:** marks retrieved evidence necessary without replay. Expected failure: Gate 10.
- **W5, policy-ID-only logger:** policy name changes but participation/effect does not. Expected failure: Gate 7.
- **W6, silent default:** missing assessment state becomes `not-performed`. Expected failure: Gate 12.

All six must be rejected before candidate implementation.

## Contract C firewall

Contract C 1.0.0 is unchanged and protected by exact current implementation blob identity. Generic `performed-positive` may remain research-side. Any downstream compatibility experiment is separate.

## Stopping rule

If one bounded research-only wrapper clears Gates 1-13 plus all production-invariance comparisons, stop. The architecture result may be no broader than:

`A bounded receipt/capture wrapper is sufficient for the frozen RC1A requirements around current CAL v1.`

Research disposition is separate and must use existing CAL governance vocabulary.

If the bounded candidate fails, identify the exact unobservable/uncapturable state and run only the smallest discriminator needed to distinguish candidate defect from inherent boundary failure.

## Non-authorization

RC1A itself does not authorize production merge, CAL v2, historical-v2 promotion, Contract B changes, Contract C changes, Evidence Bundler changes, Decision Engine changes, model changes, threshold changes, rule/config changes, release/version changes, or new aggregation/composition semantics.
