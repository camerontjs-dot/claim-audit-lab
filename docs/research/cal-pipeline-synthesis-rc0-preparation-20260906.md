# CAL Pipeline Synthesis and RC0 Preparation

Status: **Research Analysis / Planning Evidence**  
Date: **2026-09-06**  
Production authorization: **none**  
Promotion / merge / release authorization: **none**

This record reconciles the current evidence needed to define the smallest coherent research-backed `Contract A -> Evidence Bundler -> Contract B -> CAL -> Contract C` audit profile that can be built and exercised on fresh naturalistic claims. It is not a production architecture decision and does not alter released CAL behavior.

## 1. Live-state snapshot

The following mutable state was re-read from live GitHub before this synthesis.

### Claim Audit Lab

- `main`: `32275a239b68af383a56bca843e28cbc1e343976`
- distribution: `0.5.0`
- ordinary released engine: `v1-retrieve-entail`
- retired selectable control: `v0.2-lexical`
- frozen released rules: `cal-rules-v1.13.0`
- rules blob: `ac8147f6624164e9081a4ec365cd3920c25df96d`
- released rules thresholds: retrieval floor `0.40`, support `0.70`, contradiction `0.70`

The released README explicitly describes ordinary `audit` / `demo` as retrieve -> entail -> deterministic rules and states that release `0.5.0` added the Contract C exporter without changing verdict semantics. The newer semantic-authority research has not replaced this production path.

### Evidence Bundler

- `main`: `c26fbd4bfc8ba5c2604a784af158594b59fcae37`
- decomposition/retrieval terminal PR #52 head: `951f14f3043713b8b4cbab232fc78d9c14b1c15f`
- decomposition/downstream probe branch head: `a2a98f5f9f6f0281f80fdc661bca09124d386f3d`
- retrieval-localization predecessor PR #51 head: `502d4b3ef693adc551b2f4b5c7fc9ca9cf3bb3d5`

### Apparatus Contracts

- `main`: `c3563cff66d2c85dcbf575c693056e2d8e4563d4`
- Contract A release: `contract-a-v2.0.0`
  - production promotion merge: `b59c2fbe38bae78a3a35699362c0e67d17152e4b`
- Contract B release: `contract-b-v1.2.0`
  - production lock: `c314e53bd91c0736aa4370a364673b069aceb43e`
  - exact EB producer: `c8189c31adbab11729c31430c2070126224a2d42`
  - exact CAL consumer: `33a928db97316a3652d57df9cafb8ca240305233`
- Contract C release: `contract-c-v1.0.0`
  - release commit: `5fe55f9ed5d0ee9f026ca1b077e9d70ce0487ea1`

### Research Scaffold Harness

- `main`: `548bfa81f65290eda15af658f647497679b840ef`
- RC8J fresh independent reproduction aperture PR #20 remains pre-execution
  - aperture head: `14cbc8b872223dc2ae7ca95c4a1fc3fa7765accb`
  - state: `NOT_YET_EXECUTED`

This means RC8J has strong local/frozen research evidence but its planned fresh independent recoverability claim remains evidence debt. That debt is relevant to later hardening or promotion. It does not prevent normal-context research integration that makes no independent-recoverability claim.

### Training Room

- `main`: `ae6e896e9a4f0369bf49bec95cd8f8b14fe5abcb`
- relevant terminal research remains Draft/unmerged, as intended for research evidence.

## 2. What the evidence supports now

The research programme has established several components, but not one general semantic engine.

### 2.1 Observation is not warrant

The durable design principle remains supported:

> CAL may know that it observed something without claiming that it knows the thing is true. When warrant is incomplete, abstention is a successful outcome.

RC7E showed why this matters. Adding heterogeneous non-LLM instruments increased proposal coverage but also produced 35 unsafe authorized atoms and 20 false authorized dimensions. Agreement between instruments was not authority. The safe interpretation is therefore not `more measurements -> more confidence -> stronger verdict`; measurement output must cross a separate warrant boundary before it can strengthen an epistemic conclusion.

### 2.2 Bounded semantic measurement

The following current research families have positive measurement evidence, not generic language-understanding authority:

