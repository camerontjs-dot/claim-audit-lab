# CAL V1 Slice 1 Pressure Test — 2026-09-19

## Classification

Research pressure test of an already-qualified local-pipeline candidate.

No CAL runtime, schema, package, or production-candidate bytes may be changed by this experiment.

## Exact subject

Repository: `camerontjs-dot/claim-audit-lab`

Frozen local candidate:

- branch: `candidate/cal-v1-0.6.0-local-pipeline-20260918`
- commit: `61cab64149cb6119e4dbe1fe18496f3ccf89002f`
- tree: `a9ea5bad013cf8aac82ee92417bcf45820a1dd89`
- distribution candidate: `0.6.0`
- semantic implementation: `847cc970642bb648dc994b929c2053b5c9d4648c`
- qualified semantic source: `7cf0d2e50562ec4ce4082d1e1c058a11025b1a48`

Frozen upstream comparison subject:

- Evidence Bundler: `4e1f6fe00e7c350b28f52bfea14f1f8988847884`
- Contract B: `1.2.0`
- Contract B production lock: `c314e53bd91c0736aa4370a364673b069aceb43e`

## Question

How does the exact local-pipeline candidate behave under adversarial, metamorphic, malformed, concurrent, and natural-language perturbations beyond the qualification happy path?

## Critical invariants

Any failure below blocks the candidate from local pipeline use until understood:

1. Exact support and contradiction controls remain correct for both active semantic families.
2. Inverse/reordered logically equivalent forms do not flip direction.
3. Mixed or unresolved deciding evidence fails closed rather than choosing a side.
4. Unsupported semantic families never produce a terminal support/refute verdict.
5. Target/claim identity or text-hash mismatch is rejected.
6. Duplicate-key or structurally invalid target JSON is rejected.
7. Contract B corruption, missing authority files, and SHA path traversal are rejected.
8. Non-empty/file/symlink output destinations are not overwritten.
9. Replay of identical canonical input is byte-deterministic.
10. Source-tree CLI and the clean-installed candidate wheel are behaviorally and byte equivalent on the same canonical input.
11. Concurrent distinct-output runs are deterministic; same-output contention produces at most one successful writer and no partial result.
12. Output manifest hashes bind the emitted artifacts exactly.
13. The pressure branch remains byte-identical to the frozen candidate for package/runtime/schema sources.

## Interface discriminator

The following is not preregistered as an automatic blocker because the current implementation may intentionally defer family-specific semantic validity to execution:

- Does `validate-bundle` reject an active-family target whose `fields` object is structurally present but semantically incomplete or carries an unsupported direction?
- If validation accepts it, does execution still fail closed with `not_checkable / PROPOSITION_BINDING_FAILED`?

Acceptance would be recorded as an interface-quality gap, not silently relabeled as success.

## Robustness / coverage probes

These probes characterize the intentionally bounded grammar. A miss is not automatically a safety failure if it fails closed, but it may matter for real pipeline usefulness.

### Strict comparison

Probe:

- higher / greater / larger;
- exceeded / trailed;
- swapped entity order;
- uppercase relation cue;
- relation after noun (`rate higher than`);
- plural measure (`rates`);
- lowercased entity names;
- article insertion;
- trailing temporal qualifier;
- reporting/scope prefix.

### Direct event order

Probe:

- canonical BEFORE;
- canonical AFTER refutation;
- swapped event order with inverse cue;
- lowercase actor names;
- article insertion in objects;
- comma around temporal cue;
- reporting/scope prefix;
- negative event polarity.

For equivalent paraphrases, loss of a verdict is recorded as coverage brittleness. A wrong support/refute verdict is a critical semantic failure.

## Additional characterization

Record, but do not gate on a fixed timing threshold:

- repeated direct-audit throughput;
- output/artifact sizes;
- exact failure codes for bounded grammar misses.

## Evidence handling

The harness must write a machine-readable result matrix even when probes fail.

Results must distinguish:

- `PASS`
- `CRITICAL_FAIL`
- `ROBUSTNESS_LIMIT`
- `INTERFACE_GAP`
- `OBSERVATION`

No failure may be deleted to make the aggregate result green.

## Stop rule

Do not modify CAL semantics in this branch.

If a critical invariant fails, preserve the exact counterexample and stop at diagnosis.

If only bounded robustness/interface limits appear, report them and decide separately whether any are important enough to reopen research before local pipeline runs.
