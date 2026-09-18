# CAL Attribute State Measurement Machinery RC1 — Terminal Result

Date: 2026-09-17

Classification: Draft Research / Gate-1A measurement-machinery discrimination.

## Frozen lineage

- terminal Gate-0 parent: `f117698e6db3b47cc68af2024c7816cc8945b004`
- exact Gate-0 typed-contract authority: `2b4ae5c52f301f16de50719cb11e61919766aa94`
- predecessor RC0: `INCONCLUSIVE_EVALUATOR_INVALID`
- RC1 pre-candidate apparatus: `122ae86869d0091a61c24f32045714a05cc716b3`
- exact qualified RC1 head: `fadbfe0906023a24dfbb2a78ece766664021febd`
- dedicated qualification run: `35291492469`

## Disposition

**SUPPORTED FOR GATE-1B WITH BOUNDS.**

RC1 repairs the predecessor evaluator by distinguishing valid alternate bindings from semantic invalidity.

## Machinery comparison

### `direct_declared_state_grammar`

- MUST_HANDLE failures: **0**
- FAIL_CLOSED unsafe claims: **0**
- metamorphic failures: **0**
- diagnostic exact: 0
- diagnostic unresolved: AD01–AD07

### `broad_copular_state`

- MUST_HANDLE failures: **0**
- diagnostic exact: **AD01–AD07**
- diagnostic wrong claims: **0**
- FAIL_CLOSED unsafe claims: **AF01–AF09**
- metamorphic failures on reporting, modality, change-event, and composition controls

The broad path correctly preserves alternate entity/domain states after the RC1 evaluator correction, but still overreaches across membership, event/change, temporal, modal, reporting, and multi-value boundaries.

### `conservative_state_hybrid`

- MUST_HANDLE failures: **0**
- diagnostic exact: **AD01–AD07**
- diagnostic wrong claims: **0**
- FAIL_CLOSED unsafe claims: **0**
- metamorphic failures: **0**

## Evaluator correction evidence

RC0 incorrectly treated `Other batch status is released` and `Document status is released` as fail-closed. RC1 freezes both as valid diagnostics with exact entity/domain bindings.

This allows the evaluator to distinguish:

- correct alternate state extraction;
- entity erasure;
- domain erasure;
- actual family-neighbor overreach.

## Architecture consequence

Attribute-state measurement should use a declared attribute/domain inventory plus an explicit family-neighbor envelope:

```
passage
  -> declared entity/attribute/domain guard
  -> direct state grammar
       OR
     explicitly gated state extensions
  -> StateAtom(entity, attribute, domain, value, functional)
  -> MeasurementReceipt
  -> [Gate-1B independent source completion / warrant: NOT YET QUALIFIED]
  -> Gate-0 closed/functional attribute-state algebra
```

This remains a narrow declared-state family, not a generic subject-predicate-value escape hatch.

## Non-claims

No ontology acquisition, temporal-state reasoning, event-to-state inference, source-completion warrant, production plugin behavior, Contract C/Decision behavior, independent reproduction, merge, or release is established.
