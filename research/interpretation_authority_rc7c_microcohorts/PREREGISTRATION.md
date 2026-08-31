# RC7C — Interpretation Boundary Microcohort Hardening

## Classification

Research Infrastructure / post-reveal diagnostic hardening. **Not context-free.** Prior RC7B evidence is an authorized input because the objective is to test whether preserved failure mechanisms admit small, explicit, mechanically testable hardenings.

This experiment does not authorize production parser changes, Contract C changes, semantic-operator changes, model changes, aggregation changes, or downstream policy changes.

## Frozen inputs

- RC7B Interpretation Authority Contract v1: aperture head `80c2d2f8c96025ea62e8552ecfd4621cd81ea1f4`
- RC7B A immutable evidence commit: `fc1b3ff7a7ca273d732ef6202c10fb3f24b12750`
- RC7B B immutable evidence commit: `04f52a6506336c5b0772fede9dca25d4f894ef18`
- RC7B sealed evaluator commit: `19e9302a11decb08dda644fbf1018997cf138c3b`
- RC7B failure-localization receipt: `26be3e5d95f7c2690bd357b3dbc6cbd27b4ecd07`

Production `main` is explicitly outside this experiment.

## Objective

Discriminate three mechanisms exposed by RC7B failure localization:

1. **Jurisdiction recognition:** can a small explicit boundary gate reject unsupported conditional, exception, temporal, subclass, quantitative/probabilistic, and cross-family constructions without rejecting supported controls?
2. **Field independence:** do the preserved role-binding polarity and quantifier/population coupling defects reproduce on fresh metamorphic pairs, and are the intended invariants mechanically crisp?
3. **Only-permission construction sufficiency:** can a deliberately small, explicit construction interpreter recover necessary-condition, membership/nonmembership, permission grant/denial/semantic-unknown authority over a fresh bounded micro-language without fabricating missing authority?

The experiment is not designed to make RC7B A or B pass. A and B remain frozen systems under test.

## Microcohort A — jurisdiction gate

Build a new held-out microcohort with approximately equal supported and unsupported examples. Unsupported categories must include at least:

- conditional composition;
- exception systems;
- temporal conditions;
- subclass/subset reasoning;
- numeric/proportional thresholds and exact counts;
- probabilities/likelihood;
- unsupported cross-family composition.

Supported controls must span `only_permission`, `role_binding`, and `quantifier`, including near-collision lexical controls where practical.

Candidate intervention: one deterministic **jurisdiction-only** gate. It may classify `supported` versus `out_of_jurisdiction` and reason category, but must not recover semantic field values.

### Jurisdiction falsifier

The local hardening hypothesis is falsified if either:

- OOD recall < 0.95; or
- supported-control acceptance < 0.95; or
- any category has systematic failure >= 25%.

## Microcohort B — field-independence metamorphics

Create fresh paired examples with preregistered changed-field sets.

Required mutation families:

- role-binding subject/object swap where polarity and predicate must remain invariant;
- role-binding polarity flip where subject/object/predicate must remain invariant;
- quantifier change where population, predicate, and polarity must remain invariant;
- lexical/paraphrase controls with no semantic field changes.

Run frozen A and frozen B on every pair without repair.

### Field-independence falsifier

For each implementation, report pair consistency and unintended-field changes. The observed RC7B coupling mechanism is considered **reproduced** if >= 25% of fresh pairs in the corresponding family show the same unintended-field coupling. It is **not reproduced** if < 10%. Intermediate rates are inconclusive.

No runtime claim is made from a pairwise metamorphic validator; this lane tests whether the semantic decomposition itself yields stable, local invariants.

## Microcohort C — only-permission bounded construction hardening

Create a fresh bounded language covering:

- necessary permission conditions (`only C may P` and direct equivalents);
- explicit membership;
- explicit nonmembership;
- explicit membership semantic unknown;
- explicit permission grant;
- explicit permission denial;
- explicit permission semantic unknown;
- missing membership or permission authority that must remain `insufficient_authority`.

Construct a small deterministic micro-interpreter from the normative contract only after this preregistration is frozen. It must output the same field-receipt shape as Contract v1 for `only_permission` only. It must fail closed outside its declared construction language.

### Only-permission falsifier

The local construction-hardening hypothesis is falsified if any of the following occur on the fresh microcohort:

- any unsafe semantic field assignment;
- exact field status/value recovery < 0.95;
- semantic-unknown recall < 0.95;
- insufficient-authority recall < 0.95;
- necessary-condition recognition < 0.95;
- any preregistered semantic mutation changes an unrelated field.

## Alternative explanations to preserve

1. **Small-rule omission:** RC7B failures may be largely due to a handful of missing construction and jurisdiction rules.
2. **Implementation-specific canonicalization:** some failures may belong to A or B alone rather than to the contract.
3. **Shared underspecification:** A and B may converge on the same wrong interpretation because the contract leaves a construction insufficiently constrained.
4. **Corpus-local artifact:** RC7B failure patterns may not reproduce on novel texts.
5. **Surface-language limitation:** even after explicit local rules, paraphrase/generalization may remain the dominant error source.
6. **Evaluator defect:** a microcohort or scorer may encode the intended answer incorrectly. Preserve such cases as apparatus failures rather than parser failures.

## Terminal lane states

Jurisdiction:
- `JURISDICTION_HARDENING_SUPPORTED`
- `JURISDICTION_HARDENING_FALSIFIED`
- `JURISDICTION_HARDENING_INCONCLUSIVE`

Field independence:
- `COUPLING_DEFECT_REPRODUCED`
- `COUPLING_DEFECT_NOT_REPRODUCED`
- `COUPLING_DEFECT_INCONCLUSIVE`

Only permission:
- `ONLY_PERMISSION_LOCAL_RULES_SUPPORTED`
- `ONLY_PERMISSION_LOCAL_RULES_FALSIFIED`
- `ONLY_PERMISSION_LOCAL_RULES_INCONCLUSIVE`

Overall:
- `LOCAL_HARDENING_SUPPORTED` only if jurisdiction and only-permission lanes pass their hard criteria and the field-independence lane yields a mechanically coherent result with no apparatus defect.
- `PARTIAL_LOCAL_HARDENING` if at least one lane passes but another is falsified or inconclusive.
- `LOCAL_HARDENING_FALSIFIED` if neither substantive intervention lane passes or a preserved unsafe failure defeats the proposed local hardening.
- `APPARATUS_INVALID` if scoring or corpus defects prevent scientific interpretation.

## Next-step rule

A later claim that the hardened Interpretation Authority contract is independently consumable **must** be tested in a new Context-Free execution with a newly sealed evaluator and fresh implementation(s). This RC7C run cannot itself establish independence because it intentionally uses revealed RC7B failure evidence.
