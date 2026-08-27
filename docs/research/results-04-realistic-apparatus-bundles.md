# Research Results 04 — Realistic apparatus-bundle decision sequence

**Branch:** `research/obligation-composition-shadow`  
**PR:** #1, draft  
**Preregistration:** `docs/research/brief-04-realistic-apparatus-bundles.md`  
**Production impact:** none  
**Final corrected run:** Public suite run #14  
**Interpretation status:** H6–H9 supported within the preregistered downstream boundary

## Executive result

The relation-preserving CAL shadow survived a realistic three-snapshot audit sequence in which several epistemic conditions coexisted for the same claim:

- stale positive validation;
- current human-control evidence;
- supplier assertions and later supplier qualification;
- a post-change incident contradicting adequate control;
- CAPA/remediation evidence;
- current-state revalidation;
- explicit unresolved state.

The experiment held passage-level support/refutation measurements fixed across snapshots and allowed only two kinds of change:

1. new evidence entering through a new immutable bundle snapshot;
2. explicit eligibility/validity assessments supplied by the research decision sidecar for the current proposition/state.

The observed decision sequence matched the preregistration:

```text
B04-1  supplier status unresolved
       -> abstain: eligibility_unknown

B04-2  supplier qualified, incident still valid
       -> abstain: mixed_valid_evidence

B04-3  remediation + current-state validation
       -> decide: supported
```

The final support decision did not require deleting the old validation or historical incident. Both remained in the raw ledger and became non-deciding only through explicit current-state validity assessments.

## Public-suite result

Corrected head `fc815041dd64d8e97f690ad20fe5b04e2cf12cbd` was certified by Public suite run #14:

- **988 passed**;
- **5 skipped**;
- **48 research-artifact tests deselected**;
- **7 warnings** from the existing Torch JIT deprecation surface;
- Ruff: pass;
- Ruff format check: pass;
- mypy: pass, no issues in 49 source files.

Relative to the previous Annex 22 preservation rung at 982 passing tests, Rung 04 adds six passing bundle-level tests.

## Recorded apparatus deviation

The first Rung 04 public-suite execution reported:

- 986 passed;
- 2 failed;
- 5 skipped;
- 48 deselected.

Both failures were caused by the pairwise test harness using `zip(..., strict=True)` over a three-item sequence and its two-item shifted suffix. The scientific assertions did not fail; the adjacent-pair loops raised before executing their comparisons.

The defect is recorded separately in `docs/research/deviation-04a-pairwise-harness.md`.

Commit `3da111dd9429b54f3cc786c0801c78da3ae071d5` corrected only the pairwise iterator construction. No fixture content, score, annotation, threshold, reason code, or expected verdict changed.

Because GitHub did not emit a synchronization check for the corrected commit, the draft PR was closed and immediately reopened without changing code or review posture. The default `pull_request` reopening event produced run #14 against the corrected head plus the deviation record. The PR remains draft and open.

## H6 — Bundle-level preservation

**Result: supported.**

The three snapshots use distinct bundle IDs and grow monotonically:

```text
B04-1
  pre-change validation
  human-review control
  supplier attestation
  post-change incident

B04-2
  everything in B04-1
  + supplier qualification

B04-3
  everything in B04-2
  + CAPA/remediation closure
  + current-state validation
```

For every passage carried into a later snapshot, the Contract-B-shaped passage record remains byte-for-byte equivalent at the parsed-object level. Shared passage measurements also remain unchanged across snapshots.

This supports the preservation invariant at a more realistic bundle scale: later knowledge adds evidence and assessments rather than rewriting earlier evidence objects.

## H7 — Sequential uncertainty exposure

**Result: supported.**

B04-1 contains both strong valid support and a strong valid post-update incident, but the supplier attestation has unresolved eligibility.

Observed result:

```text
eligibility_unknown
```

After supplier qualification in B04-2, CAL does **not** jump to `supported`. The supplier contribution becomes eligible, exposing the still-valid support/refutation conflict.

