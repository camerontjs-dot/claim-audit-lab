# Strict-comparison polarity successor RC0

`SUPPORTED_FOR_POLARITY_SUCCESSOR_QUALIFICATION`. The frozen #188 passage `Alpha did not have a higher rate than Beta.` now contradicts `Alpha had a higher rate than Beta.` The warranted atom keeps `relation: MORE_THAN` and records `assertion_polarity: negative`. The same atom leaves `Alpha had a lower rate than Beta.` unresolved.

This is support for one polarity field on the frozen discriminator. Package version stays `0.6.0`. Release progression stays stopped.

## Question

Issue #190 asks whether the existing `strict_comparison` path can carry assertion polarity through measurement, source completion, and relation derivation. The #188 failure was `supported` on a passage that denies the comparison. The hypothesis is that the representation dropped polarity before the relation, and that putting polarity back on that same path removes the falsifier.

Scientific parent: `6bb0d60f3e2286123f56de5657de4e97d6374c63`, tree `6b09583c86800118862dd5428ce8508e6fc5f2e8`. Adverse record: issue #188, Draft Research PR #189, counterexample freeze `9bd10b6fe86e3dd91808df906688d82abe9cb325446c859b26a00015187f747b`.

## Apparatus

The cases and runner were committed before the semantic edit. The first decisive file was written once, against the implementation commit, and then committed unchanged.

- Preregistration: `be9b6bed3313bccbfa3b32e91c23d7de820bffd1`, tree `6fc0a86881390c8904e863f634ce238dbfa675d4`.
- Evaluator commit: `68d77aa621079d74be947de90c171a426e1b6890`, tree `66a6bb685552b4c3ca4fc17011ead39a38e2292a`.
- `CASES.json` SHA-256: `1f602f9e79a70745e3b4eff39d675810fbdeaa7653444895181b5906e3dde721`.
- `evaluate.py` SHA-256: `a406699bbd5a595c55d2853ba54c1938d668396b1931988a25f748ea4ddfa695`.
- Implementation: `caa0048f8f511ec3c4aa1ce713766f2219a04bc1`, tree `07cd41c4efe6a5570cdc46c4ab5f2cf8788df56f`.
- Decisive-run commit: `9948614dd5d41bd2ffac36d2502def8f34e43e09`.
- `decisive-result.json` SHA-256: `ec84150b07c60e43794282c60ad35b21e82db923ce1d034c96ba81a15a6dee5e`.

The result file records head `caa0048f8f511ec3c4aa1ce713766f2219a04bc1` and tree `07cd41c4efe6a5570cdc46c4ab5f2cf8788df56f`. Those are the implementation commit. Instrument id stays `rc7fb1-strict-comparison`. Instrument version on the run is `strict-comparison-polarity-rc0`.

The runner calls `author_target` and `audit`. Preserved output: [decisive-result.json](evidence/decisive-run-01/decisive-result.json). The twenty authentic-source refusals from #189 are outside this acceptance set.

## Observations

The run matched 33/33. Failed count 0. Apparatus errors 0. Polarity-boundary mismatches 0. On every case that produced both a measurement proposal and a warranted atom, `assertion_polarity` was the same on both.

| Case | Observed conclusion | Warranted atom | Categorical relation |
|---|---|---|---|
| D1 positive higher | `supported` | positive `MORE_THAN` alpha/beta | `SUPPORTS` |
| D2 positive opposite | `contradicted` | positive `LESS_THAN` alpha/beta | `REFUTES` |
| D3 exact #188 negation | `contradicted` | negative `MORE_THAN` alpha/beta | `REFUTES` |
| D4 `not higher` against a lower claim | `not_checkable` (`RELATION_UNRESOLVED`) | negative `MORE_THAN` alpha/beta | `UNRESOLVED` |
| D4 `not lower` against a higher claim | `not_checkable` (`RELATION_UNRESOLVED`) | negative `LESS_THAN` alpha/beta | `UNRESOLVED` |
| D5 positive entity swap | `supported` | positive `LESS_THAN` beta/alpha | `SUPPORTS` |
| D5 negative entity swap | `contradicted` | negative `LESS_THAN` beta/alpha | `REFUTES` |
| D5 swapped claim, same negation | `contradicted` | negative `MORE_THAN` alpha/beta | `REFUTES` |
| D6 `never`, `hadn't`, `did not not`, `a not higher`, `cannot` | `not_checkable` (`MEASUREMENT_MISS`) | no atom | diagnostic `unrepresentable` |

Twenty retained strict-comparison controls matched their frozen conclusions: 11 `supported`, 9 `not_checkable`. Unrelated entities stayed `IRRELEVANT`. Plural `rates` stayed unresolved.

Local regression on the implementation bytes, Python 3.11.15, immediately before commit `caa0048`: `pytest -q` reported 977 passed, 5 skipped, 48 deselected. `ruff check src tests`, `ruff format --check src`, and `mypy` reported no issues in 71 source files. `src/` and `tests/` at the decisive-run commit are that same implementation commit.

The #186 convergence qualification pins production semantic bytes to `847cc970642bb648dc994b929c2053b5c9d4648c`. This successor changes those bytes, so that identity gate is a different question and was not rerun.

From `6bb0d60` through `caa0048`, the diff is the preregistration, the frozen evaluator, `authority.py`, `measurements.py`, `relations.py`, and `tests/test_strict_comparison_polarity.py`. `direct_event_order`, Contract B, Contract C, parent composition, target authoring, schemas, and `pyproject.toml` version are untouched.

## Inference

Measurement and source completion were storing the comparison direction and dropping the negation that sat between the left entity and the cue. Both parsers now classify that span. One adjacent `did not` is negative. No overt marker is positive. Any other overt marker in the span (`n't`, `not` outside that frame, `never`, `no`, `without`, `neither`, `nor`, `cannot`) yields no proposal and no atom.

The relation reads `assertion_polarity` from the warranted atom. A negative comparison refutes the claim with that same orientation. The other orientation stays `UNRESOLVED`, so `not higher` stays `MORE_THAN` and does not become support for `lower`. Entity mismatch stays `IRRELEVANT`.

I read the 33/33 match as support for that representation on these cases. The disposition name is the preregistered label for that support. It is a qualification candidate for this successor, and it is not a release decision.

## Boundary

The closed negative frame is one adjacent `did not`. D6 is the evidence that the other surfaces abstain. Admitting them would be a new representation question, and I would not answer it by listing phrases.

Still outside this result: real-source comparison prose, the #189 authoring refusals, Contract B provenance, Contract C, parent composition, and the frozen #186 byte identity. Nothing here merges the successor or resumes CAL 1.0.
