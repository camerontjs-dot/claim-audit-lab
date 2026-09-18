# CAL Semantic Family Unseen Pressure Regression RC2 — Preregistration

Date: 2026-09-17

Classification: Draft Research / exact-corpus regression confirmation.

## Purpose

Re-run the exact frozen 64-case unseen-pressure RC1 corpus against direct-event-order RC3 while leaving the other eight exact family subjects unchanged.

This is not new hardening evidence.

## Frozen corpus

- path: `research/semantic_family_unseen_pressure_rc1/cases.json`
- frozen blob SHA: `02aa68faf8d7344b41d0b5e95010569b9511e33a`
- original unseen-pressure run: `35299285839`

No case or allowlist mutation is permitted.

## Subject change

Only direct event order changes:

- prior subject: `2c9369144fecb3025bf28885ab6e322d895c3dbf`
- RC3 subject: `b163f0faf58c8fe7e2c74e8d9e8618aa2147a359`
- RC3 qualification run: `35299574593`

The other eight exact subject SHAs remain unchanged.

## Acceptance

All 64 claim-level expectations must pass, including the prior fresh counterexample `UE05`, with zero probe errors and exact subject reconstruction.

A pass establishes only regression closure. A third unseen pressure corpus is still required.
