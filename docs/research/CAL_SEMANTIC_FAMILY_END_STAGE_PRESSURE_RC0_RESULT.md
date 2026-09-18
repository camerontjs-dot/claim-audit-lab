# CAL Semantic Family End-Stage Pressure RC0 — Terminal Result

Date: 2026-09-17

Classification: Draft Research / adversarial post-qualification pressure test.

## Frozen subject

- exact pressure apparatus head: `634267395466c442dec61b0aeb40a92d63176648`
- dedicated run: `35298162665`
- exact subject reconstruction: **PASS**
- frozen apparatus validation: **PASS**
- semantic pressure step: **FAILED**
- pressure report artifact id: `10528751967`
- artifact SHA-256: `1de1ff8374ba78b75ea457baaf696ead262117751abc202ae9e02ab23dfe6698`

## Disposition

**FAILED_END_STAGE_PRESSURE_RC0 — 9 UNAUTHORIZED WARRANTS, LOCALIZED TO 2 FAMILIES.**

The campaign exercised 50 claim surfaces across nine exact frozen family subjects, for 450 family/case observations.

All nine canonical cross-family isolation cases passed: each canonical claim warranted in exactly its permitted family and in no other family.

Forty-one of fifty claim-level expectations passed.

## Strict-comparison counterexamples

The exact strict subject `e085fbc0f74480a81e5b3bd4c11796a6543382e7` issued unauthorized warrants for:

1. `XS01` — `Sector A was never higher than Sector B.`
2. `XS02` — `Sector A appears higher than Sector B.`
3. `XS03` — `Sector A is supposedly higher than Sector B.`
4. `XS04` — `According to QA, Sector A is higher than Sector B.`

The qualified RC1 authority envelope fixed the earlier known modifiers but did not generalize to these unseen forms. The last case also exposes unsafe source-role attachment under an attribution prefix.

## Direct-event-order counterexamples

The exact event-order subject `42fe25bd5a142277bd1903dbe65b7ea57bc94c1a` issued unauthorized warrants for:

1. `XE01` — `Allegedly Talia reviewed packet u before Ravi signed ledger c.`
2. `XE02` — `Reportedly Talia reviewed packet u before Ravi signed ledger c.`
3. `XE03` — `Talia reviewed packet u before Ravi signed ledger c according to QA.`
4. `XE04` — `Talia reviewed packet u before Ravi signed ledger c reportedly.`
5. `XR04` — `QA approved the batch before Ops released it.`

The first four expose incomplete attribution/scope refusal. `XR04` exposes unqualified coreference: the current event parser treats `it` as an ordinary object even though no coreference resolver has been qualified.

## Families with no unauthorized warrant in RC0

- deontic norm;
- population/membership;
- scalar value;
- event occurrence;
- attribute state;
- typed binary relation;
- explicit causal assertion.

Their canonical owner cases also warranted correctly.

## Recombination result

Four of five recombination-boundary claims remained atomic-family silent as intended.

The only recombination leak was `XR04`, through direct event order, due to unqualified pronoun/coreference binding.

No evidence here justifies collapsing spatial or quantitative-change hypotheses. The atomic families simply refused the tested recombination surfaces except for that event-order leak.

## Architecture consequence

The failure is not evidence for a universal parser or model. It localizes two authority-envelope weaknesses:

1. strict comparison needs a more principled positive/source-scope envelope rather than a short lexical denylist;
2. direct event order needs broader attribution-scope detection plus explicit refusal of unresolved coreference.

The other seven authority boundaries survived these fresh attacks.

## Static hygiene note

After the semantic failure, Ruff also reported import-order issues inside the pressure probe harness. That is secondary tooling hygiene and did not cause or alter the semantic failure. Exact-subject reconstruction, apparatus validation, and the pressure observations completed first.

## Next action

Create fresh family-specific authority successors for strict comparison and direct event order. Use RC0 counterexamples as regression requirements, not as fresh validation. After closure, rerun this frozen corpus only as a regression check, then require a **new unseen pressure corpus** before treating the repairs as hardened.

No subject was mutated inside RC0. No merge, production promotion, or release is authorized.
