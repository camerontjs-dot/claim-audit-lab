# CAL Strict Comparison RC1 Authority Pressure RC0 — Terminal Result

Date: 2026-09-17

Classification: Draft Research / post-qualification adversarial pressure test.

## Frozen subject

- CAL V1 RC1 semantic implementation: `a902621e8baea3063dddd7f92ba975aade305464`
- pressure apparatus head: `98e34749351ad5206022a07220aeb1982893cc12`
- decisive pressure run: `35294364472`
- raw measurement precursor: PR #139

Production `src/` was verified unchanged.

## Disposition

**FALSIFIED_MODIFIER_SAFE_STRICT_COMPARISON_AUTHORITY.**

RC1's independent source re-grounding does not repair all modifier loss from strict-comparison measurement.

## Observed unsafe deciding cases

Six preregistered pressure cases reached a deciding `SUPPORTED` or `CONTRADICTED` terminal result instead of `NOT_CHECKABLE`:

- `SC-RC1-01`: `Sector A was not higher than Sector B.`
- `SC-RC1-02`: `Sector A was no higher than Sector B.`
- `SC-RC1-03`: `Sector A was probably higher than Sector B.`
- `SC-RC1-04`: `Sector A was allegedly higher than Sector B.`
- `SC-RC1-05`: `Sector A may be higher than Sector B.`
- `SC-RC1-06`: `Sector A could be higher than Sector B.`

The positive control remained supported.

The remaining seven pressure cases failed closed before a deciding relation, largely because the maintained RC1 measurement surface does not support those forms.

## Why the failure matters

The RC1 authority-integrity layer independently re-runs `_strict_source_fields` against the admitted source. However, that completion grammar accepts several of the same modifier-bearing surfaces as the measurement grammar and reconstructs the same positive relation.

Therefore the two stages are independent in execution and identity, but **not sufficiently independent in semantic assumptions** for these modifier classes.

This is not an RC8J identity-integrity failure. The source completion itself reconstructs the wrong incomplete semantic object.

## Smallest successor hypothesis

Do not widen or replace comparison extraction.

Insert an independently testable **direct-assertion / modifier eligibility gate** before a comparison atom may become warranted. At minimum it must discriminate:

- narrator-level direct assertion vs reporting/attribution;
- positive relation vs relation negation;
- asserted vs epistemically modal relation;
- unconditional vs conditional relation;
- single proposition vs unsupported composition.

The existing comparison measurement may remain proposal-only behind that gate.

## Successor discipline

The six observed failures are now development evidence, not a fresh qualification cohort.

A successor candidate must be frozen before a fresh paraphrase/mutation pressure cohort is added. Candidate repair after that reveal is prohibited.

## Non-claims

This does not invalidate RC1 authority-integrity results for stale IDs/rehashed forgeries, nor the original RC7F-B1 measurement result inside its frozen cohort. It falsifies modifier-safe deciding strict-comparison authority as currently composed. No production change, merge, release, or promotion is authorized.
