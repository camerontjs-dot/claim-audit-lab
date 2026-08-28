# Contract C RC2-A — Real CAL Boundary + Semantic Minimality

**Class:** Draft Research PR  
**Production impact:** none  
**Producer gate only:** SATISFIED / FAILED / INCONCLUSIVE

## Decision

Determine whether the current production CAL boundary can support a frozen, semantically justified Contract-C RC2 candidate that may be handed unchanged to a clean-room independent consumer.

This experiment does not decide Contract-C production promotion or versioning.

## Pinned state verified before execution

- CAL production: `33a928db97316a3652d57df9cafb8ca240305233`
- Evidence Bundler production: `c8189c31adbab11729c31430c2070126224a2d42`
- Apparatus production: `c314e53bd91c0736aa4370a364673b069aceb43e`
- Contract B: `1.2.0`
- CAL RC1 PR #15: `c7f4ad6949967538c35386ddc2a3c6c7f245c53c`
- Apparatus RC1 PR #11: `ba4ab7462fda440698f3e853b1ec9385aa2c1725`

RC1 is predecessor evidence and remains frozen. This branch starts from CAL production `main`.

## Primary claim

> A real current-production CAL execution can expose enough legitimate boundary state to construct a decision-agnostic semantic result bound exactly to its validated Contract-B input, while excluding destination policy and unnecessary implementation telemetry and preserving every semantic distinction demonstrated necessary by prior experiments.

## Competing explanations

1. current CAL boundary already exposes everything necessary;
2. necessary state is split across legitimate boundary objects;
3. CAL lacks required attributable state;
4. candidate semantics retain unnecessary information;
5. RC1 bloat mainly came from run/proposition duplication;
6. apparent minimality failure was mainly a byte-serialization artifact.

No explanation is preferred in the apparatus.

## Real-boundary fixture

Use the existing production EB fixture `tests/fixtures/scaffold-run-mixed-formats`, which contains three frozen extracted propositions (`clm-md`, `clm-txt`, `clm-pdf`) over distinct frozen source/passages.

Generate the B artifact with production EB `build_retrieval_bundle(...)` at the pinned SHA. The B artifact must pass the real CAL fail-closed loader before any Contract-C projection occurs.

The decisive capture must record:

- exact Contract-B file bytes/hashes and version;
- manifest bundle ID and bundle hash obtained from the validated manifest;
- canonical source/passage/proposition identities and proposition text hashes;
- CAL code SHA and distribution version;
- exact CAL audit/rules/model/operator identities legitimately present at the boundary;
- production AuditTrace(s) and structured report/writeback state where produced;
- validated Contract-B intake state available immediately before audit;
- post-audit CAL state used by the RC2 projection.

Never derive B identity from an AuditTrace, filename, fixture label, array index, or destination context.

## Semantic candidate rule

RC2 is derived from obligations, not copied from RC1 C1.

Run/result-set state may retain only demonstrated run-level facts such as exact B binding, CAL/config/operator identity, execution/deviation state and integrity identity. Proposition state may retain only demonstrated proposition identity, retained semantic evidence/contribution references, attributable assessment state, conclusion/exact basis/residual state, execution state, and conditional reassessment lineage.

Raw retrieval scores, logits, debug prose, internal paths, display summaries, feature ordering and destination interpretation are excluded unless a frozen falsifier demonstrates semantic necessity.

## Semantic-minimality classification

Every candidate path receives one primary classification:

- semantic meaning attributable to CAL;
- exact provenance / identity / reconstruction;
- preregistered consumer obligation;
- execution / failure / supersession interpretation;
- conditionally necessary;
- redundant / derivable;
- presentation convenience;
- implementation telemetry;
- unresolved.

No field survives merely because a validator requires it. No field is removed merely to reduce bytes.

## F2/F3 hypothesis

Test whether stable semantic relation outcome/identity can be represented using retained contribution/receipt state while raw scalar/intermediate telemetry remains private. The apparatus must allow F3 to survive, partially fold, reduce to measurement identity/type/outcome, or disappear as public state.

## Frozen falsifiers

The harness must preserve the prior RC1 distinctions and fail if RC2 collapses any of:

- same headline with different counterevidence;
- eligibility state;
- semantic-validity state;
- aperture/completeness state;
- temporal/applicability state;
- exact decision basis;
- non-deciding evidence;
- completed abstention vs assessment not performed;
- execution failure vs adverse subject finding;
- reassessment/supersession vs silent mutation;
- malformed reference/integrity failure.

It must also demonstrate:

- raw telemetry invariance where normalized semantic outcome is fixed;
- deterministic report derivation;
- Contract-C byte invariance under destination-policy changes.

## Semantic firewall controls

### Authorization non-equivalence

Hold exact RC2 bytes and substantive decision policy fixed. Change only downstream authority profile between delegated automatic action and named-human authorization. RC2 bytes must remain identical.

### Prediction non-equivalence

Hold exact RC2 bytes fixed. Change only an external future-outcome forecast/scenario. RC2 bytes must remain identical.

Contract C must not absorb expected utility, destination preference, risk tolerance, authority delegation, autonomy-envelope state, workflow routing, future-state simulation or causal/outcome prediction merely because downstream decision logic consumes them.

## Ablation record

For every field/substructure ablation record:

- exact removed path;
- semantic invariant affected;
- consumer behavior affected;
- report/reconstruction consequence;
- provenance consequence;
- whether failure is only a hard-coded harness expectation;
- final classification.

## Factoring and diagnostics

Explicitly test run-level factoring of B identity, CAL/config/operator identity and shared execution metadata. Detect duplicate canonical/derived counterevidence, summary, report text and embedded payloads. When both canonical and derived values exist, name the authority and test the invariant.

Compare C0, frozen RC1 C1 and RC2 using canonical bytes, structural field count, repeated-value count, run-level overhead, marginal proposition overhead and semantic assertion count where practical. These are diagnostics, not the gate.

## Gate

**SATISFIED** only if a genuine validated B -> production CAL execution yields enough legitimate attributable state to freeze an exact RC2 specification/profile and artifact set unchanged for Consumer B.

**FAILED** if the producer/representation claim is contradicted.

**INCONCLUSIVE** if the apparatus cannot discriminate.

## Hard stop

No production exporter, production audit semantic change, Contract-B change, Decision Engine production change, Contract-C version assignment, held-out pre-RC1 MainFrame negative-control run, or post-handoff profile change is permitted.
