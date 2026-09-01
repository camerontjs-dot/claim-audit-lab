# RC7F-A1 Pre-Held-Out Deviations

## A1-D01 — nested cue inside anchored clause was omitted

First committed candidate: `d497b353eccb173e161490aae1b3993cedfb14b9`

Qualification run: `33464255914`

Artifact: `9784273868`

Artifact digest: `sha256:52d9440e71b01e994efbe374cd2b15d46bc7843e49f099743fe2178cb2633245`

Observed: 19 probes, 2 failures. `nested-attr-epi` and `nested-cond-epi` retained the outer attribution/conditional scope but omitted `EPISTEMIC` because the candidate admitted a cue only when its match began at or before the anchor start. In both probes the epistemic cue (`probably`) was inside the anchored local-clause span.

Interpretation: pre-held-out implementation defect in scope-path collection, not scientific evidence. No RC7F-A1 held-out cohort existed.

Repair: count a supported epistemic/deontic/quantifier cue as enclosing when its match begins before the anchored observation ends. The authority decision remained fail-closed both before and after repair.

The failed candidate/run remain part of apparatus history and are not counted as successful qualification.
