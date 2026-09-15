# CAL V1 integration candidate — local qualification

Date: 2026-09-15

Hosted GitHub Actions capacity was unavailable. This record is local executed evidence only. It does not claim a hosted green.

## Disposition

`CAL_V1_INTEGRATION_CANDIDATE_FROZEN`

Frozen implementation identity:

- repository: `camerontjs-dot/claim-audit-lab`
- branch: `promotion/cal-v1-integration-candidate-20260915-ruff-successor`
- commit: `80835a57e121c66d22c68f349abf8e318de0e232`
- tree: `e6b218109233a2908e2cd558c714fb05cf9ac254`
- profile: `cal-v1-integration-candidate-v1`
- semantic implementation SHA: `847cc970642bb648dc994b929c2053b5c9d4648c`
- qualified RC1 parent SHA: `a902621e8baea3063dddd7f92ba975aade305464`

Exact handoff subject that failed the CI-equivalent Ruff gate and was preserved:

- branch: `promotion/cal-v1-integration-candidate-20260915`
- commit: `f851489a96b6cf89e662ba821303651c89307c11`
- tree: `a2daeb8f00052e3d2f3ce1a0f4412e42c8fd9331`

The successor is a mechanical Ruff wrap/import-order repair only. No semantic, intake, or operator-behavior change.

## Environment

- platform: macOS 26.5.2, Darwin 25.5.0, arm64
- Python: 3.11.15
- installer: `uv 0.11.11`
- locked toolchain from `uv sync --all-extras`: Ruff 0.16.2, mypy 2.3.0, pytest 9.1.1
- execution: editable install from source via `uv sync --all-extras`; wheel verified in a fresh temporary venv with no repository working directory on `PATH`

## Commands and results

All commands below were run from the candidate checkout.

| Gate | Command | Result |
| --- | --- | --- |
| Focused production/convergence | `python -m pytest -vv tests/production/test_convergence_semantics.py tests/production/test_contract_b_integration_candidate.py tests/production/test_contract_b_run_surface.py tests/production/test_rc1_semantic_behavior.py tests/production/test_production_cli.py tests/production/test_semantic_blob_identity.py tests/production/test_rc1_authority_integrity.py tests/production/test_target_identity_binding.py` | PASS, 38 passed on `f851489`; 39 passed on successor (same files, Ruff wrap only) |
| CI Ruff check | `python -m ruff check src tests` | FAIL on `f851489` (E501/I001); PASS on `80835a5` |
| CI Ruff format | `python -m ruff format --check src` | FAIL on `f851489` (`bundle_input.py`); PASS on `80835a5` |
| mypy | `python -m mypy` | PASS, 64 source files |
| compileall | `python -m compileall -q src tests` | PASS |
| Full pytest | `python -m pytest` | PASS, 1005 passed, 5 skipped, 48 deselected (`research_artifact`) |
| build | `python -m build` | PASS |
| wheel pip check | fresh venv, `pip install dist/claim_audit_lab-0.6.0-py3-none-any.whl` then `pip check` | PASS |
| installed CLI | from `/tmp`, `claim-audit-v1 --help` and `claim-audit-v1 inspect --json` | PASS; command does not require the repository working directory |

Successor wheel SHA-256:

- `claim_audit_lab-0.6.0-py3-none-any.whl` `1f76c0183dddb58e9e2af6e5eb2323340f01daa67c8b1c0d5cc08d43797ce2bf`
- `claim_audit_lab-0.6.0.tar.gz` `dadd8f52f3c6d98ce5484877fd982981eb5c61f1080e2a014c985f5313650d91`

Distribution metadata remains `0.6.0`. This is inherited packaging identity, not a new release.

## Contract B 1.2 operator seam

Canonical path exercised:

```text
released Contract B 1.2 bundle
+ typed CAL target
→ claim-audit-v1 validate-bundle
→ claim-audit-v1 run-bundle
```

Cases, all byte-identical across two empty output directories:

| Case | Conclusion | Failure code | Reconstruction |
| --- | --- | --- | --- |
| support (`Women had a higher rate than Men.`) | `supported` | none | match |
| contradict (`Men had a higher rate than Women.`) | `contradicted` | none | match |
| abstain / irrelevant-only | `not_checkable` | `NO_DECIDING_RELATION` | match |
| mixed support+refute | `not_checkable` | `MIXED_RELATIONS` | match |

Binding rejections:

- stale `text_sha256` → exit 2, `proposition.text_sha256 does not bind the exact Contract B claim text`
- aliased `proposition_id` → exit 2, `proposition.proposition_id must equal the exact Contract B claim_id`

Intake/aperture:

- complete B1.2 factual-context ledger remains in `contract_b_intake.snapshot.json`
- rejected retained candidates remain visible in the intake history
- only `review.decision == accepted` passages enter `audit_context.json` / semantic measurement
- `manifest.json` file hashes matched emitted bytes

Independent reconstruction used only emitted `result.json` relation categories, composition rule, admitted passage IDs, and terminal conclusion. No hidden in-memory CAL state was required for these four cases.

## Deviations preserved

1. Exact subject `f851489` failed CI-equivalent Ruff on new integration surfaces. Successor `80835a5` is the frozen implementation.
2. `python -m ruff check .` and `ruff format --check .` still fail on historical `scripts/` files. Repository CI authority is `ruff check src tests` and `ruff format --check src`.
3. `claim-audit-v1` emits a Pydantic `UserWarning` that field name `schema` on `ContractBFactualContext` shadows `BaseModel.schema`. Stdout remains `VALID` / inspect JSON. Not treated as a semantic failure.
4. The small strict-comparison Contract A fixture returned 3 BM25 candidates (`returned_count=3`, `not_retained_count=0`). Rejected retained history is proven; non-retained depth-10 history was not populated by this tiny corpus.

## Residual limits / nonclaims

- Deciding V1 families remain only `strict_comparison` and `direct_event_order`. Unsupported-family abstention is legitimate.
- Contract C is not emitted. Candidate A RC2 / proposed Contract C 2.0.0 producer conformance was previously run against CAL RC1 and is **not** inherited. Downstream gate remains open.
- This freeze is not merge, tag, release, production-default, or authorization.
- Hosted CI was not run.

## Local operator path

See `scripts/run_cal_v1_bundle.py` in this repository and the local MainFrame workspace
`30_projects/claim-audit-lab/outputs/2026-09-15-cal-v1-local-pipeline/README.md`.
