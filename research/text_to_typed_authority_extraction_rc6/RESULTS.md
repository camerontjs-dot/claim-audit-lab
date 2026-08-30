# RC6 — Text-to-Typed-Authority Extraction + Unknown Boundary — Terminal Results

## Classification

Research Infrastructure / semantic-extraction discrimination experiment.

No production parser, entailer, model, threshold, ensemble, semantic operator, Contract C surface, aggregation rule, or downstream policy is authorized by this result.

## Frozen authority and receipts

- production `main` at experiment start: `53f0885b111676794d1bd20e10b91aa58b07e9d4`
- RC5B accepted science head: `c623af35bee3b5f685c9a44e6d91ced006b2d690`
- RC5B accepted science run: `33325279730`
- RC6 pre-reveal scientific source head: `39419546adc2a0c3369c6d3cc84ef360968ced9b`
- RC6 accepted model-free freeze head: `54abacaae9e5ff0f912b6a6523f85c556ffd6ac2`
- RC6 accepted freeze run: `33330441265`
- RC6 freeze artifact: `9737476767`
- RC6 freeze artifact digest: `sha256:fed6bacf248776cbd29b205df84344e69842977d81e9dab28438f6b4d870ed8b`
- frozen RC6 cohort SHA256: `820b5a64cf4187998f2c4b416293c8fd0a577b564cab31be22dddd4ace822d23`
- RC6 accepted science head: `103ceeda47f7fc1e136c899d31a269cd032ba5cf`
- RC6 accepted science run: `33330592983`
- RC6 science artifact: `9737521527`
- RC6 science artifact digest: `sha256:effb1599ad2f93881e23d8da063f3d27ce2102371478615a616c8f539988daaf`
- `RESULTS.json` SHA256: `d6b49430299c17f47db7c7d504cdedd535b7949ddfe8430da5990dd9bbeece89`
- `MEASUREMENTS.json` SHA256: `691fb46edc622d45721f3aea8bd775eb48c0823c0ddc6461b4601345120638b4`
- `COUNTEREXAMPLES.json` SHA256: `b72697eb4ccf798b7312c6228d6c9bbed76fa5638cecdf7524336cc136524a95`

Later commits are terminal documentation only and do not redefine the accepted freeze or science heads.

## Cohort

100 frozen text/query cases:

- 70 in-schema cases, 10 each across the seven RC5B semantic dimensions;
- 10 ambiguous-reference extraction-unknown cases;
- 10 insufficient-authority extraction-unknown cases;
- 10 ontology-escape cases;
- 12 preregistered mutation pairs.

The in-schema cohort deliberately includes resolved semantic `neutral` cases. Extraction `unknown` is therefore evaluated separately from semantic neutral.

## Gold semantic sanity

Before scoring either extractor, all 70 frozen gold typed objects were passed through the unchanged RC5B deterministic consumer.

**Gold-object vs frozen-consumer disagreements: 0 / 70.**

The extraction experiment therefore did not expose a residual typed-authority-to-relation failure.

## Extractor results

| Measure | Regex/template | Token/clause | Exact-agreement consensus |
|---|---:|---:|---:|
| Overall extraction-status accuracy | 86 / 100 | **95 / 100** | 82 / 100 |
| In-schema resolved coverage | 56 / 70 (80.0%) | **65 / 70 (92.9%)** | 52 / 70 (74.3%) |
| Exact typed-object recovery over all in-schema cases | 56 / 70 (80.0%) | **64 / 70 (91.4%)** | 52 / 70 (74.3%) |
| Downstream semantic relation accuracy over all in-schema cases | 56 / 70 (80.0%) | **65 / 70 (92.9%)** | 52 / 70 (74.3%) |
| Semantic relation precision among resolved outputs | **56 / 56 (100%)** | **65 / 65 (100%)** | **52 / 52 (100%)** |
| Exact object precision among resolved outputs | 56 / 56 (100%) | 64 / 65 (98.5%) | 52 / 52 (100%) |
| Unsafe authority fabrication on expected-unknown cases | **0 / 30** | **0 / 30** | **0 / 30** |
| Unknown-reason accuracy | **30 / 30** | **30 / 30** | **30 / 30** |
| Semantic-neutral resolved and correct | 19 / 24 (79.2%) | **22 / 24 (91.7%)** | 17 / 24 (70.8%) |
| Mutation pairs passed | 8 / 12 | **12 / 12** | 8 / 12 |
| Frozen consumer runtime errors | 0 | 0 | 0 |

