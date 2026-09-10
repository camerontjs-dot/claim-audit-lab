# Contract C Unresolved-Evidence Provenance RC0 — Results

## Classification

Draft Research Infrastructure / information-sufficiency evidence record. No Contract C amendment, Decision Engine change, production CAL mutation, Contract E Authorization, merge, release, tag, or promotion.

## Exact execution

- exact research head: `34c92a5098389c3b691750baf9c3ab85fff5d20c`
- run: `34505136997`
- artifact id: `10163485923`
- artifact digest: `sha256:ab84eda20d93a3a6dec9600d16f35a96e8cebcd94bb27754f3362dbfda4cbd8d`
- disposition: `SUPPORTED_BOUNDED_CONTRACT_C_UNRESOLVED_PROVENANCE_GAP`

Frozen predecessor:

- bound temporal successor freeze `10ce0894a56f265434b24963bf0543765c453996`
- `bound_relation.py` blob `94b44f3b0b2b3f077c17ca55eb944117ffa22b77`
- `bound_projection.py` blob `77fed3e7a7273b13e6dfb89e0ffee7fce1503c6c`
- Contract C authority `5fe55f9ed5d0ee9f026ca1b077e9d70ce0487ea1`
- Contract C validator blob `9c75ccfbf2223578a8d1a7bf0c39673b394fbea4`

## Terminal observations

```json
{
  "contract_c_bytes_differ_between_unresolved_executions": true,
  "opaque_state_basis_ids_differ": true,
  "research_disposition": "SUPPORTED_BOUNDED_CONTRACT_C_UNRESOLVED_PROVENANCE_GAP",
  "same_exact_contract_b_index_between_unresolved_executions": true,
  "same_terminal_public_semantics_between_unresolved_executions": true,
  "support_control_recovered": true,
  "unresolved_a_recovered": false,
  "unresolved_b_recovered": false,
  "unresolved_causal_evidence_underdetermined": true
}
```

## OBSERVED

### Positive reconstruction control passed

A supported temporal result was projected in a Contract-B evidence world containing two admitted passages. Contract C carried the deciding support as a normal `support` contribution and the independent consumer uniquely reconstructed the exact causal passage `INFO-S-P1` through the contribution basis.

This establishes that the consumer apparatus can follow a released Contract-C evidence attribution edge when one exists.

### Unresolved provenance was not reconstructable

Two executions used the same exact negative-event proposition and the same exact Contract-B evidence world containing two admitted passages.

- Execution A projected only the warranted `UNRESOLVED` proof from `INFO-U-P1`.
- Execution B projected only the warranted `UNRESOLVED` proof from `INFO-U-P2`.

Both resulting Contract C objects:

- passed exact released Contract C validation;
- bound the same exact Contract-B index and immutable evidence world;
- reported `completed / not_checkable`;
- reported `unresolved_categorical_relation`;
- carried no falsely polarized `support` or `counterevidence` contribution for the unresolved relation.

The research-side projector receipt retained a different omitted temporal relation ID for each execution, proving the upstream participating evidence differed.

The independent consumer was given only canonical Contract C plus the exact bound Contract-B index. It imported no CAL code and performed no temporal semantic re-audit. In both executions it found an opaque causal `state:` basis and two possible bound evidence references, but no normative Contract-C edge from the state basis to either passage.

It therefore could not uniquely identify the actual participating unresolved passage in either execution.

### Opaque state identity distinguishes executions but does not resolve provenance

The two Contract C byte strings and `state:` basis IDs differ. That means Contract C preserves that some producer-attributable state identity changed.

However, Contract C 1.0 defines `state:` basis members as opaque typed CAL-attributable identities. The released contract does not define a normative mapping from a `state:` ID to a Contract-B evidence reference. An independent contract-level consumer cannot use the differing opaque IDs to recover whether `INFO-U-P1` or `INFO-U-P2` participated without producer-private knowledge or a fresh semantic re-audit.

## INFERENCE

Within this bounded event-order case, canonical Contract C 1.0 plus exact bound Contract B is insufficient for **exact causal evidence reconstruction** when the causal semantic relation is warranted but neither support nor counterevidence.

The gap is narrower than terminal-state loss. Contract C still preserves:

- exact evidence-world identity;
- proposition identity;
- not-checkable completion;
- unresolved terminal branch;
- an opaque causal state identity.

What is lost at the released interface is the explicit state-to-evidence attribution edge.

## Alternative explanations considered

- **Consumer incompetence:** weakened by the positive support control, which recovered exact provenance from the same contract machinery.
- **Different Contract-B worlds caused ambiguity:** ruled out in the paired unresolved executions; they used the same exact Contract-B index/evidence world.
- **A fresh semantic engine could inspect the source text:** true but not responsive to this test. Re-running semantic interpretation is a new audit, not reconstruction of the producer's causal attribution from Contract C.
- **Opaque state IDs contain recoverable hashes:** the current producer may construct them from richer material, but the released Contract C contract intentionally exposes them as opaque typed IDs and defines no portable decoding/mapping contract. Depending on private hash construction would violate the independent-consumer aperture.

## Hard boundary

This experiment does **not** establish that Contract C 1.0 is generally insufficient, nor that a schema revision is required immediately.

It establishes only that the tested unresolved/irrelevant-style causal evidence provenance cannot be reconstructed exactly from the released C+B interface without additional producer-private or semantic work.

## No fix selected

No change is authorized yet. At least four competing responses remain:

1. add a neutral/non-deciding evidence contribution role/channel;
2. add an explicit state-to-evidence attribution structure;
3. introduce another compact typed basis form that can reference evidence without assigning support/refutation polarity;
4. leave Contract C unchanged and require a separate immutable producer receipt when this level of reconstruction is needed.

The smallest successor should compare these representations against the frozen counterexample, existing Contract C invariants, independent consumers, and downstream Decision behavior before selecting any contract change.
