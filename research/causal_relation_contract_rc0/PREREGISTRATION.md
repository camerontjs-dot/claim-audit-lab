# CAL Causal Relation Family Contract RC0 — Preregistration

Parent `607ec560fd53bd56279193a8d39a48b6f80e1012`.

Question: is there a conservative typed family for **explicit source causal semantics** that does not convert correlation, temporal order, co-occurrence, contribution, or model confidence into stronger causation?

Gate-0 source semantics are typed as CAUSES, CONTRIBUTES_TO, PREVENTS, CORRELATES_WITH, PRECEDES, or CO_OCCURS. Exact causal kind on exact endpoints supports. CAUSES vs PREVENTS on the same outcome refutes. CONTRIBUTES_TO does not automatically imply CAUSES, and CAUSES does not automatically imply CONTRIBUTES_TO in RC0. Correlation/order/co-occurrence are non-causal observations and remain unresolved for causal queries.

Weak controls: precedence->cause, correlation->cause, contribution->cause, and cause->contribution. Passing this Gate 0 does not establish causal inference from evidence, only a safe typed boundary for explicit causal assertions.
