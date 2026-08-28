# Contract C RC2-B — Upstream Sufficiency vs CAL Attribution Results

## Final decision

**NO — CURRENT CONTRACT B IS SUFFICIENT FOR THE TESTED NEEDS**

No missing RC2-A obligation justifies reopening Contract B 1.2.0.

The decisive matched-input result is that a valid populated Contract-B 1.2 factual-context extension makes additional legitimate evidence-world facts available to CAL intake without causing the unchanged v0.2 production audit path to perform or expose any of the previously missing proposition-specific assessment axes.

The remaining gaps are CAL/result-layer attribution or semantic-operation questions, except citation, whose field-level Contract-C necessity is not established by the existing RC1/RC2 falsifiers.

This result does not promote Contract C or authorize Consumer B.

---

## Frozen predecessor

RC2-A remains frozen **FAILED** and unchanged:

- CAL PR #16 head `96c55fd4721b66cf138d89f52e262696ba6b6c01`;
- workflow `33137053355`;
- producer artifact `9672432251`;
- artifact digest `sha256:fd90160ec50f36f65ffd6a26bb1a7e6f1c7f584cb45cc36ee04a903e32f55994`;
- `producer_gate: FAILED`.

Its real Contract-B 1.2 input recorded factual-context state `absent`. RC2-B does not reinterpret that result.

---

## Contract-B production boundary verified

Contract B 1.2.0 already defines an optional factual-context extension that can carry:

- claim origin and atomicity with explicit known/unknown state;
- provenance-bound source factual context such as version, effective date, validation/status and supplier identity;
- representation anchors;
- complete nomination/admission/review history;
- derived history-count checks;
- aperture/search-scope observations, outcomes and limitations.

The same production specification prohibits proposition-specific support/refutation, semantic validity, temporal/authority/supplier applicability, completeness conclusions, decision participation, verdict and abstention.

An aperture observation explicitly does not establish proposition-specific completeness.

CAL's promoted extension-aware intake retains the complete extension as an audit ledger and constructs a narrower semantic context from admitted passages, provenance-bound factual context and anchors. Aperture observations are retained in the ledger but are not automatically promoted into the semantic-measurement context.

---

## Matched-input experiment

### Construction

From the same pinned Evidence Bundler production SHA `c8189c31adbab11729c31430c2070126224a2d42`, RC2-B created a fresh valid Contract-B 1.2 bundle and a copied sibling:

1. `absent`: no factual-context extension;
2. `present`: the promoted EB production `attach_factual_context(...)` path attached a canonical, integrity-bound extension.

The extension contained only legal evidence-world state:

- claim origin and atomicity;
- `effective_date`;
- `version`;
- `status`;
- `supplier_identity`;
- representation anchor;
- accepted preparation-history link and count check;
- search scope, observed completion state and an explicit limitation saying no completeness conclusion was asserted.

No proposition-specific judgment was inserted upstream.

### Controls

- Contract B version: `1.2.0` on both sides.
- Core claim/evidence/audit-policy digest was identical on both sides:
  `6cfdd0313b0dee339bc62dfbaff791e9000961656ee31d44c7e8969912af76b1`.
- Typed claims, source profiles, passages and audit config loaded identically.
- The present extension was accepted as `present`; the matched absent artifact remained `absent`.
- The present semantic context contained the four factual predicates above.
- The present intake ledger contained an aperture observation.
- The semantic-measurement context did **not** contain an aperture conclusion or aperture field.
- The research branch changed no file under `src/` relative to the CAL production-semantic anchor.

### Result

The exact v0.2 production computation was mirrored from `_audit_bundle_v0_2` using production:

`adapt_bundle_to_pipeline -> build_claim_evidence_scopes -> audit_claims`.

Observed:

- three claim assessments on each side;
- headline labels: `not_checkable`, `supported`, `needs_source`;
- support signals: `0.0`, `1.0`, `0.0`;
- complete `ClaimAssessment` outputs were identical absent vs present;
- public assessment fields remained exactly the existing v0.2 surface;
- none of `eligibility`, `semantic_validity`, `aperture`, `temporal_applicability`, `citation`, `decision_basis`, or `supersedes` appeared.

Dedicated run `33179626094`, job `98877182902`: **SUCCESS**.

Artifact `9689138196`, digest `sha256:0429e0ddf492598e8e62f28da3d1a56ea1cbf5e2ab5f333f6c6f94c279a8122e`.

