# Research Results 03 — Relation preservation, public traces, and Annex 22 downstream vectors

**Branch:** `research/obligation-composition-shadow`  
**PR:** #1, draft  
**Original experimental base:** `376a62b57b32ddd2e937be408e877ad91e6b1367`  
**Annex 22 extension base:** `ea06428cdce920917ddb6ae7820316c8b1284baa`  
**Production impact:** none  
**Interpretation status:** shadow architecture supported for further downstream testing; no production promotion implied

## Executive result

The tested downstream hypothesis survived all current public gates.

CAL's existing contribution-ledger shadow can preserve every admitted evidence relation while deriving narrower non-destructive views for eligibility, semantic validity, aperture, and resolution. The experiment did not require a change to the production engine, production rules, thresholds, CLI, schema, or verdict path.

The strongest result remains mechanistic: the released max-winner aggregation can change its selected label when only the numerical winner or exact-tie ordering changes, while a relation-preserving representation retains both support and refutation as `mixed`. The Annex 22 extension adds a separate result: evidence can become non-deciding for a particular proposition, authority state, lifecycle state, or supplier-control state without disappearing from the audit record.

This result does **not** validate automatic claim decomposition, obligation generation, retrieval quality, authority classification, or provenance generation. Those are upstream of the boundary tested here.

## Run chronology

| Rung | Commit / run | Public pytest | Quality gates | Interpretation |
|---|---|---:|---|---|
| Original preregistered shadow | first experiment | 970 passed, 5 skipped, 48 deselected | green | controlled relation/composition hypotheses reproduced |
| Public trace compatibility | run #7, `ea06428c` | 973 passed, 5 skipped, 48 deselected | Ruff, format, mypy green | all committed trace fixtures compatible with additive evidence-state projection |
| Annex 22 downstream preservation | run #10, `43ee87ca` | 982 passed, 5 skipped, 48 deselected | Ruff, format, mypy green | nine new preservation/regulatory stress vectors reproduced |

### Recorded apparatus deviation

The first public-trace CI attempt passed all 973 pytest cases but failed Ruff because one new assertion line was 101 characters against the repository's 100-character limit. The defect was formatting-only. It was corrected in a separate commit (`ea06428c`) rather than rewriting the failed run, and the full suite then passed.

This deviation is retained because experiment apparatus failures are part of the audit history.

## Rung 1 — Relation preservation versus max-winner aggregation

### H1 — Premature winner selection loses decision-relevant information

**Result: supported for the constructed mechanism test.**

- Changing only which of a valid support/refutation pair has the numerically larger score can flip the released max-winner label.
- Reversing passage order under an exact cross-label score tie can also change the released winner.
- Under both transformations, the relation-preserving shadow remains `mixed` and does not manufacture a terminal support/refutation verdict.
- Easy support-only and refutation-only controls continue to resolve.

**Conclusion:** a single winning signal is not a safe universal representation of the admitted evidence state.

### H2 — Eligibility and semantic validity precede resolution

**Result: supported for the constructed mechanism test.**

- Explicitly ineligible evidence does not decide, even when its NLI score is higher.
- Evidence explicitly invalid for the proposition does not decide.
- `unknown` eligibility or semantic validity causes an explicit abstention rather than silent fallback.
- The underlying contribution remains present in the full input ledger.

### H3 — Evidence aperture is a decision dependency

**Result: supported for the constructed mechanism test.**

Strong local support does not yield a terminal result when the relevant support/refutation aperture is explicitly incomplete or unknown.

### H4 — Declared obligation composition prevents semantic averaging

**Result: supported only for caller-declared structure.**

For `all_of` composition, supported components cannot convert a required unresolved or unsupported dependency into full support, and a contradicted required dependency blocks a supported parent.

This is not evidence that CAL should infer or generate the obligation structure. The current downstream test boundary assumes such structure is supplied upstream.

## Rung 2 — Public trace compatibility

All committed CAL trace fixtures were replayed through the two-channel evidence-state projection.

Acceptance properties passed:

- projection is deterministic;
- admitted passage identity is preserved;
- support/refutation candidates remain subsets of admitted passages;
- original frozen production traces are not mutated by projection.

**Result:** the additive representation is compatible with CAL's committed trace history. This is a compatibility result, not a real-world accuracy result.

## Rung 3 — Downstream preservation invariant

The Annex 22 extension hardened a previously implicit rule into an explicit acceptance criterion:

> Filtering changes decision participation, never the historical evidence record.

### G01 — Filtered views never erase the ledger

**Passed.** A single input containing valid support, higher-scoring ineligible refutation, semantically invalid refutation, and unresolved-validity refutation retained all four contributions in `EvidenceDecisionTrace.inputs`.

Derived views behaved independently:

