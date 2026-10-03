# Preregistration

Frozen before any CAL import by the decisive runner.

## Identity

- Product commit `64b6c7702696c851057c1cf0b2c105b1c81db543`
- Product tree `62c32ab15489e6c3b20e63efb500c0fa26d0084d`
- Semantic implementation `caa0048f8f511ec3c4aa1ce713766f2219a04bc1`
- Contract C `c183d2d12306ee30c509169a58db55e7430fe8c5` blob `aeb50dee8d24bda5f62eb879654e80437a50912d`
- Resolver `292168222f83c67a24190b4846eebe84392e3d04` blob `b9297ba06beefe1de8488bc25a4c424b0e10e58b`
- RC2 `b42c827acb0a9fe65353354d709add0e27bab307` blob `1d2ecd228cde807138013c33c8675c3003421d3c`
- Decision `cadef9e103edeba32f1247b99d81d5e25175bcd9`
- Released Contract D `298a1a0f7b7b6d7712e11200d04faec3e1ca169b`
- Authoring change included: no
- Interpreter for the decisive run: Python 3.11.15 at the operator python3.11

## Files frozen before exposure

`SUBJECTS.json`, `SOURCE_POOL.json`, `MATRIX.json`, `PROTOCOL.md`, `PREREGISTRATION.md`, `weak_systems.py`, `build_matrix.py`, `evaluate.py`, `fetch_sources.py`, `select_window.py`, `record_freeze.py`.

Frozen after retrieval and before exposure, in the same commit as `HARNESS_FREEZE.json`: `RETRIEVAL.json`, `COHORT.json`, `SELECTION_WINDOW.json`, and the raw bodies. `record_freeze.py` writes the blob map. The decisive runner refuses if any recorded blob differs.

## Classifications

`PASS` means the preregistered conclusion or an explicit required rejection. `CRITICAL_FAIL` means a wrong terminal direction, a contradiction treated as support or the reverse, a required authority rejection that instead decides, a materially different target meaning that passes the field-exact predicate, or a nondeterministic semantic result across `SC-ORDER-A` and `SC-ORDER-B`. `ROBUSTNESS_LIMIT` means safe loss of coverage. `AUTHORING_LIMIT` means the current authoring surface refuses an honest claim. `INTERFACE_GAP` means safe behavior depends on a caller precondition the seam does not enforce. `DEVIATION` means the harness did not obtain the preregistered observation.

`not_checkable` on a canonical in-grammar sentence whose preregistered conclusion is `supported` or `contradicted` is `CRITICAL_FAIL`, except `SC-ORDER-A` and `SC-ORDER-B`, where a shared `not_checkable` is `ROBUSTNESS_LIMIT` because one passage is outside the comparison grammar. A difference between those two cases is `CRITICAL_FAIL`.

## Invariants

- One adjacent `did not` refutes the same comparison orientation.
- `not higher` does not decide `lower`.
- Unsupported negation, including double negation, does not decide.
- Negative event polarity does not decide.
- Mixed, irrelevant, equality, and multiple-cue inputs do not decide.
- Evidence order and duplicate admission do not change a conclusion.
- Casing and punctuation outside the grammar do not invent a direction.
- Internal collapsed whitespace does not change the comparison.
- A scoped claim is not represented by bare lhs, rhs, and direction.
- Missing, stale, extra, replayed, or mis-sequenced child authority fails explicitly.
- The wrong Contract C checkout and the wrong semantic identity fail explicitly.
- The pinned checkouts verify.
- Distinct probe roots and locale, timezone, and hash-seed variation keep the same conclusion where determinism is claimed.
- Overwrite, non-directory, symlink, and nonempty collision are refused.

## Cohort rule

The source pool and selection rule in `SOURCE_POOL.json` are fixed. Claims are agent judgments recorded before CAL execution. They are not human gold. Inverses are frozen only where the source logically settles the paired claim. `NO_ELIGIBLE_ACTIVE_FAMILY_CLAIM` is recorded instead of forcing a family.

## What a clean result does not justify

Universal accuracy, a fresh blind human gold set, a public interface, a version, a merge, a tag, or a release. A critical failure freezes the counterexample and stops V1 promotion progression.
