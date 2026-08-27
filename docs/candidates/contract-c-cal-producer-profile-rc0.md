# Candidate Contract C CAL Producer Profile — RC0

**Status:** RESEARCH CANDIDATE, NOT LOCKED  
**Producer under study:** Claim Audit Lab  
**Upstream input:** Evidence Builder / Apparatus Contract B  
**Current implementation reference:** CAL v1 audited-C-B writeback + `AuditTrace`; research `EvidenceDecisionTrace`  
**Version disposition:** intentionally unassigned  
**Testing status:** no Contract-C conformance test has been run

---

## 1. Purpose

This profile defines the **producer-side semantics** of a candidate Contract C from Claim Audit Lab's perspective.

It does not define a final schema, packaging format, downstream consumer, or contract version. It states what CAL should be responsible for emitting after it has consumed a verified Contract-B input, measured the relationship between supplied propositions and admitted evidence, applied explicit assessment/policy stages, and either decided or abstained.

The central question is:

> What must leave CAL so a later consumer can reconstruct what CAL received, what CAL measured, what CAL assessed, what policy it applied, what evidence actually participated in the decision, and why the final result followed — without rewriting Contract B or collapsing distinct epistemic states?

The candidate invariant is:

> **Contract B records the evidence world presented to CAL. Contract C records CAL's attributable work over that evidence world.**

A C artifact must not retroactively convert a CAL judgment into an upstream fact.

---

## 2. Why a distinct C boundary is worth defining

### Observed current behavior

CAL v1 currently writes an audit into a **fresh copy of the sealed C-B bundle**:

- it adds `claims/{claim_id}.audit-trace.json`;
- it populates the existing C-B `audit` block;
- it reseals the copied bundle;
- it never mutates the source C-B bundle.

This is already good preservation behavior.

However, the C-B writeback is also a lossy compatibility projection. Examples from the current code:

- CAL `contradicted` maps to flat C-B `unsupported`;
- CAL flags such as `overstated` can be collapsed onto a flat C-B degree;
- finer `not_checkable` reasons survive in the trace rather than the C-B verdict field;
- the richer replay state is therefore carried by the CAL trace, not by the C-B audit block itself.

### Inference

The current audited-C-B derivative is useful as a compatibility export, but it is a poor candidate for the long-term semantic boundary because it mixes:

1. immutable upstream evidence facts;
2. CAL measurements;
3. CAL policy assessments;
4. CAL decisions;
5. compatibility crosswalks back into an upstream vocabulary.

A distinct Contract C would allow CAL to own its own result semantics without forcing them back into Contract B.

### Hypothesis

The clean long-term arrangement is likely:

```text
Contract B
  immutable evidence-world handoff
        │
        ▼
CAL
  intake verification
  semantic measurement
  proposition-specific assessments
  decision / abstention
        │
        ▼
Contract C
  immutable CAL result package
  bound to Contract B by identity + hash
```

The current audited-C-B output can remain as a derived compatibility projection if needed.

This is a hypothesis until a packaging comparison is performed.

---

## 3. Contract-C producer boundary

Contract C begins **after successful Contract-B intake verification** and ends when CAL has emitted an immutable result artifact for the supplied audit proposition(s).

Contract C does not own:

- source collection;
- evidence extraction;
- retrieval nomination;
- Evidence Bundler admission decisions;
- claim formation or decomposition unless explicitly performed by a separately named upstream component;
- the truth of the audited claim in reality;
- unrecorded human assumptions.

Contract C owns CAL-attributable state produced after intake:

```text
verified B input reference
        ↓
CAL semantic measurements
        ↓
CAL assessment receipts
        ↓
CAL retained contribution ledger / derived decision views
        ↓
CAL decision or abstention
        ↓
immutable result identity + provenance
```

---

## 4. Information Contract C must bind to, but not rewrite

A C result must identify the exact upstream state it audited.

At minimum, the logical result should bind to:

### 4.1 Contract-B input identity

- Contract-B bundle ID;
- Contract-B schema/contract version;
- immutable Contract-B bundle hash;
- source-set / integrity identity when needed for reconstruction;
- relevant admitted passage IDs and hashes;
- proposition / audit-unit ID;
- exact proposition text hash;
- supplied proposition-graph / composition identity when applicable.

