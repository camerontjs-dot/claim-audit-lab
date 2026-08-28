# Contract C RC2-A2 — Decision-Basis Parity Sweep Results

## Decision under review

Determine whether a compact attributable decision-basis receipt can be deterministically materialized from current CAL v0.2 production execution, before any clean-room Contract-C consumer experiment, without changing CAL verdict semantics.

## Pinned state

- CAL `main` at experiment start: `18592eef336ffc7c2b6b34d8ac489843f5274583`.
- Production-semantic parent: `33a928db97316a3652d57df9cafb8ca240305233`.
- Frozen v0.2 rule-vector source: `tests/test_rules.py`, blob `ed42acb8c21843676028ccd8c2b9ecc776ad2154`.
- Preregistration commit: `2b26260c4c663d9d84381d944bb2bb2d84af510f`.
- First code-bearing experiment commit: `cc26c986c8fe689f4f544212bc850b3a6624ff95`.
- Corrected code-bearing experiment commit after the recorded lint-only deviation: `46d8fdc336b015ea2e11d4ac66e89ac3dad2cbe1`.
- RC2-A remains FAILED at PR #16 head `96c55fd4721b66cf138d89f52e262696ba6b6c01`.
- RC2-A1 remains a separate predecessor at PR #17 head `7932018fd17d13feead3fbef6c974fa5a6db1d65`.

No production file under `src/` was changed.

## Observed evidence

### O1. Verdict replay parity succeeded across the frozen production rule vectors

The research receipt and an independent replay function reproduced the production `support_label` and control-flow branch for the frozen v0.2 semantic cases represented in `tests/test_rules.py`, plus the explicit classified/no-sources branch.

The sweep covered:

- unclassified / `not_checkable`;
- classified no-source behavior;
- numeric direct support and mismatch;
- all frozen support-threshold boundaries;
- counterevidence scalar reduction;
- absolute-wording direct support and counterevidence-restored overstatement;
- behaviorally relevant policy switches;
- causal overreach;
- comparison missing evidence;
- credential, public-link, and date source requirements;
- overconfident wording;
- low-reliability-only limiting state;
- stale-source opt-in and default-config invariance;
- future certainty;
- scope overreach.

For those vectors, replay did not require invoking RC1 research semantics or a new semantic judgment.

### O2. Scalar basis is narrower than the candidate evidence set

Production support signal is determined by:

- the maximum support-candidate score;
- the maximum counterevidence score;
- the configured counterevidence weight.

The added mutation control with two counterevidence candidates (`0.7` and `0.2`) demonstrated that only the `0.7` candidate participates in the scalar. The lower-scoring candidate remains retained evidence but is not part of the scalar basis.

### O3. A unique deciding evidence item cannot always be claimed

A tied-support control with scores `0.8`, `0.8`, and `0.7` produced a `supported` result while the scalar had two co-maximal support passages.

The receipt therefore records the co-maximal set rather than inventing one arbitrary winner.

This falsifies a single-`contributing_passage_id` model as a universal description of v0.2 scalar basis.

### O4. Rule presence and headline decision role are distinct

Two existing frozen-vector families demonstrate that an emitted rule can be present but not headline-deciding:

- numeric mismatch at support signal `0.69`;
- comparison missing evidence at support signal `0.55` with an admitted candidate.

In each case the score threshold already selects `partially_supported`; the rule remains residual to that headline branch.

By contrast, at sourced-support score `0.80`, `low_reliability_only` or `stale_source` changes the clean `supported` branch into `partially_supported`. Those rules are headline-deciding in those executions.

### O5. Multiple rules can be co-sufficient rather than uniquely causal

When production reaches the final sourced-score downgrade, its branch condition is effectively `counterevidence present OR any rule code present`. If multiple rule codes are present there, each is sufficient for the branch predicate.

The research receipt therefore preserves co-sufficient deciding rules instead of choosing one unique cause.

### O6. Policy/config name alone is not enough for deterministic replay at the rule-function surface

A control constructed with `dataclasses.replace` retained `config_id == "cal-rules-v1.2.0"` while setting `overstated_detection=False` and `needs_source_detection=False`.

Under the same claim/evidence input, the default policy returned `needs_source`; the mutated policy returned `unsupported`.

Therefore a receipt that retained only the policy/config name could falsely claim reproducibility. The tested receipt includes the behaviorally relevant thresholds, counterevidence weight, and rule-family switches needed for support-label replay.

This is a unit-surface finding. The locked Contract-B production path separately performs policy-drift checks; RC2-A2 does not claim arbitrary mutated policies are accepted by that locked path.

### O7. Generic rich assessment families remain truthfully `not_performed`

The receipt keeps the RC2-A1 distinction for:

- eligibility;
- semantic validity;
- aperture/completeness;
- temporal/applicability;
- citation.

Each is recorded as `not_performed`; narrow production rules are not renamed into those richer semantic assessments.

### O8. Missing receipt state fails replay closed

Deleting required receipt families such as policy state, signal basis, rule partition, or source-presence state causes replay to fail instead of inventing defaults.

### O9. Terminal branch attribution is not the same as complete causal contribution attribution

The strongest counterexample came from the existing absolute-wording + counterevidence path.

Observed pair:

- direct evidence repeating the absolute wording, no counterevidence -> `supported`;
- the same direct evidence plus counterevidence -> `overstated`.

Production `_absolute_wording_needs_flag` returns true whenever `counter_contexts` is non-empty. The counterevidence therefore causes `overconfident_wording` / `future_certainty` to fire.

