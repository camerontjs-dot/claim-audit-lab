---
title: "Recommendation on PR #37 larger-shadow preregistration"
privacy: "private-local"
---

# Recommendation on the existing 33-case preregistration

**Do not change the PR #37 CROSS_CORPUS preregistration to chase historical results.**

## What local history adds

| Question | Answer | Class |
|---|---|---|
| Same 33 cases with stronger provenance? | The **constructor** on live `main` (`2c677ee2…`) is the strongest portable provenance. Local `corpus.json` matches that design (n=33, nine variant groups) but is mixed with `expected_verdict`. Local 2026-08-19 traces are **weaker** (broken seal). | OBSERVED |
| Larger construction corpus? | Fresh-blind constructed twin n=50 exists locally; builder is on GitHub. | OBSERVED |
| Clean SLG input manifest? | 12-world freeze exists locally with hashes; CB packets are separable. A label-sealed input-only manifest for Cohort B is **not yet frozen as a successor object**. | OBSERVED |
| Additional semantic strata? | scaled-30 7×30; X5 twins; numeric comparator bound misses; composition-and-bound 11-miss taxonomy. | OBSERVED |
| Frozen source passages? | Yes in construction-gold, SLG packets, scaled-30, e2e, PILOT-001 bundles. | OBSERVED |
| Historical mutation/metamorphic controls? | PR #36 already has 6; EB challenge corpus has 614 views; X5 twins; SLG pair-invariance. | OBSERVED |
| Useful cross-version cases? | construction-gold v1.8→v1.13 exact-agreement tables; SLG structured-direct v1.7 confirmation. These characterize **legacy** versions. | OBSERVED |
| Previously undiscovered counterexamples? | e2e-08/09 are already in the RC. Numeric comparator shows C6a unreachability and range collapse. Construction DEVIATION is a seal failure, not a semantic counterexample. | OBSERVED |

## Recommendation

**Remain unchanged** for Cohort A identity: all 33 Construction Invariant Gold **inputs**, generated from the frozen GitHub builder, with gold sealed.

Do **not** substitute local 26/33 v1.13.0 scores as a reason to skip execution.

Do **not** expand Cohort A to 50 or 210 before the 33-case input-only freeze and 25-case sentinel reproduce.

Do **not** treat historical SLG Lane A 72 cells as Cohort B. Cohort B still needs a **new** input-only freeze that does not inspect CAL outputs during selection.

Optional later split, only after Cohort A:

1. Bound/numeric operator study (e2e-08, CG-05, scaled-30 bound subset) — separate preregistration, no threshold search.
2. Source-boundary/absence study (CG-08a/b/21) — construction already designed this.
3. SLG all_of families (SLG-07..10) as Cohort B if the freeze gate passes.

None of those supersede the existing preregistration. They are follow-ups.

## What would justify changing the preregistration

Only a demonstrated defect in the 33-case **input** identity: missing passages, non-regenerable builder, or gold already in the execution aperture of the planned runner. Local history did not show that. It showed the opposite: the builder is on GitHub and local mixed `corpus.json` must **not** be the execution object.
