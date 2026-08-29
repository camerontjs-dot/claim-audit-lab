# RC0B Phase-1 Source Aperture

Status: ACTIVE, PRE-FREEZE

Production baseline: `e90f301cf6ca02c0c77b6e88c3b08f8b93b9a36a`
Research branch: `research/epistemic-methodology-rc0b`

## ALLOWED

Before evaluator freeze, use only:

1. The seven explicitly named attached CAL Pipeline governance documents if actually available through the attached/connected project source.
2. Current production CAL source, tests, trace structures, fixtures, and public documentation at the exact verified live `main` identity.
3. Immutable released CAL v0.5.0 and its released artifacts/traces/fixtures.
4. Immutable released Contract B and Contract C artifacts needed to determine current/released semantics.
5. CAL issue #3, “Research: harden CAL’s Contract-B consumer seam”.
6. The seven sanitized RC0 predecessor facts supplied in the RC0B preregistration.
7. The six-item RC0 evaluator defect list supplied in the preregistration.
8. The single supplied RC0A procedural-failure fact.
9. Identity-only ref/commit endpoints for production main, v0.5.0, Contract C, RC0 head, and historical-v2 head, only when the response cannot expose bodies, diffs, candidate code, or result summaries.

## FORBIDDEN

Before evaluator freeze, exclude:

- PR #28 body, comments, diff, changed files, and candidate-comparison material.
- PR #29 body or terminal record.
- `research/epistemic-methodology-rc0`.
- `research/epistemic-methodology-rc0a`.
- `feat/v2-epistemic-pipeline`.
- historical-v2 source, tests, comments, and historical-v2 `pipeline_rules.py`.
- RC0 candidate adapters, comparison tests, gate vectors, and candidate result documents.
- all-branch/history code search for epistemic candidate terminology.
- GitHub search-result snippets that expose forbidden candidate information.
- external/deep-research epistemic-abstention synthesis.
- prior conversation summaries or architecture discussions describing candidate performance or preferences.

## OBSERVED ACCESSES

| Resource | Exact ref/SHA where possible | Why allowed | Expected-only response? |
|---|---|---|---|
| Current project context self-check | current RC0B context | Mandatory fresh-context check | YES: no prohibited candidate observations, gate vectors, historical-v2 mechanism details, or architecture conclusions |
| Uploaded-file exact-title searches for seven governance docs | n/a | Attached governance is allowlisted | YES: no matches returned |
| Connected Drive exact-title searches for seven governance docs | n/a | Attached governance is allowlisted | YES: no matches returned |
| GitHub user identity | `camerontjs-dot` | Exact repository resolution without broad discovery | YES |
| Repository metadata | `camerontjs-dot/claim-audit-lab`, repository id 1298242840 | Exact repository resolution | YES |
| `refs/heads/main` | `e90f301cf6ca02c0c77b6e88c3b08f8b93b9a36a` | Live production identity verification | YES |
| `refs/tags/v0.5.0` | annotated tag object `193c07178a8d891231746fca97c8c1bef0e9dc3c` | Immutable release identity verification | YES |
| v0.5.0 annotated tag object | commit `5533bbcf27a3ee3a7d901f7dfc44c241bc558e2c` | Mechanical tag dereference | YES |
| production main commit object | commit `e90f301cf6ca02c0c77b6e88c3b08f8b93b9a36a`, tree `8f000cc4cd973555b88d97ce1b73ef7b40c433a2` | Current-production tree identity | YES |
| production main tree | tree `8f000cc4cd973555b88d97ce1b73ef7b40c433a2` | Current production source/tests are allowlisted | YES: current-production path/blob metadata only |
| `refs/tags/contract-c-v1.0.0` in CAL repo | unresolved / 404 | Narrow attempt to verify Contract C identity | YES: no content |
| CAL issue #3 | issue #3 | Explicitly allowlisted | YES: issue body only; no predecessor PR or historical candidate source was followed |
| Current production `src/claim_audit_lab/v1` directory listing | baseline commit | Current production source is allowlisted | YES |
| Current production `src/claim_audit_lab/v1/impl` directory listing | baseline commit | Current production source is allowlisted | YES |
| Local exact-commit shallow fetch attempt | baseline commit requested | Current production source would be allowlisted | YES: network resolution failed before any repository data was returned |
| RC0B branch creation | `research/epistemic-methodology-rc0b` from baseline | Required isolated research branch | YES |
| Initial aperture-record Git tree/commit | commit `744563296ada8220fc05dfa4c7336b423764d185` | Required durable Phase-1 aperture record | YES: created from baseline with only this research record |

## DEFERRED / UNRESOLVED PRE-FREEZE IDENTITIES

- Attached governance documents are unavailable through both uploaded-file and exact-title connected Drive searches.
- Contract C tag location is unresolved in the CAL repository.
- RC0 head and historical-v2 head remain deferred unless a strictly identity-only ref endpoint can verify them without exposing branch content.

## CONTAMINATION RULE

Any unexpected exposure of candidate implementation details, candidate results, candidate gate vectors, historical-v2 mechanism details, or external methodology conclusions before freeze terminates RC0B without architecture inference.

Authority does not imply unrestricted visibility. Links from allowed resources are not followed unless separately allowlisted.

## FIREWALL STATUS

As of this record, the pre-freeze firewall has held. No forbidden candidate or historical-v2 implementation/result material has been retrieved.
