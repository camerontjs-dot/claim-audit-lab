# CAL RC0B — Span-Anchor Integration Regression Preregistration

## Class

Draft Research Infrastructure successor to RC0A and frozen CAL Profile RC0. No production authorization.

## Frozen lineage

- CAL production main: `32275a239b68af383a56bca843e28cbc1e343976`
- RC0 terminal head: `8c52a00b93c7c33c159a484c47944faf9d97f7f1`
- RC0 runtime blob: `b36dacf39d158601368b89df8fa66431ce1b4a07`
- RC0 smoke runner blob: `a53d427095876e18fa65a67993f259f8672f1650`
- RC0A frozen apparatus head: `9baa981d9e5209c08911b992effbce5c59604884`
- RC0A candidate blob: `7dd0b1d0077682d121aaa386067531cca3b742d8`
- RC0A decisive run: `34132430044`
- RC0A artifact: `10022610872`
- RC0A artifact digest: `sha256:4f8c55a212876ad47c30211c980d8104e9caab82b44710edd3b238d2bffa05c4`
- RC0A disposition: `SUPPORTED_WITH_BOUNDS`
- exact RC7F-B1: `0ecdedc5cea970485a635508255f3670ab231c33` / blob `33820f55e2a87c4de6336fca6b5e5b93a2bccde3`
- exact RC8J: `8e75c6782bb95c3763d06230b9c5df2b6af44054` / blob `f55156e43e0c1b4a7868bc8339585b8892edda38`
- Contract B 1.2 authority: `c314e53bd91c0736aa4370a364673b069aceb43e`
- Contract C 1.0 authority: `5fe55f9ed5d0ee9f026ca1b077e9d70ce0487ea1`

## Question

Does the exact frozen RC0 vertical remain fail-closed when only its first two entity-surface span lookups are replaced by the frozen RC0A unique lexical resolver?

The integration adapter is deliberately surgical: it does not modify the frozen RC0 runtime. It intercepts only the LHS and RHS span lookups inside the exact frozen `complete_strict_comparison_atom` call and delegates all later measure/quantity/unit span lookups to the frozen parent helper.

## Candidate vertical

exact Contract B validation
→ exact RC7F-B1 comparison measurement
→ frozen RC0 atom completion with only LHS/RHS span lookup supplied by frozen RC0A
→ exact frozen RC8J
→ exact atom-bound warrant
→ exact proposition binding
→ frozen categorical relation
→ frozen scoreless composition
→ frozen Contract C projection
→ exact Contract C validation.

No scalar/confidence/count/rank input gains terminal influence.

## Preregistered integration cases

The controlled cohort covers:

1. original `Women` / `Men` overlap as refutation;
2. the same source as swapped-inverse support;
3. the same source as an irrelevant foreign proposition;
4. `Russia` / `US` embedded-substring collision;
5. `Model 20` / `Model 2` digit-prefix collision;
6. `Plan AB` / `Plan A` letter-prefix collision;
7. case-insensitive entity surface recovery;
8. `Woman` / `Man` overlap;
9. `New York` / `York` lexical-component ambiguity, which must remain unresolved;
10. `Beta Group` / `Group` lexical-component ambiguity, which must remain unresolved.

Every case must pass exact Contract B and exact Contract C validation. Deciding cases must match the preregistered categorical relation and verdict. Ambiguous component cases must abstain and project only `not_checkable`.

## Weak role-misattachment control

A deliberately weak adapter uses the **first** eligible lexical span for each entity rather than requiring uniqueness.

On `New York trailed York by 4 units.` it is expected to bind the RHS `York` field to the `York` token inside the LHS `New York` span. The control is discriminating if:

- the wrong RHS span overlaps the LHS span;
- exact frozen RC8J nevertheless returns `WARRANTED / ALL_REQUIRED_WARRANT_ESTABLISHED` because RC8J does not parse source text or choose mention roles;
- the weak path reaches a deciding categorical conclusion; and
- the RC0A candidate path refuses the same ambiguous entity anchoring before RC8J.

This control tests whether exact occurrence selection is a real upstream safety responsibility rather than something downstream authority automatically repairs.

## Receipt-binding control

For a valid candidate-generated atom, mutate the consumed field-support span while replaying the stale authenticated atom warrant. Verification must fail closed because the warrant subject digest binds exact field spans.

## Hard falsifiers

Stop RC0B if any of the following occurs:

- RC0A causes an unsafe SUPPORTS/REFUTES result;
- an ambiguous component case is silently resolved by the candidate;
- a stale warrant verifies after a bound span mutation;
- Contract C strengthens an internal abstention;
- exact B or C validation fails;
- frozen RC0, RC0A, RC7F-B1, or RC8J identity drifts;
- production `src/**` changes are required.

## Success condition

`SUPPORTED_WITH_BOUNDS` requires all controlled candidate cases to match exactly, zero unsafe candidate outcomes, exact B/C validation, a valid weak role-misattachment control, and refusal of the stale-span warrant replay.

Success authorizes only a fresh RC0C naturalistic span-transfer smoke. It does not authorize the 24–32 claim audit or production promotion by itself.
