# Conservative Authority Interface for the B -> CAL -> C Shadow Track

Status: **pre-held-out conservative interface**. This interface is safe to implement as a fail-closed boundary without assuming RC8's formal candidate has earned production authority.

## Inputs

The integration track may consume:

1. a validated Contract B 1.2.0 artifact and its admitted semantic-measurement context;
2. CAL semantic measurements/proposals from bounded research instruments;
3. internal authority receipts when available.

Contract B evidence-world facts, history, anchors, and aperture observations are not proposition-specific semantic authority.

## Internal authority result

Keep execution separate from authority.

- execution: `completed | failed`;
- authority after completed execution: `WARRANTED | REJECTED | UNRESOLVED`;
- typed unresolved/rejection reason preserved internally.

Do not collapse:

- source-established semantic unknown;
- extraction unresolved;
- insufficient interpretation authority;
- applicability unknown;
- source assertion unresolved;
- composition unresolved;
- aperture unresolved;
- execution failure.

## What can be treated as measurement today

Bounded frozen research supports measurement candidates for:

- typed population/membership relations once the typed authority object is correctly established;
- bounded numeric relation/jurisdiction objects;
- explicit comparison measurement (RC7F-B1);
- explicit two-event before/after ordering (RC7F-C);
- bounded permission/exception/temporal composition measurement (RC7F-D).

These are not automatically narrator-level warranted propositions.

## What remains proposal-only for real text

The current structural assertion/scope warrant architecture is still unsafe on held-out parenthetical evidential wrappers. Fresh independent interpretation implementations were also unsafe despite high rule/span recovery.

Therefore the shadow track must not promote a real-text semantic proposal merely because:

- a specialist recognized the semantic family;
- the local typed fields appear complete;
- multiple readers agree;
- a measurement has high confidence;
- a proposal is produced by one of the bounded measurement candidates.

Absent a complete authority receipt, the proposal remains non-authoritative and must not strengthen the epistemic conclusion.

## Invariants the shadow track can enforce now

1. Contract B evidence binding is necessary but not proposition warrant.
2. Measurement and semantic authority are separate objects/states.
3. Unknown authority cannot be converted to neutral evidence.
4. An inapplicable operator cannot invalidate or validate a proposition outside its jurisdiction.
5. All material atom fields must be warranted; no partial-atom promotion.
6. Component warrant does not imply composition warrant.
7. Adding readers/instruments or agreement cannot increase authority by itself.
8. Failed execution is not epistemic abstention.
9. Internal authority reasons need not be exposed through Contract C.
10. No internal authority reason is automatically mapped to a Contract C assessment-stage value without an explicit conformance mapping.

## Contract C projection boundary

Contract C 1.0.0 is frozen and rejects unknown fields. Keep rich authority receipts internal to CAL/shadow research.

Contract C's `semantic_validity` slot has frozen states for not-performed, performed-unknown, performed-adverse, not-applicable, and failed; it does not provide a generic performed-positive state. Do not force the RC8 internal state machine into that slot. A projection rule must be demonstrated separately before positive internal warrant or source-assertion rejection is encoded as a Contract C assessment value.

## Default fail-closed behavior

If the shadow candidate has a semantic measurement but cannot establish the complete authority receipt, retain the measurement/proposal internally, mark authority `UNRESOLVED`, and prevent that proposal from strengthening a CAL epistemic conclusion.
