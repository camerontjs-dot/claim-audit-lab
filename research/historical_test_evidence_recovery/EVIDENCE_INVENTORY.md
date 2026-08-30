---
title: "Human-readable evidence inventory"
privacy: "private-local"
---

# Evidence inventory (human)

Machine-readable records: [inventory.jsonl](inventory.jsonl).

Two independent classifications per family: scientific use, then migration. Scientific usefulness does not authorize GitHub migration.

## Highest-leverage families

| ID | Scientific use | Migration | Gold leakage | Already on GitHub? |
|---|---|---|---|---|
| github-e2e-25 | sentinel + blind input (if expectations ignored) | DUPLICATE_OF_GITHUB | contaminated if stub gold used | yes |
| construction-gold builder | reproduction apparatus | DUPLICATE_OF_GITHUB | separable | yes |
| construction-gold 2026-08-19 dir | failure/deviation + mixed gold | PORTABLE_BUT_GENERATED; traces untrustworthy | MIXED | no |
| construction-gold v1.13.0 run | historical characterization of **legacy** 26/33 | PORTABLE_BUT_GENERATED; keep local | MIXED | no |
| SLG freeze 12 worlds | blind input + historical | freeze hashes yes; 39M no | MIXED / packets separable | constructor yes |
| scaled-30 | blind input (no CAL gold) | generated bulk | CLEAN_SEPARABLE | no |
| numeric-comparator FINDINGS | failure evidence for e2e-08-class gap | portable FINDINGS only | CLEAN_SEPARABLE | no |
| PILOT-001 | adaptation / human DEV | SENSITIVE_EXCLUDE | MIXED | no |
| PR #36/#37 runs | current explicit shadow | DUPLICATE_OF_GITHUB | clean in design | yes |
| gold-lite panels | insufficient / sensitive | SENSITIVE_EXCLUDE | MIXED | no |
| EB challenge corpus | independent-consumer / metamorphic | wrong owner | CLEAN_SEPARABLE | not CAL |

## Sizes (OBSERVED `du -sh`)

See LOCAL_STATE_INVENTORY.md. Largest local trees: SLG 40M, gold-lite 6.9M, PILOT-001 5.5M, v0.2 replay 5.0M.

## Epistemic limits

Not every file under `outputs/` was opened. Families were inventoried from directory listings, FINDINGS/README/SHA256SUMS, and sampled JSON schemas. Byte-level identity between local `corpus.json` and a fresh builder emission was **not** computed (would be a freeze step).
