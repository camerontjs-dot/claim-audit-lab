# RC7E — Heterogeneous Non-LLM Language-Instrument Ablation

Status: **PREREGISTERED / PRE-HELD-OUT**

Research-only. No production authorization, no Contract C change, no model-replacement authorization, and no merge authorization.

## Frozen predecessor and base

- repository: `camerontjs-dot/claim-audit-lab`
- base/evidence state: `253af5313e93932875bdd5956ac46246f3796271`
- predecessor Draft Research PR: `#62`
- predecessor scientific state: `MULTI_READER_OVERCLAIM`
- predecessor accepted run: `33439373393`
- predecessor accepted artifact: `9775624091`
- predecessor artifact digest: `sha256:cba91de05ff17671538825eb7387da0e0be886963dc29adb7ff2a592409b976f`

The predecessor workflow ran from pre-evidence head `f040b34d00b94bbd809ff41f4664817ffaacfcba`; its evidence was subsequently committed at the exact base above. This sequencing is preserved as history.

## Question

What is the smallest heterogeneous portfolio of non-LLM language-measurement instruments that contributes genuinely independent correct semantic information beyond the frozen RC7D deterministic operator bank while preserving untouched source, preserving disagreement/residue, and preventing measurement noise from becoming unsafe semantic authority?

This experiment does **not** ask which parser is best.

## Invariants

1. Every language instrument receives the exact untouched source independently.
2. `sha256(raw_source)` is recorded on every receipt.
3. No instrument rewrite becomes another instrument's sole input.
4. Instrument outputs are proposals/measurements only.
5. Confidence is neither jurisdiction nor authority.
6. Agreement and disagreement are evidence, never truth.
7. Rejected and unresolved proposals are retained.
8. Authority validation is a separate layer.
9. No generative LLM, LLM API, LLM parser, LLM judge, or LLM-generated post-hoc gold labeling is authorized.
10. Production `src/` remains byte-for-byte unchanged by this branch.

## Pre-held-out instrument selection

The selection criterion is one representative per materially distinct measurement principle when a maintained/reproducible implementation exists. Multiple logical lanes from one runtime are kept distinct in receipts but are treated as a correlated family in redundancy/error analysis.

### Core portfolio

| Order | Instrument ID | Principle | Frozen identity / intended config | Authority posture |
|---|---|---|---|---|
| 0 | `rc7d_deterministic` | lexical/rule/finite-state deterministic bank | exact predecessor files at base SHA | proposal; RC7D-D validator applied separately |
| 1 | `quantulum3` | quantitative/unit extraction | `quantulum3==0.10.0`; classifier disabled unless separately pinned | proposal only |
| 2 | `stanza_ud` | morphology + Universal-Dependencies syntax | `stanza==1.14.0`, English tokenize/POS/lemma/depparse | proposal only |
| 3 | `corenlp_openie` | Open Information Extraction | Stanford CoreNLP `4.5.10`, OpenIE annotator | proposal only |
| 4 | `corenlp_natlog` | natural-logic quantifier/polarity/scope | Stanford CoreNLP `4.5.10`, natlog | proposal only |
| 5 | `corenlp_sutime` | temporal-expression normalization | Stanford CoreNLP `4.5.10`, SUTime through NER | proposal only |
| 6 | `stanza_constituency` | constituency structure | `stanza==1.14.0`, English constituency | proposal only |
| 7 | `corenlp_coref_quote` | discourse coreference + quote attribution | Stanford CoreNLP `4.5.10`, coref + quote attribution | proposal only |
| 8 | `supar_sdp` | semantic dependency graph | `supar==1.1.4`, pretrained English semantic-dependency model if runtime qualification succeeds | proposal only; conditional instrument |
| 9 | `deberta_nli` | bounded discriminative NLI relation measurement | `MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli@e5350efffb6dea3ad0962eafd0bc0b9e212a9ff8`; sequence-classification only | relation measurement only; cannot originate or authorize atoms |
| 10 | `owlrl_reasoner` | symbolic ontology/RDFS/OWL-RL inference over already-warranted propositions | `rdflib==7.6.0`, `owlrl==7.6.2` | never raw-language authority; inferred atoms retain premise lineage |

`stanza_ud` and `stanza_constituency` share a runtime family but expose different representations. CoreNLP OpenIE/NatLog/SUTime/coref/quote likewise share a runtime family. Family correlation is therefore measured explicitly and these lanes are not counted as independent merely because their annotator names differ.

