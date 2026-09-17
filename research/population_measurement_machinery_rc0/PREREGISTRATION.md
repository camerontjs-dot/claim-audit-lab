# CAL Population Measurement Machinery RC0 — Preregistration

Date: 2026-09-17

Classification: Draft Research / Gate-1A measurement-machinery discrimination.

Parent: terminal population Gate-0 branch head `2cc293e170bfbfd4ad0c64534114e900e5512995`.
Qualified typed-contract authority remains exact Gate-0 head `3abb817e6d6aeea4498a8495e3b4d5b54f984be6`.

## Question

What measurement machinery can safely recover the narrow population-membership semantics from ordinary evidence text without laundering quantifiers, role language, temporal state, attribution, or neighboring semantic families into membership/subset authority?

The experiment also pressure-tests a representational assumption exposed by natural text: membership facts and subset facts commonly occur in different passages. Measurement therefore emits either a typed membership atom or a typed subset atom. Later composition may combine those atoms; Gate-1A does not hide both inside one passage-local authority object.

Candidate mechanisms:

1. bounded membership/subset grammar;
2. broad dependency/copular extraction using spaCy;
3. conservative hybrid routing.

## Claim-shape buckets

MUST_HANDLE:
- positive and negative entity membership;
- explicit member-of language;
- plural-class subset language;
- `all` and `every` universal subset forms;
- more than one entity/population binding.

DIAGNOSTIC:
- belongs-to / among / include wording;
- explicit `subset of`;
- `each`;
- role phrasing such as `serves as`.

FAIL_CLOSED:
- `some` / `most` mistaken for universal subset;
- `only` direction traps;
- class disjointness;
- association rather than membership;
- past or modal membership;
- reporting wrappers;
- join events;
- attribute-state neighbors;
- disjunction and multi-role scope.

## Acceptance rule

A machinery path is `QUALIFIABLE_FOR_GATE1B` only if every MUST_HANDLE case is exact, no FAIL_CLOSED case is claimed, any claimed DIAGNOSTIC is exact, replay is deterministic, metamorphic controls pass, and production `src/` is unchanged.

Diagnostic recall cannot compensate for an unsafe claim.

## Weak strategies

The frozen evaluator must reject:
- any-copula membership;
- plural copula = subset regardless of quantifier;
- negation erasure;
- past-membership = current-membership;
- reporting-wrapper erasure.

## Non-claims

This does not establish source-completion warrant, cross-passage membership inheritance, quantifier logic beyond the frozen subset forms, role ontology, temporal membership, production plugin behavior, Contract C/Decision behavior, merge, or release.
