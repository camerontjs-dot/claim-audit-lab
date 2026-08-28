# CAL Contract C RC1 Producer / Result-Package Experiment Results

## Decision under review

Determine which information already produced or legitimately knowable at CAL's boundary constitutes a stable semantic result package, versus implementation telemetry, report presentation, compatibility projection, or destination-specific policy.

## Pinned live state

- CAL production and experiment base: `33a928db97316a3652d57df9cafb8ca240305233`.
- CAL research branch: `research/contract-c-result-package-rc1`.
- CAL draft PR: #15.
- Apparatus Contract-C umbrella: `camerontjs-dot/apparatus-contracts#11`.
- Preserved CAL RC0 producer research: CAL #13, treated as historical evidence only because it is based on an older Contract-B research lineage.
- Contract B production baseline referenced by current CAL production: 1.2.0, with legacy 1.0.0/1.1.0 intake compatibility preserved.

No production audit semantics were changed. No Contract-C version was assigned.

## Frozen evidence used

Production `AuditTrace` fixtures from the pinned CAL SHA:

- `15-not-checkable-no-evidence.json`, Git blob `5090d01dc35243b0542f4618ce59a08b7bd0e54e`;
- `16-not-checkable-no-entail.json`, Git blob `bbef26b91d2abcaa5908276d0215f10d3eb5612b`;
- `inference/inf-02-contradicted-logging.json`, Git blob `49b9fc71caebc849ed8bf8a96a12f1ddd24947b1`;
- `inference/inf-03-numeric-uptime.json`, Git blob `0ec4404e7267a3cf82b3774e6acce139d1cfc6d4`.

The richer eligibility/validity/aperture/temporal controls are explicitly synthetic boundary-state fixtures. They test representational distinctions, not a claim that current production emitted those exact packages from one execution.

## Executable result

Local decisive research suite before commit:

```text
python -m pytest -q tests/research/test_contract_c_rc1.py
16 passed
```

The branch CI receipt is recorded separately after the research commit is pushed.

## Observed evidence

### O1. Existing output objects are not interchangeable

Production `AuditTrace` is rich enough for deterministic verdict replay but contains implementation-level retrieval scores, raw logits, feature structures, rule explanation prose, and probes.

Additive `EvidenceDecisionTrace` cleanly distinguishes support/refutation measurements, eligibility, semantic validity, aperture, contribution state, and exact decision basis, but it is research-only/additive and is not itself established as the current production Contract-C object.

Structured `AuditReport` mixes semantic outcomes with summaries, risk labels, evidence display, explanations, rewrite guidance, and limitations prose.

Contract-B audited writeback is a compatibility projection and loses producer distinctions.

### O2. Same headline verdict does not imply same semantic result

Two frozen production traces both report `not_checkable` but differ materially:

- `no_evidence`: no entailment results and reason `no_evidence`;
- `no_entail_signal`: a neutral relation measurement exists and reason `no_entail_signal`.

Synthetic same-verdict controls additionally demonstrate consumer-sensitive differences in counterevidence, eligibility, semantic validity, aperture, temporal applicability, unresolved evidence, and exact basis while keeping the same `supported` headline result.

### O3. A verdict-only C2 loses behaviorally relevant distinctions

The thin C2 projection contains only proposition ID + headline verdict. It is byte-identical across several same-verdict residual-state mutations that cause publication, SOP/conformance, and investigation probes to behave differently.

### O4. Report derivation is one-way

C3 human Markdown is deterministic from identical C1 + renderer policy. Reverse reconstruction from C3 loses exact Contract-B hash, CAL code SHA, numeric measurement values, and reassessment lineage.

### O5. Some trace telemetry is safely ignorable for the tested projections

Holding semantic state constant, mutating the following does not change projected C1 content:

- raw retrieval score;
- raw entailment logits;
- claim token count;
- rule explanation prose.

Changing the aggregate semantic relation score changes C1. Changing audit-config identity or CAL code identity changes result identity.

This supports a distinction between semantic state and telemetry for these tested fields. It does not prove every unretained feature/probe field is non-semantic.

### O6. Field-family ablation produces real consumer failures

Deleting `identity`, `evidence`, `assessments`, `conclusion`, or `execution` breaks all four preregistered probes. Deleting `measurements` breaks reconstruction. Deleting `reassessment` breaks investigation lineage handling.

The experiment establishes family-level utility, not field-level minimality.

### O7. Unknown, absent, failed, not-applicable, and explicitly negative states can require different behavior

The assessment-state controls distinguish:

- incompatible field absence;
- not performed;
- performed but unknown;
- failed execution;
- not applicable;
- performed with an explicit negative result.

The consumer probes react differently to each where behavior materially changes.

### O8. Partial execution can be represented without laundering failure into subject semantics

A mixed result set contains one completed supported proposition and one proposition whose semantic operator failed. The run is `partial`; the failed proposition has no semantic verdict. The completed proposition remains unchanged.

A missing evidence reference is a structural validation failure and does not rewrite a supported verdict into an adverse subject finding.

### O9. Recomputed and superseding results require immutable identity + lineage

Changing audit config under the same Contract-B input produces a distinct recomputed result identity. Changing the Contract-B input binding produces a distinct superseding result. A prior-result relation distinguishes lineage.

`current` is not embedded in the immutable package in the RC1 shape. Selection of the current result is therefore treated as mutable registry/catalog state, not as an intrinsic historical fact.

### O10. Production `AuditTrace` is not provenance-complete for Contract C

