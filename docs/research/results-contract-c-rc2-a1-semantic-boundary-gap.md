# Contract C RC2-A1 — CAL Semantic-Boundary Gap Results

## Final finding

**A. Boundary-materialization gap**

Within the real locked Contract-B 1.2.0 -> CAL v0.2 production path tested by frozen RC2-A, the remaining Contract-C blocker does **not** require CAL to invent eligibility, semantic-validity, aperture/completeness, temporal/applicability, or citation judgments that production did not perform.

The smallest justified interpretation is narrower:

1. materialize the exact production decision branch/basis already deterministically recoverable from legitimate production state;
2. materialize explicit assessment-execution state, including `not_performed`, rather than treating an absent result field as evidence that an assessment result exists;
3. preserve the narrow rules CAL actually ran, such as source freshness or low-reliability limiting, without relabeling them as broader assessment families;
4. add immutable result identity / original-or-prior-result lineage bookkeeping without changing the substantive verdict.

No production semantic change is authorized by this result.

---

## Frozen predecessor

RC2-A remains frozen as **FAILED**.

- CAL PR: #16
- frozen head: `96c55fd4721b66cf138d89f52e262696ba6b6c01`
- production baseline: `33a928db97316a3652d57df9cafb8ca240305233`
- frozen workflow run: `33137053355`
- producer job: `98739242895` — **success**
- frozen artifact: `9672432251`
- artifact digest: `sha256:fd90160ec50f36f65ffd6a26bb1a7e6f1c7f584cb45cc36ee04a903e32f55994`

The same workflow's general `test` job `98739243086` completed the full pytest step successfully and then failed at Ruff. That CI state is preserved; RC2-A1 does not repair or rerun it to improve the predecessor record.

The frozen artifact still reports `producer_gate: FAILED` and remains negative predecessor evidence.

