# CAL Epistemic Methodology RC0B — Final Research Report

## OBSERVED

Production baseline: `e90f301cf6ca02c0c77b6e88c3b08f8b93b9a36a`.

Immutable CAL v0.5.0: `5533bbcf27a3ee3a7d901f7dfc44c241bc558e2c`.

Immutable Contract C 1.0.0: `5fe55f9ed5d0ee9f026ca1b077e9d70ce0487ea1`.

Draft Research PR: https://github.com/camerontjs-dot/claim-audit-lab/pull/31

Fresh research branch: `research/epistemic-methodology-rc0b-fresh-20260829`.

Phase-1 aperture manifest commit: `b1e63aa489dbb204c5969fc11338374b2c65b7a0`; post-freeze aperture-audit update: `caee38289cd71393bfd1b0d430af67f3aecc4f25`.

Corrected evaluator freeze commit: `5d880110e39d0450af346fea91074eebaa2c2f96`.

Frozen blobs:
- evaluator spec: `792563efc4d04a088abf6016fb88d8b8073aea22`;
- cases: `e2b8a317cb8c6a0840199002957d6e6bf05531b6`;
- executable evaluator: `6f4969f9d5dd1252fbb8826b2ff0911e5a3b9cd4`;
- freeze record after completion: `90e459fd6e7e31a732f29359b530c83bebfac33c`.

The pre-freeze firewall held. No candidate result, candidate gate vector, historical-v2 mechanism detail, prior architecture conclusion, or external epistemic-abstention synthesis entered before freeze.

Current production directly preserves retrieval, admitted entailment rows, aggregate support signal, fired rules, verdict, and source metadata. It keeps measured evidence in the entailment trace even when later suppression prevents deciding participation. It does not provide a first-class typed final participation ledger, generic proposition-assessment execution/value state, or explicit unresolved-aggregation state in v1 `AuditTrace`.

Released Contract C 1.0.0 separately represents result-set/proposition execution and generic assessment states, but its generic assessment vocabulary has no performed-positive value.

## CORRECTED CONTROLS

Evidence-presence ladder:
- zero passages, available-none-admitted, semantic-silent, weak-below-signal, supportive, contradictory, and mixed are all frozen as distinct test conditions;
- the evaluator does not require a unique public verdict per row;
- it requires enough retained state to distinguish materially different causes.

Nomination-role mutation:
- fixed claim/passage/text/measurement;
- support versus counter nomination must leave semantic measurement invariant.

Trust mutation:
- primary, secondary, background are distinct source facts;
- none is itself a performed proposition-specific eligibility assessment.

Assessment ladder:
- performed-positive, performed-adverse, performed-unknown, not-performed, not-applicable, and failed are frozen as distinct states.

Temporal / authority:
- temporal not-performed, performed-unknown, performed-adverse, not-applicable;
- authority/applicability not-performed and performed-unknown;
- no positive authority judgment is invented.

Distributed evidence:
- both partial passages are retained;
- aggregation remains `unresolved`;
- no composition rule is invented.

Execution:
- completed-assessed, completed-not-checkable, assessment failure, incomplete execution, and parser/rule/model failure remain distinct.

Strong policy counterfactual:
- evidence hash fixed;
- semantic-measurement hash fixed;
- `ALLOW_PRIMARY_OR_SECONDARY` versus `PRIMARY_ONLY`;
- a secondary contradictory item with performed-positive eligibility changes from deciding/`contradicted` to residual/`not_checkable`.

Actual causal-removal replay:
- with the secondary contradictory item deciding under `ALLOW_PRIMARY_OR_SECONDARY`, baseline = `contradicted`;
- remove that item and rerun: terminal = `not_checkable`;
- therefore the item is replay-derived necessary for that terminal result in the frozen one-item case;
- no exact causal form is emitted where replay cannot establish it.

## WEAK-CONTROL DISCRIMINATION

Equivalent command: `python docs/research/rc0b_evaluator.py --self-test`.

