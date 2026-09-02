# RC8F Results: Source- and Whole-Atom-Anchored Authority Receipt

## Disposition

**SUPPORTED WITHIN THE FROZEN PROSPECTIVE ENVELOPE.**

RC8F adds only whole-atom identity binding on top of frozen RC8D source anchoring and frozen RC8B subordinate receipt consistency. The prospective result supports that narrow repair for the tested typed receipt representation.

It does not establish canonical or authentic atom IDs, source-content/span binding, natural-language semantic recovery, production readiness, Contract C projection, or independent recoverability.

## Frozen candidate

- preregistration commit: `87fe59b74f9f81a870ed90eed1608a9de12d2da5`
- candidate freeze declaration: `3097f9d5b8a45a3fa06ffeb84e725a8b329413c4`
- RC8F candidate blob: `efc50481be3179332cecb449c3c9c91da7c3dfaa`
- frozen RC8D blob: `f04f2dc529d3f1a7666d39a3bf9c8a9df87842d1`
- frozen RC8B blob: `edf84bb5aae0dd217e3f780e7a49767440b7c1e5`

## Exposed qualification

GitHub Actions run `33660212788`, job `100348634706`:

- production surface unchanged;
- predecessor candidates unchanged;
- exposed qualification succeeded.

Artifact:

- ID: `9858355736`
- digest: `sha256:e600dec6ca3c28df88c36aa345e684a89979610cfa72855d18d005e27212d913`

Exact exposed qualification:

- cases: **190**
- status exact: **190 / 190**
- typed reason exact: **190 / 190**
- unsafe warranted atoms: **0**

This is tuning/regression evidence only.

## Prospective apparatus qualification

The first pre-reveal run `33660585742`, job `100349865177`, stopped before candidate execution because the candidate-blind structural test asserted 20 cases while the already-frozen cohort contained 21. Candidate/predecessor/blob integrity checks had passed. No semantic fixture, evaluator, expected label, or candidate was changed.

Only the structural cardinality assertion was corrected from 20 to 21. The deviation is preserved in `RC8F_HELDOUT_FREEZE.json`.

Corrected pre-reveal run `33660759984`, job `100350433412`, then verified:

- production surface unchanged;
- RC8F/RC8D/RC8B blobs unchanged;
- prospective cohort and evaluator blobs unchanged;
- corrected structural test blob fixed;
- candidate-blind structural tests passed.

No RC8F held-out execution occurred in the corrected pre-reveal job.

## Prospective reveal

GitHub Actions run `33660865221`, job `100350778677`:

- all frozen identities reverified before execution;
- frozen RC8F executed on the fresh held-out;
- result artifact uploaded;
- all hard criteria passed.

Artifact:

- ID: `9858610711`
- name: `rc8f-prospective-heldout-33660865221`
- digest: `sha256:e2610637dec8ef2e95d84bd1850d7a3c03fb41b47dfc520b41c1289b920349d2`

## Exact prospective result

- cases: **21**
- status exact: **21 / 21**
- typed reason exact: **21 / 21**
- unsafe warranted atoms: **0**
- source/atom binding cases non-warranted when required: **7 / 7**
- warranted bank-invariance control: **pass**
- unresolved bank-invariance control: **pass**
- scientific state: `SOURCE_AND_ATOM_ANCHORED_GATE_SUPPORTED_WITHIN_PROSPECTIVE_ENVELOPE`

## Interpretation

### Observed

Within the frozen prospective envelope, RC8F blocked:

- absent or mismatched evidence-source anchors;
- absent target/authority atom identities;
- same-source atom mismatch;
- a complete internally consistent same-source whole-bundle transplant;
- atom mismatch combined with a later subordinate receipt mismatch.

It also preserved execution/evidence/source precedence, subordinate subject checks, source assertion unknown, extraction unresolved, field mismatch, support-span governance, composition, aperture, operator applicability, and reader/instrument-count non-authority.

### Inference

The RC8E failure was localized to missing whole-atom identity binding. Source anchoring plus whole-atom binding plus subordinate subject/span semantics is sufficient against the accumulated exposed history and this fresh typed synthetic envelope.

### Important remaining boundary

RC8F still accepts source identity, atom identity, and support spans as supplied typed facts. It does not establish that those identities or spans are actually bound to the admitted evidence content. A self-consistent receipt could still point to the right source ID and atom ID while its support span/content basis has been transplanted or fabricated within that source.

Before calling the receipt architecture sufficient for independent reproduction, inspect frozen Contract B 1.2.0 to determine what admitted-evidence identity/content anchors actually exist, then run the smallest content/segment-binding falsifier compatible with that frozen contract.

## Non-authorization

No production CAL semantics, `src/`, `schema/`, Contract B, Contract C, release, or promotion is authorized by this result.
