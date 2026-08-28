# Apparatus Deviation — Contract C RC2-A D-003

## What was discovered

The first complete producer run (`33136732108`) generated a field-ablation matrix, but that matrix encoded the expected semantic consequence of removing each field family rather than actually deleting the field from the observed RC2 candidate and probing the resulting behavior.

That is insufficient for preregistered Phase 5. In particular, the initial registry classified the public aggregate measurement family (`propositions[].measurements`) as necessary before an actual ablation had shown that any legitimate preregistered consumer or reconstruction invariant depended on it. This could bias the F2/F3 compression question toward retaining F3.

A second validity question also became material after the real run: the generated valid Contract-B artifact contains no `pipeline` selector, while CAL's Contract-B consumer model supplies `v0.2-lexical` as a compatibility default. Before treating the observed v0.2 path as the real locked B -> CAL path, the apparatus must verify against the pinned Apparatus Contract-B validator that adding `pipeline: v1-retrieve-entail` is not a valid alternative Contract-B 1.2.0 configuration.

## Correction

Without changing the candidate projector, primary claim, producer gate, fixture, production code, thresholds, or any prior falsifier:

1. add an executable post-result ablation pass that removes each preregistered field/family from the actually generated candidate, recomputes only the candidate's integrity identity, and records:
   - structural validator behavior;
   - producer-gate behavior;
   - deterministic derived-report behavior;
   - exact-input provenance reconstruction;
   - proposition-identity reconstruction;
   - evidence-reference reconstruction;
   - typed-assessment-state reconstruction;
   - conclusion-basis-state reconstruction;
   - execution-state reconstruction;
   - whether any observed failure is merely a hard-coded validator/renderer expectation;
2. treat a field as demonstrated necessary only when a semantic/reconstruction invariant fails, not merely because `_need(field)`-style validation fails;
3. explicitly report F3 as `necessary`, `folded`, `measurement identity/outcome only`, `private telemetry`, or `unresolved` according to the observed ablation;
4. run the pinned Apparatus `verify-integrity` validator over the exact generated Contract-B 1.2.0 artifact;
5. separately validate the raw `audit_config.yaml`, add only a `pipeline` field in memory, and require the pinned strict Contract-B `AuditConfig` model to reject that mutation. No mutated B artifact is used for CAL execution.

## Scientific-impact assessment

This correction can **weaken** the candidate by demonstrating that a retained field was not justified, and it can invalidate an alternate explanation that a richer CAL v1 bundle path was available under the locked B contract. It cannot turn the already-observed missing exact-basis or typed-assessment receipts into available state.

The prior run therefore remains preserved as preliminary evidence, but the final RC2-A gate/package will be assigned from a fresh run that includes these controls.

## What is unchanged

- CAL production SHA `33a928db97316a3652d57df9cafb8ca240305233`;
- Evidence Bundler production SHA `c8189c31adbab11729c31430c2070126224a2d42`;
- Apparatus production SHA `c314e53bd91c0736aa4370a364673b069aceb43e`;
- Contract B `1.2.0`;
- frozen RC1 predecessor SHAs/tests;
- mixed-format three-proposition fixture;
- primary claim and `SATISFIED` / `FAILED` / `INCONCLUSIVE` producer-gate definitions;
- semantic firewall criteria;
- telemetry-invariance criteria;
- integrity negative control;
- no production code or Contract-B mutation.

No Consumer B handoff occurs before this corrected run is frozen and reviewed.
