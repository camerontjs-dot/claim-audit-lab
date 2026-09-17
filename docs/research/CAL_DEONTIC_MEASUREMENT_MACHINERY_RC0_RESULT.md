# CAL Deontic Measurement Machinery RC0 — Terminal Result

Date: 2026-09-17

Classification: Draft Research / Gate-1A measurement-machinery discrimination.

## Frozen lineage

- terminal Gate-0 parent: `7f1e63a17b18c14fe23c3fed00c7faf102bc62e7`
- exact Gate-0 typed-contract authority: `791cd59fa47ba8e7a709f289584468aa9e255334`
- pre-candidate apparatus head: `fc29b2e9d5d6eeac9f49ca97e73a2ebbba468f4a`
- exact qualified Gate-1A candidate head: `306abf0ca4851f4fb54f006fd954d8a07d982564`
- dedicated qualification run: `35288716530`

## Disposition

**SUPPORTED FOR GATE-1B, bounded to the direct-grammar deontic measurement path and the frozen MUST_HANDLE claim shapes.**

The result does not select spaCy dependency parsing as a safe independent deontic measurement path.

## Frozen corpus

The apparatus used three buckets:

- 14 MUST_HANDLE cases: direct permission, prohibition, obligation, restricted permission, explicit permitted/prohibited/required wording, simple condition/exception/time bindings, and multiple actor/action bindings;
- 6 DIAGNOSTIC cases: passive permission, regulatory `shall` / `shall not`, alternate restricted-to wording, an unfamiliar action, and policy attribution;
- 12 FAIL_CLOSED cases: epistemic `may`, state possibility, ambiguous `may not`, negated obligation, reporting/quotation wrappers, conjunction, disjunction, nested condition/exception, `only + must`, event-neighbor modal text, and ability `can`.

## Machinery comparison

### `direct_grammar`

- MUST_HANDLE failures: **0**
- FAIL_CLOSED unsafe claims: **0**
- metamorphic failures: **0**
- diagnostic exact: 0
- diagnostic unresolved: DD01, DD02, DD03, DD05, DD06
- diagnostic not-applicable: DD04

This path is narrow but safe on the frozen RC0 boundary.

### `spacy_dependency`

- MUST_HANDLE failures: **0**
- diagnostic exact: DD01, DD02, DD03, DD05
- diagnostic unresolved: DD06
- diagnostic not-applicable: DD04
- FAIL_CLOSED unsafe claims: **DF01, DF02, DF07, DF08, DF09, DF11**
- metamorphic failure: `DM01 -> DF01` retained a deontic claim when the surface changed from deontic permission to epistemic possibility

The broader dependency path recovered useful passive/regulatory/open-action forms, but dependency structure plus modal cues was not sufficient to distinguish deontic authority from epistemic, conjunction/disjunction, nested-scope, or event-neighbor uses.

### `conservative_hybrid`

- MUST_HANDLE failures: **0**
- FAIL_CLOSED unsafe claims: **0**
- metamorphic failures: **0**
- diagnostic behavior matched the bounded grammar in this RC0

The first hybrid was safe but added no diagnostic coverage because its safety gate refused to widen after an unresolved bounded-grammar result. That negative is preserved rather than relabeled as a gain.

## Preserved failures

- baseline run `35288225603`: frozen evaluator controls 6/6 passed, then candidate import failed exactly because no candidate existed;
- first exposed-candidate run `35288359968`: apparatus and candidate semantic tests passed, then static hygiene failed;
- run `35288516372`: a candidate-only newline patch introduced a syntax error; preserved as tooling failure;
- run at `179873ea...`: semantic tests/report/Ruff passed and formatter alone rejected one candidate formatting shape;
- exact head `306abf0...`, run `35288716530`: lineage/source-isolation, 6/6 evaluator controls, 3/3 candidate tests, comparison report, focused Ruff, formatter, and strict mypy all passed.

No production `src/` file changed from the Gate-0 parent.

## Architecture consequence

For the current deontic family, the evidence supports:

```
evidence passage
  -> bounded deontic grammar proposal
  -> MeasurementReceipt
  -> [Gate-1B independent source completion / warrant: NOT YET QUALIFIED]
  -> warranted deontic atom
  -> already-qualified deterministic Gate-0 relation algebra
```

A broad dependency parser is better retained as a **shadow measurement instrument** until a successor can prove safe disambiguation. Its additional recall is useful diagnostic evidence, not verdict authority.

A successor may test selective dependency extensions for passive voice, `shall`, and unfamiliar affirmative obligation actions, but must do so on fresh frozen controls rather than treating the present diagnostics as newly earned production coverage.

## Non-claims

This result does not establish independent source completion, warrant, universal deontic language understanding, nested scope, operational authorization, a production plugin, Contract C/Decision behavior, independent reproduction, merge, or release.
