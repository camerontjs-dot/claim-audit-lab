# CAL V1 A2 → EB → B1.2 → CAL → Parent Integration RC0 — Preregistration

Date: 2026-09-18

Classification: Draft Research / cross-repository integration qualification.

## Exact CAL subject

This experiment starts from the terminal DecompositionComposer research head:

- CAL PR #177 terminal record head: `795cd7c25795a6ad08b7cca343bf7c32210cc64b`;
- exact qualified DecompositionComposer code: `7cf0d2e50562ec4ce4082d1e1c058a11025b1a48`;
- exact qualified two-registry code: `7f093e954c2554c3bf21c8bd72d36550414bf54b`.

No CAL production semantic source may change inside this experiment.

## Exact upstream pins

Contract A:
- released compatibility version: `2.0.0`;
- immutable release identity: `contract-a-v2.0.0`;
- production promotion merge: `b59c2fbe38bae78a3a35699362c0e67d17152e4b`;
- schema blob: `ff5cddfeacf4511136a3dd3b47db1a794b631cd9`.

Evidence Bundler:
- frozen V1 integration-candidate PR: `camerontjs-dot/evidence-bundler#79`;
- exact frozen head: `4e1f6fe00e7c350b28f52bfea14f1f8988847884`;
- tested semantic/runtime head beneath the receipt: `8e1e15a96308d20be24b0bd0f0a4d554b0f020cc`;
- integration profile: `eb-v1-integration-10x3-rc0`;
- configuration SHA-256: `sha256:5b10d0c29794e80d6876a99e26bcf6ec6a27a4c5165aee78054a6bc32759f4bc`;
- disposition: `SUPPORTED_EB_V1_TO_B1_2_TO_CAL_INTAKE`.

Contract B:
- released version: `1.2.0`;
- production lock: `c314e53bd91c0736aa4370a364673b069aceb43e`.

The newer Gate-informed EB obligation-selector research PR #119 is explicitly outside this experiment. It is not substituted for frozen #79.

## Question

Can one exact released Contract A 2.0 declared `all_of` object traverse the frozen Evidence Bundler V1 integration candidate, released Contract B 1.2, the qualified CAL child semantic path, and the qualified DecompositionComposer without identity loss, admission leakage, sibling corruption, or parent-rule drift?

## Route under test

```text
Contract A 2.0 declared all_of
  ↓
EB #79 exact 10/3 primary-target retrieval
  ↓
explicit preregistered retained-candidate admission
  ↓
native EB V1 package
  ↓
EB #79 explicit B1.2 compatibility carrier
  ↓
released Contract B 1.2 bundle
  ↓
exact typed child targets
  ↓
SemanticFamilyRegistry
  ↓
measure → warrant → direct relation
  ↓
CAL scoreless child composition
  ↓
immutable native child result
  ↓
BoundAuditOutcome
  ↓
DecompositionComposer
  ↓
parent result + DecompositionReceipt
```

This gate does not require a `CompositionRegistry` module to run. The child path already exercises CAL's proposition-level relation composition. Quantitative-change registry semantics remain separately qualified by PR #176 and are not falsely claimed as end-to-end A/B wired until scalar atomic production authority exists.

## Frozen fixture family

Every case has one Contract A root with exactly two declared ordered children.

Child 1, strict comparison:

`Alpha had a higher rate than Beta.`

Typed fields:
- `lhs_entity = Alpha`
- `rhs_entity = Beta`
- `comparison_direction = MORE_THAN`

Child 2, direct event order:

`Alice reviewed dossier before Bob archived dossier.`

Typed fields:
- `left_subject = alice`
- `left_predicate = review`
- `left_object = dossier`
- `left_polarity = positive`
- `temporal_relation = BEFORE`
- `right_subject = bob`
- `right_predicate = archive`
- `right_object = dossier`
- `right_polarity = positive`

The root is the exact conjunction of those two child propositions.

Each fixture includes both relevant source passages plus deterministic distractors. Admission is selected only by preregistered source identity, never by observing CAL output.

## Frozen four-case matrix

### PIPE01 — both supported

Admit:
- C1 passage: `Alpha had a higher rate than Beta.`
- C2 passage: `Alice reviewed dossier before Bob archived dossier.`

Expected:
- C1 `SUPPORTED`
- C2 `SUPPORTED`
- parent `SUPPORTED`.

### PIPE02 — contradiction + support

Admit:
- C1 passage: `Alpha had a lower rate than Beta.`
- C2 support passage.

Expected:
- C1 `CONTRADICTED`
- C2 `SUPPORTED`
- parent `CONTRADICTED`.

### PIPE03 — support + no admission

Admit:
- C1 support passage only.
- no C2 retained candidate is admitted.

Expected:
- C1 `SUPPORTED`
- C2 `NOT_CHECKABLE`
- parent `NOT_CHECKABLE`.

### PIPE04 — contradiction + no admission

Admit:
- C1 contradiction passage only.
- no C2 retained candidate is admitted.

Expected:
- C1 `CONTRADICTED`
- C2 `NOT_CHECKABLE`
- parent `CONTRADICTED`.

## Admission firewall

The integration harness may mechanically identify retained EB candidates by exact Contract A source identity. It must not:

- inspect CAL outcome before admission;
- mutate K/depth;
- rewrite a query;
- use support/refute gold labels to rank candidates;
- accept a non-retained candidate;
- bypass the EB native package;
- directly construct Contract B.

The exact admission map must be fixed before the CAL child runs.

A requested source passage that is not retained at K=3 is a valid integration failure and must not be repaired by changing K inside this gate.

## Required identity assertions

The gate must prove:

1. Contract A handoff validates through exact EB #79 code;
2. EB package identity uses the exact frozen 10/3 config;
3. the B projection receipt names Contract B 1.2 and the production lock;
4. B claim IDs exactly equal Contract A root/child proposition IDs;
5. B child claim text exactly equals Contract A child text;
6. CAL target text hash binds exact B child claim text;
7. CAL evidence world contains only B-admitted passages;
8. no EB `not_retained` candidate reaches CAL admitted evidence;
9. each child native CAL result is deterministically hashed into one `BoundAuditOutcome`;
10. each bound child ID/text hash matches Contract A;
11. DecompositionReceipt binds exact Contract A declaration and exact child-result identities;
12. replay of the same A/admission/carrier produces byte-identical native EB package, B projection receipt, child CAL result bytes, and parent receipt.

## Mutation / failure controls

At minimum:

- flip one admission from accepted to needs-review -> corresponding child must stop deciding;
- attempt admission of a non-retained candidate -> fail or remain non-admitted;
- swap C1/C2 typed targets -> CAL target binding refuses;
- mutate child text hash -> CAL target binding refuses;
- drop one child result before parent recomposition -> DecompositionComposer refuses;
- add undeclared child result -> DecompositionComposer refuses;
- swap supplied child result order -> parent result/receipt unchanged;
- mutate one native child result byte before binding -> child result digest changes and therefore parent receipt changes;
- alter B compatibility carrier -> EB native package identity unchanged while B/receipt identity changes;
- alter Contract A child order -> parent receipt identity changes.

## Stopping rule

If all four frozen cases and the mutation controls pass on one exact CAL research head while:

- CAL production semantic source remains frozen;
- EB #79 remains exact;
- Contract B 1.2 remains exact;
- no retrieval parameter changes are introduced;

freeze that integration subject.

Then test Contract C representation losslessness against the newly resulting child + parent state.

No Contract C, Decision, release, merge, tag, or production-default change is authorized here.
