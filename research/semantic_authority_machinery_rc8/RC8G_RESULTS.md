# RC8G Results: Contract-B Evidence Segment Binding Falsifier

## Disposition

**FALSIFIED.** Frozen RC8F is not a sufficient Contract-B-bound typed authority receipt because it does not bind the authority assessment to the validated canonical bundle/passage coordinate or constrain semantic support spans to the admitted passage extent.

## Frozen authority and apparatus

Contract B authority:

- repository: `camerontjs-dot/apparatus-contracts`
- commit: `c314e53bd91c0736aa4370a364673b069aceb43e`
- handoff spec blob: `3e49901dff567ff5bbad55a2d6ccdc3ed36a7a26`
- factual-context extension blob: `77645a6adac664892866f3fdf8abf66cd1d0dd10`

Frozen parent:

- RC8F blob: `efc50481be3179332cecb449c3c9c91da7c3dfaa`
- RC8D blob: `f04f2dc529d3f1a7666d39a3bf9c8a9df87842d1`
- RC8B blob: `edf84bb5aae0dd217e3f780e7a49767440b7c1e5`

RC8G apparatus freeze:

- preregistration: `aafa3fe6daff055c8f53d1ea183f493b33112818`
- apparatus freeze head: `faeca1130146129df7a9a31804dfa094850b06d7`
- cohort blob: `b90cc718e2359249b9c54d7e4dad3a8e8bd07889`
- evaluator blob: `6b5b19a6e2c0295bcaa421e8f6e6d3eadb392dda`
- structural-test blob: `741d7c09ca5ff282b34674fa77edc14aac8d5939`

## Pre-reveal qualification

GitHub Actions run `33661436137`, job `100352658124`, completed successfully before candidate reveal. It verified:

- production `src/` and `schema/` unchanged;
- exact frozen Contract B checkout and governing spec blobs;
- frozen RC8F/RC8D/RC8B candidate identities;
- frozen RC8G apparatus identities;
- candidate-blind RC8G structural tests.

No RC8G candidate execution occurred in this job.

## Reveal

GitHub Actions run `33661676676`, job `100353445570`:

- production surface verification: success;
- exact Contract B authority reverification: success;
- frozen parent/apparatus reverification: success;
- RC8G evaluator execution: success;
- result artifact upload: success;
- hard safety criterion: **failure**.

Artifact:

- ID: `9858915634`
- name: `rc8g-contract-b-segment-33661676676`
- digest: `sha256:71f75e4ccf526448aec5ea933495fb64e44a32460d8b23fe51a33c0335917a6b`

## Exact result

- cases: **17**
- status exact: **9 / 17**
- typed reason exact: **8 / 17**
- unsafe warranted atoms: **8**
- segment-binding cases non-warranted when required: **1 / 9**
- warranted bank invariance: **pass**
- unresolved bank invariance: **pass**
- scientific state: `RC8F_CONTRACT_B_SEGMENT_BINDING_FALSIFIED_OR_REGRESSED`

Unsafe cases:

1. missing raw bundle identity -> observed `WARRANTED`;
2. missing authority-receipt bundle identity -> observed `WARRANTED`;
3. explicit bundle mismatch -> observed `WARRANTED`;
4. missing raw passage identity -> observed `WARRANTED`;
5. missing authority-receipt passage identity -> observed `WARRANTED`;
6. explicit same-bundle/source passage mismatch -> observed `WARRANTED`;
7. proposal span outside admitted passage but still inside operator governance -> observed `WARRANTED`;
8. required field-support span outside admitted passage but still inside operator governance -> observed `WARRANTED`.

The combined source-mismatch + passage-mismatch case remained correctly rejected for source mismatch. The combined passage-mismatch + atom-mismatch case was rejected, but for atom mismatch rather than passage mismatch, showing that evidence-segment precedence is absent from RC8F.

## Localization

### Observed

RC8F correctly preserves:

- execution failure precedence;
- evidence rejection precedence;
- source identity precedence;
- atom identity rejection;
- semantic unresolved behavior;
- reader/instrument-count non-authority.

### Inference

The remaining typed-receipt defect is a missing bridge between validated Contract B chain-of-custody coordinates and the internal semantic authority receipt. RC8F knows source identity and atom identity, but not which validated bundle/passage segment the interpretation is allowed to draw authority from.

Because the proposal-span and field-span falsifiers remained inside operator governance, the result specifically distinguishes operator jurisdiction from admitted-evidence passage containment.

## Successor constraint

Preserve RC8F unchanged. The smallest successor should insert a Contract-B evidence-segment gate **after existing source anchoring and before atom identity**:

- missing bundle or passage coordinate -> `UNRESOLVED / AUTHORITY_EVIDENCE_SEGMENT_BINDING_UNRESOLVED`;
- bundle mismatch -> `REJECTED / AUTHORITY_EVIDENCE_BUNDLE_MISMATCH`;
- passage mismatch -> `REJECTED / AUTHORITY_EVIDENCE_PASSAGE_MISMATCH`;
- missing/malformed admitted passage extent -> `UNRESOLVED / ADMITTED_PASSAGE_SPAN_UNRESOLVED`;
- proposal span outside admitted passage -> `REJECTED / SOURCE_SPAN_OUTSIDE_ADMITTED_PASSAGE`;
- required field-support span outside admitted passage -> `REJECTED / FIELD_SUPPORT_OUTSIDE_ADMITTED_PASSAGE:<field>`;
- otherwise continue through frozen RC8F.

Do not introduce another passage hash or content digest as semantic authority. Contract B already owns canonical artifact integrity, passage hashes, source content hashes, bundle sealing, and `SHA256SUMS`. The internal gate should bind to validated canonical coordinates rather than duplicate upstream integrity authority.

## Non-claims

RC8G does not test whether semantic values are correctly recovered from passage language, whether atom IDs are canonically generated, or whether Contract B integrity validation itself is correct. It does not authorize production CAL, Contract B/C changes, release, or promotion.
