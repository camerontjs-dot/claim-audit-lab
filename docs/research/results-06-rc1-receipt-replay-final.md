# CAL Epistemic Methodology RC1 — Bounded Receipt/Replay Production-Facing Experiment

## Terminal disposition

**INCONCLUSIVE**

The experiment was terminated after the production-facing evaluator was frozen and before candidate implementation because the frozen apparatus did not discriminate the stated production-facing question.

This is an apparatus failure, not evidence that the bounded receipt/replay mechanism cannot work.

## Exact identities

Production base established from live `main` before branch creation:

`e90f301cf6ca02c0c77b6e88c3b08f8b93b9a36a`

Research branch:

`research/epistemic-receipt-replay-rc1-20260829`

Predecessor RC0B research head:

`260e6eaf777675835ae1cf5c97f643f9e516d173`

Predecessor RC0B frozen evaluator:

`5d880110e39d0450af346fea91074eebaa2c2f96`

RC1 evaluator freeze commit:

`7accb1d731d1b68cbadd2f62a0835fba8d6e0f1d`

The final research-record SHA is the commit containing this report and is recorded in PR #32 after commit.

## Frozen RC1 apparatus

- acceptance specification blob: `677fbe44e02cd961109fb3c537e8c9b7285f354e`;
- cases/regression manifest blob: `c0a78f5b715539f554072405ae88ab256394aa3d`;
- executable evaluator blob: `504143d819c06492bde1ffe79de1aed11317e4d9`;
- pytest acceptance entry point blob: `371b37f37de8799f57060cbe4353c84548df0bba`.

The regression manifest freezes all 30 existing v1 trace fixtures by Git blob identity.

## Observed evidence

### 1. Live production state

Live `main` was `e90f301cf6ca02c0c77b6e88c3b08f8b93b9a36a` when this experiment created its branch.

Relevant protected production blobs at that base include:

- v1 pipeline: `dd67d0d35590d3052826ad697ce9fd11222fff6f`;
- v1 models: `755e0ef1757055905f3c8b76b7edc5e8ddc1fefd`;
- Contract C implementation: `d6b32a44ef11109fe0ee91efa212d3904badf58c`;
- v1 entailer: `aaf9415e74ec2f04357ecf5346491d92f3e2d0d3`;
- v1 aggregator: `b1f9e2309ae3d024bc609b83cc546acb30be6e9b`;
- v1 rules implementation: `bc388d64a5a53db0d33610ab6ff84bd93a811b46`;
- v1.13.0 rules file: `ac8147f6624164e9081a4ec365cd3920c25df96d`.

No candidate implementation was created and none of these protected files was modified by RC1.

### 2. PR #31 reconciliation

Before RC1 implementation work, predecessor PR #31 was reconciled without altering its architecture result or scientific evidence.

Its architecture finding remains:

`MINIMAL STATE/POLICY CHANGE SUPPORTED`

Its single governance primary disposition is now:

`SUPPORTED FOR PROMOTION`

That promotion means only promotion into this bounded follow-on research experiment. PR #31 remains Draft, closed, and unmerged.

### 3. Evaluator freeze ordering

The RC1 acceptance specification, cases, executable evaluator, and pytest entry point were committed before the candidate path existed.

The freeze record commit is `7accb1d731d1b68cbadd2f62a0835fba8d6e0f1d`.

### 4. Weak-control discrimination

Before candidate implementation, the frozen executable evaluator was self-tested against the intentionally weak implementation.

The weak control was rejected.

Failed gates:

- `assessment_ladder`;
- `participation_reconstruction`;
- `policy_counterfactual`;
- `replay_derived_causal_basis`;
- `missing_required_state_fails_closed`.

This confirms that the frozen evaluator rejects several known epistemic shortcuts.

### 5. Post-freeze apparatus defect

After freeze, before candidate implementation, the apparatus was checked against the actual RC0B next-step claim.

RC0B did not merely call for proving that a function can serialize already-supplied epistemic state around an already-produced trace. Its smallest next test called for a production-facing producer operating from exact Contract-B input and current v1 execution, with explicit policy identity, assessment receipts, and failure capture while v1 measurements and verdicts remain stable.

The frozen RC1 candidate interface instead accepts:

`emit_receipt(trace, state, replay=None)`

where:

- `trace` is already-produced v1 output; and
- the required execution, assessment, source-fact, policy, and aggregation state is already supplied to the candidate.

Therefore a candidate can clear the gate by preserving and transforming supplied state without demonstrating that a real v1 producer can observe or capture that state at the required execution boundary.

The strongest example is outer execution failure: an already-produced successful `AuditTrace` cannot demonstrate capture of a failure that prevented trace production. The frozen gate tests representational separation by supplying a failure record, but not production-facing failure capture.

Likewise, the gate does not start from Contract-B input or invoke current v1 `run_audit`; it therefore cannot establish that the receipt is emitted by a real v1 execution while production measurements and verdicts remain unchanged.

