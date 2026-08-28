# Contract C RC1 Field Inventory

**Research branch:** `research/contract-c-result-package-rc1`  
**Production baseline:** `33a928db97316a3652d57df9cafb8ca240305233`  
**Object of study:** information CAL already emits or can materialize at its legitimate boundary without adding new epistemic reasoning.

This inventory is a classification exercise, not a Contract-C schema. A field can be important without deserving literal byte-for-byte transport. Where current evidence does not distinguish a stable semantic measurement from an implementation intermediate, the classification is `unknown` rather than silently dropping it.

## Classification vocabulary

- **semantic result**: CAL-attributable semantic measurement, assessment, conclusion, residual state, or typed abstention state that downstream policy may legitimately inspect.
- **provenance/identity**: identity needed to bind a result to proposition, evidence, input, or lineage.
- **reproducibility metadata**: method, configuration, code, model/operator, policy, or receipt identity needed to distinguish materially different computations.
- **implementation telemetry**: execution details useful for debugging or internal replay but not yet shown to carry stable semantic meaning.
- **human-report presentation**: prose, formatting, summaries, or display conveniences derivable from typed result state.
- **destination-specific policy**: downstream action/risk/routing interpretation that Contract C must not acquire merely because CAL currently renders it.
- **redundant/derivable**: reproducible from other retained semantic fields plus an explicitly identified policy or renderer.
- **unknown**: current evidence is insufficient to decide whether the field is contract-relevant.

## 1. Production `AuditTrace`

| Field / family | Primary classification | RC1 treatment | Evidence or uncertainty |
| --- | --- | --- | --- |
| `claim_id` | provenance/identity | retain | Stable proposition referent. |
| `claim_text` | provenance/identity | retain with content hash | Text is part of the audited object. |
| proposition text hash, currently not explicit | provenance/identity | materialize | Deterministically knowable without new epistemic reasoning and needed to prevent silent text drift. |
| `retrieval[].passage_id` | provenance/identity | retain only when semantically retained/referenced | Raw retrieval membership and semantic evidence participation are not the same thing. |
| `retrieval[].score` | implementation telemetry | exclude from current C1 candidate | Telemetry mutation test changes score while projected semantic package remains invariant. No preregistered consumer requires it. |
| `entailment[].passage_id` | provenance/identity | retain | Binds relation measurement to evidence. |
| `entailment[].label` | semantic result | retain | Claim-to-passage relation measurement. |
| `entailment[].score` | semantic result, provisional | retain in current candidate | Decision-relevant relation strength. Whether every score belongs in the stable package remains open. |
| `entailment[].raw_logits` | implementation telemetry | exclude | Projector metamorphic mutation leaves candidate content invariant when label/score/state are fixed. |
| `entailment[].p_entail`, `p_contradict` | unknown | exclude provisionally | Production model comments describe some probabilities as reported rather than acted on. They may be redundant with the retained semantic relation, but RC1 has not proved that universally. |
| `features.numerical_values` | unknown | do not canonize yet | It is an implementation feature today, but extracted quantities can carry semantic meaning in numeric-rule decisions. A stable semantic receipt may be needed instead of the raw feature object. |
| `features.has_explicit_negation` | unknown | do not canonize yet | Could be implementation intermediate or part of a semantically meaningful operator receipt. |
| `features.has_universal_quantifier` | unknown | do not canonize yet | Same concern. |
| `features.modal_strength` | unknown | do not canonize yet | Scope/strength can affect semantic decisions. Raw implementation shape is not automatically canonical. |
| `features.claim_token_count` | implementation telemetry | exclude | Metamorphic mutation is invariant in current projector and no consumer requires it. |
| `features.compound_claim` | unknown | do not canonize yet | Can affect decomposition/scope semantics. Stable meaning not established. |
| `features.sentence_type` | unknown | do not canonize yet | Can affect scope/out-of-scope handling. Stable meaning not established. |
| `support_signal.label` | semantic result | retain | Aggregate semantic relation state. |
| `support_signal.max_entailment_score` | semantic result, provisional | retain | Mutating it changes candidate semantic content in RC1. |
| `support_signal.contributing_passage_id` | provenance/identity + semantic basis | retain | Identifies the evidence basis used by CAL. |
| `support_signal.best_entail`, `best_contradict` and associated passage IDs | redundant/derivable or unknown | exclude provisionally | Current production comments indicate these are reported values and not all rules read them. Need targeted operator-basis test before final exclusion. |
| `rules_fired[].rule_id` | reproducibility metadata + semantic basis receipt | retain by identity | Records which policy/rule participated without transporting implementation prose. |
| `rules_fired[].reason` | human-report presentation / redundant | exclude | Projector metamorphic mutation is invariant. Reason can be rendered from rule receipt/policy where deterministic. |
| `verdict.support_verdict` | semantic result | retain | Headline CAL conclusion. |
| `verdict.support_verdict_reason` | semantic result | retain | Typed abstention/reason state distinguishes same headline verdicts. |
| `verdict.audit_flags` | semantic result, provisional | retain in current candidate | Flags such as `overstated` can preserve meaningful residual interpretation. Necessity is not independently ablated by flag family yet. |
| `verdict.citation_status` | semantic result | retain as typed assessment | CAL-attributable citation assessment where actually performed. |
| `verdict.audit_confidence` | unknown | exclude from current candidate pending a consumer/meaning test | It looks semantic, but RC1 has not established what stable decision-relevant meaning its current coarse label carries. |
| `audit_config_hash` | reproducibility metadata | retain | Changing the hash changes result identity in RC1. |
| `library_version` | reproducibility metadata | retain, but code SHA is stronger | Distinguishes producer implementation lineage. |
| production CAL code SHA, currently external to `AuditTrace` | reproducibility metadata | materialize | Legitimately knowable at boundary and required to distinguish recomputation. |
| `negation_probe.negated_claim` | unknown | exclude provisionally | Could be implementation telemetry or a semantically relevant measurement receipt. RC1 does not yet justify permanent exclusion. |
| `negation_probe.abstained` | unknown | exclude provisionally | Potentially meaningful execution/measurement state. Needs a targeted test. |
| `negation_probe.result.*` | unknown | exclude raw form provisionally | Raw logits are telemetry, but normalized relation/result may be semantically relevant if it forms the actual decision basis. |