Observed:
- W1 generic abstention fails A/D/E;
- W2 terminal-reason taxonomy without typed state fails D/E;
- W3 trust shortcut fails E/J;
- W4 causal-basis echoer fails G;
- W5 policy-id-only logger fails H.

No weak control clears the architecture gate.

## CANDIDATE COMPARISON

Candidate A: current production observable state, identity `e90f301cf6ca02c0c77b6e88c3b08f8b93b9a36a`.

Frozen A-K result:
- A PASS;
- B PASS;
- C PASS;
- D FAIL;
- E FAIL;
- F PASS at released Contract-C boundary;
- G PASS only by explicitly reporting exact causal structure unavailable;
- H FAIL;
- I PASS;
- J FAIL;
- K FAIL.

The failures are not model-quality or threshold failures. They are representational:
- no typed deciding/residual/excluded/unresolved participation family;
- no full assessment-execution/value ladder;
- no strong switchable named-policy counterfactual surface;
- trust source fact is not paired with separate explicit proposition-assessment state;
- unresolved distributed aggregation is not first-class.

Candidate B: bounded additive state/receipt, research identity `41d0a34b51c411cf32dde5d7f53969ec374123d0`.

Frozen A-K result: PASS on A, B, C, D, E, F, G, H, I, J, K.

Candidate B changes no semantic measurement. It adds only:
- explicit assessment execution/value;
- explicit participation;
- named policy effect;
- explicit execution state;
- unresolved aggregation state;
- replay-derived causal basis when available.

No partial/full staged candidate was built after Candidate B cleared all frozen properties. The stopping rule applies: additional implementation would add no discriminating evidence.

Post-freeze inspection of historical-v2 mechanisms found explicit removals and per-role participation useful as implementation hypotheses, but no frozen property uniquely required that broader staged structure.

## INFERENCE

The minimum required epistemic state is:

1. retained evidence identity plus immutable semantic measurement;
2. source facts retained separately from proposition-specific assessment state;
3. explicit assessment execution/value when an assessment is relevant;
4. explicit participation: deciding, residual/non-deciding, excluded, unresolved;
5. explicit named policy identity/effect;
6. explicit execution state separate from subject-matter conclusion;
7. unresolved aggregation where composition semantics are absent;
8. causal basis only when replay establishes it, otherwise unavailable.

This minimum state can be represented around current CAL semantic measurements and rule behavior with a bounded additive receipt/replay mechanism.

The corrected evaluator did not identify any required state that is necessarily destroyed by current semantic measurement, forced into observational equivalence beyond repair, or obtainable only through a fuller staged execution architecture.

Some facts must be recorded when they occur, especially assessment execution/failure and outer execution status. That is bounded receipt capture, not evidence that every epistemic distinction requires its own internal pipeline stage.

## FALSIFIED ALTERNATIVES

- One generic abstention state: falsified by weak control W1 and current released distinctions.
- Richer terminal reasons alone: falsified by W2.
- `primary = eligible` / `secondary-background = adverse` as proposition assessment: falsified by W3.
- Declared causal basis without removal replay: falsified by W4.
- Policy logging without derived behavior change: falsified by W5.
- Current production observable state alone is sufficient: falsified by D/E/H/J/K failures.
- A broad staged rewrite is presently necessary: not supported; Candidate B clears the corrected evaluator without it.
- Unsupported distributed-evidence composition: falsified by K.

## HYPOTHESES STILL LIVE

- The exact production factoring of a future bounded receipt is unresolved.
- Some assessment ownership, especially proposition authority/applicability, may belong outside CAL.
- A future semantic experiment could justify additional aggregation operators, but RC0B does not.
- A later implementation test may show a narrower or differently factored receipt than Candidate B.

## UNKNOWNS

- Which explicit assessor, if any, owns proposition authority/applicability for each use case.
- Whether every future real-world causal form can be replayed cheaply enough for routine emission.
- Whether a production Contract-C successor should add performed-positive or leave that state in a CAL-internal/producer convention.
- Exact operational placement of outer execution receipts.

