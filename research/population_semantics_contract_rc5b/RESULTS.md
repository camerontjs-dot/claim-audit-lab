# Population Semantics Contract RC5B — Terminal Results

## Classification

Research Infrastructure / semantic-authority sufficiency reproduction.

This record does not authorize a production parser, semantic operator, model change, threshold change, Contract C change, aggregation change, or downstream policy change.

## Frozen authority

- Production `main` at research start: `53f0885b111676794d1bd20e10b91aa58b07e9d4`
- RC4 accepted science head: `c157da7953753a2f27c306abc86ab0141752c512`
- RC4 accepted science run: `33323711511`
- RC5 first failed science run: `33324874888`
- RC5A accepted science head: `6445707a628ce6a26bf4347bf0c4a07ab2cd97a1`
- RC5A accepted science run: `33325104519`
- RC5B pre-execution source head: `c9dc89631047cfedf6868324a455014783a6cf24`
- RC5B accepted science head: `c623af35bee3b5f685c9a44e6d91ced006b2d690`
- RC5B accepted science run: `33325279730`
- Frozen corrected corpus SHA256: `92721e5144aa582ff00c10c4fc3666d43c05c5cd77e4a7669d10545c23395308`
- RC5B RESULTS SHA256: `f3c391eb6b953567f6ce134cb4f1ec5988b4808e2f32abd162b7bf5234ffaabd`
- RC5B artifact: `9736040270`
- RC5B artifact digest: `sha256:fa9ab58cfae77f7eb114ccbce5051c42e47d0e0c833bf214c6d11b66550b0104`

Later commits are terminal documentation and do not redefine the accepted science head.

## Terminal disposition

**CONTRACT_SUFFICIENT for the bounded population/membership semantic domain tested here.**

Observed on all 460 corrected bounded cases:

- possible-world oracle vs independent direct consumer disagreements: **0 / 460**;
- preregistered field-ablation witnesses: **13 / 13 valid**;
- preregistered metamorphic pairs: **8 / 8 pass for both mechanisms**;
- preregistered subclass-direction sentinels: **4 / 4 pass**;
- semantic relation vocabulary required by the modeled worlds: **entailment / neutral / contradiction only**.

## What the result supports

Within the bounded domain, the following typed authority is sufficient to determine the tested population/membership relations without relying on ordinary NLI as semantic authority:

- entity identity;
- population/class identity;
- explicit membership status: member / non-member / unknown;
- directed subclass/subset edge;
- predicate identity;
- modality where behavior is distinguished from obligation;
- population quantifier;
- `only` as a necessary-condition permission construction, not sufficient permission;
- group scope versus member scope;
- ordered semantic roles;
- temporal membership boundary/direction;
- polarity;
- explicit unknown.

The field-ablation witnesses show that each nominated distinction can be necessary: removing the nominated field can collapse two authority states that require different semantic relations.

## Directed subclass boundary

RC5A exposed the final direct-consumer gap. For `A ⊆ B`:

- `x ∈ A ⇒ x ∈ B` is valid positive inheritance;
- `x ∉ B ⇒ x ∉ A` is valid negative inheritance;
- `x ∈ B ⇒ x ∈ A` is not licensed;
- `x ∉ A ⇒ x ∉ B` is not licensed.

RC5B changed only this consumer rule. The possible-world oracle, corrected corpus, representation fields, ablation witnesses, metamorphic pairs, and all non-subclass consumer rules remained unchanged.

## Preserved failures

### RC5 apparatus failure

Run `33324874888` stopped before semantic comparison because the exhaustive generator admitted internally inconsistent authority states: `only members may P` plus the same entity explicitly non-member and explicitly permitted. The possible-world oracle rejected those states as admitting no possible world.

RC5 also had a field-ablation evaluator defect because record metadata such as `case_id` remained in the collision projection.

No semantic result was claimed from RC5.

### RC5A consumer counterexamples

Run `33325104519` produced exactly two disagreements:

- `S-009`: `A ⊆ B`, entity explicitly non-member of `B`, query membership in `A`; oracle contradiction, consumer neutral.
- `S-016`: mirrored `B ⊆ A`, entity explicitly non-member of `A`, query membership in `B`; oracle contradiction, consumer neutral.

RC5A otherwise passed all 13 ablation witnesses and all 8 metamorphic pairs and required only the three ordinary relation labels. The disagreement was therefore localized to an incomplete independent consumer, not a missing representation field.

## Falsifiers and alternatives

The tested evidence does not support the explanation that a larger ordinary NLI model alone supplies the missing population/membership semantics. RC4's strongest ordinary NLI system reached 79.8% at full coverage with eight false-adverse decisions, while the frozen typed candidate reached 98.4% selective accuracy with zero false-adverse decisions and 9/10 mutation consistency before parser recovery was separated from representation.

The result also does not support simple textual decomposition as the needed mechanism: RC4 decomposition reproduced the incumbent aggregate result and did not recover the structural distinctions.

The representation-sufficiency result is bounded. It does not establish that arbitrary natural language can be parsed into this authority reliably, that this schema covers every semantic construction, or that a production CAL operator should be introduced now.

## Architectural implication

For the tested population/membership domain, the semantic bottleneck is now localized:

`natural language / evidence -> typed semantic extraction -> bounded typed authority -> deterministic relation -> downstream epistemic machinery`

The typed-authority-to-relation step is supported by independent bounded conformance. The principal unresolved boundary is **text-to-typed-authority extraction and its abstention/unknown behavior**.

## Production disposition

**NO PRODUCTION PROMOTION FROM THIS EXPERIMENT ALONE.**

Do not change the production entailer, thresholds, ensemble policy, Contract C, CAL aggregation, or production semantic-operator surface on the basis of RC5B alone.
