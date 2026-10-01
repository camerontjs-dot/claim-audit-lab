# CAL V1 convergence RC0

This candidate reconstructs the supported Slice 2 production surface and #184 target
seam on production `main`. It imports exact supported bytes and preserves the old
operator behavior. Qualification receipts establish the result separately from this
pre-execution scope record.

## Authority and boundary

- Active entrypoint: [issue #185](https://github.com/camerontjs-dot/claim-audit-lab/issues/185).
- Base: `32275a239b68af383a56bca843e28cbc1e343976`, tree `bd5c6dd6d352f11282899e0b8c07c4f223504c2e`.
- Branch: `promotion/cal-v1-convergence-rc0-20261001`.
- Preserved [Slice 1 #181](https://github.com/camerontjs-dot/claim-audit-lab/pull/181): `61cab64149cb6119e4dbe1fe18496f3ccf89002f`.
- Qualified [Slice 2 #183](https://github.com/camerontjs-dot/claim-audit-lab/pull/183): `ddaf94551e38663920593cab89f9c60d43c1555f`, tree `1677a1de987a594f4ee8d2670d56943c5f189fbd`.
- Supported [target seam #184](https://github.com/camerontjs-dot/claim-audit-lab/pull/184): `76b7c4dee6369cc6494486eb115a096e9da370b0`, tree `b093779bb1051667380fa2a61b83dd534ae0d08e`.
- Frozen semantic implementation: `847cc970642bb648dc994b929c2053b5c9d4648c`.
- DecompositionComposer blob: `268d0dc4dd22ddde3848141d62b7d719e48d374d`.
- Contract B: released `1.2.0`; its intake and semantics are unchanged.
- Parent-bound Contract C: external Apparatus authority `c5b1d757f3a0ad4f6e2c3f6dbdc2dd2d3c1403ec`.

The `0.6.0` package/runtime/schema token is inherited candidate metadata. No final
release version or public compatibility decision is made here. The thirty legacy
trace changes contain only that version-token substitution. The legacy engine and
CLI coexist with the dedicated native V1 operators.

The target layer authors from claim text only. Conformance first validates the
existing structural binding, then re-authors the expected active-family fields from
the exact bound claim. Evidence does not select target semantics. The module CLI
remains separate and upstream: callers author/conform before calling the unchanged
`run-bundle` or trusted-target parent operator. The historical structural validator
continues accepting the eight weak controls; `VALID` is not semantic conformance.

No research docs, historical promotion workflows, broad compiler, composition
registry, Decision Engine code, or Contract C implementation is imported. The two
preserved decisive evaluators are qualification inputs rather than production code.
Their bytes and expected results remain unchanged; only their repository location
moves from `tests/research/` to `tests/qualification/`.

## Qualification and custody

`CANDIDATE.json` binds the implementation source commit/tree. Its freeze commit is
the containing Git commit. Qualification writes receipts outside tracked source;
receipt head/tree, individual command logs, input identities, artifact digests and
first failure are authoritative for the actual result. This scope record does not
predeclare a pass.

Prepare the repository-maintained Python 3.11 all-extras environment, install the
exact external EB checkout, and install the maintained regression model:

```bash
uv sync --python 3.11 --all-extras --frozen
uv pip install -e EXTERNAL/evidence-bundler
uv run --frozen python -m spacy download en_core_web_sm
.venv/bin/python scripts/qualify_v1_convergence.py --external EXTERNAL --out outputs/convergence
```

`EXTERNAL` contains clean checkouts named `frozen-cal`, `slice2`, `evidence-bundler`,
`contract-c`, `rc2`, and `resolver` at the exact pins in the runner/workflow. The runner
requires a fresh output path and a clean candidate. It verifies all production blob
identities, preserves the decisive #184 matrix and Slice 2 mutation/replay controls,
replays frozen Contract B/DecompositionComposer tests, builds wheel/sdist, checks
packaged bytes, and installs both artifacts in separate environments.

The installed wheel authors/conforms both C1/C2 targets and exercises child and
parent paths for all PIPE01–PIPE04 cases. Each child artifact and every parent artifact
must equal the exact Slice 2 source execution; both installed parent repeats must
also match. Missing and invalid targets must refuse without publishing a result.
The sdist-installed child and conformance path are exercised too.

Maintained repository gates use `python -m pytest -q`, `python -m ruff check src tests`,
`python -m ruff format --check src`, and strict `python -m mypy` in that prepared
environment. The ordinary public suite's five inference skips and research-artifact
exclusions remain explicit in its receipt; they are not covered by a green gate.

The first meaningful failure stops the runner. Preserve its exact head, command,
error, logs and classification before a bounded apparatus repair. Changing a
preregistered mutation, expectation, grammar or evaluator to obtain a pass is outside
this task. A semantic-runtime/composer change, broader grammar, Contract C migration,
new consequential API/version choice, or need for new research stops convergence.

## Preserved deviations

Before candidate commit or scientific qualification, environment setup selected
Python 3.13 locally while the maintained workflow specifies Python 3.11. The Torch
3.13-wheel download failed at DNS lookup. No qualification control executed. The
bounded correction selected Python 3.11 and restored the exact inherited lock file
altered by the failed sync, then installed that frozen lock. Command/log/hash custody
is retained in local `deviation-01.json`. Interpreter/dependency selection changed;
CAL source, evaluator, grammar, mutations and expected results did not.

The first regression-model installation also stopped before qualification: invoking
the venv Python outside `uv run` left the installer's delegated uv command without an
active virtual environment. The correction used `uv run` in the candidate directory
with the prepared environment retained. The failed command/log is preserved in
`deviation-02.json`; the same maintained model and unchanged regression were used.

That retry resolved `en-core-web-sm` 3.8.0 but encountered a missing directory in the
shared uv archive cache. `deviation-03.json` preserves the failed cache read. The
bounded correction used a fresh task-local cache for the unchanged model installer;
no shared cache was deleted and no scientific control had executed.

Predecessor failures remain in #181/#183/#184. This candidate does not rewrite those
receipts or the inherited release-specific 0.5.0 lock.

## Remaining CAL 1.0 boundaries

- Independent promotion review and operator acceptance of this exact convergence artifact are pending.
- Final distribution version, public compatibility and supported-interface policy require a separate decision.
- The successor release lock, release artifacts, tag/release and consumer migration are unrun.
- The exact convergence artifact has not been exercised through downstream Decision/D ingress; earlier #183 composition evidence remains bound to #183. Changing pipeline pins requires its own exact-subject gate.
- Fresh blind acceptance and representative accuracy remain unestablished. A bounded engineering pass does not establish validated accuracy, regulatory suitability, unrestricted authoring, additional families, Authorization or execution.

The next action after bounded qualification is independent review of the Draft
convergence PR against issue #185. No merge, readiness conversion, version assignment,
tag or release is authorized by this work.

## Changed-file inventory

Every production/packaging reuse below is exact. A qualification file can be omitted
from runtime, but omitting it removes part of the reproducible acceptance/custody
surface required by issue #185. Historical documentation and workflows are omitted.

| File | Role | Supported source | Reason | Effect of omission |
|---|---|---|---|---|
| `src/claim_audit_lab/production_v1/__init__.py` | Production | #183 exact blob `5ad5c109b876c1c82360d85d83b13a0e91a3e82d` | Package marker and frozen candidate/runtime identity | Required by qualified dependency closure or supported operator surface |
| `src/claim_audit_lab/production_v1/bundle_cli.py` | Production | #183 exact blob `537a05ca839794474a5950d1a1239f43932c9089` | Qualified claim-audit-v1 operator | Required by qualified dependency closure or supported operator surface |
| `src/claim_audit_lab/production_v1/bundle_input.py` | Production | #183 exact blob `ba3a11b1095ece2965b50e0eeec07d2d5508db82` | Canonical B1.2 loading and exact target/claim binding | Required by qualified dependency closure or supported operator surface |
| `src/claim_audit_lab/production_v1/execution.py` | Production | #183 exact blob `927e9e141c78a9d8cfe3c13572c1c6d47e1d90f3` | Qualified run-bundle and deterministic native output custody | Required by qualified dependency closure or supported operator surface |
| `src/claim_audit_lab/production_v1/packet.py` | Production | #183 exact blob `bda55edcad5bfa10a51a37d0fbc1a51acbe03300` | Typed packet and evidence-world preparation | Required by qualified dependency closure or supported operator surface |
| `src/claim_audit_lab/production_v1/parent_bound.py` | Production | #183 exact blob `b6d281590d372729b968ae75fec470c7186d6bd6` | Qualified external C projection and native-child/parent authority binding | Required by qualified dependency closure or supported operator surface |
| `src/claim_audit_lab/production_v1/parent_cli.py` | Production | #183 exact blob `774178a12acce0ad7a453eb0ba85ec5e5b14fa1c` | Qualified parent CLI orchestration | Required by qualified dependency closure or supported operator surface |
| `src/claim_audit_lab/production_v1/render.py` | Production | #183 exact blob `7dd622f72b062ea280ad21ba78b952ed4f76fbe4` | Deterministic native artifacts | Required by qualified dependency closure or supported operator surface |
| `src/claim_audit_lab/production_v1/schema/manifest-v2.schema.json` | Production | #183 exact blob `2264ec7100a76dec9d1c4a7899424b83f4905801` | Frozen native schema resource | Required by qualified dependency closure or supported operator surface |
| `src/claim_audit_lab/production_v1/schema/packet.schema.json` | Production | #183 exact blob `36e01759bffc41ef5afd55a644a4de4988e6e684` | Frozen native schema resource | Required by qualified dependency closure or supported operator surface |
| `src/claim_audit_lab/production_v1/schema/result-v2.schema.json` | Production | #183 exact blob `01b6aa0379c020aeca74d839c0b7eb8e079b224a` | Frozen native schema resource | Required by qualified dependency closure or supported operator surface |
| `src/claim_audit_lab/production_v1/schema/target.schema.json` | Production | #183 exact blob `6e6e3c1498b1ef5e3161fa0caeaea454782cd586` | Frozen native schema resource | Required by qualified dependency closure or supported operator surface |
| `src/claim_audit_lab/production_v1/semantic/__init__.py` | Production | #183 exact blob `33ed5ac6301badde7a4448cd6cbf1316912fd415` | Frozen semantic package marker | Required by qualified dependency closure or supported operator surface |
| `src/claim_audit_lab/production_v1/semantic/authority.py` | Production | #183 exact blob `09761aab9e04deca724fd213a9295fc93cc3be52` | Frozen authority construction | Required by qualified dependency closure or supported operator surface |
| `src/claim_audit_lab/production_v1/semantic/authority_validation.py` | Production | #183 exact blob `73ee2cc8e26cc3945558f76fa8c0992441177a97` | Frozen authority validity checks | Required by qualified dependency closure or supported operator surface |
| `src/claim_audit_lab/production_v1/semantic/decomposition.py` | Production | #183 exact blob `268d0dc4dd22ddde3848141d62b7d719e48d374d` | Exact frozen DecompositionComposer | Required by qualified dependency closure or supported operator surface |
| `src/claim_audit_lab/production_v1/semantic/engine.py` | Production | #183 exact blob `4111545663f97b4be53cc7523071bbed394d6769` | Frozen active-family judgment and failure precedence | Required by qualified dependency closure or supported operator surface |
| `src/claim_audit_lab/production_v1/semantic/measurement_ledger.py` | Production | #183 exact blob `5e01c0a3246a90fcc42219da78b7d8a1ed5d5f74` | Frozen deterministic measurement receipts | Required by qualified dependency closure or supported operator surface |
| `src/claim_audit_lab/production_v1/semantic/measurements.py` | Production | #183 exact blob `aa26d34a94488901d8a838824e0d7a23c6655f4c` | Frozen typed measurements | Required by qualified dependency closure or supported operator surface |
| `src/claim_audit_lab/production_v1/semantic/models.py` | Production | #183 exact blob `4a8ee5ddc66ad5512d675b45215a858eb8fdd7ee` | Frozen semantic models and conclusion definitions | Required by qualified dependency closure or supported operator surface |
| `src/claim_audit_lab/production_v1/semantic/plugins.py` | Production | #183 exact blob `a2b96f192a4acafb2471785f0b51d2c656e03afc` | Frozen active-family measurement operators | Required by qualified dependency closure or supported operator surface |
| `src/claim_audit_lab/production_v1/semantic/relations.py` | Production | #183 exact blob `2330f7acb64ac77ed0d26aebe7f4536062503400` | Frozen categorical relation semantics | Required by qualified dependency closure or supported operator surface |
| `pyproject.toml` | Packaging | #183 exact blob `9418dea386837c92a6d2dc98f0ff58262cf8d414` | Inherited candidate metadata, qualified console scripts and schema package data | Would lose coherent packaging or the maintained environment |
| `MANIFEST.in` | Packaging | #183 exact blob `50990a8550014fdbbc51385bb8bf034d76cb6ee4` | Include required native schemas in sdist | Would lose coherent packaging or the maintained environment |
| `src/claim_audit_lab/__init__.py` | Packaging | #183 exact blob `55675ac88d3b11d58fee20e10258906a7a80d5c7` | Inherited 0.6.0 candidate identity, explicitly unreleased | Would split package and native-runtime candidate identities |
| `uv.lock` | Packaging | #183 exact blob `f7fab79a85dacafd18174dbb5fe565d74437c487` | Keep inherited candidate package identity and locked dependency environment coherent | Would lose coherent packaging or the maintained environment |
| `tests/v1/fixtures/traces/01-supported-verbatim.json` | Qualification | #183 exact blob `d36409b25cafed28f9e312751d6afea3229ed063` | Inherited library_version token only; all other bytes equal main | Would break existing exact trace regression for inherited candidate metadata |
| `tests/v1/fixtures/traces/02-supported-inferred.json` | Qualification | #183 exact blob `f840dcd79f00f45dc495c3bd48ff990157085698` | Inherited library_version token only; all other bytes equal main | Would break existing exact trace regression for inherited candidate metadata |
| `tests/v1/fixtures/traces/03-partially-supported.json` | Qualification | #183 exact blob `63d46dfc2dabea7eb8317276b01f6c0de7fe115d` | Inherited library_version token only; all other bytes equal main | Would break existing exact trace regression for inherited candidate metadata |
| `tests/v1/fixtures/traces/04-unsupported.json` | Qualification | #183 exact blob `b141878bba1c78160480eb8fb13baa7d689f43c0` | Inherited library_version token only; all other bytes equal main | Would break existing exact trace regression for inherited candidate metadata |
| `tests/v1/fixtures/traces/05-contradicted-hard.json` | Qualification | #183 exact blob `7a9ab838de62cc37e008650ddb8a1fe47248e0ff` | Inherited library_version token only; all other bytes equal main | Would break existing exact trace regression for inherited candidate metadata |
| `tests/v1/fixtures/traces/06-contradicted-negation.json` | Qualification | #183 exact blob `60dc2977ef8bb9cb5d7c19842c2b9dda0e76e201` | Inherited library_version token only; all other bytes equal main | Would break existing exact trace regression for inherited candidate metadata |
| `tests/v1/fixtures/traces/07-composition-numeric-overstated.json` | Qualification | #183 exact blob `021d2b76e59cf4adc779908cab7a220ee215b9f1` | Inherited library_version token only; all other bytes equal main | Would break existing exact trace regression for inherited candidate metadata |
| `tests/v1/fixtures/traces/08-numeric-noncrux-partial.json` | Qualification | #183 exact blob `bc71a8a6200bc02c5355b7a3f26f4c21e0089cf7` | Inherited library_version token only; all other bytes equal main | Would break existing exact trace regression for inherited candidate metadata |
| `tests/v1/fixtures/traces/09-overstated-from-supported.json` | Qualification | #183 exact blob `55dae283eb33194f77c90a3c3278ab465c7c8e04` | Inherited library_version token only; all other bytes equal main | Would break existing exact trace regression for inherited candidate metadata |
| `tests/v1/fixtures/traces/10-overstated-from-partial.json` | Qualification | #183 exact blob `0e35ed594061a063986e3e6dc95c97246333dff2` | Inherited library_version token only; all other bytes equal main | Would break existing exact trace regression for inherited candidate metadata |
| `tests/v1/fixtures/traces/11-source-scope-error.json` | Qualification | #183 exact blob `44649c0586d12b2c224c5f5177b45a889ae2d360` | Inherited library_version token only; all other bytes equal main | Would break existing exact trace regression for inherited candidate metadata |
| `tests/v1/fixtures/traces/12-false-caution.json` | Qualification | #183 exact blob `5fb4803a66ea72fe263a9370b67ad9dbbc595f44` | Inherited library_version token only; all other bytes equal main | Would break existing exact trace regression for inherited candidate metadata |
| `tests/v1/fixtures/traces/13-not-checkable-opinion.json` | Qualification | #183 exact blob `f5a2fe3980f1175368beae71e344f21547ff8519` | Inherited library_version token only; all other bytes equal main | Would break existing exact trace regression for inherited candidate metadata |
| `tests/v1/fixtures/traces/14-not-checkable-short.json` | Qualification | #183 exact blob `e903363de70fcd72b0a46aff2f3e0ce8eaf13ed7` | Inherited library_version token only; all other bytes equal main | Would break existing exact trace regression for inherited candidate metadata |
| `tests/v1/fixtures/traces/15-not-checkable-no-evidence.json` | Qualification | #183 exact blob `c7304261333e2f3505df6087e141af9e89852451` | Inherited library_version token only; all other bytes equal main | Would break existing exact trace regression for inherited candidate metadata |
| `tests/v1/fixtures/traces/16-not-checkable-no-entail.json` | Qualification | #183 exact blob `51df089749969816793a761fb630ef9104cf03f4` | Inherited library_version token only; all other bytes equal main | Would break existing exact trace regression for inherited candidate metadata |
| `tests/v1/fixtures/traces/17-numeric-ambiguous-unit.json` | Qualification | #183 exact blob `f4b48e429d4df7d0dd310931cfc3cb064d66b7ae` | Inherited library_version token only; all other bytes equal main | Would break existing exact trace regression for inherited candidate metadata |
| `tests/v1/fixtures/traces/18-negation-agreeing-absence.json` | Qualification | #183 exact blob `575089b3a57df3c866efda12f5703f6647643d44` | Inherited library_version token only; all other bytes equal main | Would break existing exact trace regression for inherited candidate metadata |
| `tests/v1/fixtures/traces/19-strong-claim-plain-paraphrase.json` | Qualification | #183 exact blob `b12e77b85d69fe52d55bea785a68a8d5896d5d93` | Inherited library_version token only; all other bytes equal main | Would break existing exact trace regression for inherited candidate metadata |
| `tests/v1/fixtures/traces/20-approx-numeric-tolerated.json` | Qualification | #183 exact blob `089a15402f5bc0142bdf797313e518ec9ba6acc7` | Inherited library_version token only; all other bytes equal main | Would break existing exact trace regression for inherited candidate metadata |
| `tests/v1/fixtures/traces/21-year-vs-measure-abstains.json` | Qualification | #183 exact blob `f9733d40e3aa45623fcb290779ba568a91026218` | Inherited library_version token only; all other bytes equal main | Would break existing exact trace regression for inherited candidate metadata |
| `tests/v1/fixtures/traces/22-subfloor-contradict-filtered.json` | Qualification | #183 exact blob `362666bcf4dfb0f2f2afcc028be2f0681b450ac5` | Inherited library_version token only; all other bytes equal main | Would break existing exact trace regression for inherited candidate metadata |
| `tests/v1/fixtures/traces/23-noun-initial-declarative-audited.json` | Qualification | #183 exact blob `23ff7f9654c6e6b592cfa3633c0b084136eaedec` | Inherited library_version token only; all other bytes equal main | Would break existing exact trace regression for inherited candidate metadata |
| `tests/v1/fixtures/traces/24-imperative-out-of-scope.json` | Qualification | #183 exact blob `c1ed718edbe157f08ed5b01c18a3c442e33b3221` | Inherited library_version token only; all other bytes equal main | Would break existing exact trace regression for inherited candidate metadata |
| `tests/v1/fixtures/traces/25-unconfirmed-contradiction-demoted.json` | Qualification | #183 exact blob `34c4ddd298f90c45e8d74b0faf60a9781a86bffa` | Inherited library_version token only; all other bytes equal main | Would break existing exact trace regression for inherited candidate metadata |
| `tests/v1/fixtures/traces/inference/inf-01-supported-encryption.json` | Qualification | #183 exact blob `704f3a4a1a301613d77403380ef799cd31c91d66` | Inherited library_version token only; all other bytes equal main | Would break existing exact trace regression for inherited candidate metadata |
| `tests/v1/fixtures/traces/inference/inf-02-contradicted-logging.json` | Qualification | #183 exact blob `297fd723e9aac18ca5f2a3ed5c1a8361258dae46` | Inherited library_version token only; all other bytes equal main | Would break existing exact trace regression for inherited candidate metadata |
| `tests/v1/fixtures/traces/inference/inf-03-numeric-uptime.json` | Qualification | #183 exact blob `4c043e2e5deabd6e352e140c9c63f3b547afb2a5` | Inherited library_version token only; all other bytes equal main | Would break existing exact trace regression for inherited candidate metadata |
| `tests/v1/fixtures/traces/inference/inf-04-opinion-out-of-scope.json` | Qualification | #183 exact blob `40b070c4f24d62824eab9c5c4232f91e69f65af4` | Inherited library_version token only; all other bytes equal main | Would break existing exact trace regression for inherited candidate metadata |
| `tests/v1/fixtures/traces/inference/inf-05-no-evidence.json` | Qualification | #183 exact blob `a0fd4caf38317dffd7e44cdff9c00b520a4ccf4b` | Inherited library_version token only; all other bytes equal main | Would break existing exact trace regression for inherited candidate metadata |
| `src/claim_audit_lab/production_v1/targeting.py` | Production | #184 exact blob `ea588ab8b91008bdf4020475478a24b01d679b27` | Exact #184 bounded authoring and claim/target conformance | Required by qualified dependency closure or supported operator surface |
| `src/claim_audit_lab/production_v1/target_cli.py` | Production | #184 exact blob `91224b0bcdb91de85587228ff5ac88a619cf52e4` | Exact #184 module CLI; no new console-script API | Required by qualified dependency closure or supported operator surface |
| `tests/test_production_v1_targeting.py` | Qualification | #184 exact blob `c52400a21933f7f7b2fbeed18c39c820245ef75c` | Exact #184 authoring/refusal unit controls | Runtime works; maintained target regression would be lost |
| `tests/qualification/cal_v1_slice2_parent_contract_c_qualification.py` | Qualification | #183 exact blob `9eeb1760445f84cf5676435496373ab5d6a225ad` | Unchanged decisive predecessor evaluator, moved to qualification/ | Runtime works; decisive acceptance reproduction would be lost |
| `tests/qualification/cal_v1_target_authoring_conformance_qualification.py` | Qualification | #184 exact blob `2c0c05fd7507fed33dfaa338abfe1d71388ee7fc` | Unchanged decisive predecessor evaluator, moved to qualification/ | Runtime works; decisive acceptance reproduction would be lost |
| `README.md` | Documentation | Issue #185 | Explain bounded operators, upstream conformance and inherited candidate token | Runtime works; candidate custody/reproduction or truthful public boundary would be lost |
| `docs/promotion/CAL_V1_CONVERGENCE_RC0_20261001.md` | Documentation | Issue #185 | Single authority, scope, file inventory and reproduction record | Runtime works; candidate custody/reproduction or truthful public boundary would be lost |
| `scripts/qualify_v1_convergence.py` | Qualification | Issue #185 | Run preserved evaluators, identity gates, installed predecessor equivalence and maintained gates | Runtime works; candidate custody/reproduction or truthful public boundary would be lost |
| `.github/workflows/cal-v1-convergence-qualification.yml` | Qualification | Issue #185 | Replay this runner against exact external checkouts and publish real receipts | Runtime works; candidate custody/reproduction or truthful public boundary would be lost |
| `CANDIDATE.json` | Qualification | Issue #185 | Bind immutable implementation commit/tree and separate qualification from release | Runtime works; candidate custody/reproduction or truthful public boundary would be lost |
