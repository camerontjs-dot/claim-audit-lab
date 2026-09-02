# RC8 Semantic Authority Machinery: Aggregate Results

## Terminal research disposition

**RC8J is supported with bounds as the strongest candidate produced by this research programme.**

This disposition is limited to the tested structured authority-transition envelope. It is not production authorization, a Contract C projection result, a source-text interpretation result, or independent-recoverability evidence.

Strongest candidate:

- path: `research/semantic_authority_machinery_rc8/authority_contract_rc8j.py`
- blob: `f55156e43e0c1b4a7868bc8339585b8892edda38`
- candidate freeze: `8e75c6782bb95c3763d06230b9c5df2b6af44054`

Frozen Contract B authority used by the later chain-of-custody experiments:

- repository: `camerontjs-dot/apparatus-contracts`
- commit: `c314e53bd91c0736aa4370a364673b069aceb43e`
- handoff spec blob: `3e49901dff567ff5bbad55a2d6ccdc3ed36a7a26`
- factual-context extension blob: `77645a6adac664892866f3fdf8abf66cd1d0dd10`

## Sequential evidence record

| Stage | Question / change | Result | Consequence |
|---|---|---|---|
| RC8 | Can a typed formal authority gate discriminate structured warrant failures? | 68/68 heldout status and reason exact, 0 unsafe | Formal transition envelope worth attacking causally |
| RC8A | Are internally plausible receipt fragments sufficient without binding? | **FALSIFIED**: 6/7 unsafe provenance/span mutations warranted | Require explicit same-subject/source-span binding |
| RC8B | Does same-subject binding plus governed support span close RC8A? | 112/112 exposed + 50/50 fresh prospective exact, 0 unsafe | Same-subject receipt consistency supported within envelope |
| RC8C | Is RC8B actually anchored to admitted evidence source? | **FALSIFIED**: 2/3 unsafe source missing/substitution cases warranted | Add explicit admitted-source anchor |
| RC8D | Does explicit source anchoring preserve prior behavior? | 165/165 exposed + 15/15 fresh prospective exact, 0 unsafe | Source-bound receipt supported within envelope |
| RC8E | Can a source-bound receipt be transplanted to a different atom in the same source? | **FALSIFIED**: 3 unsafe warrants | Add explicit whole-atom identity binding |
| RC8F | Does source + atom binding close the same-source transplant? | 190/190 exposed + 21/21 fresh prospective exact, 0 unsafe | Source/atom binding supported within envelope |
| RC8G | Is source + atom identity sufficient to bind the receipt to Contract B's actual evidence segment? | **FALSIFIED**: 8 unsafe bundle/passage/span mutations | Bind to validated bundle, admitted passage and passage extent |
| RC8H | Does Contract B segment binding plus atom binding close RC8G? | 228/228 exposed + 26/26 fresh prospective exact, 0 unsafe | Source/bundle/passage/span/atom chain supported within envelope |
| RC8I | Can the fully segment-bound receipt be transplanted between distinct Contract B claims? | **FALSIFIED**: 4 unsafe claim-binding warrants; claim-vs-atom precedence also exposed | Add explicit Contract B claim binding before atom identity |
| RC8J | Does claim binding close RC8I while preserving the full prior chain? | 268/268 exposed + 28/28 fresh prospective exact, 0 unsafe | Strongest supported terminal research candidate |

## Terminal RC8J evidence

### Exposed qualification

Run `33670472654`, job `100382540151`:

- 268 cases;
- 268/268 exact authority status;
- 268/268 exact typed reason;
- 0 unsafe warranted atoms;
- artifact `9862279058`;
- digest `sha256:bc38b62b93734ab7dbd183228cb82240f5f58f5044d2c174149ad248eafeaa4d`.

### Fresh prospective heldout

Candidate freeze preceded cohort creation.

Accepted pre-reveal:

