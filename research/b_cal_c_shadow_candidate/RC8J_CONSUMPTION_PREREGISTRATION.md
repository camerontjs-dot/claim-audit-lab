# RC8J Authority Consumption Seam — Preregistration

Status: **Draft Research Infrastructure / stacked successor to PR #75**.

This experiment does not modify the frozen PR #75 shadow candidate, production CAL semantics, Contract B, Contract C, Decision Engine policy, or release state.

## Scientific question

Can the terminal B -> CAL -> C shadow boundary from PR #75 consume the exact frozen RC8J typed authority gate as an external research dependency while preserving all of these distinctions?

1. Contract B supplies validated source/bundle/passage/claim coordinates, not proposition semantic warrant.
2. Real-text RC7F measurements remain proposal-only when no correctly populated typed authority receipt exists.
3. A deliberately typed seam-control receipt can traverse the external RC8J gate and return its exact `WARRANTED | REJECTED | UNRESOLVED | NO_ASSESSMENT` state/reason.
4. Even a `WARRANTED` typed seam control does not automatically strengthen the released CAL conclusion or create a positive Contract C projection, because that projection rule is separately unestablished.

## Frozen parent

PR #75 terminal head:

- commit: `5d799218f54a97da80713727709563fe91cc9291`
- disposition: `SHADOW_BOUNDARY_OPERABLE_FAIL_CLOSED_ON_VALID_B_WITH_POSITIVE_PROPOSALS; SEMANTIC_AUTHORITY_SUBJECT_BINDING_REMAINS_BLOCKER`

The parent files are evidence and must remain byte-unchanged in this successor.

## Frozen external authority dependency

Strongest authority-track research candidate:

- candidate freeze commit: `8e75c6782bb95c3763d06230b9c5df2b6af44054`
- RC8J path: `research/semantic_authority_machinery_rc8/authority_contract_rc8j.py`
- RC8J blob: `f55156e43e0c1b4a7868bc8339585b8892edda38`
- RC8H parent blob: `4b872e455d52d7a682bb719889860d2cac7909a7`
- RC8F parent blob: `efc50481be3179332cecb449c3c9c91da7c3dfaa`
- RC8D parent blob: `f04f2dc529d3f1a7666d39a3bf9c8a9df87842d1`
- RC8B parent blob: `edf84bb5aae0dd217e3f780e7a49767440b7c1e5`
- frozen Contract B authority: `c314e53bd91c0736aa4370a364673b069aceb43e`

Authority-track evidence before this integration experiment:

- RC8J exposed qualification: 268/268 exact status, 268/268 exact typed reason, 0 unsafe warrants;
- RC8J fresh prospective heldout: 28/28 exact status, 28/28 exact typed reason, 0 unsafe warrants;
- prospective artifact: `9862475745`;
- prospective digest: `sha256:0f377934b1e4adb8e813fd6d5a7c7d2e679cf37ca882d21979ca5889b98141d0`.

These are research pins only. They do not authorize production adoption.

## Frozen B/C and measurement dependencies

Preserve the PR #75 pins unchanged:

- Contract B 1.2.0: `c314e53bd91c0736aa4370a364673b069aceb43e`;
- Contract C 1.0.0: `5fe55f9ed5d0ee9f026ca1b077e9d70ce0487ea1`;
- Evidence Bundler production pin: `c8189c31adbab11729c31430c2070126224a2d42`;
- comparison instrument: `0ecdedc5cea970485a635508255f3670ab231c33`;
- event-ordering instrument: `e8d33913db66ad21027dffdf731d50f7a0977c8f`;
- permission-composition instrument: `9e1f28c3e4f217561e4364e1560539bdf4870298`.

## Experimental architecture

```text
validated B 1.2
  -> existing PR #75 admitted-evidence selection
  -> existing RC7F bounded measurements
  -> real-text proposal remains unresolved unless an external typed receipt exists
  -> external frozen RC8J evaluator
  -> internal authority state + typed reason
  -> epistemic-use gate remains blocked in this experiment
  -> existing conservative C 1.0 projection remains unchanged
```