| Family | Current evidence disposition | RC0 use |
|---|---|---|
| explicit strict comparison | bounded measurement candidate, RC7F-B1 `0ecdedc5cea970485a635508255f3670ab231c33` | **candidate deciding family after warrant** |
| explicit event-event ordering | bounded measurement candidate, `e8d33913db66ad21027dffdf731d50f7a0977c8f` | measurement-only |
| permission + exception / temporal composition | bounded measurement candidate, `9e1f28c3e4f217561e4364e1560539bdf4870298` | measurement-only |
| assertion / scope warrant | unsafe/incomplete, including parenthetical evidential wrapper false permits in `ead5a6b068c17aefea0c2fc6b0b54b78ced26729` | fail closed / unresolved |
| generic NLI confidence | useful measurement/diagnostic | non-authoritative |
| instrument/model agreement | falsified as authority | non-authoritative |

Strict comparison is the best first vertical because it has a bounded deterministic relation target, a strong measurement candidate, and later authority/composition evidence that was explicitly exercised in a strict-comparison fragment.

### 2.3 RC8J and authority

RC8J does not establish generic language understanding. It establishes typed authority over an already-constructed semantic atom inside its tested authority envelope.

The important separation is:

`source observation/proposal -> constructed typed atom -> authority assessment -> warranted atom`

not:

`model says X with high confidence -> X is epistemically true`.

The relevant later lineage is:

- frozen RC8J authority gate: `8e75c6782bb95c3763d06230b9c5df2b6af44054`
- stale authority replay falsifier: PR #81 / `6a01e5be07c0b2ddc11aeeb3974f3221eccc9c0e`
- atomic warranted-relation successor: PR #82 / `0c324a6a866f1bc0ce678c78d6502c6b314386c2`
- portable bound authority receipt: PR #83 / `3f13b162d4b0d0cc837c99b9ad830c4c47707270`
- exact proposition-content binding: PR #84 / `2e4f42df8486684832944ddb314294d5979398a3`

The replay falsifier is essential evidence rather than an obsolete embarrassment. It demonstrated that carrying a stale `WARRANTED` status beside a changed semantic payload could create an authority substitution. The successors support binding authority to the exact semantic atom actually consumed and, separately, binding the exact proposition content to the claim/proposition identity used by the relation operator.

### 2.4 Warrant is not conclusion

The later sequence also establishes what must not happen after warrant.

- RC8J `WARRANTED` is not itself a Contract C proposition conclusion.
- PR #78 (`884405755eee6e71434c43ccae0d95d5fa1fd517`) falsified the shortcut of assigning an arbitrary scalar/channel after warrant and feeding it through threshold logic.
- PR #80 showed the initial scoreless categorical happy path but was superseded scientifically by the replay falsifier.
- PRs #82-#84 then recovered a bounded path with exact atom and proposition binding.

Inside the tested strict-comparison fragment, the supported research shape is therefore:

`warranted bound atom -> proposition-relative categorical relation -> fail-closed categorical composition`

with relation values such as:

- `SUPPORTS`
- `REFUTES`
- `IRRELEVANT`
- `UNRESOLVED`

This is bounded evidence for one fragment, not a complete CAL architecture.

## 3. Released CAL versus research candidate

### Released CAL

Released CAL remains a maintained engineering baseline:

`retrieve -> NLI/feature measurement -> cal-rules-v1.13.0 -> supported/contradicted/not_checkable`

It is useful as a baseline, regression reference, reporting surface, and source of prior failure cases. It is not the semantic architecture justified by the newer authority research.

The additive `src/claim_audit_lab/v1/decision_model.py` is also not the final research candidate. It improves state separation by recording per-passage channels, eligibility, semantic validity and aperture status, but its terminal decision still uses numerical contribution scores against receipt-bound thresholds. That makes its state/ledger ideas potentially reusable while its scalar terminal decision mechanism is not the causal decision path proposed for RC0.

### Research-supported pieces

The supported pieces are distributed across research lineages rather than one runtime:

1. bounded measurement candidates;
2. explicit proposal-versus-authority separation;
3. RC8J typed authority over a constructed atom;
4. exact atom-bound authority receipts;
5. exact proposition-content binding;
6. scoreless proposition-relative categorical relation in strict comparison;
7. fail-closed categorical composition;
8. conservative Contract C projection.

### Proposed RC0 research candidate

The smallest coherent candidate justified for construction is:

```text
Contract A 2.0 declaration
  -> Evidence Bundler retrieval with proposition/lane provenance
  -> explicit research admission state
  -> validated Contract B 1.2
  -> raw observations / proposals
  -> strict-comparison typed proposal
  -> semantic-warrant gate
  -> exact atom-bound authority receipt
  -> exact proposition binding
  -> scoreless proposition-relative categorical relation
  -> fail-closed categorical composition
  -> internal CAL proposition conclusion + basis/unresolved state
  -> Contract C 1.0 projection
```

