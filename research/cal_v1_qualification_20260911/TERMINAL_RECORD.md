# CAL V1 compact fresh qualification terminal record

## Terminal disposition

**CAL_V1_QUALIFICATION_FAILED**

The exact frozen CAL V1 candidate passed its complete pre-freeze repository gate, then failed one hard-safety condition in the fresh post-freeze qualification. The frozen implementation is not patched by this record and is not qualified for promotion.

## Classification and stop rule

This is a terminal Research Qualification evidence record. It is not a merge, promotion, tag, release, Contract B amendment, Contract C amendment, production authorization, or Decision Engine production handoff.

The qualification preregistration required:

- zero unsafe `SUPPORT` / `SUPPORTED`;
- zero unsafe `REFUTES` / `CONTRADICTED`;
- zero stale or mismatched authority/receipt acceptance;
- zero proposition/world/passage substitution acceptance;
- zero unsupported-family legacy fallback;
- zero scalar/confidence winner selection;
- zero Contract C semantic strengthening.

Any hard-safety failure requires preserving the frozen result and stopping. Candidate repair requires a separately authorized successor candidate.

## Frozen implementation identity

- repository: `camerontjs-dot/claim-audit-lab`
- convergence Draft PR: `#101`
- frozen candidate branch: `converge/cal-v1-candidate-20260911`
- exact frozen candidate commit: `dca2ec7f2c117cc0b4d6c543ab5049cac7994298`
- exact frozen candidate tree: `e48de79a38e3d0472892117b78c8619f78d45094`
- exact CAL `main` base: `32275a239b68af383a56bca843e28cbc1e343976`
- freeze receipt commit: `0ccdbbf9b8e3907f0034436135d9423107001b41`
- freeze receipt blob: `bd17a1c4a200b35bc1da587bc00e125f1b86dd9f`

Frozen candidate source blobs:

- `__init__.py`: `a5c32a7d022ae2d1e059587c4c936e27f27b9fb9`
- `authority.py`: `3cfcfb8cc3b3a8860e119edfbe22a4d684650a86`
- `cli.py`: `aeb85e9467f2fbdbb5004d130873188256485549`
- `engine.py`: `636734fd1341d2ae721ae9697c7ac7652b89eecc`
- `measurements.py`: `aa26d34a94488901d8a838824e0d7a23c6655f4c`
- `models.py`: `4710923e62ef62b472abb21b9e075b177ebb7413`
- `projection.py`: `9bc152275759304be03b84014c56bd434549a64a`
- `relations.py`: `23548bc9c463f42f2849b7697c2c4fd4614e2474`
- `report.py`: `7435c96e93e5acaf7efbb1ee8599b427e3d992ff`

No candidate semantic-source blob above changed after freeze.

## Contract authorities frozen into the qualification

Live Apparatus Contracts authority inspected before freeze:

- `camerontjs-dot/apparatus-contracts` main: `c3563cff66d2c85dcbf575c693056e2d8e4563d4`
- tree: `0e2174571c7a0f449f8b5945569266847e9ba97c`
- Contract B factual-context extension 1.2.0 blob: `77645a6adac664892866f3fdf8abf66cd1d0dd10`
- released Contract C 1.0.0 blob: `8c15f2e5f4047ccd17e204fb23aee1168781b9d5`

Qualified research Contract C `non_deciding` shadow:

- receipt commit: `ad1ffbd7906a7cf34cce5afa906a5797cd4a14ff`
- qualified implementation head: `beb195c61e7a85bdb0cb350d85c03ca48177e23d`
- handoff receipt blob: `1b02d4eb8d3d85026ec0455a0c193bac7b05dc5c`
- run: `34529151133`
- artifact: `10172768614`
- artifact digest: `sha256:7af02c2230be29b893f3480ef25b82a0caf0ce334d3967997ac713ebb659170b`
- disposition: `SUPPORTED_BOUNDED_TWO_LEAF_SHADOW_DELTA`

No Contract B or Contract C authority was modified.

## Pre-freeze CI receipt

The candidate was frozen only after exact head `dca2ec7f2c117cc0b4d6c543ab5049cac7994298` passed Public suite:

- workflow run: `34611283117`
- job: `103302509641`
- pytest: `976 passed, 5 skipped, 48 deselected`
- Ruff check: PASS
- Ruff format: PASS, `61 files already formatted`
- mypy: PASS, `Success: no issues found in 60 source files`

The earlier red-CI sequence was a static-tooling issue, not a semantic redesign: Ruff formatter and E501 disagreed on a small set of formatter-canonical lines. The final green source retained formatter output and used narrow local lint suppressions. Existing `str, Enum` representation was preserved rather than mechanically converting to `StrEnum`.

## Fresh cohort, gold and evaluator identities

Qualification branch / Draft evidence PR:

- branch: `research/cal-v1-qualification-20260911`
- Draft PR: `#103`

Fresh cohort:

- cohort id: `cal-v1-fresh-q0-20260911`
- case count: `16`
- cohort commit: `f32ed3c14230cfb19291e26fffb8428a13458449`
- `COHORT.json` blob: `28c48837f705be90ea4c3e7711acd853fb9e9a4a`

Frozen gold:

- gold commit: `4db58e91dbb0672b06812cc20175fbd4b876bb29`
- `GOLD.json` blob: `b66200b55f15e5ea797f9caf5aa95f22855c6cf8`

Frozen evaluator:

- evaluator commit: `12bc49d19f74eb756f40484223129fea11583db0`
- `tests/test_cal_v1_fresh_qualification.py` blob: `34d56372a9254087d9f0a71c9caf46d3273d37e7`

Order was implementation freeze -> cohort freeze -> gold freeze -> evaluator freeze -> scoring. Gold was not changed after scoring began.

## Qualification execution receipt

- Public suite run: `34649638396`
- job: `103428588427`
- PR merge test SHA: `143d934804fc099feb6a2e56876c918fef02db0e`
- pytest result: `1 failed, 976 passed, 5 skipped, 48 deselected`
- failing qualification test: `tests/test_cal_v1_fresh_qualification.py::test_cal_v1_fresh_qualification_cohort`
- matched frozen gold: `15 / 16`
- failed frozen gold: `1 / 16`
- unsafe-result count: `1`

The repository workflow did not upload a GitHub Actions artifact. The durable observed-result artifact is:

- observation commit: `9896686e8a817fafbd3b550d239bb74bddc3547e`
- `QUALIFICATION_OBSERVATION.json` blob: `8bb60c1810f1856536393538a0c304df49119e90`

The workflow job log is the independent execution receipt for those observations.

## Hard-safety failure

### Q12 — tampered authority identity

Gold required rejection.

The case first created a legitimate strict-comparison authority receipt in evidence world A. It then constructed a new authority object by replacing the authority and semantic-atom context/world binding fields with evidence world B while deliberately retaining the original content-derived:

- `authority_id = semantic-authority:256d89e3df06acec6f03fe9226e2985bab239db50af787390534772cc54e579e`
- `atom_id = semantic-atom:1f6077e33c4c1ed438ba169d02d5c37c15797640169b6f764570228796c7fe52`

Observed result:

- outcome: `ACCEPTED`
- categorical relation: `SUPPORTS`

This violates both the stale/mismatched-authority rejection condition and the zero-unsafe-support condition.

### Failure localization

The failure is narrower than general proposition/world binding.

The fresh cohort separately established that:

- Q09 same-ID proposition substitution was rejected with `RelationRefusal`;
- Q10 passage substitution under a stale passage hash was rejected with `ValueError: passage hash mismatch`;
- Q11 an ordinary authority from a different evidence world was rejected with `RelationRefusal`.

Q12 succeeded only after the authority/atom binding fields themselves were rewritten to look current while their original content-derived IDs remained stale. The observed behavior is therefore consistent with the lower-level relation consumer validating supplied binding fields but not independently revalidating the `authority_id` / `atom_id` against the authority/atom content it consumes.

This explanation is an evidence-supported localization, not a production fix. No frozen source was changed to test a repair.

## Per-family qualification result

### `strict_comparison`

Disposition: **FAILED HARD SAFETY**.

Passed within the fresh cohort:

