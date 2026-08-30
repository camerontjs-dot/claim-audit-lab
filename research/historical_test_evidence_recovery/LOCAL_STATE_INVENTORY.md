---
title: "Local CAL state inventory"
status: "read-only-discovery"
privacy: "public-research-record"
---

# LOCAL_STATE_INVENTORY

Discovery-time observations below are frozen as of the read-only pass. A later fetch for this isolated worktree updated `origin/main` to live `53f0885b111676794d1bd20e10b91aa58b07e9d4`. The dirty unpublished overlay was still not edited.

## Correspondence classification

Verbose Engine §29 classes. local preflight tool reported `LOCAL-AHEAD` because the worktree is dirty; that is a valid preflight result and is **not** a complete migration classification against live `main`.

| Comparison | Class | Evidence | Epistemic |
|---|---|---|---|
| Workbench `HEAD` vs `origin/feat/v2-epistemic-pipeline` | commit-identical, working tree dirty | both `b7254e713feb5556a81fb0c5b39649c415a949c6`; 8 modified + 11 untracked | OBSERVED |
| Workbench vs live GitHub `main` `53f0885b…` | **UNKNOWN** | that SHA is not in the local object store (`git cat-file` failed) | OBSERVED |
| Local `origin/main` vs live `main` | **REMOTE-AHEAD** of the stale remote-tracking ref, ancestry to live SHA **UNKNOWN** | local `origin/main` = `376a62b57b32ddd2e937be408e877ad91e6b1367` (2026-08-21); live `main` = `53f0885b…` (2026-08-29) | OBSERVED + INFERENCE |
| `feat/v2` vs local `origin/main` | **DIVERGED** | `rev-list --left-right --count origin/main...HEAD` = `1 2`; merge-base `f0c07e8981b3f883b2f0c12fb0c8be1e265b75f2` | OBSERVED |
| Local `main` branch vs `origin/main` | **REMOTE-AHEAD** | local `main` `e4be24c72f7143013eabd8a5e0dd54d72a8619c3` is behind origin/main by 3 | OBSERVED |
| Frozen candidate vs live `main` | **UNKNOWN** | candidate freeze `c1e3e58740f8670aa3c89163732d190ef8e48904` not compared to live SHA (absent locally) | UNKNOWN |
| Dirty v2 overlay vs GitHub | **LOCAL-AHEAD** (uncommitted) | preflight status entries | OBSERVED |

Do not assume a simple ancestor relationship between unpublished local CAL and GitHub CAL. The discovery pass recorded `UNKNOWN` because live `main` was absent from that object store. A subsequent `git fetch origin main` for this PR showed `origin/main` is `53f0885b111676794d1bd20e10b91aa58b07e9d4`. That does not reconcile the dirty `feat/v2` overlay.

Local preflight on the unpublished dirty worktree: `LOCAL-AHEAD` for reasons `working_tree_has_uncommitted_or_untracked_entries`. This PR did **not** edit that tree. Isolated worktree for this PR: `SYNCED` with live `main`.

## Nested repository identity

| Surface | Path | Role |
|---|---|---|
| Coordination project | `local-coordination-archive/` | private local plans, outputs, candidate worktrees |
| Nested implementation repo | `unpublished-local-workbench/` | GitHub-connected CAL source |
| Frozen candidate worktree | `local-candidate-worktree/candidates/cal-v1-eval-candidate-20260825-01` | `FROZEN` evaluation candidate |

The outer private coordination repository ignores this nested product tree. Dirtiness here is not that outer repository's Git dirtiness.

## Workbench Git

| Field | Value |
|---|---|
| Branch | `feat/v2-epistemic-pipeline` |
| HEAD | `b7254e713feb5556a81fb0c5b39649c415a949c6` |
| Upstream | `origin/feat/v2-epistemic-pipeline` at the same SHA |
| Remote | `https://github.com/camerontjs-dot/claim-audit-lab.git` |
| Working tree | dirty |

Tracked modifications include `src/claim_audit_lab/cli.py`, `v1/impl/pipeline_rules.py`, `v1/interval_algebra.py`, and related tests. Untracked includes `src/claim_audit_lab/v1/v2_pipeline.py`, deep-research adapter, v2 tests, v2 experiment JSON, and social-card assets. The frozen candidate explicitly excludes this overlay.

## Worktrees

