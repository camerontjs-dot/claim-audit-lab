# CAL Scalar Measurement Machinery RC0 — Terminal Result

Date: 2026-09-17

Classification: Draft Research / Gate-1A measurement-machinery discrimination.

## Frozen lineage

- terminal Gate-0 parent: `43bd155f3dee17d4b7271412927466c904a7f2fd`
- exact Gate-0 typed-contract authority: `c3b7e13d8940f20fcd476eb6b96f276e78e309ec`
- pre-candidate apparatus head: `49c7271d7fb0fb4a77649c7b702c694321a2700c`
- exact qualified Gate-1A head: `c477338cf9585345fab0a35c07a73046f972d86d`
- dedicated qualification run: `35289525295`

## Disposition

**SUPPORTED FOR GATE-1B WITH BOUNDS.**

Both the bounded target-aware numeric grammar and the conservative numeric hybrid satisfy the frozen acceptance rule. The broad number grabber is falsified as a safe scalar measurement path.

## Machinery comparison

### `direct_numeric_grammar`

- MUST_HANDLE failures: **0**
- FAIL_CLOSED unsafe claims: **0**
- metamorphic failures: **0**
- diagnostic exact: SD05
- diagnostic unresolved: SD01, SD02, SD03, SD04, SD06

The direct path safely handles exact point values, closed numeric intervals, counts, temperature, mass, duration, and the frozen direct measurement wording.

### `broad_number_grabber`

- MUST_HANDLE failures: **SM03, SM04**
- diagnostic wrong claims: **SD01, SD02, SD06**
- FAIL_CLOSED unsafe claims: **SF01–SF13**
- multiple metamorphic failures, including attribution, modality, wrong metric/unit, quantitative change, and range loss

The first-number strategy converted every fail-closed numeric trap into a claimed scalar state and collapsed required intervals to points.

### `conservative_numeric_hybrid`

- MUST_HANDLE failures: **0**
- diagnostic exact: **SD01–SD06**
- FAIL_CLOSED unsafe claims: **0**
- metamorphic failures: **0**

The hybrid adds frozen, typed extensions for approximation, word-form percent, terse notation, alternate syntax, Fahrenheit identity, and plus/minus uncertainty while preserving `exact=False` where the surface does not establish exact equality.

## Architecture consequence

Scalar measurement should be target-aware and specialized:

```
Typed scalar target (entity, metric, unit)
        +
admitted passage
        |
        v
binding / unit / scope guard
        |
        +-> bounded exact numeric grammar
        |
        +-> explicitly gated numeric extensions
        |
        v
ScalarAtom(low, high, exact)
        |
        v
MeasurementReceipt
        |
        v
[Gate-1B independent source completion / warrant: NOT YET QUALIFIED]
        |
        v
Gate-0 deterministic interval/value relation algebra
```

Generic number extraction is useful only as a shadow diagnostic instrument.

No unit conversion was authorized. `0.92 fraction` does not silently become `92%`, and mixed-unit ranges fail closed.

## Preserved failures

- baseline run `35289437214`: 6/6 frozen evaluator controls passed, then candidate import failed exactly because no candidate existed;
- exact candidate head `c477338...`, run `35289525295`: lineage/source isolation, evaluator controls, candidate tests, machinery report, focused Ruff, formatter, and strict mypy all passed.

Production `src/` remained unchanged from Gate 0.

## Non-claims

This result does not establish unit conversion, tolerance policy, significant figures, general uncertainty propagation, source-completion warrant, quantitative-change composition, production plugin behavior, Contract C/Decision behavior, independent reproduction, merge, or release.
