# Polarity successor pressure

Disposition: `PRESSURE_SUPPORTED_NO_CRITICAL_FAIL_WITH_DOCUMENTED_LIMITS`.

The frozen product did not emit a wrong terminal direction, a polarity inversion, or a required authority acceptance on the synthetic matrix. The fresh public cohort did not produce a single semantic decision. All 26 authored claims were refused by the current target grammar. That is an authoring limit, not evidence that authentic prose audits correctly.

No version, merge, tag, or release follows from this run.

## Subject

| Authority | Identity |
| --- | --- |
| Product commit | `64b6c7702696c851057c1cf0b2c105b1c81db543` |
| Product tree | `62c32ab15489e6c3b20e63efb500c0fa26d0084d` |
| Semantic implementation | `caa0048f8f511ec3c4aa1ce713766f2219a04bc1` |
| Contract C candidate | `c183d2d12306ee30c509169a58db55e7430fe8c5`, blob `aeb50dee8d24bda5f62eb879654e80437a50912d` |
| Resolver | `292168222f83c67a24190b4846eebe84392e3d04`, blob `b9297ba06beefe1de8488bc25a4c424b0e10e58b` |
| RC2 validator | `b42c827acb0a9fe65353354d709add0e27bab307`, blob `1d2ecd228cde807138013c33c8675c3003421d3c` |
| Maintained Decision | `cadef9e103edeba32f1247b99d81d5e25175bcd9` |
| Released Contract D | `298a1a0f7b7b6d7712e11200d04faec3e1ca169b` |
| Authoring change | excluded; issue #193 remains `FALSIFIED_EXISTING_TARGET_FIELD_MODEL_INSUFFICIENT` |

Decision and Contract D are in the supported path because apparatus-contracts #166 already recorded `SUPPORTED_POLARITY_SUCCESSOR_DOWNSTREAM_DECISION_D_CONFORMANCE`. This campaign did not rerun that downstream arm and does not replace it.

## Harness

Preregistration commit `0a6e0050cbc9cc05cd1076f9b8ea0c70b29c3611`. Published cohort and custody commit `a48ce6cf3fe6cc3980352acfca461ec26def5084`. Published successor harness `3e3b03b15ce9ac774f7451522dd3d37db6658863`.

Run 01 evaluator blob `15a4feadba6c72f99c016dbf167513aab9c9a169`. Run 02 evaluator blob `8703b8244ee099156c622d7ba9372b05a26ec931`.

`evidence/decisive-run-01` is the preserved first execution. Bare Python 3.11.15 had no `pydantic`, so CAL was not imported. Disposition of that run: `PRESSURE_INCONCLUSIVE_APPARATUS_INVALID`. Its `head` field is `9f83bf0e31a3d0de5acb26e9891f2ff682f6cee1`, the execution-time custody commit.

`evidence/decisive-run-02` is the successor. The only harness change was a Python 3.11 virtualenv with the declared runtime dependencies `pydantic`, `PyYAML`, and `typer`. The candidate bytes were not changed. Result SHA-256 `fc2844be3a43718c4fd572741016f7953713f4a8b3b1cda8e42bfa4736bb91ec`. Interpreter `3.11.15`. Its `head` field is `111d7a070acb114eb69ae512695590f8640f9c10`, the execution-time harness commit.

Those two execution heads are not in the published history. GitHub push protection rejected the first push because the NIST HTML contained one Mapbox access token in page configuration. I replaced that token with `[REDACTED-MAPBOX-TOKEN]` and rewrote the unpushed commits. The download SHA-256 `6dade421aa7a3dc2b190d73fab57dc64628bfd741accd954673b010e5752eed9` and execution blob `84d620b9cbf21f1dd666eb5f875eea5e040be19d` are the bytes both decisive runs read. The selected passage does not include the token. I did not edit either `result.json`. The published freeze map names the redacted blob `939d10f23bc4891685b29a487bfc329fc7436c8a`.

The semantic seam is `author_target` plus `audit`. `validate_target_conformance` needs a full Contract B bundle and was not re-executed. The structural gate called `_validate_target`. The field-exact check compared a mutated target with a fresh `author_target` of the same claim.

## Aggregate

95 rows: 52 `PASS`, 26 `AUTHORING_LIMIT`, 9 `NO_ELIGIBLE_ACTIVE_FAMILY_CLAIM`, 5 `ROBUSTNESS_LIMIT`, 3 `INTERFACE_GAP`. Zero `CRITICAL_FAIL`. Zero `DEVIATION`.

The four weak gates discriminated:

| Gate | Real candidate | Weak system |
| --- | --- | --- |
| Ignore `did not` | `contradicted` | `supported` |
| Collapse scoped comparison | authoring refused | bare `Alpha` / `Beta` / `MORE_THAN` |
| Structural target check | `_validate_target` accepted a direction mutation; the field-exact predicate rejected it | accepted the mutation |
| Producer identity | wrong semantic identity rejected | any non-empty SHA accepted |

## What held

`SC-DID-NOT` audited `Alpha had a higher rate than Beta.` against `Alpha did not have a higher rate than Beta.` and returned `contradicted`. `SC-NOT-HIGHER-VS-LOWER` kept `not higher` from deciding `lower` and returned `not_checkable` (`RELATION_UNRESOLVED`). `SC-NEVER` and `SC-DOUBLE-NEG` stayed `not_checkable`. Event polarity `EV-NEGATIVE` stayed `not_checkable`. `SC-ORDER-A` and `SC-ORDER-B` both returned `supported`.

