# CAL V1 qualification freeze receipt

Status: **FROZEN FOR ONE BOUNDED POST-FREEZE QUALIFICATION**

This receipt freezes the exact maintained CAL V1 candidate before any fresh qualification cohort, gold outcomes, or evaluator are added. The candidate semantic source identified below is immutable for this qualification. A qualification failure must be preserved; repair requires a separately authorized successor candidate.

## Exact implementation freeze

- repository: `camerontjs-dot/claim-audit-lab`
- convergence Draft PR: `#101`
- candidate branch at freeze: `converge/cal-v1-candidate-20260911`
- exact candidate commit: `dca2ec7f2c117cc0b4d6c543ab5049cac7994298`
- exact candidate tree: `e48de79a38e3d0472892117b78c8619f78d45094`
- CAL `main` base: `32275a239b68af383a56bca843e28cbc1e343976`
- convergence-scope record blob: `docs/CAL_V1_CONVERGENCE_DECISION.md` = `5c716b38de06472b66277d95d3418ccdb78219fd`

The qualification branch `research/cal-v1-qualification-20260911` was created directly from the exact frozen candidate commit. This receipt and every later qualification artifact are descendants of, not members of, the frozen implementation identity.

## Candidate source/blob identities

- `src/claim_audit_lab/cal_v1_candidate/__init__.py`: `a5c32a7d022ae2d1e059587c4c936e27f27b9fb9`
- `src/claim_audit_lab/cal_v1_candidate/authority.py`: `3cfcfb8cc3b3a8860e119edfbe22a4d684650a86`
- `src/claim_audit_lab/cal_v1_candidate/cli.py`: `aeb85e9467f2fbdbb5004d130873188256485549`
- `src/claim_audit_lab/cal_v1_candidate/engine.py`: `636734fd1341d2ae721ae9697c7ac7652b89eecc`
- `src/claim_audit_lab/cal_v1_candidate/measurements.py`: `aa26d34a94488901d8a838824e0d7a23c6655f4c`
- `src/claim_audit_lab/cal_v1_candidate/models.py`: `4710923e62ef62b472abb21b9e075b177ebb7413`
- `src/claim_audit_lab/cal_v1_candidate/projection.py`: `9bc152275759304be03b84014c56bd434549a64a`
- `src/claim_audit_lab/cal_v1_candidate/relations.py`: `23548bc9c463f42f2849b7697c2c4fd4614e2474`
- `src/claim_audit_lab/cal_v1_candidate/report.py`: `7435c96e93e5acaf7efbb1ee8599b427e3d992ff`

Existing candidate regression test blob:

- `tests/test_cal_v1_candidate.py`: `f5d203b27c15ab48356029b970535f22706813c1`

## Semantic-family profile

Frozen disposition from `docs/CAL_V1_CONVERGENCE_DECISION.md`:

- `strict_comparison`: deciding, bounded deterministic comparison measurement and categorical relation/composition;
- `direct_event_order`: deciding only inside the narrow direct narrator-level grammar with exactly one supported event on each side of one `before`/`after` cue;
- permission / exception / deontic: diagnostic only / deferred, not deciding;
- assertion / scope: falsified do-not-use;
- learned/NLI: diagnostic only, not terminal authority;
- undeclared/other: `UNSUPPORTED_SEMANTIC_FAMILY`, fail closed;
- composite root / `all_of`: not composed in V1.

No scalar confidence, threshold, majority-vote, or legacy v0.5 fallback participates in V1 composition.

## Implementation identities by responsibility

Strict-comparison and direct-event-order measurement implementation:

- blob: `measurements.py` = `aa26d34a94488901d8a838824e0d7a23c6655f4c`
- strict instrument: `rc7fb1-strict-comparison` / `rc7fb1-comparator-1`
- direct-event instrument: `rc7fc-event-order` / `rc7fc-event-order-1`

Semantic authority and independent source completion:

- blob: `authority.py` = `3cfcfb8cc3b3a8860e119edfbe22a4d684650a86`

Proposition/evidence-world/context identity and binding:

- blob: `models.py` = `4710923e62ef62b472abb21b9e075b177ebb7413`
- enum representation remains existing `str, Enum`; Ruff `UP042` is locally suppressed rather than converting identity-bearing enums to `StrEnum`.

Proposition-relative categorical relation derivation:

- blob: `relations.py` = `23548bc9c463f42f2849b7697c2c4fd4614e2474`

Scoreless composition and unsupported-family fail-closed behavior:

- blob: `engine.py` = `636734fd1341d2ae721ae9697c7ac7652b89eecc`

Research Contract C projection:

- blob: `projection.py` = `9bc152275759304be03b84014c56bd434549a64a`
- candidate profile: `cal-v1-candidate-2026-09`
- research wire sentinel: `research-non-deciding-rc0`

