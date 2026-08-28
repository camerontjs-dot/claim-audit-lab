# Contract C RC1 Field-Family Ablation Results

## Method

Start from the same frozen synthetic semantic-state package. Delete one candidate C1 family at a time. Run four named consumer/reconstruction probes against the mutated package and record actual exceptions or inability to answer.

The probes are deliberately different policies:

- `publication`: needs execution, aperture, residual counterevidence, and CAL result;
- `sop_conformance`: needs eligibility, semantic validity, temporal applicability, and CAL result;
- `investigation`: needs residual evidence and reassessment lineage;
- `reconstruction`: needs input/config identity and normalized semantic measurements.

These probes are research consumers. They do not become CAL or Decision Engine production policy.

## Observed failures

| Deleted family | Publication | SOP conformance | Investigation | Reconstruction |
| --- | --- | --- | --- | --- |
| `identity` | fail | fail | fail | fail |
| `evidence` | fail | fail | fail | fail |
| `measurements` | pass | pass | pass | fail |
| `assessments` | fail | fail | fail | fail |
| `conclusion` | fail | fail | fail | fail |
| `reassessment` | pass | pass | fail | pass |
| `execution` | fail | fail | fail | fail |

The executable test asserts this exact matrix.

## Inference

At the current family granularity, all seven families have at least one demonstrated consumer or reconstruction use. This does **not** establish that every field inside each family is necessary. In particular:

- measurement scores may be reducible to normalized outcomes plus receipts;
- assessment envelopes may be encoded more compactly;
- evidence references may be deduplicated at run scope;
- identity fields may be factored into run-level and proposition-level portions;
- reassessment is necessary for the investigation probe but may be optional for original results if profile semantics make absence unambiguous.

Field-family ablation therefore supports semantic family diversity while leaving field-level minimality open.

## Same-verdict controls

All controls hold `reported_verdict: supported` while mutating one residual state. Observed consumer behavior changes include:

- counterevidence present: publication changes from `publish_review` to `review`;
- eligibility unknown: SOP becomes `indeterminate`;
- eligibility ineligible: SOP becomes `indeterminate_applicability`;
- semantic validity unknown: SOP becomes `indeterminate`;
- semantic validity invalid: SOP becomes `indeterminate_invalid_evidence`;
- aperture unknown/incomplete: publication becomes `review`;
- temporal applicability historical-only: SOP becomes `indeterminate_applicability`;
- unresolved residual evidence: investigation becomes `further_investigation`;
- different exact basis: headline verdict remains the same while the attributable decision basis differs.

These controls falsify verdict-only C2 as a sufficient universal result representation for the preregistered consumer diversity.
