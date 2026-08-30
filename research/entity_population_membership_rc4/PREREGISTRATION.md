# Entity / Population Scope and Membership RC4 — Preregistration

## Classification

Research Infrastructure / semantic-measurement discrimination experiment.

This experiment is stacked on RC3 accepted science head `eb4e3043f5b16e3d65e5635b9d7013f312d5daf8` and treats PR #45's terminal comment as predecessor evidence. It is not production authorization.

## Question

What is the smallest semantic authority required to preserve entity identity, class membership, population quantifier, group/member scope, role binding, subclass direction, `only` necessary-condition semantics, and temporal membership without manufacturing unsupported implications?

Competing explanations remain live:

1. incumbent NLI weakness;
2. model capacity / alternative NLI suffices;
3. categorical disagreement/abstention suffices;
4. controlled textual decomposition before NLI suffices;
5. a typed entity/population representation is required;
6. evaluator/gold ambiguity explains a material share;
7. the problem decomposes into smaller independent mechanisms.

## Frozen predecessor authority

- production `main` observed at start: `53f0885b111676794d1bd20e10b91aa58b07e9d4`
- RC3 accepted science head: `eb4e3043f5b16e3d65e5635b9d7013f312d5daf8`
- RC3 accepted science run: `33321392021`
- RC3 cohort SHA256: `01b0d436ccf9ed812f9bb26d64f4ddd1a656e26175ee007f1fe9594a2a203785`
- RC3 result SHA256: `7443941fe196d76aa4c895fe58eeb01511c4a865aaa88a14bdfd71c0226ad663`

RC3 supports explicit scoped-rule representation, but does not authorize its parser or generalize that result to population/membership semantics.

## Fresh cohort

The RC4 cohort is newly constructed and must be frozen before any RC4 tested model sees it. RC2/RC3 scored cases are not reused as RC4 scientific cases.

Primary cohort: 84 cases, exactly 28 entailment / 28 neutral / 28 contradiction, with seven 12-case families individually balanced 4/4/4:

1. direct class membership and rule applicability;
2. subclass inheritance and directionality;
3. `only` as necessary but not sufficient permission condition;
4. population quantifier scope (`some`, `none`, `not every`, `every`);
5. group-level versus member-level predication;
6. event role binding;
7. temporal class membership and rule applicability.

Additional controls:

- 10 preregistered metamorphic pairs / 20 cases;
- six evaluator-ambiguous cases with no forced three-way target;
- machine-readable semantic rationales recording membership, population, modality, predicate scope, roles, temporal boundary, and explicit unknown where applicable.

## Primary semantic failures

- `member_to_nonmember`: known member treated as outside the governing class/rule.
- `nonmember_to_member`: known non-member treated as permitted/governed under an only-class rule.
- `subclass_reversal`: A⊂B improperly read as B⊂A.
- `some_to_all`: existential evidence generalized universally.
- `only_necessary_to_sufficient`: `Only X may Y` improperly read as `X -> may Y`.
- `group_to_every_member`: group act transferred to a named member.
- `role_swap`: predicate arguments swapped.
- `membership_absence_not_behavior`: absence of class-rule applicability turned into opposite/factual behavior.
- `temporal_membership_scope`: class rule applied outside explicit membership interval.

## Frozen systems

After the accepted freeze, compare:

- S0 exact incumbent model revision from RC2/RC3;
- S1 exact same-family large revision from RC2/RC3;
- S2 exact long-context revision from RC2/RC3;
- S3 exact RC1 adverse-conservative categorical ensemble, no retuning;
- S4 deterministic membership/scope decomposition + incumbent NLI, frozen before evaluation;
- S5 deterministic typed entity/population candidate, frozen before evaluation and allowed to return `unresolved`.

S4/S5 accept only premise and hypothesis text. They must not consume case IDs, family labels, targets, semantic rationales, critical-error tags, or evaluator metadata.

## Falsifiers

Typed-representation hypothesis is falsified if S5 does not materially reduce preregistered semantic signature errors relative to NLI without comparable new decided errors, or if it survives only by excessive unresolved output.

Decomposition is falsified if S4 fails to improve critical distinctions or creates comparable regressions.

Specialist-model sufficiency is disfavored if S1/S2 repeat the same systematic signature errors after target-balanced entity/template swaps.

Ensemble sufficiency is disfavored if disagreement/abstention identifies risk but does not recover the population semantics.

Evaluator ambiguity is supported only by cases preregistered as underdetermined before model reveal; they remain outside primary scoring.

## Metamorphic controls

Preregistered transformations:

1. add explicit membership;
2. member → known non-member;
3. subclass direction reversal;
4. some → all;
5. only-class member → known non-member;
6. group act → explicit member act;
7. role swap → explicit swapped event;
8. temporal boundary crossing;
9. entity rename invariance;
10. clause movement / passive-form invariance.

## Stop conditions

A. NLI sufficient with bounded improvements.

B. Decomposition required.

C. Typed entity/population representation required.

D. Family decomposes further; freeze counterexamples and run the next smaller discriminating experiment.

## Non-authorization

No production entailer, threshold, ensemble, semantic operator, Contract C surface, aggregation rule, or downstream policy may be changed or promoted by RC4 alone. Research PRs are evidence records only.