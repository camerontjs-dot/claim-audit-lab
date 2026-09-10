# Temporal Contract C → Maintained Decision Engine RC0 — Results

## Classification

Draft Research Infrastructure / downstream consumer conformance evidence record.

This record changes neither Contract C nor Decision Engine semantics. It performs no Contract E Authorization, external mutation, merge, release, tag, or production promotion.

## Exact scientific inputs

- bound temporal successor freeze: `10ce0894a56f265434b24963bf0543765c453996`
- `bound_relation.py` blob: `94b44f3b0b2b3f077c17ca55eb944117ffa22b77`
- `bound_projection.py` blob: `77fed3e7a7273b13e6dfb89e0ffee7fce1503c6c`
- bound successor decisive run: `34434782626`
- bound successor artifact: `10135769621`
- bound successor artifact digest: `sha256:4667d7c9328d034f32e92822229f625f8d15acba45dfc51257270b148826f67c`
- Contract C 1.0 authority: `5fe55f9ed5d0ee9f026ca1b077e9d70ce0487ea1`
- Contract C validator blob: `9c75ccfbf2223578a8d1a7bf0c39673b394fbea4`
- maintained Decision Engine exact head: `358c2bb20f490bf25e808434394b26a70a16a123`
- Decision CLI blob: `b3808a536ca5f976ca1022c7c9f13a229d31af79`
- Contract C ingress blob: `f57a8067dadc04afb459f1d0342b2b786ec775e6`
- supported-claim policy blob: `3529b75f75936fffb9b2d9e2972cb7117b526661`
- runtime dispatch blob: `7020006a350f78b0381df3309f8085966890a049`
- Contract D canonicalizer blob: `0ea61767b9ae61b3b80c0c2f26de4292f213b7fb`
- Contract D 1.0 authority: `298a1a0f7b7b6d7712e11200d04faec3e1ca169b`

## Preserved first execution: broad label is not final semantic evidence

Run `34435011700` completed the research harness and emitted `FALSIFIED_TEMPORAL_DECISION_CONFORMANCE` because all four positive Decision cases and the producer-policy metadata invariance control failed.

- artifact id: `10135845365`
- artifact digest: `sha256:e61fca1e4cf741888213a69a9014fa87cc69d61db2e14916aa13f4955e2d0ecd`

That broad scientific label is preserved as an evaluator output, but it is **not the final semantic disposition**. The all-cases failure pattern was subsequently localized to a shared apparatus dependency failure before Decision semantics could be validly evaluated.

## Refusal diagnostic

Run `34435197788` replayed the positive inputs without changing semantic inputs and captured the exact refusal boundary.

- artifact id: `10135905899`
- artifact digest: `sha256:d15209604b3eb4e044af5a5a4059f4cdbfb5adb396a009899f4cca429ceb191c`
- all positive inputs refused: `true`
- semantic inputs changed: `false`

Every positive case failed at Contract D validation with the same root cause:

`ModuleNotFoundError: No module named 'rfc8785'`

The released Contract D authority package declares `rfc8785==0.1.4`. The conformance workflow had installed the exact Contract C authority package but had not installed the exact Contract D authority package. Contract C whole-object hashes matched their expected values in the diagnostic.

This is an apparatus/environment failure, not evidence that the temporal semantic family is incompatible with the maintained Decision policy.

## Smallest apparatus correction

Commit `ca3346747aa4eb9253dd61e0be31e798b17d538d` changed only the workflow environment so the exact checked-out Contract D authority package is installed in addition to Contract C.

No change was made to:

- bound temporal relation semantics;
- bound temporal Contract C projection;
- the preregistered cohort;
- the Decision conformance evaluator;
- Contract C 1.0;
- Decision Engine code or policy;
- Contract D 1.0.

The corrected install pulled the authority-declared `rfc8785==0.1.4` dependency.

## Corrected decisive execution

Run `34504243114`: apparatus PASS and scientific cohort PASS.

- exact run head: `ca3346747aa4eb9253dd61e0be31e798b17d538d`
- artifact id: `10163138696`
- artifact digest: `sha256:664195940a5ad23d3ae93709058566dbe093321481e0eed229f74b2a994114f8`
- research disposition: `SUPPORTED_WITH_BOUNDS_AND_UPSTREAM_PROVENANCE_GAP`

Terminal summary:

```json
{
  "falsifier_failures": [],
  "mixed_hold": true,
  "policy_metadata_invariant": true,
  "positive_failures": [],
  "refute_hold": true,
  "research_disposition": "SUPPORTED_WITH_BOUNDS_AND_UPSTREAM_PROVENANCE_GAP",
  "support_clear": true,
  "unresolved_hold": true
}
```

## OBSERVED

Using exact released Contract C and Contract D authorities and exact Decision Engine head `358c2bb...`:

- temporal `supported` with `completion=assessed` produced Decision `clear` with reason `contract_c_supported`;
- temporal `contradicted` with `completion=assessed` produced Decision `hold` with reason `contract_c_reported_verdict_not_supported`;
- same-world temporal support/refute conflict projected as `not_checkable` and produced Decision `hold` with reason `contract_c_proposition_not_checkable`;
- unresolved negative-event temporal state projected as `not_checkable` and produced the same safe hold reason;
- all preregistered Decision falsifiers passed;
- changing only valid producer-owned policy metadata, with hashes and result-set identity recomputed, did not change the Decision disposition/reason/effect;
- exact Contract D canonicalization/validation passed for the successful Decision cases;
- no Contract E call, operational Authorization, or external mutation occurred.

## INFERENCE

Within this bounded temporal terminal-state cohort, the maintained `decision-engine.contract-c.supported-claim-verification@1.0.0` consumer behaves as a Contract-C-state policy rather than a hidden strict-comparison-family policy.

The corrected evidence does **not** support the earlier interpretation that temporal outputs were rejected by Decision semantics. The earlier all-cases failure is better explained, and directly reproduced, by the missing released Contract D dependency.

## Remaining upstream provenance gap

The bound temporal successor still preserves a real Contract C 1.0 compression boundary.

A warranted temporal relation classified `UNRESOLVED` or `IRRELEVANT` cannot be truthfully emitted as a Contract C evidence contribution because Contract C 1.0 contribution channels are only `support` and `counterevidence`. The bound projector therefore preserves the not-checkable terminal state with a typed `state:` basis and records the omitted temporal relation in the research receipt rather than laundering it into an incorrect contribution channel.

Decision conformance does not close that upstream information-loss question. It only establishes that the resulting valid Contract C terminal state is consumable by the tested maintained Decision policy.

## NOT ESTABLISHED

- arbitrary temporal language;
- negative-event deciding semantics;
- cross-passage temporal inference or transitivity;
- event coreference;
- evidence completeness;
- lossless Contract C representation of unresolved/irrelevant evidence provenance;
- root / `all_of` CAL composition;
- Contract E or operational Authorization;
- production authentication/key management;
- production CAL architecture;
- merge, release, tag, or promotion.

## Next discriminating question

Before proposing a Contract C change, test whether an independent consumer given only canonical Contract C plus its bound Contract B can reconstruct **which admitted evidence caused an unresolved/irrelevant not-checkable result**, rather than merely distinguish the terminal reason category.

If two different unresolved evidence worlds are distinguishable only through producer-private or research sidecar state, that is stronger evidence of a Contract C information-sufficiency gap. If the existing Contract C + Contract B pair is sufficient, no schema change is justified.