However, once those overstatement rules fire, the production support-label function returns from the overstatement branch before the later `counterevidence_present` residual-downgrade condition is reached.

The first compact receipt correctly identifies the overstatement rules as terminal branch triggers and the `counterevidence_present` flag as terminally residual, but it does **not** encode the causal edge:

`counterevidence presence -> overstatement rule fired -> overstated verdict`.

So verdict replay is demonstrated, while complete causal attribution of every deciding evidence/rule contribution is not yet demonstrated.

### O10. First run failure was apparatus hygiene, preserved rather than erased

First code-bearing Public suite run `33142053092`, job `98754819177`, at `cc26c986c8fe689f4f544212bc850b3a6624ff95`:

- pytest: `991 passed, 5 skipped, 48 deselected, 7 warnings`;
- Ruff: failed with exactly three `E501` line-length violations in the research test file;
- format and mypy were skipped after Ruff failure.

Deviation record:

`docs/research/deviation-contract-c-rc2-a2-001-lint-only.md`

Only the three overlong lines were wrapped. No fixture, expected branch, receipt field, policy value, threshold, mutation control, acceptance criterion, or falsifier changed.

Corrected code-bearing Public suite run `33142364518`, job `98755785930`, at `46d8fdc336b015ea2e11d4ac66e89ac3dad2cbe1`:

- pytest: `991 passed, 5 skipped, 48 deselected, 7 warnings`;
- Ruff: pass;
- Ruff format check: pass;
- mypy: pass, no issues in 50 source files.

## Inference

1. **Boundary materialization remains technically plausible.** Production v0.2 verdicts in the frozen rule surface can be replayed from a compact deterministic receipt without adding the rich RC1 semantic assessments.
2. **The basis must preserve non-uniqueness.** Scalar ties and co-sufficient rule triggers mean a universal single `deciding_evidence_id` or single `deciding_rule_id` would overstate what production establishes.
3. **A branch receipt is not yet a complete contribution receipt.** The experiment exposed an indirect dependency where counterevidence causes a rule to fire even though the counterevidence flag is not the terminal branch trigger.
4. **Exact policy binding matters.** Reproducibility requires binding behaviorally relevant policy state or an identity cryptographically tied to that exact state; a human-readable config name alone is insufficient at the tested rule surface.
5. **No new epistemic assessment is currently indicated by this failure.** The unresolved part is execution attribution: which already-computed inputs caused which already-computed rule results.

## Falsified alternatives

### FA1. All candidate evidence belongs in exact scalar basis

Falsified. Only maxima participate in the current scalar; lower-scoring candidates remain non-scalar evidence.

### FA2. Exact basis always has one unique evidence contributor

Falsified by tied maxima.

### FA3. Every emitted rule flag is headline-deciding

Falsified by numeric-mismatch and comparison-missing threshold cases.

### FA4. Terminal branch triggers are sufficient to describe all actual deciding contributions

Falsified by the counterevidence -> absolute-wording rule dependency. Terminal branch replay can be correct while causal attribution remains incomplete.

### FA5. Policy/config name alone guarantees replay identity

Falsified at the rule-function surface by same-name/different-switch behavior.

### FA6. Rich generic eligibility/validity/aperture/temporal/citation judgments must be invented to replay v0.2

Falsified for the tested vectors. Explicit `not_performed` plus actual narrow rule receipts suffices for verdict replay.

## Remaining hypotheses

1. A compact **per-rule dependency receipt** can close the attribution gap without changing CAL verdict semantics by recording which already-existing inputs caused each fired rule.
2. Only a small subset of rule families may need explicit evidence/fact dependency edges; other rules may be fully attributable from their own stable trigger receipt.
3. A result package can separate:
   - scalar basis;
   - terminal branch basis;
   - upstream rule-dependency basis;
   without carrying the full internal trace.

## Unknowns

- Whether every production rule family exposes enough stable input identity to materialize its dependency receipt without instrumenting the rule implementation.
- Whether one generic dependency representation is adequate or operator-specific receipt shapes are needed.
- Whether a compact dependency receipt remains materially smaller than carrying the relevant full trace across multi-proposition runs.
- Independent-consumer reproducibility remains untested and is still blocked behind producer-side attribution sufficiency.

## Research disposition

**INCONCLUSIVE**

The experiment strongly supports compact deterministic **verdict replay** and several parts of basis materialization, but it does not yet establish the stronger claim required by Contract C: an exact attributable record of every evidence/rule contribution that actually determined the proposition conclusion.

Calling the result `SUPPORTED FOR PROMOTION` would collapse replay sufficiency into causal attribution sufficiency. The counterevidence/absolute-wording control shows those are not the same property.

No production promotion is authorized by RC2-A2.

## Single smallest next evidence-producing step

Run one focused research-only **rule-dependency receipt experiment** on the exposed absolute-wording/counterevidence seam.

Freeze the existing paired production vector and require a candidate per-rule receipt to record, without changing verdict behavior:

1. the exact absolute-wording trigger;
2. the direct-support evidence references examined by that rule;
3. the counterevidence references whose presence forces the rule result;
4. the emitted rule ID/result;
5. the terminal overstatement branch that consumes that rule;
6. mutation behavior showing that removing only the counterevidence dependency changes the rule outcome and final verdict as production currently does.

If that compact dependency receipt is sufficient and attributable, then generalize the same mechanism across the remaining rule families. Do not commission clean-room Consumer B before this gap is resolved.