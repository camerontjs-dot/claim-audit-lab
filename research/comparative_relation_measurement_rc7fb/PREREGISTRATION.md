# RC7F-B Comparative / Quantitative Relation Measurement — Preregistration

Status: **FROZEN BEFORE CANDIDATE IMPLEMENTATION AND BEFORE HELD-OUT COHORT**

## Lineage

- repository: `camerontjs-dot/claim-audit-lab`
- exact parent evidence: RC7E terminal evidence commit `34e9bcafad2c63c9b0761ffc456532344bc75b88`
- parent accepted run: `33448511982`
- parent comparison residue: `4/4` tested gold comparison dimensions unobserved by the complete RC7E proposal union
- production `src/` must remain unchanged

RC7F-B is independent of RC7F-A's scope candidate. It tests a missing **measurement jurisdiction**, not semantic authorization.

## Question

Can a bounded non-LLM comparison specialist recover explicit comparative relations, their direction, and their left/right attachment from untouched source text without producing comparison proposals from lexical/domain traps?

## Output contract

A comparison proposal contains:

- `left`: normalized compared entity;
- `relation`: one of `MORE_THAN`, `FEWER_THAN`, `GREATER_THAN`, `LESS_THAN`, `EQUAL_TO`, `MULTIPLE_OF`;
- `right`: normalized compared entity or scalar reference;
- optional `delta_surface`;
- optional `measure_surface`;
- exact source span / cue;
- `status`: `CLAIMED` or `UNRESOLVED`.

The instrument has **no authority jurisdiction**. A correct comparison proposal is still only a measurement.

## Candidate boundary

Start with a small deterministic comparator grammar. Allowed cues include explicit constructions such as:

- `N more than X` / `N fewer than X`;
- `greater/higher/larger ... than`;
- `less/lower/smaller ... than`;
- `equal to` / `the same ... as`;
- `twice ... as` / `half ... as`;
- explicit scalar-threshold comparisons.

The candidate must preserve direction rather than canonicalizing away `more` versus `fewer`. It must not infer comparisons from unrelated co-occurrence of two quantities.

A bounded non-generative relation-extraction model is allowed only in a later successor if deterministic grammar leaves material residue. No generative LLM, LLM judge, or LLM-generated post-hoc gold labeling is allowed.

## Pre-held-out qualification

Qualification must include:

- entity-to-entity delta more/fewer;
- greater/lower share/rate;
- equality;
- multiplier comparison;
- scalar threshold;
- direction-changing minimal pairs;
- no-comparison controls containing words like `greater`, `lower`, `more`, or `comparison` in irrelevant contexts;
- two quantities with no comparative relation;
- ambiguous constructions that should return unresolved rather than guess.

Implementation defects may be repaired before apparatus freeze. Failures remain recorded.

## Held-out construction

Held-out cases are created only after candidate/evaluator freeze.

Gold is semantics-first. A formal comparison atom is created before deterministic rendering. No candidate/model output establishes or revises gold.

Required families:

1. delta `more than`;
2. delta `fewer/less than`;
3. greater/higher share or rate;
4. lower/smaller share or rate;
5. equality/same-as;
6. multiplier (`twice`, `half`);
7. scalar threshold;
8. comparison + explicit quantity;
9. meaning-changing direction pairs;
10. meaning-preserving paraphrase pairs;
11. domain-word traps and unrelated dual quantities;
12. deliberately unsupported ambiguous cases.

Held-out names, quantities, verbs, and objects must differ materially from qualification probes.

As in RC7F-A, identical normalized raw-source text may not carry incompatible gold comparison objects.

## Metrics

Primary:

- typed comparison precision;
- typed comparison recall;
- relation-direction accuracy;
- left/right attachment accuracy;
- false comparison proposals on negative controls;
- unresolved rate.

Metamorphic:

- direction-changing pair accuracy;
- meaning-preserving paraphrase stability.

Baseline: `NO_COMPARISON_INSTRUMENT` with recall `0` and no false proposals.

## Success criteria

`COMPARISON_INSTRUMENT_CANDIDATE_READY_FOR_HARDENING` requires:

- typed comparison precision = `1.0`;
- typed comparison recall >= `0.90` on the supported held-out comparison jurisdiction;
- relation-direction accuracy = `1.0` for resolved proposals;
- left/right attachment accuracy = `1.0` for resolved entity-to-entity proposals;
- false comparison proposals on no-comparison/domain-trap cases = `0`;
- meaning-changing direction accuracy = `1.0`;
- no evaluator/cohort invariant failure;
- no post-reveal repair.

`MORE_COMPARISON_RESEARCH_JUSTIFIED` applies when a bounded, identifiable comparative family remains unresolved or safely missed.

`COMPARISON_ARCHITECTURE_FALSIFIED_OR_INCONCLUSIVE` applies when the apparatus/evaluator is invalid or the candidate cannot discriminate comparison relations without unsafe false proposals.

## Nonclaims

This experiment does not:

- authorize comparison propositions;
- solve quantity attachment generally;
- establish narrator-level factuality;
- modify production CAL;
- modify Contract E;
- authorize an LLM lane;
- authorize a release or merge.

## Next gate if supported

Freeze the comparison proposal contract and test it as one input to the broader semantic capability portfolio. It must remain subordinate to scope/warrant authority rather than becoming authoritative because its parser confidence is high.