## ARCHITECTURE DISPOSITION

**MINIMAL STATE/POLICY CHANGE SUPPORTED**

Supported bounds:
- preserve current semantic measurement behavior;
- do not promote historical-v2;
- do not require a five-stage rewrite;
- add only typed state/receipt and replay necessary to preserve the frozen distinctions;
- keep trust/source metadata separate from proposition assessment;
- make policy identity/effect explicit;
- emit causal basis only when intervention-supported.

## CONTRACT-C COMPATIBILITY

Released Contract C 1.0.0 normative spec blob: `8c15f2e5f4047ccd17e204fb23aee1168781b9d5`.

| Required state | Contract C 1.0.0 mapping |
| --- | --- |
| retained contributions | explicitly representable |
| basis vs residual/non-deciding | explicitly representable |
| execution completed/failed/incomplete | explicitly representable |
| completed assessed vs completed not_checkable | explicitly representable |
| performed-adverse | explicitly representable |
| performed-unknown | explicitly representable |
| not-performed | explicitly representable |
| not-applicable | explicitly representable |
| failed assessment | explicitly representable |
| performed-positive | **not explicitly representable** in generic assessment vocabulary |
| temporal state | explicitly representable in `temporal_applicability` except performed-positive |
| proposition authority/applicability | ownership/schema slot unresolved; not a demonstrated generic 1.0.0 stage |
| causal multiplicity | explicitly representable for the released four causal forms |
| execution failure vs epistemic non-decision | explicitly representable |
| named CAL policy identity | explicitly representable as hashed canonical producer policy |
| unresolved aggregation | representable by producer convention/conclusion state only where compatible; no generic dedicated aggregation-state field is specified |

No Contract C change is authorized. The performed-positive mismatch supports only a later contract experiment if a production producer requires that exact state at the handoff.

## INFORMATION-APERTURE RESULT

**PASS**

The fresh branch was created from exact live production `main`. The pre-existing branch named `research/epistemic-methodology-rc0b` was not read or reused.

The corrected evaluator was durably frozen at `5d880110e39d0450af346fea91074eebaa2c2f96` before PR #28, RC0 candidate records, or historical-v2 mechanism details were retrieved.

The independent external-methodology synthesis was not supplied and was not retrieved.

## NON-CLAIMS

RC0B does not authorize:
- merging PR #31;
- production CAL changes;
- CAL v2;
- merging `feat/v2-epistemic-pipeline`;
- Contract B or Contract C changes;
- Evidence Bundler or Decision Engine changes;
- threshold/model changes;
- a release/version change;
- new multi-passage composition semantics.

RC0B does not claim Candidate B is production-ready. It establishes only that the corrected behavioral requirements do not presently justify stronger staging.

## NEXT SMALLEST TEST

A fresh promotion/implementation experiment should test only a bounded typed receipt/replay mechanism around current CAL semantics, with no Contract-C change initially.

The smallest discriminating production-facing question is:

Can a real v1 research-only producer emit the RC0B minimum state from exact Contract-B input, frozen v1 measurements, explicit policy identity, assessment receipts, and failure capture while leaving every existing production verdict and semantic measurement byte-stable?

If yes, no broader architecture change is justified. If no, the failure must identify the exact state that cannot be observed or reconstructed and only that state may justify stronger decomposition.

## TEST COMMANDS / EXECUTION RECEIPTS

Locally executed research-equivalent checks:
- `python docs/research/rc0b_evaluator.py --self-test` logic: all five weak controls rejected.
- Candidate A evaluated against frozen A-K vector: does not clear.
- Candidate B evaluated against frozen A-K vector: clears all eleven properties.
- one-at-a-time causal removal replay: contradictory secondary item removal changes `contradicted -> not_checkable`.
- strong policy counterfactual: identical evidence/measurement; policy changes participation `deciding -> residual` and terminal `contradicted -> not_checkable`.

No production suite result is used as evidence for the architecture disposition. Hosted CI status, if available, is recorded separately and cannot repair or alter frozen scientific expectations.