Observed result:

```text
mixed_valid_evidence
```

This is the intended behavior. Resolving one epistemic blocker reveals the next actual decision state instead of treating uncertainty removal as positive evidence.

## H8 — Current-state resolution without historical erasure

**Result: supported.**

B04-3 adds CAPA/remediation closure and validation of the current post-remediation model version.

The research annotations make two historical items non-deciding for the current-state proposition:

- pre-change validation remains retained but is temporally stale for the current system state;
- the historical incident remains retained but is not treated as refutation of the explicitly post-remediation state after remediation and revalidation are supplied.

Observed state:

- raw ledger contains both `support:p-pre-validation` and `refutation:p-incident`;
- valid view excludes those two contributions;
- valid view retains current-state validation, CAPA closure, human-review control, supplier attestation, and supplier qualification;
- valid evidence state is `support_only`;
- final verdict is `supported`.

The result therefore supports the distinction between **historical evidence retention** and **current decision participation**.

It does not establish that every remediation event should invalidate every historical incident. That proposition/state assessment was supplied explicitly as part of the fixture and remains a separate operator-design problem.

## H9 — Current handoff sufficiency

**Result: the preregistered contract-gap hypothesis is supported.**

The Contract-B-shaped claim/passages intentionally remain limited to fields represented by the current handoff design: claim identity, evidence/counterevidence passages, provenance/trust-related fields, scaffold labels, and null audit outputs.

They do not contain the richer state required by this shadow decision sequence:

- eligibility;
- proposition-specific semantic validity;
- aperture/completeness;
- temporal applicability;
- authority/status applicability.

The test explicitly removes the research sidecar and requires reconstruction to fail rather than inventing defaults. It does fail explicitly.

### What H9 does and does not mean

H9 does **not** prove that all of those fields belong inside Contract B.

It proves a narrower interface fact:

> The richer downstream decision state cannot be reproduced from the current Contract-B-shaped payload alone without another typed source of decision-state information or fresh inference.

Possible architectures remain open:

1. extend a future Apparatus Contract version;
2. define a separate receipt-bound decision-annotation artifact alongside Contract B;
3. make CAL produce some assessments as explicit auditable stages after handoff;
4. divide responsibility, with upstream metadata supplied and CAL-specific semantic assessments produced downstream.

Choosing among those options requires another experiment rather than silently expanding the locked contract.

## What this rung supports

Promote for further research:

1. immutable/growing evidence snapshots rather than in-place historical rewriting;
2. fixed measurements remaining stable while decision participation changes explicitly;
3. sequential blockers where resolving one unknown reveals the next actual state;
4. current-state support decisions that retain contradictory/stale historical evidence;
5. explicit proposition/state validity as a distinct dependency from NLI score;
6. an auditable interface for eligibility, validity, aperture, temporal scope, and authority/status information.

## What this rung does not validate

Do not infer validation of:

- automatic claim decomposition;
- automatic obligation generation;
- retrieval completeness;
- automatic authority/status classification;
- automatic temporal-scope reasoning;
- automatic CAPA effectiveness judgments;
- automatic supplier qualification judgments;
- production replacement of CAL's released decision path.

All such judgments were outside the experiment boundary or supplied explicitly through the research sidecar.

## Next experiment

The next useful question is no longer whether the contribution ledger can represent the richer state. It can, under these tests.

The next question is **where the decision annotations come from and what evidence makes each one defensible**.

A focused interface experiment should take one or two Rung 04 dependencies, especially temporal applicability and supplier/authority eligibility, and compare candidate ownership models:

```text
Apparatus-supplied metadata
vs
separate decision-annotation contract
vs
CAL-produced receipt-bound assessment
```

The test should ask which facts can be mechanically supplied, which require proposition-specific interpretation, and which must remain explicit `unknown` unless a dedicated assessment stage produces a receipt.