---
title: "Provenance-risk report"
privacy: "private-local"
---

# Provenance-risk report

A failed experiment with good provenance is more valuable than a polished artifact whose history has been erased. This pass preserves failures.

## High-integrity objects

| Object | Bind | Risk |
|---|---|---|
| Live GitHub `main` | `53f0885b111676794d1bd20e10b91aa58b07e9d4` | none for identity |
| e2e module | blob `48a22cfab82ea0a2abd8d1c80d0da32a3dacd260` | none |
| Construction builder | blob `2c677ee29fd121cf1c76b1476664474aa09dc982` | none |
| PR #36/#37 receipts | Actions runs + RESULT hashes in PR bodies | none for those runs |
| SLG freeze | `frozen-gold.json` sha256 `cc78b390…` | high |
| Construction-gold corpus.json / gold.json in 2026-08-19 dir | still match SHA256SUMS | high for inputs; traces fail |

## Known seal / history failures (preserve, do not repair by rehashing)

1. **Construction-gold 2026-08-19 in-place overwrite.** `DEVIATION.md`: 34/39 SHA256SUMS failures. Traces and `audit_results.json` are not the v1.10.0 22/33 result. Manifest was deliberately not regenerated. **Cite FINDINGS + corpus/gold; do not cite those traces.**

2. **SLG `v0.1-frozen-2026-07-15` superseded.** Checkpoint was text-hashed; rev01 freeze is the accepted freeze. Keep the unaccepted attempt.

3. **SLG-09 prototype 01 unaccepted; 02 bound to v1.5 baseline.** No silent replacement.

4. **PR #36 apparatus failures retained:** wrong import path + missing `pipefail`; dataclass dynamic-module registration failure. Later green runs do not erase them.

5. **Local clone vs live `main`.** Live SHA `53f0885b…` is absent locally. Any claim that local workbench “is” current GitHub CAL is false.

6. **Dirty feat/v2 overlay** is excluded from the frozen candidate and is not a provenance bind for historical corpora.

## Medium risk

| Object | Issue |
|---|---|
| Most August probe FINDINGS | name a workbench SHA sometimes (`a633c3d`, `be0ad60`); many do not |
| scaled-30 traces | SHA256SUMS present; exact rules SHA inside traces not globally audited here |
| PILOT-001 earlier runs | gold path bugs historically (wrong field `human_verdict`); later fail-closed |
| Annex eval at `f0c07e8` | rare explicit public-commit bind; gold is provisional |

## Insufficient provenance

- gold-lite raw API panels
- prunable `/tmp` worktrees
- nested `scaffold-claims-study/.../components/claim-audit-lab` stale copy
- MAP.md (stale)
- RESEARCH_PROOF_INDEX.md last close 2026-07-15 (does not index August families)

## Nested-repository flattening risk

CAL workbench is a nested git repo inside an ignored private coordination root. Copying it into that outer repository or flattening ephemeral worktrees into GitHub history would mix authorities. Stop condition if anyone proposes adding those trees from the outer repo.

## History rewrite risk

Local `main` message is `chore(release): fresh public history at cal-rules-v1.5.0`. Live GitHub now carries 0.5.0 / Contract C history. Do not force-push or assume the local `main` tip is the public history. Treat possible `DISCONNECTED` as **UNKNOWN until a clean clone compares merge-bases**.
