---
title: "Sensitive and machine-bound exclusion report"
privacy: "private-local"
---

# Sensitive / machine-bound exclusion report

Private GitHub would still be the wrong place for most of these. Public CAL is certainly the wrong place.

## SENSITIVE_EXCLUDE

| Item | Why |
|---|---|
| PILOT-001 human gold, blinding keys, adjudication packets | single-coder human labels; Decision G DEV; unblinding risk |
| gold-lite `api-response.json` / Codex event logs | third-party account/model payloads |
| `plans/fresh-blind-generation/fresh_blind_human_gold.json` | human gold |
| Operator transcripts under `raw-materials/` | personal/session material |
| Absolute workstation paths in freeze README (Downloads checkpoint path) | machine identity |
| Evidence Bundler phase-5 real FDA PDF | third-party copyrighted source |
| `pharma-sop-cal-test-corpora-generation/tooling/personal-website/` | personal, not CAL |

## MACHINE_BOUND

| Item | Why |
|---|---|
| `.venv/`, `__pycache__`, HuggingFace caches, downloaded models | regenerable, huge |
| MLX determinism control outputs | local Apple stack |
| `ephemeral-worktree/cal-*` worktrees | ephemeral; some prunable |
| Dirty untracked `v2_pipeline.py` overlay | unmanaged local experiment |
| Host scheduler glue | host environment |
| Local agent Ollama generation logs in SLG scaled first-cell | machine/runtime |

## THIRD_PARTY_REVIEW_REQUIRED

| Item | Why |
|---|---|
| PILOT-001 source SOP/guidance bundles | may contain or mimic regulated text; ownership is scaffold-claims-study |
| Pharma SOP synthetic corpus | synthetic GxP prose is probably publishable as fiction, but not as CAL gold and not as real regulation |
| EB challenge corpus | belongs to Evidence Bundler, not a CAL dump |
| Annex I/II matrices | synthetic; still not CAL-owned without a separate ownership decision |

## Generated bulk (not secrets, still excluded)

| Item | Size / note |
|---|---|
| SLG scaled-corpus prepared trees | ~39M / thousands of yaml |
| PILOT-001 calibration traces | 5.5M |
| v0.2 replay | 5.0M |
| pharma QMS 460 traces | 2.5M |
| gold-lite rehearsal | 6.9M |
| decision-model / D6 shadow dumps | 1.5–2.9M |

These are reproducible from smaller inputs or are historical characterization that GitHub already refuses via `outputs/` gitignore.

## Scanner posture

Do not weaken secret scanning, leak scan, or public-surface lint to land a migration. This PR must run those scans on the exact outbound object. Unpublished local inventory copies that still contain workstation paths stay local.
