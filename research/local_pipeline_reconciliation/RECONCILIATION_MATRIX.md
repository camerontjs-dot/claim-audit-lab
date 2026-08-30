---
title: "Reconciliation matrix"
privacy: "public-research-record"
---

# RECONCILIATION_MATRIX

Class letters: A still-useful implementation candidate · B research apparatus · C historical/case-study · D already superseded by GitHub · E generated/reproducible · F private/sealed/contaminated · G ephemeral/machine-bound · H unknown.

Migration decisions in this PR: **record only**. No `src/` forward-port.

| Item | Local identity | GitHub correspondence | Class | Scientific value | Migration this PR | Reason |
|---|---|---|---|---|---|---|
| Published v2 commits | `feat/v2-epistemic-pipeline` `b7254e7` / `b903537` | remote branch exists; not in `main` | C + B | Shows 2026-08-22 attempt at total stages + interval operator | **retain branch; do not merge** | Lineage already on GitHub; merging would smash Contract C / explicit-model `main` |
| Interval algebra | `interval_algebra.py` (+ dirty edits) | absent on `main`; numeric gap named in #38–#41 | A/B | Candidate typed bound operator | **record hashes; no src copy** | Unique, but untested on Cohort A; belongs in a later numeric RC if at all |
| Five-stage `pipeline_rules.run_v2` | committed + dirty | superseded by `decision_model` stage receipts | D + C | Explains removal-log / no-short-circuit belief | record only | Architecture compressed vs later raw/eligible/valid |
| Experimental `v2_pipeline.py` runner | untracked overlay | no equivalent runner on `main` | B | Replay-sufficient envelope; declared coverage complement | record hash only | Dirty, unpublished; do not promote |
| Coverage-complement discipline | overlay request validator | #39 source-boundary gap | A/B | Never invent complement from generic contradiction | record only | Idea is still useful; implementation tied to v2 envelope |
| Pair-union premises | overlay | none | B | Bounded multi-passage NLI | record only | Experiment, not measured family |
| `compare_v040_vs_v2.py` | committed + dirty | none | B/E | Comparative script | record only | Generated-run dependent |
| Deep Research adapter | untracked | uses `explicit_claims` already on `main` | B | Consumer glue | record hash only | Not CAL core; possible third-party packet issues |
| Probe 01 / 04 scripts | untracked | #38 already classified related probes | B | Historical probes | record hashes | Do not dump outputs |
| `experiments/v2-pipeline/*.json` | untracked generated | none | E/F | May contain run labels | **do not migrate** | Generated; possible adaptation leak |
| Social-card dirty/untracked assets | overlay | `main` already has #2 social preview | D | Presentation | do not migrate | Already superseded on `main` |
| CLI dirty hook to v2 | overlay | production CLI on `main` is v1 + Contract C | D | Would mix experiment into default CLI | **do not migrate** | Must not become default engine |
| Frozen candidate 20260825 | separate worktree `c1e3e58` | not `main` | C | Evaluation freeze, blocked | leave frozen | Different authority |
| PR #38 inventory | already on GitHub | this repo | D | Historical tests | none | Already published |
| Local `outputs/` corpora | coordination archive | gitignored | E/F | See #38 | do not migrate | Gold/bulk/private |
| `.venv`, caches, models | workbench ignored | — | G | none | do not migrate | machine-bound |
| Prunable `/tmp` worktrees | ephemeral | — | G | none | do not migrate | gitdir missing |
| Nested sibling CAL copy | `scaffold-claims-study` | stale | D/H | not this repo | do not flatten | ownership boundary |
| Q3 negation-as-qualify | `pipeline_rules._q3_*` | A4 overreach in #39/#41 | D | Negative lesson | record only | Conflicts with later evidence |
| Mixed-evidence resolve | `_r_conflicting` | #41 CG-23b monotonicity | C | Local abstain-on-mixed vs later strengthening bug | record only | Insight, not a merge |
| Human gold / API panels | #38 families | unpublished | F | DEV only | sealed | contamination |

## Decision

Smallest justified GitHub change: **this record**. Not a wholesale merge. Not a v2 release narrative. Not a forward-port of `interval_algebra` until a separately preregistered numeric/operator experiment asks for it.
