# CAL Semantic Family Gate-0 Campaign — Terminal Synthesis

Date: 2026-09-17

Classification: Draft Research Analysis / family-boundary synthesis.

This synthesis updates the hypotheses in `CAL_SEMANTIC_FAMILY_ROADMAP_RC0.md` using independently branched Gate-0 experiments from terminal M4 parent `607ec560fd53bd56279193a8d39a48b6f80e1012`. It does not register production families, alter `src/`, authorize merge/release, or bypass later measurement/warrant/runtime qualification.

## Terminal map

| Candidate | Gate-0 disposition | Exact qualified head | Run | Architecture consequence |
|---|---|---|---|---|
| `strict_comparison` | previously qualified | inherited | inherited | keep frozen baseline |
| `direct_event_order` | previously qualified | inherited | inherited | keep frozen baseline |
| `deontic_norm` | SUPPORTED WITH BOUNDS | `791cd59fa47ba8e7a709f289584468aa9e255334` | `35276294013` | one conservative norm family can contain permission, prohibition, obligation, and permission-restricted-to without stronger implication |
| `population_membership` | SUPPORTED WITH BOUNDS | `3abb817e6d6aeea4498a8495e3b4d5b54f984be6` | `35279852082` | narrow atomic family to membership + directed subset/subclass semantics; move old umbrella concerns outward |
| `scalar_value` | SUPPORTED WITH BOUNDS | `c3b7e13d8940f20fcd476eb6b96f276e78e309ec` | `35279629280` | distinct scalar-state family justified for exact/bounded values under exact entity/metric/unit binding |
| `event_occurrence` | SUPPORTED WITH BOUNDS | `eaef6c19dbe897e70af89b24d8599cfa05c335a1` | `35279644753` | keep occurrence separate from direct event order |
| `attribute_state` | SUPPORTED WITH BOUNDS | `2b4ae5c52f301f16de50719cb11e61919766aa94` | `35279662121` | narrow closed functional-attribute family justified; reject generic SPO escape hatch |
| `typed_binary_relation` | SUPPORTED WITH BOUNDS | `7463ada3358f24fa5bb53fe82631a69064346bf3` | `35279675459` | closed predicate contracts with explicit inverse/symmetry metadata are sufficient for tested atomic relations |
| `spatial_relation` | SEPARATE ATOMIC FAMILY NOT JUSTIFIED YET | `7463ada3358f24fa5bb53fe82631a69064346bf3` | `35279675459` | tested atomic spatial predicates collapse into `typed_binary_relation`; retain as a recombination/integration hypothesis for richer spatial cases |
| `causal_relation` | SUPPORTED WITH STRONG BOUNDARY | `0bfcfe532bd7dcbe0d9049c0e73173f40d05a415` | `35279704215` | explicit typed causal assertions can form a family; causal inference from observations remains unqualified |
| `quantitative_change` | SEPARATE ATOMIC FAMILY NOT JUSTIFIED YET | `309f9ccbb91a24096f3f825e9dc2d8f8ee6aa88a` | `35279720507` | exact change derives from two scalar states + temporal order; retain as a composition/integration hypothesis for richer change claims |

## What the campaign changed

The initial roadmap was intentionally permissive. The campaign reduced two proposed atomic-family hypotheses rather than merely confirming everything:

1. `spatial_relation` did not require its own atomic plugin for the tested closed predicates. `ADJACENT_TO`, `NORTH_OF`/`SOUTH_OF`, and `IN`/`CONTAINS` were handled by the same typed-binary relation algebra using explicit predicate metadata.
2. `quantitative_change` did not require its own atomic family for exact absolute increase/decrease/unchanged/delta. The semantics were reconstructable from two exact scalar states with matching bindings and temporal order.

That is evidence for a smaller **atomic kernel under the tested bounds**. It is not evidence that the corresponding capabilities should be deleted, permanently excluded, or prevented from receiving specialized integration machinery.

## Back-burner recombination and integration hypotheses

Gate 0 tested isolated typed semantics. It did **not** test whether a phenomenon that is unnecessary as an atomic family becomes useful or necessary when propositions are combined, when derived results need their own provenance identity, or when downstream contracts require a first-class representation.

Accordingly:

- `spatial_relation` remains an active back-burner hypothesis for richer cases such as containment chains, topology, frames of reference, metric geometry, spatial-temporal combinations, and cross-relation composition. The next question is not "should spatial exist?" but "does a closed typed-binary relation plus composition remain sufficient once those cases are exercised?"
- `quantitative_change` remains an active composition/integration hypothesis for percentage change, percentage-point change, ratios, rates, compound change, uncertainty propagation, approximate states, unit conversion, and multi-step temporal derivation. A dedicated composition operator, derived-proposition type, or provenance-bearing adapter may eventually be justified even if a standalone atomic family is not.
- The same rule applies to every Gate-0 boundary. Combination tests may split a family, collapse two families, or justify specialized integration machinery without changing the atomic taxonomy.

