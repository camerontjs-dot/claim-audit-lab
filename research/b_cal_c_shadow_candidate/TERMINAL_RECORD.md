# Frozen B -> CAL -> C Shadow Candidate — Terminal Evidence Record

Status: **bounded shadow boundary supported; semantic authority remains the blocker**.

Classification: Draft Research Evidence. No production authorization.

## 1. Exact live and frozen identities

- CAL production base: `53f0885b111676794d1bd20e10b91aa58b07e9d4`
- CAL release: `0.5.0`
- released Contract-C exporter lineage: `a069707e5031cef5b82af02d08b0f1a47ea8752e`
- Contract B 1.2.0 authority: `c314e53bd91c0736aa4370a364673b069aceb43e`
- Contract C 1.0.0 authority: `5fe55f9ed5d0ee9f026ca1b077e9d70ce0487ea1`
- Evidence Bundler production pin: `c8189c31adbab11729c31430c2070126224a2d42`
- RC7F-B1 comparison instrument: `0ecdedc5cea970485a635508255f3670ab231c33`
- RC7F-C event-ordering instrument: `e8d33913db66ad21027dffdf731d50f7a0977c8f`
- RC7F-D permission-composition instrument: `9e1f28c3e4f217561e4364e1560539bdf4870298`
- preserved RC7F-A1 assertion/scope falsifier: `ead5a6b068c17aefea0c2fc6b0b54b78ced26729`

No released CAL `src/` file, Contract B, Contract C, Decision Engine policy, or release state was modified.

## 2. Candidate architecture actually supported

The smallest supported shadow path is:

`validated B 1.2 -> admitted evidence observations -> bounded semantic measurement proposals -> explicit authority boundary -> unresolved internal semantic state -> conservative C 1.0 projection`

The candidate intentionally does **not** implement semantic warrant.

A `CLAIMED` specialist measurement is retained as a proposal with `insufficient_authority`. Instrument agreement, source trust, deterministic execution, or measurement confidence cannot grant authority. Unsupported typed-population and numeric assertion/scope transitions remain `not_executed` rather than being synthesized from raw text.

When no complete warrant is established, Contract C is projected conservatively as completed `not_checkable`, with `semantic_validity=performed/unknown`, no causal basis, and all retained contributions residual.

## 3. Accepted boundary run

Accepted hardened run:

- workflow run: `33639947405`
- candidate head: `8789fd01f916d1160cf022fdf7c54e15b5cd3df5`
- artifact: `9850389507`
- artifact digest: `sha256:917101df1ec1e91c7e0ef3d9070cbb5bcb6665c46e1129d6d1759a6453b87901`

Passed in that run:

- exact frozen dependency checkout and identity verification;
- 14 authority-safety unit tests;
- frozen Contract B validator on every corpus object;
- released CAL B intake on every corpus object;
- real RC7F instrument execution;
- frozen Contract C validator on every shadow export;
- byte-deterministic shadow projection;
- mandatory terminal receipt;
- `pipefail` exit propagation;
- no production `src/` changes relative to frozen CAL production base.

## 4. Contract-B corpus evidence

Five valid B 1.2 cases were exercised.

### Production-path cases

`fresh-b12-absent`

- production Evidence Bundler retrieval path;
- factual-context extension absent;
- 9 selected passages;
- 0 semantic proposals;
- all observed states non-authoritative.

`fresh-b12-present`

- same production-generated B corpus plus promoted factual-context extension;
- one rejected passage preserved;
- aperture outcome explicitly unknown;
- 7 selected passages;
- 0 semantic proposals;
- all observed states non-authoritative.

### Controlled valid-B semantic-family cases

The controlled cases were built from controlled C-A lexical surfaces through the pinned Evidence Bundler fixture writer, then independently accepted by the frozen Contract-B validator. The controlled C-A records assert no semantic truth or CAL warrant.

`controlled-semantic-absent`

- extension absent;
- 5 selected passages;
- 4 positive `CLAIMED` measurements;
- positive families: comparison, event ordering, permission composition;
- every `CLAIMED` measurement remained `insufficient_authority`;
- shadow C remained noncausal and `not_checkable`.

`controlled-semantic-admitted`

- promoted B factual-context extension admitted all five passages;
- 5 selected passages;
- the same 4 positive proposals appeared;
- every proposal remained `insufficient_authority`;
- no strengthening occurred.

`controlled-semantic-rejected`

- promoted B factual-context extension rejected all five passages;
- selected passage count: 0;
- excluded passage count: 5;
- proposal count: 0;
- no rejected evidence leaked into semantic measurement.

The corpus also includes an embedded comparative cue. It remains a non-authoritative measurement state rather than receiving narrator-level authority.

## 5. Released versus shadow divergence

A concrete released-path limitation was reproduced across the fresh and controlled B corpora.

Released CAL can produce an `unclassified` / `not_checkable` assessment while retaining candidate contributions. The released Contract-C exporter then intentionally fails closed with:

`ContractCExportError: unclassified early-return with retained candidates is not promoted`

The shadow successor does not repair that production exporter. It preserves the released failure as evidence, reuses only released observation-construction helpers, removes causal strength, and emits a valid conservative Contract C 1.0 object.

Classification: **likely legacy compression**, not automatically a candidate improvement and not evidence that Contract C itself is defective.

Where released CAL reported `supported`, `partially_supported`, or `needs_source`, the shadow reported `not_checkable` because this experiment had no established semantic warrant. Those divergences are classified **authority unresolved**, not candidate wins.

