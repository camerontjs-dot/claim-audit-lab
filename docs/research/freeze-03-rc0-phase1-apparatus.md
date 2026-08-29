# CAL Epistemic Methodology RC0 — Phase 1 apparatus freeze

## Freeze declaration

This commit freezes the RC0 Phase 1 behavioral apparatus **before any content inspection of `feat/v2-epistemic-pipeline`**.

After this freeze, the following artifacts may not be silently altered in response to candidate architecture results:

- selected fixture cases and mutations;
- evaluator gates A-J;
- positive/weak controls;
- production path inventory / abstention matrix used to motivate the tests;
- expected invariants and falsifiers below.

If a frozen evaluator defect is discovered after candidate exposure, preserve the failed/deviating run and create a clearly separated successor apparatus. Do not repair this decisive apparatus in place.

## Exact frozen identities

### Production and released baselines

- CAL current production main used for Phase 1: `e90f301cf6ca02c0c77b6e88c3b08f8b93b9a36a`
- immutable CAL v0.5.0 release commit: `5533bbcf27a3ee3a7d901f7dfc44c241bc558e2c`
- semantic delta v0.5.0 -> current main: **none**; the one post-release commit adds only `.github/workflows/cal-v0.5.0-publication-recovery.yml`
- immutable Contract C 1.0.0 release commit: `5fe55f9ed5d0ee9f026ca1b077e9d70ce0487ea1`
- historical old-v2 head identity, not content-inspected before this freeze: `b7254e713feb5556a81fb0c5b39649c415a949c6`

### Frozen Phase 1 artifacts

- fixture set: `tests/research/fixtures/epistemic_methodology_rc0_cases.json`
  - Git blob: `1a528e89cb5c6b1354904b2a0fb3323c18b1dd28`
- behavioral evaluator: `tests/research/rc0_evaluator.py`
  - Git blob: `ccd394338dcfa9c12f2a60a5597777653f972335`
- evaluator assurance tests: `tests/research/test_epistemic_methodology_rc0_evaluator.py`
  - Git blob: `f67371afdc55d923afdf91fc74f8e9398e9d8be7`
- Phase 1 production path map + abstention matrix: `docs/research/results-03-rc0-phase1-path-map-and-abstention-matrix.md`
  - Git blob: `d6c5823d6a5cf0a83cecaefe1dbdf5db2fd77cee`

The Git object identities above are the frozen repository identities. The branch head created by this freeze commit is the apparatus commit for Phase 2 candidate exposure.

## Frozen evaluator properties

A. state distinguishability  
B. fail-closed missing state  
C. evidence retention  
D. measurement-policy separation  
E. upstream-role invariance  
F. trust/eligibility separation  
G. causal decision-basis reconstruction with multiplicity  
H. execution-state separation  
I. policy-counterfactual stability  
J. replayability

The evaluator consumes an **architecture-neutral research adapter surface**. The adapter is not proposed as a production contract or schema. Candidate internals may be staged, unstaged, ledger-based, rule-based, event-based, or otherwise factored.

## Frozen discriminators

The fixture set includes:

- no-evidence versus read-silent evidence;
- evidence measured then blocked from deciding;
- louder blocked evidence plus a quieter deciding contribution;
- upstream support/counterevidence nomination mutation with passage text fixed;
- trust metadata mutation with semantic measurement fixed;
- eligibility performed-unknown / performed-adverse / not-performed / not-applicable;
- execution failure versus completed not-checkable;
- distributed partial evidence with aggregation unresolved;
- independently sufficient alternatives versus jointly sufficient evidence;
- policy-only counterfactual with measurement fixed.

## Weak controls frozen before candidate exposure

1. `generic_abstention_weak_control`
   - collapses non-success into a generic abstention and discards evidence/state.
   - expected to fail distinguishability, evidence retention, and execution separation.

2. `terminal_reason_only_weak_control`
   - adds differentiated terminal reasons but no retained participation/assessment/causal ledger.
   - expected to pass basic cause labeling but fail evidence retention, trust/eligibility separation, and causal-basis reconstruction.

If either weak control unexpectedly clears every promotion-relevant methodology gate, the apparatus is insufficiently discriminating and RC0 must be `INCONCLUSIVE` for architecture selection.

## Frozen invariants

1. Upstream nomination-role mutation alone must not change claim/passage semantic measurement.
2. Source metadata mutation alone must not rewrite an already-frozen semantic measurement.
3. Downstream/named policy mutation may change participation or conclusion but must not mutate the prior measurement/evidence facts.
4. Evidence removed from the deciding basis remains retained and identifiable as non-deciding.
5. Missing proposition-specific assessment state is not silently converted to performed-positive/eligible state.
6. Performed-unknown, performed-adverse, not-performed, not-applicable, and failed execution states remain distinct when the distinction is material.
7. A failed execution does not emit a subject-matter not-checkable verdict as a substitute for failure.
8. Causal attribution preserves independent sufficiency, joint sufficiency, and residual/non-deciding evidence rather than selecting an arbitrary winner.
9. Unvalidated multi-passage composition may remain unresolved; preserving evidence does not authorize inventing aggregation semantics.
10. Replay of frozen inputs through the same candidate adapter is deterministic at the evaluator-observation surface.

## Frozen falsifiers / negative outcomes

RC0 architecture support is not available if any of the following occurs:

- the evaluator cannot reject both weak controls for the intended reasons;
- a sophisticated candidate passes only because the adapter manufactures state not actually recoverable from that methodology;
- materially different causes remain indistinguishable at the candidate's legitimate observable surface;
- required missing state becomes a positive/eligible default;
- excluded evidence must be erased to obtain the terminal result;
- semantic measurements change under pure upstream-role or policy-only mutation;
- a unique causal winner is claimed where removal interventions support multiple bases;
- execution failure is represented as epistemic abstention;
- candidate comparison requires modifying the frozen fixture/evaluator after exposure;
- candidate evaluation requires semantic gold or model-quality assumptions not established by this apparatus.

## Exclusions and why

- No NLI threshold tuning: representation/policy architecture is the variable, not model calibration.
- No new aggregation semantics: RC0 may diagnose an unresolved composition boundary but cannot invent the answer.
- No source-authority gold: source class is retained as an upstream fact; proposition authority/eligibility is not assumed from it.
- No Decision Engine policy: downstream operational policy is outside CAL epistemic-methodology ownership.
- No old-v2 expectations: no v2 implementation detail was used to construct these gates or fixtures.

## Apparatus deviation recorded before freeze

A local `git clone` attempt from the execution container failed because the container could not resolve `github.com`. Live repository inspection and mutation therefore used the authenticated GitHub connector/API rather than a local clone. This is an environment/tool-access deviation, not a CAL scientific failure. It does not alter fixture bytes or evaluator logic; hosted CI is the execution receipt for repository tests.

## Phase 2 authorization boundary

After this freeze commit is created, Phase 2 may inspect the historical `feat/v2-epistemic-pipeline` branch as **research material only** and extract individual mechanisms. It may not treat that branch as a production merge candidate or alter these frozen Phase 1 gates around its observed behavior.
