# Quantity/unit D1: informed development candidate

## Decision and authority

On 2026-11-03 Cameron requested a quantity/unit candidate on GitHub while a
local Codex task addresses the separate RC8 18-case runtime qualification.
This is ordinary, informed development under CAL #205, alongside the blocked
#212/#214 qualification. It does not execute or satisfy the constrained S1
builder task. The implementer has seen owner records and exposed failures.

Question: can an explicitly bounded quantity instrument preserve lexical
unit identity, role, measure, scope and comparator, perform exact registered
conversions, and produce truthful V2/V3 development receipts?

Base: CAL #214 at `a10e61f0d4be26ebb93a2b798d1a5f46470cc42c`.
This PR is stacked only to reuse the exact exposed evaluators and predecessor
baseline. It changes no historical input, evaluator, source, result or freeze.

## Evidence reused and remaining uncertainty

- #209 and #211 preserve critical false supports. In particular, the old
  comparator can consume `percent` inside `percentage points`.
- The pinned RC2 comparator remains the exposed development control; its
  published 19-case comparison matched 6 relations and gave 4 false supports.
- Reuse the unchanged 19-case V1 evaluator and S1 V2/V3 receipt evaluators.
  They test bounded exposed conformance, not natural-language generalization
  or observed causal consumption.
- Python's standard-library `fractions.Fraction`, constructed from decimal
  text, supplies exact rational arithmetic. Arithmetic correctness does not
  establish correct linguistic binding. No new package/model is required.
  Primary reference: https://docs.python.org/3/library/fractions.html

Remaining local questions are unit/role binding, full-clause coverage,
selection among measures, contrary evidence, and truthful spans. Development
checks may iterate; every observed failed check is retained in the development
log. No fresh-source or held-out success is claimed.

## Implementation boundary

The candidate will parse claim and evidence independently. It will keep all
parsed source observations before selecting compatible comparisons. Exact
percentage-point/basis-point conversions and endpoint-derived absolute and
relative changes retain their identities. Unsupported syntax and ambiguity
remain explicit. Candidate runtime must not import evaluators or labels.

Changes are confined to this new research directory and a dedicated optional
development workflow. Production `src/`, contracts, synthesis weights,
Decision Engine, package versions, historical candidates and frozen cohorts
remain unchanged. No calibration or held-out bodies/labels are opened.

## Development completion criteria

1. A runnable `analyze(claim, evidence)` candidate with bounded grammar and
   typed receipts, plus documented unsupported inputs.
2. Actual execution of the unchanged exposed V1/V2/V3 checks, with all results
   preserved, and additional adversarial/metamorphic development controls.
3. Exact candidate/input/environment identities and a reproducible runner.
4. Review limitations and first failed checks retained, including evaluator
   gaps if exposed. No production or held-out qualification follows.

## Coordination with the local runtime task

RC8 belongs to apparatus-contracts #173/#177/#186. Its model-free 18 controls,
admission evidence, frozen pins and one-shot budget remain separate. This
candidate is not an input to RC8. The local runtime controller must not pass
this informed candidate or its results into the frozen S1 builder aperture.
Any later evaluation of D1 needs its own explicit admission/protocol decision;
it cannot inherit a blind-implementation claim from #214.

## Initial state

`DEVELOPMENT_IN_PROGRESS`; candidate and development results will be added to
this same Draft PR. Scientific qualification remains `NOT_RUN`.
