# CAL Measurement Envelope RC0

Research-only implementation of the common information-preserving measurement boundary tracked in issue #93.

## Purpose

The envelope separates three things that earlier CAL designs tended to compress together:

1. the **audit context**: the exact claim/proposition and admitted evidence world available to CAL;
2. a **measurement observation**: what one instrument observed after consuming an explicit subset of that world; and
3. **semantic authority / proposition conclusion**: a later boundary that this envelope intentionally does not grant.

The core shape is:

```text
immutable AuditContext
  original claim
  typed proposition/decomposition
  exact Contract B binding
  complete admitted evidence world
          |
          +--> measurement instrument A --> MeasurementReceipt A
          |
          +--> measurement instrument B --> MeasurementReceipt B
          |
          +--> future instrument C -------> MeasurementReceipt C

AuditContext + verified receipts --> append-only MeasurementLedger

MeasurementLedger != warrant
MeasurementLedger != proposition verdict
```

## Available context vs consumed context

Every receipt carries the hash of the complete `AuditContext` and the complete list of admitted passage IDs available to the instrument invocation. It separately records `consumed_passage_ids` and any exact spans exposed by the measurement output.

This permits a narrow instrument to inspect one passage without causing the other admitted passages to disappear from the audit record. The ledger retains the full context object, so later instruments and eventual composition can reconstruct the evidence world that existed when the earlier measurement was made.

## Current instruments exercised

### RC7F-B1 strict comparison

Frozen dependency:

- commit `0ecdedc5cea970485a635508255f3670ab231c33`
- blob `33820f55e2a87c4de6336fca6b5e5b93a2bccde3`

This remains the reference measurement instrument for the already-operable RC0 strict-comparison path.

### RC7F-C explicit event ordering

Frozen dependency:

- commit `e8d33913db66ad21027dffdf731d50f7a0977c8f`
- blob `3e29b0e2ec5d9ba2d873d1584e76635147e421aa`

The event-ordering output is intentionally carried as a measurement proposal only. Its `MeasurementReceipt.authority_state` is `NOT_EVALUATED`. This experiment does not reuse comparison authority by analogy and does not derive a temporal proposition verdict.

## Integrity versus authority

`receipt_id` and `audit_context_sha256` are deterministic content identities. They detect stale or mutated context/receipt content in this bounded apparatus. They are not issuer authentication and are not semantic authority.

The existing RC0 strict-comparison path has separate authenticated atom/proposition and RC8J authority machinery. A later event-order successor must establish an appropriate temporal authority boundary before an event-order measurement can participate as deciding evidence.

## Deliberate non-features

There is no:

- retrieval;
- evidence admission decision;
- NLI threshold;
- score aggregator;
- majority vote;
- measurement confidence policy;
- terminal CAL verdict;
- Contract C projection;
- operational authorization.

Those omissions are part of the experiment. The envelope is meant to preserve measurement evidence for later warranted composition, not become another verdict engine.

## Evaluator

`evaluate.py` executes the preregistered positive controls and mutations against exact frozen RC7F-B1 and RC7F-C checkouts. The GitHub workflow verifies that the candidate remains outside production `src/**` and writes a terminal JSON receipt.
