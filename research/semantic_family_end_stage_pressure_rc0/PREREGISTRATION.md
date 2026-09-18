# CAL Semantic Family Pressure Regression RC1 — Preregistration

Date: 2026-09-17

Classification: Draft Research / known-corpus regression confirmation.

## Purpose

Re-run the exact frozen end-stage pressure RC0 corpus against the two repaired authority successors while leaving the other seven qualified family subjects unchanged.

This is **not fresh hardening evidence**. The repaired strict-comparison and direct-event-order candidates were designed with the RC0 failures in view.

## Frozen corpus

The pressure cases are byte-identical to RC0.

- path: `research/semantic_family_end_stage_pressure_rc0/cases.json`
- frozen blob SHA: `b6f87e66004a7b8bed52412dc9f3dd38dd9f1e78`
- original pressure run: `35298162665`

No case additions, deletions, edits, or allowlist changes are permitted in RC1.

## Subject changes from RC0

Only two subjects change:

- strict comparison -> exact RC2 qualified candidate `33cf39b1b2fabae2c867187bc097da396ffd7014`;
- direct event order -> exact RC2 qualified candidate `2c9369144fecb3025bf28885ab6e322d895c3dbf`.

The other seven exact subject SHAs remain identical to RC0.

## Acceptance

Regression closure requires:

- exact reconstruction of all nine subject SHAs;
- all nine canonical owner cases still warrant in exactly one family;
- every RC0 noncanonical pressure case produces zero atomic-family warrants;
- zero probe errors;
- the frozen cases blob remains unchanged.

A pass shows only that the known RC0 counterexamples are closed without breaking the earlier cross-family isolation result.

A new unseen pressure corpus is required immediately afterward.
