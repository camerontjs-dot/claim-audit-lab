# CAL Event-Ordering Proposition Relation RC0 Preregistration

## Class

Draft Research Infrastructure / authority-to-conclusion experiment. No production `src/**` mutation, release, merge, tag, promotion, Contract B/C amendment, Decision Engine change, Contract E change, or operational authorization.

## Exact parent

- parent Event-Ordering Authority RC0 head: `3a4b5f24f813843eae3857ed3444fb12b1cb8182`
- parent Draft Research Infrastructure PR: #96
- parent event-order candidate freeze: `634837fe368accbd9add2c9483dfff6722f5dfc7`
- exact frozen RC7F-C measurement: `e8d33913db66ad21027dffdf731d50f7a0977c8f`
- exact frozen RC8J: `8e75c6782bb95c3763d06230b9c5df2b6af44054`

The parent established only a bounded event-order atom authority path. It did **not** establish proposition-relative temporal support/refutation.

## Research question

Can an exact authenticated RC8J warrant for a source-grounded event-order atom and a separately authenticated exact temporal proposition binding be consumed to derive a proposition-relative categorical relation and scoreless fail-closed conclusion without reopening either:

1. stale atom-warrant replay; or
2. same-claim proposition substitution?

## Alternative explanations to discriminate

A passing same-direction example alone would not establish the architecture. At least three weaker explanations must be ruled out:

- the relation could be copied from the measurement rather than derived relative to the proposition;
- claim ID alone could be treated as proposition identity, allowing same-ID proposition substitution to flip the conclusion;
- an authenticated warrant could be replayed against a changed event atom/case if the receipt does not bind the exact authority-relevant payload.

The experiment therefore includes weak controls for claim-ID-only proposition use and stale atom-warrant replay, plus authenticated candidates that must refuse both.

## Candidate temporal proposition

A bounded `TemporalProposition` contains:

- exact `claim_id` and exact original `claim_text`;
- family `event_ordering`;
- exact left event: `subject`, `predicate`, `object`, `polarity`;
- exact relation: `BEFORE | AFTER`;
- exact right event with the same fields.

The authenticated proposition receipt binds the exact semantic projection plus SHA-256 of exact claim text. Semantic equivalence is **not** canonicalized into the same receipt. A swapped inverse proposition such as `B AFTER A` requires its own exact receipt even though the relation operator may later derive it as logically equivalent to `A BEFORE B`.

## Candidate atom warrant

The portable event warrant binds the exact RC8J authority-relevant case projection used by the parent event-authority path, including exact source/bundle/passage/claim/atom identity, proposal fields, field warrants, assertion/operator state, composition and aperture state.

Issuance requires a fresh exact frozen RC8J observation of `WARRANTED / ALL_REQUIRED_WARRANT_ESTABLISHED`. The consumer verifies the authenticated warrant and exact case digest without rerunning RC8J.

The bounded research authentication mechanism is HMAC-SHA-256 with separate atom-warrant and proposition-binding keys. This is not a production key-management/signing architecture.

## Relation semantics under test

Only affirmative event pairs may produce deciding temporal relations in this RC.

Let proposition events be `P_left`, `P_right` and atom events be `A_left`, `A_right`.

### Exact same ordered event pair

- same `BEFORE|AFTER` relation -> `SUPPORTS`
- opposite relation -> `REFUTES`

### Exact swapped event pair

Because `A BEFORE B` is equivalent to `B AFTER A` for the bounded strict temporal ordering asserted here:

- swapped pair + inverse temporal relation -> `SUPPORTS`
- swapped pair + same temporal relation -> `REFUTES`

### Different event identities

- -> `IRRELEVANT`, non-deciding

### Any negative event polarity

- -> `UNRESOLVED`, non-deciding

Negative event atoms may already be source-grounded and warranted by the parent authority experiment. They are deliberately not allowed to decide here because constructions such as `A did not X before B Y` can have negation/scope readings not established by the bounded event-order measurement. This separates atom authority from proposition-relative logical sufficiency.

