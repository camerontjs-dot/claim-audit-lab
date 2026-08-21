# Research Brief 02: A gold that derives its own answers, and the coupled defect it found

**Claim Audit Lab · DEV construction · 2026-08-19**
**Source directory:** `outputs/2026-08-19-construction-gold/` (sealed, `SHA256SUMS`)
**Pipeline version:** measured on `cal-rules-v1.8.0`; fix landed as `cal-rules-v1.9.0`
**Operating point:** retrieval floor `0.40` · `top_k` 5 · aggregation `max_entailment`
**Status:** engineering finding. Not validation, not gate evidence, not an accuracy claim.
**Landed:** `cal-rules-v1.9.0` (D9 + D10), 2026-08-19, see §7.
**Not a statement about real FDA guidance**. Every passage was written for this corpus.

> **Note added 2026-08-20.** This brief reports the corpus as measured on `cal-rules-v1.8.0`
> with the fix landing in `v1.9.0`; its figures are historical and are not the current result.
> The corpus was re-run on the shipped `cal-rules-v1.13.0` and stands at **26/33**, adverse
> precision **7/7** and recall **7/7**, sealed at
> `outputs/2026-08-20-construction-gold-v1.12.0/` (a historical local receipt; it is not
> part of the public distribution).
>
> The source directory named above has since had its own seal broken: it was re-run in place
> on 2026-08-20, overwriting `audit_results.json` and its traces. Its `corpus.json` and
> `gold.json` still verify and are the inputs the re-run used. See `DEVIATION.md` in that
> directory and DEV-005 in `validation/deviation-log.md`.

---

## Summary

CAL's only human-labelled reference is a 98-claim blind-coded set, PILOT-001. Its weakest
region is *absence* claims, "the guidance does not prescribe X". Across those claims the
coded verdict tracked **how much material happened to be in the bundle** rather than any
stated rule:

| | starved bundle | full bundle |
|---|---:|---:|
| gold says `supported` | **8** | 0 |
| gold says anything else | 0 | **5** |

Perfect separation, Fisher exact **p = 0.0008**, against a 57% starved base rate. Non-absence
claims show no such pattern, and the coder was blind, so this was not deliberate. It is not a
rater-quality problem. It is an **undeclared parameter**: whether the bundle *is* the source.
That single ambiguity accounts for 7 of the 34 CAL-gold disagreements.

Declaring the parameter turns the question from a judgment call into a derivation. This brief
reports what happened when the reference stopped being coded and started being **constructed**.

---

## 1. The instrument

Thirty-three cases in regulatory prose. A function of the construction returns the verdict and
the reason it follows:

```
derive_verdict(relation, source_boundary, claimed_material_is_a_named_gap) -> (verdict, why)
```

That function **is** the gold. The corpus is regenerated rather than trusted, and a validator
fails closed on any recorded verdict that does not re-derive, any passage that is not verbatim,
any absence claim whose bundle is not actually silent, any `exhaustive` bundle that omits a
passage of a source it draws on, and any variant group that does not make a falsifiable
statement.

`source_boundary` takes three values, and the third is not a formality:

| value | means | absence claim is |
|---|---|---|
| `exhaustive` | the bundle is the complete source | decidable |
| `bounded` | the bundle is an excerpt | undecidable |
| `named_missing_material` | an excerpt that names what it left out | decidable *against* the claim, if the material is among the named gaps |

`bounded` is 25 of 33 by design. Real evidence bundles are excerpts, so the excerpt case is
the operating condition and `exhaustive` is the control.

### Variant groups

A group holds everything constant except one declared parameter and states what that parameter
must do. `separates` means the parameter must change the answer; `invariant` means it must not.
Both are scored the same way, CAL's partition of the group must equal gold's, which measures
whether CAL *responds to the parameter correctly*, independent of whether it gets the verdict
right. Failing an `invariant` group is as much a defect as failing a `separates` one.

A human coder cannot produce either kind, because a coder cannot hold everything else equal
while varying one declared assumption.

**One claim, one passage set, three verdicts:**

| | boundary | derived verdict |
|---|---|---|
| CG-08a | `exhaustive` | `supported`, the bundle is the source and is silent |
| CG-08b | `bounded` | `not_checkable`, absence from an excerpt is not absence |
| CG-21 | `named_missing_material`, retention among the named gaps | `contradicted`, the source is stipulated to address it |

---

## 2. Result

**14 of 33.** That is not an accuracy figure: the corpus is deliberately concentrated on shapes
CAL is known or suspected to fail. It is a probe, not a sample.

