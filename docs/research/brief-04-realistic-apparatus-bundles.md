# Research Brief 04 — Realistic apparatus-bundle decision sequence

**Status:** preregistered before fixture/test implementation  
**Branch:** `research/obligation-composition-shadow`  
**Parent result:** Research Results 03  
**Production impact:** none

## Question

Can the relation-preserving CAL shadow survive a more realistic apparatus-shaped audit where several epistemic problems coexist in the same supplied evidence package, rather than being isolated one at a time?

The subject claim is held constant across three immutable bundle snapshots:

> The current AI-assisted deviation-triage workflow is adequately controlled for critical GMP use.

Each later snapshot represents a new evidence bundle, not an in-place edit of the prior bundle.

## Boundary

The experiment begins at the Evidence Builder / Apparatus Contracts → CAL boundary.

Out of scope:

- claim discovery;
- claim decomposition;
- obligation generation;
- retrieval;
- source collection;
- production contract changes;
- production CAL rules or verdicts.

CAL-owned measurement is represented by frozen synthetic channel scores so the experiment can isolate downstream state handling. Those measurements are not claimed to be outputs from the current production NLI model.

## Contract-interface constraint

Locked Contract B currently supplies the bundle manifest, claim identity, evidence passages, counterevidence passages, source trust/provenance, and frozen audit configuration. It does not currently provide fields for:

- contribution eligibility;
- proposition-specific semantic validity;
- evidence aperture/completeness;
- temporal applicability;
- authority/status applicability.

This experiment must **not** silently add those fields to Contract B.

Instead, a clearly labeled research sidecar supplies them. One acceptance test will remove the sidecar and verify that the richer decision input cannot be reconstructed from the Contract-B-shaped material alone.

If the logic passes but requires the sidecar, the result is:

> downstream representation supported; current handoff contract insufficient for this richer decision state.

That is a valid outcome and must not be patched away during the experiment.

## Bundle sequence

### B04-1 — Post-change, supplier unresolved

The frozen bundle contains simultaneously:

- a strong pre-change validation report;
- evidence of human review;
- a supplier/cloud-control attestation;
- a post-change incident contradicting adequate control.

Research annotations state:

- pre-change validation is retained but temporally invalid for the current post-change system;
- human-review evidence is valid support;
- supplier attestation has `eligibility=unknown`;
- incident evidence is valid refutation;
- support/refutation aperture is complete.

**Expected decision:** `eligibility_unknown`.

The presence of strong support and strong refutation must not bypass the unresolved supplier dependency.

### B04-2 — Supplier qualified, incident unresolved

A new immutable bundle retains every B04-1 passage and adds the supplier-qualification record. The supplier attestation becomes explicitly eligible.

The post-change incident remains valid refutation.

**Expected decision:** `mixed_valid_evidence`.

Resolving one unknown must expose the next decision conflict rather than jumping directly to support.

### B04-3 — Remediated and revalidated current state

A third immutable bundle retains all prior evidence and adds:

- CAPA/remediation closure evidence;
- current-state post-change validation.

Research annotations state:

- the old pre-change validation remains retained but non-deciding for the current state;
- the historical incident remains retained but is no longer semantically/temporally valid as refutation of the *post-remediation current-state* proposition;
- supplier qualification and human-review evidence remain valid;
- current-state validation and CAPA closure are valid support;
- aperture is complete.

**Expected decision:** `supported`.

The expected support verdict is acceptable only if the old incident and old validation remain in the raw ledger.

## Frozen measurement fixture

The test harness freezes one support/refutation measurement pair per passage. Passage scores do not change between bundle snapshots.

The only permitted changes across B04-1 → B04-2 → B04-3 are:

1. new evidence entering through a new immutable bundle;
2. explicitly supplied eligibility/validity assessments tied to the current proposition/state;
3. the resulting decision trace.

No score may be changed merely to obtain the expected verdict.

## Hypotheses

### H6 — Bundle-level preservation

Every passage present in an earlier bundle remains present in each later bundle, and every contribution remains visible in the raw decision ledger even when it becomes non-deciding.

### H7 — Sequential uncertainty exposure

Resolving one dependency should reveal the next actual state:

`eligibility_unknown` → `mixed_valid_evidence`

rather than collapsing directly to a favorable result.

### H8 — Current-state resolution without historical erasure

After explicit remediation and current-state revalidation, CAL may support the current-state proposition only while retaining stale validation and historical incident evidence in the ledger with their current non-deciding assessments.

### H9 — Contract sufficiency

The locked C-B-shaped payload alone is expected to be insufficient to reconstruct the rich shadow decision input. The research sidecar is expected to be necessary.

H9 is falsified if the existing Contract B already carries all required decision-state information without inference or external annotation.

## Acceptance gates

The rung passes only if:

1. all three bundle IDs are distinct;
2. bundle evidence grows monotonically, with no passage deleted from a later snapshot;
3. fixed channel measurements are identical for the same passage across snapshots;
4. B04-1 abstains with `eligibility_unknown`;
5. B04-2 abstains with `mixed_valid_evidence`;
6. B04-3 decides `supported`;
7. B04-3 raw ledger still contains the pre-change validation and historical incident;
8. B04-3 valid view excludes those two only because of explicit proposition/state validity assessments;
9. reconstruction without the research sidecar fails explicitly rather than inventing defaults;
10. no production source file is modified;
11. the full public suite, Ruff, formatting check, and mypy remain green.

## Falsification / stop conditions

Stop and record a failed or refined hypothesis if any expected transition requires:

- deleting prior evidence;
- changing an earlier bundle in place;
- changing a frozen passage score;
- treating `unknown` as absent;
- inferring eligibility/validity from score magnitude;
- silently filling missing contract fields;
- changing production CAL code to make the fixture pass.

A test-apparatus defect must be fixed in a separate commit and retained in the visible history.