# RC8G Preregistration: Contract-B Evidence Segment Binding Falsifier

## Decision question

Can the frozen RC8F source-and-atom anchored gate prevent authority when an otherwise-valid semantic receipt is attached to the wrong canonical Contract B bundle/passage coordinate or uses support spans outside the admitted passage extent?

This tests chain-of-custody binding to the already-frozen Contract B evidence representation. It does not modify Contract B and does not duplicate Contract B integrity machinery.

## Frozen parent candidate

- parent: RC8F
- candidate freeze declaration: `3097f9d5b8a45a3fa06ffeb84e725a8b329413c4`
- candidate blob: `efc50481be3179332cecb449c3c9c91da7c3dfaa`
- frozen RC8D blob: `f04f2dc529d3f1a7666d39a3bf9c8a9df87842d1`
- frozen RC8B blob: `edf84bb5aae0dd217e3f780e7a49767440b7c1e5`

The frozen candidate must not change after this preregistration. Disagreements are evidence.

## Contract B authority used for this test

Frozen Contract B 1.2.0 authority: `c314e53bd91c0736aa4370a364673b069aceb43e` in `camerontjs-dot/apparatus-contracts`.

Observed frozen contract facts:

1. canonical C-B passage records carry `bundle_id`, `source_id`, `passage_id`, passage text, `char_start`, `char_end`, `passage_hash`, and provenance including `source_content_hash`;
2. C-B artifacts are integrity sealed through `bundle_hash` / `SHA256SUMS` and passage/source hash checks;
3. the 1.2 extension references existing canonical passage identities and representation anchors rather than duplicating passage text or hashes;
4. CAL's semantic-measurement context is defined to retain admitted passage identities, referenced source identities, provenance-bound factual context, and representation anchors.

Therefore this experiment treats canonical Contract B integrity validation as upstream evidence authority and tests only whether the internal semantic-authority receipt is bound to the correct validated evidence coordinate. It does **not** introduce a second competing passage-hash authority.

## Minimal synthetic coordinate layer

For the falsifier only, add typed observations ignored by frozen RC8F:

- `raw_bundle_id`: validated Contract B bundle identity currently consumed;
- `authority_subject_bundle_id`: bundle identity to which the semantic authority receipt claims to belong;
- `raw_passage_id`: admitted canonical Contract B passage identity currently consumed;
- `authority_subject_passage_id`: passage identity to which the semantic authority receipt claims to belong;
- `admitted_passage_span`: canonical source-coordinate extent `[char_start, char_end]` of that validated admitted passage.

Existing `raw_source_id` / `authority_subject_source_id` remain the source coordinate. Existing target/authority atom identity remains the proposition/consumer coordinate.

## Positive control

Use one validated synthetic Contract B coordinate with:

- matching bundle identity;
- matching source identity;
- matching passage identity;
- matching target/authority atom identity;
- proposal span and every required field-support span contained within `admitted_passage_span`;
- all subordinate RC8B receipts valid.

Expected result: `WARRANTED`.

## Target mutations

Freeze at minimum:

1. missing raw bundle identity;
2. missing authority-receipt bundle identity;
3. explicit bundle mismatch with source/passage otherwise equal;
4. missing raw passage identity;
5. missing authority-receipt passage identity;
6. explicit passage mismatch within the same bundle/source;
7. proposal span outside admitted passage extent but still inside operator governance;
8. one required field-support span outside admitted passage extent but still inside operator governance;
9. source mismatch plus passage mismatch, preserving existing source-anchor precedence;
10. passage mismatch plus atom mismatch, testing evidence-coordinate precedence before atom identity;
11. fully bound positive control;
12. reader/instrument bank-growth controls on warranted and unresolved semantics.

Semantic values must be held constant in identity-substitution cases.

## Expected successor precedence if falsified

The smallest compatible successor should preserve:

1. execution failure;
2. evidence admission rejection;
3. existing source identity binding;
4. Contract B bundle/passage identity binding;
5. admitted-passage span containment;
6. existing whole-atom identity binding;
7. frozen subordinate assertion/operator/field/composition/aperture checks.

Missing bundle/passage coordinate -> `UNRESOLVED`.
Explicit bundle/passage mismatch -> `REJECTED`.
Proposal or required-field support outside the admitted passage extent -> `REJECTED`.

## Hard criterion

`unsafe_warranted_atoms == 0`

Any mismatched/missing evidence-coordinate or out-of-passage support case observed as `WARRANTED` falsifies RC8F as a sufficient Contract-B-bound typed authority receipt.

## Non-claims

This does not test whether semantic field values are correctly recovered from passage language. It does not authenticate atom-ID generation, prove semantic interpretation, alter Contract B/C, authorize production, or establish independent recoverability.
