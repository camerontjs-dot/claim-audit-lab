---
title: "Frozen unpublished local CAL state"
privacy: "public-research-record"
---

# LOCAL_STATE

The dirty worktree was inventoried, not cleaned. Paths below are labels, not workstation locations.

## Authoritative unpublished workbench

| Field | Value |
|---|---|
| Branch | `feat/v2-epistemic-pipeline` |
| HEAD | `b7254e713feb5556a81fb0c5b39649c415a949c6` |
| Committed tree | `fc85172cfae1305837086529fff648d73fe5127e` |
| Stashes | none |

## Tracked dirty files (names only)

- `assets/social-card.svg`
- `scripts/compare_v040_vs_v2.py`
- `src/claim_audit_lab/cli.py`
- `src/claim_audit_lab/v1/impl/pipeline_rules.py`
- `src/claim_audit_lab/v1/interval_algebra.py`
- `tests/v1/test_adversarial_twins_x5.py`
- `tests/v1/test_interval_algebra.py`
- `tests/v1/test_pipeline_rules.py`

Diffstat at freeze: 661 insertions / 131 deletions across those eight files.

## Untracked portable sources

SHA-256 of file bytes at freeze (see `FROZEN_IDENTITIES.json`):

- `src/claim_audit_lab/v1/v2_pipeline.py` (experimental runner; 24234 bytes)
- `src/claim_audit_lab/contracts/deep_research_adapter.py`
- `tests/v1/test_v2_pipeline.py`
- `tests/v1/test_deep_research_adapter.py`
- `scripts/probe01_atomicity_bakeoff.py`
- `scripts/probe04_negation_meta_claims.py`
- experiment JSON under `experiments/v2-pipeline/`
- untracked social-card raster/svg variants

## Ignored research families (coordination archive, not this git repo)

Already classified in PR #38. Not re-copied. Largest families remain local-sealed `outputs/` (SLG ~40M, gold-lite, PILOT-001, v0.2 replay). GitHub `.gitignore` continues to exclude `outputs/`.

## Nested / stale

- Frozen candidate `cal-v1-eval-candidate-20260825-01` at `c1e3e58740f8670aa3c89163732d190ef8e48904` — inspection/evaluation freeze, not this overlay.
- Sibling nested `claim-audit-lab` under `scaffold-claims-study` — not this remote; not authoritative.
- Prunable ephemeral worktrees — not recovered.
