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

## D3: informed adversarial review exposes two defects

The ordinary informed reviewer authored 37 probes. The first run passed 34
and failed 3, representing two defects. Raw stdout/stderr and subject hash
are retained in `evidence/review_initial_failure.json`; the complete aggregate
is in `evidence/development_02/`. The exact failing candidate is committed at
`ef417c860488b7ddeb4a43fd94e0992cfc64a890` (SHA-256
`b4fca956f12da66f161efb21ff36d6331fd7129e2f6b434d4e3dcf9ce6ac3975`).

1. An endpoint from 10% to 12% independently yields 2 percentage points and
   20% relative change. When another evidence clause says 10% relative change,
   the percentage-point claim incorrectly received support, in either clause
   order. Consistency had been checked only inside the claim-selected family.
2. A bound using percentage points followed by a decisive stronger basis-point
   bound supported the claim but omitted its conversion. Conversion reporting
   had considered only the first selected observation.

The repair computes every source-local consistency group before claim
selection. A contradictory family for the same property, scope and aspect
blocks a decisive result, even if the claim selects another family. Other
properties' conflicts remain visible without automatically invalidating an
unrelated claim. Conversions are now accumulated across every selected row,
with per-observation provenance and an explicit multi-rule summary.

## D4: preserve strict legacy receipt shape

The first consistency/provenance repair made all 37 review probes and all 392
arithmetic controls pass, with 19/19 relation matches. However, the unchanged
V2/V3 checks rejected every receipt because the new `applied_rules` array had
been added inside their exact `conversion_rule` object. This failure and the
entire candidate output are retained in `evidence/development_03/`, with the
code at `3f747e6062ef7f1ec51fef1d66771f74ca582df8` (SHA-256
`9081e6121bb0e4fb6b5df1dff7fe3dd7c717eab35f28eae238d4f8adc0567848`).

The correction leaves the versioned V2 object with its original three keys.
The extended array lives in the explicitly separate top-level
`conversion_summary` and per-observation `conversion_provenance`. A legacy
scalar is present only for exactly one applied rule; the projection identifies
multiple-rule cases. No evaluator or old result is edited. This is a format
correction after a preserved failed development run.

## D5: composed conversion provenance and final bounded result

The follow-up review expanded to 50 probes. Its first run passed 49 and found
one adjacent provenance defect: endpoint evidence for a basis-point claim
reported the endpoint derivation but omitted the additional bp/pp conversion.
`evidence/review_followup_initial.json` preserves that failure against code at
`261cfe2ab006d58f9c94e8b95a70560f352c2a20` (SHA-256
`d1c8ce22986aa21f8947669e2f1d502799ab5699bb18e615dd0a165b97169eab`).
`_conversions` now accumulates both registered steps instead of returning after
the first derivation. No oracle or expected output was weakened.

The final aggregate is `evidence/development_04/RESULT.json` with complete
candidate outputs in the adjacent `CANDIDATE_RECEIPTS.json`. On CPython 3.12.14:

- All six upstream Git blob pins match.
- Unchanged V1/V2/V3 evaluator self-tests and candidate checks pass.
- Candidate relations match 19/19 exposed cases, with zero false supports,
  false refutations, or missed warranted decisions on those known cases.
- The pinned predecessor matches 6/19, with four false supports and seven
  missed warranted decisions on the same exposed cases.
- All 392 direct arithmetic controls and all 50 informed review probes pass.

Final candidate SHA-256:
`fe1037700d0d21db58b7ed6cd49e460f2c389c6ce1ff9afb7a8cb990981ef868`.
The exact hashes for the adapter, runner and controls are in the final report.

This completes bounded informed development. Scientific qualification,
runtime qualification and promotion are `NOT_RUN`; fresh generalization,
blind implementation and observed causal consumption remain unestablished.
