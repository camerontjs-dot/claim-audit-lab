# Shadow Reconciliation, Semantic-Operator Falsification, and Parallel Epistemic Artifact RC

## Classification and non-authorization

**Experiment class:** Research Infrastructure / epistemic-machinery successor experiment

This work is stacked on the completed Production Trace → Explicit Decision Model shadow evidence branch. It does not authorize replacement of the production CAL decision path, NLI-threshold tuning, Contract C changes, release/version changes, or a redesigned CAL architecture.

## Live authority frozen before implementation

- repository: `camerontjs-dot/claim-audit-lab`
- production `main` HEAD observed before implementation: `53f0885b111676794d1bd20e10b91aa58b07e9d4`
- machinery-audit PR: `#35`, observed open Draft, head `8c7cb29f6251f4f6566ab5fcc501cddc791e3539`
- predecessor production-trace shadow PR: `#36`, observed open Draft, head `b487d1dce4cc1a076e3705b0a7ef457e7d438814`
- successor branch base: exact PR #36 head `b487d1dce4cc1a076e3705b0a7ef457e7d438814`
- predecessor exact production base: `53f0885b111676794d1bd20e10b91aa58b07e9d4`
- predecessor frozen E2E corpus blob: `48a22cfab82ea0a2abd8d1c80d0da32a3dacd260`
- predecessor replay adapter blob: `cb26ba5a5ba9174dedbd686ea10dffcaae1a80db`
- predecessor explicit decision-model blob: `f0d9d3bc061d966ed9c8c16b3424b3dd5c3bb339`
- predecessor evidence-state blob: `e873772588e8c6ac27ced79559812afc8f5e9cdc`
- predecessor semantic-operator blob: `ae64056d2cbec4ed7fd615fe3f4fa6f2bebb177f`
- predecessor operator-replay blob: `11fedf036a208d94cd7516efdad4a17daa3374c8`
- Contract C exporter blob: `d6b32a44ef11109fe0ee91efa212d3904badf58c`

The predecessor primary scientific run was `33275184773` at execution head `2f8f9e1447ab1f52d2c43caafb4505e436142969`; its scientific job succeeded while a separate formatting check failed. The fully green repeat was `33275342888` at execution head `e864f3e12942bf3f47306ba895b8b965b638dae0`. Failed/bootstrap runs `33274969229` and `33275106892` remain part of the evidence record and will not be erased.

## Observed ambiguity to discriminate

### OBSERVED: e2e-08

The predecessor records a `0.9970703125` direct contradiction measurement for `p-1` on:

- claim: `The service meets 95 percent uptime and 40 percent capacity.`
- evidence: `The service meets 95 percent uptime and 70 percent capacity.`

The production rules allow an absent/abstained A4 negation probe to stand down and then permit the hard-contradiction rule to decide. The shadow operator adapter instead converts an abstained A4 probe into an `unknown` semantic-validity judgment that overrides the direct refutation contribution, causing explicit abstention.

### HYPOTHESIS H08

The shadow replay is conflating **operator inapplicability** with **an operator measurement of unknown validity**. A4 structural-negation authority is not a generic validator for every contradiction family. In particular, failure to produce a structural-negation probe over a numeric/quantity mismatch must not be interpreted as evidence that the refutation is semantically invalid, but it also must not manufacture semantic validity for that refutation.

### H08 falsifier

H08 is falsified if a receipt-bound A4 structural-negation contract can validly adjudicate all preregistered non-negation families below without semantic reinterpretation, and the same applicability rule distinguishes e2e-08 without special-casing its expected legacy verdict.

A result where A4 is inapplicable but no alternative operator validates the refutation leaves semantic validity `unknown`; it does **not** count as support for contradiction.

## Small discriminating operator cases

The research-only applicability matrix will separate these semantic families without changing model thresholds or using fixture verdicts as gold:

| Case | Claim/evidence phenomenon | Expected question, not expected verdict |
|---|---|---|
| `explicit_lexical_negation` | explicit polarity/structural negation | Can structural negation provide a canonical complementary proposition over the exact contribution? |
| `numeric_mismatch` | same proposition frame, differing scalar | Is a numeric relation operator required instead of structural negation? |
| `threshold_mismatch` | inequality/bound mismatch | Is interval/bound semantics required? |
| `quantity_mismatch` | differing units or quantities | Is unit/quantity comparability required? |
| `categorical_incompatibility` | mutually incompatible category values | Is category-exclusivity knowledge available or merely assumed? |
| `scope_mismatch` | evidence concerns a different site/subject/scope | Does scope eligibility preclude semantic contradiction authority? |

The exact e2e-08 receipt is included as a bound numeric/quantity counterexample, not as a gold label.

