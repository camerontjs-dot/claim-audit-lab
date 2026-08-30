---
title: "Independent-consumer candidate assessment"
privacy: "private-local"
---

# Independent-consumer candidate assessment

Desired test, not implemented here:

> Given only the parallel epistemic artifact and its declared contract, can an independent consumer identify evidence state, semantic unknowns, provenance, execution failure, and causal decision basis without importing CAL's legacy terminal-verdict logic?

## Nomination

| Rank | Candidate | Why | Caveat |
|---:|---|---|---|
| 1 | PR #37 25-case parallel artifacts (already emitted on GitHub) | Small, receipt-bound, includes e2e-08 unknown and e2e-09 unmeasured, plus a missing-evidence case | consumer would still need the artifact schema from the PR |
| 2 | Construction-gold 33 **input-only** after Cohort A executes | source_boundary, distractors, multi-doc, absence vs contradiction | do not hand the consumer `expected_verdict` |
| 3 | SLG-08 / SLG-09 all_of packets | mixed/partial membership is the compression the legacy verdict hides | Cohort B not frozen |
| 4 | EB challenge-corpus-v1 (evaluator-held gold) | CLEAN_SEPARABLE; independent of CAL terminal vocabulary | different owner; retrieval corpus more than decision corpus |

## Not nominated

- PILOT-001: human gold and CAL history are too easy to smuggle as the “right” answer.
- Stub e2e expected verdicts: they disagree with real NLI on the interesting case.
- X5 twins: pending signoff; invariance labels are still assessment.

## Why e2e-08 is the best single consumer item

An independent reader who only sees `contradicted` from legacy CAL cannot reconstruct:

- A4 inapplicable / null target
- missing typed numeric operator
- high `p_contradict` that is not a validated numeric relation

If the parallel artifact exposes those distinctions, the consumer test passes. If the consumer must look up C6a or the stub expected verdict, it fails.

Do not implement the consumer in this audit.
