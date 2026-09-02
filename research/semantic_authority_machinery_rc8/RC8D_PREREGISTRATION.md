# RC8D — Admitted-Evidence Anchored Authority Receipt Preregistration

## Parent evidence

RC8C falsified frozen RC8B on the smallest evidence-source perturbation: changing or removing only `raw_source_id` left an otherwise valid bound authority bundle incorrectly warranted.

RC8B remains frozen and supported only for internal receipt-fragment subject consistency. RC8C is exposed qualification evidence for RC8D.

## Decision question

Does one explicit source-anchor invariant, applied before RC8B's existing bound-receipt transition, prevent whole-bundle attachment to the wrong admitted evidence source without regressing RC8B's supported behavior?

## Smallest permitted change

RC8D may add one field:

`authority_subject_source_id`

After execution and evidence-admission precedence:

1. if `raw_source_id` is missing: `UNRESOLVED / AUTHORITY_EVIDENCE_SOURCE_BINDING_UNRESOLVED`;
2. if `authority_subject_source_id` is missing: `UNRESOLVED / AUTHORITY_EVIDENCE_SOURCE_BINDING_UNRESOLVED`;
3. if `authority_subject_source_id != raw_source_id`: `REJECTED / AUTHORITY_EVIDENCE_SOURCE_MISMATCH`;
4. otherwise delegate unchanged to the frozen RC8B bound-receipt transition.

No parsing or inferred semantics may be extracted from `authority_subject_id` itself.

No confidence, reader count, voting, or instrument count may affect this source binding.

## Qualification evidence

Before candidate freeze, RC8D may be tuned only against exposed evidence:

- the 112 exposed RC8B qualification cases, augmented with a valid source anchor;
- the exposed 50-case RC8B prospective cohort, now regression evidence, augmented with a valid source anchor;
- the exposed 3-case RC8C falsifier with a fixed source-A subject anchor.

Qualification must preserve all prior expected status/reason outcomes and repair both exposed RC8C unsafe warrants.

## Candidate freeze

Freeze exact RC8D bytes after exposed qualification passes. No fresh RC8D prospective cohort may exist before that freeze.

## Fresh prospective requirements

After freeze, author unseen tests spanning:

- valid source anchor positive;
- missing `raw_source_id`;
- missing `authority_subject_source_id`;
- explicit source mismatch in both directions;
- partial receipt subject mismatch while source anchor is valid;
- full authority-subject bundle substitution while admitted source anchor remains A;
- execution failure and evidence-not-admitted precedence over source-binding checks;
- semantic unresolved/rejected states under valid source anchoring;
- reader/instrument bank growth invariance.

## Hard falsifiers

RC8D is falsified if:

1. any explicit evidence-source mismatch is warranted or unresolved rather than rejected;
2. any missing required evidence-source binding is warranted;
3. any previously supported RC8B rejection/unresolved state becomes warranted merely because a source anchor is present;
4. reader/instrument count changes authority;
5. fully anchored positive controls cease to warrant;
6. `unsafe_warranted_atoms > 0`.

## Threat-model boundary

RC8D tests structural consistency between admitted evidence identity and the authority bundle's declared evidence-source anchor. It does not establish cryptographic authenticity or defend against an actor that can rewrite both source identities and all subordinate provenance consistently.

## Non-authorization

Passing RC8D would remain research evidence only. It would not authorize production CAL changes, Contract B/C changes, release, or independent-reproduction claims.
