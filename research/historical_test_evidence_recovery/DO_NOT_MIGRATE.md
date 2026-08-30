---
title: "Proposed do-not-migrate list"
privacy: "private-local"
---

# Proposed do-not-migrate list

Scientific usefulness does not authorize GitHub migration.

## Do not migrate

| Class | Examples | Why |
|---|---|---|
| Generated research outputs | entire `outputs/` except later redacted notes | live `.gitignore`; sealed locally |
| Broken-seal traces | `outputs/2026-08-19-construction-gold/traces/` | overwritten; not attributable |
| SLG scaled-corpus bulk | 39M prepared/measured trees | generated; method already known |
| PILOT-001 gold and traces | `pilot-001-dev-calibration/`, blinding keys | human gold / adaptation / personal |
| gold-lite API dumps | Anthropic/Codex/MLX panels | third-party payloads |
| v0.2 replay tree | 5.0M | retired instrument; negative evidence stays local |
| Pharma QMS 460 traces | `2026-08-02-pharma-qms-corpus-run/` | generated; not CAL gold |
| Dirty v2 overlay | untracked `v2_pipeline.py`, deep-research adapter | unmanaged; excluded from candidate |
| Virtualenvs, caches, models | `.venv`, HF cache | machine-bound |
| `/tmp` worktrees | prunable cal-public-* | ephemeral |
| Nested stale CAL copy | scaffold-claims-study `components/claim-audit-lab` | wrong authority |
| Real FDA PDF | EB phase-5 demo | third-party |
| Personal website tooling | pharma-sop project | not CAL |
| Mixed `corpus.json` with expected_verdict | construction-gold outputs | gold leakage |
| Selected thresholds | operating-point sweep results as config | adaptation |
| Outer coordination files | local operating contracts, live-state, this workstation | not CAL-owned |
| Credentials / .env / tokens | if found | stop |

## Do not migrate *into CAL* from sibling projects

Evidence Bundler `eb-challenge-corpus-v1` is a strong independent-consumer / retrieval corpus. It has its own owner repository. Copying it into CAL would flatten ownership.

Verified-done mutants are not CAL claim-audit evidence.

## What would be lost by exclusion (and why that is acceptable)

| Excluded | Lost if not on GitHub | Compensation |
|---|---|---|
| 33 traces at v1.13.0 | convenient replay of legacy 26/33 | builder + FINDINGS + SHA256SUMS locally; successor needs fresh execution anyway |
| SLG 12-world freeze file | local-only freeze bytes | constructor on GitHub; hash recorded here |
| PILOT-001 | human DEV gold | Decision G; not confirmatory |
| Numeric comparator results.json | 210-row table | FINDINGS already state the architectural facts |

Unknown remains unknown: no claim is made that every file under `outputs/` was individually opened.
