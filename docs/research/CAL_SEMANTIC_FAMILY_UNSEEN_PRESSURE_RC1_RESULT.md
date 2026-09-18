# CAL Semantic Family Unseen Pressure RC1 — Terminal Result

Date: 2026-09-17

Classification: Draft Research / fresh post-repair adversarial pressure test.

## Frozen subject

- exact unseen-pressure apparatus head: `e0b4a6394b77ecd0662b0449056acea121ecbd4a`
- dedicated run: `35299285839`
- frozen apparatus validation: **PASS**
- exact reconstruction of all nine subject SHAs: **PASS**
- unseen semantic pressure: **FAILED**
- static checks: **PASS**
- pressure report artifact id: `10529143100`
- artifact SHA-256: `4cd3ac6fabf6d7a97afda9906be5e65999139b5ee76c0135ce0e3ccf64b1ab89`

## Disposition

**FAILED_UNSEEN_PRESSURE_RC1 — 1 UNAUTHORIZED WARRANT, LOCALIZED TO DIRECT EVENT ORDER.**

The campaign exercised 64 claim surfaces across nine exact frozen family subjects, for 576 family/case observations.

All nine canonical cross-family owner cases passed.

Sixty-three of sixty-four claim-level expectations passed.

## Fresh counterexample

`UE05`:

```
She reviewed packet u before Ravi signed ledger c.
```

Expected atomic-family warrants: none.

Observed warrant:
- `direct_event_order`

The exact event-order RC2 subject was:
`2c9369144fecb3025bf28885ab6e322d895c3dbf`.

## Interpretation

RC2 correctly closed unresolved **object** coreference, including pronoun objects such as `it` and `that`, but its source completer did not reject unresolved **subject** pronouns.

The event parser accepted `She` as an ordinary capitalized subject and therefore issued a warrant without an independently qualified coreference resolution step.

This is a fresh generalization failure, not a replay of an RC0 failure.

## Surviving evidence

No unauthorized warrant was observed from:

- strict comparison RC2;
- deontic norm;
- population/membership;
- scalar value;
- event occurrence;
- attribute state;
- typed binary relation;
- explicit causal assertion.

Strict comparison RC2 survived the fresh belief/reporting/modifier surfaces in this corpus.

Direct event order RC2 also survived the new attribution tails, object-pronoun attacks, and other fresh event-order cases except `UE05`.

## Architecture consequence

The event-order authority boundary should treat unresolved coreference as an **argument-level property**, not merely an object-string property.

The smallest justified successor is to refuse unresolved pronouns in any event argument position consumed as semantic identity, unless a separately qualified coreference resolver establishes the referent.

No evidence supports adding a coreference resolver inside this bounded authority repair.

## Next action

Create a fresh direct-event-order authority RC3 from the exact RC2 candidate.

Use `UE05` as a regression requirement, alongside the earlier RC1/RC2 regressions. Do not alter the measurement or relation algebra.

After RC3 regression closure:
1. rerun this exact 64-case corpus as regression only;
2. require a third unseen pressure set with fresh subject/object/reflexive/demonstrative coreference surfaces before treating RC3 as hardened.

No subject was patched inside this pressure PR. No merge, production promotion, or release is authorized.
