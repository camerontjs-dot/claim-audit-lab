# Contract C Unresolved-Provenance Repair Comparison RC0 — Preregistration

## Classification

Draft Research Infrastructure / representation comparison. No canonical Contract C schema/version, validator, CAL production path, Decision Engine production path, Contract E Authorization, merge, release, tag, or promotion is changed.

## Exact parent counterexample

- parent Draft PR: #99
- exact parent head: `dc6898fd6ab06e3e2fc95d89e4818ea55c5a4689`
- decisive information-sufficiency run: `34505136997`
- artifact: `10163485923`
- artifact digest: `sha256:ab84eda20d93a3a6dec9600d16f35a96e8cebcd94bb27754f3362dbfda4cbd8d`
- disposition: `SUPPORTED_BOUNDED_CONTRACT_C_UNRESOLVED_PROVENANCE_GAP`
- released Contract C authority under challenge: `5fe55f9ed5d0ee9f026ca1b077e9d70ce0487ea1`

The frozen counterexample shows that ordinary support contribution provenance is reconstructable, while a warranted unresolved causal passage is not reconstructable from canonical Contract C 1.0 + the same exact bound Contract-B evidence world because the terminal basis is only an opaque `state:` ID.

## Promotion-era obligation being pressure-tested

EDR-002 required retained contribution/provenance state to preserve stable contribution identity, channel/type and exact Contract-B evidence reference, including non-deciding/residual contributions. The production compression was allowed to remove duplicate role encodings only if the retained representation remained lossless for demonstrated invariants.

This experiment does not assume which repair best satisfies that obligation for the newly demonstrated event-order family.

## Competing candidates

All candidates are research-only shadow representations derived from the same frozen Contract C 1.0 object and upstream causal ground truth.

### A — neutral contribution type

Extend the conceptual contribution channel/type vocabulary with one non-polarized value, `non_deciding`, and represent unresolved causal evidence as an ordinary contribution referenced directly from `conclusion.basis_members`.

Hypothesis: the smallest repair is to restore the original `channel/type` obligation rather than create a second attribution mechanism.

Risk: `contribution` may be read too strongly as support/refutation participation, and adding an enum value is an incompatible change to exact Contract C 1.0.

### B — explicit state-to-evidence attribution edge

Keep support/counterevidence contributions unchanged and add a proposition-level `state_evidence_links` structure mapping opaque causal `state:` basis IDs to exact evidence references.

Hypothesis: unresolved evidence causes an epistemic state but is not itself a support/counterevidence contribution, so attribution belongs in a separate typed edge.

Risk: duplicates provenance structure and adds a new concept/validation surface.

### C — evidence-bearing state basis member

Keep a single state basis object but allow that basis member to carry exact evidence references in addition to its opaque state identity.

Hypothesis: the causal basis is already the right place to encode attribution, so no sibling structure is needed.

Risk: weakens the clean identity-only basis-member abstraction and mixes identity with provenance payload.

### D — immutable producer-attribution sidecar

Leave Contract C bytes unchanged and create a separately immutable receipt bound to exact Contract C `result_set_id` / whole-object SHA-256, proposition ID, opaque state basis ID and exact evidence reference(s).

Hypothesis: Contract C should remain a compact terminal semantic package while deep causal reconstruction is served by a separate producer receipt.

Risk: Contract C alone remains insufficient, conflicting with the original information-sufficiency goal for independent consumers and reports that must not reopen producer internals or invent missing state.

## Required controls

1. **PR #99 unresolved A**: recover exact causal passage A.
2. **PR #99 unresolved B**: recover exact causal passage B.
3. **ordinary support control**: existing support contribution semantics remain sufficient without the new unresolved mechanism.
4. **unresolved multiplicity**: two causal unresolved passages must both remain representable without inventing a unique winner.
5. **mixed admitted evidence**: one support relation plus one unresolved relation where unresolved dominates terminal composition; support provenance must not be silently recast as the unresolved cause.
6. **wrong evidence reference**: tampering one exact evidence reference must be detectable against the bound Contract-B index.
7. **wrong state basis binding**: attribution for one opaque state ID must not be replayable under another state ID.
8. **determinism**: reversing input attribution order may change bytes only where array order is explicitly semantic; canonical candidate generation itself must be deterministic.
9. **Decision projection**: stripping only research-only candidate attribution extensions back to the frozen Contract C terminal state must preserve the same maintained Decision disposition/reason. This is a compatibility diagnostic, not evidence that a real future Contract C version requires stripping.

## Comparison metrics

For each candidate record:

- exact causal evidence reconstructability;
- multiplicity preservation;
- false-polarity risk;
- exact Contract-B reference integrity;
- state identity binding;
- support/refute semantic disturbance;
- canonical byte overhead over the frozen C1 object;
- number of new semantic field/vocabulary concepts;
- whether Contract C alone remains sufficient;
- whether a separate artifact must be co-transported;
- whether maintained Decision semantics can remain unchanged after a truthful version-aware ingress adaptation.

Byte count is diagnostic only. Semantic sufficiency and boundary clarity dominate.

## Hard falsifiers

A candidate is rejected for this bounded gap if it:

- cannot uniquely reconstruct the PR #99 unresolved causal passage;
- requires falsely labeling unresolved evidence `support` or `counterevidence`;
- loses multiplicity or invents a unique winner;
- permits cross-state or wrong-evidence replay without detection;
- changes ordinary support/refute meaning merely to repair unresolved attribution;
- requires a semantic re-audit of Contract-B prose to reconstruct producer attribution.

## Selection rule

Do not select a winner by byte count alone.

A preferred successor may be named only if one candidate preserves all preregistered invariants with strictly smaller conceptual/compatibility cost than the others. If tradeoffs remain genuine, return `NO_UNIQUE_REPAIR_SELECTED` and carry the competing designs forward.

Any preferred result authorizes only a more exact contract-design experiment. It does not authorize changing Contract C 1.0 or assigning a new canonical version.
