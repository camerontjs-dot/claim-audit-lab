# RC7F-D Deontic / Permission Scope Composition — Preregistration

Status: **FROZEN BEFORE CANDIDATE AND HELD-OUT COHORT**

## Parent evidence

- RC7E evidence: `34e9bcafad2c63c9b0761ffc456532344bc75b88`
- accepted run: `33448511982`
- shared residual permission dimensions: `5`
- exact observed residual includes `PE01`–`PE04` and `PT04`, where permission is composed with exception or temporal scope.

RC7F-D is a successor measurement experiment, not a repair of RC7E.

## Question

Can a bounded non-LLM specialist recover a **typed semantic permission observation together with explicit exception or temporal scope** without laundering that normative statement into operational authorization?

## Output boundary

The candidate may emit a proposal containing:

- permission form: necessary permission condition / restricted-to population;
- population;
- normalized predicate/action phrase;
- optional exception (`excluded` entity);
- optional temporal scope (`before|after|until|as_of`, reference);
- exact source cues.

The output says what the source normatively states. It **does not mean the named actor is operationally authorized to act**.

No production `src/` changes. No generative LLM, LLM judge, or model-generated gold.

## Supported surfaces

Permission core:

- `Only <population> may <predicate>`
- `Permission to <predicate> is restricted to <population>`

Exception composition:

- `except <entity>`
- `excluding <entity>`
- `apart from <entity>`
- `save for <entity>`
- `with the exception of <entity>`

Temporal composition:

- `before <reference>`
- `after <reference>`
- `until <reference>`
- `as of <date/reference>`

## Qualification

Must cover both permission-core surfaces, every exception cue, every temporal relation, a permission-value/domain trap, ordinary factual `may` ambiguity, and unrelated exception/temporal words. Unsupported ambiguity must abstain rather than guess.

## Held-out

Only after apparatus/evaluator freeze. Gold permission+modifier objects are created before deterministic rendering; candidate output does not establish gold.

Required families:

1. permission + exception across both permission surfaces;
2. permission + temporal across both surfaces;
3. permission with no modifier as a regression control;
4. meaning-preserving surface alternations;
5. meaning-changing exception entity / temporal direction pairs;
6. domain-word traps containing permission/exception/temporal vocabulary;
7. factual epistemic `may` controls that are not normative permission;
8. deliberately unsupported nested or ambiguous forms scored as safe abstention.

## Metrics

- typed proposal precision/recall;
- permission-core accuracy;
- exception attachment accuracy;
- temporal relation/reference accuracy;
- false proposals on negative controls;
- composition exact accuracy;
- meaning-changing pair accuracy;
- unresolved rate.

## Success

`DEONTIC_COMPOSITION_CANDIDATE_READY_FOR_HARDENING` requires:

- typed precision `1.0`;
- typed recall >= `0.95` in supported jurisdiction;
- exact composition accuracy >= `0.95`;
- exception and temporal attachment accuracy `1.0` for resolved proposals;
- negative-control false proposals `0`;
- meaning-changing pair accuracy `1.0`;
- no evaluator/cohort defect;
- no post-held-out repair.

Safe bounded residue yields `MORE_DEONTIC_COMPOSITION_RESEARCH_JUSTIFIED`; unsafe false proposals or invalid apparatus yield `DEONTIC_COMPOSITION_ARCHITECTURE_FALSIFIED_OR_INCONCLUSIVE`.

## Design principle

A source sentence can be correctly observed as a permission norm without CAL asserting that any actor presently has execution authority. Semantic warrant and operational authorization remain separately typed domains.
