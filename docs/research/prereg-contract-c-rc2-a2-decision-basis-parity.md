# Contract C RC2-A2 — Decision-Basis Parity Sweep

## Task class

Draft Research experiment. Production impact: none.

## Decision supported

Determine whether a compact attributable decision-basis receipt can be deterministically materialized from current CAL v0.2 production execution without changing CAL's verdict semantics, before any clean-room Contract-C consumer experiment.

## Pinned state

- CAL current `main` at experiment start: `18592eef336ffc7c2b6b34d8ac489843f5274583`.
- Production-semantic parent used by RC2-A/RC2-A1: `33a928db97316a3652d57df9cafb8ca240305233`.
- The delta from that parent to current `main` is governance documentation only (`docs: add compact governance PR template`), not production CAL behavior.
- Frozen v0.2 rule-vector source: `tests/test_rules.py`, Git blob `ed42acb8c21843676028ccd8c2b9ecc776ad2154` at the pinned start SHA.
- Frozen RC2-A predecessor remains FAILED at PR #16 head `96c55fd4721b66cf138d89f52e262696ba6b6c01`.
- RC2-A1 predecessor remains separate at PR #17 head `7932018fd17d13feead3fbef6c974fa5a6db1d65` with finding `A. Boundary-materialization gap`.

## Claim under review

A compact research-only receipt can represent the actual v0.2 verdict branch using only already-computed/legitimate execution state, while distinguishing headline-deciding inputs from merely present evidence/rules and retaining explicit `not_performed` state for generic assessment families that production did not execute.

## Competing explanations

1. The proposed receipt is sufficient and attributable; the remaining Contract-C producer blocker is boundary materialization only.
2. Exact basis is not stably representable because production logic depends on hidden/unretained state.
3. A receipt can replay the verdict but cannot truthfully separate deciding from residual inputs.
4. Basis is non-unique in some cases (for example tied maxima or multiple sufficient rule triggers), requiring multiplicity to be represented rather than inventing a single cause.
5. Reproducibility requires more policy state than a policy/config identifier alone.

## Frozen vectors

The sweep will reproduce the existing semantic cases in `tests/test_rules.py`, including:

- unclassified/not-checkable;
- no-source behavior where needed;
- numeric direct support and numeric mismatch;
- all frozen support-threshold boundaries;
- counterevidence scalar reduction;
- direct absolute wording versus counterevidence-restored overstatement;
- policy-switch control;
- causal-overreach;
- comparative missing evidence;
- credential/source, public-link/source, and date/source requirements;
- overconfident/future-certainty/scope-overreach;
- low-reliability-only support;
- stale-source opt-in and its default-config invariance.

Additional mutation controls may be added only to discriminate basis attribution, not to change expected production semantics.

## Candidate compact receipt obligations

For each proposition execution, the research receipt must contain only mechanically attributable state sufficient for replay:

- production branch identifier;
- reported support verdict;
- support scalar and its policy thresholds where the scalar participates;
- all support candidates attaining the maximum support score, if any;
- all counterevidence candidates attaining the maximum counterevidence score, if any;
- counterevidence weight where used;
- rule IDs/codes that actually trigger the selected branch;
- rule IDs/codes that are present but residual to the headline branch;
- the policy switches/values necessary to reproduce branch precedence;
- `not_performed` for generic eligibility, semantic-validity, aperture/completeness, temporal/applicability, and citation assessment families unless a real production stage establishes one.

The receipt must not label a narrow rule such as `stale_source`, `low_reliability_only`, or `public_link_missing_source` as a generic semantic assessment.

## Acceptance criteria

Support the claim only if all of the following hold on the frozen sweep:

1. independent receipt replay reproduces every production `support_label` exactly;
2. every emitted deciding rule is sufficient to satisfy the selected rule-family branch condition, while non-triggering rules are classified residual;
3. score-threshold branches classify rule flags as residual when the same headline verdict would be selected before the final residual-rule downgrade;
4. high-score `partially_supported` cases caused only by residual-state/rule presence identify that rule state as headline-deciding;
5. counterevidence basis records the actual scalar maximizer(s), not all counterevidence candidates;
6. non-max support candidates are not mislabeled as scalar-deciding;
7. tied maxima, if tested, are represented as a co-maximal set rather than arbitrarily selecting one evidence item;
8. removal of a required receipt field fails replay closed;
9. the generic five assessment families remain explicitly `not_performed`;
10. no file under `src/` changes and existing production tests remain unchanged.

## Falsification criteria

Falsify or materially weaken the claim if any frozen production vector cannot be replayed without:

- invoking a new semantic judgment;
- carrying hidden implementation telemetry unrelated to the verdict branch;
- falsely calling residual evidence/rules deciding;
- inventing a unique cause where production admits multiple sufficient bases;
- or consulting research-only RC1/decision-model semantics to determine a production verdict.

If only a bounded receipt-shape issue is exposed, record it and classify the experiment `INCONCLUSIVE` or `SUPPORTED FOR PROMOTION` with bounds as justified. Do not repair the evaluator after seeing an inconvenient result without a deviation record.

## Controls

- **Parity control:** receipt replay versus production `assess_claim_support` for every frozen vector.
- **Residual mutation:** a flag present below a score threshold must not be promoted to headline-deciding if the threshold already fixes the verdict.
- **Deciding-rule mutation:** at sourced-support score, a limiting rule that changes `supported` to `partially_supported` must be recorded as deciding.
- **Argmax mutation:** a lower-scoring candidate must not enter scalar basis; tied maxima must remain explicit.
- **Missing-state control:** delete a required receipt component and require replay failure.
- **Policy identity control:** test whether behaviorally relevant policy switches can be omitted safely; if not, retain them explicitly.

## Hard boundaries

Do not:

- change CAL production verdict semantics;
- modify production `ClaimAssessment`;
- modify frozen RC2-A or RC2-A1 history;
- assign or promote a Contract-C version;
- run clean-room Consumer B;
- use the held-out MainFrame negative control;
- change Contract B, Decision Engine, Outcome Model, or workflow behavior.

## Required result record

End with observed evidence, inference, remaining hypotheses, unknowns, falsified alternatives, one allowed research disposition, and the single smallest next evidence-producing step.