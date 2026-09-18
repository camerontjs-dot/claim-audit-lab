# CAL Quantitative Change Warranted Composition RC1 — Result

Date: 2026-09-17

Classification: Draft Research / terminal post-authority composition qualification.

## Disposition

**SUPPORTED FOR PROMOTION, bounded to exact warranted quantitative-change composition.**

The tested result supports keeping bounded exact quantitative change as a derived composition over two independently warranted scalar atoms plus separately established temporal bindings. It does not justify a new atomic `quantitative_change` semantic family.

## Exact evidence

- parent scalar Gate-1B candidate: `c33b656819e91ac38a85c48921b84ea20ec090bc`
- exact qualified candidate head before this result record: `ce91e0cf304985d04947acbd65d9c802751d3b56`
- dedicated qualification run: `35300631939`
- frozen evaluator controls: PASS
- candidate qualification: PASS
- parent `src/` and scalar Gate-1B isolation guards: PASS
- focused static checks: PASS

All frozen cases matched the oracle. The frozen weak strategies were discriminated for call-order dependence, scalar identity erasure, interval-midpoint laundering, and warrant erasure.

## Supported boundary

Within this RC, CAL may derive `INCREASED`, `DECREASED`, `UNCHANGED`, and exact absolute `DELTA` only when:

- both scalar atoms are warranted under distinct authority identities;
- both temporal bindings are established, distinct, and ranked;
- entity, metric, and unit identity match the query;
- both scalar values are exact points rather than intervals or approximations;
- temporal rank, not contribution call order, determines earlier/later state.

A mismatch in a fully eligible exact composition may support or refute the bounded query. Missing or incompatible identity, warrant, exactness, or temporal state remains `UNRESOLVED`.

## Preserved CI deviation

The ordinary Public suite on this branch is red only at:

`tests/production/test_historical_golden_version_migration.py::test_historical_goldens_only_change_the_distribution_version`

because `git show 32275a239b68af383a56bca843e28cbc1e343976:tests/v1/fixtures/traces/01-supported-verbatim.json` exits 128.

That failure predates this candidate. The exact scalar parent Public-suite run `35297087826` failed at the same test for the same missing historical object. It is therefore preserved as an inherited repository/CI defect, not counted as semantic evidence for or against this composition candidate.

## What is not established

This does not qualify:

- relative or percentage change;
- percentage-point normalization beyond already-identical scalar units;
- rates or compound change;
- uncertainty propagation;
- approximate/ranged composition;
- unit conversion;
- temporal extraction from text;
- production registration or runtime wiring;
- Contract C or Decision Engine behavior.

No merge, release, or production mutation is authorized by this result alone.
