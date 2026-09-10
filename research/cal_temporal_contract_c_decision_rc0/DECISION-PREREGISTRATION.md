# Temporal Contract C → Maintained Decision Engine RC0 — Preregistration

## Classification

Draft Research Infrastructure / downstream consumer conformance.

This experiment changes neither Contract C nor Decision Engine. It performs no Contract E Authorization and no external mutation.

## Exact inputs

- bound temporal successor freeze: `10ce0894a56f265434b24963bf0543765c453996`
- bound successor decisive run: `34434782626`
- bound successor artifact: `10135769621`
- bound successor artifact digest: `sha256:4667d7c9328d034f32e92822229f625f8d15acba45dfc51257270b148826f67c`
- Contract C 1.0 authority: `5fe55f9ed5d0ee9f026ca1b077e9d70ce0487ea1`
- Contract C validator blob: `9c75ccfbf2223578a8d1a7bf0c39673b394fbea4`
- maintained Decision Engine exact head: `358c2bb20f490bf25e808434394b26a70a16a123`
- Decision CLI blob: `b3808a536ca5f976ca1022c7c9f13a229d31af79`
- Contract C ingress blob: `f57a8067dadc04afb459f1d0342b2b786ec775e6`
- supported-claim policy blob: `3529b75f75936fffb9b2d9e2972cb7117b526661`
- runtime dispatch blob: `7020006a350f78b0381df3309f8085966890a049`
- Contract D canonicalizer blob: `0ea61767b9ae61b3b80c0c2f26de4292f213b7fb`
- Contract D 1.0 authority: `298a1a0f7b7b6d7712e11200d04faec3e1ca169b`

The Decision Engine head is pinned exactly for this run even if `main` later advances.

## Research question

Can the unchanged maintained `decision-engine.contract-c.supported-claim-verification@1.0.0` policy consume exact released Contract C 1.0 objects produced from the bound temporal semantic family without hidden strict-comparison assumptions?

## Positive cases

1. temporal supported + `completion=assessed` -> Contract D `completed / clear`, reason `contract_c_supported`;
2. temporal contradicted + `completion=assessed` -> `completed / hold`, reason `contract_c_reported_verdict_not_supported`;
3. same-world temporal support/refute conflict + `completion=not_checkable` -> `completed / hold`, reason `contract_c_proposition_not_checkable`;
4. unresolved negative-event temporal result + `completion=not_checkable` -> identical safe hold reason.

All Contract D outputs must pass exact Contract D 1.0 authority canonicalization performed by the maintained CLI.

The effect object that appears in Contract D is only a candidate downstream effect. `clear` is not Authorization and no Contract E call occurs.

## Boundary/falsifier cases

The consumer must fail closed for:

- wrong external whole-object Contract C SHA-256;
- wrong expected Contract-B bundle identity/hash;
- wrong Decision target content hash;
- Contract C with an illegal extra semantic-family field in a Contract-C-owned object;
- Contract C measurement containing categorical string temporal semantics where 1.0 allows only finite numeric/null values.

## Producer-policy metadata metamorphism

A second valid `supported` Contract C object will change only producer-owned policy metadata from temporal-family labeling to a control label, with the policy hash and result-set identity correctly recomputed. If exact validation still passes, Decision disposition/reason/effect must remain unchanged.

This is a policy-firewall test only. It does not mean producer metadata is semantically unimportant upstream; it tests that the maintained Decision policy does not secretly branch on it.

## Expected interpretation

`SUPPORTED_WITH_BOUNDS_AND_UPSTREAM_PROVENANCE_GAP` if all Decision controls pass while preserving the already observed Contract C unresolved-evidence provenance compression.

`FALSIFIED_TEMPORAL_DECISION_CONFORMANCE` if an exact valid deciding temporal Contract C cannot traverse the maintained consumer or if producer-only semantic-family metadata changes Decision behavior.

Apparatus/setup failures are separate and must not be relabeled as semantic evidence.
