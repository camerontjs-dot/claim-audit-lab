# CONTEXT-FREE REQUIRED: Frozen Authority Gate v1 Fresh Independent Reproduction

This packet defines a future scientific clean-room implementation experiment.

Do not execute this experiment in the RC8 research context that created the specification. Independence is part of the evidence.

## 1. Scientific question

Determine whether the frozen Authority Gate Specification v1 can be independently recovered and implemented from its normative specification alone.

The question is **recoverability**, not whether an agent can inspect a reference implementation and imitate it.

A genuine disagreement is useful evidence.

## 2. Pre-freeze information boundary

Before the independent implementation and its self-authored tests are frozen, the implementer may consume **only**:

1. this task packet;
2. `FROZEN_AUTHORITY_GATE_SPEC.md` at exactly:
   - repository: `camerontjs-dot/claim-audit-lab`;
   - specification freeze commit: `0a3d863580050751d8f87c5a73cfca82d4376901`;
   - path: `research/semantic_authority_machinery_rc8/FROZEN_AUTHORITY_GATE_SPEC.md`;
   - expected Git blob: `0f0981744646ab22a62d46a4e6535be0e7cdf773`.

No other project information is authorized pre-freeze.

## 3. Explicitly prohibited pre-freeze inputs

Do **not** retrieve, search, inspect, infer from, or use:

- prior conversations or project memory;
- personal context or summaries;
- this RC8 research thread;
- RC8/RC8A/.../RC8J results or preregistrations;
- any `authority_contract_rc8*.py` implementation;
- any RC8 cohort, fixture, evaluator or test file;
- `RESULTS.md`, `AUTHORITY_ARCHITECTURE.md`, `DEVIATIONS.md`, or integration notes;
- Git history outside the exact specification resource;
- repository search or directory listing;
- Contract B files outside what the frozen specification itself states;
- reference outputs;
- post-freeze reveal/comparator files;
- another agent's implementation or interpretation;
- web search or external semantic-authority guidance used to solve the task.

If unauthorized project-specific information becomes visible before freeze and could materially influence the implementation, record contamination rather than silently continuing as independent.

## 4. Exact-spec verification

Before implementation, verify that the supplied specification bytes correspond to Git blob:

`0f0981744646ab22a62d46a4e6535be0e7cdf773`

If the bytes cannot be verified, record a blocker and do not substitute a newer or nearby file.

## 5. Independent implementation task

Implement the frozen specification without consulting a reference implementation.

The implementation must expose this callable interface:

```python
def assess_authority(case: dict) -> dict:
    ...
```

The returned dictionary must contain the two normative keys:

- `authority_status`;
- `reason`.

Implementation language may be Python 3.11 for direct evaluator compatibility. The scientific semantics must come only from the frozen specification.

Recommended filename:

`authority_gate_independent.py`

The destination repository/directory is operational, not normative. It should be a fresh scratch location supplied by the operator and must not require browsing the Claim Audit Lab research tree pre-freeze.

## 6. Self-authored prereveal tests

Before any evaluator/reference reveal, author tests from the specification itself.

At minimum, the independent test set should exercise:

- execution vs evidence precedence;
- source missing/mismatch;
- bundle/passage missing/mismatch;
- admitted passage extent and exact-boundary containment;
- claim missing/mismatch;
- atom missing/mismatch;
- proposal/assertion/operator same-subject binding;
- assertion states;
- operator domain/applicability/governance;
- required-field jurisdiction, presence, binding, support span, typed status and value;
- composition required/not-required behavior;
- aperture required/not-required behavior;
- success;
- invariance to reader/instrument/confidence-style diagnostic growth.

Do not search for hidden evaluator cases while writing these tests.

## 7. Pre-reveal freeze

After implementation and self-authored tests pass to the implementer's satisfaction, freeze them **before** receiving any post-freeze packet.

Record at least:

- implementation path;
- implementation Git blob if in Git;
- implementation SHA-256;
- test path(s);
- test Git blob(s) if in Git;
- test SHA-256 values;
- exact prereveal test command;
- prereveal result and exit code;
- implementation/runtime identity;
- specification blob verified;
- any uncertainties or interpretations that remained unresolved;
- contamination status;
- freeze timestamp;
- freeze commit if applicable.

Recommended receipt filename:

`INDEPENDENT_PRE_REVEAL_FREEZE.json`

Once frozen, do not edit the implementation or prereveal tests and still count the edited result as independent agreement.

## 8. Required stopping point

After producing the pre-reveal freeze receipt, **stop**.

Do not inspect or request a reference implementation, evaluator, hidden cases, expected outputs or result history on your own.

The operator must separately authorize the post-freeze reveal packet after verifying that the prereveal implementation is frozen.

## 9. Scientific posture

Do not optimize to pass an unseen evaluator.

Implement what the frozen specification says. If a point is genuinely underdetermined, preserve that uncertainty in the prereveal receipt rather than importing unstated behavior.

A later disagreement may indicate:

- an implementation defect;
- a specification ambiguity;
- an evaluator/reference defect;
- a true alternative interpretation.

Those possibilities must be distinguished after reveal rather than repaired away.

## 10. Non-authorization

A successful independent reproduction would add recoverability evidence only. It would not by itself authorize:

- production CAL changes;
- Contract B or Contract C changes;
- merge or release;
- Contract C projection;
- semantic-text extraction promotion;
- Decision Engine operational authorization.
