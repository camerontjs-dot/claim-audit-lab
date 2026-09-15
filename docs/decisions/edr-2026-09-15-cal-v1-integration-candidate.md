# EDR: CAL V1 integration-candidate convergence

Date: 2026-09-15

Status: **IMPLEMENTED_AWAITING_LOCAL_QUALIFICATION**

## Decision

Converge the CAL V1 pipeline candidate as a bounded audit machine over the released Contract B 1.2 authority surface:

`Contract B 1.2 -> validated intake ledger -> semantic AuditContext -> family measurement -> source completion -> semantic authority -> proposition-relative relation -> scoreless composition -> native immutable CAL result`.

The canonical pipeline operator surface is a dedicated `claim-audit-v1 run-bundle` command. The previously packaged JSON packet execution remains a compatibility/testing surface and is not the canonical Evidence Bundler handoff.

The V1 deciding semantic families remain exactly:

- `strict_comparison` within the frozen deterministic grammar;
- `direct_event_order` within the frozen one-cue direct narrator-level grammar and positive-event deciding envelope.

All other families fail closed. Assertion/scope is not widened. Permission/exception remains outside deciding V1 authority.

## Effective artifacts

Parent packaged candidate:

- commit `4d1b8909f7e2e52c33cf99632be8565f2685f948`;
- tree `cb51b4e1e20292af2890257e995a8cd199f88a20`;
- profile `cal-v1-production-v1`;
- qualified semantic parent `a902621e8baea3063dddd7f92ba975aade305464`.

Post-RC1 semantic convergence freeze:

- commit `847cc970642bb648dc994b929c2053b5c9d4648c`;
- unchanged RC1 authority blob `3cfcfb8cc3b3a8860e119edfbe22a4d684650a86`;
- unchanged RC1 authority-validation blob `73ee2cc8e26cc3945558f76fa8c0992441177a97`;
- unchanged RC1 measurement blob `aa26d34a94488901d8a838824e0d7a23c6655f4c`;
- successor engine blob `296e59ccf855db9e15064c78b1ebeec01b28873d`;
- successor model blob `4a8ee5ddc66ad5512d675b45215a858eb8fdd7ee`;
- successor relation blob `2330f7acb64ac77ed0d26aebe7f4536062503400`.

Released Contract B authority remains `1.2.0`, promoted at Apparatus commit `c314e53bd91c0736aa4370a364673b069aceb43e`. This EDR does not amend Contract B.

Current Contract C downstream direction is Candidate A RC2 / proposed Contract C 2.0.0. Existing producer-conformance evidence established that its basis-group representation can be materialized from already-produced CAL relation/composition state without introducing a new semantic judgment. This EDR does not promote or modify Contract C.

## Observations

1. The packaged `4d1b8909...` candidate genuinely executes the RC1-derived production semantic core. It does not secretly fall through to the historical retrieve-entail-rules engine.
2. The repository already contained the released B1.2 consumer required by convergence: `load_contract_b_intake()` preserves a complete validated intake/audit view and separately derives the narrower semantic-measurement context required by the B1.2 specification.
3. The packaged operator path bypassed that canonical B1.2 intake and instead required a caller-authored distilled packet.
4. PR #97 established that any negative direct-event polarity is `UNRESOLVED`; the packaged relation implementation had lost that bound and could let matching negative tuples decide.
5. PR #97 also established that any participating `UNRESOLVED` relation forces unresolved abstention; the packaged composer evaluated support/refute before unresolved participation.
6. `IRRELEVANT`-only relation sets and pre-relation measurement failures were unnecessarily collapsed into generic relation-unresolved state.
7. Evidence Bundler Draft PR #79 currently projects its native V1 package into released B1.2, preserves full candidate history, and independently tests the exact CAL B1.2 consumer. Its final local qualification/freeze remains an upstream gate before an exact EB->CAL pipeline receipt can be claimed.
8. Hosted GitHub Actions capacity is currently exhausted for this account. A missing hosted run is an apparatus constraint, not evidence that this successor passed or failed qualification.

## Inference

The smallest evidence-backed successor is not a new semantic engine. It is:

- the qualified RC1 measurement/source-completion/authority machinery;
- restoration of the two already-supported PR #97 fail-closed rules;
- more precise failure localization;
- canonical released B1.2 intake wiring;
- a richer native CAL audit artifact;
- explicit isolation of Contract C as a separate compose-only/versioned materialization layer.

No broader semantic research is required to make this candidate testable.

## Implementation consequences

### Contract B intake

`claim-audit-v1 run-bundle` consumes one exact released B1.2 bundle plus one typed target bound to an exact Contract B claim.

The target must preserve:

- exact `claim_id`;
- `proposition_id == claim_id`;
- exact SHA-256 of Contract B `claim_text`;
- explicit semantic family;
- explicit family fields.

