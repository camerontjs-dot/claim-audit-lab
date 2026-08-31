# RC7B Failure Localization — Preregistration

Classification: Research Infrastructure / post-reveal failure localization.

This experiment does not alter either frozen RC7B implementation, the sealed evaluator, the RC5B semantic consumer, or production code.

## Exact immutable inputs

- A evidence commit: `fc1b3ff7a7ca273d732ef6202c10fb3f24b12750`
- B evidence commit: `04f52a6506336c5b0772fede9dca25d4f894ef18`
- sealed evaluator commit: `19e9302a11decb08dda644fbf1018997cf138c3b`
- repaired canonical payload semantic SHA-256: `35777672cd1a23b52864d69523ce504077b604b400fdce8adad2077fe600ac2a`
- governed transport repair: insert Base64 character `I` at position `3168`, yielding compressed SHA-256 `4f3ea5c6f00e85dfc60b833eac397626503338311c9305a81cc3ef6672af6aa2`; no sealed semantic content may be changed.

## Question

Where do the RC7B failures localize when the same 180 hidden cases are partitioned into:

1. `both_correct`: A and B agree semantically and neither has a gold error;
2. `agree_but_wrong`: A and B agree semantically but at least one has a gold error;
3. `disagree`: A and B differ in semantic field status/value or receipt family/status.

The analysis asks whether the failures are concentrated in a small number of field × linguistic-warrant constructions or remain distributed across families, partitions, paraphrases, and transformations.

## Primary measurements

For each case:

- cohort above;
- family and evaluator partition;
- A/B authorization and downstream relation;
- A/B unsafe state and wrong authorized relation;
- field-level semantic mismatches;
- field-level grounding/warrant mismatches;
- exact gold warrant construction labels;
- source text from the presealed payload;
- whether disagreement involved one correct implementation or both wrong.

For every `(family, field, gold warrant)` key:

- occurrence count;
- cohort counts;
- A semantic-error count;
- B semantic-error count;
- A/B disagreement count;
- shared-error count;
- unsafe-field counts;
- construction vs paraphrase distribution.

For mutations:

- A/B pass state;
- family;
- expected changed fields;
- observed changed fields;
- before/after text;
- concentration of failures by transformation signature.

## Error semantics

Case correctness follows the already-sealed pairwise comparator semantics:

- semantic cases are correct only when `semantic_case_exact` is true;
- out-of-jurisdiction cases are correct only when `ood_correct` is true;
- other cases are errors when unsafe/invalid or any field status is not exact.

Semantic agreement follows the already-sealed pairwise comparator: compare receipt status/family and, for matching receipt families, each overlapping field's `(status, normalized value)`. Warrant and span differences do not create semantic disagreement but are measured separately.

## Preregistered localization states

These are descriptive research states, not promotion states.

### `CONCENTRATED_CONSTRUCTION_GAPS`

Supported only if:

- at least 10 `agree_but_wrong` cases exist;
- a greedy set of at most three `(family, field, warrant)` keys touches at least 60% of `agree_but_wrong` cases;
- and at most three mutation signatures account for at least 60% of mutations failed by either implementation;
- without satisfying the distributed-surface criterion below.

### `DISTRIBUTED_LINGUISTIC_LIMITATION`

Supported only if:

- for both implementations, paraphrase case error rate exceeds construction case error rate by at least 10 percentage points;
- `agree_but_wrong` failures span at least two semantic families and at least six distinct `(family, field, warrant)` keys;
- and no three keys touch 60% of `agree_but_wrong` cases.

### `MIXED_LOCALIZED_AND_DISTRIBUTED`

Supported if the top-three construction keys touch at least 60% of `agree_but_wrong` cases, while both implementations also show a >=10-point paraphrase error-rate penalty and residual failures outside those keys span at least two families.

### `INCONCLUSIVE_LOCALIZATION`

Use if none of the above are satisfied.

### `APPARATUS_INVALID`

Use if immutable input identities cannot be materialized, the governed payload repair does not reproduce the presealed semantic hash, or the analysis script cannot deterministically complete.

## Falsifiers and alternative explanations

A concentrated result does not by itself prove the contract is repairable by adding rules; a common implementation bias could create the same concentration. A distributed result does not prove natural language is intrinsically non-deterministic; both implementations may simply share a narrow implementation strategy. Agreement is not truth: RC7B already showed substantial gold error under agreement. Disagreement is treated as a risk signal, not an oracle.

The smallest justified successor should be chosen from the actual localization evidence, not presumed in advance.

## Non-authorization

No result here authorizes production parser changes, semantic-operator changes, Contract C changes, aggregation changes, model replacement, merging either fresh implementation, or production promotion.
