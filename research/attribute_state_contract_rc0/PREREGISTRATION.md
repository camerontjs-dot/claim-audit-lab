# CAL Attribute State Family Contract RC0 — Preregistration

Parent `607ec560fd53bd56279193a8d39a48b6f80e1012`. Test whether closed, declared functional attributes need an `attribute_state` family rather than an unrestricted subject-predicate escape hatch.

Exact entity/attribute/domain/value supports. A different value refutes only when the attribute contract is functional and the value belongs to the same declared closed domain. Otherwise mismatch is unresolved. Weak controls: generic SPO mismatch-refutes, domain erasure, entity erasure, and treating non-functional predicates as attributes.

Gate 0 only; no production change or promotion.
