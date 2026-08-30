---
title: "CAL local pipeline reconciliation"
type: "research-infrastructure-record"
status: "reconciliation-record — no production promotion"
created: "2026-08-30"
privacy: "public-research-record"
do_not_use_for:
  - production CAL changes
  - merge of feat/v2-epistemic-pipeline into main
  - declaring local v2 superior
  - a CAL release
purpose: "Account for unpublished and side-branch local CAL epistemic-pipeline work against live GitHub without wholesale merge."
---

# Local pipeline reconciliation

This is a **repository reconciliation record**, not a successor implementation.

Live GitHub `main` remains the public baseline (`v0.5.0`). The unpublished local working tree was **not** cleaned, reset, or merged. Side-branch `feat/v2-epistemic-pipeline` already exists on GitHub and is **DIVERGED** from `main`. Later Draft research PRs #35–#41 are the current explicit-machinery evidence, not this branch.

## Files

| File | Content |
|---|---|
| [LIVE_AUTHORITY.md](LIVE_AUTHORITY.md) | Live GitHub and local identities |
| [LOCAL_STATE.md](LOCAL_STATE.md) | Frozen dirty-tree inventory |
| [ANCESTRY.md](ANCESTRY.md) | Merge-base and unique commits |
| [IDEA_CORRESPONDENCE.md](IDEA_CORRESPONDENCE.md) | Local v2 vs later explicit machinery |
| [RECONCILIATION_MATRIX.md](RECONCILIATION_MATRIX.md) | Item classifications A–H |
| [PUBLIC_PRIVATE_BOUNDARY.md](PUBLIC_PRIVATE_BOUNDARY.md) | Migrated / retained / sealed |
| [FROZEN_IDENTITIES.json](FROZEN_IDENTITIES.json) | Exact SHAs and portable-file hashes |
| [NEXT.md](NEXT.md) | Recommended next step |

## Terminal decision

**OBSERVED:** GitHub already holds the committed v2 work on `feat/v2-epistemic-pipeline` at `b7254e713feb5556a81fb0c5b39649c415a949c6`. A dirty overlay (experimental runner, Deep Research adapter, probes, experiment JSON) remains unpublished.

**INFERENCE:** current GitHub explicit machinery (`decision_model.py`, `evidence_state.py`, semantic operators, PRs #36–#41) supersedes the local v2 **architecture** as a decision substrate. Local interval algebra, declared coverage complements, and pair-union premises remain **unique nominations** for later bounded research, not merge candidates.

**UNKNOWN:** whether dirty overlay behavior matches the committed v2 rules after uncommitted edits; no execution of that overlay was performed here.

No code was forwarded into `src/`. No release. No history rewrite.
