# RC8J Scalar-Free Categorical Relation Participation — Preregistration

Status: **Draft Research Infrastructure / stacked successor to PR #78**.

This experiment does not modify RC8J, production CAL, Contract A/B/C, Decision Engine policy, release state, or the frozen CAL v1 decision model.

## Scientific question

After RC8J establishes authority for an already-constructed evidence atom, can a scalar-free proposition-decision lane behave coherently **provided** a separate typed proposition-relative relation is already established as `support | refutation`?

The experiment does not claim that CAL can yet establish that relation from real proposition text. It isolates the downstream participation rule.

## Frozen parent evidence

PR #78 demonstrated:

- exact RC8J `WARRANTED` with no scalar score -> existing semantic-operator path abstains `contribution_score_unmeasured`;
- changing only caller-supplied scalar `0.69 -> 0.70` changes abstention -> `supported` under the fixed 0.70 threshold;
- changing the separately stipulated channel at the same warrant/threshold changes `supported -> contradicted`;
- mixed valid support/refutation remains `mixed_valid_evidence`;
- RC8J `UNRESOLVED` is refused as valid deciding evidence.

Therefore RC8J warrant is neither decision strength nor proposition polarity.

## Contract A boundary

Contract A 2.0.0 supplies an integrity-bound authoritative proposition ID/text/hash and optional declared `all_of` lineage, but explicitly does **not** establish proposition truth, support/refutation, or CAL semantic correctness.

No Contract A widening is proposed.

## Candidate input surface

Each research contribution carries:

- `contribution_id`;
- exact RC8J terminal authority result (`WARRANTED | REJECTED | UNRESOLVED | NO_ASSESSMENT` + typed reason);
- a separately typed proposition-relative relation state:
  - `established/support`;
  - `established/refutation`;
  - `unresolved`;
- admitted/eligible state;
- diagnostic-only metadata including arbitrary scalar score, reader count, and instrument count.

The proposition-relative relation is a **fixture stipulation** in this experiment. It is not inferred from RC8J, Contract A, or raw language.

## Scalar-free candidate rule

The candidate may decide only after these gates:

1. proposition is in scope;
2. support and refutation aperture are both complete;
3. all admitted/eligible contributions that could affect the proposition have terminal authority rather than `UNRESOLVED/NO_ASSESSMENT`;
4. every deciding contribution is exactly RC8J `WARRANTED`;
5. its proposition-relative relation is exactly established support or refutation.

Then:

- warranted support only -> `supported`;
- warranted refutation only -> `contradicted`;
- warranted support + warranted refutation -> abstain `mixed_warranted_relations`;
- no warranted established relation -> abstain;
- any unresolved relevant authority or unresolved relation -> abstain with typed reason.

No scalar score is read by the decision rule.

## Falsifiers / controls

### C1 — warranted established support
Expected: `supported`.

### C2 — warranted established refutation
Expected: `contradicted`.

### C3 — mixed warranted relations
One support and one refutation, both warranted and relation-established.
Expected: abstain `mixed_warranted_relations`.

### C4 — proposition relation unresolved
RC8J remains warranted, but relation state is unresolved.
Expected: abstain `proposition_relation_unresolved`.

### C5 — RC8J authority unresolved
Relation is fixture-established support, authority is the frozen RC8J unresolved segment-binding mutation.
Expected: abstain `semantic_authority_unresolved`.

### C6 — rejected competing observation
One warranted established support plus one RC8J-rejected refutation observation.
Expected: supported; explicit rejected authority does not become competing epistemic evidence.

### C7 — unresolved competing observation
One warranted established support plus one RC8J-unresolved refutation observation.
Expected: abstain; unknown relevant authority cannot be silently discarded.

### C8 — aperture unknown
Warranted established support with refutation aperture unknown.
Expected: abstain `aperture_unresolved`.

### C9 — arbitrary diagnostic score mutation
Repeat C1 with diagnostic scalar `0.01`, `0.70`, and `0.99`.
Expected: identical supported result in all cases.

### C10 — reader/instrument bank growth
Repeat C1 with counts 1 and 32.
Expected: identical supported result.

### C11 — duplicate same-polarity warranted contribution
Add a second warranted established support contribution.
Expected: supported; bank growth does not strengthen into a different state.

## Hard interpretation rule

If all controls pass, the supported statement is only:

`SCALAR_FREE_CATEGORICAL_PARTICIPATION_IS_COHERENT_GIVEN_SEPARATELY_ESTABLISHED_PROPOSITION_RELATION; REAL_TEXT_REMAINS_BLOCKED_ON_PROPOSITION_RELATION_AUTHORITY`

This would make the categorical lane the smaller next research architecture than inventing a new scalar-strength authority merely to reuse an existing threshold path.

It would **not** establish how the proposition-relative relation is created or warranted.

## Ownership boundary

If the scalar-free lane passes, the remaining real-text blocker is authority for the proposition-side interpretation/relation itself:

`authoritative proposition text -> typed proposition meaning -> relation(evidence atom, proposition) -> support | refutation | unresolved`

That is an authority-bearing semantic interpretation problem. This integration thread must not silently define its real-text verification semantics. The separately owned semantic-authority programme should be treated as the default owner unless the operator explicitly changes ownership.

## Non-claims

This experiment does not establish:

- real-text proposition parsing;
- proposition-atom canonicalization;
- support/refutation relation authority;
- completeness of logical complement rules;
- a production CAL decision policy;
- Contract C projection/promotion;
- Decision Engine policy;
- release readiness.