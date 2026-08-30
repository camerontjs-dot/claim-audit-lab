---
title: "Live authority at reconciliation"
privacy: "public-research-record"
---

# LIVE_AUTHORITY

Observed 2026-08-30. Do not treat this file as a live dashboard after that date.

## GitHub

| Field | Value | Class |
|---|---|---|
| Repository | `camerontjs-dot/claim-audit-lab` | OBSERVED |
| `main` | `53f0885b111676794d1bd20e10b91aa58b07e9d4` | OBSERVED |
| Release | `v0.5.0` (pre-1.0 MINOR; Contract C 1.0.0 exporter; not PyPI) | OBSERVED |
| `feat/v2-epistemic-pipeline` on origin | `b7254e713feb5556a81fb0c5b39649c415a949c6` | OBSERVED |

Open Draft PRs at inspection:

| PR | Title | Head SHA (as returned) | Base |
|---:|---|---|---|
| 35 | CAL machinery audit baseline | `8c7cb29f6251f4f6566ab5fcc501cddc791e3539` | `main` |
| 36 | production trace → explicit decision shadow | `b487d1dce4cc1a076e3705b0a7ef457e7d438814` | `main` |
| 37 | semantic-operator reconciliation | `64d05b731a4f5b4c0a829a8f03b252fa0103d7fe` | #36 |
| 38 | historical test evidence recovery inventory | `7acad37ba6c0090f77deea51b80989fc84a43b8b` | `main` |
| 39 | Construction Cohort A parallel epistemic shadow | `8f8ec3593bbfe52e26c1fa7d39372acf6458993a` | #37 |
| 40 | NLI measurement discrimination RC0 | `b316d115c82fb635b0e089d43342b4b6e75c326e` | #39 |
| 41 | semantic operator applicability + monotonicity RC1 | `ce935fe94e30470695f7ca0e506afba8963a1b73` | #39 |

`v0.5.0` is a reproducible research/public baseline. It is not treated here as a finished product destination.

## Local authoritative implementation repository

| Field | Value |
|---|---|
| Nested git root | unpublished local workbench (Git remote = this GitHub repo) |
| Branch | `feat/v2-epistemic-pipeline` |
| HEAD | `b7254e713feb5556a81fb0c5b39649c415a949c6` |
| Tree SHA at HEAD (committed) | `fc85172cfae1305837086529fff648d73fe5127e` |
| Working tree | dirty: 8 tracked modifications, 11 untracked paths |
| Upstream | `origin/feat/v2-epistemic-pipeline` at the same commit |

Other local copies classified, not merged:

| Copy | HEAD | Role |
|---|---|---|
| Frozen candidate worktree | `c1e3e58740f8670aa3c89163732d190ef8e48904` | evaluation freeze; blocked |
| Historical-evidence PR #38 worktree | `7acad37ba6c0090f77deea51b80989fc84a43b8b` | sanitized inventory on `main` lineage |
| This reconciliation worktree | `53f0885b111676794d1bd20e10b91aa58b07e9d4` then this branch | isolated from live `main` |
| Stale nested copy under sibling `scaffold-claims-study` | not this remote | not authoritative |
| Several `/tmp` worktrees | prunable / detached | ephemeral |

## Local-versus-GitHub relationship

Verbose Engine §29 classes:

| Comparison | Class | Evidence |
|---|---|---|
| This isolated worktree vs live `main` (before edits) | `SYNCED` | same SHA, clean |
| Unpublished dirty workbench vs its published feature branch | `LOCAL-AHEAD` | same commit; dirty overlay |
| Published `feat/v2-epistemic-pipeline` vs live `main` | `DIVERGED` | merge-base `f0c07e8981b3f883b2f0c12fb0c8be1e265b75f2`; 2 commits on v2, 9 on `main` |
| Frozen candidate vs live `main` | `UNKNOWN` without a dedicated merge-base report in this file | separate freeze; not compared exhaustively here |

Do not treat `LOCAL-AHEAD` dirty overlay as already on GitHub.
