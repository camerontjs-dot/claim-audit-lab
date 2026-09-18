# CAL Strict Comparison Structural Eligibility Gate RC1 — Preregistration

Date: 2026-09-17

Classification: Draft Research / successor to falsified lexical gate RC0.

## Parent evidence

- CAL V1 RC1 semantic implementation: `a902621e8baea3063dddd7f92ba975aade305464`
- raw modifier-loss pressure: PR #141
- lexical modifier-gate falsification: PR #144

Production `src/` remains unchanged.

## Hypothesis

Strict-comparison warrant eligibility should be defined by a **positive structural grammar**, not by enumerating prohibited modifier words.

Only passages that fully match one of a small set of direct narrator-level comparison forms may proceed to the frozen RC1 authority path. Unknown wrappers, auxiliaries, attribution structures, conditionals, and modifier phrases are ineligible by default.

## Bounded eligible forms

RC1 tests four forms:

1. direct copular/state comparison:
   `ENTITY (is|was|remained|stayed) [degree] REL than ENTITY`;
2. explicit measure-head comparison:
   `ENTITY (recorded|showed|had) [a] [degree] REL MEASURE than ENTITY`;
3. explicit comparative verb:
   `ENTITY (exceeded|trailed) ENTITY [by DELTA]`;
4. bounded numeric-delta form:
   `ENTITY (processed|recorded|produced|counted|handled) VALUE, DELTA (more|fewer|less) than ENTITY`.

Degree modifiers are a small positive allowlist that preserve comparison sign.

Everything outside those structural forms remains proposal-only and cannot reach warrant through this candidate.

## Development evidence

All revealed PR #141 and PR #144 unsafe strings may be used only as development controls.

A fresh pressure cohort must be added after candidate freeze and must include unseen positive paraphrases plus unseen unsafe wrappers/modifiers.

## Hard conditions

Fresh pressure passes only if:

- every fresh direct positive control yields its expected supported/contradicted conclusion;
- every fresh unsafe surface yields `NOT_CHECKABLE`;
- production `src/` and frozen parent RC1 remain unchanged.

No post-reveal candidate repair is permitted inside RC1.
