# CAL RC0A — Exact Entity-Span Anchoring Preregistration

## Class

Draft Research Infrastructure successor to CAL Profile RC0. No production authorization.

## Frozen parent

- RC0 terminal head: `8c52a00b93c7c33c159a484c47944faf9d97f7f1`
- RC0 runtime blob: `b36dacf39d158601368b89df8fa66431ce1b4a07`
- RC0 terminal disposition: `RC0_VERTICAL_INCONCLUSIVE`
- preserved naturalistic counterexample: `Women trailed Men by 11 percentage points.`

The parent is immutable evidence. This experiment does not repair or recount the RC0 smoke.

## Research question

Can an already-proposed strict-comparison entity surface be anchored to one exact source span using lexical boundary constraints, while still refusing genuinely ambiguous duplicate mentions?

This experiment tests mention anchoring only. It does not test generic entity linking, coreference, semantic equivalence, fuzzy matching, retrieval quality, proposition truth, or production behavior.

## Candidate

`unique_lexical_span(text, surface)` may return a span only when:

1. the source substring is an exact codepoint-length case-insensitive match for the proposed surface;
2. the match is not embedded in a larger alphanumeric/underscore token at either material edge; and
3. exactly one eligible lexical match exists.

Otherwise it returns unresolved.

No synonym expansion, fuzzy matching, stemming, lemmatization, model score, confidence, ranking, first-match preference, or caller hint may select a span.

## Weak controls

### W1 — frozen-parent unique substring

The RC0 `_unique_casefold_span` behavior is reproduced as a weak control. It is expected to fail the `Women` / `Men` counterexample because `Men` occurs both standalone and as a substring of `Women`.

### W2 — first lexical match wins

A deliberately weak lexical-boundary resolver returns the first eligible lexical match. It is expected to resolve the original overlap case but to select a span when the same entity appears in two eligible standalone positions. This establishes that boundary filtering alone does not justify arbitrary occurrence selection.

## Preregistered cases

The frozen evaluator covers:

- `Women` / `Men` substring overlap;
- `Woman` / `Man` substring overlap;
- `Russia` / `US` embedded substring trap;
- punctuation-delimited entities;
- possessive mentions;
- mixed casing;
- digit-prefix collision (`Model 2` / `Model 20`);
- letter-prefix collision (`Plan A` / `Plan AB`);
- repeated LHS standalone mention;
- repeated RHS standalone mention;
- token-valid name inside a longer multi-token entity plus a standalone occurrence (`New York` / `York`);
- token-valid organization component plus standalone occurrence (`New York Times` / `Times`);
- Unicode quotation punctuation;
- multiword and hyphenated exact surfaces;
- empty/missing surfaces.

## Hard falsifiers

The candidate is falsified if any of the following occurs:

- an embedded substring is accepted as the target entity;
- more than one eligible lexical occurrence is silently reduced to one;
- a returned span does not slice an exact case-insensitive source surface;
- an empty surface resolves;
- the original `Women` / `Men` counterexample remains unresolved;
- the candidate relies on fuzzy/entity-semantic normalization;
- production `src/**` changes are required.

## Success condition

`SUPPORTED_WITH_BOUNDS` requires all preregistered candidate expectations to match exactly, both weak controls to discriminate as intended, and zero unsafe occurrence selections.

A successful RC0A result only justifies the next bounded RC0B integration regression. It does not authorize the fresh naturalistic smoke or the 24–32 claim audit by itself.
