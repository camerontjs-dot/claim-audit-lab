# CAL Scalar Value Family Contract RC0 — Preregistration

Parent: `607ec560fd53bd56279193a8d39a48b6f80e1012`.

Question: can one typed `scalar_value` family represent exact and bounded scalar states without collapsing intervals, units, or approximation into exact equality?

Gate 0 only. No parser, measurement model, warrant, production plugin, Contract C/Decision change, merge, or release.

Frozen semantics:
- authority binds exact entity, metric, unit, lower/upper bound, and whether the bound is exact;
- query operators are EQ, GT, GE, LT, LE;
- relation is SUPPORTS when every value admitted by the authority satisfies the query, REFUTES when no admitted value satisfies it, otherwise UNRESOLVED;
- entity/metric/unit mismatch is UNRESOLVED;
- a non-exact point estimate is not exact equality authority.

Weak controls to kill:
- midpoint-only range reasoning;
- unit erasure;
- approximate-point-as-exact;
- threshold-only reasoning that cannot distinguish support from partial overlap.

Success supports only the typed Gate-0 family contract. Unit conversion, tolerance policy, natural-language approximation, uncertainty distributions, and comparison-family integration remain later work.