## 6. Contract C projection audit

Frozen Contract C 1.0 successfully represented the bounded safe projection in every accepted case.

Internal detail lost at the C boundary:

- structured specialist measurement proposals;
- per-instrument authority reason taxonomy.

For this experiment the loss is legitimate because those details are not authorized premises and no downstream-relevant behavioral distinction has been demonstrated.

Contract B review history and aperture observations are not duplicated into C. The exact B object is identity-bound, and CAL does not convert upstream aperture observations into its own completeness conclusion.

Disposition: **no Contract C successor escalation justified**.

## 7. Preserved failed attempts and apparatus findings

Failures were retained rather than rewritten as success.

1. Initial integration run `33636168571` failed after authority tests passed.
2. Run `33636364665` appeared green because shell `tee` masked the Python failure. This evaluator/harness false positive triggered `set -o pipefail` and a mandatory terminal receipt.
3. Hardened run `33636746745` then exposed dynamic frozen-validator loading that failed to register the module in `sys.modules`, preventing Pydantic postponed-annotation resolution. The candidate had not been rejected by Contract C.
4. An apparatus-only registered-module successor produced the first genuinely hardened green boundary run `33638839574`.
5. The stronger controlled-B retrieval attempt `33639510472` exposed a cross-repository producer/validator mismatch: heading-less Markdown caused Evidence Bundler retrieval to emit `section: null`, accepted by Evidence Bundler's own validation but rejected by frozen Apparatus Contract B, which requires a string. No B contract or producer was changed. The failed run remains evidence.
6. The controlled fixture-writer successor used explicit passage sections and produced the accepted run `33639947405`.

The `section: null` mismatch is an apparatus compatibility edge case. It does not justify changing frozen B inside this programme.

## 8. Epistemic distinctions demonstrated versus unavailable

Demonstrated in this bounded integration programme:

- valid B intake;
- extension absent;
- admitted evidence selection;
- rejected/excluded evidence selection;
- no admitted semantic evidence after all-rejected history;
- explicit aperture outcome unknown;
- positive semantic measurement proposal;
- semantic relation unresolved;
- operator inapplicable;
- insufficient semantic authority;
- bounded operators deliberately not executed;
- execution failure preserved separately in authority-safety tests;
- valid conservative C projection.

Not legitimately established from the frozen real-B authority in this programme:

- proposition-level semantic support/refutation truth;
- a semantic-neutral truth label;
- source-established semantic unknown as proposition authority;
- authorized text extraction/interpretation;
- authorized typed-population mapping from raw text;
- authorized numeric assertion/scope mapping from raw text;
- authorized multi-passage composition;
- CAL aperture-completeness conclusion.

These states were not fabricated to inflate coverage.

## 9. Authority interface required from the parallel track

PR #74 (`Draft Research: Semantic Authority Machinery RC8`) is the live parallel authority track.

Its frozen RC8 candidate at `61d605902cd79ddfd9f6da4e3f1e93173a8d4257` passed a prospective 68-case held-out authority suite at PR head `77ecd0bba476f5606be31db471648f053d86ea65`, with:

- `unsafe_warranted_atoms = 0`;
- `status_exact_count = 68 / 68`;
- `reason_exact_count = 68 / 68`;
- `authority_monotonicity_violations = 0`;
- warranted precision and recall both `1.0` on that synthetic typed cohort.

That result is not sufficient for this integration to accept RC8 as a real-text warrant provider. RC8A was immediately preregistered because the frozen RC8 subreceipts are not bound to the same evidence/proposal authority subject and field-warrant spans are not validated against operator governance.

Therefore a future integration receipt must bind, at minimum:

1. proposition/claim identity;
2. exact evidence passage identity;
3. semantic family and normalized proposal/atom identity;
4. authority source/issuer identity;
5. operator jurisdiction/applicability result;
6. every material assertion/operator/field/composition/aperture subreceipt to the same authority subject/proposal;
7. every material field-support span to the operator-governed source region;
8. explicit terminal authority state and typed reason;
9. execution state orthogonally to epistemic authority.

The integration track must not define the verification semantics for an `established` / `WARRANTED` receipt. That remains authority-track ownership.

## 10. Contract consequences

### Contract B

No change justified.

B provides enough evidence identity, candidate/review history, admitted/rejected selection, factual context, and aperture observation for the bounded shadow runtime. It does not and should not be treated as supplying proposition-level semantic warrant.

The retrieval `section: null` producer/validator mismatch should remain an apparatus finding unless independently reproduced and assigned to the relevant producer/contract maintenance programme.

### Contract C

No change justified.

C 1.0 can safely carry this candidate's conservative noncausal `not_checkable` projection. Rich authority receipts remain CAL-internal until a concrete downstream behavioral distinction proves that C needs a successor field.

## 11. Terminal disposition

**`SHADOW_BOUNDARY_OPERABLE_FAIL_CLOSED_ON_VALID_B_WITH_POSITIVE_PROPOSALS; SEMANTIC_AUTHORITY_SUBJECT_BINDING_REMAINS_BLOCKER`**

The B -> CAL -> C integration architecture is supported as a shadow boundary.

The experiment does **not** establish that any real-text semantic proposal may strengthen an epistemic conclusion. The next discriminating dependency is RC8A or a successor authority-subject binding experiment owned by the parallel authority track.

Production promotion: **NO**.

Keep this PR Draft. Do not merge for tidiness.
