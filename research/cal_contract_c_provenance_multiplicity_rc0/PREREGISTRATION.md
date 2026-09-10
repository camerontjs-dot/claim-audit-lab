# Contract C Provenance Repair Multiplicity Pressure Test RC0

## Classification

Draft Research Infrastructure successor pressure test. It evaluates the exact four shadow repair candidates from run `34505939946`; it does not modify them, Contract C, CAL production, Decision Engine production, Contract E, or any release/promotion state.

## Exact predecessor

- repair-comparison candidate head: `bd1e0a0b171eed8a74445052202f938e3b734f74`
- `candidates.py` blob: `a7934b3c242dcf1c33a28121b3b141c9c6adc203`
- repair comparison run: `34505939946`
- artifact: `10163796168`
- artifact digest: `sha256:0cfdcec38a779bf30f0f2f1504056a94379fb5c3f15fda0a35e776f8fc63e985`
- predecessor disposition: `NO_UNIQUE_REPAIR_SELECTED`

All four candidates could recover exact unresolved evidence in the first comparison. That is necessary but not sufficient.

## New discriminator

The frozen temporal composer has explicit causal multiplicity semantics.

For a positive temporal proposition, create two separately warranted negative-event relations `U1` and `U2` such that:

- `U1` alone -> `abstained / unresolved_categorical_relation`;
- `U2` alone -> the same;
- `U1 + U2` -> the same;
- removing either one from the pair therefore leaves a sufficient unresolved relation.

Within this bounded composition rule, `U1` and `U2` are independent sufficient alternatives for the terminal unresolved abstention, not jointly necessary evidence and not an undifferentiated two-item list.

## Question

Does each frozen repair candidate preserve both:

1. exact causal evidence provenance; and
2. the demonstrated independent-sufficiency multiplicity of the two unresolved causal relations?

## Candidate-specific expectations

No expectation is treated as a pass merely because it was intended by the candidate design.

- Candidate A encodes each unresolved evidence item as a separate non-polarized causal contribution and currently labels two such basis members `independent_sufficient_alternatives`.
- Candidate B attaches multiple evidence references to one opaque state basis through one state-evidence link.
- Candidate C embeds multiple evidence references into one opaque state basis member.
- Candidate D attaches multiple evidence references to one opaque state basis through a sidecar.

The latter three may preserve exact references while collapsing multiplicity. The experiment must measure rather than assume this.

## Independent multiplicity consumer

The consumer receives only each candidate's shadow representation and its documented candidate semantics. It may not inspect CAL source, temporal source prose, or the evaluator's ground truth.

It must answer:

- which exact evidence references are causal;
- whether they are `single_necessary`, `independent_sufficient_alternatives`, `jointly_sufficient`, or not reconstructable at that granularity.

A raw array length of two is not evidence of independent sufficiency.

## Falsifier

A repair candidate is falsified for the stronger causal-attribution obligation if it can recover both evidence references but cannot distinguish independent sufficient alternatives from jointly sufficient or otherwise grouped evidence.

## Success scope

If one frozen candidate uniquely preserves both provenance and multiplicity in this pressure test, that supports only that shadow representation as the leading design for a later cross-repository contract experiment. It does not authorize a Contract C version change.
