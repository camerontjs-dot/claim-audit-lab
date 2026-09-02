# RC8E Preregistration: Same-Source Whole-Atom Identity Binding

## Decision question

Can the frozen RC8D admitted-evidence anchored gate prevent a complete, internally consistent authority receipt for atom B from acquiring warrant when it is attached to a different target atom A in the **same admitted source**?

This tests whole-atom/consumer-slot binding. It does not retest RC8D source anchoring and does not modify RC8D.

## Frozen parent candidate

- candidate: RC8D
- candidate declaration commit: `eab2a34f8249d06613e6bd9ca396d2c16e421c02`
- candidate blob: `f04f2dc529d3f1a7666d39a3bf9c8a9df87842d1`
- frozen RC8B dependency blob: `edf84bb5aae0dd217e3f780e7a49767440b7c1e5`

The frozen candidate must not be changed after this preregistration and any disagreement must be preserved.

## Why this is discriminating

RC8D proves that `authority_subject_source_id` matches admitted `raw_source_id`, while RC8B proves that proposal/assertion/operator/field/composition/aperture subreceipts share one `authority_subject_id`.

Neither frozen gate proves that the internally consistent authority subject is the **target atom currently being assessed**. A whole receipt bundle can therefore be source-consistent and internally consistent while still belonging to a different atom in the same source.

## Controlled representation

The falsifier introduces two explicit non-authoritative identity observations around the frozen gate:

- `target_atom_id`: the consumer/output atom whose authority is being assessed;
- `authority_subject_atom_id`: the atom identity to which the authority bundle claims to belong.

The frozen RC8D candidate does not currently inspect either field. They are introduced only to test whether whole-atom binding is absent from the current receipt architecture.

## Positive control

Use one synthetic admitted source containing two distinct atom identities A and B whose semantic field values are intentionally identical. This prevents value differences from accidentally detecting transplantation.

For the positive control:

- admitted source identity matches the RC8D source anchor;
- `target_atom_id == authority_subject_atom_id == A`;
- all RC8D/RC8B receipt fields are valid and internally consistent;
- expected result: `WARRANTED`.

## Target mutations

At minimum, freeze cases for:

1. complete receipt bundle for B attached to target A, with the same admitted source and identical semantic values;
2. missing `target_atom_id`;
3. missing `authority_subject_atom_id`;
4. explicit atom mismatch plus a subordinate receipt mismatch, to test atom-anchor precedence;
5. positive target/subject identity control;
6. reader/instrument-bank growth on both warranted and unresolved controls.

No semantic value, source identity, reader count, instrument count, or subreceipt value should distinguish A from B in the transplantation case.

## Expected behavior

- target atom identity missing -> `UNRESOLVED`;
- authority-subject atom identity missing -> `UNRESOLVED`;
- explicit target/authority atom mismatch -> `REJECTED`;
- fully bound positive control -> `WARRANTED`;
- reader/instrument count changes must not alter authority.

## Hard criterion

`unsafe_warranted_atoms == 0`

A single mismatched or missing atom-binding case that becomes `WARRANTED` falsifies RC8D as a sufficient end-to-end authority receipt.

## Falsification consequence

If RC8D is falsified:

- preserve RC8D unchanged;
- preserve RC8D's successful source-anchor result as bounded evidence;
- create a successor that adds only an explicit whole-atom identity anchor before delegating to frozen RC8D;
- do not add confidence, reader-count, instrument-count, or voting authority.

## Non-claims

This experiment does not establish source-byte authenticity, cryptographic provenance, semantic recovery from text, span-to-source-content binding, production readiness, Contract C projection, or independent recoverability.
