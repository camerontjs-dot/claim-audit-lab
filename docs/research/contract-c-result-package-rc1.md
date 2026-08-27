# Contract C Result Package — CAL Producer Research RC1

**Status:** RESEARCH DESIGN NOTE, NOT A CONTRACT  
**Producer under study:** Claim Audit Lab  
**Upstream:** locked Contract B 1.2.0  
**CAL baseline:** `33a928db97316a3652d57df9cafb8ca240305233`  
**Umbrella preregistration:** `camerontjs-dot/apparatus-contracts` branch `research/contract-c-information-sufficiency-rc1`

---

## 1. Question

What structured object should CAL emit so that:

1. a full human audit report can be rendered from it;
2. multiple downstream decision consumers can derive their own bounded projections from it;
3. those consumers do not need CAL implementation internals or heuristic report parsing;
4. the object preserves all epistemically meaningful CAL state without becoming an unbounded debug trace; and
5. the object remains bound to the exact Contract-B evidence world, CAL policy/configuration, and audited proposition that produced it?

The working architecture is:

```text
Contract B
   ↓
  CAL
   ↓
Contract C structured result package     ← machine authority
   ├── Markdown / HTML / PDF report       ← human views
   ├── consumer-specific projection       ← decision input
   └── compatibility export               ← legacy / interchange view
```

The report is not the source of truth. The structured result package is not the operational decision.

---

## 2. Current implementation evidence

### 2.1 Production report path

Current `claim_audit_lab.report` renders both Markdown and JSON from the typed v0-style `AuditReport` object. The Markdown renderer exposes:

- document identity and audit-boundary warnings;
- executive summary counts;
- claim register;
- claim text/type/support label/risk;
- linked support evidence;
- linked counterevidence;
- rule flags;
- support-quality notes;
- explanation;
- rewrite guidance;
- limitations;
- evidence links.

This proves that CAL already has a viable **structured-object → human report** pattern.

It does **not** prove that `AuditReport` is sufficient for Contract C.

### 2.2 Current v1 `AuditTrace`

Production v1 exposes an implementation-rich replay trace containing:

- exact claim identity/text;
- retrieval results and scores;
- per-passage entailment outputs, logits, probabilities;
- extracted linguistic/numeric features;
- aggregated support signal;
- fired rules;
- final support verdict + audit flags + citation status + audit confidence;
- audit-config hash and library version;
- optional negation probe.

This is strong evidence for reproducibility needs but likely contains implementation telemetry that should not automatically become stable Contract-C surface.

### 2.3 Additive research `EvidenceDecisionTrace`

The current additive decision model, explicitly not the production verdict path, separates concepts that the older report/trace compresses:

- support and refutation channel measurements;
- measurement receipts and evidence paths;
- eligibility assessments: `eligible | ineligible | unknown`;
- semantic validity: `valid | invalid | unknown`;
- support/refutation aperture: `complete | incomplete | unknown`;
- ordered stage receipts;
- retained evidence contributions with origin, score, eligibility, validity, and receipt;
- raw, eligible, and valid evidence-state views;
- explicit `decided | abstained` disposition;
- typed abstention reasons;
- exact contribution IDs forming the decision basis.

This is strong evidence that the semantically meaningful CAL result is richer than a headline support label.

It does **not** prove that these exact Pydantic types or their present field names should become the contract.

### 2.4 Audited Contract-B compatibility writeback

CAL can produce a resealed Contract-B derivative with audit state. Earlier research found that this path can flatten richer CAL distinctions and visually mixes upstream evidence ownership with downstream CAL judgments.

Treat it as a compatibility/export precedent, not the preferred canonical C authority unless testing overturns that conclusion.

---

## 3. Current compression gaps

The following gaps are material to RC1.

### Gap A — report versus richer epistemic state

The existing human report is useful but does not presently expose the full receipt-bound eligibility/validity/aperture/contribution model.

Therefore:

> A report can be complete for a human use case while still being incomplete as a stable machine handoff.

### Gap B — `AuditTrace` contains too much implementation detail

Raw logits, retrieval scores, internal feature state, and probe implementation details may be valuable for CAL debugging/replay without being stable downstream semantics.

Therefore:

> Replay sufficiency and interface sufficiency must be tested separately.

### Gap C — current objects have different epistemic vocabularies

Production v1 uses a support degree plus flags/citation/confidence, while the additive evidence-decision model uses explicit decided/abstained state over support/refutation contributions and richer assessment unknowns.

Therefore:

> Contract C must not pick a vocabulary merely by copying whichever object is easiest to serialize.

### Gap D — one report can contain convenience-derived fields

