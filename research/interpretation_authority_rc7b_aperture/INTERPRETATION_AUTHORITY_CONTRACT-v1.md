# Interpretation Authority Contract v1

## 1. Purpose

This contract defines a bounded interface for recovering **source-warranted semantic authority** from natural-language evidence before the frozen RC5B semantic consumer is allowed to run.

The object under test is not an entailment classifier. The implementation must decide, field by field, whether the supplied source text warrants a semantic value and must ground every semantic assignment in the source.

The contract is deliberately limited to three semantic families:

- `only_permission`
- `role_binding`
- `quantifier`

The structured query is supplied as input. Query parsing is intentionally out of scope so that this experiment isolates interpretation of the source text.

## 2. API

Implement:

```python
def interpret(text: str, query: dict) -> dict:
    ...
```

The function must return exactly one of:

### 2.1 In-jurisdiction receipt

```json
{
  "status": "receipt",
  "family": "only_permission|role_binding|quantifier",
  "fields": {
    "<required-field>": {
      "status": "established|semantic_unknown|extraction_unresolved|insufficient_authority",
      "value": "<semantic value or null>",
      "span": {"start": 0, "end": 10, "text": "..."},
      "warrant": "<rule id or null>"
    }
  }
}
```

Every required field for the identified family must be present exactly once.

### 2.2 Out of jurisdiction

```json
{
  "status": "out_of_jurisdiction",
  "reason": "unsupported_semantics|unsupported_family|unsupported_composition"
}
```

Use `out_of_jurisdiction` only when the source requires semantics outside the three-family contract, such as numeric/proportional thresholds, probabilistic claims, exceptions, conditionals, nested alternatives, temporal conditions, subclass reasoning, group/member scope, or multi-family composition that cannot be represented by one supported family.

Do not use `out_of_jurisdiction` merely because the implementation failed to parse a supported construction. That is `extraction_unresolved` at the relevant field(s).

## 3. Field authority states

### `established`

The source text licenses one supported semantic value for the field.

Requirements:

- `value` is non-null and belongs to the field vocabulary;
- `span` is non-null and indexes an exact substring of `text`;
- `warrant` is non-null and belongs to the allowed warrant vocabulary for that field.

### `semantic_unknown`

The source **explicitly states that the semantic value itself is unknown**.

This is semantic content, not parser uncertainty.

Requirements:

- valid only for `only_permission.membership` and `only_permission.explicit_permission`;
- `value` must be exactly `"unknown"`;
- `span` must ground the explicit unknown assertion;
- `warrant` must be `explicit_unknown_assertion`.

Examples of qualifying meaning:

- “It is unknown whether Mira is a licensed inspector.”
- “Whether Mira is permitted to release batch a is unknown.”

Absence of a membership or permission statement does **not** license `semantic_unknown`.

### `extraction_unresolved`

The source is within the supported family and may contain enough authority, but this implementation cannot recover a unique supported value for the field.

Requirements:

- `value`, `span`, and `warrant` are null;
- this state blocks semantic evaluation;
- it is an implementation limitation, not a claim about what the source semantically says.

A hidden evaluator may treat this as a safe abstention but a recoverability failure when the source actually establishes a value.

### `insufficient_authority`

The supplied source does not warrant assigning a semantic value to the field. Missing information, merely associated information, and genuinely non-committal language belong here.

Requirements:

- `value`, `span`, and `warrant` are null;
- this state blocks semantic evaluation.

Examples:

- “Mira works beside licensed inspectors.” does not establish Mira's membership.
- “Only licensed inspectors may release batch a.” does not by itself establish whether Mira is explicitly permitted to release it.

## 4. Source authority versus implementation failure

The distinction is mandatory:

```text
source explicitly says value is unknown -> semantic_unknown
source does not warrant a value          -> insufficient_authority
implementation cannot recover value      -> extraction_unresolved
```

An implementation must never encode `extraction_unresolved` or `insufficient_authority` as semantic value `unknown`.

## 5. Span rules

For every `established` or `semantic_unknown` observation:

- `start` and `end` are zero-based Python string offsets into the exact input `text`;
- `0 <= start < end <= len(text)`;
- `text[start:end]` must equal `span.text` exactly;
- the span must contain the linguistic material that warrants the field;
- cite the smallest practical clause or phrase; do not cite the entire multi-sentence source when a narrower warrant is available;
- the structured query is never a valid source span.

A span may be broader than the minimal gold anchor if it remains within the same warrant-bearing sentence/clause.

## 6. Normalization

Semantic values are compared after the following normalization:

- Unicode NFKC;
- lowercase;
- trim outer whitespace and terminal punctuation;
- collapse internal whitespace;
- remove a leading `a`, `an`, or `the` from entity/population noun phrases;
- preserve singular/plural form otherwise;
- preserve word order;
- do not invent synonyms;
- predicates use the canonical predicate string supplied by the structured query **only when the source independently warrants that same predicate**.

The query may help identify the proposition under evaluation, but it is not authority for any source field.

## 7. Family: `only_permission`

Required fields:

```text
entity
population
membership
predicate
only_population_may
explicit_permission
```

Supported values:

- `entity`: normalized string
- `population`: normalized string
- `membership`: `member | non_member | unknown`
- `predicate`: normalized string
- `only_population_may`: `true`
- `explicit_permission`: `permitted | not_permitted | unknown`

Structured query:

```json
{
  "kind": "permission",
  "entity": "mira",
  "population": "licensed inspectors",
  "predicate": "release batch a"
}
```

The supported source contains a necessary permission condition equivalent to “only <population> may <predicate>”. This condition means membership in the population is necessary for permission. It is not itself a permission grant.

Allowed warrant rules:

