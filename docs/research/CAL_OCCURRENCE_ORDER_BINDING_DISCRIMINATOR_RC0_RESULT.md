# CAL Occurrence + Order Binding Discriminator RC0 — Result

Date: 2026-09-18

Classification: Draft Research / terminal cross-family recombination discriminator.

## Disposition

**SUPPORTED FOR PROMOTION, bounded to event-instance identity preservation at the occurrence/order composition seam.**

Field equality alone is falsified for the preregistered repeated-event typed world. A composer that must distinguish multiple event instances with identical actor/action/object/polarity fields needs an additional identity-preserving carrier somewhere in composition state.

The tested explicit `binding_id` representation is sufficient under this apparatus. This result does **not** establish that a production field literally named `binding_id` is the uniquely correct architecture.

## Exact evidence

- terminal semantic-family pressure parent: `b10adbb5f185c093bbe9b7e8e7759f666141cd0e`
- event-occurrence Gate-1B subject: `7cd54f9fb28afa6f5fc0fa2d1e9905cd916e0efe`
- direct-event-order Gate-1B RC3 subject: `b163f0faf58c8fe7e2c74e8d9e8618aa2147a359`
- corrected frozen pre-candidate apparatus: `08c70e209ae8640e5ba079fb895d7325183ab01c`
- successful pre-candidate freeze run: `35348929589`
- candidate implementation commit: `a61cbe96171538cb5c23a737fc010f20d56291a1`
- candidate qualification workflow commit: `1918dae1dc36877d4b2bff067614728af5880f23`
- synchronized candidate-exposure head: `26766b088279f0b8306ed90680927faf4f04f86e`
- candidate qualification run: `35349256765`
- frozen-apparatus regression run on the exposed candidate head: `35349256934`

Observed on the synchronized candidate head:

- frozen apparatus byte guard: PASS;
- production `src/` isolation guard: PASS;
- frozen evaluator controls: 2/2 PASS;
- candidate qualification: PASS;
- all 15 frozen cases matched the oracle;
- candidate report: 3 supported controls and 12 fail-closed cases matched exactly;
- focused static checks: PASS.

The weak controls fail meaningful gates for the intended reasons:

- field-only join is caught by `OU01`, where the semantic event fields match but the event-instance bindings differ;
- binding-only join is caught by `OU04` / `OU05`, where bindings match but semantic fields do not;
- warrant-erasing composition is caught by `OU02` / `OU03`;
- occurrence call-order inference is caught by `OB03`.

## Supported boundary

Within this RC, safe typed recombination may use two warranted occurrence contributions plus one warranted direct-order contribution when:

- the relevant occurrence instances have distinct explicit identities;
- those identities resolve to the exact semantic event fields claimed by the occurrence atoms;
- the order contribution preserves the same endpoint identities and fields;
- query and order normalize to the same BEFORE/AFTER orientation;
- warrant state is preserved;
- contribution call order does not determine temporal order;
- missing, reused, mismatched, or semantically inconsistent identity state fails to `UNRESOLVED`.

This supports a composition-layer event-instance identity invariant. It does not create or justify another atomic semantic family.

## What the result rules out

The tested evidence falsifies these candidate composition policies for the bounded repeated-event world:

- join occurrence and order by semantic field equality alone;
- join by identity while ignoring semantic-field consistency;
- discard warrant state during recombination;
- infer temporal order from contribution input order.

## Alternative explanations and architectural freedom retained

The experiment assumes CAL may eventually need to distinguish repeated event instances that share the same normalized semantic fields. If the product permanently excluded such cases, field equality could remain sufficient only inside that narrower capability boundary.

The evidence does not choose among all possible identity carriers. A stable occurrence/span identity, provenance-bound event index, upstream event object identity, or another mechanically preserved identifier could satisfy the same requirement if independently qualified.

Therefore the supported architectural property is **identity-preserving event binding**, not the exact storage representation used by this research candidate.

## Preserved pre-freeze deviations

Four pre-candidate runs reached the same Ruff I001 import-block formatting issue while the semantic evaluator controls and production-isolation guard were already passing:

- `35348284126`
- `35348368225`
- `35348579046`
- `35348770420`

The successive corrections changed only import spelling / blank-line formatting in the apparatus test. They did not change preregistration, cases, expected relations, weak strategies, subject pins, apparatus semantics, or evaluator logic.

The corrected apparatus was not exposed to candidate code until run `35348929589` was fully green.

## Preserved repository CI defect

Public-suite run `35349256864` failed only at:

`tests/production/test_historical_golden_version_migration.py::test_historical_goldens_only_change_the_distribution_version`

because:

`git show 32275a239b68af383a56bca843e28cbc1e343976:tests/v1/fixtures/traces/01-supported-verbatim.json`

exits 128.

The same exact missing historical object already failed on the scalar parent lineage in Public-suite run `35297087826`. The defect is preserved as repository/CI state and is not counted as semantic evidence for or against this candidate.

## What is not established

This experiment does not establish:

- how event-instance identities should be extracted or assigned from natural language;
- cross-passage coreference or event deduplication;
- that `binding_id` must become a production schema field;
- whether existing provenance/span identities can satisfy the requirement without new state;
- temporal reasoning beyond direct BEFORE/AFTER;
- negative-event temporal semantics;
- Contract C representation;
- Decision Engine behavior;
- production runtime wiring;
- universal composition correctness.

No merge, release, or production mutation is authorized by this result alone.
