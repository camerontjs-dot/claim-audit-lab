# RC7D-B — Proposal / Authority / Composition Separation

## Classification

Post-reveal diagnostic hardening. Not context-free. No production authorization.

This successor consumes immutable RC7D evidence at `f57ffeb839f831d32d3e2b0bea1b34d5e73ac0e3` and the same 74-case cohort. It may not change the frozen RC7D specialist candidate or cohort semantics.

## Observed motivation from RC7D

The frozen 8-operator broadcast recovered substantially more semantic dimensions than single routing, while false semantic-dimension claims remained rare. However, unsafe semantic atoms accumulated as more operators were added. This suggests three distinct questions:

1. **Discovery:** did an operator correctly identify a semantic dimension worth inspecting?
2. **Authority:** are the operator's proposed typed atoms actually warranted by the source?
3. **Composition:** may independently warranted atoms be combined into a larger semantic object?

RC7D-B tests those separately.

## Hypotheses

### H1 — Proposal/authority separation

Treating specialist outputs as preserved **proposals** rather than immediate semantic authority, followed by a separate deterministic warrant validator, can retain the information advantage of broadcast while sharply reducing unsafe authorized atoms.

### H2 — Structural multiplicity advantage

Even with a perfect router and perfect specialists, selecting exactly one semantic family per source necessarily loses information on genuinely mixed-semantic cases. A multi-operator architecture therefore has a structural information-retention advantage independent of parser quality.

### H3 — Composition separability

If perfect component semantics are supplied directly to the composition governor and valid/invalid compositions are still mishandled, composition governance is an independent bottleneck rather than an extraction artifact.

### H4 — Disagreement as risk signal, not truth

For the independently coded quantifier implementations, disagreement should correlate with error risk, but agreement must not be treated as proof of correctness.

## No LLM lane

No LLM, embedding model, learned router, or generative semantic scout is allowed.

## Frozen inputs

- RC7D evidence commit: `f57ffeb839f831d32d3e2b0bea1b34d5e73ac0e3`
- RC7D candidate freeze: `b5b04485cb1e09f025017e25cd6d008e6c5030f6`
- RC7D cohort freeze with preserved count-assertion typo: `4a5148bce7d861815a08fcdf8623a7e9e28fa367`
- RC7D evaluator freeze: `d28bdd2d9e52a1c8ebf2506529c1ae0cc25b6acd`

The exact same cohort cases and gold semantics must be used.

## Architecture lanes

### A. `broadcast_proposals_raw`

The original frozen broadcast outputs are interpreted as proposals only. No proposal is semantic authority merely because an operator emitted it.

### B. `broadcast_proposals_validated`

Every frozen specialist proposal is preserved. A separately implemented deterministic validator returns per atom:

- `AUTHORIZED`
- `REJECTED`
- `UNRESOLVED`

Only `AUTHORIZED` atoms may enter composition. Rejected/unresolved proposals remain in the record.

### C. `single_router_validated`

Same validator as B, but only proposals from the frozen single-router architecture are eligible. This isolates whether validation alone, rather than multiplicity, explains gains.

### D. `proposal_only_zero_authority`

All proposals preserved; zero atoms authorized. This is a fail-closed utility control. It should have zero unsafe authority but poor authorized coverage.

### E. `oracle_component_composition`

Use cohort gold component atoms as if every specialist had interpreted its local semantics perfectly. Feed only those component dimensions to the frozen composition policy. This isolates composition from interpretation.

### F. `oracle_single_family_ceiling`

Give an ideal router perfect knowledge of all gold semantic dimensions but force it to select exactly one dimension per source. Compare retained dimensions with an oracle multi-operator union. This tests structural information loss from exclusive routing without any parser noise.

## Validator constraints

Validators must be independently coded from the frozen candidate functions. They may inspect:

- the exact raw source;
- the proposed atom;
- the proposal's source span and warrant label.

They may not inspect gold labels.

A validator must fail closed when it cannot verify the complete proposed atom.

Validation should emphasize exact semantic commitments, including modifier boundaries. Detecting the right semantic family is insufficient to authorize a wrong population, predicate, polarity, excluded entity, temporal scope, quantitative value, subclass relation, or permission status.

## Metrics

### Proposal discovery

- proposal semantic-dimension recall;
- proposal dimension precision;
- raw-source preservation.

### Authorized semantics

- authorized semantic-dimension recall;
- authorized typed-atom recall;
- authorized typed-atom precision;
- unsafe authorized atom count/rate;
- false authorized dimension count/rate;
- rejected proposal count;
- unresolved proposal count.

### Utility/safety tradeoff

Compare raw broadcast, validated broadcast, validated single routing, and zero-authority control.

### Composition

- oracle component valid-composition accuracy;
- oracle component invalid/non-collapsible composition accuracy;
- conflict preservation.

### Structural ceiling

- oracle single-family dimension retention on mixed cases;
- oracle multi-operator dimension retention on the same cases.

### Quantifier duplicate

- error rate when implementations disagree;
- error rate when implementations agree;
- unsafe authorization rate under an agreement-only gate.

### Operator-count stress after validation

For bank sizes 2, 4, 6, 8:

- proposal false-claim rate;
- authorized false-claim rate;
- unsafe authorized case rate;
- authorized semantic-dimension recall.

## Preregistered terminal states

### `PROPOSAL_AUTHORITY_SEPARATION_SUPPORTED`

All of:

- validated broadcast unsafe authorized atom count = 0;
- validated broadcast false authorized dimension count = 0;
- validated broadcast authorized semantic-dimension recall >= 0.60;
- validated broadcast authorized typed-atom precision >= 0.98;
- validated broadcast retains more authorized gold dimensions on mixed cases than validated single routing;
- validated broadcast materially outperforms zero-authority control on authorized recall;
- no material increase in unsafe authorized case rate from bank size 2 to 8;
- oracle multi-operator retains strictly more mixed-case dimensions than oracle single-family ceiling.

This state supports only the separation architecture, not general language coverage.

### `VALIDATION_GATE_TOO_LOSSY`

Validated broadcast reaches zero unsafe authority but authorized semantic-dimension recall < 0.60.

### `AUTHORIZED_OVERCLAIM_PERSISTS`

Validated broadcast still authorizes any semantically unsupported atom or false semantic dimension.

### `COMPOSITION_GOVERNOR_DEFECT`

Oracle-perfect component inputs still yield any invalid composition, missing preregistered valid composition, or incorrect collapse of a coexist-only relation.

### `EXCLUSIVE_ROUTING_NOT_STRUCTURALLY_HARMFUL`

Oracle single-family selection retains the same number of gold dimensions as oracle multi-operator on the mixed-semantic cases. This would falsify H2.

### `APPARATUS_INVALID`

Frozen inputs differ, raw source changes, validator accesses gold, or execution is otherwise invalid.

Terminal precedence:

`APPARATUS_INVALID` > `COMPOSITION_GOVERNOR_DEFECT` > `AUTHORIZED_OVERCLAIM_PERSISTS` > `VALIDATION_GATE_TOO_LOSSY` > `EXCLUSIVE_ROUTING_NOT_STRUCTURALLY_HARMFUL` > `PROPOSAL_AUTHORITY_SEPARATION_SUPPORTED`.

## Claim limits

Even a successful result is post-reveal local hardening. It does not establish fresh independent recoverability, production readiness, or the absence of a future need for probabilistic language interpretation.
