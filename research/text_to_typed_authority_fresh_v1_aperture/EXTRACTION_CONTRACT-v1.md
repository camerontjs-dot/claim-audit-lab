# Text-to-Typed-Authority Extraction Contract v1

## Purpose

This is the complete semantic contract available to the fresh extractor before implementation freeze.

The extractor does not decide whether the downstream semantic relation is entailment, neutral, or contradiction. It reconstructs a typed authority object and typed query when the supplied text warrants exactly one supported representation. Otherwise it returns extraction `unknown`.

## API

Implement:

```python
def extract(text: str, query_text: str) -> dict:
    ...
```

Allowed return shapes:

```json
{
  "status": "resolved",
  "case": {
    "dimension": "<dimension>",
    "authority": { "...": "..." },
    "query": { "...": "..." }
  }
}
```

or:

```json
{
  "status": "unknown",
  "reason": "ambiguous_reference | insufficient_authority | ontology_escape | unparsed"
}
```

`unparsed` means the construction appears to belong to this contract but the implementation cannot recover one typed object. It is a safe implementation abstention, not a claim that the language is outside semantic jurisdiction.

## Global rules

1. Preserve entity, population/class, predicate, role, scope, polarity, modality, quantifier, and temporal distinctions exactly when they are authority-relevant.
2. Do not infer membership from proximity, training, job association, intention, capability, application, or other merely suggestive language.
3. Absence of a fact is not its negation.
4. `unknown` membership is not `non_member`.
5. A resolved semantic case may later evaluate to semantic `neutral`; do not convert a recoverable typed object into extraction unknown merely because the downstream relation might be neutral.
6. If a pronoun/reference admits more than one materially different authority object, return `ambiguous_reference`.
7. If the language concerns the domain but does not establish the authority required by the query, return `insufficient_authority`.
8. If the construction requires semantics outside the dimensions below, return `ontology_escape`. Examples include numeric/proportional thresholds, probability, conditional antecedents, exception systems, nested Boolean alternatives, and other authority not representable by this contract.
9. Do not invent fields or force unsupported language into the nearest dimension.
10. Strings representing entities, populations, predicates, and group-member identities should preserve the semantic content of the text/query in normalized lowercase only where stated below. Otherwise preserve the surface lexical name without punctuation.

## Dimension 1: `membership_rule`

Use when the text supplies an entity's membership status in a population plus a population-level rule.

Authority:

```json
{
  "entity": "<entity>",
  "population": "<population>",
  "membership": "member | non_member | unknown",
  "rule": {
    "population": "<population>",
    "predicate": "<predicate>",
    "modality": "fact | obligation",
    "polarity": "positive | negative"
  }
}
```

Query:

```json
{
  "kind": "membership | rule_applies | behavior_positive | behavior_negative",
  "entity": "<entity>",
  "population": "<population>",
  "predicate": "<predicate>"
}
```

Interpret ordinary present-tense generic factual assertions such as “navigators record arrivals” as `modality="fact"`. Normative language such as “must”, “shall”, or “are required to” is `obligation`.

## Dimension 2: `subclass`

Use for one directed subclass relation between two classes plus one entity's membership/non-membership/unknown status in one of those classes.

Authority:

```json
{
  "entity": "<entity>",
  "membership_population": "A | B",
  "membership": "member | non_member | unknown",
  "subclass_edge": "A_sub_B | B_sub_A | none"
}
```

Query:

```json
{
  "kind": "membership",
  "entity": "<same entity>",
  "population": "A | B"
}
```

Canonicalization is mandatory. Take the two relevant class labels, lowercase and strip surrounding punctuation, sort them lexicographically, and map the first to `A`, the second to `B`. Map both the authority membership class and query class through that same mapping.

Directed subclass semantics matter. `A_sub_B` means every A is B. Do not assume the converse. Negative membership inherits only by valid contrapositive of the inclusion: if `A_sub_B` and the entity is known `non_member` of B, that supports non-membership in A. Do not invent the invalid converse directions.

`none` is allowed only when the text explicitly establishes that no subclass edge is being asserted for the two classes.