This is a decisive under-specification relative to the experiment objective.

## Production verdict / semantic-measurement invariance receipts

**NOT DECISIVELY TESTED FOR A CANDIDATE.**

The frozen regression manifest contains all 30 existing v1 traces and the evaluator is designed to compare their semantic-measurement and verdict hashes while requiring the trace to remain unchanged.

However, no candidate was run because the apparatus defect was discovered first.

Observed repository-level protection still holds: RC1 added research apparatus only and did not modify production v1 semantics, verdict logic, Contract B, Contract C, model/config/threshold/rules, Evidence Bundler, Decision Engine, or release surfaces.

That repository diff is not a substitute for the requested candidate invariance experiment.

## Weak-control result

**FAIL, as intended.**

The weak control failed five gates for the intended epistemic reasons listed above.

This validates some evaluator discrimination, but it does not repair the missing production-execution boundary.

## Candidate result

**NOT RUN.**

A candidate result from this frozen gate would be non-discriminating for the primary research question. Implementing a candidate after identifying that defect would risk recording a false positive.

No broader staged candidate was built.

## Deviations / failures

### D1 — local network execution limitation

The execution container could not resolve `github.com` for direct `git clone`.

Live repository authority was therefore obtained through the authenticated GitHub connector, and exact Git object identities were recorded there.

This did not cause the terminal scientific disposition.

### D2 — frozen apparatus under-specifies the production-facing boundary

This is the decisive deviation.

The frozen evaluator tests a receipt transformer over an already-produced v1 trace and already-supplied state. It does not test state capture from exact Contract-B input through real v1 execution, especially failure paths where no normal trace exists.

Because the defect was identified after freeze, the evaluator was not repaired in place and no decisive candidate run was performed.

## Inference

RC0B's representational result remains intact: a bounded typed receipt/replay state may still be sufficient and no fuller staged pipeline is justified by this RC1 run.

RC1 provides no evidence for or against the stronger claim that the required state can be captured at the real v1 production-facing execution boundary without changing existing measurements or verdicts.

The fact that a post-hoc sidecar could likely satisfy the frozen representation gate is insufficient evidence for that stronger claim.

## Hypotheses still live

1. A thin research-only wrapper around current Contract-B intake and `run_audit` can capture the RC0B minimum state while returning the exact existing `AuditTrace` unchanged.
2. Assessment receipts can be supplied/captured at that wrapper boundary without changing semantic measurement behavior.
3. Outer execution failure can be represented by a wrapper-level receipt without conflating it with a successful epistemic `not_checkable` result.
4. Policy participation and causal replay can remain additive and research-side.
5. Generic `performed-positive` can remain internal to CAL for this experiment; Contract C 1.0.0 still need not change unless an independent downstream handoff proves otherwise.

## Unknowns

- Whether every required assessment state is actually observable at the real v1 execution boundary.
- Whether failure capture requires any hook below a thin outer wrapper.
- Whether exact Contract-B input plus existing v1 regression fixtures can be paired without constructing new semantics-bearing fixtures.
- Whether a downstream consumer truly needs generic `performed-positive` across Contract C.
- Whether routine causal replay is operationally cheap enough for broader use.

## Falsified alternatives

The RC1 weak control again falsifies, within this apparatus:

- substituting source trust for explicit proposition/eligibility assessment state;
- defaulting missing required receipt state;
- declaring exact causal necessity without intervention/replay.

This RC1 run does **not** falsify:

- the bounded receipt/replay mechanism;
- current v1 semantics;
- the possibility of a thin production-facing wrapper;
- the need or non-need for stronger decomposition.

## Exactly one research disposition

**INCONCLUSIVE**

Reason: frozen apparatus defect prevents a discriminating test of the stated production-facing question.

## Smallest next evidence-producing step

Run a corrected RC1A experiment from the same live production semantics with a pre-candidate harness that requires an actual research wrapper to:

1. accept exact Contract-B-shaped input or a frozen existing Contract-B fixture;
2. invoke the unchanged current v1 `run_audit` path for successful executions;
3. compare the exact returned v1 trace, semantic-measurement hashes, and verdict hashes against the direct-v1 baseline;
4. capture wrapper/assessment failure when `run_audit` or an owned assessment fails before a normal trace exists;
5. preserve the six assessment states and four participation states without deriving assessment from trust;
6. run the same fixed policy counterfactual, unresolved aggregation, metadata-invariance, fail-closed, and replay-causality checks;
7. include the same intentionally weak control.

No staged architecture is justified before that smaller corrected discriminator is run.

## Production non-authorization

RC1 does not authorize:

- production CAL changes;
- merging PR #32;
- CAL v2 or historical-v2 promotion;
- Contract B or Contract C changes;
- Evidence Bundler changes;
- Decision Engine changes;
- model, threshold, configuration, or rule changes;
- release/version changes;
- new aggregation/composition semantics.

A later separate experiment and promotion decision would be required before any production authorization.
