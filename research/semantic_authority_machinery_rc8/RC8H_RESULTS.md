# RC8H Results: Contract-B Segment-Bound Source/Atom Authority

## Disposition

**SUPPORTED_WITH_BOUNDS** within the frozen prospective envelope.

RC8H is not a production authorization. It is evidence that the tested typed authority transition can bind a semantic authority receipt to an already-validated Contract B source/bundle/passage segment and whole-atom identity without making reader count, instrument count, or scalar confidence authoritative.

## Frozen candidate

- candidate: `authority_contract_rc8h.py`
- candidate blob: `4b872e455d52d7a682bb719889860d2cac7909a7`
- candidate freeze declaration: `1d1fec29ad5e08e28d3b9751534b85121221b17c`
- frozen parent RC8F blob: `efc50481be3179332cecb449c3c9c91da7c3dfaa`
- frozen parent RC8D blob: `f04f2dc529d3f1a7666d39a3bf9c8a9df87842d1`
- frozen parent RC8B blob: `edf84bb5aae0dd217e3f780e7a49767440b7c1e5`

Frozen Contract B authority:

- apparatus-contracts commit: `c314e53bd91c0736aa4370a364673b069aceb43e`
- handoff spec blob: `3e49901dff567ff5bbad55a2d6ccdc3ed36a7a26`
- factual-context extension blob: `77645a6adac664892866f3fdf8abf66cd1d0dd10`

## Exposed qualification

Run `33661990038`, job `100354478015`:

- 228 cases
- 228/228 exact authority status
- 228/228 exact typed reason
- 0 unsafe warranted atoms
- artifact `9859037742`
- digest `sha256:7eb6e4ab7e64e12bdf53c5a19d37a58ee42b8219a0c5c63e9562c80760492a78`

The exposed suite included the complete prior RC8 authority history plus RC8G's eight observed Contract-B chain-of-custody failures.

## Prospective apparatus

The fresh cohort was created only after the RC8H candidate freeze.

Frozen blobs:

- `rc8h_heldout_cohort.py`: `29711c381dbf5170b0157c0cd00aa121182af58e`
- `rc8h_heldout_evaluate.py`: `c7441b080f5e395eacbd8ecfbb1d79969f045843`
- `test_rc8h_heldout_apparatus.py`: `1dca40b48120ec422e858dda274b52a8ccb69105`

Accepted pre-reveal push run `33669658081`, job `100379823463`, verified:

- production `src/` and `schema/` unchanged from the research parent;
- exact frozen Contract B commit and specification blobs;
- exact RC8H/RC8F/RC8D/RC8B candidate blobs;
- exact prospective cohort/evaluator/test blobs;
- candidate-blind structural checks.

No held-out candidate execution occurred in the accepted pre-reveal run.

## Prospective result

Reveal run `33669801805`, job `100380304314`:

- 26 cases
- 26/26 exact authority status
- 26/26 exact typed reason
- 0 unsafe warranted atoms
- 13/13 targeted non-warranted binding/boundary cases remained non-warranted
- bank invariance: true for warranted and unresolved controls
- artifact `9862018646`
- digest `sha256:26dc1521b651e773b5be8684f4e22538cf63db98edc077ef231ba4a76077c43f`

Expected and observed terminal-state distribution matched exactly:

- `WARRANTED`: 5
- `REJECTED`: 10
- `UNRESOLVED`: 10
- `NO_ASSESSMENT`: 1

## What this supports

Within the tested envelope, a receipt may reach `WARRANTED` only after the tested chain remains coherent:

1. execution completed;
2. evidence admitted;
3. authority source identity matches the admitted source;
4. authority bundle identity matches the validated Contract B bundle;
5. authority passage identity matches the admitted Contract B passage;
6. admitted passage extent is present and typed;
7. proposal and required-field support stay inside that admitted passage extent;
8. whole-atom target identity matches the authority atom identity;
9. subordinate proposal/assertion/operator/required-field/composition/aperture receipts remain bound to the same authority subject;
10. operator jurisdiction/applicability and field/value/status/composition/aperture semantics pass the frozen parent gates.

Exact passage-boundary equality is permitted. Passage crossings are rejected even when the same span remains inside the broader operator-governance span.

## What this does not support

RC8H does not establish:

- Contract B claim-identity binding;
- canonical or collision-resistant atom-ID generation;
- that opaque IDs were generated honestly;
- proposition semantic correctness;
- source-text interpretation correctness;
- cryptographic authenticity beyond Contract B's existing integrity regime;
- Contract C projection sufficiency;
- production readiness or promotion;
- independent recoverability by a fresh implementation.

The next smallest discriminating test is therefore claim identity: can an otherwise valid source/bundle/passage/atom authority receipt be transplanted between two distinct Contract B claims when the semantic surface happens to be identical?
