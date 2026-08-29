# RC0B Freeze 05: Corrected Evaluator

Status: FROZEN

This record freezes the corrected RC0B apparatus before any candidate or historical implementation exposure.

## Frozen objects

- `docs/research/rc0b-phase1-source-aperture.md` blob `6a52455fa9d4189ec27904740e6e0093844c72b9`
- `docs/research/rc0b-corrected-evaluator-spec.md` blob `792563efc4d04a088abf6016fb88d8b8073aea22`
- `docs/research/rc0b-frozen-cases.json` blob `e2b8a317cb8c6a0840199002957d6e6bf05531b6`
- `docs/research/rc0b_evaluator.py` blob `6f4969f9d5dd1252fbb8826b2ff0911e5a3b9cd4`

The frozen apparatus includes properties A-K, all mandatory corrected controls, five weak controls, expected invariants, explicit falsifiers, scoring/disposition logic, and measurement-quality alternative explanations.

## Weak-control discrimination before freeze

Equivalent command: `python docs/research/rc0b_evaluator.py --self-test`

Observed failures:
- W1 generic abstention fails A, D, E.
- W2 terminal taxonomy without typed state fails D, E.
- W3 trust shortcut fails E, J.
- W4 causal-basis echoer fails G.
- W5 policy logger with invariant behavior fails H.

No weak control clears the architecture-relevant gate.

## Immutability rule

From this freeze onward, fixtures, evaluator rules, weak controls, invariants, falsifiers, and scoring/disposition logic are immutable for RC0B.

After candidate exposure, do not repair decisive expectations, alter fixtures to accommodate candidates, weaken controls, or change scoring because a candidate fails. A newly discovered material evaluator defect terminates the execution as INCONCLUSIVE or FALSIFIED as appropriate.

## Aperture transition

Phase-2 candidate/historical access is authorized only after the commit containing this freeze record exists. Every post-freeze access must be recorded in the aperture audit. Frozen evaluator objects may not be modified.
