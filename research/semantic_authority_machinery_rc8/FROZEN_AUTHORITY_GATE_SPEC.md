# Frozen Authority Gate Specification v1

Status: **normative experiment specification for fresh independent reproduction**.

This specification defines the typed authority transition supported by the RC8J research result. It is intentionally independent of any reference implementation. A future clean-room implementer should be able to implement this behavior from this document alone.

This specification does **not** authorize production adoption.

## 1. Scientific object

The authority gate assesses an already-constructed semantic atom proposal and its authority receipts against a validated Contract B evidence context.

It returns exactly:

```text
{
  authority_status: WARRANTED | REJECTED | UNRESOLVED | NO_ASSESSMENT,
  reason: <typed reason string>
}
```

The gate is not a truth oracle, evidence retriever, semantic parser, Contract B validator, Contract C exporter, confidence scorer, or voting mechanism.

## 2. Structural precondition and ownership boundary

The input container is assumed to have passed a separate structural/schema validation layer sufficient to make required object/array/scalar accesses safe.

This authority transition owns **semantic absence and authority-binding absence** that are explicitly described below. It does not define behavior for arbitrary corrupt JSON/Python objects, impossible container types, missing mandatory structural objects, or malformed proposal objects not listed as semantic states.

In particular:

- Contract B intake owns validation of canonical Contract B bundle/source/passage/claim records and their integrity hashes;
- a CAL receipt schema validator is expected to own gross internal receipt-shape/type errors;
- this specification owns the typed authority transition after those structural prerequisites.

No claim is made here that such an internal receipt schema validator is already production-qualified.

## 3. Required input surface

### 3.1 Top-level execution and evidence

- `execution_state`: `completed | failed`;
- `evidence_admitted`: boolean;
- `authority_subject_id`: string or absent;
- `raw_source_id`: string or absent;
- `authority_subject_source_id`: string or absent;
- `raw_bundle_id`: string or absent;
- `authority_subject_bundle_id`: string or absent;
- `raw_passage_id`: string or absent;
- `authority_subject_passage_id`: string or absent;
- `admitted_passage_span`: two-integer inclusive-boundary coordinate pair or absent;
- `raw_claim_id`: string or absent;
- `authority_subject_claim_id`: string or absent;
- `target_atom_id`: string or absent;
- `authority_subject_atom_id`: string or absent.

The exact coordinate convention used to generate passage offsets belongs to the validated representation context. The authority gate requires only consistent ordered coordinates and containment comparisons.

### 3.2 Proposal

`proposal` contains:

- `family`: semantic domain/family string;
- `source_span`: ordered two-integer coordinate pair;
- `fields`: map from material field name to proposed typed value;
- `extra_modifiers`: array;
- `authority_subject_id`: string or absent.

### 3.3 Assertion

`assertion` contains:

- `state`: `asserted | not_asserted | unknown`;
- `scope_path`: structural scope representation retained for audit/interpretation;
- `authority_subject_id`: string or absent.

### 3.4 Operator

`operator` contains:

- `operator_id`;
- `domain`;
- `applicability`: `applicable | inapplicable | unknown`;
- `governed_span`: ordered two-integer coordinate pair;
- `jurisdiction_fields`: collection of field names;
- `authority_subject_id`: string or absent.

### 3.5 Required fields and field warrants

- `required_fields`: ordered array of material field names;
- `field_warrants`: map from field name to receipt.

A field receipt contains:

- `status`: one of `established | semantic_unknown | extraction_unresolved | insufficient_authority | absent_not_applicable`, or another structurally valid but unrecognized status;
- `value`: typed value or null as appropriate;
- `span`: ordered two-integer support coordinate pair or absent/malformed as explicitly handled below;
- `authority_subject_id`: string or absent.

Required fields are evaluated in the supplied `required_fields` order. That order determines which typed field reason is returned when multiple required fields fail.

### 3.6 Composition

`composition` contains:

- `required`: boolean;
- `state`: when required, `warranted | rejected | unresolved` or another non-warranted state;
- `basis`: audit-visible basis;
- `authority_subject_id`: string or absent when required.

### 3.7 Aperture

`aperture` contains:

- `required`: boolean;
- `state`: `sufficient` or a non-sufficient state;
- `authority_subject_id`: string or absent when required.

### 3.8 Diagnostic-only fields

Reader agreement count, instrument IDs, instrument count, scalar confidence, retrieval rank, nomination metadata and similar diagnostic fields have no authority effect in this specification.

Adding, removing or changing only those fields must not strengthen or weaken authority.

## 4. Span validity and containment

An admitted passage span is valid only when:

- it has exactly two coordinates;
- both coordinates are integers in the receipt schema's integer domain;
- start <= end.

A required-field support span is resolved for authority only when it is a valid two-integer ordered pair. Missing or malformed field support span is handled by the field rules below.

For any valid inner `[start, end]` and outer `[outer_start, outer_end]`:

```text
inside iff start >= outer_start AND end <= outer_end
```

Equality at either boundary is inside.

## 5. Deterministic authority transition

Return immediately at the first matching condition below.

### Step 1: execution

