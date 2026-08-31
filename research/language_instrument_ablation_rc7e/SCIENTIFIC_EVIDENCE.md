# RC7E Scientific Evidence Record

Status: **ACCEPTED HELD-OUT RUN / TERMINAL RESEARCH RECORD**

Research-only. No production authorization, Contract C change, model replacement, promotion, or merge authorization follows from this record.

## Immutable lineage

- repository: `camerontjs-dot/claim-audit-lab`
- exact RC7D-D evidence base: `253af5313e93932875bdd5956ac46246f3796271`
- Draft Research PR: `#63`
- preregistration: `5426026cb05b830b995f8b2dc9531fd67850dfa4`
- qualified apparatus freeze: `05f6570cbfc46aad7941b791aa7345209494da69`
- sealed apparatus ref: `sealed/rc7e-apparatus-freeze-20260831`
- accepted qualification run: `33445483967`
- qualification artifact: `9777952734`
- qualification artifact digest: `sha256:776d451fb946aeb494117d9d87e2ca9a321fceaee340e87956fca4bc68769c44`
- held-out source manifest freeze: `8e9ae32574b871a3f340090270bdc8843db3e2df`
- held-out cohort freeze: `0ba6a30d4168f92198cd18443ce290b666761987`
- sealed held-out ref: `sealed/rc7e-heldout-cohort-20260831`
- accepted scientific run: `33448511982`
- accepted scientific artifact: `9779020469`
- accepted scientific artifact digest: `sha256:983de37ca9c9f0c55a8b610e526d84e186f333311ed7529494974b212f090459`
- `RESULTS.json` payload digest inside artifact: `sha256:0514df612d52e0949d9f80aeb2698ccbbb20d17c97bbf4d06bd9f2689e10c2cc`
- `RECEIPTS.json` payload digest inside artifact: `sha256:af91b1426965a7bc81a9b1bedbd1b3afc3f19189b0b7bc064eab98b01de62dca`
- `REPORT.md` payload digest inside artifact: `sha256:0608c762ceab76fbfabb69b95f792793553548c79a5962fa852d4745b4a22cd4`

The accepted run executed from the exact cohort-freeze SHA. The workflow resolved `scientific`, the exact production-source guard against the RC7D-D base passed, pre-held-out qualification was skipped, the cohort guard observed 94 cases, and the frozen scientific runner completed successfully.

## Cohort

The primary cohort contains 94 formally generated semantics-first cases. Gold semantic objects existed before deterministic rendering and were not inferred from rendered text. The cohort includes atomic controls, mixed-semantic cases, unseen paraphrases, metamorphic/minimal pairs, conditionals, attribution scope, coreference, comparison+quantity, event ordering, contradictions, and domain-word traps.

Every instrument received untouched source independently. Raw-source preservation in the accepted run was `1.000`.

## Headline result

| Measure | RC7D deterministic baseline | Complete heterogeneous proposal union |
|---|---:|---:|
| proposal dimension recall | 0.738095 | 0.896825 |
| proposal dimension precision | 0.869159 | 0.649425 |
| proposal typed-atom recall | 0.601449 | 0.717391 |
| proposal typed-atom precision | 0.754545 | 0.447964 |
| unsafe proposal atoms | 27 | 122 |
| false proposal dimensions | 14 | 61 |
| residual dimensions | 33 | 13 |
| authorized dimension recall | 0.682540 | 0.738095 |
| authorized dimension precision | 0.924731 | 0.823009 |
| authorized typed-atom recall | 0.594203 | 0.637681 |
| authorized typed-atom precision | 0.863158 | 0.715447 |
| unsafe authorized atoms | 13 | 35 |
| false authorized dimensions | 7 | 20 |

Heterogeneous measurements therefore added substantial semantic observation: proposal dimension recall increased by approximately `+0.159`, reducing residual dimensions from 33 to 13. The frozen authority layer did not convert that observation gain into a safe authority gain. Authorized dimension recall increased only approximately `+0.056` over the baseline authorized layer, while unsafe authorized atoms rose from 13 to 35 and false authorized dimensions from 7 to 20.

No subset satisfied the preregistered safe-gain condition. `smallest_safe_gain_candidate = null`.

## Unique and order-independent information

Direct unique correct contributions:

- `rc7d_deterministic`: 51 dimensions / 67 scorable atoms
- `corenlp_coref_quote`: 7 dimensions / 3 atoms
- `stanza_constituency`: 4 dimensions / 0 scorable atoms
- `quantulum3`: 3 dimensions / 0 scorable atoms
- `stanza_ud`: 3 dimensions / 6 atoms
- `corenlp_openie`: 0 dimensions / 2 atoms
- `corenlp_natlog`, `corenlp_sutime`, `deberta_nli`, `owlrl_reasoner`: no direct unique dimensions under this cohort/scoring contract

Order-independent direct-coverage attribution confirmed non-redundant information beyond the deterministic bank. In particular, `corenlp_coref_quote`, `stanza_ud`, `quantulum3`, and `stanza_constituency` received positive correct-dimension credit. This is evidence that heterogeneity itself was not vacuous.

## Safety and agreement

Agreement was evidence but was not a safe authority rule.

- cross-family agreement dimension error rate: `0.383562`
- singleton-family/disagreement dimension error rate: `0.326733`
- cross-family agreement atom error rate: `0.475000`
- singleton-family/disagreement atom error rate: `0.569061`
- unsafe proposal atoms occurring under cross-family agreement: `19`
- unsafe proposal atoms occurring under singleton-family support: `103`