### Landscape exclusions / conditional categories

These exclusions are preregistered before held-out construction and remain apparatus evidence:

- **AllenNLP SRL:** not selected because the project moved to maintenance-only status and its dependency posture is obsolete for a new 2026 apparatus.
- **UCCA/TUPA:** repository archived 2025-08-05; not selected as maintained apparatus.
- **AMRLib:** principal parsing path is seq2seq/generative (BART/T5 family); excluded by the no-generative-LLM boundary.
- **standalone CCG:** no current practical implementation with sufficiently clear maintenance/reproducibility was established during pre-registration research; omitted rather than filling the category weakly.
- **PropBank/FrameNet SRL:** current search found either stale research stacks or insufficiently established implementations. No lane is instantiated merely to claim SRL coverage. If a maintained bounded discriminative implementation is later established, that is a successor experiment, not a repair of this held-out run.
- **full temporal event ordering:** SUTime measures temporal expressions, not full event ordering. Missing ordering remains explicit residue.
- **general factuality/deontic/counterfactual parser:** NatLog covers bounded polarity/quantifier scope, not the full factuality/deontic space. Uncovered scope remains residue.

## Common non-authoritative proposal receipt

Every instrument adapter must emit a receipt containing at least:

- `raw_source`
- `raw_source_sha256`
- `instrument_id`
- `instrument_identity`
- `measurement_principle`
- `status`: `CLAIMED | NOT_APPLICABLE | UNRESOLVED`
- `proposed_dimensions`
- `anchors` (source spans, dependency nodes, graph edges, triples, temporal nodes, coreference mentions, or equivalent)
- `candidate_atoms` where valid
- `native_scores` where native scores exist
- `jurisdiction`
- `limitations`
- `residue`
- `runtime` including latency, peak-memory observation when available, model/package loading status, and failures

A score is stored as a native score with its native meaning. No cross-instrument confidence normalization is authorized.

## Semantic normalization / equivalence freeze requirements

Before held-out construction, freeze deterministic equivalence rules for:

- Unicode/case/whitespace normalization used only for comparison, never source replacement;
- singular/plural surface normalization only where predecessor authority already did so or where an explicitly preregistered atom field permits it;
- verb-lemma equivalence for the bounded event verbs used by the formal corpus generator;
- numeric surface/value equivalence only when exact conversion is deterministic;
- ordering-insensitive atom dictionaries;
- duplicate-proposal collapse for scoring only, with original receipts preserved.

No semantic equivalence may be added after held-out results are seen and counted as the same run.

## Authority candidate

RC7E begins with the frozen RC7D-D raw-source-grounded validator as the baseline authority filter for predecessor-compatible atom kinds. New instrument receipts may nominate those atom kinds, but validation remains independent of instrument identity and native confidence.

New atom kinds outside the validator's frozen jurisdiction default to `UNRESOLVED`, not authorized. A cross-instrument agreement rule may be measured as a control but does not itself grant authority.

The candidate authority layer must preserve:

- authorized atoms/dimensions;
- rejected proposals with reasons;
- unresolved proposals with reasons;
- raw source and hash;
- instrument lineage.

## Pre-registered cumulative order

Marginal-value conclusions will use this fixed order and will also include leave-one-in, leave-one-out, pairwise complements, and order-independent Shapley-style/all-subset contributions where tractable:

1. RC7D deterministic baseline
2. Quantulum3
3. Stanza UD
4. CoreNLP OpenIE
5. CoreNLP NatLog
6. CoreNLP SUTime
7. Stanza constituency
8. CoreNLP coref/quote
9. SuPar semantic dependency graph (only if qualification succeeds without changing the frozen held-out apparatus)
10. DeBERTa NLI relation measurement
11. OWL-RL reasoning over already-warranted atoms

## Complementary pairings

At minimum:

- dependency + OpenIE (SRL substitute is not silently implied)
- dependency + semantic graph
- OpenIE + semantic graph
- temporal + event structure
- quantitative + event structure
- NatLog scope + quantifier proposals
- coreference + proposition extraction
- NLI + independently typed proposals

## Held-out construction rule

The held-out corpus is created only after adapter/config, proposal contract, normalization/equivalence, authority candidate, evaluator metrics, evaluator controls, falsifiers, and terminal-state logic are frozen.

Gold is not produced by post-hoc LLM judgment. Cases are generated **semantics-first** from a frozen formal typed blueprint: gold atoms/dimensions are the symbolic inputs and surface strings are deterministic renderings or mechanically defined mutations/paraphrase transformations. The evaluator consumes the formal symbols directly. No model output is used to establish gold.