## e2e-09 interpretation hypothesis

### OBSERVED

The predecessor records for e2e-09:

- claim: `All submitted records pass schema validation.`
- evidence: `Most submitted entries satisfy the schema checks.`
- direct contradiction measurement: `0.673828125`
- frozen contradiction decision threshold: `0.70`
- legacy degree rule: `unsupported`
- explicit semantic validity: unmeasured/unknown
- explicit outcome: abstain

### HYPOTHESIS H09

Legacy `unsupported` is functioning here as a **degree-of-support reporting category over a sub-threshold adverse NLI measurement**, not as evidence that a semantically validated adverse proposition has been established.

### H09 falsifier

H09 is falsified if the frozen trace contains an independent, receipt-bound semantic-validity assessment that validates the adverse contribution, rather than only a terminal legacy degree/rule derived from the NLI score.

No missing assessment may be reconstructed from the legacy terminal verdict.

## Mutation/metamorphic invariants

The successor must test at least these invariants against the existing explicit machinery and research-only applicability projection:

1. numeric contradiction must not silently inherit lexical/structural-negation authority;
2. unknown semantic validity cannot decide;
3. removing a semantic-validity receipt cannot strengthen a conclusion;
4. replacing an applicable operator with an inapplicable operator cannot preserve decision authority;
5. adding irrelevant evidence cannot strengthen the decision basis;
6. ineligible evidence remains observable but cannot decide;
7. mixed semantically valid evidence remains mixed and non-resolved;
8. execution failure remains distinct from epistemic abstention.

Additional invariants may be added, but none may be weakened after observing results.

## Operator-authority rule under test

A semantic operator has decision authority only when all of the following are receipt-bound:

1. its applicability preconditions are satisfied for the evidence/claim phenomenon;
2. its exact evidence passage set matches the contribution;
3. it returns a terminal validity assessment (`valid` or `invalid`) within its declared semantic family;
4. eligibility and aperture requirements remain independently satisfied.

`inapplicable`, missing, or unresolved operator state is not contradiction, support, or semantic invalidity. It leaves the relevant semantic-validity assessment unknown unless another applicable operator supplies authority.

## Parallel epistemic artifact gate

A parallel non-authoritative research artifact may be implemented only if the falsifier stage demonstrates that the existing explicit machinery can preserve the following without inventing state from `AuditTrace.verdict`:

- raw, eligible, and semantically valid evidence states;
- exact contribution ledger and basis IDs;
- exact source passage IDs and direct model measurements;
- eligibility and semantic-operator receipts;
- aperture/completeness state, including unknown;
- execution/assessment state distinct from epistemic abstention;
- explicit decide/abstain basis;
- causal multiplicity where actually represented.

The artifact must be emitted from research-only code, alongside rather than instead of `AuditTrace`. It may not modify Contract C or become a second production decision path.

### Artifact falsifier

Artifact emission is not justified if any required field can only be populated by guessing, reading the legacy terminal verdict as semantic gold, or silently treating missing operator/aperture/execution state as known.

## Cross-corpus boundary

If, and only if, the artifact gate clears, this RC will preregister but not execute a larger heterogeneous shadow. That study must stratify by semantic phenomenon and record first divergence stage, compression, unknown creation/removal, support↔adverse transitions, operator coverage, unmeasured states, aperture failures, and execution failures. Threshold disagreements are observations, not tuning instructions.

## External NLI boundary

The pinned DeBERTa model and frozen thresholds remain unchanged. This RC first localizes disagreements to retrieval, NLI measurement, operator applicability, aggregation, policy, or missing state. Alternative NLI models/calibration are out of scope here.

## Protected surfaces

The successor workflow must fail if this branch changes any of these relative to the predecessor base unless a later explicit preregistration amendment names and justifies the change before execution:

- `src/claim_audit_lab/v1/runner.py`
- production retriever/entailer/aggregator/rules/trace models
- `src/claim_audit_lab/v1/decision_model.py`
- `src/claim_audit_lab/v1/evidence_state.py`
- `src/claim_audit_lab/v1/semantic_operators.py`
- `scripts/decision_model_replay.py`
- `scripts/evidence_state_eligibility_shadow.py`
- `scripts/evidence_state_operator_shadow.py`
- `src/claim_audit_lab/contracts/contract_c.py`
- `tests/v1/test_pipeline_e2e.py`
- threshold/config authority

The intended changes are new research-only files/workflow plus documentation/receipts. Predecessor failures and final frozen receipts remain immutable historical evidence.

## Terminal interpretation

The target is not 25-case parity. The experiment asks which distinctions are measured, which are operator-authorized, which are policy/reporting constructs, and which must remain unknown.
