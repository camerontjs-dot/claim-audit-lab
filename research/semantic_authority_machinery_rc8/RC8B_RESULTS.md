# RC8B Bound Authority-Receipt Successor — Results

## Disposition

**SUPPORTED WITHIN THE FROZEN PROSPECTIVE ENVELOPE.**

RC8B repaired the specific partial-subreceipt substitution and required-field support-span defect exposed by RC8A without regressing the previously exposed RC8 authority-state cases.

This result is not production authorization and is not a clean-room independence result.

## Frozen identities

- RC8B preregistration: `330c48dd11c6b685229671eca1731d8aaab3c3d4`
- RC8B candidate freeze declaration: `e52f70b77ed0395e33afa9b193cae47475abf892`
- candidate blob: `edf84bb5aae0dd217e3f780e7a49767440b7c1e5`
- prospective apparatus freeze head: `4a4046c921f70156e270cc9c036cfb49ffe23b8f`
- pre-reveal seal run: `33650759366`
- pre-reveal job: `100316980681`
- reveal workflow commit: `67421ac98abf46f3149ed6cf04954fcabd45ef96`
- reveal run: `33650949918`
- prospective science job: `100317656073`
- prospective result artifact: `9854745739`
- artifact digest: `sha256:9b6c9b24ed7eff15ac726b68d5f27000fed796015ae19bf22600291311fb6293`

The reveal job reverified the frozen candidate and all frozen apparatus identities before executing the candidate.

## Exposed qualification before freeze

RC8B was tuned only against already exposed evidence:

- RC8 open qualification;
- the exposed RC8 68-case held-out cohort converted to valid bound receipts;
- the exposed RC8A seven-case source-binding falsifier.

Accepted exposed qualification run `33650127191`, job `100314883140`:

- cases: `112`
- status exact: `112 / 112`
- reason exact: `112 / 112`
- unsafe warranted atoms: `0`

These numbers are qualification evidence only.

## Prospective result

Fresh post-freeze cohort:

- cases: `50`
- expected/observed states: `25 REJECTED`, `16 UNRESOLVED`, `8 WARRANTED`, `1 NO_ASSESSMENT`
- status exact: `50 / 50`
- reason exact: `50 / 50`
- unsafe warranted atoms: `0`
- explicit subject-mismatch exact rejections: `11 / 11`
- missing-binding cases not warranted: `7 / 7`
- agreement-bank invariance: `true` for warranted and unresolved controls
- scientific state: `BOUND_RECEIPT_GATE_SUPPORTED_WITHIN_PROSPECTIVE_ENVELOPE`

The cohort covered missing and mismatched binding at assessment/proposal/assertion/operator/field/composition/aperture layers, deterministic mismatch precedence, field support-span boundary/outside cases, semantic unknown versus extraction unresolved, optional composition/aperture, prior semantic rejection/unresolved states under valid binding, execution/evidence precedence, and reader/instrument bank growth.

## What this establishes

Within the frozen synthetic typed-receipt envelope:

1. explicit same-subject binding blocks partial authority-fragment substitution;
2. missing authority bindings fail closed as unresolved rather than acquiring authority;
3. explicit mismatches reject rather than abstain;
4. required-field support spans outside operator governance reject;
5. source semantic unknown remains distinguishable from extraction unresolved;
6. reader/instrument agreement remains authority-inert;
7. the added binding checks did not weaken the previously supported RC8 state transition on exposed regression cases.

## What this does not establish

The result does **not** establish:

- that an opaque `authority_subject_id` is itself correctly anchored to the admitted evidence source;
- authenticity or trustworthiness of the receipt producer;
- natural-language recovery of authority receipts;
- production CAL integration;
- Contract B or C projection semantics;
- Decision Engine policy;
- independent recoverability by a fresh implementer.

## Remaining highest-weight assumption

RC8B still assumes that the opaque `authority_subject_id` belongs to the `raw_source_id` whose evidence was admitted. The gate checks consistency among receipt fragments but does not itself check source-anchor consistency.

That assumption is now the smallest high-value target for a follow-on falsifier. Until it is tested, RC8B should be described as a **bound-receipt consistency gate**, not a complete evidence-to-authority binding contract.
