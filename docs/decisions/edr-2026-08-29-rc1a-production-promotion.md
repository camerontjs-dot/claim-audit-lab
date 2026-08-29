# EDR — RC1A production-promotion decision

Date: 2026-08-29

Status: **DEFER PRODUCTION IMPLEMENTATION; PRESERVE BOUNDED DESIGN**

This is a production-promotion decision record. It consumes prior research evidence but does not merge the research candidate or authorize unrelated semantic changes.

## Question

What is the smallest production change, if any, justified by CAL RC0B + RC1A?

## Authorities inspected

- production base: `e90f301cf6ca02c0c77b6e88c3b08f8b93b9a36a`
- RC1A terminal research record: CAL PR #33
- RC1A evaluator freeze: `9b0d03a830367dc527c94663187e51cebe56cd16`
- RC1A candidate/scientific execution: `5133264a44b1ef395542b286f298188ec6bbe96a`
- RC1A candidate blob: `782f4f7cf5635672b55fcb3e292db584ce5ba464`
- RC1A final result commit: `d64e4707a1b050bfa3cf7c435e4b17d2d05e9a1b`
- RC1A scientific workflow: `33270560829` — SUCCESS
- public production suite on RC1A candidate: `33270560858` — SUCCESS
- current production `src/claim_audit_lab/v1/pipeline.py` blob: `dd67d0d35590d3052826ad697ce9fd11222fff6f`
- current production `src/claim_audit_lab/v1/runner.py` blob: `db53f49745876b6158da0c233fb80916bbeaabaf`

## Observed evidence

RC1A established that a thin execution-facing wrapper can:

1. invoke unchanged current `run_audit`;
2. return the exact `AuditTrace` object produced by that execution;
3. preserve semantic-measurement, verdict, and full-trace identity on the frozen success cases;
4. distinguish wrapper failure before `run_audit`, `run_audit` failure, assessment failure, performed-positive/adverse/unknown, not-performed, and not-applicable;
5. record deciding/residual/excluded/unresolved participation under the frozen research policies;
6. keep aggregation unresolved rather than invent composition;
7. emit causal necessity only after an actual removal replay.

The research candidate changed no protected production semantic object.

RC1A also explicitly left unknown:

- production API ownership and ergonomics;
- persistence and operational observability;
- substantive correctness and ownership of a real assessor;
- downstream compatibility/need for the research receipt;
- future policies and richer aggregation/causal semantics.

The candidate itself exposes research-only choices including `assessment_plan`, an injected `assessor`, two frozen research policy IDs, optional aggregation mode, replay IDs, and a failure injector. RC1A established that this packaging can satisfy the frozen experiment. It did not establish that these are the correct public production API or policy semantics.

## Existing-consumer audit

Before finalizing this decision, the current downstream/operator surfaces were inspected rather than assuming no consumer existed.

### Decision Engine

Decision Engine PR #10 independently consumed frozen Contract C 1.0.0 without CAL internals and passed distinctions for:

- `not_performed`;
- performed-unknown;
- performed-adverse;
- not-applicable;
- failed/incomplete execution distinct from completed `not_checkable`;
- single-necessary, independent-alternative, jointly-sufficient, and residual-non-deciding causal/participation representations;
- residual-state preservation;
- aggregate measurement-basis preservation;
- fail-closed missing/malformed state and unknown-field rejection.

That evidence shows the existing downstream contract already carries the tested consumer distinctions that Decision Engine actually exercised. It does not establish a present need for the RC1A research receipt or for widening Contract C.

The one RC1A assessment state not explicitly demonstrated by that clean-consumer record, generic performed-positive, has no observed current Decision Engine rule or gate that requires it. Absence from the conformance list is therefore not itself a consumer requirement.

### CAL report/UI surfaces

Current CAL report and operator-reason surfaces consume the existing structured report / `AuditTrace` verdict, recorded reasons, rules fired, evidence links, and support measurements. They do not presently request RC1A assessment-plan state, participation state, policy-effect receipts, aggregation receipt state, or replay-derived causal basis.

The operator reason layer is deliberately verdict-reading rather than a second decision procedure, which is compatible with leaving RC1A state outside the current production trace until a concrete surface needs it.

### Consumer-audit conclusion

No current production consumer inspected in this decision falsifies the sufficiency of the existing production surfaces.

Therefore the reopen condition remains unmet: there is still no observed consumer that needs RC1A-only state beyond current `AuditTrace` / Contract C behavior.

## Alternatives considered

### A. Merge or mechanically transplant the RC1A candidate

**Rejected.**

This would promote experimental assessor/policy/aggregation/replay knobs whose production ownership and consumer need were not established. Passing the research apparatus is evidence that the mechanism is sufficient, not evidence that every research control belongs in the public product surface.

### B. Add a generic production receipt API now

**Deferred.**

A smaller generic wrapper could be designed, but there is currently no observed production consumer requirement that discriminates the required receipt schema, persistence boundary, assessor ownership, or public/private API placement. Designing those now would convert unknowns into interface commitments.

### C. Modify `run_audit` / `AuditTrace` directly

**Rejected.**

RC1A specifically showed that the required state can be captured without changing current v1 semantics or trace. No evidence justifies widening the core semantic object.

### D. Make no production code change now, retain RC1A as the proven implementation pattern, and require a concrete consumer before freezing a production surface

**Selected.**

This is the smallest change justified by the evidence: no speculative runtime/API change.

## Decision

**Do not promote RC1A candidate code into production at this time.**

Preserve these supported constraints for the first concrete consumer-driven implementation:

- additive wrapper/service around unchanged `run_audit`;
- exact trace identity on successful execution;
- explicit fail-closed execution state when no normal trace exists;
- no fabricated epistemic conclusion on failed execution;
- no silent default for missing assessment state;
- assessment state distinct from source trust;
- participation/policy effects explicit rather than inferred from terminal reason;
- aggregation remains unresolved unless separately authorized composition exists;
- causal necessity requires an actual intervention/replay;
- Contract B, Contract C 1.0.0, models, thresholds, rules, and existing v1 trace semantics remain unchanged unless separately justified.

The next production implementation should begin only when a concrete consumer/use case identifies the minimum subset of this receipt it actually needs. That task must freeze the consumer requirement before choosing the public API/schema.

## Falsifier / reopen condition

Reopen this decision when at least one concrete production consumer demonstrates a need that cannot be met from the existing `AuditTrace` alone and specifies which of the RC1A-observed states it consumes.

A smaller discriminating test should then compare:

1. a private/additive execution receipt wrapper;
2. any proposed public trace/schema extension;

against that exact consumer need. Prefer the private/additive option unless the consumer falsifies its sufficiency.

## Non-authorization

This decision does not authorize:

- CAL v2;
- historical-v2 promotion;
- Contract B or Contract C changes;
- new assessor semantics;
- new policy semantics;
- new aggregation/composition semantics;
- Evidence Bundler or Decision Engine changes;
- model, threshold, rules, or configuration changes;
- release/version changes.

## Disposition

**SUPPORTED DESIGN, PRODUCTION CHANGE DEFERRED**

RC1A's bounded wrapper architecture remains supported. The smallest currently justified production code change is **none** because production API/consumer requirements remain unobserved.