## Scoreless composition

Relations are canonicalized by relation identity before composition.

- any `UNRESOLVED` relation -> `abstained / verdict=null / unresolved_categorical_relation`;
- both warranted `SUPPORTS` and warranted `REFUTES` -> `abstained / verdict=null / mixed_categorical_relations`;
- one or more warranted `SUPPORTS`, no refute/unresolved -> `decided / supported / categorical_support`;
- one or more warranted `REFUTES`, no support/unresolved -> `decided / contradicted / categorical_refutation`;
- only `IRRELEVANT` -> `abstained / verdict=null / no_deciding_categorical_relation`.

No score, confidence, threshold, vote count, reader count, retrieval rank or measurement probability enters this table.

## Preregistered controls

### Positive / relation controls

1. exact same events + same direction -> `SUPPORTS -> supported`;
2. exact same events + opposite direction -> `REFUTES -> contradicted`;
3. swapped event pair + inverse direction -> `SUPPORTS -> supported`;
4. swapped event pair + same direction -> `REFUTES -> contradicted`;
5. different event pair -> `IRRELEVANT -> abstained`;
6. warranted negative-event atom -> `UNRESOLVED -> abstained`.

### Proposition binding controls

7. weak claim-ID-only consumer: same warranted atom, same `claim_id`, proposition direction mutated `BEFORE -> AFTER` must change the derived relation, demonstrating the seam;
8. authenticated stale proposition receipt from `BEFORE` replayed against same-ID `AFTER` proposition -> refused;
9. same-ID left-event substitution under stale proposition receipt -> refused;
10. claim-text mutation under stale proposition receipt -> refused;
11. wrong proposition key / MAC mutation -> refused;
12. swapped-inverse proposition under stale receipt -> refused, but separately issued exact swapped-inverse receipt -> accepted and may derive `SUPPORTS`.

### Atom-warrant controls

13. valid event atom/case -> portable warrant issuance succeeds;
14. mutate warranted case temporal relation with stale warrant -> refused by subject digest;
15. mutate field warrant/proposal value with stale warrant -> refused;
16. claim/atom/source identity substitution under stale warrant -> refused;
17. wrong warrant key / MAC mutation -> refused;
18. producer attempt to issue a warrant for a non-warranted mutated case -> refused.

### Composition / interface controls

19. support + refute -> mixed abstention;
20. reverse support/refute input order -> identical conclusion and basis relation set;
21. support + irrelevant -> supported;
22. support + unresolved -> unresolved abstention;
23. caller attempts `score`, `confidence`, `threshold`, `channel`, `relation_hint` on proposition/relation API -> rejected or absent from interface;
24. changing diagnostic metadata that is outside the authenticated authority/proposition semantic projections may not change relation/conclusion.

## Hard falsifiers

The candidate is falsified if:

- a stale authenticated atom warrant verifies against a changed authority-relevant event case;
- a stale authenticated proposition receipt verifies against changed temporal proposition semantics or exact claim text;
- a non-`WARRANTED` atom produces a deciding relation;
- a negative-polarity event atom produces a deciding relation in this RC;
- a different event pair produces support/refutation;
- support/refutation composition depends on input order;
- a scalar/confidence/vote can change the terminal conclusion;
- an unauthenticated caller-supplied relation or polarity hint can produce a deciding conclusion.

## Bounded success interpretation

A pass would establish only that, inside the bounded direct affirmative event-order fragment inherited from the parent authority candidate, exact authenticated event-atom authority and exact authenticated temporal-proposition identity can support proposition-relative scoreless categorical relation/composition while the tested stale-warrant and proposition-substitution attacks fail closed.

It would not establish arbitrary temporal language, negation scope, cross-passage temporal inference, event coreference, transitivity, evidence completeness, root composition, Contract C temporal projection, learned/NLI participation, production cryptography, production CAL architecture, merge, release or promotion.
