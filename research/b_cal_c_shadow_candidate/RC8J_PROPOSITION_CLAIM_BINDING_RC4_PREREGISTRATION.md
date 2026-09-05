# RC8J Proposition-Content / Claim-Identity Binding RC4 Preregistration

## Classification

Draft Research Infrastructure. No production authorization.

This is a normal-context successor experiment stacked on frozen RC3. It does not modify RC1, RC1A, RC2, RC3, frozen RC8J, production CAL, Contracts B/C, Decision Engine policy, releases, or promotion state.

## Frozen lineage

- production main reference: `32275a239b68af383a56bca843e28cbc1e343976`
- frozen RC3 parent / PR #83 head: `3f13b162d4b0d0cc837c99b9ad830c4c47707270`
- frozen RC2 parent: `0c324a6a866f1bc0ce678c78d6502c6b314386c2`
- exact frozen RC8J commit: `8e75c6782bb95c3763d06230b9c5df2b6af44054`
- exact frozen RC8J implementation blob: `f55156e43e0c1b4a7868bc8339585b8892edda38`

## Observed parent seam

RC3 authenticates and binds the warranted atom plus the authority-relevant RC8J case projection. Its consumer checks that the warrant claim ID equals `case.raw_claim_id`, then passes an independently supplied `ComparisonProposition` into the categorical relation operator.

The proposition currently needs only to carry the same `claim_id`; its semantic fields (`family`, `lhs_entity`, `rhs_entity`, `comparison_direction`) are not authenticated by the portable warrant.

Therefore a same-`claim_id` proposition-content substitution could alter the proposition-relative relation while leaving the atom warrant valid.

## Research question

Can the relation-consumer boundary bind exact typed proposition content to a claim identity so that a caller cannot preserve `claim_id` while substituting proposition semantics and thereby change a scoreless categorical conclusion?

## Candidate hypothesis

A separate authenticated proposition-identity receipt can bind:

- exact `claim_id`; and
- a canonical SHA-256 digest of the exact typed proposition semantic payload

before the RC3 portable warrant is allowed to enter proposition-relative relation derivation.

For this bounded research candidate, the proposition-binding receipt uses HMAC-SHA-256 under a distinct out-of-band research key from the RC3 warrant key. This models an authenticated claim/proposition registry boundary without claiming production key architecture.

The candidate consumer must require **both**:

1. a valid RC3 portable warrant for the atom/case; and
2. a valid proposition-binding receipt for the exact proposition supplied to the relation operator.

No caller-supplied score, confidence, threshold, support/refutation channel, or relation hint is introduced.

## Exact proposition projection

For the implemented strict-comparison fragment, the proposition digest binds exactly:

- `family`
- `lhs_entity`
- `rhs_entity`
- `comparison_direction`

`claim_id` is bound separately in the authenticated receipt body.

This is exact typed-content identity, not semantic-equivalence canonicalization. For example `A > B` and `B < A` may be logically equivalent under the bounded relation table, but they are distinct exact proposition payloads unless a future authority explicitly defines an equivalence-normalization contract.

## Weak control

The frozen RC3 consumer without proposition-content binding is expected to accept this substitution:

1. atom: `A > B`, valid authenticated RC3 warrant;
2. proposition P1: `claim_id = X`, `A > B` -> expected `SUPPORTS -> supported`;
3. proposition P2: same `claim_id = X`, but `A < B` -> the same RC3 warrant is still expected to verify because the warranted atom/case is unchanged;
4. the categorical relation is expected to change to `REFUTES -> contradicted`.

This weak control must succeed for the experiment setup to be valid. If it does not, classify the setup `INCONCLUSIVE_CONTROL_PRECONDITION` rather than claiming the candidate solved a nonexistent seam.

## Primary falsifier

RC4 is `FALSIFIED_PROPOSITION_CLAIM_BINDING` if a proposition whose exact semantic payload differs from the authenticated proposition-binding receipt can nevertheless enter the combined RC4 consumer and produce a categorical relation or deciding conclusion under the same claim identity.

Also falsify if an attacker can recompute the proposition digest after substitution and retain/rewrite the old receipt without possessing the proposition-binding authentication key.

Do not patch the same RC4 candidate after a decisive falsification. Preserve the result and use a new successor revision if warranted.

## Preregistered controls

### Setup and weak seam

1. baseline `A > B` atom + bound `A > B` proposition -> `SUPPORTS -> supported`;
2. frozen RC3 claim-ID-only path accepts same-`claim_id` proposition direction substitution `A > B -> A < B` and changes to `REFUTES -> contradicted`.

### Exact proposition binding

3. stale proposition-binding receipt replay against same-`claim_id` direction mutation -> refuse, non-deciding;
4. attacker recomputes substituted proposition digest but keeps stale MAC -> refuse `MAC_MISMATCH`, non-deciding;
5. same-`claim_id` lhs entity substitution -> refuse, non-deciding;
6. same-`claim_id` rhs entity substitution -> refuse, non-deciding;
7. claim-ID substitution with otherwise identical semantic payload -> refuse, non-deciding;
8. swapped-inverse proposition representation (`B < A`) against receipt for `A > B` -> refuse as exact-content mismatch, even though the relation table treats the two as semantically equivalent;
9. separately issued authenticated receipt for swapped-inverse proposition -> accept and preserve the expected supported conclusion.

### Receipt authenticity / parser controls

10. wrong proposition verification key -> refuse;
11. unknown/tampered proposition `key_id` -> refuse;
12. MAC mutation -> refuse;
13. truncated MAC -> strict-schema refusal;
14. partial receipt -> refuse;
15. unknown receipt field -> refuse;
16. duplicate JSON key -> refuse;
17. pretty/reordered JSON transport -> verify after strict parse and canonicalization;
18. proposition object construction/key-order variation that yields the same typed model -> same digest and verifies.

### Composition and inherited safety

19. RC3 atom warrant remains required and independently verified;
20. stale/mutated atom with valid proposition receipt remains refused by RC3 warrant binding;
21. support/refute/irrelevant/unresolved/swapped/mixed scoreless categorical regressions remain unchanged;
22. caller `score`, `confidence`, `threshold`, `channel`, and `relation_hint` remain rejected;
23. production `src/` remains byte-unchanged relative to production main.

## Required interpretation

A pass would support only:

> Within the already-constructed typed strict-comparison fragment and the bounded HMAC research trust model, exact proposition content can be authenticated to a claim identity at the relation-consumer boundary, preventing same-claim semantic substitution from changing the categorical conclusion while preserving the RC3 atom-warrant transport path.

It would **not** establish:

- that `claim_id` issuance itself is trustworthy in production;
- semantic-equivalence normalization or canonical claim semantics;
- natural-language claim parsing or semantic extraction;
- proposition truth in the world;
- generic entailment;
- broader semantic families;
- production cryptographic key management;
- asymmetric signatures or public verification;
- Contract C projection;
- Decision Engine policy;
- production CAL architecture;
- release, merge, promotion, or independent clean-room recoverability.

## Stop rule

Stop with one of:

- `SUPPORTED_WITH_BOUNDS`
- `FALSIFIED_PROPOSITION_CLAIM_BINDING`
- `FALSIFIED_INHERITED_WARRANT_BINDING`
- `FALSIFIED_CATEGORICAL_REGRESSION`
- `INCONCLUSIVE_CONTROL_PRECONDITION`
- `BLOCKED`

This candidate remains Draft Research Infrastructure regardless of outcome.