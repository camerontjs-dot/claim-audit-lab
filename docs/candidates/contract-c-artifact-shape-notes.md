# Contract C Artifact Shape Notes

**Status:** OPEN DESIGN NOTE  
**Parent profile:** `contract-c-cal-producer-profile-rc0.md`  
**Purpose:** narrow the physical/result shape before any Contract-C test plan is written

## 1. Problem

The CAL producer profile establishes semantic ownership but does not yet determine how those semantics should be packaged.

Current CAL has two relevant precedents:

1. **`AuditTrace` per claim** — compact, replay-oriented, CAL-owned detail;
2. **resealed audited C-B bundle** — self-contained compatibility output, but mixes upstream evidence and downstream result state and flattens some CAL distinctions.

The research decision machinery adds a third precedent:

3. **receipt-bound contribution/assessment trace** — richer epistemically, but currently implementation-shaped rather than contract-shaped.

The packaging decision should not be made by copying whichever implementation object happens to exist today.

---

## 2. Candidate A — audited Contract B remains the canonical result

```text
Contract B input
    ↓ copy
Audited C-B derivative
  + audit blocks
  + CAL traces
  + resealed hashes
```

### Advantages

- current implementation already exists;
- self-contained bundle;
- compatible with current apparatus expectations;
- upstream evidence and downstream result travel together.

### Problems

- CAL result semantics are constrained by an upstream contract vocabulary;
- current writeback is observably lossy (`contradicted → unsupported`, richer reasons only in trace);
- ownership is visually and structurally blurred;
- each re-audit duplicates the evidence bundle;
- a downstream reader may confuse CAL-derived fields with original B facts;
- multiple CAL policies over the same B input produce multiple near-duplicate evidence bundles.

### Current disposition

**Keep as compatibility baseline, not preferred canonical C hypothesis.**

---

## 3. Candidate B — immutable CAL run package bound to Contract B

```text
contract-c/{result_set_id}/
  manifest
  input_binding
  propositions/
    {proposition_id}/
      result
      measurements
      assessments
      contributions
      decision
  receipts/
    ...
  deviations/
    ...
  integrity
```

This is a logical layout only.

### Advantages

- clean ownership: B remains evidence, C remains CAL result;
- one B can support many immutable C results under different policies;
- no need to duplicate all evidence content;
- measurement / assessment / decision can remain separate;
- easy to preserve non-deciding contributions;
- supports proposition-level results plus run-level identity;
- human-readable reports can project from C without becoming canonical.

### Risks

- a C result may not be portable without its referenced B artifact;
- receipt normalization can become over-engineered;
- deciding which data are duplicated for convenience versus referenced by hash is non-trivial;
- downstream consumers now need two linked artifacts rather than one self-contained tree.

### Current disposition

**Leading hypothesis.**

---

## 4. Candidate C — one monolithic proposition trace

```text
result-{proposition_id}.json
  input refs
  all measurements
  all assessments
  all contributions
  decision
  config/model metadata
  history refs
```

### Advantages

- simple transport;
- one object can be hashed and signed;
- easy to archive per proposition;
- close to the existing `AuditTrace` mental model.

### Problems

- repeated run/config/input metadata across many propositions;
- shared receipts become duplicated;
- parent/child composition becomes awkward;
- run-level deviations and partial execution are harder to represent cleanly;
- large monolith encourages mixing semantic layers because everything lives together.

### Current disposition

**Useful interchange projection; probably too coarse as the canonical storage model.**

---

## 5. Candidate D — append-only CAL event / receipt ledger

```text
run manifest
receipt/event ledger
  intake_verified
  measurement_recorded
  assessment_recorded
  contribution_created
  view_derived
  decision_recorded
  reassessment_recorded
```

Current state is reconstructed from the ledger.

### Advantages

- natural immutability and history;
- excellent forensic reconstruction;
- reassessment and supersession fit cleanly;
- no destructive updates;
- semantic ownership can be explicit per receipt/event.

### Problems

- more machinery than the current problem may require;
- downstream readers must replay/project the ledger;
- canonical ordering and event semantics become a substantial contract in their own right;
- risks building distributed-systems machinery before evidence shows it is needed.

### Current disposition

**Interesting later option, not justified as the first Contract-C shape.**

---

## 6. Candidate E — run package + normalized receipts + materialized proposition result

This is a hybrid of B and D.

```text
Contract-C run package
├─ run manifest
├─ immutable Contract-B input binding
├─ shared operator / policy identities
├─ receipts/
│  ├─ measurements
│  ├─ assessments
│  └─ composition / review / deviations as applicable
└─ propositions/
   └─ {id}/result
      ├─ retained contribution ledger
      ├─ materialized current views
      ├─ decision basis
      └─ decision / abstention
```

The proposition result is a materialized, directly readable object. Receipts remain independently addressable for auditability and reuse.

