# Implementation Notes — RC7B Interpretation Authority B

## Information aperture

This implementation was authored from only:

- `research/interpretation_authority_rc7b_aperture/INTERPRETATION_AUTHORITY_CONTRACT-v1.md`
- `research/interpretation_authority_rc7b_aperture/BOOTSTRAP-B.md`

at aperture head `80c2d2f8c96025ea62e8552ecfd4621cd81ea1f4`.

No other repository source, prior implementation, evaluator material, corpus, PR discussion, issue, branch listing, code search, web source, external parser, or model API was used before freeze.

## Implementation posture

The implementation is a conservative standard-library extractor. The structured query selects the semantic family and target proposition, but established semantic values are emitted only when matching source language supplies an allowed warrant and an exact source span.

The implementation keeps these states distinct:

- `semantic_unknown`: only an explicit source assertion that membership or permission is unknown;
- `insufficient_authority`: the source does not warrant the field;
- `extraction_unresolved`: the source appears to contain an in-family construction but the conservative extractor does not recover a unique supported value.

Unsupported numeric/proportional language, probabilities, conditionals, exceptions, alternatives, and selected temporal/modal compositions are rejected as out of jurisdiction.

## Known limitations and independent choices

- Recognition is construction-based and intentionally incomplete. It does not attempt arbitrary-English parsing.
- Morphology support is deliberately small and regular-rule based. Irregular verb inflection is not comprehensively handled.
- For quantifiers such as `each technician` when the structured population is plural (`technicians`), the implementation treats the grammatical singular realization as source authority for the queried population and emits the normalized query population. This is a bounded constructional choice, not general singular/plural equivalence.
- Role binding recognizes direct active/passive forms. If all target ingredients occur in an apparent event clause but the binding pattern is not recovered, the role fields abstain as `extraction_unresolved`.
- Mere co-mention without a recovered binding relation remains `insufficient_authority`.
- Unsupported-composition detection is intentionally conservative and may abstain or reject constructions beyond the public sentinels rather than invent semantics.
- Contradictory recoverable values for one field are not resolved by policy; the field becomes `extraction_unresolved`.

No attempt was made to optimize for or infer hidden evaluator cases.
