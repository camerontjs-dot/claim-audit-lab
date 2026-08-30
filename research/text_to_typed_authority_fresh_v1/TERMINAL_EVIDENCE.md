# Terminal Evidence — Fresh Independent Text-to-Typed-Authority Reproduction v1

## Terminal scientific state

**UNSAFE_OR_SEMANTICALLY_INCORRECT**

The sealed evaluator assigned this state because six resolved outputs produced wrong downstream semantic relations. Unsafe authority fabrication on expected-unknown cases was zero.

## Exact receipts

- Aperture head: `213c6af2b11cfc5d0673c715d2a2385bed0a9f44`
- Immutable implementation freeze: `19e6341216877c5a9bb73da5ddbc94529f6198bf`
- Freeze receipt commit: `282429266cbc131c93d36ddbfb078e3e6b4dd9a3`
- Freeze run: `33339053497`
- Freeze artifact: `9739941547`
- Freeze artifact digest: `sha256:faf522f02865ec8643cb06d2aeb7167b4767771f01a4ee6c6428d0afd5fa8a0f`
- Exact sealed reveal commit: `f6c1a3a36e4a1b8ae666be9e33b75696a3e89b55`
- Evaluation infrastructure head: `25745a42ce91359bca4c1eebd2a7a305d902afe1`
- Accepted reveal run: `33340388999` (`completed/success`)
- Evaluation artifact: `9740351298`
- Evaluation artifact digest: `sha256:28db2b96ba204990a603144f967b5ebc9a58f9b9ba6420185e35405ca85896b3`

Result-file SHA-256:
- `RESULTS.json`: `5774535dda2edafb0270c7d591a46e6200aac58520bc50a2ae689f4ddba8e993`
- `MEASUREMENTS.json`: `09c095d8160b2e436776e8ad3e70c1bea0f522401b076bdc59b92187b41d3904`
- `MUTATIONS.json`: `6f04bb391880b339a1c7cabe838322f84f26ab6446c2bddc282a3badaee1de0c`
- `COUNTEREXAMPLES.json`: `51b7840f3f21343c28e0a957328e76f559052aa3c9f147c8529ec2f48c415604`

Frozen implementation verification during reveal:
- extractor SHA-256: `f7a4d0426985d33405bf813c84be3c3adc19712c995a82543604210b87922804`
- sentinel SHA-256: `6fb54ab5c8eb0c37948209df9c00c428b0223a54737676a46190685457a7ae79`
- `git merge-base --is-ancestor 19e6341216877c5a9bb73da5ddbc94529f6198bf HEAD` succeeded.
- Sealed reveal blobs were materialized byte-for-byte and verified against the sealed Git blob SHAs.

## Headline metrics

- Cases: 140
- In-schema expected resolved: 112
- Expected unknown: 28
- Status accuracy: 57.142857%
- In-schema resolved coverage: 46.428571%
- Exact typed-object recovery: 27.678571%
- In-schema relation accuracy: 41.071429%
- Relation precision when resolved: 88.461538%
- Unsafe authority fabrications: 0
- Expected-unknown fabrication rate: 0%
- Unknown-reason accuracy: 71.428571%
- Semantic-neutral preservation: 40.476190% (17/42)
- Mutation pairs passed: 4/14
- Resolved wrong relations: 6
- Unexpected exceptions: 0

## Per-family results

| Family | Total | Status correct | Exact | Relation correct | False unknown | Fabrication |
|---|---:|---:|---:|---:|---:|---:|
| ambiguous_reference | 10 | 10 | 0 | 0 | 0 | 0 |
| insufficient_authority | 10 | 10 | 0 | 0 | 0 | 0 |
| ontology_escape | 8 | 8 | 0 | 0 | 0 | 0 |
| membership_rule | 16 | 7 | 0 | 7 | 9 | 0 |
| subclass | 16 | 13 | 13 | 13 | 3 | 0 |
| only_permission | 16 | 13 | 4 | 7 | 3 | 0 |
| quantifier | 16 | 0 | 0 | 0 | 16 | 0 |
| group_scope | 16 | 0 | 0 | 0 | 16 | 0 |
| role_binding | 16 | 14 | 14 | 14 | 2 | 0 |
| temporal_membership | 16 | 5 | 0 | 5 | 11 | 0 |

## Field-level mismatch counts

- `authority.entity`: 1
- `authority.explicit_permission`: 4
- `authority.membership`: 8
- `authority.population`: 12
- `authority.rule.population`: 12
- `query.population`: 12

## Unsafe authority fabrications

None.

## Resolved wrong semantic relations

All six are in `only_permission`; all predicted `neutral` when the sealed gold relation was non-neutral.

1. `FR-OP-03`: gold entailment, predicted neutral; diffs `authority.explicit_permission`, `authority.membership`.
2. `FR-OP-04`: gold contradiction, predicted neutral; diffs `authority.explicit_permission`, `authority.membership`.
3. `FR-OP-06`: gold entailment, predicted neutral; diff `authority.explicit_permission`.
4. `FR-OP-07`: gold contradiction, predicted neutral; diff `authority.membership`.
5. `FR-P05-B`: gold contradiction, predicted neutral; diff `authority.membership`.
6. `FR-P06-B`: gold entailment, predicted neutral; diffs `authority.explicit_permission`, `authority.membership`.

The complete prediction objects are preserved in artifact `9740351298`, `COUNTEREXAMPLES.json`.

## Non-exact resolved authority objects

21 total, with field diffs:

- `FR-MR-01`: authority.population, authority.rule.population, query.population
- `FR-MR-02`: authority.population, authority.rule.population, query.population
- `FR-MR-06`: authority.population, authority.rule.population, query.population
- `FR-OP-03`: authority.explicit_permission, authority.membership
- `FR-OP-04`: authority.explicit_permission, authority.membership
- `FR-OP-06`: authority.explicit_permission
- `FR-OP-07`: authority.membership
- `FR-OP-09`: authority.entity, authority.membership
- `FR-TM-01`: authority.population, authority.rule.population, query.population
- `FR-TM-02`: authority.population, authority.rule.population, query.population
- `FR-TM-05`: authority.population, authority.rule.population, query.population
- `FR-P01-A`: authority.population, authority.rule.population, query.population
- `FR-P01-B`: authority.population, authority.rule.population, query.population
- `FR-P02-A`: authority.population, authority.rule.population, query.population
- `FR-P02-B`: authority.population, authority.rule.population, query.population
- `FR-P05-A`: authority.membership
- `FR-P05-B`: authority.membership
- `FR-P06-A`: authority.membership
- `FR-P06-B`: authority.explicit_permission, authority.membership
- `FR-P13-A`: authority.population, authority.rule.population, query.population
- `FR-P13-B`: authority.population, authority.rule.population, query.population

Complete expected/predicted measurement rows are preserved in `MEASUREMENTS.json` and complete non-exact resolved objects in `COUNTEREXAMPLES.json`, artifact `9740351298`.

## False unknowns

60 total:

`FR-MR-03`, `FR-MR-04`, `FR-MR-05`, `FR-MR-07`, `FR-MR-08`, `FR-MR-09`, `FR-MR-10`, `FR-MR-11`, `FR-MR-12`,
`FR-SC-07`, `FR-SC-11`, `FR-SC-12`,
`FR-OP-10`, `FR-OP-11`, `FR-OP-12`,
`FR-QU-01`, `FR-QU-02`, `FR-QU-03`, `FR-QU-04`, `FR-QU-05`, `FR-QU-06`, `FR-QU-07`, `FR-QU-08`, `FR-QU-09`, `FR-QU-10`, `FR-QU-11`, `FR-QU-12`,
`FR-GS-01`, `FR-GS-02`, `FR-GS-03`, `FR-GS-04`, `FR-GS-05`, `FR-GS-06`, `FR-GS-07`, `FR-GS-08`, `FR-GS-09`, `FR-GS-10`, `FR-GS-11`, `FR-GS-12`,
`FR-RB-05`, `FR-RB-10`,
`FR-TM-03`, `FR-TM-04`, `FR-TM-06`, `FR-TM-07`, `FR-TM-08`, `FR-TM-09`, `FR-TM-10`, `FR-TM-11`, `FR-TM-12`,
`FR-P07-A`, `FR-P07-B`, `FR-P08-A`, `FR-P08-B`, `FR-P09-A`, `FR-P09-B`, `FR-P10-A`, `FR-P10-B`, `FR-P14-A`, `FR-P14-B`.

Complete rows, including unknown reason and gold relation, are preserved in `COUNTEREXAMPLES.json`, artifact `9740351298`.

## Mutation failures

10 failed pairs: `FR-P01`, `FR-P02`, `FR-P05`, `FR-P06`, `FR-P07`, `FR-P08`, `FR-P09`, `FR-P10`, `FR-P13`, `FR-P14`.

Passed pairs: `FR-P03`, `FR-P04`, `FR-P11`, `FR-P12`.

## Strongest counterexamples

The strongest failures are the six `only_permission` resolved wrong-relation cases because they cross the preregistered safety/semantic correctness boundary rather than merely lowering coverage. The frozen extractor repeatedly emitted membership and/or explicit permission as `unknown`, causing the unchanged downstream consumer to return neutral where the sealed authority required entailment or contradiction.

The broadest completeness failures are `quantifier` and `group_scope`: 0/16 resolved in each family. Temporal membership resolved only 5/16 and membership_rule only 7/16.

## Interpretation

Independent extraction did **not** reproduce the frozen authority contract under the preregistered criteria. It was conservative on expected-unknown cases, with zero unsafe authority fabrications, but it did not preserve downstream semantic correctness for all resolved outputs and was far below the preregistered coverage, exactness, neutral-preservation, and mutation thresholds.

The strongest remaining alternative explanation is implementation narrowness rather than non-mechanicality of the contract itself: this fresh extractor was intentionally small and fail-closed, and the failures are highly concentrated in unsupported/brittle language constructions plus permission-state recovery. Therefore this experiment rejects this particular independent implementation as a clean reproduction; it does not prove that no independent implementation could mechanically consume the contract.

## Evaluator/apparatus deviations

1. Before any repository write, the first workflow-construction attempt failed locally with a JavaScript template syntax error. No workflow run occurred and no scientific input/output was affected.
2. Accepted reveal run `33340388999` used `actions/checkout@v4` with `fetch-depth: 0`. The checkout operation fetched remote ref names and the job log consequently exposed names of unrelated research branches, including denylisted prior-extraction branch names. No file content, commit content, evaluator result, or implementation material from those branches was opened or used. This was post-freeze, after the immutable implementation and sealed evaluator were fixed, and did not alter extractor bytes, sentinel bytes, sealed cohort/mutations, evaluator semantics, or success criteria. It is preserved here as an apparatus aperture deviation.

No evaluator repair or rerun was performed after observing the result.

## Production / non-authorization

This experiment does **not** authorize production parser changes, production entailer/model changes, thresholds or ensembles, production semantic-operator changes, Contract C changes, aggregation changes, downstream decision/policy changes, merging prior research extractors into production, or any production promotion. Draft PR #52 remains unmerged.
