# Contract C RC2-A1 — CAL Semantic-Boundary Gap Experiment

## Status

Preregistered bounded research experiment. No production change is authorized.

## Frozen predecessor

Contract C RC2-A is frozen as **FAILED** at CAL PR #16 head `96c55fd4721b66cf138d89f52e262696ba6b6c01`.

The predecessor's artifacts, CI runs, deviations, producer-gate evidence and negative findings are immutable inputs to this experiment. RC2-A1 will not modify or rerun RC2-A to obtain a passing gate.

Production baseline: `33a928db97316a3652d57df9cafb8ca240305233`.

## Primary question

For each semantic obligation missing at the real Contract-B -> CAL production boundary, determine whether production CAL already computes/establishes the state and merely loses it, or whether the state is not actually established by the current production path.

## Allowed classifications

Each missing obligation must receive exactly one final classification:

1. `computed-and-lost`
2. `available-but-unattributed`
3. `research-only`
4. `derivable-without-new-epistemic-judgment`
5. `requires-new-epistemic-behavior`
6. `not-actually-required`
7. `unresolved`

## Obligations under test

- exact deciding-contribution basis;
- eligibility assessment;
- semantic-validity assessment;
- aperture/completeness assessment;
- temporal/applicability assessment;
- citation assessment;
- reassessment/supersession lineage.

## Evidence rule

Trace each obligation through:

`input -> computation/assessment -> intermediate object -> conclusion -> persisted/public result`

A research object containing a field is not evidence that production computes it. A factual input that could support an assessment is not itself an assessment. `CAL could compute X` must remain distinct from `production CAL computes X`.

## Experiment A — exact basis

Inspect the actual production verdict function and intermediate state. Determine whether exact deciding evidence/rule contributions are retained, dropped, deterministically reconstructable from legitimate frozen state, or would require new decision-recording semantics. Candidate evidence as a whole is not automatically the decision basis.

## Experiment B — assessment families

For eligibility, semantic validity, aperture/completeness, temporal/applicability and citation, distinguish explicit production assessment, implicit collapse into another rule/score, upstream factual input only, or no assessment.

## Experiment C — research/production delta

Compare the real locked Contract-B production path with current richer additive/research machinery and frozen predecessor machinery. For each obligation record:

- production computes?;
- production exposes?;
- research computes?;
- deterministically derivable?;
- new epistemic behavior required?.

## Experiment D — minimal additive-boundary falsifier

Test the hypothesis:

> The Contract-C blocker can be resolved by a small attributable result/receipt materialization layer without changing CAL's substantive production verdict behavior.

The hypothesis fails if any still-necessary Contract-C obligation requires production to make an assessment it does not currently make.

No such semantic change will be implemented in RC2-A1.

## Experiment E — obligation reassessment

For each missing obligation identify the prior falsifier/consumer that justified it, distinguish semantic necessity from harness assumption, test whether a smaller state distinction suffices, and reject fields outside CAL ownership.

## Outcome vocabulary

Exactly one final finding:

- **A. Boundary-materialization gap**
- **B. Mixed gap**
- **C. Production-semantic gap**
- **D. Contract-C overreach**
- **E. Inconclusive**

## Hard stops

Do not run clean-room Consumer B, alter production CAL verdict semantics, assign a Contract-C version, promote Contract C, use the held-out MainFrame negative control, or implement Outcome Model / Workflow Advisor / Decision Engine changes.
