# CAL Strict Comparison Measurement Hardening RC0 — Preregistration

Date: 2026-09-17

Classification: Draft Research / adversarial measurement hardening.

## Frozen subject

This study does not create or repair a comparison instrument.

It pressure-tests the exact immutable RC7F-B1 comparator:

- evidence head: `0ecdedc5cea970485a635508255f3670ab231c33`
- comparator blob: `33820f55e2a87c4de6336fca6b5e5b93a2bccde3`
- prior terminal: `COMPARISON_INSTRUMENT_CANDIDATE_READY_FOR_HARDENING`
- prior science: 56/56 supported positives recovered, 0 false proposals.

The implementation is already known, so this is adversarial hardening rather than a fresh blinded held-out qualification. Candidate repair after observing this corpus is prohibited inside RC0.

## Question

Does the frozen comparator preserve its bounded semantics across additional entity forms and, critically, fail closed when comparison cues occur under material negation, epistemic modality, attribution, or conditional scope that its proposal type cannot represent?

## Buckets

### MUST_RETAIN

Representative cases from the already-supported jurisdiction:

- numeric delta;
- adjective + explicit measure head;
- comparative verb;
- equality;
- multiplier;
- scalar threshold.

Any miss or wrong typed attachment is a hard regression.

### DIAGNOSTIC

Fresh but nearby surfaces where a correct exact proposal is useful but abstention is acceptable:

- overlapping entity strings (`Women` / `Men`);
- hyphenated entities;
- degree/modifier words such as `slightly`;
- percentage-point verb delta;
- `half as ... as`;
- scalar `remained less than`.

A claimed diagnostic must be exact.

### FAIL_CLOSED

A plain positive comparison proposal is unsafe because it would erase material meaning not represented in the RC7F-B1 proposal:

- `not higher than`;
- `no higher than`;
- `probably higher than`;
- `allegedly higher than`;
- `may be higher than`;
- `could be higher than`;
- conditional `if ... higher than ...`;
- report-attributed comparison;
- negated equality;
- negated same-as;
- negated multiplier;
- multi-comparison conjunction/disjunction.

This is a measurement-representation test, not a semantic-warrant test. If the measurement emits an unqualified positive atom while dropping a material modifier, a later warrant layer cannot reconstruct that lost distinction from the proposal alone.

## Acceptance rule

RC0 hardening passes only if:

- all MUST_RETAIN cases are exact;
- every claimed DIAGNOSTIC is exact;
- zero FAIL_CLOSED case yields `CLAIMED`;
- exact comparator blob and production `src/` remain unchanged.

A failure is preserved as a hardening counterexample. Do not patch and recount inside this study.