`AuditTrace` does not include exact Contract-B bundle identity/hash/version. Trace-only projection therefore cannot satisfy exact B-to-C provenance binding. A boundary-aware producer can know those facts without new epistemic reasoning, but RC1 has not yet frozen a real current-production execution that captures both sides together.

### O11. The first C1 candidate fails the compression criterion

Canonical JSON sizes from the frozen executable harness:

| C0 case | C0 | C1 | Delta |
| --- | ---: | ---: | ---: |
| no-entail | 902 | 1,730 | +91.8% |
| contradicted-logging | 1,713 | 1,930 | +12.7% |
| numeric-uptime | 1,582 | 1,729 | +9.3% |

Even telemetry-heavy traces remain smaller than the verbose normalized candidate. The current C1 is therefore not materially smaller than C0.

### O12. True independent reproduction was not obtained

A mechanically isolated projector consumes only the candidate package and imports neither CAL nor the producer projector. It derives a publication-review projection and compact report successfully.

However, an attempt to commission a separate consumer through MainFrame Conduit found no active adapters. The mechanically isolated implementation was authored in the same research context and is not claimed as independent reproduction.

## Inference

1. Contract C needs a semantic layer between full trace and destination projection. Verdict-only and report-only objects are too lossy, while full trace carries implementation machinery that diverse consumers do not need.
2. Exact Contract-B binding, proposition identity, producer/config identity, semantic measurements/assessments, exact basis, residual state, execution state, and reassessment lineage are legitimate candidate families.
3. The current normalized **representation** is too verbose. Semantic richness and wire verbosity are separate variables. The next iteration should compress encoding and deduplicate run-level identity without dropping tested distinctions.
4. Compatibility writeback and human reports are downstream views over a richer CAL result, not the authoritative result package.
5. Mutable `current` status is more naturally resolved outside the immutable result artifact.

## Remaining hypotheses

1. A run-level identity/config/evidence table plus per-proposition references can make C1 materially smaller than the aggregate full internal trace while preserving all current ablation results.
2. Stable receipt/operator IDs can replace repeated verbose assessment/measurement structures without reducing reconstructability.
3. Some current feature/probe fields that look like telemetry may need normalized semantic receipts when they actually form the decision basis, especially numeric, negation, modality/scope, and decomposition-related operators.
4. `audit_confidence` may either be a stable semantic assessment or a presentation/control heuristic. RC1 does not yet discriminate.
5. A clean independently authored projector will reproduce the same semantics once the candidate is compacted and documented without implementation hints.

## Unknowns

- Exact C1 shape at a real current-production boundary with an actual Contract-B 1.2.0 bundle identity captured alongside the CAL result.
- Whether all semantically meaningful numeric/operator measurements can be represented as compact receipts without raw intermediate features.
- Field-level minimality inside the seven candidate families.
- Independent-consumer reproducibility under a genuine contamination boundary.
- Aggregate compression on a multi-proposition run after deduplicating run-level identity/config/evidence tables.
- Whether current consumer diversity requires raw relation scores or only typed outcomes + receipts.

## Falsified alternatives

### FA1. Contract-B compatibility writeback is already sufficient as Contract C

Falsified for the preregistered diversity criterion. It collapses `contradicted` and distinct `not_checkable` residual states.

### FA2. Headline verdict + proposition ID is a sufficient universal result

Falsified by same-verdict controls whose legitimate consumer behavior changes while C2 remains identical.

### FA3. Human report is a reconstructable semantic result package

Falsified by deterministic reverse information loss.

### FA4. Full `AuditTrace` must be carried because every trace field is necessary

Falsified within the tested projection scope. Retrieval scores, raw logits, token count, and rule explanation prose can mutate without changing candidate semantic content. This does not classify every trace field as telemetry.

### FA5. The first normalized C1 candidate is promotion-ready because it is cleaner than the trace

Falsified by the explicit size criterion. It is larger than all three frozen production traces measured.

## Promotion-criterion check

| Criterion | RC1 status |
| --- | --- |
| materially smaller than full internal trace | **not met** |
| materially richer than consumer-specific projection where diversity requires it | met for tested C2 controls |
| sufficient for preregistered consumers | met at current family-level test harness |
| sufficient for deterministic report derivation | met |
| explicit unknown/failure state | met in synthetic controls |
| provenance/identity bound | shape supports it, but real production trace-only fixture does not provide exact Contract-B binding |
| reproducible by an independent consumer | **not met**; only mechanically isolated same-context implementation |
| free of destination-specific decision policy | met for candidate C1; destination probes remain outside package |

Two hard promotion criteria are unmet and one provenance criterion is only shape-level rather than demonstrated on a real current-production execution.

## Smallest next evidence-producing iteration

Do not add a production exporter or Contract-C version.

Instead:

1. capture one real current-production CAL execution at the boundary with exact validated Contract-B 1.2.0 identity and the CAL result side by side;
2. refactor the research candidate into a compact run envelope that deduplicates producer/config/input/evidence identities and references per-proposition semantic records by stable IDs;
3. rerun the exact same consumer, report, unknown/failure, partial-run, lineage, and telemetry tests without relaxing any falsifier;
4. add targeted basis tests for numeric/negation/scope/decomposition intermediates before permanently classifying them as telemetry;
5. commission a clean projector from specification + frozen candidate bytes only, with explicit forbidden access to producer implementation.

## Final disposition

**NEEDS ITERATION**

The experiment supports the existence and rough semantic families of a Contract-C result layer, and it falsifies several tempting smaller existing objects. It does **not** support promotion of the current candidate representation because the candidate is larger than C0, exact live B-to-C binding is not yet demonstrated in one frozen execution, and independent reproduction remains unrun.
