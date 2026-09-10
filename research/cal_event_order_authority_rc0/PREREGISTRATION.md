# CAL Event-Ordering Authority RC0 Preregistration

## Class

Draft Research Infrastructure / semantic-authority experiment. No production `src/**` mutation, release, merge, tag, promotion, Contract B/C amendment, Decision Engine change, Contract E change, or operational authorization.

## Exact parent

- parent CAL Measurement Envelope RC0 final head: `6cb12e81698b21d3bed82f0f31d592ab6e5f1500`
- parent Draft Research Infrastructure PR: #95
- event-order measurement authority: RC7F-C `e8d33913db66ad21027dffdf731d50f7a0977c8f`
- event-order measurement blob: `3e29b0e2ec5d9ba2d873d1584e76635147e421aa`
- frozen RC8J authority evaluator: `8e75c6782bb95c3763d06230b9c5df2b6af44054`
- frozen RC8J implementation blob: `f55156e43e0c1b4a7868bc8339585b8892edda38`

The parent envelope established only information-preserving measurement transport. Event-order receipts in the parent remain `authority_state=NOT_EVALUATED`.

## Research question

Can an explicit RC7F-C event-order measurement be completed into an independently source-grounded temporal atom and then evaluated by the exact frozen RC8J authority machinery such that caller-stipulated or mutated temporal semantics cannot become `WARRANTED` merely by supplying internally consistent field warrants?

This is an event-atom authority experiment. It does not yet establish proposition-relative temporal support/refutation or root composition.

## Alternative explanation to discriminate

A green RC8J result alone could be misleading because RC8J deliberately does not parse source language. If a caller fabricates a proposal and matching field-warrant values/spans, RC8J may accept their internal consistency even when the proposal contradicts the source. Therefore the experiment must first demonstrate that weak seam and then test an independent source-to-atom completion boundary in front of RC8J.

## Weak control

For a direct source such as:

`Alice reviewed dossier before Bob archived dossier.`

RC7F-C should measure `BEFORE`.

A deliberately weak constructor will mutate that proposal to `AFTER`, build matching caller-stipulated field warrants over a broad valid source span, and pass the internally consistent object to frozen RC8J.

Expected weak-control result: RC8J may return `WARRANTED / ALL_REQUIRED_WARRANT_ESTABLISHED`. If it does not, the setup is still informative, but the candidate must not claim to have closed a demonstrated laundering seam.

The weak constructor is never a candidate architecture.

## Candidate boundary

The candidate must independently reconstruct a bounded direct event-order atom from the exact admitted source text before RC8J evaluation. It must not derive event fields by copying RC7F-C proposal values into field warrants.

### Candidate accepted grammar

Only a deliberately narrow, direct narrator-level form is in scope:

`<subject> <past-event-verb> <object> before|after <subject> <past-event-verb> <object>.`

or a direct negative event using:

`<subject> did not <base-event-verb> <object>`

The vocabulary is bounded to the existing RC7F-C event predicates. One or two token subjects and one-to-six token objects are permitted. Only a terminal period is allowed as punctuation. Reporting prefixes/wrappers, parentheticals, quotes, additional clauses, multiple ordering cues, unsupported predicates, and malformed/ambiguous structures must fail closed before authority.

### Independently grounded required fields

The candidate reconstructs these fields from source tokens/spans:

- `left_subject`
- `left_predicate`
- `left_object`
- `left_polarity`
- `temporal_relation`
- `right_subject`
- `right_predicate`
- `right_object`
- `right_polarity`

Each field receives an exact support span derived from the source reconstruction. For positive polarity, the affirmative event-verb span is the bounded support for positive polarity; for negative polarity, the exact `did not` span supports negative polarity.

The candidate then requires exact semantic agreement between the independently reconstructed atom and the RC7F-C measurement proposal. Any disagreement is a non-warranted completion failure and RC8J is not invoked as a repair mechanism.

### RC8J case

Only after successful independent completion may the candidate construct an RC8J case with:

- exact source/bundle/passage/claim/atom identity;
- admitted-passage span;
- proposal family `event_ordering`;
- direct assertion state established only by successful accepted-grammar completion;
- operator domain `event_ordering`;
- applicability `applicable`;
- governed span equal to the exact direct source sentence;
- jurisdiction exactly the nine fields above;
- exact field warrants and support spans from independent completion;
- no extra modifiers;
- composition not required for one atom;
- aperture not required for atom authority.

`composition required=false` and `aperture required=false` mean only that neither is required to establish whether this one already-admitted direct temporal atom is source-grounded. They do not establish proposition completeness or permit later decision without composition.

## Preregistered positive controls

At minimum:

1. direct positive `BEFORE`;
2. direct positive `AFTER`;
3. direct negative left event;
4. direct negative right event;
5. two-token subject control.

Every positive control must:

- produce RC7F-C `CLAIMED`;
- independently complete to exactly the same typed event semantics;
- have all required support spans inside the admitted passage;
- receive exact frozen RC8J `WARRANTED / ALL_REQUIRED_WARRANT_ESTABLISHED`.

## Preregistered falsifiers / mutations

The candidate is falsified if any of the following can enter as `WARRANTED`:

1. RC7F-C `BEFORE -> AFTER` proposal mutation under unchanged source;
2. left-subject proposal mutation;
3. right-object proposal mutation;
4. left-polarity proposal mutation;
5. right-polarity proposal mutation;
6. stale cue-span mutation;
7. left/right event swap without matching source;
8. reporting-prefix source that RC7F-C still measures but the direct-assertion candidate should reject;
9. additional-clause or unsupported punctuation wrapper admitted as direct assertion;
10. foreign source identity after atom construction;
11. foreign bundle identity after atom construction;
12. foreign passage identity after atom construction;
13. foreign claim identity after atom construction;
14. atom-ID substitution after atom construction;
15. field-support span moved outside the admitted passage;
16. field-warrant value changed while the proposal remains fixed;
17. operator domain changed away from `event_ordering`;
18. evidence admission changed to false.

For measurement-proposal mutations 1-7, independent completion must refuse before a deciding authority result is available. For identity/jurisdiction mutations 10-18, exact frozen RC8J must reject or remain unresolved as appropriate.

## Evaluator invariants

- Frozen RC7F-C and RC8J code identities are checked before execution.
- Weak control and candidate results are reported separately.
- An execution failure is not a scientific pass.
- Every unsafe `WARRANTED` candidate mutation is terminal falsification.
- Candidate repairs after a decisive mutation failure require a successor, not silent recounting.
- Released CAL v0.5.0 has zero causal role.

## Bounded success interpretation

If all candidate controls pass, the supported claim is only:

Within the accepted direct event-order grammar and exact frozen RC7F-C/RC8J dependencies, an independent source-to-atom completion boundary can prevent tested caller-stipulated temporal-semantic mutations from entering RC8J as warranted event-order atoms, while valid directly asserted event-order atoms can receive bounded semantic authority.

This does not establish arbitrary-language event extraction, general assertion/scope recognition, proposition-relative temporal entailment, evidence completeness, cross-passage temporal reasoning, root composition, production trust/key management, production CAL architecture, release, merge or promotion.