A capability therefore has three distinct possible homes:

1. an **atomic semantic family** when it needs its own proposition contract and relation algebra;
2. a **modifier/composition/integration module** when it combines or qualifies already-warranted atoms;
3. a **deferred hypothesis** when current evidence cannot yet distinguish those options.

"Not justified as a separate atomic family" must not be read as "ruled out."

## Cross-cutting modifier position remains unchanged

Nothing in these Gate-0 results promotes assertion scope/attribution, negation, epistemic modality, conditions/exceptions, temporal applicability, quantifier/cardinality scope, entity/coreference/role binding, unit normalization, or interpretation-authority state into independent deciding families.

They remain modifier/jurisdiction candidates unless a future discriminating experiment shows that one needs its own typed proposition and distinct relation algebra.

In particular:

- historical assertion/scope work remains insufficient for deciding authority;
- deontic exception/condition/time fields remained scope bindings in RC0;
- population RC0 supports moving quantifier, deontic `only`, group/event scope, role binding, and temporal applicability out of the old population umbrella rather than deleting their semantic importance;
- unit conversion was not qualified merely because scalar identity requires a unit field.

## Preserved negative and failure evidence

Every new lane first froze evaluator controls and candidate falsifiers with the candidate absent. The expected capability-absence baselines were preserved.

The campaign also preserved tooling failures rather than relabeling them as semantic failures:

- deontic exposed frozen-apparatus Ruff hygiene and candidate-format failures before a clean exact-head qualification;
- population exposed frozen-apparatus lint and candidate-format failures before exact-head qualification;
- the first typed/spatial candidate run passed evaluator/candidate/full-repository tests but failed because the generic workflow attempted to format already-frozen apparatus.

That last failure exposed a shared harness defect. The successor workflows retained exact `git diff` guards over frozen apparatus/tests while restricting Ruff/format to the newly exposed candidate. No evaluator material was reformatted to manufacture green results.

No Gate-0 family candidate produced a preserved semantic counterexample against its final frozen contract. That is bounded evidence about these typed contracts, not evidence that natural language, source completion, combinations, or the full pipeline will behave equivalently.

## Smallest next pressure-test stage

Do **not** register all supported families in production from Gate 0.

The next stage should test the smallest set of cross-family machinery that can falsify this taxonomy under realistic CAL operation:

1. define one reusable modifier envelope for scope/attribution, negation, condition/exception, temporal applicability, and explicit unknown;
2. select a small representative set of supported families spanning different algebras: `deontic_norm`, `population_membership`, `scalar_value`, `event_occurrence`, `attribute_state`, and `typed_binary_relation`;
3. for each, test source completion/warrant independently from the Gate-0 relation consumer;
4. attack modifier binding with swaps, omissions, contradictions, nested scope, and unsupported language;
5. run **paired combination discriminators** where the atomic result may be insufficient, including scalar + temporal → quantitative change, typed relation + containment/topology → spatial behavior, membership + deontic, occurrence + order, and state + temporal applicability;
6. for each paired case, compare at least two architectures: generic composition over existing atoms versus a specialized family/module. Require a concrete loss, unsafe inference, or provenance/contract failure before promoting the specialized form;
7. use M4 shadow observation to test secondary measurements without granting them authority;
8. only after warrant and combination behavior survive, wire one family or composition module at a time through plugin registration, claim compiler, Contract B intake, native CAL trace, Contract C, and Decision Engine;
9. retain `causal_relation` behind a stronger gate because explicit assertion interpretation is far weaker than causal inference;
10. keep `spatial_relation` and `quantitative_change` on the active test backlog even while they remain outside the atomic production-family set.

A later EDR can select the production taxonomy and integration modules after these operational and combination tests. Gate 0 alone is not that EDR.

## Terminal campaign state

**SUPPORTED WITH BOUNDS as a Gate-0 family taxonomy evidence record.**

The smallest evidence-supported atomic set after this campaign is:

- `strict_comparison`;
- `direct_event_order`;
- `deontic_norm`;
- `population_membership`;
- `scalar_value`;
- `event_occurrence`;
- `attribute_state`;
- `typed_binary_relation`;
- explicit-assertion `causal_relation`, held behind a stronger downstream gate.

`spatial_relation` and `quantitative_change` are **not separate atomic families under the tested bounds**, but both remain active recombination/integration hypotheses for later pressure testing.
