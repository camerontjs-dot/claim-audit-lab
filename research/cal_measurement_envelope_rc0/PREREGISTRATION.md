# CAL Measurement Envelope RC0 Preregistration

## Class

Draft Research Infrastructure experiment. No production `src/**` change, release, promotion, Contract B/C amendment, Decision Engine change, Contract E change, or operational authorization.

## Frozen parent

- Parent research evidence record: PR #91
- Exact parent head: `7a46d61585f868a2e904f870528f605fb06772ea`
- Parent branch: `research/cal-pipeline-data-campaign-rc0-20260907`
- Production `main` at experiment start: `32275a239b68af383a56bca843e28cbc1e343976`

## Existing measurement evidence used as fixed dependencies

- strict comparison RC7F-B1: `0ecdedc5cea970485a635508255f3670ab231c33`
- strict comparison implementation blob: `33820f55e2a87c4de6336fca6b5e5b93a2bccde3`
- explicit event ordering RC7F-C: `e8d33913db66ad21027dffdf731d50f7a0977c8f`
- explicit event ordering implementation blob: `3e29b0e2ec5d9ba2d873d1584e76635147e421aa`
- frozen RC8J comparison authority: `8e75c6782bb95c3763d06230b9c5df2b6af44054`

RC7F-C is measurement evidence only. This experiment must not represent event ordering as warranted or deciding unless a separate event-order authority experiment exists.

## Research question

Can CAL represent multiple independent semantic measurements under one common, lossless audit-context envelope such that:

1. every measurement remains bound to the exact original claim/proposition and exact admitted Contract B evidence world;
2. each measurement declares the subset of evidence/spans it actually consumed;
3. non-consumed admitted evidence remains recoverable after measurement;
4. measurements are append-only and do not replace the audit context;
5. measurement ordering does not alter the canonical ledger identity;
6. a second semantic family, explicit event ordering, can use the same envelope without strict-comparison-specific schema assumptions; and
7. the envelope itself grants no semantic authority and emits no proposition verdict.

## Candidate architecture

`AuditContext`

- exact original claim ID and text;
- exact proposition ID and typed proposition payload;
- decomposition path;
- Contract B version, bundle ID and bundle hash;
- complete admitted passage set including exact source ID, passage ID, passage hash and passage text.

`MeasurementReceipt`

- exact `audit_context_sha256`;
- instrument ID/version and semantic family;
- measurement status;
- exact available admitted passage IDs;
- exact consumed passage IDs;
- consumed spans, where the instrument identifies spans;
- raw measurement proposals/residue/diagnostics;
- explicit authority state `NOT_EVALUATED`;
- deterministic receipt ID over canonical receipt content.

`MeasurementLedger`

- contains the immutable `AuditContext` plus zero or more verified measurement receipts;
- canonicalizes receipts by receipt identity so insertion order cannot change ledger identity;
- provides no verdict/scoring/voting surface.

## Hard invariants / falsifiers

The candidate is falsified if any of the following occurs:

1. **claim mutation survives binding**: a receipt verifies against changed original claim text or proposition payload;
2. **evidence-world mutation survives binding**: a receipt verifies after admitted passage membership, passage text/hash, bundle ID or bundle hash changes;
3. **out-of-aperture consumption**: a receipt can name a consumed passage not present in the admitted context;
4. **invalid span accepted**: a consumed span outside its named passage is accepted;
5. **available-context shrinkage**: a receipt can claim an available passage set smaller/different from the bound admitted context;
6. **lossy ledger**: after appending a one-passage measurement, another admitted passage can no longer be reconstructed from the ledger context;
7. **order dependence**: the same valid receipt set appended in different orders yields different canonical ledger identity;
8. **family coupling**: the event-ordering instrument cannot be represented without adding comparison-specific fields to the common receipt schema;
9. **authority laundering**: an event-order measurement receipt is represented as `WARRANTED`, `SUPPORTS`, `REFUTES`, `supported`, `contradicted`, or otherwise deciding merely because the measurement returned `CLAIMED`;
10. **measurement-to-verdict surface**: the common envelope exposes a terminal verdict, confidence-threshold, majority-vote, or score-aggregation decision API.

## Positive controls

- RC7F-B1 on `Alpha exceeded Beta by 4 units.` must preserve its raw `CLAIMED` proposal exactly inside a verified receipt.
- RC7F-C on an explicit two-event before/after sentence must preserve its raw `CLAIMED` proposal exactly inside a verified receipt.
- Both receipts must bind to the same full audit context while declaring only the passage they individually consumed.

## Weak / mutation controls

At minimum:

- original claim text mutation;
- typed proposition mutation;
- bundle hash mutation;
- admitted-set removal;
- passage-text mutation with stale passage hash;
- foreign consumed passage ID;
- out-of-range span;
- available-passage-set omission;
- proposal mutation with stale receipt ID;
- reversed receipt insertion order;
- strict-comparison and event-order receipts coexisting in one ledger.

## Interpretation boundary

A passing experiment establishes only that a common information-preserving measurement envelope can carry two existing bounded measurement families without making measurements authoritative or deciding.

It does not establish generic semantic understanding, event-order authority, root composition, evidence completeness, source legitimacy, learned-model validity, production key management, production CAL architecture, release, merge or promotion.

## Successor if supported

The smallest next scientific boundary is an event-ordering authority/warrant experiment that asks what exact event identities, polarity, source spans, scope and proposition binding must be established before a temporal measurement may produce a proposition-relative categorical relation. Do not reuse the comparison authority family by analogy alone.
