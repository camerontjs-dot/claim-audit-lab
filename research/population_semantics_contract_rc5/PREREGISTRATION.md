# Population Semantics Contract RC5 — Preregistration

## Classification

Research Infrastructure / semantic-authority sufficiency experiment.

Stacked on RC4 accepted science head `c157da7953753a2f27c306abc86ab0141752c512`. RC4 evidence is preserved in Draft PR #47 and its terminal checkpoint comment `5470082717`.

## Question

RC4 showed that a frozen typed population/membership candidate achieved 98.4% selective accuracy, zero false-adverse decisions, and 9/10 mutation consistency, but text-to-structure recovery left 22 primary cases unresolved and one literal-substring error. This successor removes language parsing entirely.

The question is now narrower:

> Is a small typed authority sufficient to determine the supported three-way semantic relation for population scope and membership, and which fields are irreducibly necessary to preserve the distinctions observed in RC4?

## Competing explanations

1. Typed representation is sufficient; RC4 residuals were primarily extraction/query-normalization failures.
2. Typed representation is still semantically incomplete; even perfect structured inputs leave contradictions or unresolved distinctions.
3. A smaller subset of fields is sufficient; the proposed authority is over-specified.
4. The three-way relation itself is insufficient for some population semantics even after structure is explicit.

## Separation of responsibilities

RC5 has no text parser and no language model.

It compares two independently coded mechanisms over the same typed inputs:

- **possible-world oracle**: enumerates all bounded worlds consistent with the authority and derives entailment if the query is true in every world, contradiction if false in every world, otherwise neutral;
- **direct consumer**: implements the intended contract as local deterministic projection rules without enumerating worlds.

The consumer must not call the oracle. The oracle must not call the consumer.

## Semantic dimensions

The frozen corpus exhaustively covers:

1. class membership + universal rule applicability vs actual behavior;
2. directed subclass inheritance without converse inference;
3. `only` as a necessary permission condition, not a sufficient permission grant;
4. population quantifiers `every`, `none`, `some`, `not_every`;
5. group-level event vs named-member event;
6. ordered event-role binding;
7. temporal membership + rule applicability vs actual behavior.

## Proposed minimum authority fields

The candidate authority separates:

- entity identity;
- population/class identity;
- membership status: member / non-member / unknown;
- directed subclass edge;
- predicate identity;
- modality: fact / obligation / permission;
- population quantifier;
- `only` necessary-condition semantics distinct from permission itself;
- group scope distinct from member scope;
- ordered semantic roles;
- temporal membership boundary and direction;
- polarity;
- explicit unknown rather than coercion to false.

## Falsifiers

The typed-sufficiency hypothesis fails if the direct consumer disagrees with the independently coded possible-world oracle on any frozen corpus case.

A proposed field is not justified as irreducible unless at least one preregistered ablation witness contains two states that become indistinguishable when that field is removed but have different oracle relations for the same query.

Three-way semantics is inadequate if the possible-world oracle requires a fourth semantic relation for any modeled case. `neutral` is explicitly used for propositions that vary across admissible worlds; absence of entailment is not contradiction.

## Metamorphic requirements

The frozen tests require invariance under entity renaming and irrelevant entity addition, and directional sensitivity under membership flip, subclass reversal, quantifier strengthening/weakening, role swap, group/member scope change, and temporal-boundary crossing.

## Stop conditions

A. **Contract sufficient**: consumer and oracle agree exhaustively, all required ablation witnesses exist, and metamorphic properties pass. Population/membership semantics are considered nailed at the representation/consumption layer; text extraction remains a separate unvalidated boundary.

B. **Contract incomplete**: preserve counterexamples and add only the missing semantic primitive in a fresh successor.

C. **Three-way relation incomplete**: preserve the case demonstrating the missing relation and stop semantic promotion.

## Non-authorization

RC5 does not authorize a text parser, production semantic operator, NLI replacement, threshold, ensemble, Contract C change, aggregation change, or downstream policy change.