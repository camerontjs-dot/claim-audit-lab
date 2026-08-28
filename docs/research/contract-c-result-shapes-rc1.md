# Contract C RC1 Candidate Result Shapes

**Status:** experimental research shapes only.  
**No Contract-C version is assigned.**

The shapes below exist to make compression, reconstruction, consumer-diversity, execution-state, and lineage hypotheses falsifiable. They are not a production schema proposal.

## C0: full producer trace

C0 is the richest available producer-side record for the frozen case.

For current production controls this is `AuditTrace`, plus boundary context where the experiment explicitly supplies it. For richer semantic-state controls, `EvidenceDecisionTrace` concepts are used synthetically because that trace is additive research machinery rather than the current production verdict path.

Important observed limitation: production `AuditTrace` does not contain the exact Contract-B bundle identity. Therefore C0 trace bytes alone cannot satisfy Contract C's required B-to-C lineage binding.

## Candidate C1: normalized semantic package

Current research families:

```text
result_id
identity
  producer / code identity
  exact Contract-B binding
  proposition identity + text hash
  audit config identity
evidence
  retained evidence references
  counterevidence references
  unresolved evidence references
measurements
  normalized claim/evidence semantic measurements
assessments
  explicit performed / not performed / failed / not applicable state
conclusion
  CAL result
  typed reason / flags
  exact decision basis
  residual counterevidence / unresolved evidence
reassessment
  original / recomputed / superseding
  prior result identity
execution
  completed / partial / failed
  typed failures / deviations
```

`result_id` is deterministic over the immutable candidate content. Changing input binding, audit config identity, producer code identity, semantic measurements, semantic state, or lineage changes the result identity.

### Explicit assessment state model

RC1 uses only distinctions that change behavior in the preregistered controls:

- field absent: incompatible with the candidate profile or not part of that profile;
- `state: not_performed`: assessment was not performed;
- `state: performed, value: unknown`: assessment was performed but unresolved;
- `state: failed, failure: ...`: attempted assessment did not complete;
- `state: not_applicable`: assessment does not apply;
- `state: performed, value: <negative>`: explicit negative result such as invalid/ineligible.

No extra unknown taxonomy is introduced unless a behavioral distinction requires it.

### Result-set envelope for partial execution

A research-only result-set wrapper carries:

```text
result_set_id
exact Contract-B binding
results[]
run execution state
```

A frozen control contains one completed proposition and one proposition whose semantic operator failed. The result set is `partial`; the completed proposition remains `supported`; the failed proposition has no semantic verdict. Execution failure is not converted into an adverse claim finding.

The current wrapper intentionally retains redundant Contract-B identity inside each proposition result as well as at run scope. RC1 measures this redundancy rather than deleting it first and declaring compression achieved.

## C2: deliberately thin consumer projection

Current control:

```json
{
  "proposition_id": "...",
  "reported_verdict": "..."
}
```

C2 is useful precisely because it is too small. Same-headline `supported` cases with different counterevidence, eligibility, validity, aperture, temporal applicability, unresolved evidence, and decision basis collapse to the same C2 bytes even when preregistered consumers behave differently.

C2 is therefore a projection, not a universal semantic handoff candidate.

## C3: human report

C3 is deterministic Markdown derived from C1 plus an explicit renderer policy ID. It includes proposition text, result ID, execution state, headline result, basis, residual state, and assessment-state summary.

Two derivations from identical C1 + renderer policy are byte-identical in RC1.

Attempted reverse reconstruction from C3 fails. The report intentionally omits at least:

- exact Contract-B bundle hash;
- CAL producer code SHA;
- numeric semantic measurement values;
- reassessment lineage.

Therefore the human report is a view over the semantic package, not the semantic package itself.

## Compression measurements

Canonical JSON byte counts from frozen production traces:

| Frozen C0 case | C0 bytes | candidate C1 bytes | C1 / C0 | Result |
| --- | ---: | ---: | ---: | --- |
| `16-not-checkable-no-entail` | 902 | 1,730 | 1.918x | fails smaller-than-trace criterion |
| `inf-02-contradicted-logging` | 1,713 | 1,930 | 1.127x | fails smaller-than-trace criterion |
| `inf-03-numeric-uptime` | 1,582 | 1,729 | 1.093x | fails smaller-than-trace criterion |

The larger inference traces contain substantial raw logits, probabilities, retrieval telemetry, and a negation probe, yet the current normalized C1 envelope is still larger. This falsifies the current C1 representation as promotion-ready under the preregistered compression criterion.

An earlier ad hoc measurement used one shorter fixed surrogate binding and produced C1 sizes of 1,913 and 1,712 for the two larger traces. The frozen harness uses the per-fixture surrogate binding and records 1,930 and 1,729. The apparatus refinement changes exact byte counts but not the conclusion. It is preserved in the failed-attempt/deviation record.

## What the compression failure does and does not establish

### Established for this candidate

- Removing raw telemetry is not enough to guarantee a smaller transport representation.
- Repeating verbose family names, assessment envelopes, evidence references, and per-proposition identity can outweigh removed telemetry.
- The current C1 shape cannot satisfy the stated promotion criterion as written.

### Not established

- that a semantic package must be larger than `AuditTrace`;
- that telemetry belongs in Contract C;
- that exact provenance should be dropped to save bytes;
- that a compact run-level envelope cannot amortize identity/config fields across many propositions;
- that stable receipt IDs cannot replace verbose repeated structures.

The next candidate should compress representation without compressing semantic distinctions.
