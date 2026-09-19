# CAL V1 Slice 1 Pressure Test Result — 2026-09-19

## Disposition

**SUPPORTED_CONTROLLED_LOCAL_PIPELINE_USE_WITH_TRUSTED_TARGETS**

**UNATTENDED_TARGET_AUTHORING_NOT_QUALIFIED**

No critical runtime safety invariant failed. The candidate held across deterministic replay, clean-wheel equivalence, real EB → Contract B → installed-CAL execution, bundle corruption, target identity/hash attacks, output safety, concurrency, and authority-integrity mutations.

However, the canonical typed-target boundary assumes that target semantics are trustworthy. `validate-bundle` does not establish that active-family fields faithfully represent the exact claim text, and the engine can issue a terminal verdict over a semantically drifted target.

## Exact subject

Frozen local candidate:

- branch: `candidate/cal-v1-0.6.0-local-pipeline-20260918`
- commit: `61cab64149cb6119e4dbe1fe18496f3ccf89002f`
- tree: `a9ea5bad013cf8aac82ee92417bcf45820a1dd89`
- distribution candidate: `0.6.0`
- semantic implementation: `847cc970642bb648dc994b929c2053b5c9d4648c`
- qualified semantic source: `7cf0d2e50562ec4ce4082d1e1c058a11025b1a48`

Upstream pressure subject:

- Evidence Bundler: `4e1f6fe00e7c350b28f52bfea14f1f8988847884`
- Contract B: `1.2.0`
- Contract B production lock: `c314e53bd91c0736aa4370a364673b069aceb43e`

Research branch head:

- `84c4ff3e28344c9f459fa28c5c1bcbd9a856be46`

## Decisive run

Workflow run:

- `35445114191` — **PASS**

Artifact:

- ID `10585087624`
- `cal-v1-slice1-pressure-20260919-84c4ff3e28344c9f459fa28c5c1bcbd9a856be46`
- artifact digest `sha256:a7c5d684965d699ed75239e67fdd5035960d48d37fcb0d08362dcaa38c6a4786`

The artifact contains:

- `pressure-results.json`
- `pressure-summary.md`

## Aggregate result

61 probes completed:

- **47 PASS**
- **7 ROBUSTNESS_LIMIT**
- **6 INTERFACE_GAP**
- **1 OBSERVATION**
- **0 CRITICAL_FAIL**

The final workflow critical-failure gate passed.

## What held

### Semantic direction and composition

Strict comparison:

- exact support → `supported / SUPPORTS`;
- exact reverse → `contradicted / REFUTES`;
- swapped-entity inverse form normalized correctly;
- mixed support/refute → `not_checkable / MIXED_RELATIONS`;
- unrelated evidence alone → `not_checkable / MEASUREMENT_NOT_APPLICABLE`.

Direct event order:

- exact BEFORE support passed;
- direct AFTER refutation passed;
- swapped-order/inverse-cue normalization passed;
- mixed support/refute → `not_checkable / MIXED_RELATIONS`;
- positive support plus negative-event unresolved relation → `not_checkable / RELATION_UNRESOLVED`.

### Authority integrity

The runtime refused:

- a measurement receipt from a foreign audit context;
- a forged measurement instrument identity;
- a forged semantic-authority identity.

### Real cross-repository CLI path

The pressure run rebuilt the exact candidate wheel, clean-installed it, and used the installed `claim-audit-v1` executable against real frozen Evidence Bundler output projected to Contract B 1.2.

Observed:

- support case → `supported / SUPPORTS`;
- refute case → `contradicted / REFUTES`;
- `input.mode = contract_b_bundle`.

### Determinism

Passed:

- identical canonical input produced byte-identical output directories;
- source-tree CLI and clean-installed wheel produced byte-identical output directories;
- JSON formatting changes in the target changed the exact input hash but preserved the semantic audit context and conclusion.

### Artifact integrity

Every file hash recorded in the native manifest matched the emitted file bytes.

### Target parser / identity attacks

The CLI rejected:

- wrong claim-text SHA-256;
- proposition/claim ID mismatch;
- unknown semantic-family string;
- duplicate JSON keys.

### Contract B corruption

The CLI rejected:

- passage-byte mutation;
- missing `CONTRACT_VERSION`;
- SHA256SUMS path traversal outside the bundle.

### Output safety

The CLI refused without mutation:

- a non-empty output directory;
- an output path that is a file;
- a symlink output directory.

Concurrency also held:

- two distinct output directories succeeded with byte-identical artifacts;
- two processes racing for the same output produced exactly one successful writer, one refusal, a valid final output, and no temporary-directory residue.

