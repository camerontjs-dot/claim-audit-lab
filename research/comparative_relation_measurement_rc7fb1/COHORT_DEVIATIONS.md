# RC7F-B1 Held-Out Apparatus Deviations

## B1-D01 — frozen cohort count guard mismatch before candidate execution

First held-out freeze:

`611a87680a8604998bed63f2642f31dd2cb4a591`

Sealed ref:

`sealed/rc7fb1-heldout-cohort-20260831`

Workflow run:

`33464911009`

Artifact:

`9784489485`

Artifact digest:

`sha256:d018892dd06b09711eefe78d19a2e2cbefbc16ee5ac64b2b8e6c96832dbccfe7`

Observed failure: the formal cohort materialized 68 cases, while the terminal bookkeeping assertion incorrectly required 64. The workflow failed in `Guard scientific cohort` while importing the cohort. The scientific candidate step was skipped, so no candidate output against held-out cases was observed.

R1 correction commit `2127c39c8702ab6ce9aa4467e1c57d598cf6450d` changes only the cohort freeze token/bookkeeping count to 68. Case definitions, candidate apparatus, evaluator, and expected semantic objects are unchanged.

Do not count the failed run as scientific evidence for or against the B1 comparison candidate.
