# RC7B Fresh Independent Interpretation-Authority Reproduction — Implementation B

## Classification

CONTEXT-FREE REQUIRED. Clean-room / independent implementation reproduction.

## Objective

Independently implement the frozen Interpretation Authority Contract v1 from only the authorized aperture. Determine whether source text can be converted into field-level warrant receipts without inventing semantic authority. Do not try to make the implementation pass hidden evaluation.

The structured query is already typed. Query parsing is out of scope.

## Starting repository

`camerontjs-dot/claim-audit-lab`

Create branch:

`research-infra/interpretation-authority-rc7b-b-fresh-20260830`

from the exact aperture head supplied in the launch prompt.

Create implementation only under:

`research/interpretation_authority_rc7b_b/`

Required implementation files:

- `__init__.py`
- `interpret.py` exposing `interpret(text: str, query: dict) -> dict`
- `test_contract_sentinels.py`
- `IMPLEMENTATION_NOTES.md`
- `FREEZE_RECEIPT.json`

Required workflow:

- `.github/workflows/research-freeze-interpretation-authority-rc7b-b.yml`

## Exact pre-freeze allowlist

Before implementation freeze, you may read only the following files at the exact aperture head supplied by the launch prompt:

1. `research/interpretation_authority_rc7b_aperture/INTERPRETATION_AUTHORITY_CONTRACT-v1.md`
2. this bootstrap file: `research/interpretation_authority_rc7b_aperture/BOOTSTRAP-B.md`

You may also read back files you create under your own implementation path and your own workflow.

You may inspect only the exact Git identity required to verify the aperture head and your own branch/PR/run identities.

Python 3.11 standard library is allowed.

## Pre-freeze denylist

Do not read, search for, infer from, or ask for any of the following before freeze:

- RC7A source code, corpus, oracle, gate, legacy comparator, workflows, artifacts, PR #53 discussion/results, or branch contents;
- RC6 extraction implementations, corpora, results, workflows, artifacts, or PR #51;
- fresh text-to-typed-authority reproduction implementation/results/evaluator material or PR #52;
- RC4/RC5/RC5A/RC5B corpora, builders, or oracle implementations;
- any hidden/sealed RC7B evaluator branch, corpus, payload, mutations, expected outputs, hashes, or artifacts;
- any other RC7B implementation branch, code, PR, notes, workflow, run, or receipt;
- broad GitHub code search, PR search, issue search, branch listing, repository-wide orientation, or web search;
- surrounding CAL Pipeline conversation, project summaries, memory, prior reasoning, or expected outcomes;
- external LLM/model APIs, NLP services, or online parsers.

The semantic consumer is intentionally not available pre-freeze. The task is to implement the receipt contract, not to tune against final relations.

## Implementation posture

- Implement from the normative contract and its public Appendix A examples only.
- Do not hard-code sentinel text, hashes, or case IDs.
- Do not use exact-sentence lookup tables.
- Generalize by semantic/linguistic construction.
- Preserve `semantic_unknown`, `extraction_unresolved`, and `insufficient_authority` as distinct outputs.
- When the source lacks warrant, use `insufficient_authority`; do not substitute semantic `unknown`.
- When the source is in jurisdiction but your implementation cannot recover a unique value, use `extraction_unresolved`.
- Use `out_of_jurisdiction` only for unsupported semantics/composition, not parser difficulty.
- Every semantic assignment must carry a valid source span and allowed warrant rule.
- Fail closed rather than inventing authority.

## Contract tests

Create self-authored sentinel tests derived only from the public contract and Appendix A examples. Test every family, all four field statuses where legal, span validation, semantic-unknown versus insufficient-authority separation, passive role preservation, quantifier normalization, and out-of-jurisdiction behavior.

## Draft Research PR

Open a Draft Research PR against the exact aperture branch supplied in the launch prompt. The PR is an evidence record, not authorization for production or reveal.

## Freeze protocol

Freeze before discovering any hidden evaluator material.

1. Commit the implementation and sentinel tests.
2. Create the model-free freeze workflow.
3. The freeze workflow must begin with a shallow exact-ref checkout (`fetch-depth: 1`). If ancestry verification needs more history, fetch only the exact aperture SHA and your own exact head/branch history with explicit refspecs. Never fetch `refs/heads/*`, list remote branches, or use a full-history checkout.
4. Verify:
   - exact aperture head is an ancestor;
   - only authorized aperture files plus your own files were used;
   - all self-authored contract sentinels pass;
   - implementation sources compile;
   - no hidden evaluator/ref has been read.
5. Upload a freeze artifact containing source hashes and sentinel result summary.
6. Record `FREEZE_RECEIPT.json` with:
   - implementation identity `B`;
   - aperture branch/head;
   - implementation freeze commit;
   - SHA-256 for implementation source and sentinel test;
   - run ID, artifact ID, artifact digest;
   - exact pre-freeze files read;
   - explicit denylist-not-read statement;
   - deviations/contamination.
7. After the accepted freeze, the implementation and sentinel tests are immutable.

## Contamination rule

If any denylisted content, hidden evaluator information, other implementation content, or prior extraction implementation/result is exposed before the accepted freeze:

1. stop immediately;
2. preserve the exposure record;
3. mark the execution `CONTAMINATED`;
4. do not continue and later relabel it independent.

## Stop point

After a successful clean freeze, stop. Do not search for evaluator/reveal material.

Return only the compact handoff:

- implementation ID;
- branch;
- Draft PR;
- aperture branch/head;
- implementation freeze SHA;
- freeze receipt commit;
- freeze run/artifact/digest;
- implementation/test hashes;
- exact pre-freeze files read;
- deviations/contamination status;
- state `READY_FOR_REVEAL`.

Do not compare with another implementation before reveal.

## Non-authorization

This run does not authorize production parser changes, LLM/model changes, semantic operator changes, Contract C changes, aggregation changes, downstream policy changes, merging research code, or production promotion.
