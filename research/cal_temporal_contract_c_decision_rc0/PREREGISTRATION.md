# CAL Temporal Contract C / Decision RC0 — Preregistration

## Classification

Draft Research Infrastructure / downstream conformance experiment.

This experiment does not amend Contract C, Decision Engine, Contract D, CAL production code, or operational authorization semantics. No merge, release, tag, promotion, Contract E call, or external mutation is authorized.

## Exact starting state

- parent documentation head: `1fe223979a866ec10428ff696bb373739728d461`
- terminal Phase-3 evidence head: `ba5ac7a6f3438b054803ea50fee0d62d2b3fb3ca`
- Phase-3 temporal relation candidate freeze: `94ea0c7531aeb852520f34bd56393b63a4b5ac75`
- Contract C 1.0 release authority: `5fe55f9ed5d0ee9f026ca1b077e9d70ce0487ea1`
- Contract C validator blob: `9c75ccfbf2223578a8d1a7bf0c39673b394fbea4`
- live maintained Decision Engine main at preregistration: `358c2bb20f490bf25e808434394b26a70a16a123`
- Contract D 1.0 release authority: `298a1a0f7b7b6d7712e11200d04faec3e1ca169b`

The Decision Engine commit is one maintenance commit after the previous integration pin `a4425f8...`; its commit record states that the change pins a Contract-C authority-root regression and does not change Decision policy/runtime semantics. The exact live commit above is nevertheless the authority for this experiment.

## Research questions

1. Can the unchanged Contract C 1.0 schema and reference validator carry the bounded Phase-3 temporal `supported`, `contradicted`, and mixed-conflict `not_checkable` outcomes without semantic-family-specific schema changes?
2. Can a bounded unresolved temporal abstention be represented without lying about evidence-channel polarity?
3. Does live maintained Decision Engine consume valid temporal Contract C strictly from the existing Contract C execution/completion/verdict surface, producing the same `clear` / `hold` semantics as for prior strict-comparison outputs?
4. Does exact-version validation reject attempts to add temporal-family fields to Contract-C-owned objects or encode categorical temporal relations into the numeric/null measurement value?
5. Does changing producer-owned semantic-family policy metadata, while producing otherwise equivalent valid Contract C terminal state, leave Decision disposition invariant?

## Candidate projection rules

The candidate may project only exact Phase-3 `TemporalProposition`, `TemporalRelationRecord`, and `TemporalConclusion` objects.

### Deciding relations

- `SUPPORTS` becomes a Contract C `support` contribution.
- `REFUTES` becomes a Contract C `counterevidence` contribution.
- A single deciding relation becomes a `single_necessary` causal contribution basis.
- A mixed support/refute abstention preserves both deciding contributions as a `jointly_sufficient` basis for the `not_checkable` conflict state.

### Unresolved / irrelevant relations

Contract C 1.0 has no neutral or unresolved evidence-contribution channel. The candidate MUST NOT mislabel `UNRESOLVED` or `IRRELEVANT` evidence as support or counterevidence.

For such an abstention the Contract C object may preserve the terminal state with a deterministic `state:` basis member and `reported_verdict=not_checkable`, but the research projection receipt must explicitly report the omitted evidence-linked relation IDs. Such a projection is classified as `VALID_WITH_PROVENANCE_COMPRESSION`, not lossless.

### Measurement

The categorical temporal relation is not a finite numeric aggregate. The candidate therefore sets Contract C `measurement` to `null`. It must not stringify `BEFORE`, `AFTER`, `SUPPORTS`, or `REFUTES` into `measurement.value`.

### Assessment slots

The Contract C 1.0 generic assessment slots are emitted as `not_performed`. This experiment does not equate the Phase-3 source-completion/authority machinery with those historical Contract C stage slots without a separately justified mapping.

## Preregistered outcomes

### Full downstream support

`SUPPORTED_WITH_BOUNDS` requires:

- unchanged Contract C exact validation PASS for supported, contradicted, mixed-conflict not-checkable, and unresolved not-checkable shapes;
- supported/contradicted/mixed projections preserve every deciding evidence relation as a correctly polarized contribution;
- unresolved projection explicitly reports its provenance compression rather than fabricating a channel;
- live Decision Engine outputs `clear` only for supported assessed Contract C;
- contradicted and both not-checkable cases produce `hold`;
- Decision output remains invariant to producer-owned temporal-vs-control policy metadata when terminal Contract C semantics are otherwise the same;
- illegal Contract C semantic-family field is rejected;
- string-valued temporal measurement is rejected;
- wrong whole-object digest, wrong Contract-B binding, and wrong Decision target text binding fail closed;
- no Contract E or Authorization occurs.

### Partial / gap outcome

`SUPPORTED_CONCLUSION_HANDOFF_WITH_PROVENANCE_GAP` if Contract C and Decision safely carry terminal temporal conclusions, but one or more bounded temporal provenance states cannot be represented without information loss.

This is expected to be the likely disposition if unresolved/irrelevant evidence cannot be retained with truthful channel semantics.

### Falsified

`FALSIFIED_TEMPORAL_CONTRACT_C_DECISION_HANDOFF` if unchanged Contract C or maintained Decision cannot safely carry a valid deciding temporal conclusion through the exact released boundaries.

### Apparatus invalid

Dependency, checkout, environment, test-index, canonicalization, or harness failures are not semantic evidence and must be preserved separately.

## Boundaries

The Contract-B index in this experiment is a validator conformance projection only. It does not prove Evidence Bundler retrieval, Contract B production, evidence completeness, or source legitimacy.

Contract D remains Decision output only. No operational Authorization is evaluated.
