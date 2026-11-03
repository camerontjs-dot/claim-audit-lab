# Informed development review and evidence limits

## Review context

The implementer had CAL owner/status context and exposed development failures.
The separate review agent read the public builder-only packet, exposed cases,
V2/V3 requirements, current candidate, README and arithmetic controls. It then
authored local diagnostic probes and the reproducible review controls.

This is ordinary informed code review. Separate agent authorship does not
establish independent blind qualification. These tests were used to repair
the candidate and are development evidence from that point forward.

The local candidate checkout materialized only the six upstream development
inputs pinned in `run_development.py`, plus the new D1 directory and workflow.
No source or evaluator bytes were changed. No fresh-source, calibration or
held-out experiment was executed. Full-source product/provenance integration,
independent causal consumption, and runtime/actor admission were not tested.

## U07 receipt decision

The reviewer accepted the explicit property/aspect distinction. Both
level-versus-change directions return `unit_role_mismatch`. Evidence source
observations remain identical when the claim changes, and a literal property
named `rate change` is distinct from a change to the property `rate`.

The V2 compatibility view can name the common property because it separately
retains quantity roles and declares its projection. It must never replace or
rewrite the independent source observations. Controls verify that separation.

## Findings retained and repaired

The initial 37-probe review found two defects (three failures): cross-family
contradictions were hidden by claim-family selection, and conversion provenance
depended on the first selected row. `DEVELOPMENT_LOG.md` records concrete
counterexamples, the exact failed subjects, and the general repairs. Later
strict V2 format rejection is also preserved; tests were not weakened.

Controls cover source conservation, level/change projection, exact arithmetic,
strict and overlapping bounds, contradictory clauses in both orders, original
Unicode spans/hashes, time/measure binding, and abstention on unsupported text.
The 392 arithmetic controls use direct Python integer comparisons as their
oracle, rather than candidate interval internals.

The bounded follow-up expanded the suite to 50 probes, adding byte-serialized
source-conflict invariance across claims, retained unrelated contradictions,
and composed/multiple conversion provenance. It found one additional omission
of the bp/pp rule after an endpoint derivation; that failed subject and raw
result are preserved too. After accumulating both conversions, the final
aggregate passes all 50 probes and all 392 arithmetic controls. No further
review expansion or scientific acceptance is implied by that result.

## Interpretation

The 19 exposed rows show conformance to a known small development contract.
The authored arithmetic and review probes exercise specific risks and revealed
real defects. Their passing result cannot estimate natural-language accuracy,
prove coverage of unseen source forms, or satisfy the frozen S1 builder test.

The candidate is deliberately narrow. Complete CAL process integration,
source quality/provenance, rich linguistic scope, and fresh-source robustness
remain open. The retained `consumed_spans` and deciding-basis declarations
are instrument reports, not observed causal consumption. A separately
reviewed protocol is required before any fresh D1 evaluation or promotion.
