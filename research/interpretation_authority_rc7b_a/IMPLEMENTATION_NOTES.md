# Implementation Notes

Implementation identity: A

This is a clean-room, standard-library-only receipt producer for Interpretation Authority Contract v1.

## Pre-freeze information aperture

Read exactly:

1. `research/interpretation_authority_rc7b_aperture/INTERPRETATION_AUTHORITY_CONTRACT-v1.md` at `80c2d2f8c96025ea62e8552ecfd4621cd81ea1f4`
2. `research/interpretation_authority_rc7b_aperture/BOOTSTRAP-A.md` at `80c2d2f8c96025ea62e8552ecfd4621cd81ea1f4`

No repository-wide code search, PR/issue search, branch listing, web search, prior research implementation, hidden/sealed evaluator, external model, NLP service, or online parser was used.

## Interpretation strategy

The implementation is deliberately bounded and fail-closed.

- Query `kind` selects the contract family; the query is never used as a source span.
- String values are normalized with NFKC, lowercasing, whitespace collapse, terminal-punctuation trimming, and leading-article removal.
- Established and semantic-unknown fields always carry exact source offsets and an allowed warrant.
- Only-permission handling recognizes direct necessary-condition forms, direct membership/nonmembership statements, explicit permission grants/denials, and explicit unknown assertions.
- Role-binding handling recognizes direct active and passive clauses, preserving semantic roles under passive voice and explicit negation.
- Quantifier handling recognizes the four contract quantifier classes and preserves the source singular/plural surface form for the population field.
- Obvious conditionals, exception systems, probabilistic/modal-only event claims, unsupported quantifiers, percentages/counts, and temporal conditions fail out of jurisdiction.

## Deliberate limitations

This is not a general English parser.

- Only a small rule-based inflection set is used.
- Elaborate word order, long-distance dependencies, coordination, ellipsis, and many paraphrases are not recovered.
- Where contract-family authority plausibly exists but the implemented grammar cannot recover a unique binding, the relevant field(s) return `extraction_unresolved`.
- Mere association or mention returns `insufficient_authority`, never semantic `unknown`.
- No attempt is made to infer synonyms, subclass relations, group/member scope, or unstated permission.

These limitations are preserved rather than tuned away.
