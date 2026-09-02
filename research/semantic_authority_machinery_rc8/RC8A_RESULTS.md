# RC8A Authority-Subject Binding Falsifier — Results

## Disposition

**FALSIFIED.** The frozen RC8 receipt is not a sufficient authority boundary against authority-fragment substitution.

This is a preserved failure of the frozen candidate, not a repair target for `authority_contract.py`.

## Frozen identities

- preregistration commit: `77ecd0bba476f5606be31db471648f053d86ea65`
- RC8 candidate freeze: `61d605902cd79ddfd9f6da4e3f1e93173a8d4257`
- RC8 candidate blob: `628a3ba1676b48fc4572b949df0db7d4ad5a1696`
- RC8A apparatus freeze head: `89cc7d6e68d265c0306c3e7e9a863e12acbcd56c`
- pre-reveal qualification run: `33649562809`
- reveal workflow commit: `3b1268c339857bd3cd96bbad662abd792765c33d`
- reveal run: `33649696646`
- RC8A job: `100313346891`
- result artifact: `9854236211`
- result artifact digest: `sha256:ece83e698e3a7623e611518f51367d85162ef3a735dac4dcd3bc4937c47085ab`

The reveal job verified the frozen RC8 candidate and frozen RC8A apparatus before execution. The evaluator executed successfully and uploaded its result. The hard safety step then failed because unsafe warranted atoms were present. In the same run, the original RC8 held-out science job remained successful.

## Exact result

- case count: `7`
- status exact: `1 / 7`
- reason exact: `1 / 7`
- unsafe warranted atoms: `6`
- scientific state: `RC8_RECEIPT_FALSIFIED_BY_SOURCE_BINDING`

The fully bound positive control returned `WARRANTED / ALL_REQUIRED_WARRANT_ESTABLISHED` as expected.

Every preregistered substitution mutation incorrectly returned `WARRANTED / ALL_REQUIRED_WARRANT_ESTABLISHED`:

| Case | Mutation | Expected | Observed |
|---|---|---|---|
| `RC8A-ASSERTION-SUBJECT-B` | assertion receipt from authority subject B | `REJECTED` | `WARRANTED` |
| `RC8A-OPERATOR-SUBJECT-B` | operator receipt from authority subject B | `REJECTED` | `WARRANTED` |
| `RC8A-FIELD-SUBJECT-B` | required field receipt from authority subject B | `REJECTED` | `WARRANTED` |
| `RC8A-FIELD-SPAN-DISJOINT` | required field support span outside operator governance | `REJECTED` | `WARRANTED` |
| `RC8A-COMPOSITION-SUBJECT-B` | composition receipt from authority subject B | `REJECTED` | `WARRANTED` |
| `RC8A-APERTURE-SUBJECT-B` | aperture receipt from authority subject B | `REJECTED` | `WARRANTED` |

## What this establishes

Observed evidence supports a narrow causal diagnosis:

1. RC8's existing value matching, operator-domain checks, proposal-span governance, field-state handling, composition state, and aperture state are not sufficient to bind warrant fragments to the authority subject being assessed.
2. A semantically identical receipt fragment can be transplanted from another authority subject without RC8 detecting the substitution.
3. A required field warrant can cite a span outside the operator's governed source region without RC8 detecting it.
4. Reader count, instrument count, or scalar confidence cannot repair this defect because the falsifier holds semantic values constant and mutates only authority provenance.

## What this does not establish

RC8A does not establish the final representation of an authority-subject identifier, whether it must be a digest or structured reference, or whether every non-authority-bearing diagnostic receipt requires such binding.

It also does not establish production readiness, natural-language extraction correctness, Contract B/C projection, or downstream Decision Engine policy.

## Successor constraint

RC8 remains frozen and falsified for this sufficiency claim.

A successor may add only the smallest mechanism required by the evidence:

- one explicit authority-subject identity for the assessment;
- binding of proposal and authority-bearing assertion/operator/field/composition/aperture receipts to that same subject;
- explicit validation that required field support spans remain inside operator governance;
- typed mismatch versus missing-binding outcomes;
- no authority role for reader agreement, instrument count, or confidence.

A successor must first use RC8A as an exposed qualification cohort, then freeze before a fresh prospective held-out source-binding cohort is authored.
