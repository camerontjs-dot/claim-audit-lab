# CAL Quantitative Change Composition RC0 — Preregistration

Parent `607ec560fd53bd56279193a8d39a48b6f80e1012`.

Question: can `quantitative_change` remain a composition rule over two exact scalar states plus temporal ordering, rather than becoming another atomic semantic family?

Inputs bind entity, metric, unit, time, exactness, and value. A change query binds the same entity/metric/unit and asks INCREASED, DECREASED, UNCHANGED, or exact absolute DELTA. Derivation is allowed only when both scalar states are exact and bindings agree. Unit/metric/entity mismatch or approximate states fail closed to UNRESOLVED.

Weak controls: ignore unit, ignore metric/entity, treat approximate points as exact, and ignore state order. A pass supports the composition-first hypothesis only; percent-vs-percentage-point language, ratios, rates, uncertainty, and natural-language extraction remain unqualified.
