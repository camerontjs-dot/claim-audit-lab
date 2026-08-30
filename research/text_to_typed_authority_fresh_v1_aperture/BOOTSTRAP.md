# Fresh Independent Text-to-Typed-Authority Reproduction v1 — Bootstrap

## Classification

**CONTEXT-FREE REQUIRED**

Research Infrastructure / independent semantic-extraction reproduction.

This task tests implementation independence. Do not import surrounding CAL Pipeline conversation, RC6 discussion, prior extractor reasoning, prior extractor outputs, hidden evaluator state, or expected answers.

## Exact objective

Using only the authorized pre-freeze aperture below, independently implement a deterministic extractor that maps `(text, query_text)` to the frozen typed-authority contract in `EXTRACTION_CONTRACT-v1.md`, or returns an explicit extraction-unknown state when the text does not warrant one typed object.

Determine whether a fresh implementation can recover enough of the frozen authority to preserve downstream semantic relations without fabricating authority.

Do not try to make the reproduction pass. Preserve every disagreement and abstention.

## Starting authority

Repository:

`camerontjs-dot/claim-audit-lab`

Semantic ancestor:

`c623af35bee3b5f685c9a44e6d91ced006b2d690`

This aperture branch is intentionally separate from the prior extraction experiment.

## Pre-freeze allowlist

Before implementation freeze, you may read only:

1. this file;
2. `research/text_to_typed_authority_fresh_v1_aperture/EXTRACTION_CONTRACT-v1.md`;
3. Git identity for the exact aperture branch/head;
4. files you create yourself under:
   - `research/text_to_typed_authority_fresh_v1/`
   - `.github/workflows/research-freeze-text-to-typed-authority-fresh-v1.yml`
5. GitHub Actions runs produced by your own fresh branch.

You may use Python 3.11 standard library.

Do not use web search, external models, external APIs, or repository-wide code search before freeze.

## Pre-freeze denylist

Do **not** read, search, open, summarize, or infer from any of the following before implementation freeze:

- PR #51 or any prior extraction PR narrative/comments;
- branch `research-infra/text-to-typed-authority-extraction-rc6-20260830`;
- any path matching `research/text_to_typed_authority_extraction_rc6*`;
- any prior extractor implementation, test, corpus, result, counterexample, workflow, Actions artifact, or log;
- RC4 text parser/decomposer candidates or corpora;
- RC5/RC5A/RC5B corpora, builders, oracle, direct-consumer source, tests, results, PR bodies, comments, or workflows;
- repository-wide branch listings, broad GitHub search, historical PR search, issue search, or code search used for orientation;
- hidden/reveal evaluator branches or artifacts;
- any surrounding CAL Pipeline conversation or memory.

The semantic contract file in the allowlist is the complete pre-freeze specification. If it is insufficient, record the ambiguity rather than broadening the aperture.

## Required implementation

Create a fresh branch from this aperture head:

`research-infra/text-to-typed-authority-fresh-reproduction-v1-20260830`

Implement exactly:

- `research/text_to_typed_authority_fresh_v1/__init__.py`
- `research/text_to_typed_authority_fresh_v1/extractor.py`
- `research/text_to_typed_authority_fresh_v1/test_contract_sentinels.py`
- `research/text_to_typed_authority_fresh_v1/IMPLEMENTATION_NOTES.md`
- `research/text_to_typed_authority_fresh_v1/FREEZE_RECEIPT.json`
- `.github/workflows/research-freeze-text-to-typed-authority-fresh-v1.yml`

The public API is exactly:

```python
def extract(text: str, query_text: str) -> dict:
    ...
```

Do not add case IDs, family names, expected labels, gold state, or evaluator-specific arguments to the API.

Your sentinel tests must be authored only from the contract and must not use any hidden evaluator material.

## Implementation posture

Prefer a small deterministic implementation over a broad language system.

The purpose is not to solve arbitrary English. It is to test whether the frozen typed authority is independently mechanically consumable from bounded language.

Important constraints:

- no tuning against hidden cases;
- no lookup by exact full input sentence;
- no case-specific hashes or IDs;
- no reference-extractor mimicry;
- no final semantic-label repair;
- do not call the downstream RC5B consumer before freeze;
- preserve `neutral-capable resolved authority` versus extraction unknown;
- fail closed when authority is genuinely absent, ambiguous, or outside the ontology.

## Freeze point

Before reading any post-freeze/reveal material:

1. open a Draft Research PR against the exact aperture branch;
2. commit all implementation/source/sentinel tests;
3. run the model-free freeze workflow;
4. obtain a successful Actions receipt;
5. record in `FREEZE_RECEIPT.json`:
   - aperture head;
   - implementation freeze commit;
   - implementation tree or source hashes;
   - freeze workflow run ID/artifact if used;
   - exact pre-freeze files actually read;
   - statement that denylisted material was not read;
   - any accidental exposure/deviation.

After the freeze receipt is accepted, **do not modify the extractor or its sentinel tests**.

## Contamination rule

If any denylisted information is exposed before implementation freeze:

- stop;
- preserve the exposure record;
- mark the execution `CONTAMINATED`;
- do not continue and later relabel the same implementation independent.

## Reveal boundary

After a successful implementation freeze, stop and return a compact handoff containing:

- fresh branch;
- Draft PR;
- aperture head;
- implementation freeze SHA;
- freeze run/artifact receipts;
- exact pre-freeze sources read;
- contamination/deviation status.

Do **not** search for the evaluator yourself.

The normal CAL Pipeline thread will then supply the exact sealed reveal commit/path. The extractor remains immutable during evaluation.

## Preregistered scientific states for reveal

The sealed evaluator will measure at least:

- in-schema resolved coverage;
- exact typed-object recovery;
- downstream relation preservation through the unchanged frozen semantic consumer;
- unsafe authority fabrication on expected-unknown cases;
- preservation of resolved semantic-neutral cases;
- mutation consistency;
- field-level extraction failures.

`CLEAN_REPRODUCTION` requires all of:

- zero unsafe authority fabrications;
- zero wrong downstream semantic relations among resolved outputs;
- at least 90% in-schema resolved coverage;
- at least 90% exact typed-object recovery;
- at least 90% semantic-neutral preservation;
- every sealed mutation pair passing.

If safety conditions hold but coverage/exactness/mutations miss the clean threshold, classify the scientific state `SAFE_BUT_INCOMPLETE`.

If any expected-unknown case is resolved into invented authority, or any resolved output produces a wrong downstream semantic relation, classify the scientific state `UNSAFE_OR_SEMANTICALLY_INCORRECT`.

These scientific states do not themselves authorize production promotion.

## Non-authorization

This experiment does not authorize:

- production parser changes;
- production entailer/model changes;
- thresholds or ensembles;
- production semantic-operator changes;
- Contract C changes;
- aggregation or downstream decision changes;
- merging prior research extractors into production.

Research failures and counterexamples must be preserved.

## Immediate task

Implement and freeze the fresh extractor now using only the pre-freeze allowlist.

Stop at `READY_FOR_REVEAL` with the freeze receipt. Do not ask for hidden evaluator material before that point.