Summary counts, strongest-evidence labels, prose explanations, and display risk labels may be useful report projections while being derivable or policy/UI-specific.

Therefore:

> Human usefulness does not by itself make a field canonical.

---

## 4. Leading logical shape

The leading hypothesis remains a **run/result-set package + materialized proposition results + independently addressable receipts**.

```text
contract-c-result-set/
├── manifest
│   ├── result_set_id
│   ├── Contract-B input binding
│   ├── CAL/policy/config/operator identities
│   ├── execution status / deviations
│   └── integrity root
│
├── propositions/
│   └── {proposition_id}/result
│       ├── exact proposition identity
│       ├── input evidence references
│       ├── retained contribution ledger
│       ├── materialized epistemic views
│       ├── assessments / unknowns
│       ├── decision or abstention
│       ├── decision basis
│       └── receipt references
│
└── receipts/
    ├── measurements
    ├── assessments
    ├── policy / stage
    └── deviations / review when justified
```

This is a **logical model only**. File names, JSON/YAML layout, receipt granularity, and content-addressing rules remain experimental.

---

## 5. Candidate producer obligations

A future Contract-C producer should be able to establish the following without downstream inference.

### O1 — exact input lineage

Bind the result to:

- Contract-B bundle ID/hash/version;
- exact audited proposition ID/text/hash;
- original/parent/decomposition lineage where supplied;
- exact CAL policy/config/rules/operator identities used.

### O2 — distinguish observations from CAL assessments

Do not collapse:

- inherited B facts;
- CAL measurements;
- CAL proposition-specific assessments;
- final CAL epistemic conclusion;
- downstream operational policy.

### O3 — preserve the retained evidence ledger

A winning decision basis must not erase:

- counterevidence;
- unresolved contributions;
- valid but non-deciding evidence;
- evidence rendered ineligible/invalid/non-applicable;
- historical/superseded evidence needed for reconstruction.

### O4 — preserve explicit unknown and failure states

Missing or unresolved eligibility, validity, aperture, scope, operator availability, composition, or execution must not serialize as an apparently complete favorable/adverse result.

### O5 — identify the decision basis

A decided result should identify exactly which contribution(s)/receipt(s) made it decidable.

An abstention should identify the blocker/reason and affected state rather than merely saying `unknown`.

### O6 — support deterministic derived views

The same C object should be able to produce:

- human report;
- consumer-specific projection;
- audit/replay inspection view;
- optional legacy compatibility projection.

A derived view may omit detail but must not invent new epistemic findings.

### O7 — preserve immutability and supersession

Re-audit under:

- a different CAL policy/config;
- a changed Contract-B evidence world; or
- a corrected proposition

must produce a distinct result identity. Old C results remain reconstructable rather than being rewritten in place.

---

## 6. Copy-versus-reference hypothesis

Default rule:

> **Reference upstream evidence by immutable identity; materialize the minimum needed to make CAL's own result interpretable and independently verifiable.**

### Likely reference-only from Contract B

- full source documents;
- full bundle tree;
- rejected nomination content not used by CAL;
- upstream preparation telemetry irrelevant to CAL's result.

### Likely materialized or explicitly referenced in C

- exact audited proposition text/hash;
- admitted passage IDs/hashes;
- any B factual input actually consumed by a CAL assessment;
- measurement result and measurement receipt identity;
- eligibility/validity/aperture assessment result and receipt;
- retained CAL contribution ledger;
- materialized evidence views;
- decision/abstention and basis;
- CAL policy/config/operator identity.

### Open portability control

Test two C1 transport forms:

- **C1-R:** reference-oriented package requiring the bound B artifact for full text;
- **C1-P:** portable projection duplicating selected proposition/passage text while hash-binding every duplicated upstream byte/source object.

If portability adds no demonstrated consumer value, prefer the smaller reference-oriented form.

---

## 7. Report contract

Human reports should be projections of C, not parallel authorities.

### Required property

For every report statement that purports to describe CAL's audit state, there must be a deterministic provenance path to C.

Examples:

- headline verdict → proposition result;
- support/counterevidence table → retained contribution/evidence refs;
- limitation → explicit blocker/deviation/assessment state;
- claim-level explanation → templated rendering of typed reason + basis, unless clearly labeled free-form interpretation;
- evidence link → immutable evidence identity;
- summary count → deterministic aggregation of proposition results.

### Derived-only conveniences

The following should be presumed view-level until testing establishes otherwise:

- presentation order;
- prose wording;
- CSS/HTML structure;
- table labels;
- summary counts derivable from proposition results;
- `strongest evidence` convenience labels;
- destination-specific risk labels;
- rewrite prose.

