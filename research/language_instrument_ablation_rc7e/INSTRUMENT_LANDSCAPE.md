# RC7E maintained non-LLM instrument landscape

Research performed 2026-08-31 before held-out construction. Package/model identities below are apparatus inputs, not endorsements or semantic authority.

## Selected

- **Stanza 1.14.0** — maintained Stanford NLP pipeline, released 2026-07-15. Used for English tokenization/POS/lemma/UD dependency and constituency representations. Apache-2.0 project family.
- **Stanford CoreNLP 4.5.10** — current CoreNLP release family. Used for OpenIE, Natural Logic, SUTime-backed NER, coreference and quote attribution. GPL-3.0. Its annotators share underlying syntactic machinery, so their errors are expected to be correlated and will be measured as such.
- **Quantulum3 0.10.0** — current PyPI release 2026-03-09, MIT. Used only for bounded quantity/unit measurement.
- **SuPar 1.1.4 / `sdp-biaffine-en`** — MIT semantic-dependency parser using the DM representation from SemEval-2014 Task 8. The PyPI release is old relative to the rest of the portfolio, so it is conditional on pre-held-out runtime qualification rather than presumed usable.
- **MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli** at revision `e5350efffb6dea3ad0962eafd0bc0b9e212a9ff8` — MIT, 0.2B-parameter discriminative sequence-classification model trained on MultiNLI, FEVER-NLI and ANLI. Used only to measure entailment/neutral/contradiction relations for independently typed proposals. No generation, routing authority, gold labeling or automatic authorization.
- **RDFLib 7.6.0 + OWL-RL 7.6.2** — maintained 2026 symbolic stack. Used only for subclass closure over already-warranted typed propositions.

## Rejected or not instantiated

- **AllenNLP SRL:** maintenance-only posture with old dependency surface. Not chosen for a new 2026 apparatus.
- **TUPA/UCCA:** repository archived 2025-08-05. Scientifically interesting representation, but not a maintained practical instrument for this run.
- **AMRLib:** primary parsing path uses seq2seq BART/T5-family generation. Excluded by the experiment's no-generative-LLM boundary.
- **PropBank/FrameNet SRL:** current search surfaced stale research stacks and poorly established alternatives, but no implementation whose maintenance, licensing, output contract and runtime posture were strong enough to freeze for this main run. The category remains a visible gap.
- **Standalone CCG:** no sufficiently maintained/practical implementation established during this research window. Omitted rather than filling a category with weak machinery.
- **Full temporal event ordering:** SUTime provides temporal expressions/normalization, not a complete event-ordering semantics. This remains explicit residue.
- **General factuality/deontic/counterfactual scope:** CoreNLP Natural Logic provides polarity/quantifier machinery but does not claim this complete jurisdiction.

## Architecture note

Different annotators from one package are not automatically different measurement principles. RC7E records runtime-family identity and pairwise error correlation to distinguish genuinely independent information from repackaged shared machinery.
