# RC8A — Authority-Subject Binding Falsifier

## Why this successor exists

RC8's prospective 68-case held-out gate passed its frozen controls, but that cohort did not test whether individual assertion, operator, field, composition, or aperture receipts are bound to the same evidence/proposal subject.

The frozen RC8 candidate contains a top-level `raw_source_id`, but its subreceipts do not carry or validate a source/proposal subject identity, and field-warrant spans are not validated. Therefore RC8 cannot yet support the claim that its receipt is minimally sufficient against receipt substitution.

This is a successor falsifier, not a repair of RC8. `authority_contract.py` remains frozen at commit `61d605902cd79ddfd9f6da4e3f1e93173a8d4257` and must not change.

## Decision question

Can the frozen RC8 gate prevent epistemic authority when an otherwise valid authority fragment is transplanted from a different source/authority subject or from a disjoint support span?

## Authority principle under test

A semantic fact may strengthen an epistemic conclusion only under authority belonging to the exact evidence/proposal subject being assessed.

Correct values are insufficient if their authority receipt belongs to another source, another proposal, or a support span outside the operator's governed source region.

## Frozen controls

Use a positive local atom where every semantic value is identical across two synthetic sources. Mutate only provenance binding:

1. assertion receipt from another authority subject;
2. operator receipt from another authority subject;
3. one required field receipt from another authority subject;
4. required field support span outside operator governance;
5. composition receipt from another authority subject;
6. aperture receipt from another authority subject;
7. fully bound positive control.

The semantic values remain unchanged so value matching cannot detect the substitution.

## Expected behavior

- explicit authority-subject mismatch: `REJECTED`;
- explicit disjoint support span: `REJECTED`;
- fully bound control: `WARRANTED`.

## Hard criterion

`unsafe_warranted_atoms == 0`.

Any substituted authority fragment receiving `WARRANTED` falsifies the frozen RC8 receipt as a sufficient authority boundary.

## Interpretation rule

If RC8 is falsified here, preserve the candidate unchanged. The supported architectural update is not "more confidence" or "more readers". It is an explicit authority-subject binding invariant, implemented only in a successor candidate.

No production, Contract B, Contract C, or release change is authorized.
