# First genuine CAL Pipeline B-side receipt

Status: frozen research receipt; portable summary only.

## Result

The exact source claim reached Contract D through the Evidence Bundler → Contract B → CAL → Contract C2 → Decision Engine path. The first semantic divergence was at CAL: the frozen strict-comparison instrument returned `not_checkable` with `MEASUREMENT_MISS` / `UNRESOLVED`, preserving the admitted passage without inventing a relation.

Contract C2 completed with `not_checkable` / `no_deciding_relation`. Contract D completed with `hold`, and its validation passed. Primary and replay C2/D objects were byte- and hash-identical. This is bounded end-to-end plumbing and abstention evidence for one frozen input. It is not a semantic accuracy result or a production decision.

## Frozen identity

The raw source claim, packets, logs, and local invocation records are not included here. They are identified by hashes so this note can travel without copying private or machine-specific material.

| Object | Frozen identity |
| --- | --- |
| Receipt schema | `first-genuine-b-side-receipt-v1` |
| Source claim ID | `FIRST-GENUINE-B-SIDE-001` |
| Source payload | `sha256:512e7415ac1c54195d14d93b93cbd191d5713689681773f6f60b3633c33c84fa` |
| Contract B | `1.2.0`; bundle `fc459009-fc50-5cc7-a874-0371ce7a3853`; bundle hash `sha256:8c25ad48cb0a87081088706eed98e53bcb426b6f7f1b944ba776db722a134c80` |
| Evidence Bundler profile | `eb-v1-integration-10x3-rc0`; authority head [`4e1f6fe`](https://github.com/camerontjs-dot/evidence-bundler/commit/4e1f6fe00e7c350b28f52bfea14f1f8988847884) |
| CAL current C2 authority | [`8204417`](https://github.com/camerontjs-dot/claim-audit-lab/commit/8204417f478cfbd891499145a7edec5ee33405ad); semantic implementation `847cc970642bb648dc994b929c2053b5c9d4648c` |
| CAL integration candidate recorded by the freeze | [`d03d0e9`](https://github.com/camerontjs-dot/claim-audit-lab/commit/d03d0e960ad82d889e6763fd4fb53cd24babd187) |
| Contract C2 authority | [`b42c827`](https://github.com/camerontjs-dot/apparatus-contracts/commit/b42c827acb0a9fe65353354d709add0e27bab307); resolver `1d33e0612befcf8016816197c90c062373796df9` |
| Contract D authority | [`298a1a0`](https://github.com/camerontjs-dot/apparatus-contracts/commit/298a1a0f7b7b6d7712e11200d04faec3e1ca169b) |
| Decision Engine | [`b1bcc33`](https://github.com/camerontjs-dot/decision-engine/commit/b1bcc33e2b5ef0707b8cbf7dd8e821b2d34d1b55) |
| C2 object | `sha256:6696bf1fcf92f277767a26d4a8656a03257fdb77074d8a637265bd8ccc7eeda6` |
| Contract D output | `sha256:af5c3c8ee201b29333a9bfa8e63f0d45eafea22b4e62756240e4ff84a05b1817` |
| CAL result | `sha256:d5c771fad5583952e2941c3ffe45a437cb3e2ec281fae73dd3eba44fdede9b5f` |
| Freeze manifest | `sha256:6e71a620b64a11cfb24af879881c149c3769fffeb1af14169306cee3f3d32d94` |
| Execution receipt | `sha256:4c511d0a80f90d81fb57c58059c9138d1b97f43646f5740606ff2ba6fabfcd3f` |

The CAL C2 authority work is recorded in [claim-audit-lab PR #114](https://github.com/camerontjs-dot/claim-audit-lab/pull/114). This receipt is a separate downstream slice from that active research line.

## Observed path

| Stage | Observation | Boundary |
| --- | --- | --- |
| Evidence Bundler / Contract B | Nine candidate relationships were returned; three were retained and one was accepted. Contract-B integrity checks passed. | The bounded candidate depth does not establish corpus completeness. |
| CAL | One passage was admitted. The strict-comparison measurement produced no relation, with `not_checkable` and `MEASUREMENT_MISS`. | CAL did not emit support, refutation, applicability, completeness, or authority. |
| Contract C2 | The result completed as `not_checkable`; terminal reason `no_deciding_relation`. The C2 validation receipt recorded a deterministic repeat with equal bytes. | This is the successor research profile, not a promoted Contract C release. |
| Contract D / Decision Engine | The completed evaluation was `hold`; reason code `contract_c_no_deciding_relation_not_supported`. | No downstream authorization was inferred. |

## Replay

The replay receipt records:

- C2 primary and replay bytes equal;
- C2 primary and replay hashes equal;
- Contract D primary and replay bytes equal;
- Contract D primary and replay hashes equal;
- replay Decision Engine exit code `0`.

## Non-claims

This receipt does not establish:

- that the source claim is true or false;
- CAL accuracy, representative qualification, or fresh-blind acceptance;
- corpus completeness or retrieval recall beyond the recorded bounded run;
- Contract C or Contract D production readiness;
- merge, promotion, release, automatic action, or production authorization.

The execution receipt explicitly records `production_authorization: false`, `promotion: false`, `release: false`, and `semantic_widening: false`. CAL records automatic action as not allowed, and its Contract C handoff remains `not_emitted`.

## Publication boundary

This file is a portable index, not a replacement for the frozen raw receipt. It intentionally excludes the source passage, raw Contract A/B/C2/D packets, execution logs, local absolute paths, and private runtime state. The frozen local record remains the evidence source; this public note records only its bounded identity and disposition.

No semantic code, contract version, release, or production state changes are part of this publication.
