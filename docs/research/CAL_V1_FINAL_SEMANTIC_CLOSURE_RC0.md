# CAL V1 Final Semantic Closure RC0 — Definition/Equivalence and Entity Existence

Date: 2026-09-18

Classification: Draft Research / final family-boundary discrimination before CAL V1 freeze.

## Exact CAL base

This experiment starts from terminal integrated-parent result head:

- CAL PR #178 terminal record head: `47d7067476088e7b5b86944ec0df72ef949f5127`;
- integrated executable subject: `b695a1ca16051fde1c204987895b672e73225168`;
- decisive integration run: `35368736767`.

No production semantic source changes are permitted.

## Reused qualified family authorities

Typed binary relation:

- terminal PR #127;
- exact qualified candidate head: `7463ada3358f24fa5bb53fe82631a69064346bf3`;
- terminal result head: `22bc5c1d97b78cfe6f9e2f57e52f69d528069b9a`;
- candidate blob: `4dbbc3a94ce561ef71590c8ac900c87259ac361f`;
- candidate behavior: closed predicate vocabulary, explicit symmetry/inverse metadata, exact subject/object identity, polarity-preserving support/refute.

Attribute state:

- terminal PR #126;
- exact qualified candidate head: `2b4ae5c52f301f16de50719cb11e61919766aa94`;
- terminal result head: `f117698e6db3b47cc68af2024c7816cc8945b004`;
- candidate blob: `5d33fd1fd5259cd3d3176b9c7e748252a8eac646`;
- apparatus blob: `e86d0073252cd74fcb8e18cc407e242c9d3a070d`;
- candidate behavior: exact entity + attribute + domain binding; equal value supports; mismatch refutes only when both sides declare functional/closed state.

The workflow must execute these exact historical subjects from detached checkouts rather than rewriting their relation logic.

# Question A — definition / equivalence

Does an explicitly typed definition/equivalence claim require a new atomic family, or can it reuse the already-qualified closed typed-binary relation machinery?

## Registered test predicates

The exact generic candidate is exercised unchanged after adding only closed predicate metadata:

- `EQUIVALENT_TO`: symmetric;
- `DEFINED_AS`: inverse `DEFINITION_OF`;
- `DEFINITION_OF`: inverse `DEFINED_AS`.

No new relation algorithm is permitted.

## Frozen cases

Equivalence:
- direct exact equivalence -> SUPPORTS;
- reversed symmetric equivalence -> SUPPORTS;
- exact equivalence with opposite polarity -> REFUTES;
- different counterpart -> UNRESOLVED.

Definition:
- direct `DEFINED_AS` -> SUPPORTS;
- inverse `DEFINITION_OF` -> SUPPORTS;
- reversed `DEFINED_AS` without inverse predicate -> UNRESOLVED;
- exact definition with opposite polarity -> REFUTES;
- unregistered definition-like predicate -> UNRESOLVED.

## Important boundary

This tests only already-typed explicit assertions.

It does not authorize:
- interpreting arbitrary copular “X is Y” language as definition;
- substitution of equivalent expressions inside other propositions;
- transitive closure of definitions;
- ontology induction;
- synonym discovery;
- lexical entailment.

Success therefore means **no new atomic family is needed for bounded explicit definition/equivalence relation state**. It does not establish a generic definition reasoner.

# Question B — entity existence

Does explicitly warranted entity existence require a new atomic family, or can it reuse the qualified narrow attribute-state contract?

## Frozen representation

Existence is represented only as the following closed functional state:

- `entity = <exact entity identity>`;
- `attribute = existence`;
- `domain = entity_existence_v1`;
- `value = present | absent`;
- `functional = true`.

This is not a generic subject-predicate escape hatch.

## Frozen cases

- present vs present -> SUPPORTS;
- absent vs present -> REFUTES;
- present vs absent -> REFUTES;
- different entity -> UNRESOLVED;
- different domain -> UNRESOLVED;
- mention/reference state vs existence query -> UNRESOLVED;
- non-functional existence mismatch -> UNRESOLVED.

## Important boundary

Only an upstream measurement/warrant that explicitly establishes existence or nonexistence may create this state.

The following are forbidden shortcuts:
- entity mention -> existence;
- retrieval hit -> existence;
- membership -> existence;
- event occurrence -> existence;
- absence of evidence -> nonexistence.

Success therefore means **no new atomic family is needed for bounded explicit existence state**. It does not establish existence extraction or world-completeness reasoning.

# Freeze criterion

If the exact historical candidates produce the frozen expected results with no algorithm change, record:

- `DEFINITION_EQUIVALENCE_COLLAPSES_TO_TYPED_BINARY_RC0`;
- `ENTITY_EXISTENCE_COLLAPSES_TO_ATTRIBUTE_STATE_RC0`.

If either requires special-case logic beyond closed predicate/state registration, preserve that counterexample and do not freeze CAL V1 until dispositioned.

No merge, release, production registration, Contract mutation, or Decision change is authorized.
