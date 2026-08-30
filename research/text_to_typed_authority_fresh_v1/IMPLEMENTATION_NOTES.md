# Fresh Text-to-Typed-Authority Reproduction v1 — Implementation Notes

## Clean-room aperture

Pre-freeze semantic inputs read by this implementation were limited to:

1. `research/text_to_typed_authority_fresh_v1_aperture/BOOTSTRAP.md` at `213c6af2b11cfc5d0673c715d2a2385bed0a9f44`;
2. `research/text_to_typed_authority_fresh_v1_aperture/EXTRACTION_CONTRACT-v1.md` at `213c6af2b11cfc5d0673c715d2a2385bed0a9f44`.

No prior extractor, corpus, evaluator, reveal material, downstream semantic consumer, prior PR discussion, historical research branch, repository-wide search, or web search was used.

## Implementation posture

The extractor is a bounded deterministic grammar implemented with Python 3.11 standard-library regular expressions and small normalization helpers. It attempts the seven contract dimensions in a fixed order and returns a resolved object only when one supported parse is recovered. Multiple distinct supported parses fail closed as `ambiguous_reference`.

The implementation does not compute entailment/neutral/contradiction labels and contains no case IDs, hashes, exact-sentence lookup table, expected results, or evaluator-specific arguments.

## Normalization choices

- Surrounding punctuation and repeated whitespace are removed from extracted lexical spans.
- Population comparison uses a small singular/plural normalization only to match semantically corresponding class labels across text and query.
- `subclass` canonicalization lowercases class labels through the comparison normalization, sorts the two class keys lexicographically, and maps them to `A`/`B` exactly as required by the contract.
- Simple verb inflections are normalized by a small deterministic lemmatization heuristic; passive and active binary events map to ordered semantic subject/object roles.
- Any named temporal boundary recovered by the bounded temporal grammar is emitted as literal `cutoff`.

## Supported bounded constructions

The implementation covers direct declarative/question forms for:

- explicit entity membership/non-membership/unknown plus a generic factual or obligation population rule;
- one directed subclass inclusion plus one entity membership state;
- `only C may P` necessary-condition permission with optional explicit membership and permission/denial;
- `every`, `none`, `some`, and `not_every` quantified propositions;
- group-scope versus one named-member event scope;
- binary active/passive role binding with positive/negative polarity;
- before/after temporal membership expressed either as one `only before/after` sentence or paired before/after facts, plus one population rule.

## Deliberate limitations and abstentions

These are preserved as implementation limitations rather than repaired by guessing:

- The grammar is not a general English parser. Unrecognized but plausibly in-contract wording returns `unparsed` or, when the text is in-domain but lacks the authority required by the query, `insufficient_authority`.
- Multiword named entities are only partially supported in event-role grammars; some such inputs will abstain.
- Verb normalization is intentionally small and heuristic. Irregular or derivational morphology outside the embedded bounded table may abstain or fail to match.
- Quantifier population/predicate splitting is deliberately conservative and optimized for simple population-plus-predicate clauses, not arbitrary noun phrases.
- Pronouns with multiple named antecedent candidates are conservatively classified `ambiguous_reference`; this may abstain on cases that a broader discourse resolver could settle.
- Conditional, exception, probabilistic, numeric/proportional, comparative, and nested alternative constructions are classified `ontology_escape` when recognized. The extractor does not force them into the nearest supported dimension.
- The implementation does not infer membership from training, work association, application, intention, capability, or proximity language.
- The implementation does not infer permission from membership under an `only C may P` rule.
- Group events and named-member events are kept distinct.
- Directed subclass edges are not reversed, and no downstream semantic conclusion is computed inside extraction.

## Sentinel provenance

`test_contract_sentinels.py` was authored solely from the two authorized pre-freeze files. Its examples are synthetic contract exercises, not copied or inferred evaluator cases.
