# CAL V1 RC1 authority-integrity successor

Status: **pre-implementation successor scope record**

Parent candidate: `dca2ec7f2c117cc0b4d6c543ab5049cac7994298`

Failed qualification evidence: Draft PR #103, terminal `CAL_V1_QUALIFICATION_FAILED`.

## Observed failure

Fresh qualification case `Q12_TAMPERED_AUTHORITY_IDENTITY` rewrote an otherwise legitimate `AuthorityReceipt` and nested `SemanticAtom` so their supplied audit-context and evidence-world binding fields matched a different evidence world while retaining the original content-derived `authority_id` and `atom_id`.

The frozen parent accepted that reconstructed object and derived categorical `SUPPORTS`.

Separate qualification cases established that same-ID proposition substitution, stale passage hashes, and an ordinary stale-world authority were already rejected. The repair target is therefore the lower-level authority-consumer integrity seam, not general CAL proposition/world binding.

## Smallest successor hypothesis

A relation consumer can reject the observed unsafe class if it independently revalidates, before relation derivation:

1. authority status/reason;
2. exact context/world binding at both authority and atom layers;
3. atom semantic-family agreement with the proposition;
4. atom passage/source membership in the admitted evidence world;
5. atom semantic fields against independent source completion from that admitted passage;
6. the content-derived `atom_id` from the exact atom material;
7. the content-derived `authority_id` from the exact authority material.

This does not introduce signatures, portable authentication, new semantic families, scalar confidence, new composition rules, Contract B/C changes, or a new production surface.

## Falsifiers

The successor is not supported if any of the following survive fresh post-freeze qualification:

- a rebound authority with stale atom/authority identities is accepted;
- an atom whose fields no longer match the admitted source passage is accepted even after IDs are recomputed;
- a recomputed atom identity paired with stale authority identity is accepted;
- ordinary supported/refuted cases change conclusion unexpectedly;
- same-ID proposition substitution, stale passage hash, ordinary stale-world authority, mixed-evidence abstention, unsupported-family fail-closed behavior, or Contract C non-deciding projection regresses.

## Explicit boundary

Content-address revalidation plus source re-grounding is an integrity and semantic-grounding check. It does **not** establish cryptographic authenticity of an arbitrarily reconstructed external authority receipt. A caller able to fabricate an entirely new internally self-consistent object is outside the claim of this successor unless the object fails source grounding or other exact checks above.

If external portable authority is later required, that is a distinct authenticated-receipt boundary and must not be smuggled into this repair.

## Freeze rule

RC1 implementation may be changed only before successor freeze. After ordinary CI is green, the exact successor source is frozen. Fresh qualification artifacts are then added on a separate descendant branch. A hard-safety failure after freeze is preserved and requires another successor rather than patching RC1 in place.
