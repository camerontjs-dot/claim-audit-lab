---
title: "Proposed migration allowlist"
privacy: "private-local"
---

# Proposed migration allowlist

This is a **proposal**, not an executed move. No GitHub branch was created.

Goal: smallest portable scientific objects. Not a workstation backup.

## Already on GitHub (do not copy again)

| Path | Reason |
|---|---|
| `scripts/build_construction_gold.py` | 33-case constructor |
| `scripts/audit_construction_gold.py` | auditor |
| `scripts/build_fresh_blind_constructed.py` | 50-case twin constructor |
| `scripts/simple_logic_gold.py` and SLG test/harness family | SLG apparatus |
| `tests/v1/test_pipeline_e2e.py` + `fixtures/traces/` | 25-case sentinel |
| `docs/research/brief-02-construction-gold.md` | public brief |
| `research/` on PRs #35–#37 | current RC evidence |

## Allowlist for a later isolated Draft Research Infrastructure PR

Create from a **clean clone of live `main` `53f0885b…`**, not from the dirty worktree. Stage exact paths only.

| Path | Item | Reason |
|---|---|---|
| `research/historical_test_evidence_recovery/README.md` | sanitized public index | points to live SHAs; no workstation paths |
| `research/historical_test_evidence_recovery/FINDINGS.md` | sanitized conclusions | construction gold already regenerable; outputs/ stay local; e2e-08 gap already localized |
| `research/historical_test_evidence_recovery/CROSSWALK.md` | GitHub object → local archive hash table | hashes only, no bulk traces |
| `scripts/emit_construction_gold_input_manifest.py` **or** a one-shot invocation documented in FINDINGS | generate input-only 33-case manifest from existing builder | required by PR #37 Cohort A; does not copy local mixed `corpus.json` |
| optional: `research/historical_test_evidence_recovery/seals/construction-gold-v0.2.input.sha256` | hash of the generated input-only object | freeze without gold |

If an input-only manifest is committed, it must be generated from the GitHub builder at blob `2c677ee2…` and must omit `expected_verdict`, `gold_verdict`, historical CAL rows, and `derivation` text that encodes the answer.

## Conditional later allowlist (not this PR)

| Path | Condition |
|---|---|
| Numeric-comparator FINDINGS excerpt | only if redacted of local paths; already summarized in this audit |
| Construction-gold `DEVIATION.md` as a research note | failure preservation; do not re-seal |
| SLG 12-world input-only packet | only after a Cohort B freeze design, from constructor + freeze hashes, not the 39M tree |

## Durable local location (already the right place)

This entire discovery directory under CAL `outputs/` is the durable local archive. GitHub `.gitignore` already says outputs are sealed with SHA256SUMS, not version-controlled. That policy is live authority.

## Execution constraints if a PR is later authorized

1. Isolated worktree from live `main` or stacked only if it must consume #37 files.
2. Record exact base SHA.
3. Stage exact paths, never `git add .`.
4. Secret scan + public-surface lint + leak scan on the exact diff.
5. Do not depend on host-control-plane utilities in CAL CI.
6. Clean-clone verification.
7. Draft PR. Do not merge.
8. Do not change `src/`, Contract C, thresholds, or pinned NLI.