- run `33670888377`;
- job `100383924982`;
- exact candidate/parent/apparatus and Contract B authority verification passed;
- candidate-blind structural checks passed;
- no heldout candidate execution occurred.

Reveal:

- run `33670993492`;
- job `100384271951`;
- 28/28 exact authority status;
- 28/28 exact typed reason;
- 0 unsafe warranted atoms;
- 5/5 targeted claim-binding cases stayed non-warranted;
- reader/instrument bank invariance held for warranted and unresolved controls;
- artifact `9862475745`;
- digest `sha256:0f377934b1e4adb8e813fd6d5a7c7d2e679cf37ca882d21979ca5889b98141d0`.

Expected and observed state distribution matched exactly:

- `WARRANTED`: 3;
- `REJECTED`: 12;
- `UNRESOLVED`: 12;
- `NO_ASSESSMENT`: 1.

## Strongest supported authority chain

The evidence currently supports this ordered internal chain:

1. execution completed;
2. evidence admitted;
3. admitted source identity bound;
4. validated Contract B bundle identity bound;
5. admitted Contract B passage identity bound;
6. admitted passage extent valid;
7. proposal and valid required-field support contained within the admitted passage;
8. referenced Contract B claim identity bound;
9. target atom identity bound;
10. subordinate proposal/assertion/operator/required-field/composition/aperture receipts bound to the same authority subject;
11. assertion state/scope accepted;
12. operator domain, applicability, governance and field jurisdiction accepted;
13. required field status/value/support accepted;
14. required composition and aperture accepted when required.

Successful completion yields `WARRANTED`. Typed adverse conditions yield `REJECTED` or `UNRESOLVED` according to the frozen behavior. Execution failure is `NO_ASSESSMENT` and is not epistemic unresolved.

## Invariants supported by the programme

- Evidence admission is necessary but not semantic warrant.
- Contract B factual context/history are not proposition authority by themselves.
- Source, bundle, passage, claim and atom identities are distinct bindings.
- Admitted-passage extent and operator-governance extent are distinct boundaries.
- Extraction unresolved is not semantic unknown.
- A required material field cannot borrow authority from a partially correct atom.
- Warranted components do not automatically warrant their composition.
- Aperture/completeness requires separate authority when material.
- Reader count, instrument count, agreement and scalar confidence do not strengthen authority by themselves.
- Execution failure is orthogonal to epistemic state.

## Preserved falsifiers

The terminal candidate does not erase failures. The following are primary causal evidence:

- `RC8A_RESULTS.md`: receipt-fragment source binding failure;
- `RC8C_RESULTS.md`: admitted-source anchor failure;
- RC8E atom-identity falsifier records;
- RC8G Contract-B evidence-segment falsifier records;
- `RC8I_RESULTS.md`: Contract-B claim-identity failure.

The programme's architecture changed because these tests failed.

## Procedural deviations

See `DEVIATIONS.md`.

Important bounded deviations include:

- the original pre-preregistration open-fixture prototype is not prospective evidence;
- RC8F's first pre-reveal attempt had a model-free 20-vs-21 case-count assertion error, corrected before any candidate execution;
- duplicate push/PR workflow runs are not counted as replication;
- this entire programme is one accumulated normal-context research thread and therefore cannot establish fresh independent recovery.

## What remains unknown

The terminal result does **not** establish:

- canonical or collision-resistant atom-ID generation;
- honest derivation of opaque identity fields;
- correctness of source-text semantic interpretation;
- proposition truth;
- complete composition semantics;
- cryptographic authenticity beyond validated Contract B integrity;
- Contract C projection sufficiency;
- production integration/release readiness;
- independent implementation recoverability.

## Next scientific boundary

The next costly-to-fake evidence is a **fresh independent implementation/reproduction from a frozen specification under a clean information aperture**.

That experiment must occur in a separate context. This thread is contaminated by the implementation and falsification history and must not be used as the independent implementer.