## Contract authority bindings

Exact live Apparatus Contracts authority inspected before freeze:

- repository: `camerontjs-dot/apparatus-contracts`
- exact `main`: `c3563cff66d2c85dcbf575c693056e2d8e4563d4`
- exact tree: `0e2174571c7a0f449f8b5945569266847e9ba97c`

Contract B factual-context extension 1.2.0:

- `contract-b-factual-context-extension-v1.2.0.md`
- blob: `77645a6adac664892866f3fdf8abf66cd1d0dd10`
- Contract B transports/validates evidence-world and aperture state and does not acquire CAL semantic/decision authority.

Released Contract C 1.0.0:

- `contract-c-v1.0.0.md`
- blob: `8c15f2e5f4047ccd17e204fb23aee1168781b9d5`
- released Contract C retains `support` / `counterevidence`, exact input/producer/result binding, and the existing causal-form vocabulary. It is not modified by this qualification.

Qualified research `non_deciding` shadow authority:

- Apparatus Draft PR `#85`, Contract C non-deciding shadow RC0;
- receipt commit: `ad1ffbd7906a7cf34cce5afa906a5797cd4a14ff`;
- exact handoff qualification head: `beb195c61e7a85bdb0cb350d85c03ca48177e23d`;
- receipt blob: `research/contract_c_non_deciding_shadow_rc0/HANDOFF_QUALIFICATION_RECEIPT.json` = `1b02d4eb8d3d85026ec0455a0c193bac7b05dc5c`;
- decisive handoff run: `34529151133`;
- artifact: `10172768614`;
- artifact digest: `sha256:7af02c2230be29b893f3480ef25b82a0caf0ce334d3967997ac713ebb659170b`;
- disposition: `SUPPORTED_BOUNDED_TWO_LEAF_SHADOW_DELTA`;
- bounded semantic delta: research version sentinel plus added `non_deciding` contribution channel; unrelated released Contract C structure, binding, reference-integrity, canonicalization, and causal-multiplicity rules remain fixed.

No official Contract C successor version is assigned by this freeze.

## Pre-freeze CI receipt

Exact required workflow:

- `.github/workflows/public-suite.yml` blob: `7bf0f9e9f1bf57ece569bcaa9a81b450fe8fa66b`
- workflow run: `34611283117`
- job: `103302509641`
- tested candidate head: `dca2ec7f2c117cc0b4d6c543ab5049cac7994298`

Observed gate:

- pytest: `976 passed, 5 skipped, 48 deselected`;
- Ruff check: PASS;
- Ruff format check: PASS, `61 files already formatted`;
- mypy: PASS, `Success: no issues found in 60 source files`;
- Public suite job: PASS.

## CI-repair audit

The supplied pre-repair head was `76a8720eedd01f00c6063e92ac0f2e5a64c0987b`. The exact comparison to the frozen head is 25 commits ahead and changes only the candidate package/test files implicated by the static-quality gate. The sequence is import ordering, `collections.abc.Mapping`, line wrapping, Ruff formatting, and narrow lint suppressions. No released v0.5 source, semantic family, threshold, fallback path, Contract B authority, or Contract C authority was changed.

The repeated pre-freeze CI failures were a formatter/linter interaction: Ruff formatting canonicalized several expressions into layouts that `E501` then rejected. The final repair retains formatter-canonical source and uses local `# noqa: E501` only where required. This is a tooling resolution, not a semantic redesign.

## Known pre-qualification observations

These are not qualification failures and are not patched after freeze:

1. The normal maintained `audit()` path constructs measurement, authority, relation, and composition internally and checks exact context/world/proposition binding. Fresh qualification will pressure stale/mismatched receipts and proposition/world substitution at the relevant lower-level seams as explicit adversarial cases.
2. Contract C projection uses the released causal-form vocabulary together with the qualified research `non_deciding` channel. Fresh qualification must verify that projection does not strengthen a CAL result, polarize neutral evidence, or invent a scalar winner.
3. PR #101 currently states an operator surface named `claim-audit-v1-candidate`, but live `pyproject.toml` does not install that script. This qualification does not alter packaging or released v0.5 behavior. The supported module entry point is not treated as evidence for an installed console-script claim; the PR record must be corrected rather than changing packaging during this qualification.

## Freeze boundary

At creation of this receipt:

- no fresh qualification cohort has been committed;
- no fresh qualification gold/expected outcomes have been committed;
- no fresh qualification evaluator has been committed or executed;
- no candidate scoring has occurred;
- candidate semantic source is immutable for the remainder of this qualification;
- no merge, promotion, tag, release, Contract B change, Contract C change, or Decision Engine production work is authorized.