| Path | HEAD | Branch | Notes |
|---|---|---|---|
| `workbench/` | `b7254e713feb5556a81fb0c5b39649c415a949c6` | `feat/v2-epistemic-pipeline` | dirty, current |
| `.worktrees/candidates/cal-v1-eval-candidate-20260825-01` | `c1e3e58740f8670aa3c89163732d190ef8e48904` | `codex/cal-v1-candidate-20260825-01` | frozen candidate |
| `ephemeral-worktree/cal-decomposer-eval-s1` | `b7254e713feb5556a81fb0c5b39649c415a949c6` | detached | ephemeral |
| `ephemeral-worktree/cal-public-followup` | `f0c07e8981b3f883b2f0c12fb0c8be1e265b75f2` | detached | **prunable**; gitdir missing |
| `ephemeral-worktree/cal-public-release-polish` | `a078bd91dbabbfd1651cea5c369dbafbbf021855` | detached | **prunable**; gitdir missing |
| Claude scratchpad `cal-v2` | `edec2ae41ec577210046d70387a07a632fa32abf` | `fix/v2-unvetted-gate-and-measurand` | **prunable**; gitdir missing |

Prunable worktrees are lifecycle findings, not deletion authority.

## Frozen candidate

From `CANDIDATE.json`:

| Field | Value |
|---|---|
| ID | `cal-v1-eval-candidate-20260825-01` |
| State | `frozen_for_evaluation` |
| Advancement | `blocked` |
| Freeze commit | `c1e3e58740f8670aa3c89163732d190ef8e48904` |
| Source commit | `98d09029a722eef4a751547de955a3c36c92a52f` |
| Source tree | `169ae146ff600265436b86d027e077ae5a000e86` |
| Behavior commit | `edec2ae41ec577210046d70387a07a632fa32abf` |
| Rules | `cal-rules-v1.13.0` |
| Distribution | `0.4.0` |

Excluded: dirty feat/v2 overlay, untracked v2 runner, Grok atom/decomposer stream. Fresh-blind acceptance has not been run for this candidate.

## Local branches that never reached current remote (or whose upstream is gone)

| Branch | SHA | Upstream |
|---|---|---|
| `cal-v1-skeleton` | `68c82c88da124ebb5adeb47eb0c65af965e76861` | `origin/cal-v1-skeleton` **gone** |
| `codex/cal-v0.2-stabilization` | `ee518d18d372e3fd2b955851209a30854a638f57` | gone |
| `codex/cal-v1-candidate-20260825-01` | `c1e3e58740f8670aa3c89163732d190ef8e48904` | none |
| `fix/v2-unvetted-gate-and-measurand` | `edec2ae41ec577210046d70387a07a632fa32abf` | none |
| `legacy-biotech-regex` | `a7162b05cc68ed66a7f2ece7364ce4c8bc2f9a2b` | gone |
| `public-followup` | `f0c07e8981b3f883b2f0c12fb0c8be1e265b75f2` | none |
| `public-polish` | `a078bd91dbabbfd1651cea5c369dbafbbf021855` | none |
| `release/v0.4.0` | `3eba6d6bab60e118cccc3e96f73e030ef7c37063` | none |
| `feat/add-social-preview` | `ac117dd3f94fd911f7f477968d4a938cbee84754` | present on origin |

Local tags: `archive/v0.2.0-preserved-20260711`, `migration-snapshot-2026-06-11`, `v0.2.0`, `v0.4.0`.

## Coordination-project historical holdings (not Git-tracked in CAL)

Approximate sizes from `du -sh`:

| Family | Size | Notes |
|---|---:|---|
| `outputs/simple-logic-gold/` | 40M | freeze + 39M scaled-corpus generated tree |
| `outputs/gold-lite-dev-rehearsal/` | 6.9M | assisted gold + API panels |
| `outputs/pilot-001-dev-calibration/` | 5.5M | 98-claim DEV calibration |
| `outputs/v0.2-pilot-replay/` | 5.0M | falsified v0.2 instrument |
| `outputs/2026-08-08-claim-validation-blueprint-shadow/` | 2.9M | |
| `outputs/2026-08-11-d6-a4-offline-probe/` | 2.7M | |
| `outputs/2026-08-02-pharma-qms-corpus-run/` | 2.5M | 460 traces |
| `outputs/2026-08-08-decision-model-shadow/` | 2.1M | |
| `outputs/2026-08-02-qms-claim-generation/` | 1.9M | includes scaled-30 |
| `outputs/v1-acceptance-test/` | 1.8M | 50-item packet |
| Remaining dated probes | <1.5M each | construction-gold ~240–300K |

GitHub `.gitignore` excludes `outputs/`. These trees are local sealed archives by current CAL policy.

Related holdings outside the CAL coordination folder, inspected read-only:

- `sibling-project/scaffold-claims-study/` — PILOT-001 source bundles and blinding key
- `sibling-project/pharma-sop-cal-test-corpora-generation/` — synthetic SOP/annex corpora and a CAL 0.4.0 annex run bound to `f0c07e8`
- `sibling-project/evidence-bundler/` — `eb-challenge-corpus-v1` (CLEAN_SEPARABLE by design)
- `sibling-project/verified-done/` — not a CAL claim-audit corpus

## What was not mutated on the unpublished dirty tree

The dirty `feat/v2-epistemic-pipeline` overlay was left in place. This PR's isolated worktree was created from live `main` after fetching that SHA.
