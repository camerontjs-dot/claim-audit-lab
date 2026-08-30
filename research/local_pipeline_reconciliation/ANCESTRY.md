---
title: "Ancestry of feat/v2-epistemic-pipeline vs main"
privacy: "public-research-record"
---

# ANCESTRY

## Merge base

`f0c07e8981b3f883b2f0c12fb0c8be1e265b75f2` — 2026-08-21 — `test: stabilize public inference receipts`

That commit is public CAL 0.4.0-era history (`f0c07e8` also appears in a sibling annex eval bind). Live `main` then added Contract B/C, `v0.5.0`, and RC1A bounding.

## Commits unique to local / `feat/v2-epistemic-pipeline`

| SHA | Date | Subject |
|---|---|---|
| `b903537d1fb16977d65c42c4aea2958edb171dbc` | 2026-08-22 | `feat(v2): implement deterministic interval algebra and 5-stage epistemic pipeline` |
| `b7254e713feb5556a81fb0c5b39649c415a949c6` | 2026-08-22 | `test(benchmarks): add multi-corpus comparative evaluation script` |

These two commits **are on GitHub** as `refs/heads/feat/v2-epistemic-pipeline`. They are **not** on `main`. Neither is an ancestor of the other line.

`b903537` added:

- `src/claim_audit_lab/v1/interval_algebra.py`
- `src/claim_audit_lab/v1/impl/pipeline_rules.py`
- tests for interval algebra, pipeline rules, X5 twins
- `impl/__init__.py` export change

`b7254e7` added `scripts/compare_v040_vs_v2.py`.

## Commits unique to live `main` (not in v2 HEAD)

Nine commits, including:

- public social-card / README hero (#2)
- Contract B 1.2 factual-context consumption (#14)
- governance PR template
- Contract C 1.0.0 exporter promotion and 0.5.0 release (#25–#27)
- RC1A production-API deferral (`53f0885`)

Live `main` therefore independently gained explicit contribution-ledger machinery, Contract C, and the #35–#41 research stack that v2 never saw.

## Patch-equivalent?

**OBSERVED:** `origin/main` has **no** `interval_algebra.py` and **no** `v1/impl/pipeline_rules.py`. GitHub `decision_model.py` / `evidence_state.py` / `semantic_operators.py` exist on `main` and are absent from the v2 commit list above (they arrived on the `main` side of the divergence, or were already on the merge-base).

**INFERENCE:** later GitHub explicit machinery is not a rewrite of the two v2 commits. It is a parallel, more complete state/decision design. Shared vocabulary (eligibility, negation probe, abstention) does not make the implementations patch-equivalent.

## Dirty overlay (not in either published tip)

Uncommitted on the unpublished workbench, after `b7254e7`:

- experimental `v2_pipeline.py` runner and tests
- Deep Research → `explicit_claims` adapter and tests
- probe scripts
- experiment JSON
- further edits to interval algebra, pipeline rules, CLI, social card, compare script

That overlay is **LOCAL-AHEAD** of the already-published feature branch.