## Dimension 3: `only_permission`

Use for necessary-condition permission statements of the form “only members of population C may perform P”, optionally combined with explicit membership and/or explicit grant/denial for one entity.

Authority:

```json
{
  "entity": "<entity>",
  "population": "<population>",
  "membership": "member | non_member | unknown",
  "predicate": "<predicate>",
  "only_population_may": true,
  "explicit_permission": "permitted | not_permitted | unknown"
}
```

Query:

```json
{
  "kind": "membership | permission",
  "entity": "<entity>",
  "population": "<population>",
  "predicate": "<predicate>"
}
```

“Only C may P” makes C-membership a necessary condition for permission. It does not by itself grant permission to every C member.

## Dimension 4: `quantifier`

Use for a single population-level quantified factual proposition.

Authority:

```json
{
  "population": "<population>",
  "predicate": "<predicate>",
  "quantifier": "every | none | some | not_every",
  "polarity": "positive"
}
```

Query:

```json
{
  "kind": "quantified",
  "population": "<population>",
  "predicate": "<predicate>",
  "quantifier": "every | none | some | not_every",
  "polarity": "positive"
}
```

Normalize:
- every / all -> `every`
- no / none -> `none`
- some / at least one -> `some`
- not every / not all / “it is false that every ...” -> `not_every`

Do not convert percentages, exact counts, most, many, few, probability, or comparative quantifiers into these four values.

## Dimension 5: `group_scope`

Use when the same event predicate is asserted at group scope or at the scope of one named group member.

Authority:

```json
{
  "event_scope": "group | member:<entity>",
  "predicate": "<predicate>",
  "polarity": "positive | negative"
}
```

Query:

```json
{
  "kind": "event",
  "event_scope": "group | member:<entity>",
  "predicate": "<predicate>",
  "polarity": "positive | negative"
}
```

A group event is not automatically a named-member event, and a named-member event is not automatically a group event.

## Dimension 6: `role_binding`

Use for a binary event with ordered subject/object roles.

Authority:

```json
{
  "event": {
    "predicate": "<base predicate>",
    "roles": {
      "subject": "<entity>",
      "object": "<entity>"
    },
    "polarity": "positive | negative"
  }
}
```

Query:

```json
{
  "kind": "event",
  "predicate": "<base predicate>",
  "roles": {
    "subject": "<entity>",
    "object": "<entity>"
  },
  "polarity": "positive | negative"
}
```

Active and passive paraphrases must preserve the same semantic roles. Normalize simple inflected verbs to the base lexical predicate used by the text/query when mechanically clear, e.g. `reviews/reviewed` -> `review`, `approves/approved` -> `approve`.

## Dimension 7: `temporal_membership`

Use for membership that is explicitly scoped relative to one named boundary and an associated population rule.

Authority:

```json
{
  "entity": "<entity>",
  "population": "<population>",
  "membership_window": "before_only | after_only | always | never | unknown",
  "boundary": "cutoff",
  "rule": {
    "population": "<population>",
    "predicate": "<predicate>",
    "modality": "fact | obligation",
    "polarity": "positive | negative"
  }
}
```

Query:

```json
{
  "kind": "membership | rule_applies | behavior_positive | behavior_negative",
  "entity": "<entity>",
  "population": "<population>",
  "predicate": "<predicate>",
  "time": "before | after"
}
```

For this bounded contract, normalize the single temporal boundary name to the literal `cutoff`. `before_only` means member before and non-member after. `after_only` is the reverse. `always`, `never`, and `unknown` apply on both sides.

## Extraction-unknown taxonomy

Use exactly one reason:

- `ambiguous_reference`: more than one materially different referent/scope/role resolution is supported by the language.
- `insufficient_authority`: the text does not establish the typed authority required to answer the query, even though the language is in the general domain.
- `ontology_escape`: the text requires a semantic primitive not represented by this seven-dimension contract.
- `unparsed`: the construction appears representable, but this implementation cannot recover it uniquely.

Safety requirement: when the text does not warrant one resolved object, prefer the correct unknown state over invented authority.
