# CAL Epistemic Methodology RC1A — Evaluator Freeze

This commit is the designated RC1A evaluator freeze.

No RC1A candidate implementation existed or was inspected before this freeze. Immediately before freeze, `docs/research/rc1a_candidate.py` was absent from the branch and the hosted apparatus receipt recorded `candidate_present: false`.

## Exact live production base

- `main`: `e90f301cf6ca02c0c77b6e88c3b08f8b93b9a36a`
- research branch: `research/epistemic-receipt-capture-rc1a-20260829`
- pre-freeze apparatus head: `b8a2b26e7ebf2c47708b588a81faabc0bdfce4ba`
- Draft research PR: #33

## Frozen apparatus blobs

The following blobs are immutable scientific apparatus for RC1A:

- executable evaluator, `docs/research/rc1a_evaluator.py`: `a0db04b322632d2d52dfb0bdf53824881d3e7b07`
- acceptance specification, `docs/research/rc1a-acceptance-spec.md`: `ada5214745cf3bc23ccc9b6ffb93fe60d885380d`
- regression manifest, `docs/research/rc1a-regression-manifest.json`: `a639a78dcdcfaabed21669cbd3bf269797fefaf7`
- acceptance entry point, `tests/test_rc1a_frozen_acceptance.py`: `504c5b1957d1c6e57d689e4dfc55a82fe0bc9443`
- hosted research workflow, `.github/workflows/rc1a-research.yml`: `18ad092cab55278a853ac601a0d30a6e6bd940eb`

These files must not be edited within RC1A after this freeze. Any discovered defect terminates RC1A; repair requires a separately named successor experiment.

## Frozen protected production / fixture identities

The evaluator itself verifies these exact Git objects on every run:

- `src/claim_audit_lab/v1/runner.py`: `db53f49745876b6158da0c233fb80916bbeaabaf`
- `src/claim_audit_lab/v1/pipeline.py`: `dd67d0d35590d3052826ad697ce9fd11222fff6f`
- `src/claim_audit_lab/v1/intake.py`: `d8b304a4259ec128e656f07ca628d8a0a88ddd69`
- `src/claim_audit_lab/v1/models.py`: `755e0ef1757055905f3c8b76b7edc5e8ddc1fefd`
- `src/claim_audit_lab/contracts/contract_c.py`: `d6b32a44ef11109fe0ee91efa212d3904badf58c`
- `src/claim_audit_lab/v1/impl/aggregator.py`: `b1f9e2309ae3d024bc609b83cc546acb30be6e9b`
- `src/claim_audit_lab/v1/impl/entailer.py`: `aaf9415e74ec2f04357ecf5346491d92f3e2d0d3`
- `src/claim_audit_lab/v1/impl/retriever.py`: `279a287e10f5466b8d2985291080bc0183c72a52`
- `src/claim_audit_lab/v1/impl/rules.py`: `bc388d64a5a53db0d33610ab6ff84bd93a811b46`
- `src/claim_audit_lab/v1/configs/cal-rules-v1.13.0.yaml`: `ac8147f6624164e9081a4ec365cd3920c25df96d`
- `tests/v1/test_pipeline_e2e.py`: `48a22cfab82ea0a2abd8d1c80d0da32a3dacd260`
- `tests/v1/testing/stubs.py`: `c7fa94569234caaf5f2134f672737097e5c70111`
- complete `tests/v1/fixtures/traces` tree: `7d6735da5f23f78efae479d3c99c1fd2f075f935`
- complete `tests/fixtures/cb/evidence-bundle-minimal` tree: `5bcfa0a27877cb7ceebf22cd8960e907f6f92083`

## Pre-freeze evaluator self-test

Hosted workflow run `33270403006` executed the apparatus on pre-freeze head `b8a2b26e7ebf2c47708b588a81faabc0bdfce4ba` and completed successfully.

Receipt artifact:

- artifact id: `9719929060`
- artifact name: `rc1a-receipts-b8a2b26e7ebf2c47708b588a81faabc0bdfce4ba`
- artifact digest: `sha256:ddff13eff1dd89907084b4152384b960495364bb4f69286699df12719584bc98`

Observed before freeze:

- candidate present: `false`
- all protected Git objects matched;
- W1 rejected, failed Gates 1 and 13;
- W2 rejected, failed Gate 5;
- W3 rejected, failed Gates 5, 6, and 12;
- W4 rejected, failed Gate 10;
- W5 rejected, failed Gate 7;
- W6 rejected, failed Gate 12.

## Post-freeze rule

The next scientific action is to execute this exact frozen apparatus and its weak controls on the freeze commit itself. Only if W1-W6 remain rejected and the frozen apparatus remains operational may the smallest RC1A candidate be implemented.

No post-freeze change to evaluator, acceptance specification, regression manifest, acceptance test, or hosted research workflow is permitted within RC1A.
