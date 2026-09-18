# CAL Attribute State Measurement Machinery RC0 — Terminal Result

Date: 2026-09-17

Classification: Draft Research / evaluator-under-test failure.

## Disposition

**INCONCLUSIVE_EVALUATOR_INVALID.**

RC0 must not be used as qualification evidence even though its candidate semantic tests passed.

## Frozen lineage

- Gate-0 parent: `f117698e6db3b47cc68af2024c7816cc8945b004`
- Gate-0 typed-contract authority: `2b4ae5c52f301f16de50719cb11e61919766aa94`
- pre-candidate apparatus: `ef6896f9882bea53c31bec8e44d06e2d25b5c7c8`
- exposed-candidate head: `19659ebb9bdc16e661c10bfa0b5c6d9a7eb075d4`
- exposed-candidate run: `35290862667`

## Invalidating defect

Two RC0 FAIL_CLOSED controls conflated **relevance/binding mismatch** with **semantic invalidity**:

- `AF10: Other batch status is released.`
- `AF11: Document status is released.`

Both can express legitimate attribute-state atoms. A correct generic extractor may safely emit a different entity or domain. RC0 instead classified any claimed output as unsafe, which rewards refusal and cannot distinguish a correct alternate binding from entity/domain erasure.

This is load-bearing because Gate-0 explicitly requires entity/attribute/domain identity to be preserved before relation compilation. The measurement evaluator must test exact binding preservation, not prohibit valid non-query atoms.

## Observed but non-qualifying result

Against the flawed RC0 evaluator:

- direct declared grammar had zero required failures and zero unsafe claims;
- broad copular extraction recovered all five diagnostics but produced ten FAIL_CLOSED claims;
- conservative hybrid recovered all five diagnostics with zero FAIL_CLOSED claims;
- semantic tests and Ruff passed before formatter-only failure.

Those observations are retained, but none qualifies machinery because the evaluator's binding controls are invalid.

## Successor requirement

RC1 must freeze before candidate exposure and:

1. represent valid alternate-entity/domain state surfaces as diagnostics with exact expected atoms;
2. fail broad machinery only when it emits the **wrong binding**, not merely any atom;
3. preserve membership/event/modality/reporting/composition neighbors as true fail-closed controls;
4. rerun from the Gate-0 parent independently of this candidate branch.

No promotion, merge, production wiring, or warrant work is authorized from RC0.
