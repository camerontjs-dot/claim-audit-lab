# Claim Audit Lab V1 integration-candidate result

- Profile: 'cal-v1-integration-candidate-v1'
- Distribution metadata: 'claim-audit-lab 0.6.0'
- Semantic implementation: '847cc970642bb648dc994b929c2053b5c9d4648c'
- Proposition: Alice reviewed dossier before Bob archived dossier.
- Proposition ID: 'C2'
- Proposition text SHA-256: 'fafacbe46796663d673cdcbf3e53860e50cad3e9dd4566dc47ac116b5b4e309f'
- Semantic family: 'direct_event_order'
- Conclusion: 'contradicted'
- Failure localization: none
- Contract B: '1.2.0' / 'd2915bdc-bd20-5f6f-8f6f-f06ddc1a8f7b'
- Contract B bundle hash: 'sha256:c7be5440f4da6d3b3560848bc04025bcf45e45783f0925501d3a844f70f939cb'
- Evidence-world SHA-256: 'e368929d13822e40d14283c80e89d82239601abf77e40ff60c455834ddc8acde'
- Composition rule: 'scoreless-categorical-v1'
- Contract C handoff: 'not_emitted' (separate compose-only versioned layer).
- Authorization: 'not_evaluated'; automatic action is not allowed.
- Limitation: CAL decides only within the supported semantic envelope and admitted evidence.

## Upstream aperture observation

```json
{
  "contract_b_factual_context_state": "present",
  "observation": {
    "claim_id": "C2",
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
        "not_retained_count": 0,
        "rejected_count": 0,
        "retained_count": 3,
        "returned_count": 3,
        "status": "completed"
      }
    },
    "search_scope": {
      "candidate_depth_limit": 10,
      "config_sha256": "sha256:5b10d0c29794e80d6876a99e26bcf6ec6a27a4c5165aee78054a6bc32759f4bc",
      "query_id": "query:5747a15d23f15b2208c632eda525cb4f",
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
      "retrieval_id": "retrieval:27ed82ed47707df2d3b460b1cc0fd414",
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

### 'passage:cdfce7346d70aaa440927df2a1467e3d': counterevidence

Alice reviewed dossier before Bob archived dossier.

Source: 'S-C2-SUPPORT'; passage SHA-256: 'sha256:fafacbe46796663d673cdcbf3e53860e50cad3e9dd4566dc47ac116b5b4e309f'.
Measurement: 'rc7fc-event-order' / 'rc7fc-event-order-1' / receipt 'measurement:f0289997e70f63b11b5e141210367fd81a3dd77a0563f5699a760f1538f9a7c9'.
Authority: 'semantic-authority:c1758e9ca3d6a47d6fcb3643caa5252bb25da0555342208a025ed83bed462036'.
Relation: 'REFUTES' / 'bound-relation:0fb7ba0d3f1ef3f8fa70534675df2345b11d98b1e5c167b921d4bb8208781dc7'.
Failure localization: none.
