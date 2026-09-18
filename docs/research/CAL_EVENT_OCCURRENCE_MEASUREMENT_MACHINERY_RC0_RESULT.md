# CAL Event Occurrence Measurement Machinery RC0 — Terminal Result

Date: 2026-09-17

Classification: Draft Research / Gate-1A measurement-machinery discrimination.

## Frozen lineage

- terminal Gate-0 parent: `245cf7481b4340fc17b80f7000d1663c2769e012`
- exact Gate-0 typed-contract authority: `eaef6c19dbe897e70af89b24d8599cfa05c335a1`
- pre-candidate apparatus head: `b8ee3c717ecec28a961808a8fe2363168847c05d`
- exact qualified Gate-1A head: `855b0435684e0cbc8e31bdac597fee05e60bdfa9`
- dedicated qualification run: `35290810066`

## Disposition

**SUPPORTED FOR GATE-1B WITH BOUNDS.**

The bounded direct event grammar and conservative gated event hybrid satisfy the frozen acceptance rule. Unrestricted dependency/event extraction does not.

## Machinery comparison

### `direct_event_grammar`

- MUST_HANDLE failures: **0**
- FAIL_CLOSED unsafe claims: **0**
- metamorphic failures: **0**
- diagnostic exact: 0
- diagnostic unresolved: ED01–ED05

### `broad_dependency_event`

- MUST_HANDLE failures: **0**
- diagnostic exact: **ED01–ED05**
- FAIL_CLOSED unsafe claims: **EF01, EF02, EF03, EF04, EF05, EF06, EF08, EF09**
- metamorphic failures on reporting, epistemic modality, deontic obligation, and event-order surfaces

The broad path erased or ignored material distinctions between direct occurrence and reporting, possibility, obligation, intention, event-order language, and multi-event composition.

### `conservative_event_hybrid`

- MUST_HANDLE failures: **0**
- diagnostic exact: **ED01–ED05**
- FAIL_CLOSED unsafe claims: **0**
- metamorphic failures: **0**

The hybrid only admits broader extraction for frozen safe surfaces: passive occurrence, passive negation, one open-vocabulary direct action, nominalized occurrence, and terse event-log syntax.

## Preserved failures

- baseline run `35289761512`: 6/6 frozen evaluator controls passed, then candidate import failed because no candidate existed;
- first exposed run `35289888520`: all semantic stages passed, Ruff found one candidate-only line-length defect;
- successor `ed94917...`: semantic/report/Ruff passed; formatter found one candidate-only formatting difference;
- exact head `855b043...`, run `35290810066`: lineage/source isolation, evaluator controls, candidate tests, report, Ruff, formatter, and strict mypy all passed.

Production `src/` remained unchanged from Gate 0.

## Architecture consequence

Event occurrence measurement should keep direct occurrence distinct from event order, state, obligation, and reported/possible occurrence:

```
passage
  -> occurrence safety envelope
  -> direct grammar
       OR
     explicitly gated event extension
  -> EventAtom(actor, action, object, polarity, time)
  -> MeasurementReceipt
  -> [Gate-1B independent source completion / warrant: NOT YET QUALIFIED]
  -> Gate-0 event-occurrence relation algebra
```

Direct event-order remains a separate family. This experiment does not authorize an order sentence to manufacture an occurrence atom.

## Non-claims

No universal event extraction, cross-family order composition, independent source completion/warrant, production plugin behavior, Contract C/Decision behavior, independent reproduction, merge, or release is established.
