# RC6 — Text-to-Typed-Authority Extraction + Unknown Boundary

Classification: Research Infrastructure / semantic-extraction discrimination experiment.

## Question

Given the frozen RC5B population/membership semantic authority and deterministic consumer, can independently implemented text extractors recover that authority from held-out bounded natural-language constructions while failing closed when the text is ambiguous, insufficient to establish authority, or outside the schema's semantic jurisdiction?

This experiment tests the inference that the principal bottleneck has moved upstream from typed-authority consumption to text-to-typed-authority extraction.

## Frozen predecessor authority

- production `main`: `53f0885b111676794d1bd20e10b91aa58b07e9d4`
- RC5B accepted science head: `c623af35bee3b5f685c9a44e6d91ced006b2d690`
- RC5B accepted science run: `33325279730`
- RC5B frozen corrected typed corpus SHA256: `92721e5144aa582ff00c10c4fc3666d43c05c5cd77e4a7669d10545c23395308`
- RC5B direct consumer path: `research/population_semantics_contract_rc5b/consumer.py`

The RC5B consumer and its parent semantic implementation are frozen dependencies. RC6 may not alter them.

## Frozen RC6 cohort

Materialized SHA256: `820b5a64cf4187998f2c4b416293c8fd0a577b564cab31be22dddd4ace822d23`.

100 cases:
- 70 in-schema text/query pairs across seven RC5B dimensions, 10 each;
- 10 ambiguous-reference cases;
- 10 insufficient-authority cases;
- 10 ontology-escape cases;
- 12 preregistered mutation pairs.

The 70 in-schema cases contain both determinate relations and explicit semantic neutral. In particular, explicit `membership=unknown` is a valid typed authority state and must not be confused with extraction unknown.

The 30 extraction-unknown cases have no gold RC5B object. An extractor that emits a resolved typed object on such a case is an authority-fabrication error.

## Frozen candidate extractors

Two independent code paths are frozen before cohort execution:

- `extractor_regex.py`: regex/template-oriented whole-text extractor;
- `extractor_tokens.py`: token/clause-oriented compositional extractor.

They may share the frozen output contract but do not call each other and do not call the RC5B consumer.

Extractor API:

`extract(text, query_text) -> {status: resolved, case: ...} | {status: unknown, reason: ...}`

Inputs do not contain case ID, family, partition, expected relation, or expected typed object.

## Measurements

For each extractor and their exact-agreement consensus:

1. extraction status accuracy over all 100 cases;
2. exact semantic-object recovery over the 70 in-schema cases;
3. downstream relation accuracy after passing resolved objects through the unchanged RC5B consumer;
4. unsafe authority fabrication on the 30 expected-unknown cases;
5. false extraction-unknown on the 70 in-schema cases;
6. semantic-neutral preservation: resolved neutral cases must remain resolved rather than being converted into extraction unknown;
7. unknown-reason accuracy for ambiguous / insufficient / ontology-escape partitions;
8. mutation-pair consistency;
9. extractor disagreement rate and error enrichment under disagreement;
10. per-family field failure inventory.

Consensus resolves only when both extractors resolve to byte-equivalent semantic objects. Any other pair returns extraction unknown. Consensus is evaluated for precision, coverage, and fabrication rate; abstention is not counted as a correct in-schema semantic decision.

## Hard falsifiers

The bottleneck-localization theory is weakened or falsified if any of the following occurs:

- the frozen RC5B consumer frequently produces the wrong relation from correctly recovered typed authority;
- extraction errors are not separable from semantic-consumer errors;
- extractors systematically collapse explicit semantic neutral into extraction unknown;
- ambiguous or out-of-schema language is routinely forced into resolved RC5B objects;
- hidden semantic mutations do not produce the expected typed-object/relation changes;
- apparent success depends on one extractor while the independent implementation disagrees broadly.

## Success interpretation

No single accuracy threshold authorizes production. Evidence supports the architecture only if both frozen extractors show high-precision authority recovery, low fabrication, preserved neutral/unknown distinction, and mutation stability, with consensus increasing safety rather than merely hiding errors through abstention.

A bounded positive result supports only the separation:

`text -> extraction status / typed authority -> frozen deterministic semantic relation`.

It does not establish arbitrary-language coverage or authorize a production parser.

## Non-authorization

No production parser, entailer, model, threshold, ensemble, semantic operator, Contract C surface, aggregation rule, or downstream decision policy may be changed or promoted by RC6 alone.