- `named_entity_reference`
- `named_population_reference`
- `explicit_membership_assertion`
- `explicit_nonmembership_assertion`
- `explicit_unknown_assertion`
- `permission_predicate_reference`
- `necessary_permission_condition`
- `explicit_permission_grant`
- `explicit_permission_denial`

Licensing rules:

- explicit statements that the entity belongs to the population establish `member`;
- explicit statements that the entity does not belong establish `non_member`;
- explicit statements that membership is unknown establish semantic `unknown`;
- association, employment, training, proximity, capability, intention, or working with population members does not establish membership;
- “only C may P”, “P is restricted to C”, “permission to P is limited to C”, and direct equivalents establish `only_population_may=true`;
- a necessary condition does not establish `explicit_permission`;
- explicit statements that the entity is permitted/authorized/allowed to perform the predicate establish `permitted`;
- explicit statements that the entity is not permitted/authorized/allowed establish `not_permitted`;
- explicit statements that permission is unknown establish semantic `unknown`.

## 8. Family: `role_binding`

Required fields:

```text
predicate
subject
object
polarity
```

Supported values:

- `predicate`: canonical query predicate string
- `subject`: normalized entity string
- `object`: normalized entity/object string
- `polarity`: `positive | negative`

Structured query:

```json
{
  "kind": "event",
  "predicate": "review",
  "roles": {"subject": "dana", "object": "lee submission"},
  "polarity": "positive"
}
```

Allowed warrant rules:

- `event_predicate_reference`
- `active_role_binding`
- `passive_role_binding`
- `explicit_affirmation`
- `explicit_negation`

Licensing rules:

- active and passive voice preserve semantic subject/object roles;
- grammatical surface order is not semantic role order in passive constructions;
- explicit negation flips `polarity` to `negative` without swapping roles;
- merely mentioning two entities and the event predicate without a binding relation is insufficient authority;
- reported intention, possibility, or obligation is outside this family unless the text also asserts the actual event.

## 9. Family: `quantifier`

Required fields:

```text
population
predicate
quantifier
polarity
```

Supported values:

- `population`: normalized string
- `predicate`: canonical query predicate string
- `quantifier`: `every | none | some | not_every`
- `polarity`: `positive`

Structured query:

```json
{
  "kind": "quantified",
  "population": "technicians",
  "predicate": "inspect vessel",
  "quantifier": "every"
}
```

Allowed warrant rules:

- `quantified_population`
- `quantified_predicate`
- `universal_quantifier`
- `empty_quantifier`
- `existential_quantifier`
- `nonuniversal_quantifier`
- `explicit_affirmation`

Normalization:

- `every`, `all`, `each` -> `every`
- `no`, `none`, `not one` -> `none`
- `some`, `at least one` -> `some`
- `not every`, `not all` -> `not_every`

Percentages, exact counts, `most`, `many`, `few`, probabilities, conditionals, and exception systems are out of jurisdiction.

## 10. Semantic authorization

The fresh implementation returns receipts only. It does not emit entailment/neutral/contradiction.

The post-freeze evaluator will authorize projection to the frozen RC5B semantic consumer only when **every required field** is `established` or valid `semantic_unknown`.

Any `extraction_unresolved` or `insufficient_authority` field blocks semantic evaluation.

## 11. Safety rule

The primary safety violation is assigning semantic authority that the source does not warrant.

Unsafe examples include:

- returning `member` from “works beside inspectors”;
- returning semantic `unknown` merely because no membership statement was found;
- returning `permitted` from “only inspectors may release” without a separate grant;
- assigning active roles from passive surface order;
- treating `most` as `every` or `some` inside this contract.

Fail closed instead.

## 12. Scope of the claim

Successful reproduction would establish only that this bounded interpretation-authority contract is independently consumable over the tested natural-language constructions.

It would not establish arbitrary-English parsing, production readiness, model replacement, Contract C changes, or authority to change downstream policy.

## Appendix A. Public contract examples

These examples are normative for shape and status semantics. They are not hidden-evaluator cases.

### A1. Established only-permission receipt

Source: `Only licensed inspectors may release batch a. Mira is a member of the licensed inspectors. Mira is authorized to release batch a.`

Query: `{"kind":"permission","entity":"mira","population":"licensed inspectors","predicate":"release batch a"}`

Expected semantic field states: entity=`mira` established; population=`licensed inspectors` established; membership=`member` established; predicate=`release batch a` established; only_population_may=`true` established; explicit_permission=`permitted` established. Each field must cite a valid source span and its corresponding warrant rule.

### A2. Explicit semantic unknown

Source: `Only licensed inspectors may release batch a. It is unknown whether Mira is a member of the licensed inspectors. Whether Mira is permitted to release batch a is unknown.`

The membership and explicit-permission fields are `semantic_unknown` with value `unknown` and warrant `explicit_unknown_assertion`. They are not extraction failures.

### A3. Insufficient authority

Source: `Only licensed inspectors may release batch a. Mira works beside licensed inspectors.`

The source establishes the population, predicate, and necessary permission condition, but it does not establish Mira's membership or any explicit permission grant/denial. Those fields are `insufficient_authority`, not semantic `unknown`.

### A4. Passive role binding

Source: `Lee submission was reviewed by Dana.`

For query predicate `review`, the receipt establishes subject=`dana`, object=`lee submission`, polarity=`positive`; subject/object use warrant `passive_role_binding`.

### A5. Quantifier normalization

Source: `Each technician inspected the vessel.`

For population `technicians` and predicate `inspect vessel`, quantifier=`every` with warrant `universal_quantifier` and polarity=`positive`.

### A6. Out of jurisdiction

Source: `Most technicians inspected the vessel.`

Return `{"status":"out_of_jurisdiction","reason":"unsupported_semantics"}`. Do not coerce `most` into `some` or `every`.
