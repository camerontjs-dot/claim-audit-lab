# CAL Strict Comparison Modifier Eligibility Gate RC0 — Terminal Result

Date: 2026-09-17

Classification: Draft Research / successor experiment after PR #141.

## Frozen candidate

- parent RC1: `a902621e8baea3063dddd7f92ba975aade305464`
- exact pre-cohort candidate head: `71e4fd38ce03463116b889408970aa27c13616e4`
- candidate blob: `b944af74d7b4fa96953d3e727f97ab317ac004aa`
- candidate-freeze run: `35294741032` — PASS
- fresh cohort execution head: `6e09a6b94581f00ce8463f2f7de7cebfb499e6e0`
- fresh pressure run: `35294828063`

Candidate code was not changed after fresh cohort reveal.

## Disposition

**FALSIFIED_LEXICAL_MODIFIER_GATE.**

The lexical eligibility strategy closed the six revealed PR #141 failure strings but did not generalize to structurally different unseen modifiers.

## Positive controls

Fresh direct controls had zero failures:

- `remained higher than`
- `substantially higher than`
- `stayed lower than` -> expected contradiction
- `notably higher than`

The candidate therefore was not vacuously rejecting all comparison language.

## Fresh unsafe deciding cases

Seven fresh modifier/scope cases reached deciding conclusions:

- `SCG-U01`: `is believed to be higher than`
- `SCG-U02`: `is thought to be higher than`
- `SCG-U03`: `should be higher than`
- `SCG-U04`: `must be higher than`
- `SCG-U05`: `can be higher than`
- `SCG-U06`: `is conceivably higher than`
- `SCG-U07`: `is expected to be higher than`

The candidate correctly rejected `is said to be`, contraction negation, and `only if`.

## Interpretation

A negative lexical inventory is not a robust semantic-jurisdiction boundary. Open-ended modifier vocabularies create an endless blacklist problem.

The evidence now favors the inverse architecture:

> define a positively bounded direct-assertion grammar and admit only text that fully matches that grammar.

This turns unknown modifier constructions into safe abstention by construction instead of trying to enumerate every unsafe word.

## Smallest successor

Freeze a **structural direct-comparison assertion grammar** before another fresh cohort. It should positively admit only explicit bounded surfaces such as:

- direct copular/state comparison;
- explicit measure-head comparison;
- explicit `exceeded` / `trailed`;
- bounded numeric-delta comparison.

Unrecognized wrappers/modifiers remain ineligible even if RC1's raw measurement happens to emit a comparison proposal.

The RC0 fresh failures become development evidence only. A new fresh cohort is required.

## Non-claims

No production change, merge, release, or final strict-comparison family authorization follows from RC0.
