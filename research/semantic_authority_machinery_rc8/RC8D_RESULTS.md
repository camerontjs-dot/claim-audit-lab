# RC8D Results: Admitted-Evidence Anchored Authority Receipt

## Disposition

**SUPPORTED WITHIN THE FROZEN PROSPECTIVE ENVELOPE.**

RC8D adds one admitted-evidence source anchor to RC8B and otherwise delegates to the frozen RC8B authority transition. This result supports that narrow source-anchor repair for the tested receipt representation. It does not establish natural-language semantic recovery, receipt authenticity, whole-atom identity binding, production readiness, or Contract C projection.

## Frozen candidate

- RC8D candidate declaration commit: `eab2a34f8249d06613e6bd9ca396d2c16e421c02`
- RC8D candidate blob: `f04f2dc529d3f1a7666d39a3bf9c8a9df87842d1`
- frozen RC8B dependency blob: `edf84bb5aae0dd217e3f780e7a49767440b7c1e5`
- prospective apparatus freeze head: `4829ba73e9cc870a3093629a613860c95257259f`

## Pre-reveal qualification

GitHub Actions run `33659515300`, job `100346314941`, verified before candidate reveal:

- production `src/` and `schema/` unchanged from the parent research synthesis;
- RC8D candidate blob unchanged;
- frozen RC8B dependency blob unchanged;
- prospective cohort, evaluator, and structural-test blobs unchanged;
- candidate-blind structural tests passed.

The candidate was not executed on the prospective cohort in this job.

## Prospective reveal

GitHub Actions run `33659589125`, job `100346564947`:

- all frozen identities reverified before execution;
- prospective evaluator executed successfully;
- result artifact uploaded successfully;
- all hard criteria passed.

Artifact:

- ID: `9858115501`
- name: `rc8d-prospective-heldout-33659589125`
- digest: `sha256:b09536e5c1fdf526c94d9a6a34030051adb7be479171956d8e33f6ddab94fe55`

## Exact result

- cases: **15**
- status exact: **15 / 15**
- typed reason exact: **15 / 15**
- unsafe warranted atoms: **0**
- source-anchor cases non-warranted when required: **5 / 5**
- subordinate subject-binding cases non-warranted when required: **2 / 2**
- warranted bank-invariance control: **pass**
- unresolved bank-invariance control: **pass**
- scientific state: `ADMITTED_EVIDENCE_ANCHORED_GATE_SUPPORTED_WITHIN_PROSPECTIVE_ENVELOPE`

## Interpretation

### Observed

Within this frozen synthetic envelope, an authority bundle could not acquire warrant when its admitted-evidence source anchor was absent or mismatched. RC8D also preserved execution/evidence precedence, RC8B subordinate subject binding, unresolved semantic states, field mismatch rejection, and reader/instrument-count non-authority.

### Inference

The RC8C failure was localized to missing evidence-source anchoring rather than a need to redesign the RC8B transition. The one-field source-anchor repair is sufficient against all previously exposed cases and this fresh RC8D cohort.

### Not established

This result does **not** establish that `authority_subject_id` is bound to the correct proposed atom within the same admitted source. A complete receipt bundle may still be internally consistent and source-consistent while being attached to the wrong atom or consumer slot. That is the next discriminating boundary.

It also does not authenticate receipt producers, bind spans to source bytes/content digests, prove semantic extraction from natural language, authorize production CAL, alter Contract B/C, or justify a release.

## Next falsifier

Preregister a same-source whole-atom transplantation test before authoring its cohort. Hold admitted source and semantic values constant while changing only the target atom identity versus the authority bundle's atom identity. If the frozen RC8D candidate warrants a mismatched bundle, preserve RC8D unchanged and add the smallest explicit atom-identity anchor in a successor.
