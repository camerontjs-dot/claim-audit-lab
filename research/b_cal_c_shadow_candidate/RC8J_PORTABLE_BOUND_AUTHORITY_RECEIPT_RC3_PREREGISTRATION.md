# RC8J Portable Bound Authority Receipt RC3 — Preregistration

## Classification

Draft Research Infrastructure only. No production authorization, Contract C projection, Decision Engine policy change, release, merge, or promotion is authorized by this experiment.

## Frozen lineage

- production main reference: `32275a239b68af383a56bca843e28cbc1e343976`
- frozen RC2 parent / PR #82 head: `0c324a6a866f1bc0ce678c78d6502c6b314386c2`
- frozen RC8J commit: `8e75c6782bb95c3763d06230b9c5df2b6af44054`
- frozen RC8J implementation blob: `f55156e43e0c1b4a7868bc8339585b8892edda38`

RC2 and RC8J must remain byte-unchanged.

## Research question

Can a `WARRANTED` RC8J authority result be transported from a producer to an independent consumer as an authenticated, payload-bound receipt, such that the consumer can derive the existing bounded categorical relation without rerunning RC8J and without accepting stale, substituted, tampered, forged, or partially specified authority?

## Trust model under test

This experiment distinguishes **binding** from **authenticity**.

A payload digest by itself is not sufficient authority because an untrusted caller that can construct the receipt can recompute the digest after mutating the payload. Therefore the candidate receipt must authenticate the attestation as well as bind it to the exact authority-relevant case projection.

The bounded candidate uses HMAC-SHA-256 from the Python standard library. The producer and consumer are assumed to share an out-of-band secret verification key identified by `key_id`. The key is not embedded in the receipt. Production key distribution, rotation, storage, revocation, multi-issuer trust, asymmetric signatures, and hardware-backed signing are explicitly out of scope.

This shared-secret assumption is a material boundary. A passing RC3 would establish only that an authenticated portable receipt can preserve the tested authority binding under this trust model.

## Authority-binding projection

The receipt subject digest must be computed from an explicit projection containing every field consumed by the frozen RC8B/RC8D/RC8F/RC8H/RC8J authority stack and every semantic field later consumed by the bounded categorical relation operator:

- `execution_state`
- `evidence_admitted`
- `authority_subject_id`
- `raw_source_id`
- `authority_subject_source_id`
- `raw_bundle_id`
- `authority_subject_bundle_id`
- `raw_passage_id`
- `authority_subject_passage_id`
- `admitted_passage_span`
- `raw_claim_id`
- `authority_subject_claim_id`
- `target_atom_id`
- `authority_subject_atom_id`
- `proposal`
- `assertion`
- `operator`
- `field_warrants`
- `required_fields`
- `composition`
- `aperture`

The projection deliberately excludes only diagnostic/non-authority metadata already demonstrated not to confer RC8J authority, including `case_id`, `instrument_ids`, and `reader_agreement_count`.

Unknown fields are not silently added to the projection in this frozen candidate. Widening the authority stack or binding scope is a successor-version decision.

## Canonicalization

The projection and receipt body must use deterministic JSON canonicalization for this experiment:

- UTF-8
- object keys sorted
- compact separators `,` and `:`
- Unicode preserved (`ensure_ascii=False`)
- non-finite numbers rejected (`allow_nan=False`)
- no semantic coercion of numbers, strings, booleans, or nulls

Dictionary insertion order and transport JSON whitespace/key order must not affect verification after parse and re-canonicalization.

Raw receipt JSON parsing must reject duplicate object keys rather than accepting last-key-wins ambiguity.

## Candidate receipt body

The authenticated body must include at least:

- `schema_version = cal.rc8j.portable-warrant.v1`
- exact frozen `issuer_rc8j_commit`
- exact frozen `issuer_rc8j_blob`
- `key_id`
- `authority_status = WARRANTED`
- `authority_reason = ALL_REQUIRED_WARRANT_ESTABLISHED`
- `claim_id`
- `atom_id`
- `subject_digest_algorithm = sha256`
- `subject_digest`

The HMAC covers the canonical serialized receipt body. The transport object adds only `auth_algorithm = hmac-sha256` and the MAC value. Any authenticated field modification must invalidate verification.

## Producer behavior

The producer must:

1. deep-copy the supplied case;
2. run the exact frozen RC8J evaluator on a value-identical copy;
3. refuse to issue a receipt for every non-`WARRANTED` result;
4. compute the authority-binding projection from the untouched captured case;
5. compute its SHA-256 subject digest;
6. construct the exact receipt body with pinned issuer identity, claim ID, atom ID, status, reason, digest algorithm, and key ID;
7. HMAC-authenticate the canonical receipt body;
8. return a portable JSON-serializable receipt.

## Consumer behavior

The consumer must not receive or invoke an RC8J evaluator. It must:

