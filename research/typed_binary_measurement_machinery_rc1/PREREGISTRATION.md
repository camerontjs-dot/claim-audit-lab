# CAL Typed Binary Relation Measurement Machinery RC1 — Preregistration

Date: 2026-09-17

Classification: Draft Research / Gate-1A successor after RC0 evaluator invalidity.

Parent: terminal typed/spatial Gate-0 head `22bc5c1d97b78cfe6f9e2f57e52f69d528069b9a`.
Typed-contract authority remains `7463ada3358f24fa5bb53fe82631a69064346bf3`.

## RC0 correction

RC0 incorrectly made `B owns A` fail-closed even though it is a valid closed typed-relation atom. RC1 freezes that surface as a diagnostic with exact reversed arguments. An argument-erasing parser now fails by making the wrong diagnostic claim.

## Question

What proposal machinery safely recovers closed typed binary relations while preserving predicate identity, argument order, polarity, and the distinction between direct atoms and unqualified spatial/compositional inferences?

MUST_HANDLE:
- direct OWNS / OWNED_BY;
- ADJACENT_TO;
- NORTH_OF / SOUTH_OF;
- IN / CONTAINS;
- direct negative ownership.

DIAGNOSTIC:
- valid reversed ownership;
- `belongs to`;
- `lies north of`;
- `lies within`;
- symmetric adjacency wording.

FAIL_CLOSED:
- unknown predicates;
- spatial relation chains and inferred transitivity;
- metric geometry;
- reporting and modality;
- conjunction/disjunction;
- population/state neighbors.

A path qualifies only if required cases are exact, no fail-closed case is claimed, claimed diagnostics are exact, replay/metamorphics pass, and production `src/` is unchanged.

No measurement proposal is authority. Gate-1B source completion/warrant remains separate.
