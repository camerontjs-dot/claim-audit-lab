# CAL Epistemic Methodology RC1A — Frozen Apparatus Receipt

This is the durable record of the required post-freeze, pre-candidate evaluator execution.

## Freeze identity

- evaluator freeze commit: `9b0d03a830367dc527c94663187e51cebe56cd16`
- frozen evaluator blob: `a0db04b322632d2d52dfb0bdf53824881d3e7b07`
- Draft research PR: #33
- candidate present in the hosted receipt: `false`

## Hosted execution

- workflow run: `33270463090`
- RC1A evaluator step: `success`
- artifact id: `9719947552`
- artifact name: `rc1a-receipts-9b0d03a830367dc527c94663187e51cebe56cd16`
- artifact digest: `sha256:ec787bc71add1596de9094473c16d17cf03116d25839f687d4eb5fcde56efdda`

## Protected-object check

Every protected production and fixture object matched the frozen identity encoded in the evaluator, including unchanged current v1 `run_audit`/pipeline/intake/model surfaces, Contract C implementation, production rule/model adapter surfaces, the full current v1 trace-corpus tree, and the frozen Contract-B fixture tree.

## Weak controls

| Control | Expected defect | Observed failed gate(s) | Rejected |
| --- | --- | --- | --- |
| W1 | RC1-style post-hoc sidecar does not prove real execution/input-boundary capture | Gates 1, 13 | yes |
| W2 | source trust masquerades as proposition assessment | Gate 5 | yes |
| W3 | terminal reason without typed assessment/participation | Gates 5, 6, 12 | yes |
| W4 | causal necessity echoed without intervention | Gate 10 | yes |
| W5 | policy identity logged without policy effect | Gate 7 | yes |
| W6 | missing epistemic state silently defaulted | Gate 12 | yes |

## Chronology decision

The frozen evaluator remained operational after freeze and all weak controls were rejected for their preregistered defects. Therefore candidate implementation is authorized to begin after this observation.

This does not authorize any production change or any modification of the frozen RC1A apparatus.