Passage-hash mutation, stale child, missing child, extra child, replayed result id, bad child sequence, empty Contract B version, the live apparatus HEAD, and a semantic-identity substitution were rejected. The pinned Contract C, RC2, and resolver checkouts verified. Supply order of the commutative `all_of` stayed `supported`.

`AUTH-CROSS-WORLD` was rejected as `PROPOSITION_BINDING_FAILED: relation/context mismatch`. The context hash changes with the world, so the world-specific code was not the one observed. The traces did not compose.

The live apparatus HEAD fails `verify_external_authorities` at the Contract C checkout. `AUTH-WRONG-RESOLVER` records that same exception. The resolver pin is covered by the positive control, which verified all three checkouts, not by a separate negative message.

Wheel `claim_audit_lab-0.6.0-py3-none-any.whl` SHA-256 `c7a0aea6e10f5cb923778d4903582d08439d8f92965bb9f37382e26c59f90070` and sdist `claim_audit_lab-0.6.0.tar.gz` SHA-256 `dd4fd665b8e134bfbf90a4a9ec03a30e251468d690d7c21f5c3aa19ebebc8c70` both returned `contradicted` on the same `did not` sentence. Two locale, timezone, and hash-seed probes returned the same conclusion. Non-empty output, overwrite, non-directory, and symlink destinations were refused. Two distinct output directories both succeeded.

## Limits

Robustness, still safe: lowercase comparison and event prose, an exclamation mark, a comma in an event sentence, and the longer event sentence `EV-COMPLEX` all returned `not_checkable` with `MEASUREMENT_MISS`.

Interface gaps:

- A well-formed substituted `source_sha256` still produced `supported`. Passage text is bound. The caller-supplied source hash is only format-checked.
- An unknown aperture key still produced `supported`.
- Two callers both passed `_destination_available` on one empty directory. The helper does not lock.

Authoring: the grammar still stores a strict comparison as lhs, rhs, and direction, or an event as the closed nine-field form. Scoped, qualified, and ordinary public sentences do not fit. Refusal is the safe behavior. It is not a semantic pass.

## Fresh sources

The pool was S01–S16, fixed before retrieval. The #189 cohort was not reused. BLS S01–S04 and CDC S09 returned access-denied pages. I did not retry them with another client. Census S05 and BEA S06 returned 404. EIA S07 was a discontinuation notice with no in-scope relation. FDA S15 had no in-scope factual relation in the window. Those nine rows are `NO_ELIGIBLE_ACTIVE_FAMILY_CLAIM`.

The other sources contributed 13 forward claims and 13 inverses. Claims were written from the source before CAL ran. They are agent judgments, not human gold. Every one was `AUTHORING_LIMIT`.

| Case | Family | Source relation | Result |
| --- | --- | --- | --- |
| S08-C1 | strict comparison | supports / refutes | authoring refused |
| S08-C2 | strict comparison | supports / refutes | authoring refused |
| S10-C1 | strict comparison | supports / refutes | authoring refused |
| S10-C2 | strict comparison | supports / refutes | authoring refused |
| S11-C1 | strict comparison | supports / refutes | authoring refused |
| S11-C2 | strict comparison | supports / refutes | authoring refused |
| S12-C1 | strict comparison | supports / refutes | authoring refused |
| S12-C2 | strict comparison | supports / refutes | authoring refused |
| S13-C1 | strict comparison | supports / refutes | authoring refused |
| S13-C2 | strict comparison | supports / refutes | authoring refused |
| S14-C1 | strict comparison | supports / refutes | authoring refused |
| S14-C2 | strict comparison | supports / refutes | authoring refused |
| S16-C1 | event order | supports / refutes | authoring refused |

S08-C1 is the representative refusal. The passage says markets' reaction to trade-policy information was more restrained than in April and May. The forward claim keeps that scope. The authoring surface refused it. The weak collapse still extracted a bare comparison from the synthetic scoped sentence, so the gate can tell those behaviors apart.

Custody hashes and URLs are in `RETRIEVAL.json`. Exact passages and claim text are in `COHORT.json`.

## What this does and does not justify

This supports a bounded claim: on this exact tree, the frozen synthetic, authority, packaging, and weak-system matrix did not show a critical semantic failure, and the documented limits above are real.

It does not support universal accuracy, a fresh blind gold set, a public interface, or a release. It does not show that CAL can audit the held-out public sentences. Issue #193 stays falsified. I am not repairing the grammar in this campaign.

There is no critical counterexample to freeze, so this run does not itself stop V1 promotion on a semantic falsifier. It also does not open promotion. The authoring limit still blocks any claim that this candidate can take authentic public prose.

## Next gate

A context-free, successor-specific independent review of this frozen receipt is warranted before any further promotion step. The review question is whether `PRESSURE_SUPPORTED_NO_CRITICAL_FAIL_WITH_DOCUMENTED_LIMITS` follows from the frozen cases and the two preserved runs. It is not a release review, and it should not treat authoring refusal as semantic success.

The reviewer needs product `64b6c770`, published harness `3e3b03b15ce9ac774f7451522dd3d37db6658863`, run 01 blob `15a4feadba6c72f99c016dbf167513aab9c9a169`, result `fc2844be3a43718c4fd572741016f7953713f4a8b3b1cda8e42bfa4736bb91ec`, and the cohort file. The result's own `head` is the execution-time commit `111d7a070acb114eb69ae512695590f8640f9c10`, which is not the published harness commit. The evaluator bytes are the same. I would keep the reviewer off the authoring implementation `eb1de81c` and off any repair of `src/`.
