# Conservative Authority Interface for the B -> CAL -> C Shadow Track

Status: **research-supported internal interface, not production authority**.

RC8J is the strongest typed authority gate supported by the RC8 research programme. The integration/shadow track may use this document to fail closed, but must not treat the research result as permission to modify production CAL semantics or frozen Contract C.

## Inputs

The shadow track may consume:

1. a validated Contract B 1.2.0 artifact and its admitted semantic-measurement context;
2. CAL semantic measurements/proposals from bounded research instruments;
3. internal typed authority receipts.

Contract B remains the integrity and identity authority for its canonical claim/source/passage/bundle records. RC8 does not create a second hash regime.

Contract B evidence-world factual context, history, anchors and aperture observations are not proposition-specific semantic authority merely because they are integrity-bound.

## Required Contract B context for the supported gate

For a proposition-specific authority assessment, the internal context must preserve the already-validated coordinates needed by the supported research candidate:

- admitted `source_id`;
- validated `bundle_id`;
- admitted `passage_id`;
- admitted passage extent/representation coordinates;
- referenced Contract B `claim_id`;
- evidence-admitted state.

If the shadow path cannot supply one of these required identity bindings, it must fail closed rather than manufacture an equivalent identifier from local semantic output.

## Internal authority result

Keep execution separate from authority:

- execution: `completed | failed`;
- authority after completed execution: `WARRANTED | REJECTED | UNRESOLVED`;
- failed execution: `NO_ASSESSMENT`;
- typed unresolved/rejection reason retained internally.

Do not collapse:

- source-established semantic unknown;
- extraction unresolved;
- insufficient interpretation authority;
- evidence source binding unresolved;
- Contract B segment binding unresolved;
- Contract B claim binding unresolved;
- atom identity binding unresolved;
- applicability unknown;
- source assertion unresolved;
- composition unresolved;
- aperture unresolved;
- execution failure.

## Required internal receipt surface

The strongest supported research interface contains these authority-bearing elements.

### Contract B and execution binding

- execution state;
- evidence-admitted state;
- raw/admitted source identity and authority-subject source identity;
- raw/validated bundle identity and authority-subject bundle identity;
- raw/admitted passage identity and authority-subject passage identity;
- admitted passage extent;
- raw/referenced Contract B claim identity and authority-subject claim identity;
- target atom identity and authority-subject atom identity.

### Proposal and assertion

- proposed atom family;
- proposed material field values;
- proposal source span;
- unsupported extra modifiers, if any;
- authority-subject identity;
- source assertion state;
- structural scope path;
- assertion authority-subject identity.

### Operator jurisdiction

- operator identity;
- semantic domain/family;
- applicability;
- governed span;
- jurisdiction fields;
- operator authority-subject identity.

### Material field warrants

For every required material field:

- interpretation status;
- typed value where applicable;
- support span;
- field receipt authority-subject identity.

### Composition and aperture

When required:

- composition state, basis and authority-subject identity;
- aperture state and authority-subject identity.

## Supported fail-closed ordering

The shadow consumer should preserve this precedence rather than merely testing all conditions as an unordered bag:

1. execution failure;
2. evidence rejection;
3. admitted source binding;
4. Contract B bundle binding;
5. Contract B passage binding;
6. admitted passage extent and containment;
7. Contract B claim identity;
8. target atom identity;
9. same-subject proposal/assertion/operator/field/composition/aperture binding;
10. assertion state and scope;
11. operator applicability/domain/governance;
12. required field status/value/support;
13. required composition/aperture state.

This ordering is part of the typed reason behavior exercised by the frozen research suite.

## Invariants the shadow track can enforce

1. Contract B evidence admission is necessary but not proposition warrant.
2. A receipt must stay attached to the admitted source, validated bundle, admitted passage, referenced claim and target atom.
3. Proposal and valid required-field support must remain inside the admitted passage extent as well as applicable operator governance.
4. Measurement and semantic authority remain separate objects/states.
5. Unknown authority cannot be converted to neutral evidence.
6. An inapplicable operator cannot validate or invalidate material outside its jurisdiction.
7. All material atom fields must be warranted; no partial-atom promotion.
8. Component warrant does not imply composition warrant.
9. Adding readers, instruments, agreement or confidence cannot increase authority by itself.
10. Failed execution is not epistemic abstention.
11. Internal authority reasons need not be exposed through Contract C.
12. No internal positive authority state is automatically a Contract C assessment value.

## What remains proposal-only for real text

RC8J establishes a typed receipt transition over frozen structured inputs. It does not establish that a real-text extraction system can correctly populate those receipts.

Therefore the shadow track must not promote a real-text proposal merely because:

- a specialist recognized the semantic family;
- local typed fields appear complete;
- IDs are present but their derivation is not established;
- multiple readers agree;
- a measurement has high confidence;
- a bounded measurement candidate produced the proposal.

Absent a complete, correctly populated authority receipt, retain the measurement/proposal internally and prevent it from strengthening the epistemic conclusion.

## Contract C projection boundary

Contract C 1.0.0 remains frozen and rejects unknown fields. Keep the rich authority receipt internal to CAL/shadow research.

Do not force `WARRANTED`, `REJECTED`, `UNRESOLVED`, or their typed reasons directly into a Contract C field merely because a similar word exists there. Contract C projection requires its own demonstrated conformance rule.

In particular, positive internal authority does not by itself establish how Contract C's frozen assessment-stage values should be populated.

## Default fail-closed behavior

If the shadow candidate has a semantic measurement but cannot establish the complete supported authority receipt, retain the measurement/proposal internally, mark authority `UNRESOLVED` with the specific internal reason, and prevent that proposal from strengthening the CAL epistemic conclusion.

If execution itself failed, record `NO_ASSESSMENT` rather than an epistemic unresolved state.

## Research pins

Strongest supported candidate:

- RC8J blob: `f55156e43e0c1b4a7868bc8339585b8892edda38`;
- exposed qualification: 268/268 exact, 0 unsafe warrants;
- fresh prospective heldout: 28/28 exact, 0 unsafe warrants;
- prospective artifact: `9862475745`;
- digest: `sha256:0f377934b1e4adb8e813fd6d5a7c7d2e679cf37ca882d21979ca5889b98141d0`.

These pins identify research evidence only. They do not authorize production adoption.
