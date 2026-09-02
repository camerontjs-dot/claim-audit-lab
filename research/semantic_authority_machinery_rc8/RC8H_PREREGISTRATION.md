# RC8H Preregistration: Contract-B Segment-Bound Source/Atom Authority Receipt

## Hypothesis

The RC8G chain-of-custody failure can be repaired without changing Contract B integrity semantics or the frozen RC8F semantic gate by inserting one validated Contract-B evidence-segment layer after source binding and before whole-atom binding.

## Frozen authorities

Contract B:

- repository: `camerontjs-dot/apparatus-contracts`
- commit: `c314e53bd91c0736aa4370a364673b069aceb43e`
- handoff spec blob: `3e49901dff567ff5bbad55a2d6ccdc3ed36a7a26`
- factual-context extension blob: `77645a6adac664892866f3fdf8abf66cd1d0dd10`

Frozen parent stack:

- RC8F blob: `efc50481be3179332cecb449c3c9c91da7c3dfaa`
- RC8D blob: `f04f2dc529d3f1a7666d39a3bf9c8a9df87842d1`
- RC8B blob: `edf84bb5aae0dd217e3f780e7a49767440b7c1e5`

RC8G falsification:

- preregistration: `aafa3fe6daff055c8f53d1ea183f493b33112818`
- reveal run: `33661676676`
- artifact: `9858915634`
- unsafe warranted atoms: `8`

## Minimal successor layer

RC8H consumes an already validated Contract B semantic-measurement context. It does not revalidate bundle hashes, passage hashes, source content hashes, or `SHA256SUMS`.

It adds only consistency checks for these typed coordinates:

- `raw_bundle_id` versus `authority_subject_bundle_id`;
- `raw_passage_id` versus `authority_subject_passage_id`;
- `admitted_passage_span`, the validated canonical passage `[char_start, char_end]` extent.

Existing source and atom bindings remain owned by frozen RC8F.

## Precedence

RC8H must preserve the smallest observed chain:

1. execution failure: preserve frozen RC8F result;
2. evidence not admitted: preserve frozen RC8F result;
3. source identity missing/mismatch: preserve frozen RC8F result;
4. bundle/passage segment binding:
   - any missing raw/authority bundle or passage ID -> `UNRESOLVED / AUTHORITY_EVIDENCE_SEGMENT_BINDING_UNRESOLVED`;
   - bundle mismatch -> `REJECTED / AUTHORITY_EVIDENCE_BUNDLE_MISMATCH`;
   - passage mismatch -> `REJECTED / AUTHORITY_EVIDENCE_PASSAGE_MISMATCH`;
5. admitted passage extent:
   - missing or malformed extent -> `UNRESOLVED / ADMITTED_PASSAGE_SPAN_UNRESOLVED`;
   - proposal span outside extent -> `REJECTED / SOURCE_SPAN_OUTSIDE_ADMITTED_PASSAGE`;
   - any required field warrant with a valid typed support span outside extent -> `REJECTED / FIELD_SUPPORT_OUTSIDE_ADMITTED_PASSAGE:<field>`;
6. whole-atom identity and all subordinate semantic authority checks: delegate unchanged to frozen RC8F.

If a required field receipt is missing or its support span is itself malformed, RC8H does not invent a segment judgment; frozen RC8F/RC8B remains responsible for the existing missing/unresolved field semantics.

## Why no duplicate content digest

Frozen Contract B already owns artifact and passage integrity through bundle sealing, `SHA256SUMS`, passage hashes, source content hashes, and validation. The semantic authority layer should bind to validated canonical coordinates rather than create a competing hash authority.

This is a preconditioned gate: `raw_bundle_id`, `raw_source_id`, `raw_passage_id`, and `admitted_passage_span` are observations from a successfully validated Contract B intake/semantic-measurement context.

## Exposed qualification

Before freezing RC8H, replay all exposed authority cases:

- RC8F exposed qualification history;
- RC8F prospective held-out, now exposed;
- RC8G falsifier.

For non-RC8G historical cases, inject a neutral matching bundle/passage coordinate and a broad admitted passage extent that does not alter the pre-existing expected semantic decision. RC8G retains its original segment mutations and expected labels.

Hard exposed qualification requirements:

- exact status on every case;
- exact typed reason on every case;
- `unsafe_warranted_atoms == 0`.

## Prospective requirement

If exposed qualification passes, freeze RC8H before authoring a new prospective cohort. The fresh cohort must independently exercise:

- bundle/passage missing and mismatch;
- exact admitted-span boundary controls;
- proposal and required-field support crossing the passage boundary while staying within operator governance;
- source > segment > atom precedence;
- semantic unresolved/rejected controls;
- required composition/aperture controls;
- reader/instrument-bank invariance.

## Hard falsifier

One unsafe warranted atom in the fresh RC8H held-out falsifies the successor within that envelope.

## Non-claims

RC8H does not establish proposition semantic correctness, canonical atom-ID generation, Contract B claim-identity binding, source-text interpretation, production readiness, Contract C projection, or independent recoverability.
