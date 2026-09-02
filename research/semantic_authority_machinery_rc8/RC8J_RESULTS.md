# RC8J Results: Claim-Bound Contract-B Authority

## Disposition

**SUPPORTED_WITH_BOUNDS** within the frozen prospective envelope.

RC8J is the strongest authority-gate candidate supported by this research thread. This is not production authorization.

## Frozen candidate

- candidate: `authority_contract_rc8j.py`
- candidate blob: `f55156e43e0c1b4a7868bc8339585b8892edda38`
- candidate freeze declaration: `8e75c6782bb95c3763d06230b9c5df2b6af44054`
- parent RC8H blob: `4b872e455d52d7a682bb719889860d2cac7909a7`
- parent RC8F blob: `efc50481be3179332cecb449c3c9c91da7c3dfaa`
- parent RC8D blob: `f04f2dc529d3f1a7666d39a3bf9c8a9df87842d1`
- parent RC8B blob: `edf84bb5aae0dd217e3f780e7a49767440b7c1e5`

Frozen Contract B authority:

- apparatus-contracts commit: `c314e53bd91c0736aa4370a364673b069aceb43e`
- handoff spec blob: `3e49901dff567ff5bbad55a2d6ccdc3ed36a7a26`
- factual-context extension blob: `77645a6adac664892866f3fdf8abf66cd1d0dd10`

## Exposed qualification

Run `33670472654`, job `100382540151`:

- 268 cases
- 268/268 exact authority status
- 268/268 exact typed reason
- 0 unsafe warranted atoms
- artifact `9862279058`
- digest `sha256:bc38b62b93734ab7dbd183228cb82240f5f58f5044d2c174149ad248eafeaa4d`

The exposed qualification replayed the complete prior authority history, RC8H's prospective result, and the RC8I claim-identity falsifier.

## Prospective apparatus

Created only after the RC8J candidate freeze.

Frozen blobs:

- `rc8j_heldout_cohort.py`: `bf1ec5bd1086163460a38e4ccf0ac044fe34c148`
- `rc8j_heldout_evaluate.py`: `1ff6db92d5df1e01540cea79207015cc4f97893a`
- `test_rc8j_heldout_apparatus.py`: `1a2764ace6674abe02f5ebcba66aea257f5950f2`

Accepted pre-reveal push run `33670888377`, job `100383924982`, verified:

- production `src/` and `schema/` unchanged;
- exact frozen Contract B authority bytes;
- exact RC8J/RC8H/RC8F/RC8D/RC8B candidate blobs;
- exact heldout cohort/evaluator/test blobs;
- candidate-blind structural checks.

No heldout candidate execution occurred in that run.

## Prospective result

Reveal push run `33670993492`, job `100384271951`:

- 28 cases
- 28/28 exact authority status
- 28/28 exact typed reason
- 0 unsafe warranted atoms
- 5/5 targeted claim-binding cases remained non-warranted
- bank invariance true for warranted and unresolved controls
- artifact `9862475745`
- digest `sha256:0f377934b1e4adb8e813fd6d5a7c7d2e679cf37ca882d21979ca5889b98141d0`

Expected and observed state distribution matched exactly:

- `WARRANTED`: 3
- `REJECTED`: 12
- `UNRESOLVED`: 12
- `NO_ASSESSMENT`: 1

## Supported transition envelope

Within the tested envelope, a receipt may reach `WARRANTED` only after this chain remains coherent:

1. execution completed;
2. evidence admitted;
3. authority source identity matches the admitted source;
4. authority bundle identity matches the validated Contract B bundle;
5. authority passage identity matches the admitted Contract B passage;
6. admitted passage extent is present and typed;
7. proposal and required-field support remain inside the admitted passage extent;
8. authority claim identity matches the referenced Contract B claim;
9. authority atom identity matches the target atom;
10. proposal, assertion, operator, required-field, required-composition, and required-aperture receipts remain bound to the same authority subject;
11. operator domain/applicability/governance checks pass;
12. required field status/value/support checks pass;
13. required composition and aperture checks pass.

Execution failure remains orthogonal and yields `NO_ASSESSMENT`. Reader count, instrument count, and scalar confidence remain non-authoritative.

## Falsification history retained

The supported candidate is evidence-driven rather than a post-hoc clean result:

- RC8A falsified unbound receipt sufficiency;
- RC8C falsified missing admitted-source binding;
- RC8E falsified source-only binding via same-source atom transplant;
- RC8G falsified missing Contract B bundle/passage/span binding;
- RC8I falsified missing Contract B claim binding.

Each failure localized a distinct missing invariant and remains part of the evidence record.

## Non-claims and remaining debt

RC8J does not establish:

- canonical or collision-resistant atom-ID generation;
- that opaque IDs were generated honestly;
- proposition truth;
- source-text interpretation correctness;
- semantic extraction recoverability;
- cryptographic authenticity beyond Contract B's validated integrity regime;
- Contract C projection sufficiency;
- production integration or release readiness;
- independent recoverability by a fresh implementation.

The next costly-to-fake evidence is a fresh independent implementation/reproduction from a frozen specification in a clean context. This contaminated research thread should prepare that experiment but should not execute it and count the result as independent evidence.
