# Population Semantics Contract RC5B — Negative Subclass Inheritance Reproduction

Classification: Research Infrastructure / semantic-authority sufficiency reproduction.

## Parent evidence

RC5A accepted science run `33325104519` on frozen corrected corpus SHA256 `92721e5144aa582ff00c10c4fc3666d43c05c5cd77e4a7669d10545c23395308` produced exactly two possible-world-oracle vs direct-consumer disagreements out of 460 cases. All 13 field-ablation witnesses and all 8 metamorphic pairs passed, and no semantic relation beyond entailment / neutral / contradiction was required.

Both disagreements are directed-subclass non-membership cases:

- `A ⊆ B`, `x ∉ B`, query `x ∈ A`;
- mirrored `B ⊆ A`, `x ∉ A`, query `x ∈ B`.

The frozen authority already contains every field needed to determine these cases. RC5A therefore localized the residual disagreement to direct-consumer implementation rather than representation.

## Frozen predecessor material

RC5B reuses without modification:

- RC5A corrected 460-case corpus and SHA256;
- RC5 possible-world oracle;
- RC5A semantic ablation projection and all 13 witnesses;
- all 8 metamorphic pairs;
- every non-subclass direct-consumer rule.

## Exactly one authorized semantic-consumer correction

For a directed subset edge `A ⊆ B`:

- preserve positive inheritance: `x ∈ A ⇒ x ∈ B`;
- add negative inheritance downward: `x ∉ B ⇒ x ∉ A`.

Do **not** infer either invalid converse:

- `x ∈ B ⇒ x ∈ A`;
- `x ∉ A ⇒ x ∉ B`.

The mirrored rule applies identically when the declared edge is `B ⊆ A`.

No other consumer rule may change.

## Hard success condition

`CONTRACT_SUFFICIENT` requires, without post-reveal repair:

- zero possible-world-oracle vs RC5B direct-consumer disagreements across all 460 corrected cases;
- 13/13 field-ablation witnesses valid;
- 8/8 metamorphic pairs pass in both mechanisms;
- relation vocabulary remains entailment / neutral / contradiction only;
- explicit sentinels verify both valid negative-inheritance directions and both prohibited converses.

Any residual disagreement terminates RC5B as incomplete and is preserved.

## Non-authorization

This is not authorization to change CAL production parsing, semantic operators, the entailer, thresholds, Contract C, aggregation, or downstream policy.
