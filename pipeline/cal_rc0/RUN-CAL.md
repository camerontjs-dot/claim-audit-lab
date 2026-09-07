# Run CAL on one claim

This is the runnable CAL surface for the currently supported RC0 strict-comparison family.

It is intentionally smaller than the full CAL Pipeline. The operator supplies a claim, an explicit typed comparison target, and an explicit evidence world. CAL performs the semantic measurement, atom completion, RC8J warranting, proposition binding, categorical relation derivation, and scoreless composition.

It does **not** perform web search, Evidence Bundler retrieval, Contract A/B/C transport, general claim decomposition, or operational authorization.

## Input packet

Use `cal-runnable-claim-rc0-v1` JSON:

```json
{
  "schema": "cal-runnable-claim-rc0-v1",
  "claim_id": "example-001",
  "claim_text": "Women trailed Men by 11 percentage points.",
  "target": {
    "family": "strict_comparison",
    "lhs_entity": "Women",
    "rhs_entity": "Men",
    "comparison_direction": "less_than"
  },
  "evidence": [
    {
      "source_id": "source-1",
      "passage_id": "passage-1",
      "text": "Women trailed Men by 11 percentage points.",
      "admission": "accepted"
    }
  ]
}
```

Every evidence row requires an explicit `admission` value:

- `accepted`: admit the passage to CAL;
- `rejected`: preserve it in the evidence world but do not let it participate;
- `needs-review`: preserve it as unresolved upstream admission state and do not let it participate.

`accepted` means admitted to the audit. It does **not** mean supporting. CAL derives support/refutation/irrelevance/unresolved after admission.

The current target contract is deliberately explicit. CAL does not yet infer `lhs_entity`, `rhs_entity`, or `comparison_direction` from arbitrary raw English. Hiding that gap behind a heuristic would make the runner look more general than the evidence supports.

## Run

From the repository root:

```bash
uv sync
uv run python pipeline/cal_rc0/run_claim.py path/to/claim.json \
  --out-dir build/cal-runnable-claim
```

On first execution the runner creates `.cal/rc0-deps/` and checks out the exact frozen RC7F-B1 and RC8J commits. Later runs reuse those checkouts and force them back to the pinned identities before execution.

To supply already-prepared exact dependency checkouts instead:

```bash
uv run python pipeline/cal_rc0/run_claim.py path/to/claim.json \
  --rc7fb1-root /path/to/rc7fb1 \
  --rc8j-root /path/to/rc8j \
  --out-dir build/cal-runnable-claim
```

## Outputs

Each successful execution writes:

- `CAL-AUDIT-RESULT.json`: full machine-readable audit receipt, including evidence admission, measurements, typed atoms, warrant status, categorical relations, composition, exact implementation identities, and explicit boundaries;
- `CAL-AUDIT-REPORT.md`: compact human-readable audit result.

The command exits non-zero for malformed input or apparatus/identity failure. A semantic result of `contradicted` or `not_checkable` is still a successful CAL execution and therefore does not make the command fail.

## Current verdict surface

For the supported family, the operator-facing `reported_verdict` is:

- `supported` when warranted categorical support is the deciding relation;
- `contradicted` when warranted categorical refutation is the deciding relation;
- `not_checkable` when CAL abstains, including unresolved measurement/warrant state, mixed support/refutation, or no deciding relation.

The underlying receipt preserves the more specific `conclusion.reason_code` and every passage-level stage rather than collapsing those distinctions.

## Authentication boundary

The standalone runner uses fresh ephemeral HMAC keys inside each process to exercise and verify the existing atom/proposition binding machinery. Those keys are not persisted, so the standalone receipt does not claim portable post-run authentication or production issuer/key management.

That boundary is intentional. A runnable local CAL does not need to pretend that the downstream production authorization envelope has already been solved.