The RC8J evaluator is executed from a detached exact checkout. Its implementation is not copied into this branch.

## Controlled seam fixture

One seam-control authority object may be constructed from the already validated `controlled-semantic-admitted` Contract B corpus produced by the PR #75 v5 runner.

The control may reuse only validated Contract B coordinates:

- bundle ID;
- admitted source ID;
- admitted passage ID;
- admitted passage extent;
- referenced claim ID.

Its semantic atom, assertion state, operator applicability, field values and field warrant states are **explicit typed test stipulations**, not facts inferred from the passage text. The receipt must be labelled fixture-only in the integration record.

Therefore a `WARRANTED` result for this control demonstrates only that the integration seam can carry a fully bound typed authority object through RC8J. It does not demonstrate correct natural-language interpretation or proposition truth.

## Directed mutations

Starting from the fully bound seam control, exercise at least:

1. admitted source mismatch -> `REJECTED / AUTHORITY_EVIDENCE_SOURCE_MISMATCH`;
2. Contract B bundle mismatch -> `REJECTED / AUTHORITY_EVIDENCE_BUNDLE_MISMATCH`;
3. admitted passage mismatch -> `REJECTED / AUTHORITY_EVIDENCE_PASSAGE_MISMATCH`;
4. Contract B claim mismatch -> `REJECTED / AUTHORITY_CLAIM_MISMATCH`;
5. target atom mismatch -> `REJECTED / AUTHORITY_ATOM_IDENTITY_MISMATCH`;
6. missing bundle/passage coordinate -> `UNRESOLVED / AUTHORITY_EVIDENCE_SEGMENT_BINDING_UNRESOLVED`;
7. required-field support outside admitted passage while still inside operator governance -> typed rejection;
8. subordinate field authority-subject mismatch -> typed rejection;
9. execution failure -> `NO_ASSESSMENT / EXECUTION_FAILED`;
10. evidence not admitted -> `REJECTED / EVIDENCE_NOT_ADMITTED`.

The exact RC8J reason ordering is part of the test.

## Real-text negative control

Re-run the unchanged PR #75 v5 integration corpus first.

For every real RC7F `CLAIMED` measurement in `controlled-semantic-admitted`:

- no synthetic authority receipt may be generated from the measurement;
- the original PR #75 `insufficient_authority` observation must remain unchanged;
- no real-text observation may become `WARRANTED` merely because RC8J is now available.

## Contract C boundary

Do not add RC8J states or reasons to Contract C 1.0.0.

The existing PR #75 shadow C output must remain byte-deterministic and valid under the frozen C validator. A typed seam-control `WARRANTED` result must remain internal because this experiment does not own a positive internal-authority -> Contract C conformance mapping.

## Hard success criteria

The experiment is supported only if all are true:

- the exact frozen RC8J and parent blobs are verified before execution;
- the unchanged PR #75 authority-safety tests pass;
- the unchanged PR #75 v5 boundary integration passes;
- no frozen PR #75 research file is modified;
- no production `src/` file changes;
- the fully bound typed seam control returns exact `WARRANTED / ALL_REQUIRED_WARRANT_ESTABLISHED`;
- every directed mutation returns the preregistered exact state and typed reason;
- every real-text `CLAIMED` observation remains non-authoritative;
- no typed seam result is used to strengthen the released CAL conclusion;
- no typed seam result is projected as a positive Contract C assessment;
- the frozen Contract C validator continues to pass on the unchanged conservative shadow outputs;
- a machine-readable terminal receipt is produced.

One unexpected `WARRANTED` mutation is a hard failure.

## Non-claims

This experiment cannot establish:

- correctness of text -> receipt population;
- proposition truth;
- canonical atom-ID generation;
- independent recoverability of RC8J;
- production authority;
- Contract C positive projection semantics;
- Decision Engine policy;
- release readiness.

The separate authority programme owns independent reproduction and any further authority-machine repair. This integration successor consumes only the frozen research interface.