---
title: "Claim Audit Lab — historical test evidence recovery"
domain: "applied-ai-research"
type: "research-infrastructure-audit"
status: "sanitized-research-record — bulk outputs not migrated"
created: "2026-08-29"
updated: "2026-08-30"
privacy: "public-research-record"
do_not_use_for:
  - production CAL changes
  - threshold tuning
  - Contract C changes
  - promotion of explicit decision machinery
  - workstation backup to GitHub
  - treating old pass/fail as current explicit-machinery validation
purpose: "Recover costly historical CAL evidence, classify scientific reuse separately from GitHub eligibility, and stop before a public dump."
---

# Historical test evidence recovery — index

Research-infrastructure audit. This directory is the sanitized public record. Bulk historical `outputs/` trees, credentials, and machine paths are withheld. The unpublished dirty `feat/v2-epistemic-pipeline` worktree was not committed, cleaned, or reconciled in this PR.

## Authority used

- Live GitHub `camerontjs-dot/claim-audit-lab` for current repository state.
- Live Verbose Engine `camerontjs-dot/verbose-engine` at `3b893f1c0c8c80814bc037ff54aceee2db9c38fb`, especially `project-governance/GITHUB-AND-PR-GOVERNANCE.md` §29.
- Local CAL coordination project and nested workbench as evidence about prior work, not as authority about current CAL behavior.

## Deliverables

| # | File | Content |
|---|---|---|
| 1 | [LIVE_AUTHORITY.md](LIVE_AUTHORITY.md) | Live GitHub `main`, PRs #35–#37, exact SHAs |
| 2 | [LOCAL_STATE_INVENTORY.md](LOCAL_STATE_INVENTORY.md) | Local Git, worktrees, candidate, outputs |
| 3 | [inventory.jsonl](inventory.jsonl) / [EVIDENCE_INVENTORY.md](EVIDENCE_INVENTORY.md) | Machine-readable + human family records |
| 4 | [HISTORICAL_TEST_COVERAGE.md](HISTORICAL_TEST_COVERAGE.md) | What old tests already established |
| 5 | [SEMANTIC_PHENOMENON_COVERAGE.md](SEMANTIC_PHENOMENON_COVERAGE.md) | Phenomenon matrix |
| 6 | [BLIND_INPUT_GOLD_SEPARATION.md](BLIND_INPUT_GOLD_SEPARATION.md) | Input-only vs sealed assessment |
| 7 | [PROVENANCE_RISK.md](PROVENANCE_RISK.md) | Provenance and seal failures |
| 8 | [SENSITIVE_MACHINE_BOUND_EXCLUSIONS.md](SENSITIVE_MACHINE_BOUND_EXCLUSIONS.md) | Sensitive / machine-bound holdings |
| 9 | [MIGRATION_ALLOWLIST.md](MIGRATION_ALLOWLIST.md) | Smallest later GitHub allowlist |
| 10 | [DO_NOT_MIGRATE.md](DO_NOT_MIGRATE.md) | Explicit exclusions |
| 11 | [PREREGISTRATION_RECOMMENDATION.md](PREREGISTRATION_RECOMMENDATION.md) | PR #37 33-case study |
| 12 | [NEW_TESTS_REQUIRED.md](NEW_TESTS_REQUIRED.md) | Smallest genuinely new tests |
| 13 | [INDEPENDENT_CONSUMER.md](INDEPENDENT_CONSUMER.md) | Independent-consumer candidates |
| 14 | [NEXT.md](NEXT.md) | Authorized next actions |
| 15 | [MIGRATION_RECEIPT.md](MIGRATION_RECEIPT.md) | Isolated-worktree publication receipt |

## Terminal decision

**OBSERVED:** historical testing, builders, and frozen runs exist locally in volume. The portable constructors for Construction Invariant Gold and Simple Logic Gold already live on GitHub `main`. GitHub `.gitignore` intentionally excludes `outputs/`.

**INFERENCE:** the scientifically useful GitHub object is already mostly present. Local `outputs/` is a sealed/local evidence archive, not a missing public corpus.

**UNKNOWN at discovery time:** the unpublished local object store did not yet contain live `main` `53f0885b111676794d1bd20e10b91aa58b07e9d4`. A later fetch for this isolated worktree showed `origin/main` is that SHA. The dirty `feat/v2` overlay remains unreconciled.

GitHub migration of historical bulk outputs is **not justified**. This PR publishes only the sanitized inventory and recommendations.