## 2. Additive `EvidenceDecisionTrace`

The richer decision trace is research-only/additive on the production baseline. It is useful evidence about CAL's legitimate semantic boundary, not proof that current production emits Contract-C-ready objects.

| Field / family | Primary classification | RC1 treatment |
| --- | --- | --- |
| `claim_id` | provenance/identity | retain |
| scope status | semantic result | retain if performed |
| stage receipts | reproducibility metadata / provenance | retain by stable receipt/operator identity, not debug payload |
| admitted passage IDs | provenance/identity | retain as evidence references |
| support/refutation channel measurements | semantic result | retain normalized semantic measurements and evidence binding |
| measurement receipt/operator identity | reproducibility metadata | retain |
| aperture assessments | semantic result | retain state, value, reason code/receipt as needed |
| signal floors / thresholds | reproducibility metadata | bind through policy/config identity unless a consumer needs inline values |
| policy ID / policy receipt | reproducibility metadata | retain |
| contribution ID | provenance/identity | retain where it is an exact decision basis referent |
| contribution channel | semantic result | retain |
| contribution passage IDs | provenance/identity | retain |
| contribution score/method | semantic result + reproducibility metadata, provisional | retain only if it is a stable normalized measurement; raw implementation internals should remain out |
| contribution origin | provenance/identity | retain if it distinguishes measured vs historical/reused basis |
| contribution eligibility / validity | semantic result | retain |
| raw/eligible/valid aggregate snapshots | redundant/derivable, provisional | prefer deriving from contribution state if deterministic; do not assume this until round-trip reconstruction is tested |
| decision disposition | semantic result | retain |
| resolved verdict | semantic result | retain |
| decision reason/reason code | semantic result | retain typed form |
| exact basis contribution IDs | semantic result + provenance/identity | retain |

## 3. Structured `AuditReport`

| Field / family | Primary classification | RC1 treatment |
| --- | --- | --- |
| `document_id` | provenance/identity | retain only if it identifies the audited source/result set rather than a report file |
| summary counts | redundant/derivable | exclude from semantic core |
| claim ID/text | provenance/identity | retain |
| claim type/location | provenance/identity or human-report presentation | source location may be retained by reference; display location is report concern |
| support label | semantic result | retain only through normalized CAL result semantics, not because this report field exists |
| risk label | destination-specific policy | exclude from Contract-C semantic core unless separately demonstrated as a CAL epistemic assessment rather than action/risk policy |
| candidate evidence IDs/references | provenance/identity | retain references, not duplicated upstream source truth |
| excerpts/source metadata | redundant/derivable / upstream provenance | reference Contract B rather than rewriting source facts into CAL authority |
| evidence matching scores | implementation telemetry or semantic measurement, depending operator | unresolved at field level; do not promote wholesale |
| evidence rationale prose | human-report presentation | exclude |
| evidence reliability/date/URL | upstream evidence facts | reference provenance from Contract B; do not re-author as CAL facts |
| counterevidence | semantic residual + provenance/identity | retain typed evidence references |
| support signal | semantic result | normalize if stable |
| rule flag code | semantic result / reproducibility metadata | retain typed semantic flag or rule receipt where needed |
| rule flag message | human-report presentation | exclude |
| rule flag risk | destination-specific policy | exclude |
| explanation | human-report presentation | derive from semantic package plus renderer policy |
| rewrite guidance | human-report presentation / destination policy | exclude |
| limitations prose | human-report presentation with possible semantic content | replace with typed unknown/blocker/execution state in C1, then derive prose |
| report warnings | human-report presentation or execution state | only typed execution/deviation meaning belongs in C1 |