The consensus rule resolved only when the two extractors produced byte-equivalent typed objects. It achieved 100% semantic precision and zero fabrication, but reduced in-schema coverage to 74.3%. In this bounded experiment, exact agreement functions as a conservative risk gate, not as a semantic recovery mechanism.

## Extractor disagreement

The two implementations disagreed on semantic authority in 17 / 100 cases.

For the stronger token/clause extractor:

- exact scientific failure under extractor disagreement: 5 / 17 = 29.4%;
- exact scientific failure under extractor agreement: 1 / 83 = 1.2%;
- relative risk: approximately 24.4x.

For the regex/template extractor:

- exact scientific failure under disagreement: 13 / 17 = 76.5%;
- exact scientific failure under agreement: 1 / 83 = 1.2%;
- relative risk: approximately 63.5x.

Thus independent-code-path disagreement is a strong extraction-risk signal in this cohort. It is not itself authority or truth.

## Preserved stronger-extractor failures

The token/clause extractor had six exact scientific failures:

1. `SC-05`: resolved, but recovered `membership_population=B` instead of `A`; the frozen consumer still returned the correct `neutral` relation.
2. `SC-06`: valid mirrored subclass construction rejected as `unparsed`.
3. `SC-07`: valid mirrored negative-subclass construction rejected as `unparsed`.
4. `SC-08`: valid mirrored subclass construction rejected as `unparsed`.
5. `SC-09`: valid mirrored subclass construction rejected as `unparsed`.
6. `TM-06`: valid temporal `never` construction rejected as `ontology_escape` because a conservative lexical escape guard overfired on `either`.

No frozen extractor is repaired after reveal. These failures are preserved as extraction counterexamples.

The weaker regex/template extractor additionally failed on two membership/behavior cases and six quantifier cases because broad lexical fail-closed guards overrejected valid in-schema language, plus five subclass cases and the same temporal case. These are also preserved in the science artifact.

## What RC6 supports

### OBSERVED

- Correct frozen typed authority always produced the preregistered relation in RC6: 0 gold-consumer disagreements.
- Neither extractor fabricated typed authority on any of the 30 frozen ambiguous, insufficient-authority, or ontology-escape cases.
- Every resolved prediction from either extractor produced the correct downstream semantic relation.
- Semantic neutral remained recoverable as a resolved semantic state rather than being inherently collapsed into extraction unknown.
- The stronger extractor passed all 12 mutation pairs.
- Extraction disagreement sharply enriched for extraction failures.

### INFERENCE

Within this bounded synthetic language, the evidence supports localizing the remaining population/membership bottleneck to **text-to-typed-authority recovery and jurisdiction recognition**, not to the already-frozen typed-authority-to-relation consumer.

The evidence also supports keeping at least three states conceptually distinct:

1. resolved typed authority whose semantic relation is `neutral`;
2. extraction unknown because the text does not establish a unique authority object;
3. ontology/jurisdiction escape because the construction is outside the tested authority schema.

### IMPORTANT ALTERNATIVE EXPLANATION / LIMITATION

RC6 does **not** establish genuinely independent natural-language extraction. Both extractors and the synthetic corpus were authored in the same research execution and share knowledge of the bounded semantic vocabulary. They are separate implementations, but not context-free independent consumers.

The cohort is intentionally controlled and template-like. High precision may therefore reflect bounded lexical regularity rather than robust arbitrary-language semantic extraction.

This limitation prevents production promotion and makes fresh independent extraction the highest-value falsifier.

## Terminal scientific interpretation

**Bounded support for the extraction-bottleneck / explicit-unknown architecture.**

The strongest result is not the 92.9% coverage number. It is the combination of:

- 0 / 70 gold-consumer disagreements;
- 0 / 30 authority fabrications for both extractors;
- 100% downstream semantic precision on every resolved extractor output;
- preserved semantic-neutral versus extraction-unknown distinction;
- 12 / 12 mutation stability for the stronger extractor;
- extraction disagreement strongly predicting extraction failure.

However, because extractor and corpus independence is not established, the governance disposition for generalization or production remains **INCONCLUSIVE**.

## Production disposition

**NO PRODUCTION PROMOTION FROM RC6.**

Do not change CAL's production parser, entailer, thresholding, ensemble policy, semantic operator, Contract C surface, aggregation, or downstream policy on the basis of RC6 alone.
