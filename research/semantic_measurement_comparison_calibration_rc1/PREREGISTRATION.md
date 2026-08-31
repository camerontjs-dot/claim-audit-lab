# Semantic Measurement Comparison Calibration RC1

## Classification

Post-reveal diagnostic research. Normal context. No production authorization. No LLM or learned model is introduced by this experiment.

This experiment starts from the frozen RC7D-D evidence commit `253af5313e93932875bdd5956ac46246f3796271` and may also inspect prior NLI ensemble/disagreement research as historical evidence.

## Problem

Raw `agreement` / `disagreement` is too coarse to govern heterogeneous semantic measurements.

Two instruments may:

- make the same semantic claim in different representations;
- make compatible partial claims about different facets of the source;
- disagree only about slot boundaries;
- disagree about scope attachment;
- disagree about polarity/operator value;
- disagree about applicability/jurisdiction;
- disagree because one did not see the decisive evidence;
- produce genuinely contradictory claims;
- agree exactly while sharing a correlated error.

Therefore neither equality, majority vote, unanimity, nor a single global instrument score is adequate semantic authority.

## Research question

Can a typed comparison layer classify pairwise semantic measurements into relation classes that are more decision-relevant than raw binary agreement/disagreement, while preserving each native measurement and avoiding automatic truth selection?

Secondary question: can instrument usefulness be represented as a conditional profile by semantic use case and claim facet rather than one global weight?

## Frozen motivating observations

### RC7D-D

Accepted run `33439373393` reported:

- raw-source preservation `1.0`;
- multi-reader proposal dimension recall `0.6286`;
- multi-reader authorized dimension recall `0.6214`;
- multi-reader authorized typed-atom precision `0.8041`;
- `19` unsafe authorized atoms;
- `1` false authorized dimension;
- raw agreement error rate `0.5556`;
- raw disagreement error rate `0.9412`;
- agreement-only `3` unsafe authorized atoms;
- oracle composition `68/68`.

The preserved counterexamples include scope/boundary leakage such as modality, exceptions, and temporal material entering semantic slots.

### NLI Ensemble / Disagreement RC1

Historical NLI work found disagreement strongly enriched for semantic error on a small clean slice, but also found unanimous wrong cases under stress. It also found that evidence visibility / aperture eligibility must be considered before comparing model outputs.

These observations motivate, but do not validate, this comparison taxonomy.

## Core invariants

1. Exact raw source remains independently available to every instrument.
2. Native instrument outputs are preserved and are not overwritten by a common representation.
3. Comparison occurs only after measurement eligibility/provenance is recorded.
4. A comparison relation is evidence about measurements, not authority over source meaning.
5. Agreement never automatically authorizes a claim.
6. Disagreement never automatically identifies which instrument is correct.
7. Gold labels are used only by the evaluator, never by taxonomy classification.
8. No global scalar weight is promoted from this experiment.

## Comparison ontology

The first frozen taxonomy will distinguish at least:

- `EXACT_AGREEMENT`: native semantic atoms are exactly equal.
- `SEMANTIC_EQUIVALENCE`: normalized semantic identity agrees while surface/native representation differs.
- `COMPATIBLE_PARTIAL_OVERLAP`: measurements make compatible claims about overlapping but non-identical facets.
- `COMPLEMENTARY_ORTHOGONAL`: measurements concern different semantic dimensions/facets and are not in conflict.
- `GRANULARITY_MISMATCH`: one measurement decomposes or specializes content represented more coarsely by another.
- `SLOT_BOUNDARY_DISAGREEMENT`: same operator/relation core but argument or predicate boundaries differ.
- `SCOPE_ATTACHMENT_DISAGREEMENT`: modifier, exception, temporal, modal, negation, or conditional scope attaches differently.
- `ROLE_BINDING_DISAGREEMENT`: predicate/participant binding differs.
- `OPERATOR_VALUE_DISAGREEMENT`: quantifier, modality, permission, temporal relation, quantitative kind, or other operator value differs.
- `POLARITY_DISAGREEMENT`: positive/negative polarity differs.
- `JURISDICTION_DISAGREEMENT`: one instrument claims applicability while another is NOT_APPLICABLE/UNRESOLVED for the comparable facet.
- `PROVENANCE_OR_VISIBILITY_DISAGREEMENT`: claimed semantic content may match but decisive-source coverage/provenance differs materially.
- `CONTRADICTION`: claims are mutually incompatible under the comparison contract.
- `INCOMMENSURABLE`: outputs do not make claims in a common comparison space; no agreement/disagreement inference is legal.