## 4. Contract-B writeback / compatibility output

| Field / behavior | Classification | RC1 finding |
| --- | --- | --- |
| `audit_run_id` | provenance/identity | potentially useful identity, but not sufficient alone |
| `audited_at_utc` | reproducibility metadata / event time | useful lineage metadata if execution time matters |
| `audit_support_verdict` | consumer-specific projection | too lossy to serve as C1 |
| `audit_confidence` | unknown | current semantic sufficiency not established |
| notes / display fields | human-report presentation | not C1 core |
| mapping `contradicted -> unsupported` | consumer-specific compatibility policy | loses a CAL distinction |
| flattening multiple `not_checkable` reasons | consumer-specific compatibility policy | loses same-headline residual state |

The writeback is therefore best treated as a compatibility projection, analogous to C2, unless new evidence overturns the loss findings.

## 5. Boundary context CAL can legitimately materialize

These values are not all present inside production `AuditTrace`, but they are legitimately knowable at the producer boundary without new epistemic reasoning:

| Field | Classification | RC1 treatment |
| --- | --- | --- |
| exact Contract-B bundle ID | provenance/identity | required |
| exact Contract-B bundle/content hash | provenance/identity | required |
| Contract-B contract version | provenance/identity / reproducibility metadata | required as lineage fact, not as an applicability judgment |
| CAL producer code SHA | reproducibility metadata | required for immutable result identity |
| audit policy/config hash | reproducibility metadata | required |
| model/operator revision IDs where semantically material | reproducibility metadata | required by stable identity/receipt, not runtime debug dump |
| result ID | provenance/identity | derive deterministically from immutable semantic package |
| prior result ID + relation (`original`, `recomputed`, `superseding`) | provenance/identity | required for reassessment lineage |
| mutable notion of `current` | destination/runtime registry state | do not embed in immutable result package |

## 6. Temporal and version facts

A source date, version, effective period, or supersession fact from Contract B remains an upstream evidence-world fact. CAL may reference the fact and emit a proposition-specific temporal/version applicability **assessment only when it actually performed one**.

Therefore:

- upstream date/version values: provenance-bound Contract-B facts, not CAL-authored semantic conclusions;
- CAL temporal/version applicability outcome: semantic result if performed;
- operator/policy/receipt for that assessment: reproducibility metadata;
- absence of such an assessment: explicit `not_performed`, not an invented default of current/applicable.

## 7. Model/runtime telemetry

### Keep by identity when materially semantic

- model/revision identifier;
- tokenizer/operator revision where it can change the semantic measurement;
- policy/config hash;
- CAL code SHA;
- deterministic operator/receipt ID.

These are reproducibility metadata, not destination policy.

### Exclude by default

- raw logits where normalized semantic relation is retained;
- retrieval scores where they are only nomination/ranking internals;
- device, latency, cache, process, memory, thread, batch, and debug fields;
- prose rule explanations;
- display-only diagnostics.

A telemetry field must be reclassified if a mutation changes legitimate downstream semantic meaning. RC1 deliberately treats that as an empirical question.

## RC1 field-level uncertainties that remain promotion-relevant

1. Whether numeric, modal, negation, compound-claim, or sentence-type intermediates need normalized semantic receipts because they form part of CAL's actual basis.
2. Whether `audit_confidence` has a stable enough meaning to be canonical or is only a presentation/control heuristic.
3. Whether `audit_flags` should be a separate semantic assessment family or can be deterministically derived from retained basis and policy.
4. Whether normalized relation scores are needed by diverse consumers or can be replaced with typed relation outcomes plus receipts.
5. Whether redundant `EvidenceDecisionTrace` snapshots can be safely recomputed from contribution state.

These are left as unknowns rather than converted into schema decisions.
