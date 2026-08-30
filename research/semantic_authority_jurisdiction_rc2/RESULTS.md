# Semantic Authority / Jurisdiction RC2 — Results

## Classification

Research Infrastructure / epistemic-authority architecture experiment.

## OBSERVED

Accepted science head: `4000f37b1f861cca696cb9852722fee8f4f50f0b`.

Accepted push run: `33321461944`. Accepted PR run: `33321464202`. Public suite at the same science head passed.

Artifact: `9735000430`, digest `sha256:b443a1c36ad75a6356c16ba9eb727e3aed9ce36b73bde4008d9a8c88968bdbb6`.

All 12 preregistered authority-domain falsifiers passed.

No production code, Contract C, threshold, or NLI model changed. No new model execution occurred.

### Numeric authority

- CG-12a: a five-business-day maximum claim against an in-scope one-business-day maximum produced a current/applicable `numeric_relation` receipt with status `invalid`.
- CG-24 wrong-scope five-day passage: produced `inapplicable` with reason `scope_mismatch`.
- CG-24 in-scope one-day passage: produced an applicable `invalid` numeric receipt.
- property substitution and unit substitution failed closed as inapplicable.
- CG-05: temperature and duration threshold conditions could each be established, but neither numeric receipt could exercise `composition` authority over the Quality Hold conclusion.

### Source-boundary authority

Retention-sample family:

- CG-08a exhaustive aperture: absence receipt `valid`;
- CG-08b bounded aperture: `unknown`;
- CG-21 exact named missing material: absence claim `invalid`.

Post-release family:

- CG-09a exhaustive: `valid`;
- CG-09b bounded: `unknown`;
- CG-22 unrelated named gap: `unknown`.

A source-boundary receipt could not be substituted for numeric authority.

### CAL-native stage authority

CAL natively emitted an `assessment.issue` descriptor bound to exact Contract B bundle/claim identity and bundle hash in domain `assessment_mandate`.

That assessment mandate did not confer numeric/support semantic authority.

## INFERENCE

The evidence supports a typed semantic-jurisdiction pattern:

`measurement -> applicability -> authority domain -> validity -> aggregation/decision`

Numeric decision authority becomes defensible only after property, scope, unit and relation geometry are bound. Source completeness/absence is a separate authority domain. Composition is another separate domain.

The numeric problem is therefore not adequately described as merely an NLI weakness. A material part of it is missing typed semantic jurisdiction.

## HYPOTHESIS STATUS

- H1 domain firewall: SUPPORTED.
- H2 typed numeric jurisdiction: SUPPORTED on the bounded tested relations.
- H3 numeric/composition separation: SUPPORTED.
- H4 scope mismatch fails closed: SUPPORTED.
- H5 source-boundary authority: SUPPORTED on the frozen construction families.
- H6 common cross-cutting authority shape: requires the independent cross-repository consumer in Apparatus Contracts PR #25; CAL alone cannot establish it.

## UNKNOWN

This experiment does not establish reliable natural-language extraction of property/scope/unit/relation tuples. The tested quantities are typed research objects derived from frozen construction semantics.

It also does not establish a general arithmetic theorem prover, unit conversion system, temporal reasoner, quantifier system, or composition engine.

## DISPOSITION

Typed semantic authority is SUPPORTED as a research architecture candidate.

Production promotion is NOT SUPPORTED.

The next numeric experiment must test text-to-typed-relation extraction independently from semantic validation, rather than conflating the two.