| by relation | | | by boundary | |
|---|---:|---|---|---:|
| `restates` | 5/6 | | `bounded` | 12/25 |
| `absent_from` | 6/13 | | `exhaustive` | 1/5 |
| `partial_conjunction` | 2/2 | | `named_missing_material` | 1/3 |
| `overgeneralizes` | 1/1 | | | |
| `contradicts` | **0/6** | | | |
| `conjunction` | 0/2 | | | |
| `chains` | 0/1 | | | |
| `instantiates_bound` | 0/1 | | | |
| `weakens` | 0/1 | | | |

Variant-group partition agreement: **4 of 9**.

---

## 3. One rule discards every contradiction in the corpus

Seven cases carry a derived verdict of `contradicted`, six by the `contradicts` relation, plus
one where a named gap makes an absence claim decidably false.

**The entailer identified all seven, at 0.975 to 0.996. `A4_negation_consistency` stood down
all seven.**

| case | entailer | CAL |
|---|---:|---|
| CG-03, shelf-life 36 months on accelerated data alone | contradict **0.9961** | `not_checkable` |
| CG-04, relocation needs no requalification | contradict **0.9946** | `not_checkable` |
| CG-12a / CG-12b, deviation recorded within five days | contradict **0.9829** | `not_checkable` |
| CG-19, every change requires requalification | contradict **0.9907** | `not_checkable` |
| CG-21, absence claim refuted by a named gap | contradict **0.9746** | `not_checkable` |
| CG-24, out-of-scope timeline applied to Building 4 | contradict **0.9902** | `not_checkable` |

Meanwhile CAL emitted `contradicted` exactly three times, and all three are absence claims
whose source is mechanically verified silent. On this corpus the adverse verdict fires **only**
where it should not and **never** where it should: precision 0/3, recall 0/7, with no human in
the loop to disagree with.

This is the same `refutation_stood_down` mechanism that is the largest abstention bucket on
PILOT-001. There, the claim that CAL was wrong rested on contested human gold. Here it rests on
construction.

---

## 4. The finding that matters most: two defects that must move together

`CG-23a` and `CG-23b` are the same claim and the same supporting passage. `CG-23b` adds one
passage stating the identical obligation **for a different site**:

- claim, scoped to Building 4: recorded within **one** business day
- in-scope passage, Building 4, entailed at **0.948**
- out-of-scope passage, the contract testing laboratory, **five** days, reads as contradict at **0.964**

CAL returns `supported` on CG-23a and **`not_checkable` on CG-23b**. The aggregation is
`max_entailment`, which takes the highest score **regardless of its label**, so a passage that
cannot bear on the claim (scoring 0.016 higher) overrode a correct entailment and flipped the
support signal to `contradict`. `A4_negation_consistency` then stood that down.

The coupling is the point:

> **A4's over-suppression is currently masking the aggregation defect.** Fix A4 in isolation and
> CG-23b stops being an abstention and becomes a false **`contradicted`**, an adverse verdict on
> a correctly-sourced claim. The two have to move together.

This is what gets shipped when defects are triaged one at a time, and it took a corpus that can
hold everything else equal to see it.

---

## 5. The distractor result was hollow until the distractors could survive retrieval

Three groups add topically unrelated passages, and CAL's verdict does not move. That looks like
robustness. It is not: **every topical distractor scored 0.125–0.300 against a 0.40 floor**, so
retrieval dropped all of them and the entailer never saw one. The floor did the work; the rule
layer was never tested.

Replacing them with a **scope-mismatched** distractor (near-identical wording, disjoint declared
scope) put the distractor in front of the entailer at 0.738, and the verdict moved immediately.
Same method, opposite result, one design change.

The audit now reports this permanently rather than leaving it to be noticed: it counts agreements
reached with **zero passages entailed** (4 of 14 here, all `A2_retrieval_empty`) and reports how
many distractors cleared the floor. A corpus that cannot reach the component under test should
say so out loud.

The same honesty applies to the boundary: no rule reads `source_boundary`, so the audit prints
`boundary_ever_read: false` and notes that every boundary-axis `invariant` group therefore passes
**vacuously**.

---

## 6. Known defects, reproduced on constructed cases

`CG-05` (10 °C for 7 h against a stipulated cap of 8 °C for 6 h) and `CG-20` (a minimum of 12
entails a minimum of 6) both abstain: the Brief 01 result, *the entailer does not perform the comparison*, on
cases where the intended relation is not in dispute. `CG-06` and `CG-14` show conjunctions
abstaining whole, `CG-14` across two documents; `CG-15` shows a two-hop chain abstaining where
each hop is separately stipulated.