### 4.2 CAL execution identity

- CAL library / engine version;
- audit run ID;
- creation timestamp;
- frozen policy / rules ID and hash;
- model / operator identities and revisions used for material measurements;
- material configuration hash(es);
- result-artifact hash.

Contract C references these B facts. It does not copy them into a new semantic meaning.

---

## 5. Measurement receipts

Contract C should preserve CAL's semantic observations separately from later decision policy.

For each material proposition/passage or proposition/passage-set measurement, the result should be able to reconstruct:

- proposition ID;
- passage ID(s);
- measurement family / operator;
- operator or model version/revision;
- frozen configuration identity;
- measured channel(s), label(s), score(s), or deterministic output;
- raw operator output or sufficient replay information where available;
- evidence-path / input reference;
- measurement receipt hash;
- whether the relationship was measured, unmeasured, or the operator abstained.

### 5.1 Required separation

The following are not equivalent:

```text
semantic measurement   ≠ proposition-specific eligibility
semantic measurement   ≠ authority
semantic measurement   ≠ temporal applicability
semantic measurement   ≠ completeness
semantic measurement   ≠ final verdict
```

Changing a CAL policy should not rewrite the historical measurement receipt.

---

## 6. Assessment receipts

Any proposition-specific judgment that can change decision participation should be explicit, attributable, and independently reconstructable.

Candidate assessment families inherited from the Contract-B CAL consumer work are:

### 6.1 Eligibility

```text
eligible | ineligible | unknown
```

Question: may this contribution participate under the named audit policy?

### 6.2 Proposition-specific semantic validity

```text
valid | invalid | unknown
```

Question: is the measured semantic relation actually meaningful for this proposition, entity, obligation, operator, or scope?

### 6.3 Temporal / lifecycle applicability

Question: does the evidence apply to the system, process, policy, version, or state under audit?

A historically valid contribution may be non-deciding for a present-state proposition without being deleted.

### 6.4 Authority / supplier applicability

Question: is the source / actor authorized or qualified to establish this proposition under the named decision policy?

### 6.5 Aperture / completeness

```text
complete | incomplete | unknown
```

Question: do the supplied corpus/search/retrieval facts justify treating the evidence aperture as sufficiently complete for this proposition and decision?

### 6.6 Receipt requirements

A decision-relevant assessment should identify:

- assessment family;
- status;
- proposition ID;
- contribution / passage IDs affected;
- factual inputs used;
- policy / operator ID and version;
- reason / reason code;
- receipt hash;
- prior assessment reference if this is a reassessment.

---

## 7. Retained contribution ledger

Contract C should distinguish the **retained audit record** from the **current decision basis**.

A contribution is a CAL-attributable evidence position tied to one or more admitted Contract-B passages, for example:

- support contribution;
- refutation contribution;
- semantic-operator contribution;
- unresolved contribution.

Each contribution should retain:

- stable contribution ID;
- channel / relation represented by CAL;
- Contract-B passage ID(s);
- originating measurement receipt(s);
- score / score method when applicable;
- eligibility assessment;
- semantic-validity assessment;
- applicability assessments relevant to participation;
- provenance to the CAL operator that created it.

### 7.1 Non-destructive views

CAL may derive views over the retained ledger such as:

```text
raw / measured
eligible
valid
currently applicable
current decision basis
```

These are views or annotations, not destructive pipeline stages.

The Contract-C analogue of the existing research invariant is:

> **Non-deciding does not mean erased.**

A contribution that is stale, ineligible, invalid, superseded for current-state use, or otherwise non-deciding remains reconstructable.

---

## 8. Decision record

A Contract-C result must distinguish a decision from an abstention.

Candidate logical state:

```text
disposition: decided | abstained
verdict: <decision vocabulary> | null
reason_code: <typed reason>
decision_basis: [contribution IDs]
```

### 8.1 Required semantic distinctions

The eventual vocabulary must preserve, rather than silently collapse, distinctions such as:

