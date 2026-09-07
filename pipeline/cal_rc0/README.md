# CAL Pipeline RC0 integration build

This directory is the first runnable end-to-end CAL Pipeline assembly built from
the bounded results already established in Evidence Bundler and Claim Audit Lab.

It is an implementation/integration candidate, not a new research programme and
not a release or production authorization.

## Executable path

```text
Contract A 2.0 declared propositions
  -> Evidence Bundler exact declared-child retrieval
  -> preserved candidate pool
  -> retained set
  -> explicit admission
  -> Contract B 1.2 + factual-context history
  -> exact Contract B validation
  -> admitted strict-comparison evidence only
  -> frozen RC7F-B1 measurement
  -> RC0A exact lexical-boundary span anchoring
  -> frozen RC8J authority assessment
  -> authenticated atom warrant + proposition binding
  -> proposition-relative categorical relation
  -> scoreless fail-closed composition
  -> Contract C 1.0 projection
  -> exact Contract C validation
```

The released CAL v1 inference path has no terminal causal role in this vertical.

## Evidence-backed implementation choices

The build uses the exact Evidence Bundler RC0 handoff implementation at
`50270b9bfcf6b5112c6ec88c02c7cdd7215e0ff4`, with the supported retrieval
settings carried into `eb_profile.json`: one query per exact declared child,
candidate depth 5, retained K 3, no parent/child flattening, no learned retriever,
no reranker, and no default root-rescue lane.

CAL consumes only evidence that Contract B factual-context history records as
`accepted`. Retention or nomination alone is not admission.

The semantic path uses the frozen RC0 runtime blob
`b36dacf39d158601368b89df8fa66431ce1b4a07`, plus the supported RC0A
lexical-boundary resolver blob `7dd0b1d0077682d121aaa386067531cca3b742d8`.
The adapter changes only the span-resolution seam. Frozen RC7F-B1 and RC8J
dependencies are checked by exact commit and blob identity before execution.

No confidence, retrieval score, model score, threshold, reader count, or caller
support/refutation polarity can decide a proposition.

## Inputs

`run_pipeline.py` takes four logical inputs:

- a Contract A 2.0 cohort;
- explicit Evidence Bundler admission decisions;
- an Evidence Bundler integration profile;
- a CAL target declaration mapping each declared child proposition to the
  bounded `strict_comparison` family and its exact typed comparison target.

The CAL target declaration is deliberately separate from Contracts A and B.
Those contracts do not own `lhs_entity`, `rhs_entity`, or
`comparison_direction`, and this build does not smuggle those semantic fields
upstream.

The included smoke fixture is intentionally small. It exercises the previously
observed `Women` / `Men` substring collision, a second direct comparison, and a
retained-but-rejected distractor.

## Deliberately unresolved product boundaries

Four details remain visible rather than being silently decided:

1. **Typed target ownership.** The current build accepts an explicit audit-input
   target declaration. The long-term owner and public schema for that declaration
   still need to be locked.
2. **Root composition.** Contract A `all_of` child structure is preserved, but
   this RC0 build emits child-level CAL/Contract C results only. It records the
   root as `NOT_COMPOSED` because no supported CAL rule yet maps child categorical
   conclusions to a root conclusion.
3. **Production key management.** The authenticated receipt mechanism is wired,
   but production issuer identity, key provisioning, rotation, revocation, and
   compromise recovery are not established. `--test-keys` is CI-only.
4. **Operational action.** Decision Engine and Contract E are not part of this
   build. An epistemic conclusion is not operational authorization.

These are end-of-build decisions, not reasons to block the executable vertical.

## Run

The integration workflow checks out all frozen dependencies at exact identities
and runs:

```bash
python pipeline/cal_rc0/run_pipeline.py \
  --cal-head <exact current CAL commit> \
  --evidence-bundler-root <EB checkout> \
  --rc7fb1-root <RC7F-B1 checkout> \
  --rc8j-root <RC8J checkout> \
  --apparatus-b <Contract B authority checkout> \
  --apparatus-c <Contract C authority checkout> \
  --cohort pipeline/cal_rc0/fixtures/cohort.json \
  --admission pipeline/cal_rc0/fixtures/admission.json \
  --targets pipeline/cal_rc0/fixtures/cal_targets.json \
  --eb-profile pipeline/cal_rc0/eb_profile.json \
  --semantic-implementation-sha <exact 40-hex implementation commit> \
  --out-dir pipeline/cal_rc0/run-output
```

Normal execution requires `CAL_PIPELINE_ATOM_HMAC_KEY` and
`CAL_PIPELINE_PROPOSITION_HMAC_KEY`, each at least 32 UTF-8 bytes. The workflow
uses `--test-keys`; those fixed keys are test apparatus only and must not be
treated as production secrets.

The durable success receipt is `PIPELINE-RECEIPT.json`. Failures write
`PIPELINE-FAILURE.json` before the process exits non-zero.
