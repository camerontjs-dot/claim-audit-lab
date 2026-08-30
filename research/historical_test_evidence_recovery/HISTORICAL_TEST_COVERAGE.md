---
title: "Historical test coverage versus current scientific questions"
privacy: "private-local"
---

# HISTORICAL_TEST_COVERAGE

Old CAL passing a test is not explicit-machinery validation. Historical **results** characterize the legacy system. Historical **inputs** may be reusable.

## Already established historically (do not rerun for ceremony)

| Claim | Evidence | Limits |
|---|---|---|
| Real pinned retriever + DeBERTa + rules compose | PR #35 integrated smoke, run `33274013299`, byte-identical repeats | 3 synthetic controls, not a corpus |
| Explicit shadow from real `run_default_audit` is reproducible | PR #36 two valid runs; scientific object equal after stripping `execution_head_sha` | 25 e2e cases |
| Parallel epistemic artifact is justified as research observation | PR #37 disposition `PARALLEL_RESEARCH_ARTIFACT_JUSTIFIED_WITH_OPERATOR_GAPS` | not production emission |
| Legacy `not_checkable` compresses distinct evidence states | PR #36: 6 internal divergences vs 2 terminal disagreements; e2e-22 mixed→support_only | 25-case diagnostic |
| Construction-gold 33-case surface exists and is regenerable | GitHub `scripts/build_construction_gold.py` blob `2c677ee2…`; local corpus.json n=33 | derived gold, not human gold |
| Construction gold priced D9–D11 and later v1.12/v1.13 | FINDINGS 22/33 then citable 26/33; adverse P/R 7/7 at v1.13.0 | DEV probe, not a sample |
| 2026-08-19 construction traces were overwritten in place | `DEVIATION.md`; SHA256SUMS fails 34/39 | failure is the record |
| v0.2 lexical matcher is falsified on PILOT-001 | 4/98, κ≈-0.006 | DEV human gold |
| PILOT-001 absence labels tracked bundle starvation | Fisher p=0.0008 on starved vs full | single coder |
| C6a numeric machinery is unreachable when Phase B is neutral | numeric-comparator FINDINGS, 2026-08-04 | scaled-30 v1.7.0 traces |
| quantulum3 collapses ranges to midpoints | same probe; `"2.5°C to 4.5°C"` → 3.5 | extractor fact |
| Deterministic bound comparator resolves 6/6 numeric misses as `violates` with 0 false violates on 120 negatives | same probe | one-directional; not a landed rule; not NLI tuning |
| Asking the negated claim does not unlock the abstention mass | negation probe: 5/121 (4.1%) | SLG+scaled-30 |
| SLG 12 worlds are an approved construction freeze | frozen-gold.json `sha256:cc78b390…`; Cameron 12/12 approve | DEV, not validation |
| SLG-09 has no safe general fix from the 2026-07 bidirectional prototype | prototype run 02 | historical |
| Lane A scaled SLG 72 cells preserved CAL relation vs T1; some floor failures | project README | DEV comparisons |

## Reusable as new blind input

| Input | Why | Seal required |
|---|---|---|
| Construction-gold 33 claims+passages+IDs+source_boundary | regenerable from GitHub builder; PR #37 already preregisters this | strip `expected_verdict` / `gold.json` / historical CAL rows |
| Fresh-blind constructed 50 | larger construction twin; builder on GitHub | same |
| SLG 12-world CB packets | facts and claims without parent_verdict in the execution aperture | seal `frozen-gold.json` |
| scaled-30 210 authored claims | no CAL gold; relationship is generation spec | do not promote relationship to gold |
| e2e 25 texts+passage IDs | already used blindly in PR #36/#37 | keep stub expected verdicts out |
| EB challenge-corpus-v1 sources/cases | CLEAN_SEPARABLE by design | keep `gold/` evaluator-only; not a CAL ownership dump |

## Requires fresh execution

Anything whose scientific question is about **current explicit machinery**:

- Cohort A 33-case parallel-artifact shadow (preregistered, not executed)
- Optional SLG Cohort B after a frozen input-only manifest
- Independent-consumer read of the parallel artifact
- Typed numeric/relational operator representation for the e2e-08 shape
- `inapplicable` vs `unknown` as a first-class operator receipt (PR #37 NEXT)

Historical 26/33 on v1.13.0 rules does **not** answer these.

## Cannot answer the current question

| Artifact | Why |
|---|---|
| 2026-08-19 overwritten traces | not attributable to a rules version |
| PILOT-001 exact agreement figures | adaptation set; human gold; Decision G |
| gold-lite API panels | third-party logs; assisted labels |
| v0.2 replay | retired instrument |
| Stub e2e expected verdicts as science gold | software-regression expectations; real NLI disagrees on e2e-08 |
| Threshold-sweep selected floors | adaptation information |
| Huge SLG prepared yaml trees | generated bulk; method already known |

## e2e-08 specifically

**OBSERVED fixture (stub):** claim “The service meets 95 percent uptime and 40 percent capacity.” vs passage “95 percent uptime and 70 percent capacity.” Expected `partially_supported` via `C6a_numeric`.

**OBSERVED real shadow (PR #36/#37):** `p_contradict=0.9970703125`; A4 structural-negation probe abstains with null target; no typed numeric operator; explicit path preserves validity unknown and abstains.

**OBSERVED historical numeric probe:** C6a never runs when NLI is neutral; range extraction is destroyed by the shipped extractor; a separate bound comparator can resolve threshold/bound antecedents without NLI.

**INFERENCE:** historical work already localizes e2e-08 to **operator applicability / missing typed relation state**, which is exactly PR #37's disposition. It does **not** justify threshold tuning. It does **not** make the numeric refutation semantically validated.

**HYPOTHESIS:** the cheapest new discriminating test is a typed numeric/relational operator receipt on frozen e2e-08 (and CG-05 `instantiates_bound`, CG-12 numeric contradiction, scaled-30 bound claims) without touching DeBERTa thresholds.

## What old testing cannot substitute

Current explicit machinery on construction-gold, SLG, or scaled-30. Those runs were legacy `SupportSignal` + rules. Fresh shadow execution is required for any claim about the parallel artifact.
