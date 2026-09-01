# RC7F-B Scientific Evidence Record

Status: **ACCEPTED HELD-OUT RUN / TERMINAL RESEARCH RECORD**

Terminal disposition: `MORE_COMPARISON_RESEARCH_JUSTIFIED`

Research-only. The instrument has no semantic authority jurisdiction.

## Immutable lineage

- parent RC7E evidence: `34e9bcafad2c63c9b0761ffc456532344bc75b88`
- preregistration: `8a5889c5a658c1c0aae941154be8f5f9acdf5314`
- apparatus freeze: `d331fe6cbd6ce5ec56c446bd3a8a572b33c3457f`
- sealed apparatus ref: `sealed/rc7fb-comparison-apparatus-20260831`
- accepted qualification run: `33453159594`
- qualification artifact: `9780474015`
- qualification digest: `sha256:7eafa20c8bf91fef9ad1f9b516d8543a05de0cae95564635cf6219db978423a7`
- held-out cohort freeze: `827dd907d2f8de2cc550b2e4331cc89872d5f1f6`
- sealed cohort ref: `sealed/rc7fb-heldout-cohort-20260831`
- accepted scientific run: `33453256638`
- scientific artifact: `9780509280`
- artifact digest: `sha256:28b35bc37010ee285814b75cb1ddfaae4544394bea10915e290f80390f54d831`
- `RESULTS.json` digest: `sha256:5facef30f9413a7e036b1694c805d5506da67bc8b61cb1c70fd89f392b309634`
- `REPORT.md` digest: `sha256:5cf4fd4ad5b411cf329ec777c515137fb3ed2712732db5c1691c4299e6a95561`

## Result

- held-out cases: `60`
- gold comparison cases: `50`
- true positives: `40`
- false proposals: `0`
- misses: `10`
- typed precision: `1.000000`
- typed recall: `0.800000`
- direction accuracy on resolved gold: `1.000000`
- left/right attachment accuracy on resolved gold: `1.000000`
- false proposals on negative controls: `0`

The candidate therefore fails the preregistered >=0.90 recall gate but exhibits the preferred CAL failure mode: safe abstention/miss rather than invented comparison authority.

## Family decomposition

Perfect on the frozen held-out set:

- numeric delta more/fewer/less: `12/12`
- share/rate direction: `8/8`
- equality/same-as: `6/6`
- multiplier: `6/6`
- scalar threshold: `8/8`
- negative/domain controls: `0/10` false proposals

Missed:

- direct adjective + measure noun comparisons: `0/8`
  - examples used `higher output than` / `greater output than`
- deliberately unsupported verb paraphrases: `0/2`
  - `Division K exceeded Depot F by seven records.`
  - `Center H trailed Lab Z by four modules.`

The first miss family is narrower than a generic relation-extraction failure. The frozen direct-comparison grammar expected the comparative adjective adjacent to `than`; it did not model an intervening measure noun such as `output` except for its separately enumerated `share/rate/percentage/proportion` family.

The two verb paraphrases demonstrate an additional bounded lexical/relation family (`exceed`, `trail`) that is not represented by adjective/delta grammar.

## Evaluator weakness discovered after reveal

The frozen paraphrase-stability evaluator scored the four `higher output than` / `greater output than` pairs as stable because both members produced no proposal. This makes the reported paraphrase stability of `1.0` insufficient evidence of semantic recovery.

This does **not** change the primary typed precision/recall result, because those cases are correctly counted as misses there. A successor evaluator must distinguish:

- `stable_correct` — equivalent meanings both correctly recovered;
- `stable_abstention` — both safely unresolved;
- `stable_wrong` — both recover the same wrong atom.

Do not repair this accepted RC7F-B evaluator and rerun the same held-out set as independent evidence.

## Interpretation

Observed evidence supports a bounded non-LLM comparison instrument architecture:

1. explicit comparison direction is recoverable without an LLM across several important families;
2. when this candidate resolves, direction and entity attachment were perfect on the held-out set;
3. precision-first abstention avoided all negative/domain traps;
4. remaining residue is concretely localized to adjective+measure-noun attachment and comparative verbs, not generic language understanding.

A small successor should first generalize the relation grammar to an explicit `comparative adjective -> measure head -> than -> right entity` structure and add a bounded comparative-verb lexicon or relation extractor. A learned encoder relation extractor is only justified if that bounded extension fails on a fresh cohort.

## Production / authority impact

None. A comparison measurement, even if correct, remains a proposal. It must later be scoped and warranted before any downstream authority can rely on it.
