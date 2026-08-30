---
title: "Migration receipt — historical test evidence recovery record"
privacy: "public-research-record"
---

# MIGRATION_RECEIPT

Evidence-preservation publication of the sanitized inventory. Not production authorization. Not a workstation backup.

## Base

| Field | Value |
|---|---|
| Repository | `camerontjs-dot/claim-audit-lab` |
| Isolated branch | `research-infra/historical-test-evidence-recovery-20260830` |
| Base SHA | `53f0885b111676794d1bd20e10b91aa58b07e9d4` |
| Isolated worktree correspondence | `SYNCED` with live `main` before edits |
| Work class | research / research-infrastructure |
| Unpublished dirty tree | left untouched (`feat/v2-epistemic-pipeline` at `b7254e713feb5556a81fb0c5b39649c415a949c6` plus overlay) |

## Included (exact tree)

`research/historical_test_evidence_recovery/` — sanitized Markdown + `inventory.jsonl` only.

## Excluded

- local sealed `outputs/` bulk trees
- `github-preflight.json` (machine-local receipt)
- credentials, virtualenvs, caches, models
- mixed construction-gold `corpus.json` with expected verdicts
- PILOT-001 gold / blinding keys / API panels
- dirty unpublished overlay files

## Staging rule

Exact paths under `research/historical_test_evidence_recovery/`. No `git add .`.

## Redaction

Absolute workstation paths, private coordination-root paths, and ephemeral `/tmp` worktree paths were replaced with labels (`local-sealed-archive/`, `unpublished-local-workbench/`, `sibling-project/<name>`, `ephemeral-worktree/<name>`).

## What this does not establish

Repository-wide reconciliation of unpublished local branches. Merge of PRs #35–#37. Production promotion. Threshold or Contract C change.
