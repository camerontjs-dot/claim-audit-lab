# Contract C RC2-B — Upstream Sufficiency vs CAL Attribution

## Status

Preregistered bounded research experiment. No production change, Contract-B change, Contract-C version, or downstream consumer is authorized.

## Frozen predecessor

Contract C RC2-A remains frozen **FAILED** at CAL PR #16 head `96c55fd4721b66cf138d89f52e262696ba6b6c01`.

Pinned predecessor receipt:

- workflow `33137053355`;
- producer artifact `9672432251`;
- artifact digest `sha256:fd90160ec50f36f65ffd6a26bb1a7e6f1c7f584cb45cc36ee04a903e32f55994`;
- `producer_gate: FAILED`;
- real Contract-B 1.2.0 input recorded factual-context state `absent`.

This experiment does not rerun, repair, or alter RC2-A.

## Production baselines

- CAL semantic production anchor: `33a928db97316a3652d57df9cafb8ca240305233`;
- CAL current main start point: `18592eef336ffc7c2b6b34d8ac489843f5274583` (governance-template-only descendant of the semantic anchor);
- Evidence Bundler production: `c8189c31adbab11729c31430c2070126224a2d42`;
- Apparatus / Contract B production semantic anchor: `c314e53bd91c0736aa4370a364673b069aceb43e`;
- Contract B: `1.2.0`.

## Primary decision

For each RC2-A missing Contract-C obligation, distinguish:

- missing evidence-world state requiring a Contract-B change;
- state already representable in Contract B 1.2 but absent from RC2-A;
- CAL proposition-specific work not performed/retained;
- CAL work that exists but lacks an attributable result receipt;
- an obligation not demonstrated necessary.

The promotion question under test is specifically whether Contract B needs reopening.

## Matched-input falsifier

Construct two fresh valid production Contract-B 1.2 artifacts from the same EB production retrieval output:

1. extension `absent`;
2. extension `present`, attached only through the promoted Contract-B 1.2 factual-context writer.

Hold canonical claims, passages, source payloads, and audit policy fixed. The present extension may contain only legitimate evidence-world facts: claim origin/atomicity, source version/effective-date/status/supplier facts, representation anchors, complete nomination/admission/review history, aperture/search-scope observations/limitations, and explicit known/unknown state.

No proposition-specific support/refutation, semantic validity, applicability, completeness conclusion, decision participation, verdict, or abstention may be added upstream.

Required observations:

- CAL extension-aware intake distinguishes `absent` from `present` and retains the legal factual state;
- core claim/evidence inputs remain semantically identical;
- run the same production v0.2 audit computation on both artifacts;
- compare complete `ClaimAssessment` outputs;
- record whether any missing RC2-A assessment/result becomes performed or attributable solely because the legal extension is present;
- verify aperture observations remain observations rather than a completeness conclusion.

## Falsifiers

`Contract B must be expanded` is falsified for an obligation if 1.2 already represents the required evidence-world facts and the remaining distinction is CAL semantic work or result lifecycle.

`CAL already has everything and merely fails to expose it` is falsified if the relevant operation is not performed even when legal upstream facts are present.

A Contract-C obligation is weakened or falsified if prior RC1/RC2 tests did not demonstrate any downstream semantic distinction that depends on it.

## Hard stops

Do not change Contract B, production CAL, a Contract-C schema/version, Decision Engine behavior, or Consumer B. Do not materialize missing semantic judgments in a research wrapper.
