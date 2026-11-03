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

## Implementation and boundary

`candidate_adapter.py` exports `analyze(claim, evidence)`. The candidate is a
standard-library-only, deterministic instrument with no runtime file, network,
model, evaluator, or label access. It independently parses each original input
before comparing the resulting observations. This is a bounded grammar, not a
general natural-language parser.

It distinguishes percent levels, relative percent change, percentage points,
and basis points; `pp` remains an unregistered ambiguous abbreviation. Values
use exact fractions constructed from decimal strings. A change from one percent
level to another derives absolute and, for a positive starting level, relative
change separately. The registered absolute conversion is 100 bp = 1 percentage
point. Units, property, measurement aspect, time scope, comparator, negation,
original text spans, and input hashes remain in the receipts.

Evidence entails a claim only when its compatible numeric constraints are a
subset of the claim's constraints. Disjoint constraints refute; overlap remains
unresolved. Before claim selection, source-only consistency checks cover every
parsed quantity family. A contradiction in any family for the claim's property,
scope and aspect produces `material_conflict`, including relative contradictions
when the claim asks about absolute change. Conflicts about other properties are
retained in `source_conflicts`. Selection uses declared properties before numeric
values and retains the complete independent source observations. Conversion
provenance covers every selected observation; the legacy scalar is populated
only for a single applied rule, while `applied_rules` and per-observation
provenance retain all rules when multiple conversions contribute.

The grammar recognizes simple level/bound clauses, increases/decreases, and
percent endpoints, with a single explicit year and limited clause separators.
Unparsed clauses block a decisive result. Conditional or modal claims, tables,
anaphora, general numeric counts, compound claims, and richer temporal or
linguistic scope are not qualified. Missing scope and explicit scope do not
silently match. Abstention is an intended result for unsupported inputs.

The older V2 pair format has an explicitly labeled property/aspect projection
for level-versus-change comparisons. The source-local observations never change
to satisfy that view. V3 spans declare the deciding text; neither those spans
nor the full-input `consumed_spans` establish observed causal consumption.
See `DEVELOPMENT_LOG.md` for the original U07 discrepancy and its correction.

Changes are confined to this new research directory and a dedicated
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

## Reproduction

From the repository root with Python 3.12:

```sh
python3 research/cal_quantity_unit_development_d1_20261103/run_development.py \
  --out /tmp/cal-quantity-unit-d1-new-result
```

Use a previously nonexistent output directory. The runner refuses overwrites,
verifies all six reused input Git blobs, runs the unchanged V1/V2/V3 self-tests
and candidate checks, compares the predecessor, and executes development
controls. It records code/input hashes, interpreter version, exit statuses,
stream hashes, candidate receipts, and the bounded result. Public stdout/stderr
replace only the local checkout prefix; raw stream hashes remain recorded.

The dedicated workflow performs the same bounded check with a sparse checkout
and read-only repository permissions. Its artifacts are development evidence.
`evidence/development_01/` preserves the initial exact-input V2/V3 failure;
later evidence directories never replace it. Development iteration is allowed
here and must not be represented as a fresh scientific qualification attempt.

## Current disposition

The candidate is implemented as a Draft research PR. Development results and
review are recorded with their exact subject identities. Scientific and runtime
qualification remain `NOT_RUN`; blind implementation and fresh generalization
remain unestablished. A future D1 evaluation needs its own reviewed protocol.
