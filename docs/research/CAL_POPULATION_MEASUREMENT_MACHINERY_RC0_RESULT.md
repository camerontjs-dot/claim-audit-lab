# CAL Population Measurement Machinery RC0 — Terminal Result

Date: 2026-09-17

Classification: Draft Research / Gate-1A measurement-machinery discrimination.

## Frozen lineage

- terminal Gate-0 parent: `2cc293e170bfbfd4ad0c64534114e900e5512995`
- exact Gate-0 typed-contract authority: `3abb817e6d6aeea4498a8495e3b4d5b54f984be6`
- pre-candidate apparatus head: `014c95657676e5d631adf612aa2b07469a37ead1`
- exact qualified Gate-1A head: `7e0ef92a7fb25577d85b1a8f7aa9c222c3f61632`
- dedicated qualification run: `35289125082`

## Disposition

**SUPPORTED FOR GATE-1B WITH BOUNDS.**

Two proposal paths survived the frozen acceptance rule:

1. the bounded direct membership/subset grammar;
2. the conservative hybrid that permits dependency-derived output only behind explicit safe-extension surfaces.

The unrestricted dependency/copular path did not survive the fail-closed controls.

## Representation result

Natural-language pressure testing exposed a useful architecture correction: entity-membership and class-subset evidence should be measured as separate atom types.

```
MembershipAtom(entity, population, MEMBER | NON_MEMBER)

SubsetAtom(child_population, parent_population)
```

A passage need not carry both. Cross-passage inference such as:

```
Alice ∈ sterile_technicians
sterile_technicians ⊆ trained_personnel
-----------------------------------------
Alice ∈ trained_personnel
```

belongs in a separately tested composition stage rather than being smuggled into passage-local extraction.

## Machinery comparison

### `direct_grammar`

- MUST_HANDLE failures: **0**
- FAIL_CLOSED unsafe claims: **0**
- metamorphic failures: **0**
- diagnostic exact: 0
- diagnostic unresolved: PD01–PD06

The bounded grammar safely covers direct positive/negative membership plus bare, `all`, and `every` subset forms.

### `spacy_dependency`

- MUST_HANDLE failures: **0**
- diagnostic exact: **PD01–PD06**
- FAIL_CLOSED unsafe claims: **PF01, PF02, PF03, PF06, PF07, PF08, PF11, PF12**
- metamorphic failures:
  - `PM05 -> PF01`
  - `PM05 -> PF03`
  - `PM01 -> PF08`
  - `PM01 -> PF07`

The broad path erased or failed to respect material distinctions involving existential/majority quantifiers, `only`, past membership, epistemic modality, reporting scope, and role composition.

### `conservative_hybrid`

- MUST_HANDLE failures: **0**
- diagnostic exact: **PD01–PD06**
- FAIL_CLOSED unsafe claims: **0**
- metamorphic failures: **0**

The hybrid only admits broad-parser output for frozen safe-extension surfaces such as `belongs to`, `among`, `include`, explicit `subset of`, `each`, and `serves as`. It is therefore evidence for dependency parsing as a bounded proposal aid, not as free-standing semantic authority.

## Preserved failures

- baseline run `35288961168`: 6/6 frozen evaluator controls passed; candidate import then failed because no candidate existed;
- first exposed-candidate run `35289053215`: semantic/evaluator/report/Ruff stages passed, formatter alone failed;
- exact head `7e0ef92...`, run `35289125082`: lineage/source isolation, evaluator controls, candidate discrimination, comparison report, focused Ruff, formatter, and strict mypy all passed.

Production `src/` remained unchanged from the Gate-0 parent.

## Architecture consequence

The bounded current candidate machinery is:

```
passage
  -> membership/subset safety envelope
  -> direct grammar
       OR
     explicitly gated dependency extension
  -> MembershipAtom | SubsetAtom proposal
  -> MeasurementReceipt
  -> [Gate-1B independent source completion / warrant: NOT YET QUALIFIED]
  -> warranted population atom(s)
  -> separately tested cross-passage subset composition
  -> Gate-0 relation algebra
```

The raw dependency parser remains suitable as a shadow instrument for finding recall opportunities and evaluator counterexamples.

## Non-claims

This result does not establish source-completion warrant, general quantifier logic, temporal membership, role ontology, class disjointness, cross-passage inheritance, production plugin behavior, Contract C/Decision behavior, independent reproduction, merge, or release.
