# CAL Direct Event Order Measurement Hardening RC0 — Preregistration

Date: 2026-09-17

Classification: Draft Research / adversarial measurement hardening.

## Frozen subject

This study pressure-tests the exact immutable RC7F-C event-order instrument:

- evidence head: `e8d33913db66ad21027dffdf731d50f7a0977c8f`
- implementation blob: `3e29b0e2ec5d9ba2d873d1584e76635147e421aa`
- prior terminal: `EVENT_ORDERING_INSTRUMENT_CANDIDATE_READY_FOR_HARDENING`
- prior science: 44/44 supported explicit before/after cases and 0 false proposals on 16 negative/unsupported controls.

The candidate is already known. This is adversarial hardening, not fresh blinded qualification. Candidate repair after observing this corpus is prohibited inside RC0.

## Question

Does the frozen instrument preserve explicit two-event ordering while failing closed when `before` / `after` occur under attribution, conditionals, temporal-relation negation, fine-grained temporal modifiers, causal tails, or multi-event composition that its proposal type cannot represent?

## Buckets

### MUST_RETAIN

Representative inherited forms:

- positive BEFORE;
- positive AFTER;
- negative left event;
- negative right event;
- irrelevant preceding sentence.

### DIAGNOSTIC

Fresh but nearby exact two-event forms where a correct proposal is useful but abstention is acceptable:

- hyphenated actor;
- longer object;
- another frozen event verb;
- extra punctuation that does not alter semantics.

A claimed diagnostic must be exact.

### FAIL_CLOSED

Any plain two-event order proposal is unsafe if it drops material information not represented by RC7F-C:

- reporting wrapper;
- epistemic wrapper;
- conditional wrapper;
- `not before`;
- `immediately before`;
- `shortly before`;
- causal tail after the second event;
- conjunction/disjunction adding a third event;
- multiple ordering cues;
- non-event calendar/narrative uses.

## Acceptance

RC0 passes only if:

- all MUST_RETAIN cases are exact;
- every claimed DIAGNOSTIC is exact;
- no FAIL_CLOSED case yields a proposal;
- the exact RC7F-C implementation blob and production `src/` remain unchanged.

A failure is preserved as a hardening counterexample. No patch-and-recount is allowed inside this study.
