# CAL Strict Comparison Measurement Hardening RC0 — Terminal Result

Date: 2026-09-17

Classification: Draft Research / adversarial hardening.

## Frozen subject

- RC7F-B1 evidence head: `0ecdedc5cea970485a635508255f3670ab231c33`
- comparator blob: `33820f55e2a87c4de6336fca6b5e5b93a2bccde3`
- prior terminal: `COMPARISON_INSTRUMENT_CANDIDATE_READY_FOR_HARDENING`
- hardening apparatus head: `94a4cdabde9fe03253b8409e25c98b1b0698dfdc`
- hardening run: `35292180149`

The exact comparator and production `src/` were verified unchanged before execution.

## Disposition

**FALSIFIED FOR MODIFIER-SAFE STANDALONE MEASUREMENT.**

This does not falsify the original RC7F-B1 bounded result. It falsifies the stronger interpretation that the frozen comparison proposal can safely stand alone when comparison cues occur under material modifiers its proposal type does not represent.

## Preserved positives

All six MUST_RETAIN controls remained exact:

- numeric delta;
- adjective + explicit measure head;
- comparative verb;
- equality;
- multiplier;
- scalar threshold.

All six fresh DIAGNOSTIC claims were also exact:

- overlapping entity strings `Women` / `Men`;
- hyphenated entities;
- `slightly higher than`;
- percentage-point trailing delta;
- `half as ... as`;
- scalar `remained less than`.

There were zero diagnostic wrong claims and zero inherited-regression failures.

## Hardening counterexamples

The comparator emitted a plain positive comparison atom for 10 FAIL_CLOSED cases:

- `SCF01`: `Sector A was not higher than Sector B.`
- `SCF02`: `Sector A was no higher than Sector B.`
- `SCF03`: `Sector A was probably higher than Sector B.`
- `SCF04`: `Sector A was allegedly higher than Sector B.`
- `SCF05`: `Sector A may be higher than Sector B.`
- `SCF06`: `Sector A could be higher than Sector B.`
- `SCF08`: `The report says Sector A is higher than Sector B.`
- `SCF09`: `Sector A is not equal to Sector B.`
- `SCF10`: `Sector A is not the same as Sector B.`
- `SCF11`: `Sector A produced not twice as many units as Sector B.`

The conditional control and the two multi-comparison controls failed closed, so the defect is not generic cue matching. It is specifically that several supported comparison patterns tolerate material prefix/modifier text while the proposal schema retains only the positive relation and endpoints.

## Architectural consequence

RC7F-B1 remains strong evidence for bounded **surface comparison observation**, but its output must not be treated as a complete comparison-state proposal in the presence of unrepresented modifier/scope language.

The smallest successor question is not “improve comparison parsing” in general. It is:

> Can a modifier-aware envelope preserve comparison observation while explicitly binding negation, epistemic modality, attribution, and similar scope state before the atom is eligible for warrant?

Until that is qualified, either:

1. a pre-measurement modifier/scope gate must block these surfaces; or
2. the measurement proposal must carry the material modifier state explicitly.

A downstream warrant layer cannot recover distinctions that were already erased from the measurement receipt unless it independently re-reads the source.

## Preserved failure

Run `35292180149` verified the immutable subject, printed all observations, then failed exactly at the preregistered fail-closed acceptance test. Static checks were skipped after the semantic failure. The candidate was not repaired and the corpus was not rewritten.

## Non-claims

This result does not invalidate RC7F-B1 inside its original frozen cohort, does not establish a successor implementation, does not alter the qualified strict-comparison relation algebra, and does not authorize production changes, merge, or release.
