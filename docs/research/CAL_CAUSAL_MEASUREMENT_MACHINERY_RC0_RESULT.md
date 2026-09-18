# CAL Causal Explicit-Assertion Measurement Machinery RC0 — Terminal Result

Date: 2026-09-17

Classification: Draft Research / Gate-1A measurement-machinery discrimination.

## Frozen lineage

- terminal Gate-0 parent: `d08f3708e6ba2a1cc3a1705ad280ca4da92dd395`
- exact Gate-0 typed-contract authority: `0bfcfe532bd7dcbe0d9049c0e73173f40d05a415`
- pre-candidate apparatus: `470af99e4f149f001e8caaadea3d26ef03c7a3b3`
- exact qualified Gate-1A head: `c47b2d44c9819563566959b6acf0fa71a60c7e70`
- dedicated qualification run: `35291801222`

## Disposition

**SUPPORTED FOR GATE-1B WITH STRICT BOUNDS ON EXPLICIT ASSERTION INTERPRETATION ONLY.**

This result qualifies proposal machinery for explicit typed relation assertions. It does not qualify causal inference.

## Frozen relation-kind inventory

- `CAUSES`
- `CONTRIBUTES_TO`
- `PREVENTS`
- `CORRELATES_WITH`
- `PRECEDES`
- `CO_OCCURS`

All six are valid measurement outputs. The evaluator fails machinery for laundering one kind into another, not for correctly recognizing non-causal relation kinds.

## Machinery comparison

### `direct_kind_grammar`

- MUST_HANDLE failures: **0**
- FAIL_CLOSED unsafe claims: **0**
- metamorphic failures: **0**
- all diagnostics unresolved

The direct grammar safely covers canonical explicit surfaces for all six frozen kinds and preserves endpoint identity.

### `broad_assertion_classifier`

- MUST_HANDLE failures: **0**
- diagnostic exact: **CD01–CD06**
- diagnostic wrong claims: **0**
- FAIL_CLOSED unsafe claims: **CF01, CF03, CF04, CF05, CF06, CF07, CF08, CF09**
- metamorphic failures on reporting and effect-composition controls

The broad classifier recovered every harder explicit surface, but also manufactured typed relation authority from reporting, risk-factor language, prediction, conjunction/disjunction, experimental context, generic association, and explanatory language.

### `conservative_assertion_hybrid`

- MUST_HANDLE failures: **0**
- diagnostic exact: **CD01, CD02, CD03, CD05, CD06**
- diagnostic unresolved: **CD04**
- FAIL_CLOSED unsafe claims: **0**
- metamorphic failures: **0**

The conservative hybrid deliberately leaves coordinated `A and B are correlated` unresolved in this RC0 rather than widen its safe surface.

## Preserved failures

- baseline run `35291666095`: 7/7 frozen evaluator controls passed, then candidate import failed exactly because no candidate existed;
- exposed-candidate run `35291750376`: evaluator/candidate/report/Ruff stages passed, formatter alone rejected one candidate layout;
- exact head `c47b2d44...`, run `35291801222`: lineage/source isolation, evaluator controls, candidate tests, report, Ruff, formatter, and strict mypy all passed.

Production `src/` remained unchanged from Gate 0.

## Architecture consequence

The bounded path is:

```
admitted passage
  -> explicit-assertion safety envelope
  -> direct kind grammar
       OR
     explicitly gated assertion extension
  -> CausalAtom(endpoint_a, endpoint_b, relation_kind)
  -> MeasurementReceipt
  -> [Gate-1B independent source completion / warrant: NOT YET QUALIFIED]
  -> Gate-0 explicit-assertion relation algebra
```

The words `causal` and `CAUSES` here describe the typed source assertion, not an inference that causality is true in the world.

## Non-claims

This result does not establish causal inference from observational data, experiments, interventions, temporal order, statistical association, model confidence, multiple passages, or external scientific validity. It does not establish source-completion warrant, production plugin behavior, Contract C/Decision behavior, independent reproduction, merge, or release.
