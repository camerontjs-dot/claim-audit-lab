# Claim Audit Lab V1 integration-candidate result

- Profile: 'cal-v1-integration-candidate-v1'
- Distribution metadata: 'claim-audit-lab 0.6.0'
- Semantic implementation: '847cc970642bb648dc994b929c2053b5c9d4648c'
- Proposition: Alpha had a higher rate than Beta.
- Proposition ID: 'C1'
- Proposition text SHA-256: 'e6f2ac2792789b8430ea3468071801712f25b7386f7641b415f859fd7aea9601'
- Semantic family: 'strict_comparison'
- Conclusion: 'contradicted'
- Failure localization: none
- Contract B: '1.2.0' / '78977d18-2eb1-5b1a-bd29-bd1ea8361d1a'
- Contract B bundle hash: 'sha256:9dd3aa55b5bf2329299c6cb3e4540b2587027a3baf7949578ab165d6938f39fe'
- Evidence-world SHA-256: 'd41e45cdd8552d31e395a38211f94a57bfd394cb64bdc9d4584ab37fccf1a602'
- Composition rule: 'scoreless-categorical-v1'
- Contract C handoff: 'not_emitted' (separate compose-only versioned layer).
- Authorization: 'not_evaluated'; automatic action is not allowed.
- Limitation: CAL decides only within the supported semantic envelope and admitted evidence.

## Upstream aperture observation

```json
{
  "contract_b_factual_context_state": "present",
  "observation": {
    "claim_id": "C1",
    "limitations": [
      "B1.2 lacks native admission_state=not_applicable; non-retained candidates use review.decision=needs-review only as compatibility encoding while preserving native_admission_state=not_applicable.",
      "Candidate depth is bounded and does not establish corpus completeness.",
      "No support, refutation, applicability, completeness or verdict is emitted.",
      "Nomination, retention and admission are distinct non-semantic stages."
    ],
    "outcome": {
      "state": "known",
      "value": {
        "accepted_count": 1,
        "aperture_state": "bounded_under_limit",
        "candidate_depth_hit": false,
        "needs_review_count": 2,
        "not_retained_count": 2,
        "rejected_count": 0,
        "retained_count": 3,
        "returned_count": 5,
        "status": "completed"
      }
    },
    "search_scope": {
      "candidate_depth_limit": 10,
      "config_sha256": "sha256:5b10d0c29794e80d6876a99e26bcf6ec6a27a4c5165aee78054a6bc32759f4bc",
      "query_id": "query:ca5c997653141eba480738f49c4daa0c",
      "requested_source_ids": [
        "S-C1-REFUTE",
        "S-C1-SUPPORT",
        "S-C2-SUPPORT",
        "S-D01",
        "S-D02",
        "S-D03",
        "S-D04",
        "S-D05",
        "S-D06",
        "S-D07"
      ],
      "retained_k": 3,
      "retrieval_id": "retrieval:dd6c50f19341b01c71f8fd3db3a95143",
      "retrieval_lane": "declared_child",
      "searched_source_ids": [
        "S-C1-REFUTE",
        "S-C1-SUPPORT",
        "S-C2-SUPPORT",
        "S-D01",
        "S-D02",
        "S-D03",
        "S-D04",
        "S-D05",
        "S-D06",
        "S-D07"
      ]
    }
  }
}
```

## Evidence trace

### 'passage:170f80a49ae83ccb680d9ace6efc5942': counterevidence

Alpha had a higher rate than Beta.

Source: 'S-C1-SUPPORT'; passage SHA-256: 'sha256:e6f2ac2792789b8430ea3468071801712f25b7386f7641b415f859fd7aea9601'.
Measurement: 'rc7fb1-strict-comparison' / 'rc7fb1-comparator-1' / receipt 'measurement:e8f0b77f003111aeaa9d820d0b76a78aeaac3ab85c33483677474dc6eb28d5e7'.
Authority: 'semantic-authority:ff8e093d96853d442e7ebf05b05127d9cea48eba5e494f693731d1eacba0af94'.
Relation: 'REFUTES' / 'bound-relation:97c8a86a867f034d19055d3af5b502934227d395ad730173fd10543c36da367f'.
Failure localization: none.
