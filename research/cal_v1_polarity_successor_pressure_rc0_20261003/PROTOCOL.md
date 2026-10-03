# Polarity successor pressure protocol

This campaign pressure-tests one frozen CAL product. It does not repair that product, and it does not assign a version, merge, tag, or release.

## Subject

The product is commit `64b6c7702696c851057c1cf0b2c105b1c81db543`, tree `62c32ab15489e6c3b20e63efb500c0fa26d0084d`, semantic implementation `caa0048f8f511ec3c4aa1ce713766f2219a04bc1`. Distribution string `0.6.0` is observed and is not a version assignment.

Included external authority, already qualified and not modified here:

- Contract C candidate `c183d2d12306ee30c509169a58db55e7430fe8c5`, blob `aeb50dee8d24bda5f62eb879654e80437a50912d`
- Resolver `292168222f83c67a24190b4846eebe84392e3d04`, blob `b9297ba06beefe1de8488bc25a4c424b0e10e58b`
- RC2 validator `b42c827acb0a9fe65353354d709add0e27bab307`, blob `1d2ecd228cde807138013c33c8675c3003421d3c`
- Maintained Decision `cadef9e103edeba32f1247b99d81d5e25175bcd9`
- Released Contract D `298a1a0f7b7b6d7712e11200d04faec3e1ca169b`
- Apparatus issue #166 disposition `SUPPORTED_POLARITY_SUCCESSOR_DOWNSTREAM_DECISION_D_CONFORMANCE`

Excluded: authentic-authoring implementation `eb1de81c36683c4239ee5eef6a26ea1079b31ce2` and draft PR #202. Issue #193 remains `FALSIFIED_EXISTING_TARGET_FIELD_MODEL_INSUFFICIENT`. Authoring refusal is a limit of this candidate. Convergence commit `6bb0d60f3e2286123f56de5657de4e97d6374c63` is not the subject.

The negative Contract C control is the live apparatus workbench, observed at freeze preparation as `3934423b1a97ad1b099057c40fe8014e5dd08c97`. The required behavior is rejection of any checkout that is not the pinned commit. The positive control uses temporary detached worktrees of the three pins and removes them before the runner returns.

## Seams

Semantic cases call `author_target` and then `audit` on an `AuditContext`. That is the qualified polarity seam. `validate_target_conformance` needs a full Contract B bundle and is not re-executed. The structural gate calls `_validate_target`. The conformance predicate is the production comparison of family and complete field map against a fresh `author_target` of the same claim text.

Parent cases call `verify_external_authorities`, `_load_authority_modules`, and `recompose` on real objects. Supply order of a commutative `all_of` is an invariance test. A declared child sequence other than `1..n` must be rejected.

`AdmittedPassage.verify` binds passage text and only format-checks `source_sha256`. A decision after a well-formed source-hash substitution is an `INTERFACE_GAP`. A passage-text hash mutation must be rejected before a decision. Unknown aperture keys that still reach a conclusion are an `INTERFACE_GAP`.

`OPS-COLLISION` is two callers against one pre-filled output directory. Both must be refused. `OPS-EMPTY-RACE` is two callers against one empty directory. The helper does not lock. Both accepting is an `INTERFACE_GAP`. Both rejecting is a stronger pass. `OPS-DET-ROOTS` and `OPS-LOCALE` compare two probe processes of `SC-DID-NOT` under `C`/`UTC`/`PYTHONHASHSEED=0` and `en_US.UTF-8`/`America/Toronto`/`PYTHONHASHSEED=1`.

Wheel and sdist probes install the built artifact into a clean Python 3.11 environment and require the same `contradicted` conclusion as the source tree on the adjacent `did not` sentence. A wrong terminal direction is `CRITICAL_FAIL`. A build or install failure is `DEVIATION`.

## Real sources

`SOURCE_POOL.json` is the complete pool and process order. The #189 cohort is excluded. `select_window.py` applies the mechanical window. The concise claim, the exact passage, and any inverse are written into `COHORT.json` before CAL is imported. A source that does not honestly map is `NO_ELIGIBLE_ACTIVE_FAMILY_CLAIM`. No source is replaced because CAL performs badly.

Real-claim classes stay distinct: `CRITICAL_FAIL`, `ROBUSTNESS_LIMIT`, `AUTHORING_LIMIT`, `INTERFACE_GAP`, and `PASS`. Abstention and authoring refusal are not semantic success.

## Weak gates

The weak systems live only in this harness:

- ignore assertion polarity
- collapse a scoped comparison to bare lhs, rhs, and direction
- accept any string-to-string field map
- accept any non-empty producer identity

If the real candidate and a weak system clear the same gate, the disposition is `PRESSURE_INCONCLUSIVE_EVALUATOR_NOT_DISCRIMINATING`.

## Run rule

One decisive command, after the freeze commit:

`python3.11 research/cal_v1_polarity_successor_pressure_rc0_20261003/evaluate.py --execute`

The decisive interpreter is Python 3.11.15. The command is run from the campaign worktree.

The runner refuses a dirty tree, a HEAD still equal to the product commit, a product commit that is not an ancestor, a blob that differs from `HARNESS_FREEZE.json`, and an existing `evidence/decisive-run-01`. An uncaught exception writes that directory with `PRESSURE_INCONCLUSIVE_APPARATUS_INVALID` and is preserved. The candidate is not repaired inside this campaign.

## Dispositions

- `PRESSURE_FALSIFIED_CRITICAL_SEMANTIC_FAILURE` stops V1 promotion progression.
- `PRESSURE_SUPPORTED_NO_CRITICAL_FAIL_WITH_DOCUMENTED_LIMITS` does not establish universal accuracy, fresh blind gold, a public interface, or a release.
- `PRESSURE_INCONCLUSIVE_EVALUATOR_NOT_DISCRIMINATING`
- `PRESSURE_INCONCLUSIVE_APPARATUS_INVALID`
- `PRESSURE_BLOCKED_REQUIRED_SUBJECT_OR_SOURCES_UNAVAILABLE`
