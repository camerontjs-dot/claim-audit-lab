---
title: "Idea correspondence: local v2 vs later GitHub explicit machinery"
privacy: "public-research-record"
---

# IDEA_CORRESPONDENCE

Compare **ideas**, not filenames. Labels: SAME IDEA / EARLIER VERSION / SUPERSEDED / CONFLICTS WITH LATER EVIDENCE / STILL UNIQUE / UNCLEAR.

GitHub later evidence is `main` plus Draft PRs #35–#41. Local v2 is `feat/v2-epistemic-pipeline` plus dirty overlay.

| Local idea | GitHub later | Correspondence | Notes |
|---|---|---|---|
| Independent support and refutation as passage roles that can coexist | `evidence_state` mixed/support_only/refutation_only; decision-model dual channels | **EARLIER VERSION** | Local `_r_conflicting` keeps both arms and returns `not_checkable`/`not_resolvable`. Later machinery keeps mixed **valid** state instead of compressing to a v1-style terminal. |
| Raw vs eligible vs semantically valid | explicit eligibility + validity + unknown | **EARLIER VERSION / SUPERSEDED** | Local stages 1-admit / 2-qualify / 3-score approximate this, but qualify mixes eligibility with A4-like negation and interval operators. Later work split those stages on purpose. |
| Unknown / unmeasured | `ValidityStatus=unknown`, `unmeasured_state` taxonomy | **EARLIER VERSION** | Local skips Q3 when no negated reading (`skipped: True`) rather than recording inapplicability. |
| Execution failure vs epistemic abstention | typed failure envelope in #36/#37 | **UNCLEAR locally** | Overlay runner raises `V2PipelineError` / `V2ReplayError`. Not shown to be a normal output state. |
| Aperture / completeness / source-boundary | #39: CG-08a/08b/21 flattened; later NEXT asks for a source-boundary experiment | **STILL UNIQUE in part** | Local forbids inferring a coverage complement; requires `declared_mode='coverage'` and `source_boundary='exhaustive'`. Exhaustive silence is treated as a finding, not stage-1 failure. That discipline matches later “do not reconstruct missing state,” but is not the GitHub projection. |
| Contribution / basis provenance | contribution ledger + basis IDs | **EARLIER VERSION** | Local `Removal` log and `deciding_passages` are a removal/citation trail, not a dual-channel ledger. |
| Reconstructing epistemic state from terminal verdict | forbidden by later RCs | **SAME IDEA (good)** | Overlay docstring: coverage complement is never invented from generic contradiction. |
| Measurement vs operators vs policy | later first-divergence stages | **CONFLICTS WITH LATER EVIDENCE** | Local Q3 (negation consistency) and Q4 (interval) live in qualify/eligibility. #39 showed A4-as-generic-validity is overreach. Putting operators in eligibility repeats that compression. |
| Multiple contributing causes without a unique winner | Contract C multiplicity; decision-model mixed abstention | **EARLIER VERSION** | Local conflicting rule refuses to pick a winner (good vs v1 max-signal) but emits `not_checkable`, which later work showed is too coarse. |
| Operator inapplicability vs negative operator result | #37 e2e-08; #41 A4 invalid→unknown | **CONFLICTS / EARLIER** | Local Q3 skip is closer to inapplicable, but not first-class. Q4 `incomparable`/`inconclusive` is closer to a typed numeric unknown. |
| Typed numeric / quantity / bound machinery | #38/#39 nominate a numeric study; GitHub still has no interval algebra | **STILL UNIQUE** | `interval_algebra.py` is absent from `main`. It is the local answer to the D1/D12 / e2e-08-class gap. It is **not** validated against Cohort A and must not land as production. |
| Collapse of `not_checkable` | #36: 6 internal divergences vs 2 terminal disagreements; #39 27 explicit abstains vs 18 legacy not_checkable | **CONFLICTS WITH LATER EVIDENCE** | Overlay `V2VerdictRecord.degree` is still `supported` / `contradicted` / `not_checkable`. |
| Contract C unknowns | `v0.5.0` exporter on `main`; local C-B crosswalk marks `partially_supported` unavailable and `writeback_permitted=False` | **EARLIER VERSION** | Loss-aware crosswalk is honest; it is not Contract C 1.0.0. |
| Pair-union premises | not on `main` | **STILL UNIQUE** | Overlay generates bounded pair unions as extra NLI premises. Research apparatus, not a measured operator family. |
| Deep Research packet adapter | `explicit_claims.py` exists on `main`; adapter does not | **STILL UNIQUE as glue** | Thin consumer of existing explicit-claim protocol. Not a new epistemic engine. |

## What later research learned that v2 did not have

Cohort A (#39): A4 invalidation generalized beyond e2e-08; seven legacy contradictions became explicit abstentions; CG-23b strengthened mixed→support_only after A4 dropped the refutation arm. #41 preregisters reversing unjustified A4-negative authority and blocking unresolved→decided strengthening.

Local `_r_conflicting` would likely **not** perform that CG-23b strengthening (it abstains on mixed eligible support+refute). That is a **positive local contrast**, not proof that v2 is the better substrate: it still lacks raw/eligible/valid separation and still uses `not_checkable`.

## Evaluation stance

Do not score local v2 as “better than released CAL” from this correspondence. Released CAL is the experimental baseline. Later explicit shadow is the current research instrument. Local v2 is a diverged 2026-08-22 experiment with some unique operators and some now-falsified compressions.
