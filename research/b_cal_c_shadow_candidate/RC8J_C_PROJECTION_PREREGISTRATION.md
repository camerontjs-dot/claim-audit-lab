# RC8J -> Contract C Projection Falsifier — Preregistration

Status: **Draft Research Infrastructure / stacked successor to PR #76**.

This experiment does not change RC8J, production CAL, Contract B, Contract C, Decision Engine policy, or release state.

## Scientific question

After the B -> CAL integration seam can consume a fully bound RC8J `WARRANTED` result, does that authority result by itself justify a stronger Contract C object, or is a separate CAL-internal proposition-conclusion/causal layer still required?

The experiment specifically tests whether a Contract C successor is needed merely to expose positive RC8J authority.

## Frozen parents

Integration parent:

- PR #76 accepted head: `dcddb6a08d2e68052edee7a74b014a2632fdc6cf`;
- accepted seam run: `33672904838`;
- artifact: `9863224746`;
- digest: `sha256:0ad60a1d88998ad3b1492bd4d6c3f7d763a5deee5ed368975b31f3cdcfd8d9a5`;
- typed positive control: `WARRANTED / ALL_REQUIRED_WARRANT_ESTABLISHED`;
- unsafe warranted seam mutations: `0`;
- all four real-text RC7F `CLAIMED` measurements remained `insufficient_authority`;
- no positive Contract C projection was attempted.

Authority dependency:

- RC8J freeze commit: `8e75c6782bb95c3763d06230b9c5df2b6af44054`;
- RC8J blob: `f55156e43e0c1b4a7868bc8339585b8892edda38`.

Contract C authority:

- Contract C 1.0.0 commit: `5fe55f9ed5d0ee9f026ca1b077e9d70ce0487ea1`;
- normative spec blob: `8c15f2e5f4047ccd17e204fb23aee1168781b9d5`;
- canonical positive/assessed fixture blob: `38b2271fc31ffa7683c09a486a8919572fc2f1a4`.

## Frozen Contract C facts under test

Contract C 1.0.0:

1. rejects unknown Contract-C-owned fields;
2. has no generic `performed/positive` assessment-stage value;
3. already represents completed assessed CAL conclusions through `conclusion.reported_verdict`, `terminal_branch`, `causal_form`, `basis_members`, residual contribution classification, and rule roles;
4. already contains valid assessed examples such as `partially_supported` and `unsupported` in its canonical production fixture while generic assessment slots remain `not_performed`;
5. intentionally omits producer-private reasoning/telemetry.

Therefore lack of a generic positive assessment-state token is not, by itself, evidence that Contract C cannot carry a positive CAL conclusion.

## Falsifiers

### F1 — Direct authority-field embedding

Take a valid C 1.0 proposition and add a Contract-C-owned `authority` / RC8J receipt field.

Expected: frozen C validator rejects it because exact 1.0.0 rejects unknown fields.

This tests the tempting but unsupported approach of widening C merely to serialize CAL-internal authority receipts.

### F2 — Invented positive semantic-validity stage

Take a valid C 1.0 proposition and set:

`semantic_validity = {state: performed, value: positive}`.

Expected: frozen C validator rejects it. The frozen vocabulary allows only performed `unknown` or `adverse`.

This tests whether positive authority can simply be jammed into an assessment-stage slot. It cannot.

### F3 — Existing positive-conclusion capacity control

Validate the exact frozen canonical C 1.0 fixture and inspect its completed assessed proposition records.

Expected:

- frozen validator passes;
- at least one assessed proposition carries a non-`not_checkable` CAL conclusion;
- positive/negative CAL conclusion state is therefore representable without a generic performed-positive assessment token.

### F4 — Authority-result insufficiency for conclusion construction

Inspect the accepted #76 RC8J seam positive result.

The external authority gate returns authority status + typed reason. A valid assessed C conclusion additionally requires, at minimum:

- proposition-relative `reported_verdict`;
- terminal branch identity;
- causal form;
- basis members;
- complete residual contribution classification;
- rule-role classification where applicable.

Expected: the RC8J result does not supply those conclusion/causal values and the authority specification does not define them.

The absence is not repaired by treating `WARRANTED` as a verdict. `WARRANTED` means the proposed semantic atom has passed the authority transition; it is not itself a proposition support/refutation/aggregation result.

### F5 — Preserve safe current projection

The unchanged #76 real-text shadow objects must remain valid C 1.0 `not_checkable` results. This experiment does not promote the fixture-only `WARRANTED` control into a CAL verdict.

## Hard decision rule

A Contract C successor is justified by this experiment only if:

- a CAL-attributable assessed conclusion that is otherwise fully known cannot be represented in C 1.0 without losing a demonstrated downstream-relevant distinction.

A Contract C successor is **not** justified merely because:

- RC8J has internal typed reasons C does not expose;
- C lacks `performed/positive` in generic assessment slots;
- the integration layer has not yet established proposition-relative conclusion semantics.

If F1/F2 reject, F3 passes, F4 shows missing conclusion information upstream, and F5 remains valid, the supported disposition is:

`CONTRACT_C_1_0_HAS_ASSESSED_CONCLUSION_CAPACITY; RC8J_STATUS_ALONE_IS_NOT_A_PROPOSITION_CONCLUSION; NEXT_BLOCKER_IS_CAL_INTERNAL_AUTHORITY_TO_CONCLUSION_SEMANTICS`

## Non-claims

This experiment does not define:

- text -> authority receipt population;
- proposition-relative support/refutation semantics;
- aggregation across warranted atoms;
- burden-of-proof policy;
- threshold policy;
- a new CAL verdict;
- a new Contract C field;
- Decision Engine behavior;
- production promotion.

The separate authority programme remains owner of authority-machine independent reproduction and text/receipt authority questions.