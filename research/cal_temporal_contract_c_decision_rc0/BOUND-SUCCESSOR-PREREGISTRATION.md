# Evidence-World-Bound Temporal Relation / Contract C Successor — Preregistration

## Why this successor exists

Two preserved falsifiers localize the same missing invariant:

1. first temporal Contract C projector freeze `75242634...` accepted a genuine relation from bundle A while emitting Contract C bound to forged bundle B (`34434330048`);
2. Phase-3 frozen composer `94ea0c75...` accepted a genuine `SUPPORTS` relation from bundle A plus a genuine `REFUTES` relation from bundle B as one mixed conclusion (`34434431645`).

Neither result falsifies the single-atom proposition-relative temporal relation table. Both falsify treating proposition identity alone as sufficient evidence-world identity.

## Candidate

New files only:

- `bound_relation.py`
- `bound_projection.py`

The failed `projection.py` and Phase-3 relation candidate remain byte-frozen.

A `BoundTemporalProof` retains:

- exact immutable `AuditContext`;
- exact `MeasurementReceipt`;
- consumed passage ID;
- exact temporal proposition;
- authenticated event-atom warrant;
- authenticated proposition binding;
- previously derived Phase-3 relation record.

Verification MUST:

1. bind context claim/proposition identity and claim text;
2. independently reconstruct the event atom from the exact context + measurement receipt;
3. rebuild the RC8J case;
4. reverify the authenticated event-atom warrant against that rebuilt case;
5. reverify the authenticated exact proposition binding;
6. rederive the Phase-3 temporal relation;
7. require byte/structural equality with the supplied relation record;
8. expose the exact `AuditContext.context_sha256`, Contract-B version/id/hash and passage hash.

Composition MUST reject unless every verified relation has identical evidence-world identity:

`(audit_context_sha256, contract_b_version, bundle_id, bundle_hash)`.

Contract C projection MUST derive its input binding and passage index from that same `AuditContext`; it accepts no caller-supplied bundle binding or evidence index.

## Decisive positive controls

1. single same-world `SUPPORTS` proof -> supported;
2. single same-world `REFUTES` proof -> contradicted;
3. same AuditContext containing support + refute passages -> mixed abstention, order invariant;
4. same-world unresolved negative-event proof -> unresolved abstention;
5. Contract C validation passes for all four projected terminal states using exact released Contract C 1.0;
6. deciding/mixed projection carries every deciding relation with exact source/passage/hash provenance;
7. unresolved projection explicitly reports provenance compression because Contract C 1.0 has no neutral/unresolved contribution channel.

## Decisive falsifiers

The successor is falsified if any of the following reaches composition/projection as valid:

1. support proof from bundle A + refute proof from bundle B;
2. same bundle ID with changed bundle hash / changed context;
3. stale MeasurementReceipt under changed bundle or evidence text/hash;
4. stale atom warrant under reconstructed changed context;
5. stale proposition binding under changed proposition text/semantics;
6. caller-modified Phase-3 relation record that disagrees with rederivation;
7. proof whose passage evidence ref does not match the AuditContext;
8. direct attempt to supply an alternate Contract-B binding or evidence index to the bound projector API.

## Downstream gate after bound successor

Only if the bound successor passes may the experiment test unchanged Contract C / maintained Decision behavior. That downstream test must still preserve the separate Contract C 1.0 provenance-compression finding for unresolved/irrelevant relations rather than relabeling them as support/counterevidence.

No Contract C amendment is authorized by this preregistration.
