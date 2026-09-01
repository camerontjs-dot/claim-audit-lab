# RC7F-C Explicit Event-to-Event Ordering — Terminal Evidence

Status: **TERMINAL RESEARCH EVIDENCE**

Terminal token:

`EVENT_ORDERING_INSTRUMENT_CANDIDATE_READY_FOR_HARDENING`

## Immutable lineage

- parent RC7E evidence: `34e9bcafad2c63c9b0761ffc456532344bc75b88`
- preregistration: `ca67c80a996a6e494f950d38b0af109d42a0da14`
- apparatus freeze: `9e172ebd221301b6a4513ead2c15cc4095e55ea4`
- qualification run: `33464603028`
- qualification artifact: `9784390823`
- qualification digest: `sha256:8d5be9cd09493b5e2f489a232e619007b040e4ccb7c8e85796d25e2315e590f3`
- held-out cohort freeze: `4ced5d9b2e5a784529431e2bd440549be41e0b18`
- accepted scientific run: `33464936862`
- scientific artifact: `9784497429`
- artifact ZIP digest: `sha256:e1707378d0b815d6773951b18744aee8b2fb3246175d4f4ff7f127f5c993bcbd`

The production `src/` guard passed. Candidate code was not changed after held-out creation.

## Scientific result

Accepted result over 60 cases, including 44 supported explicit event-order cases and 16 negative/unsupported controls:

- true positives: `44`
- false proposals: `0`
- misses: `0`
- typed precision: `1.000000`
- typed recall: `1.000000`
- relation-direction accuracy: `1.000000`
- left/right event attachment accuracy: `1.000000`
- event-polarity accuracy: `1.000000`
- false proposals on negative/unsupported controls: `0`
- meaning-changing before/after pair accuracy: `1.000000`

## Supported bounded observation jurisdiction

Only explicit two-event `before` / `after` constructions using the frozen event vocabulary, including positive and negative event polarity.

This result does not establish:

- implicit narrative chronology;
- `prior to` / `following` or arbitrary temporal paraphrases;
- timestamp normalization;
- duration or interval reasoning;
- causal ordering;
- calendar arithmetic.

Those forms remain outside this candidate rather than being guessed.

## Interpretation

RC7E directly observed `0/4` tested event-ordering dimensions. RC7F-C establishes that the narrow explicit `before/after` gap can be filled with small non-LLM machinery without false proposals on the frozen controls.

That result is a candidate for hardening, not authority to assert arbitrary chronology.

## Design principle preserved

> **CAL may know that it observed something without claiming that it knows the thing is true. When warrant is incomplete, abstention is a successful outcome.**

The instrument measures an ordering relation. A separate semantic-warrant step remains required before CAL may promote that observation to an asserted proposition.

## Nonclaims

No production CAL behavior, semantic-warrant promotion, operational authorization, universal temporal ontology, release, or merge is authorized by this research result.
