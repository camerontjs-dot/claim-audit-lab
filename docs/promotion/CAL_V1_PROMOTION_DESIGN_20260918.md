# CAL V1 Promotion Design — 2026-09-18

## Objective

Determine the smallest production change against the real CAL production base that makes only already-qualified CAL V1 machinery reachable and packageable without reopening semantic research.

This is a promotion-design artifact. It is not a release record and does not itself authorize merge.

## Production base

- repository: `camerontjs-dot/claim-audit-lab`
- production base: `main`
- exact starting SHA: `32275a239b68af383a56bca843e28cbc1e343976`

## Frozen research authority

Prototype freeze:

- disposition: `CAL_V1_PROTOTYPE_FROZEN`
- freeze ID: `cal-v1-prototype-20260918`
- accepted freeze commit: `e24e405f5336ee024674f39dba97255bb58a2dd9`
- accepted freeze tree: `02b442c30c9b8c8411cf3e3a18f20b31bebad6e1`
- qualified semantic source: `7cf0d2e50562ec4ce4082d1e1c058a11025b1a48`
- decisive freeze workflow: `35372362109`
- terminal synthesis: PR #180

The freeze passed the exact semantic-source guard, external-authority guards, integrated A2 → EB → B1.2 → CAL → parent path, final semantic closure, architecture gates, full-history repository regression, Ruff, and strict mypy.

## Exact production-to-freeze delta

Comparison:

`32275a239b68af383a56bca843e28cbc1e343976...7cf0d2e50562ec4ce4082d1e1c058a11025b1a48`

Observed:

- 78 commits ahead of production `main`;
- no commits behind;
- the delta contains production runtime work, qualification machinery, research records, workflows, fixture-version churn, and unrelated historical changes.

Conclusion: the research branch must not be merged wholesale.

A second comparison from the earlier frozen integration candidate:

`80835a57e121c66d22c68f349abf8e318de0e232...7cf0d2e50562ec4ce4082d1e1c058a11025b1a48`

isolated the later V1 source changes to:

- `production_v1/claim_compiler.py`
- `semantic/authority.py`
- `semantic/composition.py`
- `semantic/decomposition.py`
- `semantic/engine.py`
- `semantic/measurement_ledger.py`
- `semantic/plugins.py`

This makes the active-runtime boundary directly inspectable.

## Canonical production route

The earlier integration EDR and the frozen code agree that the canonical operator route is:

```text
released Contract B 1.2 bundle
        +
typed target bound to exact Contract B claim
        ↓
claim-audit-v1 run-bundle
        ↓
canonical Contract B intake
        ↓
AuditContext
        ↓
SemanticFamilyRegistry
        ↓
measurement → warrant → proposition-relative relation
        ↓
scoreless categorical compose()
        ↓
native CAL result + deterministic artifacts
```

The historical/top-level `claim-audit` compatibility-packet commands are not the canonical Evidence Bundler handoff.

## Proposed first promotion slice

The smallest production slice should promote the already-qualified canonical Contract B → CAL verdict path and no more.

### Runtime and intake

Promote frozen versions of:

- `src/claim_audit_lab/production_v1/__init__.py`
- `src/claim_audit_lab/production_v1/bundle_cli.py`
- `src/claim_audit_lab/production_v1/bundle_input.py`
- `src/claim_audit_lab/production_v1/execution.py`
- `src/claim_audit_lab/production_v1/packet.py`
- `src/claim_audit_lab/production_v1/render.py`

`packet.py` remains in the dependency closure because frozen `execution.py` imports and preserves the compatibility-packet surface, but that surface is not the canonical promoted operator boundary.

### Active semantic dependency closure

Promote frozen versions of:

- `semantic/__init__.py`
- `semantic/models.py`
- `semantic/measurements.py`
- `semantic/authority.py`
- `semantic/authority_validation.py`
- `semantic/relations.py`
- `semantic/plugins.py`
- `semantic/measurement_ledger.py`
- `semantic/engine.py`

This preserves the exact qualified ordinary audit behavior, including:

- active families `strict_comparison` and `direct_event_order`;
- explicit fail-closed family dispatch;
- source/authority integrity checks;
- the authority-family firewall;
- measurement-ledger integrity needed by the frozen engine dependency graph;
- scoreless categorical support/refute/not-checkable behavior.

### Schemas and packaging

Promote only the schema resources referenced by the frozen runtime:

- `packet.schema.json`
- `target.schema.json`
- `result-v2.schema.json`
- `manifest-v2.schema.json`

Packaging changes required for reachability:

- add `claim-audit-v1 = "claim_audit_lab.production_v1.bundle_cli:app"`;
- package `production_v1/schema/*.json`;
- include those schema files in source-distribution packaging.

The existing historical `claim-audit` command should remain untouched in the first promotion slice.

## Explicitly deferred from the first promotion slice

### Claim compiler

`production_v1/claim_compiler.py` is research-qualified but is not required by the canonical typed-target Contract B route.

Do not promote it in Slice 1.

