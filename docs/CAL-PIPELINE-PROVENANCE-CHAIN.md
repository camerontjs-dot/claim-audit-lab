# CAL Pipeline Provenance Chain

**Status:** cross-repo architecture pointer / local obligation record. No CAL semantic rule, Contract C/C2 schema, Decision behavior, Authorization, release, or production default is changed by this document.

## Canonical blueprint

The canonical proposed architecture is maintained in `camerontjs-dot/apparatus-contracts` Draft PR #101:

- `docs/architecture/CAL-PIPELINE-PROVENANCE-CHAIN-BLUEPRINT.md`
- canonical proposal head at this pointer's creation: `d16e5e14cab55ed23bdeee4cdeecf48724c542db`

Apparatus Contracts owns the cross-pipeline blueprint. Claim Audit Lab owns CAL semantic execution, native CAL records, Contract C producer behavior, and conformance to any later-qualified provenance schema.

## Local requirement

CAL must leave enough immutable provenance for a later auditor to distinguish:

1. evidence that never reached CAL;
2. evidence admitted by Contract B but not semantically participating;
3. evidence CAL measured but could not turn into a deciding relation;
4. evidence that became causal or residual semantic state;
5. apparatus failure/incomplete execution;
6. a legitimate `not_checkable` semantic result.

### CAL must eventually attest

- exact Contract B version/bundle ID/bundle digest as `causal_input`;
- exact B artifact digest actually validated and consumed;
- Contract-B checksum/integrity verification outcome;
- exact admitted semantic-context identity/digest derived from B;
- exact CAL implementation identity;
- exact behaviorally relevant CAL policy identity/digest;
- exact resolver / producer-authority identity required by the active Contract C profile;
- exact native CAL result digest;
- exact Contract C/C2 byte digest plus internal result identity;
- terminal apparatus execution state;
- semantic completion class without reinterpretation (`assessed`, `not_checkable`, failure/incomplete as applicable);
- durable locators for reconstruction-required intake, native-result, handoff and authority artifacts.

## Evidence-world binding

Contract C may declare the exact B world it consumed, but that declaration must not become its own trust root. A downstream consumer should be able to recover the exact B bytes and verify them against an independently trusted producer/run commitment before deriving participant authority.

## Producer-authority binding

Historical C2 integration pressure showed that CAL implementation/policy/resolver identity is material. A provenance record must preserve the exact producer-authority mapping used for each historical C object so later consumers can distinguish a genuine producer-conformance break from a CAL semantic result.

## Semantic boundary

Provenance must not convert a semantic `MEASUREMENT_MISS`, `UNRESOLVED`, or `not_checkable` result into support/refutation. Its job is to prove what exact evidence and exact machinery produced that result.

## Nonclaims

This pointer does not qualify a production attestation schema, widen Contract C/C2, promote the current CAL V1 candidate, authorize a new resolver row, or change any semantic verdict behavior.
