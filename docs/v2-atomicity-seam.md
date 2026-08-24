# The atomicity seam: what CAL v2 needs from a decomposer

**Status:** design note, 2026-08-22. No implementation in CAL. Written so the
apparatus-contracts work has a fixed target to standardize against.

## The short version

**CAL already has this contract, and v2 does not use it.** `claim_audit_lab.v1.explicit_claims`
defines caller-declared atoms, an `all_of` operator, and a fixed parent
aggregation table. Its module docstring already states the division of labour the
upstream work assumes:

> This additive API does not decompose claim text. A caller supplies stable,
> provenance-bound atoms, CAL audits each atom through the existing atomic path,
> and this module derives a parent verdict from the declared operator.

So the deliverable is **not** a decomposer inside CAL. It is a seam: `run_v2`
currently takes `claim_text: str` and has no idea atoms exist.

## The finding that changes the shape of the fix

The v2 diagnostic attributed 11 of 98 PILOT-001 misses to v2's three-degree
vocabulary — `supported | contradicted | not_checkable` — being unable to express
the gold label `partially_supported`.

That is a seam problem, not a vocabulary problem. Feeding v2's three atomic
degrees into the existing aggregator produces the fourth degree at the parent:

| atom degrees (all from v2) | parent | rule |
|---|---|---|
| `supported`, `supported` | `supported` | `ECA-ALLOF-SUPPORTED` |
| `supported`, `not_checkable` | **`partially_supported`** | `ECA-ALLOF-PARTIAL` |
| `supported`, `contradicted` | `contradicted` | `ECA-ALLOF-CONTRADICTED` |
| `not_checkable`, `not_checkable` | `not_checkable` | `ECA-ALLOF-NOT-CHECKABLE` |

**v2's `Degree` should stay at three values.** Widening it would put a
compound-claim outcome into an atomic vocabulary, which is the category error
that produced the problem. `partially_supported` is a statement about a
conjunction; no single atom is ever partially supported.

`unsupported` is the one E2 degree v2 can never produce, because v2 collapses
"no evidence", "all ineligible" and "no signal" into `not_checkable` with a
distinguishing `null_reason`. That is a deliberate difference and the mapping
below keeps it visible rather than papering over it.

## What CAL v2 requires of an atom

Per atom, to audit it at all:

| field | why |
|---|---|
| `atom_id` | stable across runs; the trace keys on it |
| `claim_text` | one predicate, one subject — see the atomicity test below |
| `provenance` | `origin: operator_declared \| source_contract` plus an immutable reference. Already in `AtomProvenance`. |

Per parent, to aggregate:

| field | why |
|---|---|
| `operator` | `single \| all_of` today |
| `parent_claim_text` | for `single`, must equal the one atom's text (already validated) |

Per atom, **optional but load-bearing** — every one of these already exists as a
`run_v2` parameter, and each is the difference between a decided verdict and an
abstention:

| field | consumed by | what its absence costs |
|---|---|---|
| `declared_mode` | stage 0 | falls back to the lexicon, which misfires on `requirements` |
| `source_boundary` | R2, R6 | an undeclared boundary cannot settle a coverage claim either way |
| `claimed_material_is_a_named_gap` | R1 | the named-gap route is unreachable |
| `trust_levels` + `trust_policy` | Q1 | see below |
| `claim_scope` / `passage_scope` | Q2 | scope isolation does not run |

## The atomicity test the decomposer has to enforce

An atom is auditable when it asserts **one predicate of one subject under one
scope and one boundary condition** — the blueprint's `ℋ = Φ(X, Ω, τ)`. In
practice the decomposer should split on:

1. **Coordinated predicates.** "The SOP specifies a 24-hour hold *and* names a
   deviation owner" — two obligations, two atoms.
2. **Coordinated subjects.** "Chambers CH-04 and CH-07 recorded no excursions" —
   two scopes, two atoms. This one matters most: a single atom spanning two
   scopes defeats Q2 entirely, because the claim's scope anchor set intersects
   both passages and disjointness can never be concluded.
3. **Mixed modality.** "The packet does not establish a timeframe, and the
   timeframe used was 30 days" — one coverage claim and one ordinary claim
   sharing a sentence. These need different obligations and cannot share a
   `ClaimFrame`.
4. **Mixed dimensions in one bound.** "Held at 2–8 °C for at least 6 months" —
   two measurands. The interval operator abstains on multiple bounds in one
   dimension; two dimensions in one atom is the case it cannot even detect.

What it should **not** split on: relative clauses, appositives, or any
restrictive modifier. "The retain samples, which are stored in CH-04, are held
six months" is one claim with a scope anchor, not two claims.

## What CAL should do with a compound claim it is handed anyway

Refuse it, visibly. The right shape is a stage-0 outcome, not a rule:

- add `not_atomic` to `NullReason`
- `build_claim_frame` records the detected coordination and its span
- `run_v2` terminates at `0-frame`, as it already does for `out_of_form`

That is strictly better than today, where a compound claim is audited as though
it were atomic and lands in `no_signal` — indistinguishable in the trace from a
genuine absence of evidence. **A claim that could not be tested must not look
like a claim that was tested and found wanting.** Same principle as the Q1 fix.

CAL should not attempt the split itself even as a fallback. A parse-based
decomposition that is wrong produces two atoms that are each individually
auditable and jointly not the claim, and nothing downstream can detect that.

## Proposed seam

One function, no change to `run_v2`:

```python
def run_v2_explicit(
    request: ExplicitClaimRequest,      # existing type: operator + atoms
    per_atom_evidence: dict[str, AtomEvidence],
    *,
    trust_policy: TrustPolicy = "optional",
) -> tuple[ParentAggregationTrace, dict[str, V2Verdict]]:
    ...
```

- audits each atom with `run_v2` unchanged
- maps each `V2Verdict.degree` to a `Verdict` for aggregation
- calls the existing `aggregate_explicit_claim_verdicts`
- returns the parent trace **and** every atom verdict, because a
  `partially_supported` parent is useless to a reviewer without knowing which
  conjunct failed

The degree mapping is total and lossy in exactly one direction, which the trace
should carry:

| v2 `Degree` + `null_reason` | E2 `SupportVerdict` |
|---|---|
| `supported` | `supported` |
| `contradicted` | `contradicted` |
| `not_checkable` (any null reason) | `not_checkable` |

v2 never emits `unsupported` or `partially_supported` at the atom level. Both
remain reachable at the parent.

## Open question for the contract owners

`all_of` is the only compound operator CAL implements. Real drafts also carry
disjunctions ("either a deviation was raised or the batch was rejected") and
conditionals ("if the excursion exceeded 8 °C, a deviation was required").

`any_of` is a small addition to the E2 table. **Conditionals are not** — the
antecedent is a scope restriction on the consequent, not a conjunct, and
aggregating them with a truth table gives the wrong answer whenever the
antecedent is false. If conditional claims are in scope for the apparatus work,
that needs its own decision before either side builds to it.

## Related

- `src/claim_audit_lab/v1/explicit_claims.py` — the existing contract
- `tests/v1/test_explicit_claims.py` — its behaviour
- `scripts/test_abstention_and_decomposition.py` — the earlier probe
