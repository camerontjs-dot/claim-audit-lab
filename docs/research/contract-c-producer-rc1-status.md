# CAL Contract C Producer RC1 Status

**Current status:** experiment executed, final disposition **NEEDS ITERATION**.

Pinned production base: `33a928db97316a3652d57df9cafb8ca240305233`.

The first C1 semantic-package candidate preserves tested consumer-relevant distinctions and supports deterministic report derivation, explicit unknown/failure state, partial execution, lineage, and field-family ablation. It is not promotion-ready because:

1. the candidate is larger than the frozen C0 traces measured;
2. production `AuditTrace` alone lacks exact Contract-B bundle binding;
3. the isolated projector is mechanically code-isolated but was not independently authored because no active Conduit adapter was available.

See:

- `contract-c-field-inventory-rc1.md`
- `contract-c-result-shapes-rc1.md`
- `contract-c-ablation-results-rc1.md`
- `contract-c-failed-attempts-rc1.md`
- `contract-c-result-package-rc1-results.md`

No production exporter/schema change or Contract-C version is justified by RC1.