## Bounded grammar robustness limits

No tested equivalent phrase produced the **wrong** terminal direction. The misses failed closed as `not_checkable`.

Strict-comparison misses:

1. plural measure: `higher rates`;
2. lowercase entity names;
3. article before right entity;
4. trailing temporal qualifier.

Direct-event-order misses:

5. article-bearing objects: `the dossier`;
6. lowercase actor names;
7. comma before the temporal cue.

Reporting/scope prefixes did not turn into support/refute, and negative event polarity remained unresolved.

These are coverage limits, not observed unsafe direction flips.

## Target-interface gaps

### 1. Missing family-specific fields are accepted by validation

A strict-comparison target with only `lhs_entity` passed `validate-bundle`.

Execution then failed closed:

- `not_checkable / PROPOSITION_BINDING_FAILED`.

### 2. Unsupported comparison direction is accepted by validation

A target with `comparison_direction = SIDEWAYS` passed `validate-bundle`.

Execution then failed closed:

- `not_checkable / PROPOSITION_BINDING_FAILED`.

### 3. Extra semantic fields are accepted and ignored by the active relation logic

Target fields:

```json
{
  "lhs_entity": "Alpha",
  "rhs_entity": "Beta",
  "comparison_direction": "MORE_THAN",
  "time_scope": "2025"
}
```

passed validation and produced:

- `supported`
- failure code `null`.

The evidence contained no 2025 qualification. The additional proposition field participates in proposition identity but is not evaluated by strict-comparison relation derivation.

This is a material target-authoring hazard.

### 4. Direction can disagree with the exact claim text

Exact Contract B claim text remained:

`Alpha had a higher rate than Beta.`

The typed target used:

`comparison_direction = LESS_THAN`.

Validation passed and execution produced:

- `contradicted`
- failure code `null`.

The engine consistently followed the typed proposition, not the natural-language claim semantics.

### 5. Entity orientation can disagree with the exact claim text

Exact claim text remained Alpha > Beta.

The typed target specified Beta > Alpha.

Validation passed and execution produced:

- `contradicted`
- failure code `null`.

### 6. An inactive family passes `validate-bundle`

A target using `permission_exception` passed `validate-bundle`, even though `inspect --json` reports only:

- `strict_comparison`
- `direct_event_order`

as active.

Execution failed closed:

- `not_checkable / UNSUPPORTED_SEMANTIC_FAMILY`.

## Interpretation

The evidence supports the frozen Slice 1 runtime as a **safe, deterministic consumer of a correctly authored typed target and released Contract B 1.2 bundle**.

It does **not** support treating `validate-bundle` as proof that the target is a faithful semantic translation of the bound claim text.

The heaviest assumption in the current local-pipeline route is therefore no longer CAL verdict composition. It is **target compilation / target conformance**.

A wrong target can deterministically produce the wrong textual-claim verdict while all hashes and runtime integrity checks remain valid.

## Local pipeline boundary after pressure test

Controlled local pipeline runs remain justified if the typed target is:

- prevalidated;
- generated by a trusted/frozen producer; or
- manually reviewed against the exact Contract B claim text.

Do not yet authorize unattended target generation merely because `validate-bundle` returns `VALID`.

## Smallest successor test

Before unattended pipeline execution, qualify one bounded target-authoring/conformance path for the two active families.

The successor should answer:

1. Can a target producer deterministically derive the exact active-family fields from the bound claim text?
2. Does it reject extra semantic fields not represented in the claim?
3. Does it reject entity/direction/event-order disagreement with the exact claim text?
4. Does it reject inactive families before semantic execution?
5. Can an independent consumer verify the target/claim correspondence without importing the producer implementation?

This may reuse the already-researched claim-compiler work, but that promotion must be decided from live evidence rather than assumed.

## Preserved harness deviations

The following runs are preserved as pressure-apparatus failures and are **not** candidate failures:

- `35444846254`: harness lint failure;
- `35444889684`: superseded intermediate harness run;
- `35444891914`: remaining harness import-rule failure;
- `35444936276`: workflow expression escaping produced an invalid EB path and the matrix aborted.

No CAL pressure disposition was inferred from those runs.

The corrected workflow then passed at `35445009021`, and the second-wave target-semantic matrix passed at decisive run `35445114191`.

## Promotion consequence

No CAL runtime mutation is justified by this pressure test alone.

PR #181 should remain a qualified local-pipeline candidate, but its use claim should be narrowed to **trusted typed targets**.

Target compilation/conformance should be handled as a separate bounded successor rather than widening Slice 1 silently.
