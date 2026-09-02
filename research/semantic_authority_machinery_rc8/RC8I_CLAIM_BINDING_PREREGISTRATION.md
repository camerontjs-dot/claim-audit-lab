# RC8I Preregistration: Contract-B Claim Identity Binding Falsifier

## Scientific question

Can a receipt that is fully bound to the correct admitted source, Contract B bundle, Contract B passage, admitted passage extent, and whole-atom identity still be transplanted between two distinct Contract B claims when the local semantic values happen to be identical?

If yes, RC8H remains insufficient as a claim-specific authority gate.

## Frozen parent

RC8H is frozen and must not be modified for this falsifier:

- candidate blob: `4b872e455d52d7a682bb719889860d2cac7909a7`
- candidate freeze: `1d1fec29ad5e08e28d3b9751534b85121221b17c`
- successful fresh prospective result: run `33669801805`, artifact `9862018646`

Frozen parent stack remains:

- RC8F: `efc50481be3179332cecb449c3c9c91da7c3dfaa`
- RC8D: `f04f2dc529d3f1a7666d39a3bf9c8a9df87842d1`
- RC8B: `edf84bb5aae0dd217e3f780e7a49767440b7c1e5`

## Contract B authority

Use the already-frozen Contract B 1.2.0 authority:

- apparatus-contracts commit: `c314e53bd91c0736aa4370a364673b069aceb43e`
- handoff spec blob: `3e49901dff567ff5bbad55a2d6ccdc3ed36a7a26`
- factual-context extension blob: `77645a6adac664892866f3fdf8abf66cd1d0dd10`

Contract B makes `claim_id` a stable canonical identity, claim files are self-contained audit units, history links `claim_id` to admitted `passage_id`, and the 1.2 semantic-measurement context explicitly retains the referenced claim identity. Therefore claim identity is available upstream without inventing new semantic authority.

## Mutation design

Create two distinct Contract B claim identities, `CLAIM_A` and `CLAIM_B`, while keeping the admitted source, bundle, passage, passage extent, atom identity, proposal fields, assertion, operator, field warrants, composition, and aperture unchanged.

Test:

1. positive control: `raw_claim_id == authority_subject_claim_id == CLAIM_A` -> preserve `WARRANTED`;
2. raw claim identity missing -> `UNRESOLVED / AUTHORITY_CLAIM_BINDING_UNRESOLVED`;
3. authority-subject claim identity missing -> same unresolved result;
4. claim transplant `raw_claim_id == CLAIM_A`, `authority_subject_claim_id == CLAIM_B` -> `REJECTED / AUTHORITY_CLAIM_MISMATCH`;
5. whole receipt transplant control with identical semantic values and unchanged source/bundle/passage/atom -> same claim mismatch rejection;
6. execution/evidence precedence controls;
7. source > bundle > passage > claim precedence controls;
8. claim > atom precedence control;
9. downstream semantic unresolved and reader/instrument-bank invariance controls.

## Hard falsifier

Any non-positive claim-binding mutation that reaches `WARRANTED` is unsafe evidence and falsifies RC8H as a sufficient claim-specific authority receipt.

`unsafe_warranted_atoms == 0` is the hard criterion.

## Interpretation boundaries

A failure would establish only that explicit claim identity binding is required in addition to the already-supported RC8H chain. It would not invalidate RC8H's narrower source/bundle/passage/span/atom results.

A success would not establish canonical atom generation, semantic correctness, text interpretation correctness, independent recoverability, production readiness, or Contract C projection.

## Non-authorization

No production CAL, Contract B, Contract C, release, merge, or promotion change is authorized by RC8I.
