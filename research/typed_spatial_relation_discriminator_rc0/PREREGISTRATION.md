# CAL Typed Binary / Spatial Relation Discriminator RC0

Parent `607ec560fd53bd56279193a8d39a48b6f80e1012`.

Question: does atomic spatial relation semantics require a separate family, or can spatial predicates be a closed subset of a constrained typed-binary relation family?

Each admitted predicate has an explicit relation spec: symmetry and optional inverse. Exact or spec-equivalent atom supports; opposite polarity refutes; direction/inverse mistakes remain unresolved. Unregistered predicates are outside jurisdiction even when surface strings match.

Spatial sentinels use ADJACENT_TO (symmetric), NORTH_OF/SOUTH_OF (inverse), and IN/CONTAINS (inverse). Success requires the same generic typed-relation consumer to handle those cases without spatial-specific branches.

Weak controls: open-predicate acceptance, all-relations-symmetric, ignore inverse/direction, and spatial-name routing. Gate 0 only; richer topology/transitivity is not claimed.