### CompositionRegistry / quantitative change

`semantic/composition.py` is qualified and registers `quantitative_change_exact_v1`, but ordinary A/B execution does not produce active `scalar_value` authority.

The ordinary verdict path uses the frozen scoreless categorical `compose()` in `semantic/engine.py`; it does not call the quantitative CompositionRegistry.

Do not place quantitative composition on the ordinary production path in Slice 1.

A later promotion may package the registry as an explicit dormant extension surface if there is a concrete consumer need.

### DecompositionComposer

`semantic/decomposition.py` is qualified for root/single and declared exact `all_of`, but multi-child orchestration is not a normal one-command production route.

Apparatus Contracts PR #107 also preserves:

`C1_CANNOT_AUTHORITATIVELY_BIND_CAL_V1_DECOMPOSITION_RC0`

Do not couple DecompositionComposer promotion to the first CAL runtime merge.

### Research-only and unrelated delta

Do not promote merely because they exist on the research lineage:

- research workflows;
- research/preregistration/result documents except the terminal promotion record;
- research fixtures and harnesses;
- historical trace version-token churn;
- `scripts/run_cal_v1_bundle.py`;
- `src/claim_audit_lab/v1/impl/retriever.py` changes;
- root `claim-audit` compatibility command additions;
- Contract C or Decision Engine changes.

## Why this is the smallest defensible slice

The canonical `run-bundle` path imports the active semantic registry and authority stack directly.

By contrast:

- `claim_compiler.py` is not imported by the canonical path;
- `semantic/composition.py` is not imported by ordinary `audit()`;
- `semantic/decomposition.py` is not imported by ordinary `audit()`;
- the historical `claim-audit` CLI is not needed because `claim-audit-v1` is a dedicated entry point.

Therefore including those surfaces in the first production merge would enlarge the production claim without being necessary to expose the already-proven claim → verdict route.

## Pre-promotion live smoke evidence

Two disposable runs exercised the exact frozen semantic code before this design was finalized.

### Positive control

Claim:
`Women had a higher rate than Men.`

Evidence:
`Women had a higher rate than Men.`

Run `35398836307` produced:

- authority `WARRANTED`;
- relation `SUPPORTS`;
- conclusion `supported`;
- failure code `null`.

### Reversed control

Evidence remained:
`Women had a higher rate than Men.`

Claim changed only to:
`Women had a lower rate than Men.`

Run `35403739264` produced:

- authority `WARRANTED`;
- relation `REFUTES`;
- conclusion `contradicted`;
- failure code `null`.

Both runs passed a guard that `src/claim_audit_lab` remained unchanged from qualified semantic subject `7cf0d2e50562ec4ce4082d1e1c058a11025b1a48`.

These are bounded smoke results, not new semantic qualification.

## Required production-candidate gates

Before Slice 1 can leave Draft, the production-shaped branch should demonstrate:

1. byte identity for every promoted semantic file against the qualified frozen subject, except any separately declared nonsemantic packaging/version token;
2. canonical `claim-audit-v1 run-bundle` execution against exact Contract B 1.2;
3. target identity/text binding and evidence-aperture preservation;
4. frozen positive and reversed negative controls;
5. unsupported-family and mixed/unresolved fail-closed controls;
6. RC1 authority-integrity regressions;
7. semantic plugin-registry and measurement-ledger regressions;
8. deterministic native artifact replay;
9. full repository regression;
10. Ruff, Ruff format and strict mypy;
11. clean wheel/sdist installation with the `claim-audit-v1` entry point and packaged schemas;
12. no Contract C output and no automatic action.

## Version consequence

The promotion adds a new installed operator surface and native artifact/schema surface. That is release-visible additive functionality, so it should not be shipped under the already released `0.5.0` identity.

The research lineage carries `0.6.0`, but this design does not itself authorize that exact release token, tag, or publication. Version assignment remains a separate release-governance decision after the production candidate is qualified.

## Preserved downstream boundary

Contract C 1.0 cannot independently bind the richer decomposition lineage to exact child results and the DecompositionReceipt.

Decision Engine has not been requalified against richer parent decomposition state.

Neither issue blocks Slice 1 because Slice 1 emits native CAL results only and does not claim downstream decomposition transport or decision authority.

## Promotion-design disposition

**SUPPORTED_MINIMAL_PROMOTION_SLICE_1**

The smallest justified production candidate is the canonical Contract B 1.2 → frozen CAL V1 verdict runtime with:

- dedicated `claim-audit-v1` entry point;
- exact active semantic registry/authority dependency closure;
- deterministic native result artifacts;
- no semantic widening;
- no claim compiler;
- no quantitative composition wiring;
- no DecompositionComposer production orchestration;
- no Contract C / Decision Engine change;
- no release or tag.

## Next action

Build Slice 1 on this PR from production `main` by copying only the frozen files and packaging changes named above, then run the production-candidate gates.

If implementation requires any semantic edit rather than exact promotion of already-qualified code, stop and return that specific change to research.
