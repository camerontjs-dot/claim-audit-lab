# Development observations, preserved in order

This is informed ordinary development; no scientific attempt was consumed.

## D0: initial local check and materialization correction

Initial candidate SHA-256: `1203e90e1def27d295173abce800f5bb55bcf7220842691a7c5cae0d92f5056d`.
Initial adapter SHA-256: `91ac00c9fd6172e442eb8a61e4aa832126cca5755a9d24e3fd3091fd82abce1a`.

The first V3 command returned exit 1. U07 reported
`evidence_measure_binding`, `evidence_measure_semantics`, and `refusal_reason`;
the other 18 exposed rows reported no errors. No result is called qualification.

A subsequent exact-byte check found local materialization had appended one LF
to each of six downloaded upstream files. Those local copies were replaced
with the exact connector-returned content and all six Git blob identities were
verified before the next run. No GitHub evaluator or historical bytes changed.
The initial output remains a development observation against those local
copies, not exact-upstream conformance evidence. Candidate bytes were unchanged
during this correction.

The U07 receipt expectation needs explicit review: the independent source parse
calls `The rate increased by 5 percent.` a `rate change`; U07's V2 reference
expects `rate`, whereas other exposed change cases expect a `... change`
measure. Relation correctness and this receipt-convention discrepancy must be
reported separately. The evaluator is not edited in this work.
