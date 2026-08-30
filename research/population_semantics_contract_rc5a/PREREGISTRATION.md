# Population Semantics Contract RC5A — Apparatus-Corrected Sufficiency Reproduction

Classification: Research Infrastructure / semantic-authority sufficiency reproduction.

## Parent failure

RC5 science run `33324874888` failed before producing semantic comparison results because the exhaustive generator admitted an internally inconsistent authority state: `only members may P` + the same entity is explicitly `non_member` + explicitly `permitted`.

A separate evaluator inspection also established that RC5's ablation collision projection retained non-semantic case metadata, so distinct witness IDs would prevent projected collisions even when the nominated semantic field was the only authority difference.

These failures are preserved in PR #48. They are apparatus defects, not semantic results.

## Frozen semantic mechanisms

RC5A imports, without modification:

- `research.population_semantics_contract_rc5.oracle.relation`
- `research.population_semantics_contract_rc5.consumer.relation`

No RC5 oracle or consumer source may change in this successor.

## Exactly authorized corrections

1. Filter only authority states that are logically inconsistent under their own declared fields. The currently identified exclusion is `only_population_may == true`, `membership == non_member`, and `explicit_permission == permitted` for the same entity/predicate.
2. For field-ablation collision testing, compare semantic `{dimension, authority, query}` projections after field removal. Exclude `case_id` and other record metadata from collision identity.

No relation rule, quantifier implication, subclass rule, role rule, temporal rule, modality rule, or unknown handling may change.

## Success condition

`CONTRACT_SUFFICIENT` requires all of:

- zero possible-world-oracle vs direct-consumer disagreements on the corrected bounded corpus;
- 13/13 preregistered field-ablation witnesses demonstrate projected collision plus different oracle relation;
- 8/8 metamorphic pairs satisfy the frozen expected same/different relation in both mechanisms;
- all modeled semantic relations remain representable by entailment / neutral / contradiction.

Any semantic disagreement or failed semantic witness is preserved and terminates RC5A as incomplete. Do not repair it in place.

## Non-authorization

No production parser, semantic operator, entailer, threshold, Contract C surface, aggregation rule, or decision policy is changed or authorized by this experiment.
