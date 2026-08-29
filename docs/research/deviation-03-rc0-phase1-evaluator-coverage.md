# CAL Epistemic Methodology RC0 — Apparatus deviation: Phase 1 evaluator coverage

## Status

**POST-CANDIDATE-EXPOSURE APPARATUS DEVIATION.**

This record invalidates the frozen Phase 1 apparatus at commit `9b28df7298257218ec0c9f33163fb60dde71d2a6` as a complete decisive evaluator for the RC0 architecture disposition.

The frozen files are preserved unchanged. They are not repaired in place.

## When discovered

The omission was discovered after the historical `feat/v2-epistemic-pipeline` branch had been inspected and after exploratory candidate adapters had been added at head `0e8ab401fc91836703028b5aa97d2b672d729925`.

Therefore any corrected evaluator created in this same execution context would no longer satisfy RC0's original clean Phase-1-before-v2-exposure isolation condition.

## What was wrong

The user's RC0 protocol required the Phase 1 mutation plan to exercise several specific state interventions. The frozen apparatus covered many but not all of them.

### 1. Positive eligibility state was omitted

The protocol required proposition-specific eligibility to vary across:

- positively established;
- adversely established;
- unknown;
- not performed;
- not applicable where legitimate.

The frozen fixture set included adverse, unknown, not-performed, and not-applicable, but **did not include positively established eligibility**.

This matters because a methodology could pass the frozen gate while lacking a truthful representation for a performed-positive assessment.

It also matters for Contract C compatibility: released Contract C 1.0.0 currently has generic assessment encodings for `not_performed`, performed `unknown`, performed `adverse`, `not_applicable`, and `failed`; it does not encode a generic performed-positive value. RC0 cannot claim exact Contract-C compatibility without confronting that gap.

### 2. Trust mutation did not cover all preregistered values

The protocol required the same claim/passage semantic measurement to be held fixed while trust metadata varies among:

- `primary`;
- `secondary`;
- `background`.

The frozen fixture set included primary and background only. Secondary was omitted.

Current P1 treats any present non-primary value equivalently for adverse-decision suppression, but that implementation fact does not excuse omission of a preregistered metamorphic value.

### 3. Evidence-presence controls were incomplete

The protocol called for a claim-fixed ladder including:

- no passages;
- irrelevant passages;
- weakly related passages;
- clearly supportive passage;
- clearly contradictory passage;
- mixed evidence.

The frozen apparatus represented several analogous abstract states, but it did not include a literal no-passages case or a complete explicit ladder under one fixed claim identity. It therefore cannot establish that the methodology distinctions remain coherent across the full preregistered presence-control family.

### 4. Applicability / temporal / authority unknown controls were not exercised

The protocol specifically required controlled fixtures where semantic support is held constant while decision-relevant applicability information is absent or changed, with ownership left open rather than invented.

The frozen evaluator exercised eligibility-state absence but did not separately exercise temporal applicability or authority unknown/not-performed state.

This omission is material because CAL issue #3 independently records fail-closed proposition-specific eligibility / temporal / authority context as still open.

### 5. Causal intervention was represented, not executed as an evaluator intervention

F11/F12 froze `removal_effect` facts describing independent versus joint sufficiency, but the evaluator checked candidate-declared `basis_form` and members rather than deriving or validating those claims by actually replaying one-at-a-time removals.

That is weaker than the preregistered causal-intervention requirement. A candidate could theoretically echo the expected causal vocabulary without demonstrating that its terminal result changes under the required interventions.

### 6. Policy counterfactual gate was too weak

The frozen policy-counterfactual pair required:

- different policy identity;
- unchanged measurement token;
- unchanged retained evidence.

It did **not** require a controlled case in which the downstream/eligibility policy actually changes the derived participation or terminal conclusion while upstream measurement remains invariant.

A methodology that merely records two policy IDs could therefore pass this gate without proving the intended separation.

## What remains valid from the first apparatus

The deviation does **not** erase the following direct production observations:

- current CAL already distinguishes several non-decision causes;
- no-evidence and read-silent traces are different today;
- Contract-B nomination containers do not drive v1 NLI measurement intake;
- `trust_level` is not passed into NLI measurement;
- P1 later uses source `trust_level` as an adverse-decision suppression condition;
- suppressed measured evidence remains in the original entailment trace;
- the final post-suppression deciding pool/signal is not a first-class typed v1 `AuditTrace` field;
- Contract C 1.0.0 already separates execution state from subject-matter conclusion and has explicit generic assessment-state slots;
- historical v2 contains explicit removals/per-role participation but lacks several Contract-C-style state distinctions.

Those are code/artifact observations independent of the deficient evaluator.

## What is invalidated

The exploratory comparison encoded after Phase 1 freeze may be retained as diagnostic evidence, but it may **not** establish:

- that an additive receipt is sufficient for the full RC0 methodology;
- that a staged pipeline is unnecessary;
- that the historical v2 architecture is falsified as a whole;
- that current Contract C 1.0.0 can losslessly carry every epistemic state RC0 may require.

In particular, the fact that the additive receipt and a staged-ledger shadow candidate were observationally equivalent under the deficient evaluator is useful hypothesis evidence, not a decisive architecture result.

## Scientific consequence

The original stopping rule has fired: **the frozen evaluator is not adequate for the intended bounded architecture decision and a new experiment is required.**

RC0 therefore cannot honestly end with a positive architecture disposition.

Primary research disposition for this run: **INCONCLUSIVE**.

## Successor rule

Do not repair the frozen Phase 1 fixture/evaluator files.

The next experiment must be a genuinely fresh-context successor, provisionally `CAL Epistemic Methodology RC0A`, that starts from the original RC0 protocol plus this deviation record and freezes the missing controls before inspecting old-v2 implementation or prior candidate-result details.

The successor should not inherit expected candidate gate vectors from this run. It should inherit only:

- the original decision question;
- direct production observations that are durable GitHub evidence;
- this explicit apparatus-failure record;
- the exact missing protocol controls listed above.
