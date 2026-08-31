# RC7F-A Assertion Status and Semantic Scope Jurisdiction — Preregistration

Status: **FROZEN BEFORE CANDIDATE IMPLEMENTATION AND BEFORE HELD-OUT COHORT**

## Lineage

- repository: `camerontjs-dot/claim-audit-lab`
- exact parent evidence: RC7E terminal evidence commit `34e9bcafad2c63c9b0761ffc456532344bc75b88`
- parent accepted run: `33448511982`
- parent disposition: `MORE_NON_LLM_INSTRUMENT_RESEARCH_JUSTIFIED`
- production `src/` is out of scope and must remain unchanged

RC7E post-hoc analysis discovered a frozen-cohort defect: three exact duplicate raw-source strings carried incompatible gold dimension sets on the quantitative/role-binding boundary. RC7F-A must not inherit that defect. The accepted RC7E evidence remains immutable.

## Question

Can a bounded non-LLM scope/assertion layer preserve a locally observed predicate/argument event while correctly determining whether that local observation is eligible to become a narrator-level factual proposition?

This experiment isolates **scope/assertion jurisdiction** from upstream parsing quality. The input event observation is treated as already measured. RC7F-A does not test whether a parser can discover the event.

## Primary hypothesis

A substantial fraction of RC7E unsafe role-binding authority is caused by locally valid event observations being assigned the wrong assertion status under quotation/attribution, conditionals, epistemic modality, deontic modality, and quantificational scope.

A bounded scope firewall can reduce false narrator-level authorization to zero or near-zero while preserving high recall for direct asserted positive and negative events.

## Safety ordering

Optimization is lexicographic:

1. minimize **false permits**: an embedded/non-factual observation marked authority-eligible;
2. preserve explicit `UNRESOLVED` rather than force a scope classification;
3. only then maximize direct-assertion recall.

A candidate with materially better recall but any systematic unsafe permit pattern does not qualify.

## Frozen input contract

Every case provides:

- untouched `raw_source`;
- one local event `observation` containing only predicate, subject, object, polarity, and a character-span anchor into the raw source;
- no gold scope label is passed to the classifier.

The candidate may inspect raw source and the observation anchor. It may not inspect case id, gold label, test group, expected outcome, or neighboring cases.

## Candidate output

For each observation:

- `scope_status`: one of
  - `ASSERTED`
  - `ASSERTED_NEGATIVE`
  - `ATTRIBUTED`
  - `CONDITIONAL_ANTECEDENT`
  - `CONDITIONAL_CONSEQUENT`
  - `EPISTEMIC`
  - `DEONTIC`
  - `QUANTIFIED`
  - `UNRESOLVED`
- `authority_eligible`: boolean
- `basis`: bounded machine-readable cues used for the classification
- `limitations`: explicit residue

Only `ASSERTED` and `ASSERTED_NEGATIVE` are authority-eligible in RC7F-A. All other statuses fail closed.

## Candidate design boundary

Allowed:

- deterministic lexical/syntactic scope rules;
- bounded discriminative non-generative NLP if preregistered before held-out reveal;
- raw-source and anchor-local punctuation/dependency-like cues.

Disallowed:

- generative LLMs;
- LLM judges;
- post-hoc gold labeling;
- case-id lookup;
- rewriting rendered held-out text after observing failures;
- widening production CAL authority.

The initial candidate should prefer a small deterministic scope graph before adding a learned model. Existing event-factuality research such as MAVEN-FACT is external evidence that factuality is a real bounded NLP task, not permission to import its labels or tune on the held-out cohort.

## Pre-held-out qualification

Qualification uses development probes derived from already-known RC7E failure families plus evaluator controls. It must verify:

1. direct positive assertion remains eligible;
2. direct explicit negative assertion remains eligible with negative polarity;
3. quoted/attributed content is not eligible as narrator fact;
4. reported complement content is not eligible;
5. conditional antecedent and consequent are not eligible;
6. epistemic/modal content is not eligible as categorical fact;
7. deontic/permission content is not eligible as factual event;
8. quantified event observations are not promoted as ordinary event atoms;
9. unknown/ambiguous patterns can return `UNRESOLVED`;
10. classifier is invariant to case id and irrelevant domain nouns.

Qualification results may repair implementation defects before freeze. Every failed qualification remains recorded.

## Held-out construction

Held-out cases are created only after candidate/evaluator freeze.

Gold is semantics-first: a formal wrapper/status object is constructed before deterministic rendering. The same event content is rendered under multiple scope operators. No parser/model output establishes gold.

Required families:

- direct positive assertion;
- direct negative assertion;
- quotation;
- reported speech/complement;
- denial/reporting context;
- epistemic probability/possibility;
- deontic permission/requirement;
- quantifier scope;
- conditional antecedent;
- conditional consequent;
- nested combinations such as attributed conditional and epistemic quantifier;
- deliberately unsupported/ambiguous constructions that should abstain.

Lexemes, names, predicates, and objects in held-out rendering must differ materially from qualification probes.

### Cohort consistency invariant

Before scientific execution, the evaluator must reject the cohort if identical normalized raw-source text maps to incompatible gold scope or authority-eligibility labels. This directly prevents recurrence of the RC7E duplicate-surface defect.

## Metrics

Primary:

- unsafe false permits;
- safe direct-assertion recall;
- authority-eligibility precision;
- scope-status accuracy;
- `UNRESOLVED` rate;
- meaning-preserving stability;
- meaning-changing scope sensitivity.

Secondary:

- by-family false permits/false rejects;
- outermost-scope confusion matrix;
- nested-scope failure classes;
- cost/latency.

Baseline: `ALLOW_ALL_LOCAL_EVENTS`, which marks every supplied event observation authority-eligible.

Ablation: remove each scope rule family to measure whether the rule contributes unique safety or merely duplicates another cue.

## Success criteria

`SCOPE_FIREWALL_CANDIDATE_READY_FOR_HARDENING` requires all of:

- unsafe false permits = `0` on held-out;
- authority-eligibility precision = `1.0`;
- direct asserted positive/negative recall >= `0.90`;
- no cohort/evaluator invariant failure;
- meaning-changing wrapper pairs change eligibility/status as preregistered;
- no post-reveal candidate repair.

`MORE_SCOPE_RESEARCH_JUSTIFIED` applies when the candidate materially improves safety but misses a bounded, identifiable scope family or abstains excessively.

`SCOPE_ARCHITECTURE_FALSIFIED_OR_INCONCLUSIVE` applies when the evaluator is invalid, the candidate cannot discriminate scope without unacceptable false permits, or results cannot distinguish the hypothesis from a simpler explanation.

## Nonclaims

This experiment does not:

- establish universal natural-language understanding;
- make `scope_status` production authority;
- modify production CAL;
- modify or define Contract E;
- establish that semantic warrant and operational authorization are the same authority domain;
- authorize an LLM proposal lane;
- authorize release or merge.

## Next gate if supported

If RC7F-A succeeds, integrate its scope receipt as **measurement metadata** in a separate hardening experiment before allowing it to influence production semantic authority. Then proceed to the bounded comparison-relation experiment (RC7F-B).