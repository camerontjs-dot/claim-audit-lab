# RC8F Preregistration: Source-Anchored Whole-Atom Authority Receipt

## Hypothesis

A receipt that already satisfies RC8D source anchoring and RC8B subordinate subject consistency can be made resistant to the RC8E same-source transplantation failure by adding exactly one whole-atom identity gate before subordinate semantic checks.

## Frozen predecessors

- RC8D candidate blob: `f04f2dc529d3f1a7666d39a3bf9c8a9df87842d1`
- RC8B dependency blob: `edf84bb5aae0dd217e3f780e7a49767440b7c1e5`
- RC8E falsifier apparatus freeze: `53f2fe8233c33e52609a258d5bd6883678e24881`
- RC8E reveal run: `33660009114`

Neither predecessor candidate may be modified.

## Minimal successor architecture

RC8F adds only:

- `target_atom_id`: atom/consumer slot whose authority is being assessed;
- `authority_subject_atom_id`: atom to which the authority bundle belongs.

Precedence:

1. execution failure remains `NO_ASSESSMENT` via frozen RC8D;
2. evidence rejection remains `REJECTED` via frozen RC8D;
3. admitted-evidence source anchor remains authoritative and precedes atom binding via frozen RC8D behavior;
4. once source anchoring is valid:
   - missing target or authority atom identity -> `UNRESOLVED / AUTHORITY_ATOM_IDENTITY_BINDING_UNRESOLVED`;
   - explicit mismatch -> `REJECTED / AUTHORITY_ATOM_IDENTITY_MISMATCH`;
   - match -> continue through frozen RC8D and RC8B.

No semantic field, operator, composition, aperture, reader-count, instrument-count, or confidence logic changes.

## Exposed qualification

Before freezing RC8F, replay all prior exposed authority cases under explicit valid atom binding, including:

- RC8/RC8B qualification and regression cases;
- RC8B prospective cases, now exposed;
- RC8C source-anchor falsifier;
- RC8D prospective held-out, now exposed;
- RC8E atom-identity falsifier.

RC8E cases retain their original target/authority atom identities and expected labels. Other historical cases receive a neutral matching atom identity only for exposed regression qualification.

Hard exposed qualification requirements:

- `unsafe_warranted_atoms == 0`;
- exact status for every case;
- exact typed reason for every case.

## Prospective requirement

If exposed qualification passes, freeze RC8F before authoring a new prospective cohort. The fresh cohort must include same-source whole-bundle transplantation, missing atom identities, source-vs-atom precedence, subordinate-vs-atom precedence, semantic unresolved/rejection controls, and reader/instrument-bank invariance.

## Falsifier

One unsafe warranted atom after the RC8F freeze falsifies the successor within the tested envelope. Preserve the candidate and disagreement unchanged.

## Non-claims

Even a clean prospective RC8F result would not authenticate atom IDs, prove canonical atom-ID generation, bind spans to source bytes/content, recover semantics from natural language, authorize production, alter Contracts B/C, or establish independent recoverability.
