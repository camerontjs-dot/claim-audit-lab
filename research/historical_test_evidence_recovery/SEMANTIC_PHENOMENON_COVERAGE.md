---
title: "Semantic-phenomenon coverage matrix"
privacy: "private-local"
---

# Semantic-phenomenon coverage matrix

Counts are cheap observed N, not sampling weights. Discriminating power matters more than total N. `Current explicit shadow tested` means PR #36/#37 real-model shadow on the 25 e2e cases unless noted.

| Phenomenon | Historical cases | Legacy execution evidence | Blind inputs reusable | Current explicit shadow tested | Remaining gap |
|---|---:|---|---|---|---|
| Direct entailment / identity support | e2e-01; CG restates 6; SLG-01; scaled-30 `states`/`entails` 60 | many legacy traces | yes | e2e-01 and other support cases in 25 | small; sentinel already exists |
| Direct contradiction | e2e-05; CG contradicts 6; SLG-02 | entailer often high p_contradict; A4 historically stood some down | yes | e2e-05 real path | localized; not the current RC gap |
| Lexical / structural negation | e2e-06, e2e-18, e2e-25; SLG-06; negation probe 280 pairs | A3/A4 history; SLG-09 prototype “no safe general fix”; negation probe 4.1% abstention unlock | yes | e2e-06/18/25 in 25 | A4 inapplicability vs unknown still not first-class |
| Numeric equality | e2e-20 approx 40% vs 39.6%; CG VG-EQ-INTERVAL | C6a on some fixtures | yes | e2e-20 | extractor/range issues remain |
| Numeric inequality / mismatch | e2e-08 (40 vs 70 capacity); e2e-17 5 vs 9 mg/kg; CG-03/12 | stub e2e-08 expects partial; **real NLI contradicts** | yes | **e2e-08 is the RC counterexample** | **typed numeric/relational operator missing** |
| Thresholds and bounds | CG-05 instantiates_bound; numeric comparator 6/6 bound misses on scaled-30 | C6a unreachable when Phase B neutral; range→midpoint | yes | e2e-08 only, and it is compound not a bound | **largest remaining operator gap** |
| Percentages | e2e-07/08/20; scaled-30 | mixed C6a vs NLI | yes | e2e-07/08/20 | compound percent+percent (e2e-08) untyped |
| Unit conversions | e2e-17 mg/kg | fixture exists | yes | e2e-17 | no conversion corpus beyond one fixture |
| Quantity mismatch | overlap with numeric inequality | numeric comparator | yes | e2e-08/17 | same operator gap |
| Degree mismatch | e2e-09/10 overstated; CG-20 weakens; scaled-30 overstated 30 | C6b | yes | e2e-09 is PR #37 second disagreement (`unsupported` vs abstain) | reporting-policy + unmeasured validity |
| Quantifier mismatch | e2e-09/10 all/every vs most/some; SLG-04/05 universal | mixed | yes | e2e-09/10 | SLG-04 historically a universal-support miss |
| Categorical incompatibility | SLG-02 drawer A vs B; CG contradicts | construction | yes | little in the 25 | not covered as a named stratum in 25 |
| Scope mismatch | e2e-11 source_scope; CG-24; VG-DIST-SCOPE | C6d / D11 | yes | e2e-11 | construction VG covers more than 25 |
| Multi-passage composition | CG-14, CG-16a/b; SLG-07..10 all_of; e2e-07 compound | composition-and-bound probe: 4/11 misses “composition never formed” | yes | e2e-07, e2e-08, e2e-22 | 25 under-represents conjunction/all_of |
| Mixed support/refutation | e2e-22; SLG-08/09 | PR #36: mixed raw/eligible vs support_only valid | yes | e2e-22 | good sentinel; SLG all_of still needed |
| Irrelevant evidence | VG-DIST-*; e2e-22 subfloor; PR #36 metamorphic control 1 | construction distractors 5/33 | yes | 6 metamorphic controls, not corpus | metamorphic already green |
| Ineligible evidence | PR #36 control 2; C6d | control-only | limited historical corpus | control passed | need corpus cases, not more controls |
| Missing evidence | e2e-15; SLG-03/11/12; CG absence 13 | strong historical | yes | e2e-15 | construction absence is richer (bounded vs exhaustive vs named gap) |
| Semantic operator abstention | A4 null on e2e-08; negation probe | PR #37 | e2e-08 is the case | **tested and preserved** | representation of `inapplicable` vs `unknown` |
| Semantic validity unknown | e2e-08, e2e-09 | PR #37 | yes | **tested** | do not repair by tuning |
| Retrieval failure | e2e-15; PR #35 unrelated weather control | real retrieval floor −0.022 | yes | PR #35 smoke + e2e-15 | adequate sentinel |
| NLI ambiguity | e2e-09 sub-threshold 0.6738; scaled-30 B2 121/210 | abstention decomposition | yes | e2e-09 | do not retune 0.70 |
| Aperture/completeness failure | CG-08a/b retention triple; D6 shadows; PR #36 control 5 | A6 history | yes | metamorphic control only | construction 33 is the right next corpus |
| Execution failure vs epistemic abstention | PR #36 control 6 | control passed | n/a | control | keep distinct; no corpus needed yet |

## Reading

The 25-case shadow already covers many names at N=1. It does **not** cover construction-gold source-boundary, SLG all_of families, or bound-satisfaction as typed operators.

Do not enlarge N for its own sake. The discriminating next cases are:

1. e2e-08-like compound numeric/relational (already frozen)
2. CG-05 bound instantiation
3. CG-08a/b/21 source-boundary triple
4. SLG-04/05/09 quantifier and partial all_of
5. scaled-30 bound claims as **inputs only**, if Cohort A is insufficient