### Why this currently looks strongest

It avoids both extremes:

- not a giant opaque event log;
- not a single flattened verdict;
- not a duplicated C-B bundle;
- not one enormous proposition JSON containing every shared detail.

It also matches the semantic layers already exposed by CAL research without requiring the internal research Pydantic types to become the public contract unchanged.

### Current disposition

**Leading packaging hypothesis, still untested.**

---

## 7. Proposed logical granularity

Before file names are chosen, three levels appear useful.

### 7.1 Run/result-set level

Shared identity:

- Contract-C result-set ID;
- Contract-B bundle ID/hash;
- CAL version;
- audit policy/rules identity;
- common model/operator revisions;
- run timestamps/status;
- shared deviations;
- integrity root.

### 7.2 Proposition-result level

One supplied audit proposition:

- proposition ID/text hash;
- admitted B passage refs;
- contribution ledger;
- materialized decision views;
- decision/abstention;
- proposition-specific receipt refs;
- parent/child result refs when applicable.

### 7.3 Receipt level

One attributable operation or judgment:

- receipt ID/hash;
- family/type;
- inputs by immutable identity;
- operator/policy identity;
- output/status;
- reason;
- timestamp where meaningful.

This three-level split is a candidate abstraction, not a schema decision.

---

## 8. Copy versus reference rule

A useful default principle may be:

> **Reference upstream facts by immutable identity; copy only what is required to make the CAL result interpretable and verifiable.**

Likely reference-only from B:

- full source documents;
- full evidence bundle tree;
- retrieval nomination metadata not used in CAL decisions;
- rejected candidate content unless a C decision explicitly depends on a preserved upstream record.

Likely materialized in C:

- exact audited proposition text or text hash plus ID;
- admitted passage IDs/hashes used by CAL;
- factual B inputs actually used by a CAL assessment, either copied into the receipt or referenced explicitly;
- CAL measurement output;
- CAL assessment output;
- CAL contribution and decision state;
- CAL policy/operator identities.

### Open portability question

A downstream consumer may need a portable snapshot containing selected proposition/passage text so a C artifact remains intelligible if B is unavailable.

That is a packaging convenience, not semantic ownership. If included, duplicated B content must remain hash-bound to the original B object.

---

## 9. Compatibility projection

If Contract C becomes canonical, the current audited-C-B shape can be treated as a derived export:

```text
Contract B + Contract C
        ↓ compatibility projector
resealed audited C-B
```

A compatibility projector must make information loss explicit.

For example:

```text
C verdict: contradicted
legacy C-B projection: unsupported
projection note: loss_of_specificity
```

The projection must never become the only surviving representation of the richer C result.

---

## 10. Result vocabulary should not be chosen by C-B compatibility

Current production CAL and the research decision model use different but overlapping state vocabularies.

The future C vocabulary should be selected for epistemic clarity, then mapped to legacy outputs where needed.

At minimum, preserve separate axes for:

- execution status;
- decision disposition;
- result/verdict;
- abstention/reason code;
- audit flags/modifiers;
- citation/provenance status if retained;
- confidence/uncertainty if retained.

Do not put all of these into one enum simply because the old C-B field is flat.

---

## 11. Questions to resolve before tests

1. Is Candidate E meaningfully simpler than a full receipt/event ledger in actual use?
2. Should receipts be content-addressed individually or only covered by the package integrity root?
3. Which facts used by an assessment must be copied into the receipt versus referenced by B path/hash?
4. Can one Contract-C run package contain results for propositions from multiple B bundles? Current hypothesis: probably no; one C result set should bind to one immutable B input.
5. How are partial runs represented when some propositions completed and others failed?
6. How does parent composition reference child results without duplicating them?
7. Should a proposition result carry a complete retained contribution ledger or reference ledger entries stored centrally in the package?
8. How much raw model output is needed for deterministic replay?
9. What does a downstream consumer need to verify without CAL installed?
10. What is the smallest compatibility projection required for current apparatus users?

---

## 12. Current epistemic compression

### Observed

- CAL already produces immutable-ish replay traces and a copied/resealed audited C-B derivative.
- The legacy C-B projection loses finer CAL distinctions.
- Research CAL state already separates measurements, assessments, contributions, views, and decision basis.

### Inference

- A separate C package would clarify ownership and avoid repeated mutation-like copies of B.
- A run-level package plus proposition-level materialized results is likely a better granularity than one monolithic trace per claim.

### Hypothesis

- **Candidate E** — run package + normalized receipts + materialized proposition result — is the best current physical shape to carry the CAL producer semantics.

### Unknown

- downstream consumer requirements;
- portability requirements;
- exact replay minimum;
- receipt granularity;
- controlled vocabulary;
- human-review placement.

No test plan should be locked until these questions have been reviewed alongside the producer profile.