A later heterogeneous-instrument experiment may extend this ontology before its held-out corpus, but may not silently collapse these distinctions.

## Claim-facet comparison

Do not require native outputs to have identical schemas.

For heterogeneous instruments, comparisons should be performed through explicit claim facets, for example:

- applicability/jurisdiction;
- predicate identity;
- participant/role binding;
- slot boundary;
- scope attachment;
- polarity;
- quantifier/operator value;
- temporal relation;
- numeric/quantitative relation;
- class/membership relation;
- provenance/evidence visibility.

A dependency parser and an SRL system, for example, need not emit the same object to supply mutually supporting or conflicting claims about an attachment or role.

## Outcome labels for calibration

Gold-aware evaluator outcomes for each comparable pair/facet:

- `BOTH_CORRECT`;
- `LEFT_ONLY_CORRECT`;
- `RIGHT_ONLY_CORRECT`;
- `BOTH_WRONG_SHARED`;
- `BOTH_WRONG_DIFFERENT`;
- `BOTH_VALID_DISTINCT` when multiple gold-compatible claims legitimately differ;
- `NOT_SCORABLE` when the comparison cannot be evaluated under the bounded gold ontology.

These outcome labels must never be available to the classifier itself.

## Instrument usefulness profile

Do not assign one overall reader score.

For each instrument and bounded semantic use case, estimate a vector containing where sample size permits:

- proposal coverage/recall;
- proposal precision;
- authorized precision/recall where an authority layer is tested;
- unique correct contribution;
- residual reduction;
- unsafe proposal/authorization rate;
- disagreement capture rate;
- shared-error rate under agreement;
- source/provenance completeness;
- cost/latency when available.

For each instrument pair + use case + comparison relation, record:

- sample count;
- P(any error | relation);
- P(shared error | relation);
- P(exactly one correct | relation);
- P(both correct | relation);
- whether the relation helps identify risk;
- whether the relation contains information capable of selecting a winner (expected to be rare and requires separate evidence).

## Weighting posture

This experiment does not create production weights.

A future weighting/calibration experiment may test bounded likelihood-ratio or calibrated-probability updates only if:

- the relation taxonomy is frozen;
- calibration uses a separate cohort;
- validation is held out;
- weights are instrument-pair + semantic-use-case specific where necessary;
- effective sample size is sufficient;
- correlated instruments are not treated as independent votes;
- the underlying measurements remain visible after aggregation;
- the weighting layer cannot itself grant semantic authority.

Until then, comparison outputs should be typed evidence states rather than numeric truth scores.

## RC7D-D retrospective diagnostic

The first execution will replay the frozen RC7D-D reader bank and classify pairwise same-dimension comparisons without changing readers, validator, cohort, or evaluator evidence.

This diagnostic may use the frozen cohort gold only after classification to measure whether typed relation classes stratify error more meaningfully than raw agreement/disagreement.

It is explicitly retrospective and cannot establish prospective calibration.

## Success criteria for the retrospective diagnostic

`TYPED_COMPARISON_MORE_INFORMATIVE_WITH_BOUNDS` requires all:

- raw-source identity preserved;
- taxonomy classification never reads gold;
- every comparable pair receives exactly one primary relation class plus optional facets;
- `EXACT_AGREEMENT` / `SEMANTIC_EQUIVALENCE` shared-error cases are preserved;
- disagreement rows distinguish at least scope/boundary/value/jurisdiction classes where present;
- at least one typed relation class has materially different empirical error composition from the pooled raw-disagreement bucket;
- no automatic winner/authority is selected from the relation class.

`RAW_AGREEMENT_TAXONOMY_NOT_IMPROVED` if the typed taxonomy adds no meaningful stratification over raw agreement/disagreement.

`TAXONOMY_APPARATUS_INVALID` if classification depends on gold, mutates source/measurements, or conflates incommensurable outputs as agreement/disagreement.

## Prospective use with the heterogeneous ablation

The important validation is later: apply this frozen comparison contract to the heterogeneous instrument ablation without changing relation definitions in response to its outcomes.

The later test should ask whether relation classes calibrated or hypothesized here predict risk across genuinely different measurement principles.

Do not infer that same-principle RC7D-D statistics transfer to dependency, SRL, OpenIE, AMR/UCCA, temporal, quantitative, or other heterogeneous instruments.

## Scope / non-authorization

This experiment does not authorize production aggregation, reader weighting, majority vote, unanimity rules, Contract C changes, parser changes, or production promotion.
