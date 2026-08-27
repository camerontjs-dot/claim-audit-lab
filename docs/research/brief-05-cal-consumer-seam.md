# Research Brief 05 — CAL Contract-B consumer seam

**Status:** preregistered consumer-side seam experiment  
**Branch:** `research/obligation-composition-shadow`  
**Canonical cross-repo discussion:** `camerontjs-dot/apparatus-contracts#1`  
**CAL seam issue:** `camerontjs-dot/claim-audit-lab#3`  
**Production impact:** none

## Question

What may CAL legitimately inherit from a verified Contract-B bundle, and what must CAL derive itself under an explicit, receipt-bound audit policy?

This rung treats Contract B as an immutable evidence/preparation artifact. It does not change Evidence Bundler, Apparatus Contracts, the production CAL rules, the production C-B adapter, or C-B writeback.

## Boundary

The consumer-side seam has three epistemic categories:

1. **Contract facts** — source/passages, hashes, dates, provenance, source type/trust vocabulary, EB nomination/admission state.
2. **CAL measurements** — claim/passage semantic relation measured independently of EB's nomination lane.
3. **CAL judgments** — proposition-specific eligibility, validity, temporal applicability, authority applicability, aperture/completeness, and final decision participation.

The invariant under test is:

> Upstream metadata may inform a CAL judgment, but it may not silently become that judgment.

## Existing implementation observations

### Correct v1 behavior

`v1/intake.py` gives each auditable claim the full frozen C-B passage set. It explicitly refuses to use C-B `evidence_passages` / `counterevidence_passages` as pre-filters. This is the desired future seam.

### Legacy lane coupling

`contracts/adapter.py` + `evidence_matching.match_scoped_evidence()` convert C-B support/counter containers into separate CAL support/counter search scopes. This is retained as legacy behavior but should not define the v1 seam if EB roles are only nominations.

### Trust-level policy coupling

Contract B defines `trust_level = primary | secondary | background`, but the locked contract does not define non-primary sources as proposition-ineligible.

Current v1 intake copies `trust_level` into passage metadata. Current Decision-H P1 then suppresses an adverse degree when the contributing passage has a present trust tier other than `primary`.

That may be a CAL policy choice, but it is not a lossless contract adaptation. Rung 05 separates semantic measurement from that policy effect.

### Legacy reliability mapping

The legacy adapter maps `primary → high`, `secondary → medium`, and `background → low` into CAL `SourceReliability`. Rung 05 treats this as observed semantic promotion, not a contract fact.

## Preregistered hypotheses

### H05-1 — Nomination-lane invariance

For v1, moving the same admitted passage between C-B support and counterevidence containers must not change the normalized `AuditRequest.passages` set.

**Falsifier:** the v1 passage set or passage content changes solely because the EB nomination lane changes.

### H05-2 — Semantic measurement independence from trust tier

With claim text, passage text, retrieval admission, and entailer response frozen, changing only C-B-style trust metadata must not change the recorded entailment result or aggregate semantic signal.

**Falsifier:** the semantic measurement changes before CAL's policy/rules layer sees the source metadata.

### H05-3 — Current P1 is a CAL policy dependency

The current production v1 rules are expected to change an adverse final verdict when only trust metadata changes from `primary` to `secondary`, because P1 interprets non-primary as adverse-ineligible.

If reproduced, classify the difference as a CAL policy effect, not as changed evidence semantics.

**Falsifier:** the current verdict is invariant to the trust-only transformation or the measurement itself changes.

### H05-4 — Explicit assessment can replace implicit metadata equivalence in the shadow

The additive shadow decision model should permit the same measured refutation to be explicitly assessed as `eligible`, `ineligible`, or `unknown`, each with a receipt. The model must not need a trust-level field to make that assessment.

Expected outcomes:

- explicit eligible + valid refutation → `contradicted`;
- explicit ineligible refutation → abstain because no eligible contribution remains;
- explicit unknown eligibility → `eligibility_unknown`.

### H05-5 — Missing context remains missing

No Rung-05 helper may manufacture proposition-specific eligibility, reliability, authority, temporal applicability, or semantic validity from `primary/secondary/background` alone.

## Controlled variables

Frozen throughout the trust-tier metamorphic test:

- claim text;
- passage text and identity;
- retrieval score;
- entailer response;
- aggregation algorithm;
- CAL rules/config;
- all feature values.

Only passage `source_meta["trust_level"]` changes.

## Acceptance gates

1. v1 normalized passages are nomination-lane invariant.
2. semantic entailment trace is trust-tier invariant.
3. any trust-only verdict delta is attributable to a named CAL rule, expected `P1_eligibility_suppressed`.
4. shadow eligibility states are explicit receipt-bound inputs, not derived from trust labels.
5. `unknown` remains an abstention.
6. no production file or Contract-B schema changes in this rung.
7. full public CI remains green.

## Interpretation rule

A green result does not prove that `secondary` evidence should be eligible. It proves a cleaner ownership statement:

```text
Contract fact: trust_level=secondary
        ↓
explicit CAL policy / assessment
        ↓
eligible | ineligible | unknown
```

The policy itself requires separate validation against real audit use cases.