---

## Obligation discrimination matrix

The final classification names the decisive remaining cause after the matched test. `B artifact condition` is noted where RC2-A lacked already-supported optional facts, but that is not treated as a Contract-B schema gap when the present-side control still leaves CAL behavior unchanged.

| Missing obligation | Required upstream facts | Contract B 1.2 already supports them? | Present in RC2-A? | CAL performs operation? | CAL retains attributable result? | Contract-C necessity established? | Classification | Next action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Exact deciding-contribution basis | Canonical claim/evidence identity and scoped candidates from B; CAL-produced scores/rules; exact CAL policy state | **Yes for upstream inputs.** The deciding relation itself must not be upstream. | **Yes** for the core B inputs; no CAL basis receipt | **Yes, bounded:** CAL computes scalar/rules/verdict. RC2-A2 shows verdict replay parity but not yet complete causal dependency attribution. | **No** exact causal contribution receipt | **Bounded / partial.** Conclusion-basis provenance is justified, but exact receipt granularity remains under test. | **D** — CAL operation exists, attributable basis receipt incomplete | Continue the already-justified focused CAL rule-dependency receipt experiment from PR #19. No B change. |
| Typed eligibility assessment | Evidence/source identity; trust/reliability; any policy-relevant source status/authority/supplier facts | **Yes for tested factual needs:** core B carries trust/source facts; 1.2 extension can carry additional provenance-bound context/history. | **Partial:** core trust/reliability facts present; extension-specific context absent | **No generic eligibility operation** on v0.2. `low_reliability_only` is a narrower rule and does not exclude evidence from the scalar. | No generic eligibility receipt | **Yes, bounded:** RC1 demonstrated eligibility-state distinctions can change SOP/conformance behavior; that does not imply a positive eligibility judgment must exist. | **C** — CAL operation not performed. RC2-A also had an already-supported optional-B-state absence, but the matched present control shows it is not the decisive blocker. | Keep the truthful stage state `not_performed` unless a separately validated CAL eligibility policy is added. No B change. |
| Typed semantic-validity assessment | Claim text/identity; evidence passage bytes/identity; provenance and, where needed, representation anchors | **Yes.** Core B carries claim/passages; 1.2 can carry anchors/context facts. | **Core facts yes; extension anchors absent** | **No generic validity operation** on v0.2. The private direct-support predicate is narrower and is not a validity gate. | No generic validity receipt | **Yes, bounded:** RC1 demonstrated validity-state distinctions can alter conformance behavior. | **C** | Do not relabel direct-support logic. Preserve `not_performed` until a real CAL validity operation is separately justified. |
| Typed aperture/completeness assessment | Search scope/outcome/limitations plus nomination/admission/review history; potentially corpus/search-universe identity as policy requires | **Yes for the tested factual state.** This is an explicit Contract-B 1.2 extension capability. It expressly does not carry the completeness conclusion. | **No:** RC2-A's extension state was `absent` | **No.** The present matched artifact delivered an aperture observation to CAL's intake ledger, but v0.2 produced the identical assessments and the semantic context contained no aperture conclusion. | No CAL completeness/aperture assessment receipt | **Yes, bounded:** RC1 publication behavior distinguished performed/unknown/incomplete aperture state. | **C**, with predecessor condition **B**: RC2-A lacked already-supported B observations, but supplying them does not create the CAL assessment. | Any future completeness claim requires a separately tested CAL/named-assessor stage consuming B observations. Do not put completeness into B. |
| Typed temporal/applicability assessment | Publication/effective dates, version/status, supplier/authority/scope facts, plus proposition context | **Yes for tested facts.** Core B carries bibliographic dates; 1.2 context facts can carry version/effective-date/status/supplier facts. | **Partial:** core date facts present; richer extension context absent | **No generic applicability operation.** v0.2 has narrow freshness logic such as `stale_source`; the present matched extension delivered effective-date/version/status/supplier facts without changing assessments. | No generic applicability receipt | **Yes, bounded:** RC1 temporal-state control changed conformance behavior. | **C**, with predecessor condition **B** for optional context facts | Preserve actual freshness receipts under their real names. A proposition-specific applicability assessor, if needed, is a CAL/policy experiment, not B 1.3. |
| Typed citation assessment | Source identity/URL/DOI/PMID where available, passage/source hashes and provenance | **Yes** on the existing B surface for the tested citation/provenance facts. | **Yes / sufficient for the tested narrow source-link rules** | No generic citation axis; only narrower source/link rules such as `public_link_missing_source` | No generic citation receipt | **No field-level necessity demonstrated.** RC1 preregistered consumers did not read citation state, and RC2-A ablated the assessments family rather than citation independently. | **E** — current Contract-C citation obligation not justified | Drop generic citation assessment from the required minimum unless a future consumer/falsifier demonstrates the distinction. Preserve narrow source/provenance receipts. |
| Reassessment / supersession lineage | Current immutable CAL result identity; prior CAL result identity; explicit relation/reason or registry state | **Not a Contract-B evidence-world responsibility.** | Not supplied, and should not be inferred from B absence | **No production prior-result/supersession operation**; current writer retains run identity only | No prior/supersedes relation | **Yes, bounded:** RC1 investigation/lineage controls distinguished recomputed/superseding results. | **C** — CAL/result-lifecycle operation not performed/retained | Define explicit prior-result input/registry ownership and immutable result identity as a CAL/Contract-C lifecycle question. No B change. |