Thus disagreement was somewhat informative at atom level, but agreement still concealed nearly one wrong atom in two. At dimension level, agreement was not safer in this cohort.

The agreement-only authority control remained unsafe: 6 unsafe authorized atoms and 5 false authorized dimensions, while authorized dimension recall collapsed to `0.134921`.

The preserve-all / authorize-none control produced zero unsafe authority, demonstrating that the evaluator distinguishes safe incompleteness from overclaim.

## Generalization / composition

Mixed-semantic cases:

- baseline proposal recall `0.656`; complete proposal recall `0.856`
- baseline authorized recall `0.578`; complete authorized recall `0.656`
- baseline unsafe authorized atoms `6`; complete unsafe authorized atoms `18`

Unseen-paraphrase cases:

- baseline proposal recall `0.710`; complete proposal recall `0.887`
- baseline authorized recall `0.677`; complete authorized recall `0.726`
- baseline unsafe authorized atoms `8`; complete unsafe authorized atoms `16`

Metamorphic/minimal-pair evaluation over 14 pairs:

- proposal dimension-delta exact rate: `0.857143`
- authorized dimension-delta exact rate: `0.857143`
- proposal atom-delta exact rate: `0.357143`
- authorized atom-delta exact rate: `0.428571`

Proposal exact composition rate was `0.202128`; authorized exact composition rate was `0.425532`. Oracle dimension ceiling and oracle composition were both `1.000`, so the corpus/evaluator can represent the target structures in principle.

## Remaining shared residue

After every runnable non-LLM proposal instrument inspected the source, 13 gold semantic dimensions remained unobserved:

- `permission`: 5
- `comparison`: 4
- `event_ordering`: 4

All eight direct proposal principles missed every one of the four comparison cases and every one of the four event-ordering cases. They also jointly missed the permission dimension in `PE01`-`PE04` and `PT04`, where exception or temporal material tests permission-scope boundaries.

This residue is concrete rather than generic. It points to bounded missing measurement principles: comparative/numeric-relation structure, full event-event temporal ordering, and deontic/permission scope under exception/temporal composition.

## Shared failure pattern

The most important overclaim pattern is not random noise. Multiple independent families repeatedly proposed `role_binding` where the formal gold treated the event content as scoped by a quantifier, probability operator, permission construction, conditional, attribution, or quantitative statement rather than as a standalone narrator-level event assertion.

Examples of jointly wrong cross-family role-binding proposals occurred in quantifier, probability, quantitative, quantifier+exception, permission+exception, permission+temporal, conditional, comparison, and attributed-speech cases.

This preserves and generalizes the RC7D-D scope/segmentation warning: adding heterogeneous readers improves observation, but readers that correctly see predicate/argument structure can still be wrong about the authority level of that structure.

## NLI diagnostic

The bounded DeBERTa NLI lane was diagnostic only and never granted authority.

Across measured typed proposals:

- correct proposals: 81; mean entailment score `0.901851`
- wrong proposals: 139; mean entailment score `0.783929`

The separation is directionally useful but substantially overlapping. It does not justify a universal threshold or semantic authority. This run therefore does not convert NLI confidence into jurisdiction.

## Cost / runtime

All selected runtime lanes completed without runtime failure. Full-run observed instrument latencies included approximately:

- Quantulum3: 1.85 s
- CoreNLP NatLog: 2.33 s
- CoreNLP coref/quote: 2.48 s
- Stanza constituency: 20.43 s
- Stanza UD: 24.61 s
- CoreNLP OpenIE: 28.19 s
- DeBERTa NLI: 28.88 s

The environment remains operationally heavy because the current CPU setup installs a large PyTorch/CUDA dependency stack and downloads CoreNLP. This is apparatus-cost evidence, not a scientific failure.

SuPar semantic dependency parsing remains the preserved pre-held-out unavailable lane and is not counted as a successful instrument.

## Evaluator status

All preregistered evaluator adversarial controls passed before interpretation. No evaluator defect was observed that invalidates the scientific result.

No post-held-out tuning, semantic-equivalence change, authority-validator change, instrument repair, cohort repair, or model substitution was performed before accepting run `33448511982`.

## Bounded conclusion

The heterogeneous-instrument hypothesis is **partially supported at the measurement layer and not supported as a safe authority portfolio** in its present form.

Different measurement principles contributed genuinely independent correct information and reduced proposal residue materially, including on mixed-semantic and unseen-paraphrase cases. However, the proposal expansion created a multiple-observation overclaim problem after the frozen authority layer: unsafe authorization increased materially, agreement remained unsafe, and no safe-gain subset existed.

The result does **not** justify an LLM proposal experiment. The remaining residue is concentrated in specific bounded non-LLM jurisdictions, while the larger immediate defect is scope-aware authority validation of otherwise useful proposals.

The smallest defensible successor should separately test:

1. a scope/embedding authority firewall that prevents predicate/argument measurements inside quantifier, modality, permission, conditional, attribution, and quantitative structures from becoming standalone factual authority merely because several readers observe them;
2. a bounded comparison/quantitative-relation specialist;
3. a bounded event-event temporal-ordering specialist; and
4. a deontic/permission scope specialist for exception and temporal composition.

These are successor experiments, not repairs of RC7E.

## Terminal research disposition

`MORE_NON_LLM_INSTRUMENT_RESEARCH_JUSTIFIED`