```text
abstained      ≠ unsupported
unsupported    ≠ contradicted
unknown        ≠ adverse
unknown        ≠ favorable
ineligible     ≠ semantically irrelevant
invalid        ≠ false
stale          ≠ erased
no evidence    ≠ evidence read but silent
mixed evidence ≠ whichever score is slightly larger
confidence     ≠ support strength
```

The exact final controlled vocabulary is **not locked by RC0**.

### 8.2 Decision basis is a subset

The contribution IDs used to justify the current result are a subset of the retained ledger.

A downstream consumer must be able to answer both:

1. What evidence did CAL retain and assess?
2. What evidence actually participated in this decision?

Those are different questions.

---

## 9. Claim decomposition and parent synthesis

Contract C does not authorize CAL to invent decomposition.

If Contract B or another upstream artifact supplies:

- original claim identity;
- derived proposition graph;
- parent-child lineage;
- composition operator / rule;

then CAL may emit child result records and, where supported, a **composition/synthesis receipt** that identifies:

- parent proposition ID;
- child result IDs;
- supplied composition rule identity;
- CAL composition operator/version;
- resulting parent disposition/verdict;
- receipt hash.

If required composition information was not supplied, Contract C should expose the limitation rather than manufacture parent logic.

---

## 10. Reassessment and immutability

Contract C results are immutable historical records.

A re-audit caused by any of the following creates a **new** C result:

- changed CAL policy;
- changed thresholds/configuration;
- changed model/operator version;
- additional Contract-B evidence;
- changed proposition graph;
- corrected assessment facts;
- human review that changes a decision-relevant state.

The old result remains intact.

Candidate lineage relationships include:

- `supersedes`;
- `reassesses`;
- `same_input_different_policy`;
- `new_input_bundle`.

Exact vocabulary remains open.

---

## 11. Execution failure and partial-state handling

Contract C must not imply that every audit run ends in a clean verdict.

A result or run manifest should distinguish at least:

```text
completed
partial
failed
```

and preserve material deviations such as:

- input verification failure;
- operator/model failure;
- missing required assessment;
- unsupported proposition shape;
- incomplete measurement;
- policy/configuration incompatibility;
- serialization/integrity failure.

A missing result must not be interpretable as a favorable or adverse audit outcome.

Whether intake failures that occur before semantic processing belong in Contract C or in a separate execution/deviation artifact is an open packaging question.

---

## 12. Human review / override boundary

Human review is not automatically part of CAL's semantic measurement.

If a human reviewer:

- changes an assessment;
- overrides a machine decision;
- approves/rejects a result;
- supplies a missing fact;

that action must be separately attributed and must not overwrite the original machine receipt.

Two candidate arrangements remain open:

1. human-review receipts are optional objects inside Contract C; or
2. human adjudication is a downstream contract layered over immutable Contract C.

RC0 does not choose between them.

---

## 13. Human-readable reports are projections

CAL reports, dashboards, summaries, and buyer-facing outputs should be treated as **views over Contract C**, not the canonical audit record itself.

A presentation layer may compress or reorder information for usability, but it must not become the sole location of decision-relevant provenance.

This keeps machine audit history separate from presentation formatting.

---

## 14. Current CAL artifacts and their likely role

### 14.1 `AuditTrace`

Observed role today:

- replay-sufficient claim-level inference trace;
- retrieval result;
- entailment results;
- extracted features;
- aggregated support signal;
- rules fired;
- verdict;
- config hash;
- CAL version;
- optional probe state.

Likely Contract-C relationship:

- valuable measurement/replay source;
- not by itself sufficient for the richer proposition-specific assessment model exposed by Rungs 03–05.

### 14.2 Research `EvidenceDecisionTrace`

Observed research role:

- retained contribution ledger;
- independent support/refutation channels;
- eligibility assessments;
- semantic-validity assessments;
- aperture assessments;
- ordered stage receipts;
- raw / eligible / valid views;
- explicit decision/abstention basis.

Likely Contract-C relationship:

- stronger semantic prototype for C;
- still research-only and not a canonical result schema.

### 14.3 Audited C-B derivative

Observed role today:

- compatibility output for existing apparatus consumers;
- preserves source C-B by copying/resealing;
- flattens some CAL distinctions into C-B vocabulary.

Candidate future role:

- optional compatibility projection generated from Contract C;
- not necessarily the canonical CAL result artifact.

This is not yet decided.

---

## 15. Candidate logical Contract-C object model

This is a semantic inventory, **not a file layout**.

```text
ContractCResult
├─ result_identity
│  ├─ result_id
│  ├─ created_at
│  ├─ result_hash
│  └─ lineage / prior-result refs
│
├─ input_binding
│  ├─ Contract-B bundle ID/version/hash
│  ├─ proposition ID/text hash
│  ├─ admitted passage IDs/hashes
│  └─ proposition-graph/composition ref if supplied
│
├─ execution_identity
│  ├─ CAL version
│  ├─ policy/rules ID + hash
│  ├─ config hash
│  └─ model/operator revisions
│
├─ measurement_receipts[]
├─ assessment_receipts[]
├─ contributions[]
├─ derived_views
│  ├─ raw
│  ├─ eligible
│  ├─ valid
│  └─ decision_basis
│
├─ decision
│  ├─ disposition
│  ├─ verdict / abstention
│  ├─ reason code
│  └─ basis contribution IDs
│
├─ composition_receipts[]       # if supplied graph permits synthesis
├─ deviations[]
└─ integrity
```

---

## 16. What Contract C should not do

RC0 prohibits treating any of the following as a desirable canonical pattern:

```text
rewrite Contract B in place
flatten CAL state solely to fit C-B vocabulary
store only the final verdict
store only the winning passage
erase non-deciding contributions
replace unknown with a default
replace abstention with unsupported
hide policy transformations inside generic confidence fields
allow a report to be the only audit record
silently mutate an earlier result after reassessment
silently invent claim decomposition or parent composition
```

---

## 17. Open questions before any test plan

1. Is Contract C one result per proposition, one package per audit run, or a run package containing proposition results?
2. Does C reference Contract-B passage text by hash/ID only, or embed a portability snapshot as well?
3. Which raw model/operator outputs are required for replay versus optional diagnostics?
4. Should measurement, assessment, and decision receipts be separate files/objects or one normalized event ledger?
5. Is the research `EvidenceDecisionTrace` too implementation-specific to become a contract object?
6. What is the correct stable decision vocabulary for partial support, contradiction, mixed evidence, and abstention families?
7. Should citation/provenance status remain orthogonal to support/refutation in C?
8. Should human review be inside C or become a downstream contract?
9. Does a failed pre-semantic intake create a C artifact or only a deviation/execution record?
10. Can the current audited-C-B derivative be generated losslessly enough as a compatibility projection from C?
11. What information must a future downstream consumer be able to verify without rerunning CAL?
12. What minimum subset is required for deterministic replay versus forensic reconstruction?

---

## 18. What would falsify this producer boundary

Revise or reject RC0 if later evidence shows that:

- a separate C artifact cannot preserve enough context without duplicating all of Contract B;
- downstream reconstruction is materially worse than the current resealed audited-C-B design;
- measurement / assessment / decision separation cannot be defined without artificial duplication;
- the richer receipt model cannot reproduce existing CAL outputs;
- a substantially simpler immutable result shape preserves the same decision-relevant information;
- CAL cannot emit a stable result without importing semantic ownership that properly belongs upstream or downstream.

---

## 19. Current disposition

### Observed

- CAL already emits a replay-sufficient `AuditTrace` and a resealed audited copy of C-B.
- The C-B compatibility writeback loses some CAL distinctions while the trace preserves them.
- Research CAL machinery already represents richer assessment and contribution state than the production C-B audit block.

### Supported inference

- CAL needs an explicit producer boundary separate from the evidence handoff if those distinctions are to remain durable and attributable.
- A C result should bind immutably to B rather than mutate B.
- Measurement, proposition-specific assessments, retained evidence contributions, and decision basis should remain distinguishable.

### Hypothesis

- A separate immutable Contract-C result package is cleaner than making audited C-B the canonical downstream artifact.

### Unknown

- physical packaging;
- exact vocabulary;
- result granularity;
- replay-minimum fields;
- human-review placement;
- downstream consumer requirements.

**Do not test or lock Contract C until these producer-side semantics have been reviewed and the open questions have been narrowed.**
