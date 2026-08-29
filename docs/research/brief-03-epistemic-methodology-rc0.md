# CAL Epistemic Methodology RC0

## Decision

Determine the minimum epistemic state, separation, and causal accounting CAL needs so that materially different causes of abstention or non-decision remain reconstructable without silently converting missing information, excluded evidence, weak evidence, policy choices, or execution failure into one another.

Architecture selection is downstream of that methodology decision.

## Research class

Draft Research. This branch is an evidence record only. It does not authorize production changes, merge, release, Contract B/C changes, Evidence Bundler changes, Decision Engine changes, or promotion of the historical `feat/v2-epistemic-pipeline` branch.

## Live identities recorded before Phase 1

- CAL production `main`: `e90f301cf6ca02c0c77b6e88c3b08f8b93b9a36a`
- CAL immutable release baseline expected/pinned for semantic comparison: `v0.5.0` / `5533bbcf27a3ee3a7d901f7dfc44c241bc558e2c` (tag identity to be verified independently before decisive execution)
- Historical v2 branch identity only, not inspected during Phase 1: `feat/v2-epistemic-pipeline` at `b7254e713feb5556a81fb0c5b39649c415a949c6`
- Contract C expected/pinned release: `contract-c-v1.0.0` / `5fe55f9ed5d0ee9f026ca1b077e9d70ce0487ea1` (release identity to be verified independently before decisive execution)

The current `main` parent relationship indicates the post-release change is release-recovery/publication infrastructure; Phase 1 will verify whether any CAL semantic delta exists relative to the immutable v0.5.0 release rather than assuming none.

## Phase 1 isolation boundary

Before inspecting any implementation, comments, tests, or detailed design from `feat/v2-epistemic-pipeline`, Phase 1 will inspect only current production CAL, immutable v0.5.0, current tests and frozen traces/fixtures, public historical records, issue #3, and released contracts.

The Phase 1 apparatus must be frozen on this branch before Phase 2 begins. The frozen apparatus will include:

- production epistemic-path inventory;
- abstention causal matrix;
- behavioral evaluator properties;
- selected fixtures and mutation plan;
- expected invariants;
- explicit falsifiers;
- excluded cases and reasons;
- exact baseline identities and fixture hashes where practical.

If the Phase 1 evaluator is later falsified, the decisive run will remain preserved and a clearly separated successor apparatus will be required.

## Required evaluator properties

Candidate methods will be judged on behavior, not resemblance to a preferred architecture. The preregistered property families are:

1. state distinguishability;
2. fail-closed missing state;
3. evidence retention;
4. measurement-policy separation;
5. upstream-role invariance;
6. trust/eligibility separation;
7. causal decision-basis reconstruction with multiplicity;
8. execution-state separation;
9. policy counterfactual stability;
10. replayability.

## Required discriminators

The frozen test plan must include, where current production artifacts make them legitimate:

- evidence-presence controls;
- upstream nomination-role mutation;
- trust metadata mutation;
- known/adverse/unknown/not-performed eligibility controls;
- applicability/temporal/authority unknown controls where ownership is legitimate;
- one-at-a-time evidence removal interventions;
- multi-passage/aggregation controls;
- early-return/execution-failure controls;
- policy-only counterfactual replay;
- at least one deliberately weak methodology that should fail a promotion-relevant property for the intended reason.

If the weak control and a sophisticated candidate clear the same methodology gate, the architecture comparison is `INCONCLUSIVE` rather than evidence for complexity.

## Phase 1 stopping/falsification rules

Stop or preserve a negative disposition when:

- a preregistered falsifier is observed;
- required production behavior cannot be reconstructed from available artifacts;
- the evaluator proves insufficiently discriminating;
- frozen fixtures would need to change after candidate exposure;
- the remaining uncertainty requires a successor experiment;
- continuing would become implementation without additional epistemic value.

## Protected state

Production CAL verdict behavior, v0.5.0, Contract B, Contract C 1.0.0, Evidence Bundler, Decision Engine, production thresholds/model choices, existing failures, and historical research evidence are protected from mutation in RC0.

## Planned terminal outputs

RC0 will preserve observed evidence, inference, falsified alternatives, live hypotheses, unknowns, a bounded methodology disposition, explicit non-claims, and the next smallest discriminating test if needed. No production promotion occurs in this task.