No obligation is classified **A**. No missing evidence-world fact was found that requires a Contract-B schema expansion.

---

## What the matched test falsified

### F1 — Contract B must be expanded before CAL can represent the missing RC2-A semantics

**Falsified for the tested needs.**

The current 1.2 extension already transported the tested richer evidence-world facts, including aperture observations and temporal/version/status/supplier context. The missing CAL axes remained missing and the v0.2 assessments remained identical.

### F2 — RC2-A failed mainly because its extension was absent

**Falsified as a sufficient explanation.**

The absence was real and matters to what factual state was available in that exact predecessor. But a matched present extension did not cause CAL to perform any of the missing generic assessments.

### F3 — More upstream factual context is equivalent to a CAL assessment

**Falsified.**

The present artifact made additional factual context visible to CAL intake while preserving identical v0.2 outputs. Aperture is the clearest control: a real aperture observation was present in the intake ledger and still did not become a completeness conclusion.

### F4 — CAL already has every missing operation and only needs serialization

**Falsified for eligibility, semantic validity, aperture/completeness, generic temporal/applicability, generic citation and supersession lineage.**

Exact deciding basis is the narrower exception: CAL already performs the underlying scalar/rule/verdict work, but PR #19 showed that exact causal contribution attribution remains richer than terminal branch replay.

### F5 — Generic citation state is already a demonstrated Contract-C minimum

**Not supported by current falsifiers.** Treat the obligation as unnecessary until contrary evidence is produced.

---

## Inference

1. Contract B 1.2 is not the current bottleneck for Contract C.
2. The optional-extension absence in RC2-A is an important predecessor fact, not evidence of a schema defect.
3. Evidence-world facts and CAL judgments remain correctly separated by the current boundary.
4. Aperture and temporal applicability are especially clear examples: Contract B can supply the factual basis without owning the proposition-specific conclusion.
5. The next useful work should be smaller than a broad CAL semantic redesign. Exact decision-basis attribution already has a concrete unresolved falsifier in PR #19.

---

## Unknowns / bounds

- This matched test proves sufficiency only for the factual families actually populated. A future CAL policy may require a novel evidence-world fact not currently expressible in 1.2; that would be a new bounded Contract-B question, not evidence for reopening now.
- RC2-B does not validate a new eligibility, validity, completeness or applicability assessor.
- RC2-B does not establish the final Contract-C field set or encoding.
- RC2-B does not resolve PR #19's causal rule-dependency receipt question.
- RC2-B does not establish later reassessment registry semantics.
- No independent Consumer B was run.

---

## Smallest next step

Do **not** reopen Contract B and do **not** create Consumer B yet.

The smallest evidence-producing next experiment remains PR #19's focused **CAL rule-dependency receipt** experiment on the existing absolute-wording/counterevidence seam. It should determine whether CAL can emit a compact attributable causal contribution receipt that preserves evidence-to-rule dependency, exact policy identity and terminal branch without changing production verdict behavior.

Only after that survives should a narrow producer-boundary materialization/promotion candidate be considered. Generic eligibility/validity/aperture/applicability machinery should not be added merely to fill Contract-C fields; each would require its own evidence of necessity and assessor validity.

## Production impact

**None.** No production CAL file, Contract B object/version, Contract-C version, or downstream consumer changed.
