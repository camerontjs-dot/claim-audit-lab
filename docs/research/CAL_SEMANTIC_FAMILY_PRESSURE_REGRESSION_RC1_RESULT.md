# CAL Semantic Family Pressure Regression RC1 — Terminal Result

Date: 2026-09-17

Classification: Draft Research / known-corpus regression confirmation.

## Frozen lineage

- original pressure RC0 apparatus: `634267395466c442dec61b0aeb40a92d63176648`
- original pressure RC0 run: `35298162665`
- exact RC1 regression apparatus head: `88e332e3ee69bda4a91227baccfa0715a4b573fd`
- dedicated RC1 run: `35299097949`
- frozen cases blob: `b6f87e66004a7b8bed52412dc9f3dd38dd9f1e78`

## Disposition

**SUPPORTED_PRESSURE_REGRESSION_RC1.**

The exact 50-case end-stage pressure RC0 corpus passes against the two repaired authority subjects while the other seven exact family subjects remain unchanged.

## Subject changes

Only:

- strict comparison:
  - RC0 subject `e085fbc0f74480a81e5b3bd4c11796a6543382e7`
  - RC1 subject `33cf39b1b2fabae2c867187bc097da396ffd7014`

- direct event order:
  - RC0 subject `42fe25bd5a142277bd1903dbe65b7ea57bc94c1a`
  - RC1 subject `2c9369144fecb3025bf28885ab6e322d895c3dbf`

The other seven subject SHAs are byte-identical to RC0.

## Result

Run `35299097949` passed:

- frozen pressure apparatus validation;
- exact reconstruction of all nine subject SHAs;
- all nine canonical cross-family owner cases;
- all 41 noncanonical RC0 pressure cases with zero unauthorized atomic-family warrants;
- static checks.

The nine unauthorized warrants discovered by RC0 are therefore closed on their exact frozen regression corpus.

## Epistemic status

This is regression closure only.

The repaired subjects were designed with the RC0 failures in view, so this result does not establish generalization.

A second unseen corpus was frozen separately before this result was used for any further repair. That campaign is the next source of hardening evidence.

The unrelated repository Public suite remained red on this research branch and is not used as semantic qualification evidence.

No production promotion, merge, or release is authorized.
