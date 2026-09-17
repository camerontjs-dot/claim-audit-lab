# CAL Scalar Value Family Contract RC0 — Terminal Result

Date: 2026-09-17

Classification: Draft Research / Gate-0 semantic-family discrimination.

## Frozen lineage

- parent M4 terminal result: `607ec560fd53bd56279193a8d39a48b6f80e1012`
- frozen candidate-test apparatus: `b622a46c652234987ce9842c6da8cf12401b13fd`
- exact qualified head: `c3b7e13d8940f20fcd476eb6b96f276e78e309ec`
- dedicated full-history qualification run: `35279629280`

## Disposition

**SUPPORTED FOR PROMOTION, bounded to the typed Gate-0 `scalar_value` family contract.**

The tested contract admits exact scalar points and bounded scalar intervals over exact entity, metric, and unit identity. It supports a query only when every value admitted by the authority satisfies the query, refutes only when no admitted value satisfies the query, and otherwise remains unresolved.

A non-exact point estimate does not establish exact equality. Unit, metric, or entity mismatch does not silently convert or compare values.

## Evidence

On exact head `c3b7e13d…`:

- frozen apparatus verification passed;
- all frozen evaluator controls passed;
- all frozen candidate falsifiers passed;
- the full repository test suite passed;
- candidate Ruff lint passed;
- candidate Ruff format passed;
- strict mypy passed;
- production `src/` remained unchanged from M4.

The preregistered weak strategies were discriminated: midpoint-only range reasoning, unit erasure, approximation-as-exact, and range/equality collapse were not accepted as equivalent semantics.

## Boundary

This Gate-0 result supports a distinct scalar-state semantic family. It does not yet establish unit conversion, tolerances, measurement uncertainty distributions, significant figures, natural-language approximation, claim extraction, source completion/warrant, runtime/plugin integration, Contract C/Decision behavior, independent reproduction, or release readiness.
