# CAL Attribute State Measurement Machinery RC1 — Preregistration

Date: 2026-09-17

Classification: Draft Research / Gate-1A measurement-machinery discrimination.

Parent: terminal attribute-state Gate-0 head `f117698e6db3b47cc68af2024c7816cc8945b004`.
Gate-0 typed-contract authority: `2b4ae5c52f301f16de50719cb11e61919766aa94`.
Predecessor RC0: `INCONCLUSIVE_EVALUATOR_INVALID` because valid alternate entity/domain state atoms were incorrectly treated as fail-closed.

## Corrected question

What proposal machinery safely recovers declared attribute-state atoms while preserving exact entity, attribute, domain, value, and functional/non-functional identity?

RC1 distinguishes:

- **semantic invalidity / family-neighbor hazards**, which remain FAIL_CLOSED;
- **valid alternate bindings**, which are DIAGNOSTIC and must be exact if claimed.

This prevents the evaluator from rewarding blanket refusal on valid non-query atoms.

## Claim buckets

MUST_HANDLE:
- direct functional batch/device/system states;
- direct non-functional record tags.

DIAGNOSTIC:
- possessive, terse, alternate copular, and remains-state surfaces;
- one open-vocabulary value in a declared domain;
- valid alternate entity binding: `Other batch status is released`;
- valid alternate domain/entity state: `Document status is released`.

FAIL_CLOSED:
- class membership;
- change-event language;
- historical state;
- epistemic/deontic modality;
- reporting/quotation;
- conjunction/disjunction;
- scalar-value neighbor.

## Acceptance rule

A path qualifies only if all MUST_HANDLE cases are exact, no FAIL_CLOSED case is claimed, every claimed DIAGNOSTIC is exact, replay and metamorphics pass, and production `src/` is unchanged.

No measurement proposal is authority; Gate-1B source completion/warrant remains separate.