### Report-only negative control

An independent machine consumer receives only rendered Markdown/HTML.

If it needs regexes, scraping heuristics, or unstated conventions to recover decision-relevant state, the report is empirically insufficient as Contract C even if it is excellent for humans.

---

## 8. Telemetry boundary

Start with a presumption **against** stabilizing implementation telemetry.

Candidate CAL-private fields unless ablation proves downstream necessity:

- raw NLI logits;
- raw retrieval scores/ranks;
- model-specific intermediate feature values;
- incidental feature ordering;
- debug traces;
- UI state;
- free-form explanation text;
- implementation-specific probe objects where their stable semantic result can be represented separately.

Important exception:

A model/operator identity, raw measurement, threshold, or receipt may become contract-relevant when it is necessary to:

- interpret the result;
- reproduce a decision-relevant measurement;
- identify a material methodological change;
- audit a contested result.

This is an experimental classification, not a blanket rule to hide model details.

---

## 9. Producer-side experiments

These tests implement the umbrella RC1 preregistration from CAL's side.

### E1 — semantic inventory

Map every current production and research CAL output field into:

- inherited fact;
- measurement;
- assessment;
- conclusion;
- receipt/lineage;
- execution/deviation;
- implementation telemetry;
- report-only derived convenience;
- unsupported/ambiguous.

Do this before defining a schema.

### E2 — C0/C1/C2/C3 projection

From frozen identical audit state, produce:

- C0 full implementation-rich trace;
- C1 semantic package candidate;
- C2 thin MainFrame-style consumer projection;
- C3 human report only.

Record every lossy transformation.

### E3 — report derivation

Render Markdown and HTML exclusively from C1 or a deterministic C1 materialization layer.

**Fail if:** report generation requires a CAL-internal field absent from C1 that carries decision-relevant semantic information.

### E4 — same-verdict/different-state pairs

Freeze pairs with the same headline outcome but differing counterevidence, aperture, eligibility, validity, temporal applicability, or basis.

C1 must preserve the differences even if a particular rendered summary is identical.

### E5 — telemetry metamorphics

Mutate raw telemetry while holding semantic state fixed.

C1 and report semantics must remain unchanged unless the mutated value is explicitly classified as a stable measurement that C retains.

### E6 — field-family ablation

Ablate result identity, evidence refs, measurements, assessments, conclusion/basis, resolution state, and execution/deviation families.

Use the preregistered diverse consumers to determine which omissions are actually material.

### E7 — partial execution

Produce a result set in which:

- some propositions completed;
- one operator failed;
- one assessment remained unknown;
- one proposition never reached resolution.

The package and report must not imply complete execution.

### E8 — supersession

Produce three immutable results:

1. same B + policy P1;
2. same B + policy P2;
3. changed B + policy P2.

No result inherits another's authority merely because proposition text is unchanged.

### E9 — independent projector

Give frozen C1 bytes and the logical profile to a clean implementation that did not inspect CAL implementation code.

Require it to reproduce a selected report projection and consumer projection.

---

## 10. What not to implement yet

Do not yet:

- replace production `AuditTrace`;
- replace current report renderers;
- remove audited-B compatibility output;
- assign Contract-C v1.0.0;
- choose JSON versus YAML by preference;
- normalize every CAL receipt type into a universal event ledger;
- force current additive research decision classes into the contract unchanged;
- add destination policy fields to the CAL result;
- make CAL mutate MainFrame or other consumer state.

The next coding step, after review, should be a **research projector** that maps frozen existing CAL outputs into candidate C1 without modifying the production audit path.

---

## 11. Current epistemic compression

### Observed

- CAL already renders human Markdown/JSON from a structured report object.
- CAL production v1 carries a replay-rich trace.
- CAL additive research exposes richer epistemic distinctions and receipt-bound contribution/assessment state than the existing report or compatibility projection.
- No current single object has been demonstrated to be both minimal and sufficient for diverse downstream consumers.

### Inference

A separate semantic result package is a better experimental center than either the rendered report or the full implementation trace.

### Hypothesis

A run/result-set package with materialized proposition results and addressable receipts will preserve CAL's meaningful audit state while permitting both human rendering and multiple decision-specific projections.

### Falsifier

If a materially smaller representation, including the existing report object or a thin projection, preserves all preregistered consumer distinctions and reconstruction requirements, the richer package hypothesis should be compressed rather than defended.

### Unknowns

- final field set;
- final result vocabulary;
- receipt granularity;
- portability requirements;
- replay minimum;
- which confidence constructs deserve stable surface;
- human adjudication/review placement.

No production schema or version decision is justified yet.
