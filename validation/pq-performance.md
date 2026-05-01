# PQ: Performance Qualification

status: planned
last_updated: 2026-05-01

Purpose: verify that Claim Audit Lab performs consistently in representative full audit runs using checked-in fictional or sanitized data.

## Scope

PQ covers complete runs through the public workflow:

- draft input
- evidence bundle input
- claim extraction
- evidence matching
- rule checks
- report generation
- human-review calibration notes where research use is involved

## Required Example Families

| Family | Claim types | Minimum evidence | Status |
| --- | --- | --- | --- |
| AI research memo | numeric, causal, scope, interpretive | `examples/drafts/ai-research-note.md`, `examples/evidence/ai-research-evidence.yml`, generated Markdown and JSON reports | report family ready; protocol execution planned |
| Product README paragraph | capability, scope, comparative, prediction, stale-source behavior | `examples/drafts/product-readme-note.md`, `examples/evidence/product-readme-evidence.yml`, generated Markdown and JSON reports | report family ready; protocol execution planned |
| Neutral/adverse scaffold case | no-change, worse-output, false-caution behavior | research-use fixture family; see `../docs/research-use.md` | deferred outside v1 |

## Protocol

| Step | Command or inspection | Expected result | Status | Evidence |
| --- | --- | --- | --- | --- |
| PQ-001 | Run full audit for AI research memo. | Markdown and JSON reports are generated from checked-in data. | planned | TBD |
| PQ-002 | Run full audit for second fictional family. | Reports exercise labels and rule checks not covered by the AI research memo. | planned | TBD |
| PQ-003 | Inspect generated reports. | Reports include trace links, limitations, support labels, rule flags, and rewrite guidance where applicable. | planned | TBD |
| PQ-004 | Validate JSON reports against typed report models. | JSON report output round-trips through `AuditReport`. | planned | TBD |
| PQ-005 | Review examples for private data and local-only paths. | No private application materials, tokens, or local-only paths appear. | planned | TBD |
| PQ-006 | Compare a calibration sample against human review before research use. | Disagreements are documented rather than hidden. | planned | TBD |

## Acceptance Criteria

PQ passes when at least two complete example families can be run from checked-in data, reports are stable and inspectable, and known limitations are visible.

## Record

Full audit reports now exist for two fictional families. Do not mark this protocol `verified` until Phase 12 executes the protocol steps and records evidence.