RC2-A1 is a distinct Draft Research PR (#17) from production main.

---

# Observed evidence

## O1 — The real production boundary is the v0.2 Contract-B compatibility path

Locked Contract B 1.2.0 does not carry a production engine selector. CAL's Contract-B compatibility intake selects `v0.2-lexical` for the real path exercised by RC2-A.

The v0.2 path is:

`validated Contract-B -> adapter/scoped candidates -> assess_claim_support -> ClaimAssessment -> AuditReport / compatibility writeback`

The production `ClaimAssessment` contains:

- claim identity/text;
- support label;
- risk label;
- support/counter candidates;
- support signal;
- rule flags;
- explanation/guidance/limitations.

It has no public fields named eligibility, semantic validity, aperture, temporal applicability, citation, exact decision basis, or supersession lineage.

## O2 — Exact headline-decision basis is deterministically reconstructable

Production `assess_claim_support` computes, in order:

1. support and counterevidence contexts;
2. a private `direct_contexts` view;
3. aggregate `support_signal`;
4. deterministic rule flags;
5. the final `_support_label` branch;
6. risk label.

`support_signal` is exactly:

`max(support candidate score) - counterevidence_weight * max(counterevidence score)`

with deterministic clamp/rounding.

The final support-label function has a deterministic branch order over named rule codes, support thresholds, counterevidence presence and residual rule presence.

RC2-A1 reconstructs this path from legitimate returned state without adding a new semantic judgment.

### Frozen real RC2-A observations

The final frozen RC2-A artifact is pinned into the RC2-A1 fixture by head SHA, workflow/job IDs, artifact ID and digest.

For its three real propositions:

| Claim | Support signal | Headline verdict | Support candidates | Rule codes |
| --- | ---: | --- | ---: | --- |
| `clm-md` | 0.6075 | `partially_supported` | 2 | none |
| `clm-pdf` | 0.6148 | `partially_supported` | 1 | `low_reliability_only` |
| `clm-txt` | 0.4474 | `unsupported` | 1 | `low_reliability_only` |

All three headline branches are reproduced by the production decision function from the frozen observations.

The result is narrower than “all candidates and all flags are the basis”:

- `clm-md` has two support candidates, but the max-score candidate alone determines the aggregate scalar;
- `clm-pdf` carries `low_reliability_only`, but its 0.6148 signal already enters the partial-support threshold branch before the residual-code fallback;
- `clm-txt` carries the same rule code, but its 0.4474 signal already enters the unsupported threshold branch.

Therefore a future basis receipt must distinguish **deciding branch inputs** from merely present evidence/rule state.

## O3 — Production does not compute generic eligibility

Contract-B trust is adapted into CAL source reliability (`primary -> high`, `secondary -> medium`, `background -> low`).

Production can emit `low_reliability_only`, but low-reliability evidence remains in the support scalar. RC2-A1's controlled probe observes score 0.80 retained as support signal 0.80 while the rule limits the final result to `partially_supported`.

That is a reliability-policy rule, not an `eligible | ineligible | unknown` gate.

The richer `EligibilityAssessment` type exists in the additive `v1.decision_model` machinery, whose module explicitly states that it does not alter the production verdict path.

## O4 — Production does not compute generic semantic validity

Production computes a private `_is_direct_support` predicate for rule/explanation logic.

RC2-A1 supplies a passage that fails `_is_direct_support` because of adverse-limitation wording while retaining a candidate score of 0.90. The score still drives `support_signal = 0.90` and the production headline result is `supported`.

Therefore `_is_direct_support` cannot truthfully be relabeled as the richer research `valid | invalid | unknown` decision gate.

The additive shadow's `ValidityAssessment` is richer research machinery, not a hidden production assessment.

## O5 — Production has narrow freshness logic, not generic temporal applicability

With an explicit reference date, production can emit `stale_source`. This is an attributable freshness rule.

It does not establish a proposition-specific lifecycle/applicability judgment such as “historical evidence is invalid for the current system state.” The Rung-04 research program supplied that richer temporal validity explicitly through research annotations and expressly did not claim automatic temporal reasoning.

A Contract-C boundary may retain the actual `stale_source` rule receipt. It must not promote that fact into a generic temporal-applicability verdict.

## O6 — Production has narrow source/link checks, not a generic citation-status assessment

The v0.2 path can emit `public_link_missing_source` when a specific public-link claim lacks source URL metadata.

`ClaimAssessment` has no citation/citation-status axis. This narrow source-presence rule is not equivalent to the richer v1 engine's citation-status vocabulary.

For the locked-B v0.2 path, a generic citation assessment was not performed.

## O7 — No production aperture/completeness assessment is present

The Contract-B adapter provides explicit support and counterevidence passage scopes. Those are supplied evidence boundaries, not proof that retrieval/evidence aperture is complete.

Production v0.2 contains no `complete | incomplete | unknown` aperture assessment on this path.

The additive shadow provides `ChannelApertureAssessment`, but its own module states that the machinery is additive and does not alter the production verdict path.

## O8 — Research explicitly distinguishes `not_performed` from absence

Frozen RC1's production-trace projector already encoded:

- eligibility: `not_performed`;
- semantic validity: `not_performed`;
- aperture: `not_performed`;
- temporal applicability: `not_performed`;

for production traces where those stages did not run.

Its unchanged consumer tests distinguish:

- field absent/incompatible;
- `not_performed`;
- performed-unknown;
- failed;
- not-applicable;
- explicit negative.

This is the key correction to the RC2-A ambiguity. At a pure output-object boundary, “not exposed” was the only safe statement. After tracing the actual production code path, RC2-A1 can establish the narrower fact that the generic assessment stages did not run.

This does not retrospectively change RC2-A's result: RC2-A correctly failed because its frozen boundary evidence had not established that attribution.

## O9 — Reassessment lineage is bookkeeping, not a new epistemic assessment

The current compatibility writer persists `audit_run_id` but no `supersedes`, `prior_result` or equivalent relation.

Frozen RC1 already models an initial result mechanically as:

- relation: `original`;
- prior result: null;

and changes immutable result identity when config or input identity changes.

For the initial RC2-A result, materializing “original / no prior result” requires no new subject-matter judgment. A later supersession relation would require prior-result registry/input state, but still not a new CAL epistemic assessment.

---

# Production / research delta matrix

| Semantic obligation | Production computes? | Production exposes? | Research computes / represents? | Deterministically derivable now? | New epistemic behavior required for the surviving Contract-C obligation? |
| --- | --- | --- | --- | --- | --- |
| exact deciding-contribution basis | Components + deterministic branch are computed; no basis object | No exact receipt | Yes, additive decision trace has exact contribution basis | **Yes** | **No** |
| eligibility assessment state | Generic eligibility outcome: **no**; reliability facts/rules only | No generic state | Yes, additive shadow can represent/decide explicit eligibility | **Yes: `not_performed` for this path** | **No** |
| semantic-validity assessment state | Generic validity outcome: **no**; private direct-support predicate is narrower | No generic state | Yes, additive shadow represents validity | **Yes: `not_performed` for this path** | **No** |
| aperture/completeness assessment state | **No** | No | Additive shadow represents aperture; Rung-04 annotations supplied it | **Yes: `not_performed` for this path** | **No** |
| temporal/applicability assessment state | Generic applicability: **no**; narrow freshness rule can run | Narrow rule flag only | Rung-04 research annotations represent richer temporal applicability | **Yes: generic stage `not_performed`; preserve actual freshness receipt separately** | **No** |
| citation assessment state | Generic v0.2 citation assessment: **no**; narrow source/link rule can run | No generic state | Alternate v1 engine has citation status; RC1 can represent performed/not-performed state | **Yes: `not_performed` for locked-B v0.2** | **No** |
| reassessment/supersession lineage | No prior-result relation is computed in compatibility writer | Run ID only | RC1 represents immutable result identity + prior relation | **Yes for current `original / null-prior`; later relation needs prior-result registry input** | **No** |

---

# Final field classifications

The classification is for the **minimum Contract-C obligation that survives the RC1/RC2 falsifiers**, not for a hypothetical richer judgment CAL could be taught to make.

| Missing RC2-A obligation | Final classification | Reason |
| --- | --- | --- |
| exact deciding-contribution basis | **4. derivable without new epistemic judgment** | Production result + evidence + pinned policy/code reproduce scalar, flags and exact headline branch; the receipt itself is missing. |
| typed eligibility assessment | **4. derivable without new epistemic judgment** | The truthful state for the locked-B v0.2 path is `not_performed`; positive eligibility would be new behavior and is not required merely to represent this run. |
| typed semantic-validity assessment | **4. derivable without new epistemic judgment** | Generic validity did not run; `not_performed` is attributable. The private direct-support predicate must not be promoted into a validity verdict. |
| typed aperture/completeness assessment | **4. derivable without new epistemic judgment** | No completeness stage ran; `not_performed` is attributable without claiming completeness or incompleteness. |
| typed temporal/applicability assessment | **4. derivable without new epistemic judgment** | Generic applicability did not run. Existing narrow freshness rules remain separate attributable receipts. |
| typed citation assessment | **4. derivable without new epistemic judgment** | Generic citation assessment did not run on this engine; narrow URL/source rules are preserved separately. |
| reassessment/supersession lineage | **4. derivable without new epistemic judgment** | Current result can be materialized as immutable original/no-prior; later lineage is mechanical given prior-result registry state. |

No missing obligation is classified `computed-and-lost`: production does not create the proposed rich generic assessment objects and then drop them.

No missing obligation is classified `available-but-unattributed`: related facts such as trust, age or URL presence are not equivalent to the richer assessments.

No missing obligation is classified `research-only` **after obligation minimization**: the rich positive assessment outcomes are research-only, but the Contract-C obligation for this production path is to state truthfully that those stages were not performed.

No surviving obligation requires new epistemic behavior.

No family is removed as `not actually required`, because RC1 demonstrated that field absence and explicit `not_performed` can produce different legitimate consumer behavior. What is rejected is the stronger interpretation that every result must contain a substantive positive/negative outcome for every family.

---

# Minimal additive-boundary hypothesis

## Result: survived RC2-A1

The evidence did not falsify:

> The Contract-C blocker can be resolved by a small attributable result/receipt materialization layer without changing CAL's substantive production verdict behavior.

The minimum capability is not a new decision engine. It is a recorder at the legitimate producer boundary that can materialize:

1. exact validated Contract-B identity already available at intake;
2. proposition identity;
3. producer / code / policy identity;
4. retained support and counterevidence references;
5. stable aggregate measurement already returned by production;
6. a typed **decision-branch receipt** identifying the max-score contribution(s), threshold/rule branch and only the rule/residual facts actually relevant to that branch;
7. generic assessment-family execution states, using `not_performed` where no such stage ran;
8. narrow rule receipts under their real names (`low_reliability_only`, `stale_source`, `public_link_missing_source`, etc.), not promoted to broader semantics;
9. execution state;
10. immutable result identity and optional prior-result relation.

This layer must be observational/additive: deleting it must leave the production `ClaimAssessment` and verdict bytes unchanged.

---

# Falsified alternatives

## FA1 — The rich research assessment objects are hidden inside v0.2 production and merely dropped

**Falsified.** The production path does not construct generic eligibility, validity or aperture objects. The additive decision-model module explicitly says it does not alter the production verdict path.

## FA2 — Source reliability is already an eligibility assessment

**Falsified.** Low-reliability evidence remains in the production aggregate scalar. The rule limits the result but does not exclude the contribution as ineligible.

## FA3 — `_is_direct_support` is already semantic validity

**Falsified.** A candidate can fail that predicate and still drive a high support scalar and supported headline verdict.

## FA4 — `stale_source` is already temporal applicability

**Falsified.** It is a freshness check. Rich current-state lifecycle applicability in Rung 04 was supplied explicitly by research annotations.

## FA5 — Missing generic assessment fields imply their state is unknowable

**Falsified after code-path inspection.** The real path establishes that those generic stages did not run, allowing explicit `not_performed` without inventing a result.

## FA6 — All candidate evidence and all emitted rule flags are the exact headline basis

**Falsified on the frozen RC2-A real run.** Non-max support candidates and present low-reliability flags can be non-deciding for the headline branch.

---

# Inference

1. RC2-A exposed an **attribution problem**, not evidence that CAL must immediately grow five new epistemic operators.
2. Contract C should describe what CAL actually did. It may carry a typed assessment-family state of `not_performed` without pretending an assessment outcome exists.
3. Actual narrow production rules should remain independently attributable instead of being forced into broader conceptual buckets.
4. Exact basis is the one missing item that needs more careful recording logic, but the tested real results show it is reconstructable from existing production state and deterministic policy.
5. RC2-A therefore remains correctly FAILED: the necessary attributable materialization was absent from that frozen experiment. RC2-A1 supplies diagnosis, not a retroactive pass.

---

# Remaining hypotheses / unknowns

1. RC2-A1 has not yet demonstrated a basis receipt across **every** v0.2 decision branch (no-evidence, unclassified, needs-source overrides, overstated overrides, high-score residual limiting, etc.).
2. A future basis receipt must prove that it does not accidentally call every present rule/candidate “deciding.”
3. A later supersession relation needs stable access to prior-result identity; RC2-A1 establishes only that this is bookkeeping rather than subject-matter inference.
4. This experiment does not establish independent-consumer reproducibility and does not authorize Consumer B.
5. This experiment does not establish that the alternate v1 engine should use the same minimal receipt vocabulary; that must be mapped from what that engine actually computes.

---

# Single smallest evidence-producing next step

Run one **research-only decision-basis parity sweep over the existing frozen v0.2 production rule/test vectors**.

For every production verdict branch, emit a proposed compact branch receipt from the already-computed production state and require:

- the receipt deterministically reproduces the existing headline verdict;
- deleting a claimed deciding input changes or invalidates that branch, rather than merely satisfying a harness `_need(field)`;
- non-deciding candidates/rules remain available as residual state but are not mislabeled as basis;
- all generic assessment families remain explicit `not_performed` unless an actual named production stage ran;
- production `ClaimAssessment` / verdict behavior remains byte-identical.

Do **not** proceed to clean-room Consumer B until that basis-receipt parity experiment survives.
