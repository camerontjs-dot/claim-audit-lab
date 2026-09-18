# CAL Typed Binary Measurement Machinery RC0 — Terminal Result

Date: 2026-09-17

Classification: Draft Research / evaluator-under-test failure.

## Disposition

**INCONCLUSIVE_EVALUATOR_INVALID.**

No candidate was exposed.

## Frozen lineage

- Gate-0 parent: `22bc5c1d97b78cfe6f9e2f57e52f69d528069b9a`
- Gate-0 typed-contract authority: `7463ada3358f24fa5bb53fe82631a69064346bf3`
- frozen RC0 apparatus head: `a0f2aecfeaf4c6846f4a2f808f6e03726b9e29d6`
- capability-absence run: `35290968619`

The run passed all 6 evaluator-control tests and then failed exactly because `candidate.py` did not exist.

## Invalidating defect

`RF11: B owns A.` was classified as FAIL_CLOSED.

That sentence is not semantically invalid for the closed `OWNS` predicate. It is a legitimate typed atom with reversed arguments:

`RelationAtom(subject="b", predicate="OWNS", object="a")`

Treating any parse as unsafe rewards refusal rather than argument preservation. It also cannot distinguish a correct reversed atom from the weak failure mode the control intended to detect: incorrectly coercing `B owns A` into `A owns B`.

## Successor requirement

RC1 must freeze `B owns A` as a diagnostic with an exact expected atom. Argument-erasing machinery should fail by producing the wrong diagnostic claim, while correct machinery may either emit the exact atom or conservatively remain unresolved.

All true family-neighbor and unsafe-composition controls remain fail-closed.

No candidate qualification, production wiring, merge, or release is authorized from RC0.
