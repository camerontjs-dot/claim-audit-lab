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

## Capability that may be considered for promotion

The frozen architecture is:

```text
Contract A / typed proposition structure
        ↓
Evidence Bundler / Contract B
        ↓
SemanticFamilyRegistry
        ↓
CompositionRegistry
        ↓
scoreless proposition result
        ↓
DecompositionComposer
        ↓
native CAL child + parent results
```

Current active runtime authority remains narrower:

- semantic families:
  - `strict_comparison`
  - `direct_event_order`
- registered composition:
  - `quantitative_change_exact_v1`
- decomposition:
  - root/single
  - declared exact `all_of`

Important reachability constraints:

- ordinary A/B execution does not yet produce active `scalar_value` atomic authority, so quantitative change must not be promoted as an ordinary end-to-end capability merely because the composition module is qualified;
- DecompositionComposer is qualified through the frozen integration harness, but multi-child parent orchestration is not yet a one-command production path.

## Research-qualified extension authority that is not automatically in scope

Research also supports bounded contracts for:

- `deontic_norm`
- `population_membership`
- `scalar_value`
- `event_occurrence`
- `attribute_state`
- `typed_binary_relation`
- `explicit_causal_assertion`

Definition/equivalence collapses to closed typed-binary relation semantics. Explicit entity existence collapses to closed functional attribute-state semantics.

These results may inform future promotion work, but this PR must not silently wire them into production merely because research authority exists.

## Evidence spine

- PR #175 — portable composition vectors; independent consumer in Apparatus Contracts PR #104
- PR #176 — `SemanticFamilyRegistry + CompositionRegistry`
- PR #177 — `DecompositionComposer`
- PR #178 — exact Contract A 2.0 → EB #79 → Contract B 1.2 → CAL children → parent recomposition
- PR #179 — final semantic closure
- PR #180 — terminal prototype freeze

Upstream authorities:
- Contract A `2.0.0`
- Evidence Bundler PR #79 frozen head `4e1f6fe00e7c350b28f52bfea14f1f8988847884`
- EB profile `eb-v1-integration-10x3-rc0`
- Contract B `1.2.0`, production lock `c314e53bd91c0736aa4370a364673b069aceb43e`

## Preserved downstream blocker

Apparatus Contracts PR #107 established:

`C1_CANNOT_AUTHORITATIVELY_BIND_CAL_V1_DECOMPOSITION_RC0`

Contract C 1.0 cannot independently bind the richer CAL V1 decomposition lineage to exact child results and the DecompositionReceipt.

This is not a CAL V1 freeze blocker. It is also not authority to redesign Contract C inside this PR.

Decision Engine has not been requalified against the richer parent state.

## Promotion-design boundary

In scope:

- inspect the delta between production `main` and the frozen V1 research architecture;
- identify which already-qualified source modules and public entry points are genuinely required;
- identify the smallest production-facing orchestration/API/CLI surface needed to expose that machinery;
- determine compatibility and version implications from observed consumer behavior;
- define exact production qualification gates;
- preserve the current active-family and composition reachability limits.

Allowed mutations in this PR should remain minimal and traceable to the frozen evidence.

Protected / prohibited:

- no new semantic family research;
- no widening of warrant/relation semantics;
- no new decomposition modes;
- no scalar-value end-to-end claim without separately demonstrated runtime authority;
- no Contract C redesign;
- no Decision Engine change;
- no release/tag;
- no reinterpretation or deletion of failed research evidence.

## Acceptance condition

This promotion-design step is complete only when the PR makes it possible to answer, from exact diffs and tests:

1. What is the minimum code/configuration surface that must move from the frozen research lineage into production?
2. Which frozen semantic files remain byte-identical?
3. Which runtime entry points become newly reachable?
4. Which capabilities remain research-qualified but unreachable?
5. What production regression and cross-repository conformance gates are required?
6. What SemVer class, if any, would the resulting production change require?
7. What remains blocked downstream by Contract C / Decision Engine?

If answering those questions requires inventing new semantic behavior, stop and return that question to research.

## Current next action

Start by comparing production `main` with the exact frozen semantic subject and decomposing the delta into:

- semantic machinery already qualified;
- research-only harness/evidence;
- integration/orchestration glue;
- packaging/public-surface changes;
- downstream-incompatible state that must remain native CAL output for now.

Then propose the smallest promotion candidate. Do not widen the candidate merely to make the research tree easier to merge.