1. strictly parse/validate the transported receipt;
2. reject unknown/missing receipt fields and duplicate JSON keys;
3. require exact schema, issuer commit/blob, algorithm, and trusted key ID;
4. verify the HMAC before treating any receipt field as authoritative;
5. recompute the authority-binding projection and subject digest from the consumer-side case;
6. compare subject digests in constant-time;
7. require receipt `claim_id` and `atom_id` to equal the case values;
8. require `WARRANTED / ALL_REQUIRED_WARRANT_ESTABLISHED`;
9. only then derive the existing bounded categorical relation and allow scoreless composition.

The consumer must have no caller-supplied score, confidence, threshold, support/refutation channel, or relation hint.

## Weak control

A digest-only, unauthenticated receipt control is included specifically to demonstrate the distinction between binding and authenticity. The weak control is expected to be forgeable if an attacker mutates the case and recomputes the digest. Acceptance of that weak-control forgery does **not** falsify the authenticated candidate; failure to demonstrate the weak-control weakness makes the experiment setup inconclusive.

## Preregistered decisive attacks

1. **Exact RC1A payload replay:** issue on valid `A > B`; mutate proposal to `A < B` while retaining the old field-warrant value and same atom ID; stale authenticated receipt must be refused and non-deciding.
2. **Recomputed-digest forgery:** mutate to the non-warranted payload and recompute the subject digest in a forged receipt without a valid MAC; authenticated consumer must refuse. Digest-only weak consumer should accept, demonstrating why authentication is necessary.
3. **Atom-ID substitution:** same semantic content with different `target_atom_id`; stale receipt must be refused.
4. **Claim substitution:** change `raw_claim_id` / proposition binding; stale receipt must be refused.
5. **Authority-subject substitution:** mutate an authority subject binding while semantic proposal remains fixed; stale receipt must be refused.
6. **Field-warrant mutation:** mutate a field-warrant value/status/span after issuance; stale receipt must be refused.
7. **Evidence-coordinate mutation:** mutate source/bundle/passage/admitted-span authority coordinates after issuance; stale receipt must be refused.
8. **Receipt status/reason tamper:** change authenticated `WARRANTED` or reason fields without recomputing a valid MAC; refuse.
9. **Issuer pin tamper:** change RC8J commit/blob in receipt; refuse.
10. **Key-ID / wrong-key control:** wrong trusted key or unknown `key_id`; refuse.
11. **MAC mutation/truncation:** refuse.
12. **Partial/missing field receipt:** refuse.
13. **Unknown receipt field:** refuse.
14. **Duplicate JSON key transport:** refuse.
15. **Transport order/whitespace metamorphic:** semantically identical serialized receipt with reordered keys/whitespace must verify after strict parse and canonicalization.
16. **Case dictionary insertion-order metamorphic:** authority-binding digest must remain identical.
17. **Diagnostic metadata invariance:** changes only to `case_id`, `instrument_ids`, and `reader_agreement_count` must not alter binding digest, relation, or scoreless conclusion.
18. **Producer-side non-warranted control:** exact frozen RC8J rejection/unresolved states must never receive a portable warrant receipt.
19. **Categorical regressions:** support, refute, irrelevant, unresolved same-pair relation, swapped inverse, mixed abstention, support+irrelevant, support+unresolved, and order invariance must retain RC2/RC1 bounded behavior.
20. **Forbidden scalar/polarity surfaces:** score, confidence, threshold, channel, and relation hint remain absent/rejected.

## Primary falsifier

Classify RC3 `FALSIFIED_PORTABLE_AUTHORITY_BINDING` and stop if any case independently known to be non-`WARRANTED` under the exact frozen RC8J can use an authenticated RC3 receipt to enter scoreless categorical composition as deciding `SUPPORTS` or `REFUTES` without possession of the trusted key used to authenticate the original receipt.

Also falsify if a stale authenticated receipt remains valid after mutation of any field in the frozen authority-binding projection, or if authenticated receipt fields can be tampered without rejection.

Do not patch a falsified frozen RC3 candidate and relabel it as the same result.

## Setup-invalid / inconclusive conditions

Record an inconclusive/setup-invalid disposition rather than support if:

- exact RC8J identity cannot be verified;
- the base positive case is not `WARRANTED`;
- the exact RC1A mutation is not independently non-`WARRANTED`;
- the digest-only weak control cannot be forged as expected;
- producer and consumer accidentally share the RC8J evaluator path;
- the consumer reruns RC8J instead of verifying the portable receipt;
- the candidate changes production `src/` or frozen RC2/RC8J semantics.

## Supported-with-bounds condition

Only `SUPPORTED_WITH_BOUNDS` if all preregistered authenticated-binding attacks and categorical regressions pass, the weak control demonstrates digest-only forgery, production `src/` remains unchanged, and the receipt consumer reaches bounded categorical conclusions without rerunning RC8J.

## What even a pass would not establish

- production cryptographic architecture
- production key management, rotation, revocation, or compromise recovery
- asymmetric signatures or public-verification trust
- generic semantic entailment
- semantic-text extraction
- proposition truth in the world
- broader semantic families
- Contract C projection or successor semantics
- Decision Engine policy
- independent clean-room reproduction
- release, merge, or promotion authorization