If `execution_state != completed`:

- `NO_ASSESSMENT / EXECUTION_FAILED`.

### Step 2: evidence admission

If `evidence_admitted == false`:

- `REJECTED / EVIDENCE_NOT_ADMITTED`.

### Step 3: admitted-source binding

If either `raw_source_id` or `authority_subject_source_id` is absent:

- `UNRESOLVED / AUTHORITY_EVIDENCE_SOURCE_BINDING_UNRESOLVED`.

If they differ:

- `REJECTED / AUTHORITY_EVIDENCE_SOURCE_MISMATCH`.

### Step 4: Contract B segment binding presence

If any of these is absent:

- `raw_bundle_id`;
- `authority_subject_bundle_id`;
- `raw_passage_id`;
- `authority_subject_passage_id`;

return:

- `UNRESOLVED / AUTHORITY_EVIDENCE_SEGMENT_BINDING_UNRESOLVED`.

### Step 5: Contract B bundle identity

If `authority_subject_bundle_id != raw_bundle_id`:

- `REJECTED / AUTHORITY_EVIDENCE_BUNDLE_MISMATCH`.

### Step 6: admitted passage identity

If `authority_subject_passage_id != raw_passage_id`:

- `REJECTED / AUTHORITY_EVIDENCE_PASSAGE_MISMATCH`.

### Step 7: admitted passage extent

If `admitted_passage_span` is absent or not a valid ordered two-integer span:

- `UNRESOLVED / ADMITTED_PASSAGE_SPAN_UNRESOLVED`.

### Step 8: proposal containment in admitted passage

If `proposal.source_span` lies outside `admitted_passage_span`:

- `REJECTED / SOURCE_SPAN_OUTSIDE_ADMITTED_PASSAGE`.

### Step 9: valid required-field support containment in admitted passage

For each field in `required_fields`, in supplied order:

- if no field receipt exists, do not return here; field presence is adjudicated later;
- if the receipt support span is missing or malformed, do not return here; support-span resolution is adjudicated later;
- if a valid receipt support span lies outside `admitted_passage_span`, return:
  - `REJECTED / FIELD_SUPPORT_OUTSIDE_ADMITTED_PASSAGE:<field>`.

### Step 10: Contract B claim binding

If either `raw_claim_id` or `authority_subject_claim_id` is absent:

- `UNRESOLVED / AUTHORITY_CLAIM_BINDING_UNRESOLVED`.

If they differ:

- `REJECTED / AUTHORITY_CLAIM_MISMATCH`.

### Step 11: atom identity binding

If either `target_atom_id` or `authority_subject_atom_id` is absent:

- `UNRESOLVED / AUTHORITY_ATOM_IDENTITY_BINDING_UNRESOLVED`.

If they differ:

- `REJECTED / AUTHORITY_ATOM_IDENTITY_MISMATCH`.

### Step 12: assessment authority-subject binding

If top-level `authority_subject_id` is absent:

- `UNRESOLVED / AUTHORITY_SUBJECT_BINDING_UNRESOLVED:assessment`.

Call this value `subject` for the remaining checks.

### Step 13: proposal same-subject binding

If `proposal.authority_subject_id` is absent:

- `UNRESOLVED / AUTHORITY_SUBJECT_BINDING_UNRESOLVED:proposal`.

If it differs from `subject`:

- `REJECTED / AUTHORITY_SUBJECT_MISMATCH:proposal`.

### Step 14: assertion same-subject binding

If `assertion.authority_subject_id` is absent:

- `UNRESOLVED / AUTHORITY_SUBJECT_BINDING_UNRESOLVED:assertion`.

If it differs from `subject`:

- `REJECTED / AUTHORITY_SUBJECT_MISMATCH:assertion`.

### Step 15: operator same-subject binding

If `operator.authority_subject_id` is absent:

- `UNRESOLVED / AUTHORITY_SUBJECT_BINDING_UNRESOLVED:operator`.

If it differs from `subject`:

- `REJECTED / AUTHORITY_SUBJECT_MISMATCH:operator`.

### Step 16: source assertion state

If `assertion.state == not_asserted`:

- `REJECTED / SOURCE_ASSERTION_NOT_ESTABLISHED`.

If `assertion.state == unknown`:

- `UNRESOLVED / SOURCE_ASSERTION_UNRESOLVED`.

`asserted` proceeds.

### Step 17: operator domain

If `operator.domain != proposal.family`:

- `REJECTED / OPERATOR_DOMAIN_MISMATCH`.

### Step 18: operator applicability

If `operator.applicability == inapplicable`:

- `REJECTED / OPERATOR_INAPPLICABLE`.

If `operator.applicability == unknown`:

- `UNRESOLVED / OPERATOR_APPLICABILITY_UNKNOWN`.

`applicable` proceeds.

### Step 19: proposal containment in operator governance

If `proposal.source_span` lies outside `operator.governed_span`:

- `REJECTED / SOURCE_SPAN_OUTSIDE_OPERATOR_GOVERNANCE`.

### Step 20: unsupported extra modifiers

If `proposal.extra_modifiers` is non-empty:

- `REJECTED / UNSUPPORTED_EXTRA_MODIFIER`.

### Step 21: required fields

For each field in `required_fields`, in supplied order, perform all of the following before moving to the next field.

#### 21a. Operator jurisdiction

If field is not in `operator.jurisdiction_fields`:

- `REJECTED / FIELD_OUTSIDE_OPERATOR_JURISDICTION:<field>`.

#### 21b. Required receipt presence

If no receipt exists in `field_warrants`:

- `REJECTED / FIELD_REQUIRED_ABSENT:<field>`.

#### 21c. Field same-subject binding

If receipt `authority_subject_id` is absent:

- `UNRESOLVED / AUTHORITY_SUBJECT_BINDING_UNRESOLVED:field:<field>`.

If it differs from `subject`:

- `REJECTED / AUTHORITY_SUBJECT_MISMATCH:field:<field>`.

#### 21d. Field support span under operator governance

If receipt support span is absent, malformed, or not an ordered two-integer pair:

- `UNRESOLVED / FIELD_SUPPORT_SPAN_UNRESOLVED:<field>`.

If it lies outside `operator.governed_span`:

- `REJECTED / FIELD_SUPPORT_OUTSIDE_OPERATOR_GOVERNANCE:<field>`.

#### 21e. Required-field status

If status is `absent_not_applicable`:

- `REJECTED / FIELD_REQUIRED_ABSENT:<field>`.

If status is `extraction_unresolved`:

- `UNRESOLVED / FIELD_EXTRACTION_UNRESOLVED:<field>`.

If status is `insufficient_authority`:

- `UNRESOLVED / FIELD_INSUFFICIENT_AUTHORITY:<field>`.

If status is neither `established` nor `semantic_unknown` nor one of the states above:

- `UNRESOLVED / FIELD_STATUS_UNRECOGNIZED:<field>`.

#### 21f. Field value equality

For `established` or `semantic_unknown`, if `proposal.fields[field] != receipt.value`:

- `REJECTED / FIELD_VALUE_MISMATCH:<field>`.

Otherwise the field passes.

### Step 22: required composition

If `composition.required == true`:

1. missing `composition.authority_subject_id` ->
   - `UNRESOLVED / AUTHORITY_SUBJECT_BINDING_UNRESOLVED:composition`;
2. subject mismatch ->
   - `REJECTED / AUTHORITY_SUBJECT_MISMATCH:composition`;
3. `composition.state == rejected` ->
   - `REJECTED / COMPOSITION_REJECTED`;
4. `composition.state != warranted` ->
   - `UNRESOLVED / COMPOSITION_UNRESOLVED`;
5. `warranted` proceeds.

If composition is not required, no composition binding is required.

### Step 23: required aperture

If `aperture.required == true`:

1. missing `aperture.authority_subject_id` ->
   - `UNRESOLVED / AUTHORITY_SUBJECT_BINDING_UNRESOLVED:aperture`;
2. subject mismatch ->
   - `REJECTED / AUTHORITY_SUBJECT_MISMATCH:aperture`;
3. `aperture.state != sufficient` ->
   - `UNRESOLVED / APERTURE_UNRESOLVED`;
4. `sufficient` proceeds.

If aperture is not required, no aperture binding is required.

### Step 24: successful authority

If every applicable prior condition passes:

- `WARRANTED / ALL_REQUIRED_WARRANT_ESTABLISHED`.

## 6. Non-authority invariants

The following must not independently increase authority:

- more readers;
- more instruments;
- agreement count;
- confidence score;
- nomination rank;
- retrieval score;
- reviewer identity or notes;
- Contract B history-count summaries.

These may be retained for diagnostics or audit history but have no transition role above.

## 7. Contract B boundary

The authority gate assumes that `raw_bundle_id`, `raw_source_id`, `raw_passage_id`, `raw_claim_id`, admitted passage coordinates and evidence-admitted state were produced from a validated Contract B context.

The gate does not independently recompute Contract B bundle trees, `SHA256SUMS`, passage hashes or source-content hashes.

The frozen Contract B authority used to define this boundary is:

- repository: `camerontjs-dot/apparatus-contracts`;
- commit: `c314e53bd91c0736aa4370a364673b069aceb43e`;
- `handoff-contract-v1.0.0.md` blob: `3e49901dff567ff5bbad55a2d6ccdc3ed36a7a26`;
- `contract-b-factual-context-extension-v1.2.0.md` blob: `77645a6adac664892866f3fdf8abf66cd1d0dd10`.

## 8. Explicit non-claims

This specification does not define or establish:

- how atom IDs are generated;
- whether opaque IDs are honest or collision-resistant;
- how source language is parsed into proposals/receipts;
- whether a proposition is true;
- all possible composition semantics;
- Contract C projection;
- Decision Engine operational authorization;
- production release criteria;
- cryptographic authenticity beyond Contract B validation.

## 9. Independent-reproduction success question

A fresh implementer should be judged on whether this behavior can be recovered from the specification alone, not on whether it can imitate a reference implementation after reveal.

A disagreement is scientific evidence and must be preserved rather than repaired after reference/evaluator reveal.
