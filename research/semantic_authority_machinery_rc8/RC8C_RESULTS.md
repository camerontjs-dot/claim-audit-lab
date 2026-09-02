# RC8C Admitted-Evidence Source Anchor Falsifier — Results

## Disposition

**FALSIFIED.** The frozen RC8B candidate is an internally consistent bound-receipt gate, but it is not sufficient as an evidence-to-authority binding gate because it does not bind its authority subject to the admitted `raw_source_id`.

RC8B remains frozen and its earlier partial-receipt consistency result remains valid within that narrower claim.

## Frozen identities

- preregistration: `2f5bc984db1ebe691b91462c6d497b3420e59c5d`
- parent RC8B freeze: `e52f70b77ed0395e33afa9b193cae47475abf892`
- RC8B candidate blob: `edf84bb5aae0dd217e3f780e7a49767440b7c1e5`
- RC8C apparatus freeze head: `2600d79f7224498692ac565f39a971a9e8c6ca38`
- pre-reveal run: `33651406186`
- pre-reveal job: `100319050487`
- reveal workflow commit: `f672d93450ac7adc426516ef397901f744a94ba5`
- reveal run: `33651630044`
- reveal job: `100319905772`
- artifact: `9855007368`
- artifact digest: `sha256:e7d395ce577cc1720627388d3f0d70d8f2d8146123aafa87ef1643ffdc0d8583`

The reveal reverified candidate and apparatus identities, executed the evaluator, uploaded the result, and then failed the hard safety criterion.

## Exact result

- cases: `3`
- status exact: `1 / 3`
- reason exact: `1 / 3`
- unsafe warranted atoms: `2`
- scientific state: `RC8B_FALSIFIED_BY_MISSING_EVIDENCE_SOURCE_ANCHOR`

| Case | Mutation | Expected | Observed |
|---|---|---|---|
| `C-ANCHOR-POSITIVE` | unchanged admitted source and receipt bundle | `WARRANTED` | `WARRANTED` |
| `C-ANCHOR-SOURCE-SUBSTITUTED` | only `raw_source_id` changed A → B | `REJECTED` | `WARRANTED` |
| `C-ANCHOR-SOURCE-MISSING` | `raw_source_id` removed while evidence remains admitted | `UNRESOLVED` | `WARRANTED` |

## Causal interpretation

The semantic proposal, authority-subject bundle, field warrants, operator jurisdiction, spans, composition/aperture state, instruments, and reader count were held fixed. Only the admitted evidence identity was changed or removed.

Therefore the failure localizes to absence of a source-anchor invariant. It does not support adding confidence, reader agreement, or instrument agreement, and it does not negate RC8B's demonstrated ability to reject partial receipt-fragment substitution.

## Successor constraint

A successor may add only the smallest explicit link between the authority subject and admitted evidence source. A suitable typed surface is an `authority_subject_source_id` that must equal `raw_source_id` after execution/evidence-admission precedence is resolved.

- missing source identity or missing subject-source anchor: `UNRESOLVED / AUTHORITY_EVIDENCE_SOURCE_BINDING_UNRESOLVED`
- explicit source mismatch: `REJECTED / AUTHORITY_EVIDENCE_SOURCE_MISMATCH`
- otherwise preserve the frozen RC8B transition unchanged.

This does not claim cryptographic authenticity or protect against an actor that can rewrite every provenance field consistently.
