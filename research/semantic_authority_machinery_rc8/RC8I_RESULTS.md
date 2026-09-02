# RC8I Results: Contract-B Claim Identity Binding Falsifier

## Disposition

**FALSIFIED** the frozen RC8H candidate as a sufficient claim-specific authority gate.

RC8H's narrower source/bundle/passage/span/atom result remains intact. RC8I isolates an additional Contract B claim-identity requirement.

## Frozen parent and apparatus

- RC8H candidate blob: `4b872e455d52d7a682bb719889860d2cac7909a7`
- RC8H candidate freeze: `1d1fec29ad5e08e28d3b9751534b85121221b17c`
- RC8I preregistration: `52e6f170628ed953207cf9006df58867c2d602f3`
- cohort blob: `d66b2642df223dbce6f250d7f567be35bfc43675`
- evaluator blob: `9bd5884da54c542b86f2b8e84da46c8651843b2b`
- structural-test blob: `3ec42f0ecd8b6831963cd2ce84a89a6ece3246ce`

The accepted pre-reveal run `33670140258` / job `100381420904` verified the production surface, frozen Contract B authority, frozen RC8H stack, and RC8I apparatus, then ran only candidate-blind structural checks.

## Reveal

Run `33670225461`, job `100381701360`:

- evaluator execution: success
- result artifact upload: success
- hard safety criterion: failure
- artifact: `9862180423`
- digest: `sha256:35bba3e564869d4ec4750c15e49e620cd09274e0fbfd8952c76f8816a1972fae`

Exact result:

- 14 cases
- 10/14 exact status
- 9/14 exact typed reason
- 4 unsafe warranted atoms

Unsafe cases:

1. `I-RAW-CLAIM-MISSING`: expected unresolved claim binding, observed `WARRANTED`.
2. `I-SUBJECT-CLAIM-MISSING`: expected unresolved claim binding, observed `WARRANTED`.
3. `I-CLAIM-MISMATCH`: expected claim mismatch rejection, observed `WARRANTED`.
4. `I-WHOLE-RECEIPT-TRANSPLANT`: expected claim mismatch rejection, observed `WARRANTED` despite identical source/bundle/passage/span/atom and semantic material.

`I-CLAIM-ATOM-PREC` rejected at atom identity rather than the preregistered earlier claim mismatch. This is not unsafe, but it confirms the existing RC8H chain has no claim-before-atom gate.

## Interpretation

The evidence supports a small repair: bind the authority receipt to the referenced Contract B `claim_id` after validated source/bundle/passage segment binding and before whole-atom identity.

This does not justify new hash authority, new semantic inference, confidence thresholds, reader voting, or Contract B schema changes. Contract B already supplies canonical claim identity to the semantic-measurement context.

No production, contract, release, merge, or promotion action is authorized by this result.
