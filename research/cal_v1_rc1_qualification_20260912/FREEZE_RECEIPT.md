# CAL V1 RC1 qualification freeze receipt

Status: **FROZEN FOR FRESH POST-FREEZE QUALIFICATION**

This receipt freezes the exact RC1 authority-integrity successor before the fresh qualification cohort, gold outcomes, or evaluator are added. Candidate semantic source is immutable for this qualification. A hard-safety failure must be preserved and requires another successor.

## Exact implementation freeze

- repository: `camerontjs-dot/claim-audit-lab`
- successor Draft PR: `#104`
- successor branch: `converge/cal-v1-candidate-rc1-authority-integrity-20260912`
- exact frozen RC1 commit: `a902621e8baea3063dddd7f92ba975aade305464`
- exact frozen RC1 tree: `0ad4434e4a897b39cda062917a3c1eb0968d11aa`
- parent failed candidate: `dca2ec7f2c117cc0b4d6c543ab5049cac7994298`
- parent qualification evidence: Draft PR `#103`, terminal `CAL_V1_QUALIFICATION_FAILED`
- RC1 preregistration blob: `docs/CAL_V1_RC1_AUTHORITY_INTEGRITY.md` = `325ba1171e09c35d1db6e2bed01e01f83dd7c636`

Qualification branch `research/cal-v1-rc1-qualification-20260912` was created directly from the exact frozen RC1 commit. This receipt and all later qualification artifacts are descendants of, not members of, the frozen implementation identity.

## Candidate source/blob identities

- `src/claim_audit_lab/cal_v1_candidate/__init__.py`: `a5c32a7d022ae2d1e059587c4c936e27f27b9fb9`
- `src/claim_audit_lab/cal_v1_candidate/authority.py`: `3cfcfb8cc3b3a8860e119edfbe22a4d684650a86`
- `src/claim_audit_lab/cal_v1_candidate/authority_validation.py`: `73ee2cc8e26cc3945558f76fa8c0992441177a97`
- `src/claim_audit_lab/cal_v1_candidate/cli.py`: `aeb85e9467f2fbdbb5004d130873188256485549`
- `src/claim_audit_lab/cal_v1_candidate/engine.py`: `636734fd1341d2ae721ae9697c7ac7652b89eecc`
- `src/claim_audit_lab/cal_v1_candidate/measurements.py`: `aa26d34a94488901d8a838824e0d7a23c6655f4c`
- `src/claim_audit_lab/cal_v1_candidate/models.py`: `4710923e62ef62b472abb21b9e075b177ebb7413`
- `src/claim_audit_lab/cal_v1_candidate/projection.py`: `9bc152275759304be03b84014c56bd434549a64a`
- `src/claim_audit_lab/cal_v1_candidate/relations.py`: `e9e9401c92ee11d25a50dbc36e80aeb4c4cd220d`
- `src/claim_audit_lab/cal_v1_candidate/report.py`: `7435c96e93e5acaf7efbb1ee8599b427e3d992ff`

RC1 regression test:

- `tests/test_cal_v1_authority_integrity_rc1.py`: `aacc755cf8cc4a1a1becb06bfdb5235bca558c5d`

## RC1 semantic delta from the failed parent

RC1 does not change semantic-family scope, measurement instruments, proposition relation semantics, composition, Contract B handling, Contract C projection, scalar policy, or legacy v0.5 behavior.

The semantic delta is limited to relation-boundary authority consumption. Before deriving a categorical relation, RC1 independently verifies:

1. exact warranted status/reason;
2. authority context/world binding;
3. atom-to-authority context/world binding;
4. atom/proposition semantic-family agreement;
5. atom passage/source membership in the exact admitted evidence world;
6. atom semantic fields against independent source completion from that passage;
7. content-derived `atom_id`;
8. content-derived `authority_id`.

The parent relation consumer trusted supplied binding fields without recomputing the content-derived IDs; fresh parent qualification case Q12 demonstrated that this could admit a rebound authority and yield unsafe `SUPPORTS`.

## Explicit authority boundary

This successor establishes only content-integrity and source-grounding checks at the relation consumer. Content hashes are not signatures. RC1 does **not** claim cryptographic authentication or origin authenticity for arbitrary externally reconstructed semantic-authority receipts.

If a future architecture requires portable external authority, authenticated-receipt semantics remain a separate contract/security problem.

## Pre-freeze repository gate

Exact Public suite:

- workflow: `.github/workflows/public-suite.yml`
- workflow blob: `7bf0f9e9f1bf57ece569bcaa9a81b450fe8fa66b`
- exact tested RC1 head: `a902621e8baea3063dddd7f92ba975aade305464`
- run: `34674924671`
- job: `103502956632`
- PR merge-test SHA: `406950ed99f2ece1ed32e5e205c2973a884b26cd`

Observed gate:

- pytest: `980 passed, 5 skipped, 48 deselected`;
- Ruff lint: PASS, `All checks passed!`;
- Ruff format: PASS, `62 files already formatted`;
- mypy: PASS, `Success: no issues found in 61 source files`;
- Public suite job: PASS.

The immediately preceding RC1 run had the same passing pytest and Ruff-lint results but failed only `ruff format --check` on `authority_validation.py`. Commit `a902621e8baea3063dddd7f92ba975aade305464` applied Ruff's exact canonical formatting and made no semantic change.

## Fresh qualification requirements

The post-freeze cohort must use fresh entities/surfaces and must include at minimum:

- deciding strict-comparison support/refutation/inversion;
- deciding direct-event-order support/refutation plus safe reporting/scope refusal;
- unsupported-family fail-closed behavior;
- same-ID proposition substitution rejection;
- stale passage-hash rejection;
- ordinary stale-world authority rejection;
- Q12-class rebound authority with stale IDs;
- partial rehash where atom ID is recomputed but authority ID remains stale;
- fully self-consistent rehash of source-fabricated semantic fields, which must still fail source grounding;
- semantic-family mutation rejection;
- mixed support/refutation abstention;
- Contract C `non_deciding` attribution, safe abstention projection, and mixed-evidence no-scalar-winner behavior.

Hard safety requires zero unsafe support/refutation, zero stale/mutated authority acceptance within the stated RC1 boundary, zero unsupported-family fallback, zero scalar/confidence winner selection, and zero Contract C semantic strengthening.

## Freeze boundary

At creation of this receipt:

- no fresh RC1 qualification cohort has been committed;
- no fresh RC1 gold has been committed;
- no fresh RC1 qualification evaluator has been committed or executed;
- no RC1 qualification scoring has occurred;
- candidate semantic source is immutable for this qualification;
- no merge, promotion, tag, release, Contract B/C mutation, or Decision Engine production work is authorized.