- direct categorical support;
- categorical refutation;
- inverse/reversal support;
- insufficient-evidence safe abstention;
- same-ID proposition-substitution rejection;
- stale-passage-hash rejection;
- ordinary stale-world authority rejection;
- mixed support/refutation -> `not_checkable` / `MIXED_RELATIONS`;
- no scalar/confidence winner selection;
- `non_deciding` Contract C attribution in the exercised projection cases.

Failed:

- tampered/rebound authority identity was accepted and yielded `SUPPORTS`.

### `direct_event_order`

Disposition inside this cohort: **MATCHED FROZEN GOLD**.

- direct support matched;
- direct refutation matched;
- reporting/scope surface failed closed;
- safe-abstention Contract C projection remained `not_checkable` with `non_deciding` attribution.

This does not override the whole-candidate qualification failure.

### unsupported semantic family

Disposition inside this cohort: **MATCHED FROZEN GOLD**.

- permission/exception case returned `not_checkable` / `UNSUPPORTED_SEMANTIC_FAMILY`;
- no historical v0.5 fallback was observed.

## Safe abstention / miss characterization

The following non-deciding outcomes were expected and safe under frozen gold:

- Q04: strict-comparison evidence contained no supported comparison surface -> `MEASUREMENT_NOT_APPLICABLE`, terminal `RELATION_UNRESOLVED` / `not_checkable`;
- Q07: direct-event-order reporting/scope surface -> `MEASUREMENT_MISS`, terminal `RELATION_UNRESOLVED` / `not_checkable`;
- Q08: unsupported semantic family -> `UNSUPPORTED_SEMANTIC_FAMILY` / `not_checkable`;
- Q13: mixed support + refutation -> `MIXED_RELATIONS` / `not_checkable`;
- Q15: scope-limited event-order projection -> `not_checkable`, contribution remains `non_deciding`;
- Q16: mixed comparison projection -> `not_checkable`, both support and counterevidence preserved with no scalar winner.

None of these safe abstentions caused the terminal failure.

## Contract C research projection result

The exercised research projection matched frozen gold and did not itself fail qualification:

- Q14: `supported`; channels `[non_deciding, support]`; `causal_form = single_necessary`;
- Q15: `not_checkable`; channel `[non_deciding]`; `causal_form = redundant_non_deciding`;
- Q16: `not_checkable`; channels `[support, counterevidence]`; `causal_form = jointly_sufficient`;
- no `score`, `confidence`, `probability`, `winner`, or `rank` selection key was observed in Q16;
- no Contract C semantic strengthening was observed in these fresh projection cases.

This is only a result for the qualified research `research-non-deciding-rc0` shadow shape. It does not assign or promote an official Contract C successor version.

## Deviations and record corrections

1. The pre-freeze CI repair required multiple preserved red runs before the final green run because Ruff lint and Ruff formatting had incompatible expectations on a small set of lines. No semantic repair was used to obtain green CI.
2. PR #101 previously stated an installed operator surface `claim-audit-v1-candidate`. Live `pyproject.toml` does not install that console script. No packaging change was made after freeze to manufacture the claim; the PR evidence record must instead be corrected.
3. The qualification workflow stops at pytest after the hard-safety failure, so Ruff/format/mypy did not execute on the qualification-only branch. This does not weaken the exact candidate's pre-freeze green receipt; the qualification branch changed only evidence/fixtures/evaluator after that frozen parent.
4. No GitHub Actions artifact was uploaded by the Public suite. The committed observation plus run/job log serve as the durable result record.

## Exact nonclaims

This record does **not** establish:

- CAL V1 production readiness;
- CAL V1 promotion eligibility;
- generic NLU/NLI or general temporal reasoning;
- source truthworthiness or retrieval completeness;
- permission/exception deciding semantics;
- root/all-of composition;
- a released Contract C successor;
- operational authorization or execution permission;
- safety of consuming reconstructed or externally supplied semantic-authority objects;
- that the Q12 repair is known, implemented, or qualified;
- that the candidate may be patched and still retain this qualification identity.

## Stop state

`CAL_V1_QUALIFICATION_FAILED`

The frozen candidate and failure remain preserved. No merge, promotion, tag, release, Contract B mutation, Contract C mutation, candidate patch, successor candidate, or Decision Engine production work is performed by this thread after this terminal record.
