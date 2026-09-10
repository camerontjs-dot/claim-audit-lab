# Temporal Contract C / Decision RC0 — Preserved Falsifiers

These failures are evidence records. They do not establish defects in Contract C, RC8J, or the single-relation temporal semantics. They localize missing evidence-world identity at later composition/projection boundaries.

## F1 — first Contract C projector accepts cross-bundle laundering

Frozen first projector:

- freeze: `75242634cc6c638f961035d2f2dc3f8570308090`
- `projection.py` blob: `57d389f8b39d458388a6aed7c99c620ea165354a`

Post-freeze run:

- run: `34434330048`
- artifact: `10135616044`
- digest: `sha256:12f4de30aa98c5ca1775febcc63153f5a85b19255246a4720db5a5f97a38fb64`
- disposition: `FALSIFIED_CROSS_BUNDLE_PROVENANCE_BINDING`

Observed:

- a genuine Phase-3 `SUPPORTS` relation was produced under `bundle-cross-bundle-a`;
- the frozen projector was then supplied `bundle-forged-cross-bundle-b` plus a conformance index repeating the same evidence reference;
- it emitted Contract C naming the forged bundle;
- exact released Contract C 1.0 validation passed against that forged index.

Interpretation:

Contract C validated the object/index pair it was given. The failure is in the producer-side bridge: a naked Phase-3 relation does not expose enough evidence-world identity for the projector to prove that its supplied Contract-B binding is the world under which the relation was warranted.

## F2 — Phase-3 composer accepts relations from different evidence worlds

Frozen Phase-3 relation candidate:

- freeze: `94ea0c7531aeb852520f34bd56393b63a4b5ac75`
- `relation.py` blob: `70f9eff65330c4182b5ac3bd1a11d13059326ed6`
- `candidate.py` blob: `7e964d85eb80298b9b0d5b84eff32e14bed4b013`

Post-evidence run:

- run: `34434431645`
- artifact: `10135645747`
- digest: `sha256:78966ba9e865fc44a9031728ef0a988c61c407d852247cd5b0c881b44b92a91b`
- disposition: `FALSIFIED_COMMON_EVIDENCE_WORLD_BINDING`

Observed:

- `SUPPORTS` relation from `bundle-world-a-support`, bundle hash `sha256:475325e4ed81a812c400109bc2fc7a0e155caaa0a013b12bab2310bde56ec3bb`;
- `REFUTES` relation from `bundle-world-b-refute`, bundle hash `sha256:6be54a7ff487751a929893e5b4ac414d401b2cb1756fb976024a80894849e524`;
- both targeted the same exact proposition;
- the frozen Phase-3 composer accepted both and returned `abstained / mixed_categorical_relations`.

Interpretation:

This does not falsify the proposition-relative relation table for a single authenticated atom. It falsifies the stronger multi-relation claim that exact proposition identity is sufficient composition identity. A common evidence-world binding is also required.

## Successor requirement

The smallest successor must not patch either frozen failed surface. It must introduce a separately testable bound-relation layer that:

1. consumes the original immutable `AuditContext` rather than caller-supplied Contract-B identity;
2. verifies the `MeasurementReceipt` against that exact context;
3. independently reconstructs the event atom/case from the context + measurement receipt;
4. verifies the authenticated atom warrant against that reconstructed case;
5. verifies the exact authenticated proposition binding;
6. re-derives the Phase-3 relation and binds it to the context SHA and exact Contract-B version/id/hash;
7. permits composition only when every bound relation has the identical context/evidence-world identity and exact proposition projection;
8. derives Contract C binding and passage hashes from that same context instead of accepting a caller-supplied evidence index.

Any widening beyond this boundary requires separate evidence.