The corpus must include easy controls and hard mixed cases spanning, where formally representable:

- quantifier + exception
- quantifier + modality
- permission + exception
- permission + temporal
- subclass + permission
- quantity + event
- role binding + negation
- conditional + otherwise-supported semantics
- comparison + quantity
- cross-sentence coreference
- attribution/reported speech
- multiple temporally related events
- irrelevant prose + valid proposition
- contradictory same-dimension assertions
- domain-word traps
- unseen paraphrases
- meaning-preserving lexical/syntactic transformations
- meaning-changing minimal pairs

Unsupported target dimensions remain gold-visible residue; they are not removed to make the portfolio look better.

## Evaluator controls before scientific trust

Evaluator unit controls must cover:

1. perfect predictions;
2. safe but incomplete predictions;
3. systematic overclaim;
4. representation-equivalent predictions;
5. wrong-scope predictions;
6. domain-word traps;
7. jointly wrong agreement;
8. disagreement with exactly one correct instrument;
9. preserved contradictions;
10. one-dimension-changing mutations;
11. meaning-preserving paraphrases.

If an evaluator control fails, the scientific run is not interpreted. The defect and affected outputs remain preserved.

## Measurements

Proposal and authorized layers are scored separately. At minimum record:

- raw-source preservation
- proposal semantic-dimension recall/precision
- proposal typed-atom recall/precision where atom comparison is valid
- authorized dimension recall/precision
- authorized typed-atom recall/precision
- unsafe authorized atoms
- false authorized dimensions
- unresolved/residual semantic dimensions
- unique correct dimensions/atoms by instrument
- marginal recall and residue reduction
- overlap/redundancy matrix
- pairwise error correlation
- agreement-conditioned and disagreement-conditioned error rates
- disagreement capture of unsafe proposals
- mixed-semantic and unseen-paraphrase contribution
- metamorphic/minimal-pair performance
- composition accuracy
- latency, memory observation, package/model size where available, CI cost, and loading failures

## Multiple-testing / instrument-count stress

For cumulative portfolio prefixes, record proposal growth, false proposals, unsafe authorized atoms, and false authorized dimensions. Increasing proposal volume with stable or worsening unsafe authorization is evidence against the portfolio strategy even if raw recall rises.

## Falsifiers

The heterogeneous-instrument hypothesis is weakened/falsified if any of the following dominates the held-out evidence:

- different principles reproduce substantially the same errors;
- unique correct information is negligible;
- proposal coverage grows while the authority layer cannot keep unsafe authorization bounded;
- residual semantics stop decreasing materially before useful coverage is reached;
- gains disappear on unseen paraphrases or metamorphic pairs;
- agreement contains substantial shared error;
- disagreement is not informative about error risk;
- outputs cannot be grounded to untouched source;
- computational cost becomes unreasonable relative to unique information gained;
- conclusions depend materially on evaluator representation artifacts.

## Pre-registered decision logic

These are research dispositions, not production decisions.

- `PORTFOLIO_CANDIDATE_READY_FOR_HARDENING` requires a strict safety profile (`unsafe authorized atoms == 0`, `false authorized dimensions == 0`) plus material non-redundant residue reduction beyond the RC7D baseline and survival on unseen/metamorphic cases.
- `READY_FOR_FRESH_CONTEXT_FREE_REPRODUCTION` additionally requires the candidate portfolio/config/authority contract to be frozen, technically reproducible, and no unresolved apparatus deviation that materially changes the claim.
- `NON_LLM_RESIDUE_JUSTIFIES_LLM_PROPOSAL_EXPERIMENT` requires important residual semantics to persist across genuinely diverse runnable non-LLM representations **and** evidence that no cheaper bounded specialist identified in the maintained landscape reasonably closes that residue.
- `MORE_NON_LLM_INSTRUMENT_RESEARCH_JUSTIFIED` applies when the current portfolio reveals a concrete missing bounded non-LLM principle likely to discriminate the remaining residue without changing the research question materially.
- `ARCHITECTURE_FALSIFIED_OR_INCONCLUSIVE` applies when evaluator/apparatus failure prevents interpretation or when heterogeneity fails to add defensible information under the safety/cost constraints.

No held-out result may be used to alter the instrument order, equivalence rules, authority candidate, or success criteria and still be counted as this same experiment.
