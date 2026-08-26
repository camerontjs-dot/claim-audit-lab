# Research Brief 03A — Downstream preservation and Annex 22 stress vectors

**Status:** preregistered extension to Research Brief 03  
**Branch:** `research/obligation-composition-shadow`  
**Green baseline:** `ea06428cdce920917ddb6ae7820316c8b1284baa`  
**Production impact:** none

## Boundary

This extension begins **after the apparatus handoff**.

Claim discovery, claim decomposition, obligation authoring, source collection, provenance
capture, and any upstream authority/status classification are outside the subject under
test. The test harness receives already-prepared obligation/evidence relations and asks
only what CAL may defensibly do with them.

This matches the locked apparatus-contract framing of Contract B as a
"measurement-ready" Evidence Builder → Claim Audit Lab artifact. The contract also
requires preservation of lineage and documents disagreements rather than deleting them.

The test subject is therefore:

> Given an admitted, provenance-addressable evidence ledger for one supplied obligation,
> can CAL preserve every observation while producing narrower non-destructive views for
> eligibility, semantic validity, aperture, and resolution?

## Preservation invariant

The downstream architecture is acceptable only if all five statements remain true:

1. **Admission is historical.** Once an evidence contribution enters the CAL-facing
   ledger, later disagreement does not erase the fact that it was admitted.
2. **Filtering creates views, not replacements.** `raw`, `eligible`, and `valid` are
   derived decision views over one retained ledger.
3. **Decision basis is a subset, not the record.** A contribution may be non-deciding
   while remaining inspectable with its passage identity, score, assessment, and receipt.
4. **Unknown remains unknown.** An unresolved contribution blocks or qualifies a decision
   where required; it is not silently treated as false, invalid, or absent.
5. **Reassessment is append-only in effect.** A later eligibility/validity determination
   produces a new trace. The earlier trace remains reconstructable.

This is intentionally stricter than "keep the winning evidence." Contradicted,
ineligible, invalid-for-this-proposition, and unresolved evidence all remain part of the
audit record.

## Why Annex 22 is a useful stress-test source

The July 2025 draft of EU GMP Annex 22 and EMA's 30 June–1 July 2026 expert workshop
provide unusually concrete evidence-decision failure shapes.

The draft is not final guidance. In its consultation form it applies a restrictive scope
to critical GMP use of dynamic, probabilistic, GenAI, and LLM systems. EMA's 2026
workshop explicitly re-opened the design question and asked experts for evidence on a
possible risk-based pathway. The workshop does **not** itself grant permission.

Official sources:

- European Commission consultation and draft Annex 22:
  https://health.ec.europa.eu/consultations/stakeholders-consultation-eudralex-volume-4-good-manufacturing-practice-guidelines-chapter-4-annex_en
- EMA Annex 22 expert workshop:
  https://www.ema.europa.eu/en/events/good-manufacturing-practice-multistakeholder-workshop-expert-contributions-artificial-intelligence-guidance-development-annex-22

The draft also contains three patterns directly relevant to CAL:

- test documentation and deviations should be retained;
- low-confidence model outputs may need an `undecided` state rather than a forced
  prediction;
- model/process changes require documented evaluation and possible retesting.

Those are useful analogues for CAL's own preservation, abstention, and lifecycle logic.

## Annex 22 vector matrix

| ID | Annex 22 topic | Downstream obligation shape | Expected CAL behavior |
|---|---|---|---|
| A22-01 | Regulatory pathway | draft restriction + later workshop interest | preserve both; workshop interest cannot masquerade as current permission |
| A22-02 | Reliability / incidents | successful guardrail validation + later failure record | preserve both as valid mixed evidence; do not select a winner |
| A22-03 | Human oversight | strong guardrail evidence offered for a human-oversight proposition | retain it but reject it as semantically insufficient for that proposition |
| A22-04 | Validation / lifecycle | pre-update validation + post-update failure | retain both; pre-update support cannot launder the changed system |
| A22-05 | Strategic limits | very strong local support + unresolved adverse aperture | retain support but abstain while the relevant evidence aperture is unknown |
| A22-06 | Cybersecurity / outsourcing | supplier assertion with unresolved control/qualification status | retain the assertion and block resolution while eligibility is unknown |

### Additional enforcement vector

`FDA-01` is drawn from the regulated-AI radar's Purolea warning-letter signal.

The vector asks whether an AI-generated GMP procedure can serve as evidence that the
required human quality-unit review occurred. It cannot. The generated artifact is still
retained, but it is semantically invalid for the human-review proposition; an inspection
record documenting the review gap remains independently usable.

This tests the radar's cross-cutting principle:

> synthesis is not authority.

## Generic preservation controls

Two non-domain-specific controls precede the Annex 22 vectors.

### G01 — filtered views never erase the ledger

One claim receives:

- valid support;
- higher-scoring ineligible refutation;
- eligible but semantically invalid refutation;
- eligible refutation with unresolved semantic validity.

Expected result:

- all four contributions remain in `trace.inputs.contributions`;
- `raw` contains all four measured relations;
- `eligible` excludes only the explicitly ineligible contribution;
- `valid` contains only the valid contribution;
- the unresolved validity still blocks the terminal decision.

### G02 — later classification does not rewrite history

A supplier refutation begins with `eligibility=unknown`. A later assessment classifies it
as ineligible.

Expected result:

- the original trace still records `unknown`;
- a new trace records `ineligible`;
- both traces still preserve the supplier contribution in the raw ledger;
- only the later decision view excludes it.

This is the concrete test of "keep it now; decide what it means later."

## Controlled variables

This extension does **not** test or change:

- claim decomposition;
- obligation generation;
- retrieval;
- Evidence Builder selection;
- provenance generation;
- NLI model outputs;
- production thresholds;
- production rules;
- production verdicts;
- the apparatus-contract schema.

Authority/status and proposition-specific validity are represented as already-resolved
test inputs. Whether those assessments should ultimately be supplied by Apparatus
Contracts, CAL operators, or another typed layer is a separate interface question.

## Acceptance gates

The extension passes only if:

1. every rejected or unresolved contribution remains in the immutable input ledger;
2. filtered state snapshots contain only the expected subsets without altering the input;
3. re-evaluation leaves the previous trace unchanged;
4. valid support + valid refutation yields `mixed`, regardless of which score is larger;
5. evidence valid for one proposition cannot support a different obligation merely due to
   lexical/NLI strength;
6. temporal mismatch prevents old validation from proving current post-change behavior;
7. incomplete/unknown aperture blocks a terminal result without deleting positive
   evidence;
8. unresolved supplier status remains visible and blocks resolution;
9. the full public CI gate remains green.

## Stop conditions

Do not promote this downstream design if any test requires deleting an evidence record,
mutating a prior trace, treating `unknown` as absent, or allowing a stronger score to
override a proposition-specific semantic or lifecycle mismatch.

A CI failure caused by the apparatus itself is recorded and corrected in a separate
commit before interpreting the experiment.
