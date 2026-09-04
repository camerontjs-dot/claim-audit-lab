# RC8J Categorical Warranted-Relation Participation RC1

## Classification

Draft Research Infrastructure / authority-to-conclusion semantics experiment. Research-only. No production authorization.

## Parent evidence preserved

- production `main`: `32275a239b68af383a56bca843e28cbc1e343976`
- stacked parent PR #78 accepted head: `884405755eee6e71434c43ccae0d95d5fa1fd517`
- frozen CAL decision-model blob under the parent test: `f0d9d3bc061d966ed9c8c16b3424b3dd5c3bb339`
- frozen RC8J candidate commit: `8e75c6782bb95c3763d06230b9c5df2b6af44054`
- frozen RC8J candidate blob: `f55156e43e0c1b4a7868bc8339585b8892edda38`

PR #78 remains immutable evidence that RC8J `WARRANTED` supplies neither a scalar decision score nor a support/refutation channel and that arbitrary scalar/channel stipulation can manufacture different ordinary threshold decisions. This successor does not repair that result or choose a better score.

## Question

Can a fully warranted, already-constructed comparison atom participate in a CAL proposition conclusion through a proposition-relative categorical relation and a scoreless composer, without accepting caller-supplied support/refutation polarity or scalar decision strength?

The answer may be no.

## Candidate architecture under test

```text
already-constructed typed comparison atom
        ↓
frozen RC8J authority gate
        ↓
WARRANTED atom only
        ↓
CAL research-only comparison relation operator
  SUPPORTS | REFUTES | IRRELEVANT | UNRESOLVED
        ↓
scoreless categorical proposition composer
        ↓
supported | contradicted | mixed-abstain | unresolved-abstain
```

The categorical relation is not an RC8J output. It is a separate CAL research hypothesis and must be derived from typed atom/proposition semantics.

## Controlled semantic fragment

This RC tests only already-constructed typed `comparison` atoms with:

- `lhs_entity`
- `rhs_entity`
- `comparison_direction`

The relation operator may use only the warranted atom payload and a strict proposition target. It may not accept `channel`, `support`, `refutation`, `relation_hint`, `score`, `confidence`, threshold, reader count, or instrument count as decision inputs.

For the bounded strict-order fragment:

- same ordered pair + same direction => `SUPPORTS`;
- same ordered pair + opposite strict direction => `REFUTES`;
- swapped pair + logically inverse strict direction => `SUPPORTS`;
- swapped pair + same strict direction => `REFUTES`;
- a different entity pair => `IRRELEVANT`;
- a same-pair direction outside the implemented strict-order relation table => `UNRESOLVED`.

No text extraction, world truth, numeric calibration, confidence, probabilistic strength, or generic semantic entailment is claimed.

## Scoreless composition rule under test

Given only relation receipts from warranted atoms:

1. any `UNRESOLVED` relation => `unresolved-abstain`;
2. at least one `SUPPORTS` and at least one `REFUTES` => `mixed-abstain`;
3. at least one `SUPPORTS` and no `REFUTES` => `supported`;
4. at least one `REFUTES` and no `SUPPORTS` => `contradicted`;
5. otherwise, including only `IRRELEVANT`, => `unresolved-abstain`.

`IRRELEVANT` is non-deciding. Relation count carries no strength semantics.

## Required cases

The decisive runner must use the real frozen RC8J evaluator and the existing fixture-only typed seam coordinates, then require:

1. warranted atom `A > B` against proposition `A > B` => `SUPPORTS` => `supported`;
2. warranted atom `A < B` against proposition `A > B` => `REFUTES` => `contradicted`;
3. both warranted atoms together => `mixed-abstain`;
4. warranted atom over another entity pair => `IRRELEVANT` => `unresolved-abstain`;
5. warranted atom `A > B` against unsupported same-pair direction `at_least` => `UNRESOLVED` => `unresolved-abstain`;
6. `SUPPORTS + IRRELEVANT` remains `supported`;
7. `SUPPORTS + UNRESOLVED` fails closed to `unresolved-abstain`;
8. swapped semantic equivalence `A > B` versus proposition `B < A` => `SUPPORTS`;
9. input order does not change mixed composition;
10. changing only diagnostic reader/instrument metadata does not change a warranted relation/conclusion;
11. an RC8J `UNRESOLVED` mutation cannot enter the warranted relation operator;
12. caller attempts to provide `score`, `channel`, or `relation_hint` are rejected by the strict proposition input surface.

## Falsifiers

The categorical architecture is falsified for this bounded fragment if any of the following occurs:

- a non-`WARRANTED` atom can participate as deciding categorical evidence;
- relation or conclusion requires a scalar score or threshold;
- caller-supplied support/refutation polarity is required or accepted;
- the same typed atom/proposition semantics produce different relation due only to diagnostic reader/instrument metadata;
- strict-order direction mutation does not flip `SUPPORTS`/`REFUTES` as preregistered;
- `SUPPORTS + REFUTES` produces a terminal supported/contradicted result;
- `UNRESOLVED` is laundered into neutral/irrelevant state and permits a terminal decision;
- order of the same relation multiset changes the proposition result;
- the real frozen RC8J dependency or decision-model blob no longer matches its frozen identity;
- production `src/` changes.

A failing implementation/test is evidence against the candidate as encoded; do not repair the apparatus after seeing a decisive semantic result and call the same run unchanged.

## Evidence and receipts

The research workflow must:

- verify the exact frozen RC8J commit/blob and frozen decision-model blob;
- re-run the frozen valid-B parent corpus needed for the typed seam coordinates;
- execute deterministic unit/metamorphic tests for the relation/composer;
- execute the decisive runner against the real frozen RC8J evaluator;
- emit a JSON run receipt containing each authority result, derived relation, scoreless composition outcome, and non-claims;
- verify no production `src/` changes relative to production baseline;
- upload the run-output artifact.

## Boundary / non-authorization

Do not modify RC8J, Contract B, Contract C, Decision Engine policy, production CAL source, release state, or the separate `research-scaffold-harness` clean-room aperture. Do not claim semantic-text extraction or generic proposition entailment.

A passing result would establish only that this bounded typed-comparison categorical architecture can carry already-warranted atoms into a scoreless CAL research conclusion. It would not authorize production promotion.
