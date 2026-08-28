# Contract C RC2-C — CAL Evidence-to-Rule Dependency Receipt

## Status

Preregistered narrow Research experiment. No production semantic change, Contract-B change, Contract-C version, downstream consumer, or Decision Engine behavior is authorized.

## Decision under test

Determine whether current CAL v0.2 execution contains enough legitimate information to produce a compact attributable receipt for the frozen absolute-wording/counterevidence seam:

`evidence state -> rule trigger -> emitted rule result -> terminal verdict branch`.

The experiment is limited to this one seam. Success authorizes only a broader CAL rule-family attribution experiment.

## Frozen identities

- CAL production-semantic SHA: `33a928db97316a3652d57df9cafb8ca240305233`.
- Research base / live main at start: `18592eef336ffc7c2b6b34d8ac489843f5274583`.
- Frozen `tests/test_rules.py` blob: `ed42acb8c21843676028ccd8c2b9ecc776ad2154`.
- Frozen production `rules.py` blob: `4e2c7ebb1a7866d941fc2570757e64098359413a`.
- Frozen production `policy.py` blob: `cdd7c248b50660c0d2ed93db0f351e3c0630f67f`.
- RC2-A2 / CAL PR #19 head: `a148191927074de34537d0e7bc5cc22d6fa0432f`; disposition `INCONCLUSIVE`.
- RC2-B / CAL PR #20 head: `8c80f8ab9a08f209d3bf91a52e9621b8b2968694`; disposed claim `the missing RC2-A obligations require reopening Contract B`; primary disposition `FALSIFIED` for the tested Contract-C needs only.

RC2-A remains frozen FAILED at PR #16 head `96c55fd4721b66cf138d89f52e262696ba6b6c01`.

## Frozen behaviorally relevant policy identity

Canonical policy JSON is UTF-8, recursively key-sorted, compact separators, one trailing LF:

```json
{"candidate_admission":0.4,"config_id":"cal-rules-v1.2.0","counterevidence_weight":0.3,"false_caution_detection":true,"false_caution_threshold":0.85,"needs_source_detection":true,"overstated_detection":true,"partial_support":0.55,"require_passage_level_match":true,"sourced_support":0.8}
```

Canonical SHA-256: `88f007c96f3acf63a191556fe7fa46b80b37e9fcb5224ec1e90fb626a061104d`.

A human-readable `config_id` alone is not accepted as policy identity.

## Frozen production seam

Original vector:

- proposition: `The tool guarantees audit summaries.` / type `prediction`;
- evidence text: `The tool guarantees audit summaries.`;
- support candidate score: `1.0`;
- counterevidence candidate score: `0.5`;
- expected production support signal: `0.85`;
- expected final verdict: `overstated`;
- expected rule codes: `counterevidence_present`, `future_certainty`, `overconfident_wording`.

Production `_absolute_wording_needs_flag(...)` returns `True` immediately when `counter_contexts` is non-empty. Therefore in the original execution the causal evidence state is the non-empty counterevidence-context collection. Direct-support contexts are available to the call but their passage contents are not examined after that short-circuit.

Causal-removal mutation:

- remove only counterevidence;
- keep proposition, evidence and support candidate score `1.0` fixed;
- expected support signal: `1.0`;
- expected final verdict: `supported`;
- expected absence of `future_certainty`, `overconfident_wording`, and `counterevidence_present`.

## Candidate receipt obligations

Research-only receipt for this seam must contain only attributable state needed to validate the causal chain:

- proposition/execution identity;
- available direct-support refs and the subset actually examined by the absolute-wording trigger;
- counterevidence refs and the collection-presence state actually examined by the trigger;
- exact lexical trigger and trigger predicate/result;
- canonical behaviorally relevant policy object/hash;
- emitted rule IDs/codes/results;
- dependency edges from observed evidence state to emitted rule result;
- terminal production branch and final verdict;
- explicit causal-input versus terminally-residual classification.

The receipt must preserve the distinction that counterevidence **state** is causal to the overconfidence/future-certainty rules even though the later `counterevidence_present` rule flag is terminally residual once the overstatement branch fires.

Do not add generic eligibility, validity, aperture, applicability, citation, or other assessments production did not perform.

## Required controls

### C1 — causal removal

Remove only the counterevidence state. Production must change `overstated -> supported`, and the receipt must lose the counterevidence-to-rule dependency.

### C2 — irrelevant-state negative control

Add an unrelated/non-triggering support-evidence state while preserving the original counterevidence seam. Production output must remain unchanged and the unrelated state must not be recorded as a causal dependency.

### C3 — missing-dependency fail closed

Delete a required dependency edge or trigger state from an otherwise unchanged receipt retaining the reported verdict. An independent receipt validator, operating without production internals, must reject it as insufficiently attributable.

### C4 — policy identity

Change one behaviorally relevant policy value while keeping `config_id == cal-rules-v1.2.0`. Canonical policy hash must change. For the preregistered mutation `overstated_detection=False`, production is expected to cease the overstatement rule family and return `partially_supported` on the original evidence state.

### C5 — necessity of causal attribution

Test the weaker representation that retains terminal verdict/rules/evidence presence but omits dependency edges. The independent validator must be unable to validate the evidence-removal consequence from the receipt alone. The semantic distinction at stake is whether linked counterevidence **caused** the overstatement rules or was merely co-present residual state. A consumer that must infer this relation by re-executing private CAL rule semantics does not possess an independently attributable producer receipt.

## Competing explanations

1. A small evidence-to-rule dependency receipt is sufficient.
2. Production uses hidden/unretained state and a narrow production instrumentation change is necessary.
3. Multiple causal bases are valid and a receipt must preserve multiplicity rather than inventing one cause.
4. Exact causal attribution is unnecessary and deterministic replay is sufficient.

Explanation 4 is weakened only if C3/C5 demonstrate an independently relevant distinction that terminal replay cannot validate without hidden CAL semantics.

## Dispositions

Finish with exactly one primary disposition: `SUPPORTED FOR PROMOTION`, `FALSIFIED`, `INCONCLUSIVE`, or `SUPERSEDED`.

`SUPPORTED FOR PROMOTION` means only that the mechanism is justified for the next broader CAL rule-family attribution experiment. It does not authorize production implementation or Contract C.

## Hard stops

Do not change Contract B, production CAL semantics, `ClaimAssessment`, a Contract-C schema/version, Decision Engine behavior, or Consumer B. Do not generalize beyond this seam. A failed scientific control must remain recorded; any later correction requires an explicit deviation record.