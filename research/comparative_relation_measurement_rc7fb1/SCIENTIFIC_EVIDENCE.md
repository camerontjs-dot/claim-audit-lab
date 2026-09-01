# RC7F-B1 Comparative Relation Measurement — Terminal Evidence

Status: **TERMINAL RESEARCH EVIDENCE**

Terminal token:

`COMPARISON_INSTRUMENT_CANDIDATE_READY_FOR_HARDENING`

## Immutable lineage

- parent RC7F-B evidence: `3009da45e98dac099c4758c1d41ff42cf2a56eae`
- preregistration: `750cfe288cf58a9ae2f7c2629e9e77a8ad80e608`
- apparatus freeze: `e3463a7c92747fa9583d5abde230b89373756693`
- qualification run: `33464436835`
- qualification artifact: `9784332950`
- qualification digest: `sha256:620c10630f71c6d99a7c5aa45badb4a91aaaf5e26cefe21e56e07c12889a4f02`
- first held-out freeze: `611a87680a8604998bed63f2642f31dd2cb4a591`
- first held-out guard run: `33464911009`
- failed guard artifact: `9784489485`
- failed guard digest: `sha256:d018892dd06b09711eefe78d19a2e2cbefbc16ee5ac64b2b8e6c96832dbccfe7`
- cohort-only R1 correction: `2127c39c8702ab6ce9aa4467e1c57d598cf6450d`
- R1 held-out/deviation freeze: `f386da3d80eabfae836ab37c59a4ecf77f172634`
- accepted scientific run: `33465045942`
- scientific artifact: `9784534254`
- artifact ZIP digest: `sha256:2c65ddfc0f2bc7a91a34ee6ea4c09d8a696a5cc7538b2e4e86e64e8788e89e67`

The production `src/` guard passed. Candidate/evaluator code was unchanged after held-out creation.

## Preserved cohort deviation

The first held-out file contained 68 frozen cases but its terminal bookkeeping assertion incorrectly required 64. Run `33464911009` failed in the cohort guard before the scientific candidate executed. No held-out candidate output was observed in that run.

R1 changed only the cohort identity/count guard to 68 and recorded the deviation in `COHORT_DEVIATIONS.md`. Case definitions and semantic gold objects were unchanged.

## Scientific result

Accepted R1 result over 68 cases, including 56 supported comparison-positive cases:

- true positives: `56`
- false proposals: `0`
- misses: `0`
- typed precision: `1.000000`
- typed recall: `1.000000`
- direction accuracy: `1.000000`
- left/right attachment accuracy: `1.000000`
- false proposals on negative/unsupported controls: `0`
- unresolved rate: `0.102941`

Pair-state evaluator correction:

- `stable_correct`: `6`
- `stable_abstention`: `0`
- `stable_wrong`: `0`
- meaning-changing pairs correct: `16/16`

The parent evaluator weakness that counted paired abstention as generic stability is therefore not repeated.

## Supported bounded observation jurisdiction

The candidate recovered the parent-supported comparison families plus the preregistered successor residue:

- numeric `more/fewer/less than` delta;
- comparative adjective + explicit measure head + `than`;
- `exceeded ... by` / `trailed ... by`;
- equality;
- multiplier;
- scalar threshold.

Unsupported/synonym/domain traps remain non-proposals rather than being guessed.

## Interpretation

RC7E comparison was unobserved and RC7F-B achieved safe partial measurement. RC7F-B1 now supports a bounded comparison-measurement candidate for hardening under the frozen cohort. This is evidence for **measurement capability only**.

A comparison proposal still does not acquire semantic warrant merely because direction and attachment were measured correctly.

## Design principle preserved

> **CAL may know that it observed something without claiming that it knows the thing is true. When warrant is incomplete, abstention is a successful outcome.**

## Nonclaims

This record does not authorize comparison propositions, production CAL behavior, operational execution, an LLM lane, release, or merge. General relation extraction outside the frozen bounded jurisdiction remains unevaluated.
