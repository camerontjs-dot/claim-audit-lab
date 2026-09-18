# CAL Strict Comparison RC1 Authority Pressure RC0 — Preregistration

Date: 2026-09-17

Classification: Draft Research / post-qualification adversarial pressure test.

## Frozen subject

- CAL V1 RC1 semantic implementation: `a902621e8baea3063dddd7f92ba975aade305464`
- qualified in PR #105 at 19/19 fresh cases, 0 unsafe results.
- raw strict-comparison modifier-loss counterexamples: Draft PR #139.

No production source is modified by this study.

## Question

Does RC1's independent source-completion / authority boundary actually prevent the modifier-loss counterexamples exposed in PR #139 from becoming warranted deciding strict-comparison evidence?

This tests the whole bounded path:

```
passage
-> RC1 strict-comparison measurement
-> RC1 independent source completion
-> authority integrity
-> proposition-relative relation
-> scoreless composition
```

## Positive control

`Sector A was higher than Sector B.`

Expected: `supported`.

## Fail-closed pressure cases

Every following passage is unsafe to treat as an unqualified narrator-level `Sector A > Sector B` atom under the current proposition because material semantics are absent from the atom schema:

- `not higher than`
- `no higher than`
- `probably higher than`
- `allegedly higher than`
- `may be higher than`
- `could be higher than`
- conditional `If ... higher than ...`
- report-attributed comparison
- negated equality
- negated same-as
- negated multiplier
- multi-comparison conjunction
- multi-comparison disjunction

Expected terminal outcome for every pressure case: `not_checkable`, with no deciding SUPPORTS/REFUTES relation.

## Hard gate

One unsafe `supported` or `contradicted` pressure outcome falsifies modifier-safe RC1 strict-comparison authority.

The frozen RC1 implementation must not be patched in this study. A failure becomes successor-design evidence.
