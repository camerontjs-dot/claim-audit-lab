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

## D1: separate the property from the measurement aspect

The candidate now retains a source-local `property_name` and a separate
measurement aspect (`change` or `level_or_bound`). Selection and compatibility
use both; a level is not interchangeable with its change, including when the
two have the same lexical unit. The original source-local measure label stays
in `source_observations`.

The legacy V2 pair receipt has an explicit compatibility projection: when the
same property is compared across different measurement aspects, its measure
field reports that common property and the quantity-role fields retain the
difference. `receipt_projection` declares this presentation rule. No case ID,
sentence lookup, expected relation, or evaluator import is used by the
candidate. The independent original parses do not receive the other input.

After this general property/aspect change, the unchanged exact V3 evaluator
reports zero errors on all 19 exposed rows. The D0 result and original code
remain committed. This is development correction, not repair of a frozen
scientific attempt.

## D2: inherited repository-wide CI result

The automatically triggered Public suite on the initial D1 implementation
commit `d87717f939db0f44ef69cfaf31832b60a262aba8` reported 976 passed,
1 failed, 5 skipped, and 48 deselected. The failure is
`tests/test_no_authoring_paths.py::test_no_tracked_file_contains_an_authoring_path`.
Its two flagged locations are the historical
`research/cal_v1_independent_judges_natural_rc1_20261004/sources/raw/P08.bin`
and `research/cal_v1_quantity_comparator_binding_rc2_20261004/execution/regression.json`.
Neither is changed by D1. The scanner flags an embedded path in preserved
source material; no source bytes or test expectation were edited to force green.

The exact #214 base's recorded Public suite has the same two offenders and
the same 976/1/5/48 counts, establishing this as an inherited failure.

- D1 initial run: https://github.com/camerontjs-dot/claim-audit-lab/actions/runs/41704154456
- Exact base run: https://github.com/camerontjs-dot/claim-audit-lab/actions/runs/39040337694

The dedicated D1 workflow runs only the exact exposed candidate checks and
authored development controls. Its result must be reported separately from
the repository-wide suite; a green D1 job does not make the full suite green.