Logged, low severity: the quantity extractor reads **4.0 out of "Building 4"**. A site number is
not a measured value. No rule keys on it today, so nothing is currently wrong, but a numeric
rule that did would read a building name as a bound.

**Follow-up, same day.** A counterfactual probe sorted all eleven remaining misses by
mechanism, and they are not one defect. Three (`CG-06`, `CG-14`, `CG-15`) are clean
*composition* misses: both support passages cleared the floor, each is correctly neutral
alone, and the two concatenated into a single premise entail at 0.976–0.996. The pipeline
has no step at which two passages become one premise. Three more are `A6` abstaining on
purpose. `CG-05` fails twice independently: the second passage misses the floor by 0.047,
*and* the entailer entails the threshold restated verbatim at 0.988 while going neutral on
a satisfying value at 0.011, giving essentially the same answer for 10 °C and 9 °C. Two new
register entries came out of it: **D12**, the first defect no rule change can close, and
**D13**, `explain` telling five of nine `read_silent` cases to find another source when the
evidence they hold settles the claim.

---

## 7. The fix, and what it cost to get wrong

Both defects landed together as `cal-rules-v1.9.0`, because the corpus proved they could
not land separately.

* **D10**, `A4_negation_consistency`'s veto now requires the probe to be at least as
  confident as the contradiction it demotes. A fixed confidence floor does not
  discriminate here: the probe was *confidently* wrong twice. The criterion was not tuned
  to this corpus, it independently preserves the one PILOT-001 claim where the rule does
  real work (primary 0.766, probe neutral 0.996, still demotes).
* **D9**, a new gate, `A5_conflicting_evidence`, ahead of A4 and the degree mapping. When
  two passages take opposite positions and both clear their thresholds, CAL abstains and
  names both rather than resolving a disagreement by a margin of thousandths. It reuses
  the configured thresholds rather than adding a knob, and it covers the false-`supported`
  direction as well as the false-`contradicted` one.

| | v1.8.0 | v1.9.0 |
|---|---:|---:|
| exact agreement | 14/33 | **20/33** |
| `contradicts` relation | 0/6 | **6/6** |
| adverse-verdict precision | 0/3 | **6/9** |
| adverse-verdict recall | 0/7 | **6/7** |
| PILOT-001 verdicts changed | n/a | **2 of 98** (corrected 2026-08-20; published as 0 on a rules-only replay that could not exercise A5, see D15) |
| frozen inference goldens flipped | n/a | **0 of 30** |

Six verdicts moved, all wrong→right; none moved the other way. The PILOT-001 figure is a
rules-only replay over sealed evidence, run twice, once on v1.8.0 as a control, once on
v1.9.0, and the two are identical on all 98 claims in verdict, reason, and fired rules.

**The coupling, verified rather than argued.** Blanking the two signal channels on the
real `CG-23b` trace reproduces the pre-A5 code path exactly:

| | verdict | rules fired |
|---|---|---|
| D9 + D10, as shipped | `not_checkable` / `conflicting_evidence` | `A5_conflicting_evidence` |
| D10 only, A5 blind | **`contradicted`** | `A4_negation_probe_uninformative`, `A4_hard_contradiction` |

Gold is `supported`. Landing the A4 fix on its own would have converted a wrong
abstention into a false adverse verdict on a correctly-sourced claim, the failure this
tool exists to prevent.

`CG-23b` is still a miss, and that is the honest outcome. CAL now abstains and cites both
passages instead of silently picking one; closing it properly needs a scope feature CAL
does not have, which is new capability rather than a defect fix.

## 8. What this changes

Human gold moves from **reference** to **corroboration**. Where the two disagree on a shape the
construction covers, the construction is the answer and the human verdict becomes evidence about
the coder. PILOT-001 keeps its real value, it is a genuinely independent blind check, and it
corroborated the ~20% entailment miss across two label sources, but it stops being the thing
rule changes are scored against.

---

## Boundaries

DEV construction, n=33, chosen to concentrate on suspected failure shapes. Not validation, not
gate evidence, not an accuracy claim. Nothing landed in `src/` from this work beyond an additive
`source_boundary` field that no rule reads; no threshold, rule, or version changed.

Still not covered: partial *contradiction*, temporal or versioned sources, and distractors that
are in-scope but stale. Claims whose support is split across passages that individually entail
nothing were listed here as uncovered; they are now measured, three of the eleven misses, see
section 6. `named_missing_material` has three cases and remains the least exercised boundary value.

The v1.9.0 landing changed rule logic only. No threshold moved, the aggregator is untouched,
and the `source_boundary` field still has no rule reading it.
