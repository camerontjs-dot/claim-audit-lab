# RC8J Preregistration: Claim-Bound Contract-B Authority Receipt

## Hypothesis

RC8I's four unsafe claim-binding failures can be repaired without changing frozen Contract B integrity semantics or any established semantic gate by inserting one explicit claim-identity check after RC8H's validated source/bundle/passage/span chain and before RC8F's whole-atom identity check.

## Frozen authorities

Contract B:

- repository: `camerontjs-dot/apparatus-contracts`
- commit: `c314e53bd91c0736aa4370a364673b069aceb43e`
- handoff spec blob: `3e49901dff567ff5bbad55a2d6ccdc3ed36a7a26`
- factual-context extension blob: `77645a6adac664892866f3fdf8abf66cd1d0dd10`

Frozen parent stack:

- RC8H: `4b872e455d52d7a682bb719889860d2cac7909a7`
- RC8F: `efc50481be3179332cecb449c3c9c91da7c3dfaa`
- RC8D: `f04f2dc529d3f1a7666d39a3bf9c8a9df87842d1`
- RC8B: `edf84bb5aae0dd217e3f780e7a49767440b7c1e5`

RC8I falsification:

- reveal run: `33670225461`
- artifact: `9862180423`
- unsafe warranted atoms: `4`

## Minimal successor

Add only:

- `raw_claim_id`: referenced canonical Contract B claim identity from the validated semantic-measurement context;
- `authority_subject_claim_id`: claim identity to which the authority receipt asserts it belongs.

After execution, evidence, source, bundle, passage, and admitted-span checks have passed:

- either claim identity missing -> `UNRESOLVED / AUTHORITY_CLAIM_BINDING_UNRESOLVED`;
- claim identities differ -> `REJECTED / AUTHORITY_CLAIM_MISMATCH`;
- claim identities match -> continue into the frozen whole-atom and semantic authority chain.

## Required precedence

Preserve this tested order:

1. execution failure;
2. evidence rejection;
3. source binding;
4. Contract B bundle binding;
5. Contract B passage binding;
6. admitted passage extent and proposal/required-field containment;
7. Contract B claim identity;
8. whole-atom identity;
9. subordinate semantic authority checks.

No confidence, reader count, instrument count, nomination metadata, retrieval rank, or history-count value gains authority.

## Exposed qualification

Before RC8J can be frozen, replay:

- RC8H exposed qualification history;
- RC8H prospective held-out, now exposed;
- RC8I claim-identity falsifier.

For historical non-RC8I cases, inject a neutral matching claim identity. RC8I cases retain their original claim mutations and expected labels.

Hard requirements:

- exact authority status for every exposed case;
- exact typed reason for every exposed case;
- zero unsafe warranted atoms.

## Prospective requirement

If exposed qualification passes, freeze RC8J before creating a fresh held-out. The fresh held-out must independently exercise:

- missing and mismatched claim identity;
- whole-receipt cross-claim transplant with unchanged source/bundle/passage/atom/semantic material;
- source > bundle > passage > claim > atom precedence;
- passage-boundary containment;
- field extraction/value/support controls;
- composition/aperture controls;
- semantic unresolved controls;
- reader/instrument-bank invariance.

## Hard falsifier

One unsafe warranted atom in the fresh held-out falsifies RC8J within that envelope.

## Non-claims

RC8J does not establish canonical atom-ID generation, source-text interpretation correctness, proposition truth, cryptographic authenticity beyond Contract B's validated integrity regime, Contract C projection sufficiency, independent recoverability, or production readiness.

## Non-authorization

No production CAL, Contract B, Contract C, release, merge, or promotion change is authorized.