When the B1.2 factual-context extension is present, only passages derived as accepted by the existing B1.2 semantic context enter CAL semantic measurement. The complete validated extension, including rejected and needs-review preparation history, remains preserved in the native intake snapshot.

### Native CAL artifact

A canonical Contract B run emits:

- `input.target.json`;
- `contract_b_intake.snapshot.json`;
- `audit_context.json`;
- `result.json`;
- `report.md`;
- `manifest.json`.

The result receipt explicitly records proposition fields, evidence-world identity, measurement receipts, consumed evidence/spans, authority objects, categorical relations, composition participants/rule, terminal disposition and typed failure localization. Contract C is not emitted inside this semantic execution.

### Failure semantics

The successor preserves distinct state for at least:

- `MEASUREMENT_NOT_APPLICABLE`;
- `MEASUREMENT_MISS`;
- `SOURCE_COMPLETION_FAILED`;
- `SEMANTIC_AUTHORITY_UNRESOLVED`;
- `PROPOSITION_BINDING_FAILED`;
- `COMMON_EVIDENCE_WORLD_MISMATCH`;
- `NO_DECIDING_RELATION`;
- `RELATION_UNRESOLVED`;
- `MIXED_RELATIONS`;
- `UNSUPPORTED_SEMANTIC_FAMILY`.

Invalid Contract B artifacts remain intake failures rather than synthetic semantic conclusions.

## Alternatives considered

### Keep `4d1b8909...` unchanged

Rejected for the integration baseline. It is useful bounded local-smoke evidence, but it bypasses the canonical B1.2 two-view intake and does not preserve two PR #97 semantic bounds.

### Replace RC1 with a fresh semantic engine

Rejected. No evidence supports discarding qualified RC1 authority/source-grounding machinery. The identified defects are narrow and locally repairable.

### Widen assertion/scope so natural smoke claims produce verdicts

Rejected. Existing evidence explicitly falsified deciding assertion/scope machinery. Natural smoke abstention is test-to-learn evidence, not justification for semantic widening.

### Add cryptographic receipt authentication

Deferred. RC1 establishes local content integrity and source grounding, not portable issuer authentication. The present local pipeline does not justify a key-management architecture.

### Put Contract C materialization inside CAL execution

Rejected. It would blur the CAL native system-of-record boundary and risk adding hidden downstream semantic judgment.

## Falsifiers

This candidate must not be treated as qualified if any post-freeze local gate shows:

- a negative direct-event case yields terminal support/refute;
- support/refute survives alongside an unresolved relation;
- exact B1.2 accepted evidence differs from the semantic AuditContext admitted set;
- rejected/needs-review B history is lost from the native intake snapshot;
- target proposition identity/text can be substituted while retaining acceptance;
- an RC1 authority-integrity attack regresses;
- cross-world relation composition is accepted;
- packet or bundle replay is nondeterministic;
- historical CAL verdict machinery affects the new operator result;
- the native receipt cannot be reconstructed without hidden CAL semantic state;
- Contract C projection requires a new semantic/causal judgment;
- strict comparison or direct-event positive controls regress.

A post-freeze hard failure requires a successor candidate. Do not patch this source freeze in place and continue calling it the same qualification subject.

## Compatibility and migration

The existing `claim-audit` command and compatibility packet input remain available. The canonical pipeline boundary is newly exposed through `claim-audit-v1` so the migration is explicit rather than silently changing the historical operator surface.

The source branch still carries inherited distribution metadata `0.6.0`. This is **not** a new release/version authority and no wheel from this branch may be published as the canonical `0.6.0` release. The successor changes semantic and public operator behavior materially enough that any later release requires a separate version-class decision under release governance. No tag, release, merge or publication is authorized by this EDR.

## Residual uncertainty

- The successor has not yet completed the required local full-suite/static/build qualification.
- The exact frozen EB V1 -> B1.2 output is not yet available as a terminal locally qualified upstream object; EB PR #79 is still `IMPLEMENTED_AWAITING_LOCAL_QUALIFICATION`.
- Existing Contract C RC2 producer-conformance evidence was run against exact CAL RC1. Because this successor changes relation/composition behavior and native receipt shape, affected C2 producer conformance must be rerun rather than inherited by assertion.
- Independent native-receipt reconstruction remains a local qualification gate.
- The natural-claim family-typing question remains test-to-learn work after the baseline is runnable.

## Reconsideration trigger

Reopen this decision only if qualification exposes a concrete in-scope defect, realistic pipeline use shows a supported family is inaccessible because of the architecture rather than target typing, or a downstream contract demonstrably requires information absent from the native receipt.

Do not reopen broad NLI, assertion/scope, permission reasoning, claim decomposition, root/all-of composition, temporal transitivity/coreference, learned judging or distributed authentication merely because V1 coverage remains narrow.

## Lineage

`4d1b8909... packaged candidate -> 847cc970... semantic convergence freeze -> promotion/cal-v1-integration-candidate-20260915 integration shell -> local qualification -> exact source freeze / Draft PR evidence record`.