Only **strict comparison** should be a deciding semantic family in RC0. Event ordering and permission/exception/temporal machinery may run as measurement-only shadow instruments. Assertion/scope uncertainty must fail closed.

The most important unresolved vertical seam is naturalistic evidence text -> complete typed comparison atom. RC8J can warrant an exact constructed atom; it cannot make a guessed or incompletely parsed atom correct. RC0 must therefore refuse authority when every material field of the strict-comparison atom cannot be established inside the bounded measurement grammar.

## 4. Legacy rule disposition for RC0

The released rules are not deleted, rewritten, or declared useless. Their status changes only inside the new research profile.

| Mechanism | RC0 disposition |
|---|---|
| `cal-rules-v1.13.0` terminal score thresholds | baseline/diagnostic only |
| released `v1-retrieve-entail` | baseline/diagnostic only |
| `v0.2-lexical` | historical/apparatus control only |
| v1 A5 conflicting-evidence abstention | useful prior safety case; do not auto-port as authority |
| v1 A6 source-boundary/absence guard | useful prior safety case; preserve as test/failure class |
| v1 A7 scope-mismatch withholding | useful prior safety case; preserve as test/failure class |
| research contribution ledger / evidence-state separation | reusable modeling reference |
| threshold terminal decision in `decision_model.py` | not causal in RC0 |
| model confidence / agreement count | diagnostic only |
| unsupported semantic family | abstain / unresolved |

No legacy fallback should be allowed to convert an RC0 unresolved case into support or contradiction. The baseline may disagree visibly; it may not repair or override the research candidate.

## 5. Evidence Bundler and retrieval synthesis

EB PR #52 establishes a useful boundary for the first audit.

For a valid Contract A declaration with exact declared child propositions:

- child retrieval is the currently supported normative lane;
- EB must preserve proposition identity and retrieval-lane provenance;
- flattening root and child evidence is unsuitable as the default because it erases proposition/lane relations even when physical evidence IDs remain;
- typed root+child retrieval did not add decisive evidence in the valid tested D1/D2 cases;
- root rescue appeared under deliberately poor over-decomposition/equal-total-budget conditions and is therefore a diagnostic/backstop hypothesis, not a default lane;
- equal-per-query root+child retrieval increased duplicate burden without demonstrated decisive gain;
- EB's attempted local language-model decomposition did not produce usable declared child decompositions in the tested experiment, so EB must not silently mint authoritative decomposition.

The research candidate should therefore begin with Contract A-declared decomposition when decomposition exists, retrieve each child separately, retain lane/proposition identity through Contract B, and keep any optional root-rescue arm isolated and explicitly labeled.

### Stale downstream CAL probe

The EB downstream probe branch at `a2a98f5f9f6f0281f80fdc661bca09124d386f3d` correctly separated Contract B representability from semantic interpretation, but its `run_probe.py` imports and calls `claim_audit_lab.auditor.audit_claims` with `AuditConfig()`. That is not the intended new research CAL vertical.

Therefore:

- its Contract B representability, nomination/history and provenance findings remain useful;
- its semantic outcome differences are **not** evidence for the proposed research CAL architecture;
- a successor must pin the exact Research CAL Profile and entry point.

## 6. Retrieval / admission / sufficiency separation

The first serious audit must produce separate receipts for:

1. **candidate-pool availability**: did retrieval ever surface every piece required to assess the proposition?
2. **retention/selection**: did the configured retrieval/reranking stage retain those pieces?
3. **admission**: which retained items were actually admitted for semantic assessment and why?
4. **evidence-set sufficiency**: was the admitted set jointly sufficient, including qualifiers, exceptions and counterevidence?
5. **semantic interpretation**: given sufficient admitted evidence, were typed proposals correct?
6. **warrant**: did only complete, supported typed atoms acquire authority?
7. **composition**: did warranted relations combine correctly?
8. **Contract C projection**: was the result represented without strengthening it?

A single `CAL incorrect` bucket would erase the causal information needed to decide what to fix.

## 7. Training Room implications

Training Room currently argues against starting another training campaign as part of RC0.

Observed project evidence includes:

- synthetic reranker improvement did not cleanly transfer to the naturalistic SciFact aperture (`SYNTHETIC_TRANSFER_NOT_CONFIRMED`, PR #11, head `8e2f2d68d3343e2a5f26cccc50e039c59b0df75c`);
- naturalistic inference context was materially truncated at 192 tokens and rescoring at 512 substantially changed results (PR #13, `TRUNCATION_MECHANISM_SUPPORTED`);
- the original 300 RR1 training rows all fit under 192 tokens, maximum 61, so simply retraining the same examples at 512 would expose no new training information (PR #15, `RR1_TRAINING_TRUNCATION_NOT_MATERIAL`);
- fixed-K source uniqueness / lexical-diversity selectors did not recover jointly necessary evidence at fixed capacity, while required qualifier/triad evidence often sat just beyond K (PR #21, `CAPACITY_PRESSURE_ONLY`);
- this does not justify a production `increase K` rule or a diversity heuristic.

Training should therefore follow failure localization. It becomes justified only if fresh RC0/pipeline evidence repeatedly shows that the required evidence is available and retained, context is adequate, authority/composition machinery is sound, and a learned measurement/retrieval component still exhibits a repeatable naturalistic failure that training can plausibly address.

## 8. Contract B boundary

Use released `contract-b-v1.2.0` unchanged.

B is allowed to carry provenance-bound evidence-world facts, history/search/aperture observations and limitations, typed anchors, nomination/admission/review history, and factual context. It does **not** decide whether the supplied evidence supports/refutes the proposition and it must not inject semantic-looking downstream authority.

For RC0, every handoff should validate against exact B 1.2 and retain candidate, selected, admitted and unresolved/rejected evidence identities separately where B already permits those facts.

## 9. Contract C boundary

Keep released `contract-c-v1.0.0` unchanged for RC0.

Prior CAL research already falsified direct projection of RC8J authority status into C. C should receive the actual assessed proposition result when such a result exists. Internal warrant receipts, raw proposals and richer unresolved causes may remain CAL-internal audit provenance unless C already provides an appropriate non-strengthening field.

The C projection should bind at least:

- assessment/execution state;
- proposition/claim identity;
- final assessed conclusion where performed;
- admitted/basis evidence references that C permits;
- non-performed/unresolved state where no justified proposition conclusion exists.

If a richer CAL internal state cannot be represented, record projection loss. Do not create a C successor without a concrete downstream-relevant counterexample.

## 10. Research CAL Profile manifest

A commit SHA is insufficient to identify the semantic engine under test. Before fresh RC0 execution, freeze a machine-readable manifest that binds at least:

```json
{
  "profile_id": "cal-research-rc0-strict-comparison-vertical",
  "contract_a": {"version": "2.0.0", "tag": "contract-a-v2.0.0"},
  "evidence_bundler": {
    "commit": "<exact>",
    "retrieval_profile": "<exact>",
    "decomposition_policy": "contract-a-declared",
    "root_lane": "disabled_or_explicit_diagnostic",
    "flatten_parent_child": false,
    "admission_policy": "<exact>"
  },
  "contract_b": {
    "version": "1.2.0",
    "commit": "c314e53bd91c0736aa4370a364673b069aceb43e"
  },
  "cal": {
    "commit": "<exact research head>",
    "entry_point": "<exact research entry point>",
    "deciding_families": ["strict_comparison"],
    "measurement_only_families": ["event_ordering", "permission_exception_temporal"],
    "unsupported_family_policy": "unresolved",
    "comparison_measurement": "0ecdedc5cea970485a635508255f3670ab231c33",
    "authority_gate": "8e75c6782bb95c3763d06230b9c5df2b6af44054",
    "bound_atom_receipt": "3f13b162d4b0d0cc837c99b9ad830c4c47707270",
    "proposition_binding": "2e4f42df8486684832944ddb314294d5979398a3",
    "scalar_terminal_thresholds": null,
    "legacy_baseline": "v1-retrieve-entail/cal-rules-v1.13.0"
  },
  "contract_c": {
    "version": "1.0.0",
    "commit": "5fe55f9ed5d0ee9f026ca1b077e9d70ce0487ea1"
  },
  "evaluator": "<exact>",
  "cohort": "<exact>",
  "gold": "<exact>"
}
```

## 11. RC0 should be a build, not another large benchmark

The programme has enough architecture evidence to construct the vertical. Another broad taxonomy or instrument-bank experiment is not the best next use of effort.

RC0 should therefore be intentionally small:

1. consolidate the already-supported strict-comparison measurement, authority, binding, categorical relation and composition machinery into one research-only entry point;
2. use a minimal seam/falsifier suite, approximately 10-12 cases, mostly reusing frozen predecessor controls;
3. after candidate/evaluator freeze, expose only a small 6-8-case fresh naturalistic strict-comparison smoke cohort;
4. if zero unsafe conclusions occur and failures localize correctly, proceed directly to the first modest full-pipeline cohort, approximately 24-32 fresh real/naturalistic claims.

This is smaller than a 48+ case opening benchmark while still protecting the seams that have already produced real falsifiers.

### Mandatory safety seams

The small RC0 suite must still cover:

- stale warrant with modified atom;
- valid atom receipt with modified proposition/claim content;
- comparison direction reversal;
- entity/role substitution;
- non-warranted atom attempting deciding participation;
- unsupported semantic family attempting deciding participation;
- support plus refutation;
- unresolved plus support;
- confidence/score/agreement perturbation with zero causal effect;
- Contract C projection that must not strengthen the internal result.

A fresh naturalistic smoke case may safely abstain. Unsafe support/refutation is the critical failure.

## 12. Acceptance and stop conditions

### Supports continued development

RC0 supports moving to the first 24-32-claim pipeline cohort if:

- B and C validate exactly;
- every terminal support/refutation is backed by a warranted exact atom and exact proposition binding;
- no score, confidence, agreement count or legacy verdict can alter the candidate conclusion;
- no stale/foreign/substituted receipt is accepted;
- unsupported families remain unresolved;
- fresh naturalistic strict-comparison cases produce either correct categorical conclusions or safe, localized abstentions;
- failure records distinguish retrieval/admission/sufficiency/measurement/warrant/composition/projection.

### Falsifies the candidate

Stop rather than broaden if any case yields:

- unsupported warranted atom;
- unsafe `SUPPORTS`;
- unsafe `REFUTES`;
- accepted stale/mismatched authority receipt;
- accepted proposition substitution;
- scalar/consensus-driven terminal change;
- mixed support/refutation winner selection without a separately warranted composition rule;
- C projection stronger than CAL's internal conclusion.

### Retrieval blocker

Retrieval is the primary blocker when the adjudicated required evidence never reaches the candidate pool or retained set even though the semantic vertical succeeds when supplied the correct evidence directly.

### CAL semantic blocker

CAL semantics are the primary blocker when the required evidence is present, retained, admitted and jointly sufficient but proposal construction, warrant, relation or composition fails.

### When training is justified

Training is justified only after a repeatable learned-component failure remains after context/cutoff and evidence-set availability are controlled and after authority/composition are independently sound.

### When training is not justified

Do not train to compensate for missing retrieval evidence, incomplete admitted sets, source/decomposition ambiguity, unsafe warrant, proposition-binding failures, categorical composition defects, or Contract C projection issues.

## 13. Immediate parallel work

Only two concurrent tracks are recommended before integration.

### Track A: CAL RC0 vertical

Build the research-only strict-comparison vertical in Claim Audit Lab by composing the existing supported research pieces. Do not change released `src/**` behavior and do not fall back to released v1 verdicts when the research profile is unresolved.

### Track B: EB -> Contract B RC0 handoff

Build a research-only Evidence Bundler handoff/fixture emitter for Contract A-declared child retrieval, proposition/lane provenance, explicit research admission and valid Contract B 1.2 output. Do not call any CAL semantic engine from this track.

The two tracks should coordinate only through stable research fixture/profile identities and Contract B, not through shared implementation internals.

After both complete, run one small integration slice. A third parallel research programme is not justified now.

## 14. Evidence debts and explicit nonclaims

This preparation record does not establish:

- a general CAL natural-language semantic engine;
- independent recoverability of RC8J, whose RSH aperture remains unexecuted;
- production readiness;
- universal source/decomposition correctness;
- retrieval completeness;
- semantic competence for event ordering, permissions or scope beyond their stated measurement evidence;
- a need to change Contracts B or C;
- model confidence as authority;
- a need for new training;
- operational authorization or execution permission.

The intended next bounded claim is much smaller: construct and test whether this exact research profile can carry a naturalistic strict-comparison proposition from validated evidence to a bound categorical CAL result and honest Contract C projection without laundering measurement into authority.

## 15. Supervisor disposition

**BUILD_RC0_NOW_WITH_TWO_PARALLEL_TRACKS**

The evidence is sufficient to build the bounded research candidate. Additional broad semantic-instrument research should pause until the vertical tells us which seam actually fails on naturalistic inputs.
