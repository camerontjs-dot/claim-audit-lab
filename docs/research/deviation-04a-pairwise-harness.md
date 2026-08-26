# Rung 04 Apparatus Deviation 04A — Pairwise iteration defect

**Experiment:** Research Brief 04 — Realistic apparatus-bundle decision sequence  
**Classification:** test-harness defect  
**Scientific fixture changed:** no  
**Expected decisions changed:** no  
**Production code changed:** no

## Observation

The first public-suite execution of the realistic bundle rung reached 988 non-skipped tests and reported:

- 986 passed;
- 2 failed;
- 5 skipped;
- 48 research-artifact tests deselected.

The two failures were:

- `test_r04_01_bundles_are_immutable_monotonic_snapshots`
- `test_r04_02_measurements_are_frozen_across_bundle_snapshots`

Both failed before their pairwise assertions executed because the harness used `zip(..., strict=True)` with a three-item sequence and its two-item shifted suffix.

## Root cause

The intended adjacent-pair construction was:

```python
zip(items[:-1], items[1:], strict=True)
```

The initial harness incorrectly used:

```python
zip(items, items[1:], strict=True)
```

Python therefore raised `ValueError` because the iterable lengths were intentionally unequal.

## Impact assessment

This defect does not alter the scientific fixture or the decision-model observations.

In the failed run, the other four Rung 04 tests passed, including the tests that exercised:

- B04-1 → `eligibility_unknown`;
- B04-2 → `mixed_valid_evidence` after supplier qualification;
- B04-3 → `supported` after remediation/current-state validation while stale validation and the historical incident remain in the raw ledger;
- the absence of the richer decision-state fields from the Contract-B-shaped claim/passages;
- explicit failure to reconstruct the rich shadow input when the research sidecar is removed.

The failed run therefore does not falsify H6–H9, but H6's monotonic-preservation and frozen-measurement acceptance checks were not fully executed and require a corrected rerun.

## Resolution

Commit `3da111dd9429b54f3cc786c0801c78da3ae071d5` changed only the two adjacent-pair iterators to slice both inputs to equal length:

```python
zip(passage_maps[:-1], passage_maps[1:], strict=True)
zip(measurement_maps[:-1], measurement_maps[1:], strict=True)
```

No bundle content, measurement score, sidecar annotation, threshold, expected reason code, or expected verdict was changed.

## Disposition

Retain the failed run and this deviation in the experiment history. Interpret Rung 04 only after a full corrected public-suite run completes.