# RC7E Held-Out Source Manifest

Status: **FROZEN BEFORE RC7E COHORT CONSTRUCTION**

Research-only. This manifest constrains corpus construction after the apparatus freeze `05f6570cbfc46aad7941b791aa7345209494da69`. It does not modify the frozen language instruments, equivalence rules, authority validator, evaluator, falsifiers, or terminal-state logic.

## Primary-gold rule

The primary RC7E scientific cohort is **not labeled from rendered text**.

Gold semantic objects are constructed first from the already-frozen RC7E typed vocabulary. Surface text is then emitted by deterministic renderers or deterministic single-dimension mutations. The evaluator consumes the symbolic objects that preceded rendering.

No LLM output, NLI output, parser output, instrument output, majority vote, agreement signal, or post-hoc human/model judgment may establish or revise primary gold after rendering.

Existing corpora below constrain phenomenon selection and supply independent challenge evidence. Their labels are not silently translated into RC7E semantic authority.

## Construction / phenomenon sources

### RuleTaker

- role: methodological blueprint for declarative/formal structure -> deterministic natural-language rendering -> mechanically known target
- public repository: `allenai/ruletaker`
- pinned public repository state observed before cohort construction: `abaacec9364992eff5ec4555b837e20fee2f2ff0`
- RC7E use: construction method only; no RuleTaker model output is used as RC7E gold
- note: RuleTaker's object language is not treated as equivalent to RC7E semantic types

### FraCaS textual inference suite

- role: externally established phenomenon inventory and adversarial inspiration for quantification, anaphora, comparatives, and temporal/compositional inference
- source: Bill MacCartney public-domain distribution of the FraCaS Consortium suite
- source page: `https://www-nlp.stanford.edu/~wcmac/downloads/`
- reported suite size: 346 textual inference problems
- RC7E use: phenomenon/mutation design only; FraCaS entailment labels are not converted into RC7E typed atoms

### HELP

- role: mechanically generated monotonicity / natural-logic transformation precedent
- public repository: `verypluming/HELP`
- pinned public repository state observed before cohort construction: `3ee5c298d48549704629a3687ccd8a00168281b8`
- license at pinned state: CC BY-SA 4.0
- RC7E use: metamorphic design for quantifier/scope changes; no HELP model output is used

### Legal Obligation Metadata Ontology (LOMO)

- role: independent formal-domain support for separating actor, action, deontic modality, condition, exception/derogation, and temporal constraint
- source: Publications Office / European Institutions LOMO
- release observed before cohort construction: 2026-07-10
- documentation: `https://drpm.pages.code.europa.eu/lomo/`
- RC7E use: phenomenon selection and successor-hypothesis context only; LOMO does not change frozen RC7E authority types

### Human disagreement in EU legislation annotation

- publication: Gijs van Dijck, Carlos Aguilera, Shashank M. Chakravarthy, "Deciphering disagreement in the annotation of EU legislation", *Artificial Intelligence and Law* 34 (2026), 191-226
- DOI: `10.1007/s10506-024-09423-9`
- publication license reported by Maastricht repository: CC BY
- relevant independently annotated categories: quantities, IF-THEN, exceptions, scope, hierarchy, deontic clauses, active role, passive role
- RC7E use: motivates preserving ambiguity/disagreement and including scope/conditional/deontic mixed cases; adjudicated labels are not treated as semantic truth for the primary cohort

## Independent challenge sources (separate scoreboard)

These resources are eligible for a later or parallel **external challenge scoreboard**. They are not part of primary formal recoverability unless an exact, mechanically justified mapping is separately frozen before observing RC7E outputs.

### Lawnotation / deontic EU legislation

- title: "To NER or not to NER? A case study of low-resource deontic modalities in EU legislation?"
- DOI: `10.34894/D9AKUS`
- version observed: `1.0.0`
- rights: CC BY 4.0
- use: natural-text obligation / permission / prohibition challenge; especially useful because multiple modalities can coexist in one text

### MeasEval

- role: human gold for quantity, unit, measured entity/property, qualifier, and attachment relations
- public repository: `harperco/MeasEval`
- pinned public repository state observed before cohort construction: `1fa738b6bc9b72c84c88a80344ca3ab39a310a44`
- RC7E use: external quantitative-attachment challenge, especially for the frozen Quantulum limitation that quantity recognition does not itself bind event/entity scope

### GUM

- role: manually corrected entity/coreference, speaker/addressee, syntax, discourse, and related annotations across natural genres
- public repository: `amir-zeldes/gum`
- pinned public repository state observed before cohort construction: `22fdf87f9c71c96bcc771461d06e689b1f90020d`
- licensing caution: underlying documents have source-specific licenses; use only a separately whitelisted redistributable subset for any vendored challenge data
- RC7E use: external coreference/attribution and cross-sentence transport challenge

### MAVEN-ERE / MATRES

- role: independent event-relation / temporal-ordering challenge evidence
- RC7E use: measure residue explicitly left by frozen SUTime, which handles temporal expressions but is not a full event-ordering instrument
- boundary: exact dataset snapshot and licensing must be frozen before any data are vendored or executed

## Excluded from the primary gold path

- LexDeMod is not needed for RC7E primary construction; its Adobe research license is noncommercial-only and therefore introduces avoidable downstream licensing constraints.
- No generative semantic parser, LLM judge, LLM annotation service, or LLM-generated label set is an eligible gold source.
- No external corpus item is manually reinterpreted into an RC7E atom after seeing instrument output.

## Two-scoreboard rule

RC7E keeps two epistemically distinct questions separate:

1. **formal recoverability**: can the frozen portfolio recover semantics that are mechanically known because the symbols existed before the text?
2. **natural-language transport**: do the same principles survive independent human-authored language and human annotation ambiguity?

The primary RC7E terminal state is determined by the preregistered formal scientific run. External challenge evidence may qualify or weaken later architecture claims but cannot retroactively repair the primary held-out result.