- `raw` retained all measured relations;
- `eligible` omitted only the explicitly ineligible contribution from its deciding view;
- `valid` contained only semantically valid contributions;
- the unresolved-validity contribution remained recorded and blocked terminal resolution.

### G02 — Later classification does not rewrite history

**Passed.** A supplier contribution initially classified `eligibility=unknown` produced an abstention. A later trace reclassified the same contribution as ineligible and allowed the remaining support to resolve.

The original trace retained `unknown`; the new trace retained `ineligible`; both retained the supplier contribution in their raw record.

**Conclusion:** the appropriate architecture is append-only in effect. Reassessment creates a new decision trace, not a rewrite of the previous one.

## Annex 22 stress vectors

The six EMA Annex 22 workshop areas were used as test-shape generators, not as CAL rules.

### A22-01 — Regulatory pathway / authority status

**Passed.** Evidence that regulators are exploring a future risk-based pathway can remain in the ledger without being allowed to masquerade as current permission for a proposition governed by the restrictive draft state.

The key property is preservation plus proposition/authority-specific validity, not deletion of the lower-authority item.

### A22-02 — Reliability, guardrails, and incidents

**Passed.** A successful guardrail-validation record and a later guardrail-incident record remain simultaneously valid evidence. The state remains `mixed` regardless of which score is larger.

### A22-03 — Human oversight

**Passed.** Strong evidence that a technical guardrail works does not prove that required human oversight occurred. The guardrail evidence remains recorded but is non-deciding for the human-oversight proposition.

### A22-04 — Validation and lifecycle change

**Passed.** Pre-update validation does not prove post-update behavior when a lifecycle/temporal assessment says it no longer applies. The earlier validation remains in the record; a post-update failure remains independently usable.

### A22-05 — Strategic limits / unresolved adverse aperture

**Passed.** Very strong local positive evidence remains recorded, but an unresolved relevant adverse-evidence aperture prevents a terminal result.

### A22-06 — Outsourcing / supplier controls

**Passed.** A supplier attestation with unresolved eligibility remains visible and blocks resolution instead of being silently ignored or accepted.

## FDA enforcement vector

### FDA-01 — Synthesis is not authority

**Passed.** An AI-generated GMP procedure may be retained as an artifact but cannot, solely by existing, prove that required quality-unit human review occurred. A separate inspection record documenting the review gap remains independently deciding evidence for that proposition.

## Cross-cutting finding

The useful downstream state is not:

```text
all evidence -> choose winner -> forget the rest -> verdict
```

The experiments support:

```text
immutable admitted evidence ledger
              |
              +-> measured relation view
              +-> eligibility view
              +-> proposition-specific validity view
              +-> aperture / completeness state
              |
              `-> decision basis (subset of retained ledger)
```

A contribution may therefore be:

- historically admitted;
- contradictory to another contribution;
- ineligible for one decision policy;
- invalid for one proposition;
- temporally stale for the current system state;
- unresolved pending supplier/authority information;
- non-deciding in the current trace;

without being erased.

## What the regulated-AI radar contributed

The radar supplied realistic evidence classes and failure shapes rather than a new decision policy. In particular:

- Annex 22 supplied six downstream stress families: authority/permissibility, reliability/incidents, human oversight, lifecycle change, strategic limits, and supplier/cybersecurity controls.
- The FDA Purolea enforcement signal supplied the `synthesis is not authority` vector.
- NIST/EN 18286/radar findings reinforce a broader future interface need for context-of-use, authority/status, provenance, lifecycle, evaluation, and human-authority metadata.

Those fields should be tested as typed inputs or upstream contract surfaces before CAL is asked to infer them itself.

## Main-branch movement during the experiment

`main` advanced during this test sequence to `fbe27056d02bb08d9aa332203ce38312673a0aa0` through a documentation/social-preview change. GitHub Actions run #10 exercised PR #1 as a merge candidate against that newer `main` and remained fully green.

No experimental result depends on the social-preview change.

## Decision

### Promote for further research

Promote the following as downstream design constraints for the next experimental rung:

1. full evidence ledger preservation;
2. independent support/refutation relations;
3. non-destructive eligibility and semantic-validity views;
4. explicit unknown/incomplete states;
5. receipt-bound decision basis as a subset of the retained ledger;
6. new traces for later reassessment rather than mutation of prior traces;
7. lifecycle/authority/proposition scope as explicit decision dependencies where supplied.

### Do not promote yet

Do not yet promote:

- automatic claim decomposition;
- automatic verification-obligation generation;
- automatic authority classification;
- obligation-specific retrieval redesign;
- generalized temporal/causal operators;
- production replacement of the released decision path.

The next experiment should remain downstream of the apparatus contract and test richer supplied evidence states on realistic audit bundles, especially cases containing simultaneous positive evidence, counterevidence, lifecycle changes, supplier assertions, and explicit unknowns.
