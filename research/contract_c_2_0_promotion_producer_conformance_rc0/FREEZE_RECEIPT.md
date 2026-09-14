# Freeze Receipt — Contract C 2.0 Promotion Producer Conformance RC0

Freeze order: exact CAL base -> exact prior materializer -> preregistration -> evaluator -> this receipt -> workflow execution.

Exact CAL base: `a902621e8baea3063dddd7f92ba975aade305464`.

Exact Apparatus promotion subject: `b42c827acb0a9fe65353354d709add0e27bab307`.

Pre-execution experiment head after evaluator creation: `380f11bc0aabeb41ebe844aa043f45e17d7e9e89`.

Frozen experiment blobs:

- `PREREGISTRATION.md`: `1a4cfec752ac4180308f08f19f4aa822653b7b6f`;
- `materialize.py`: `f9b22abff561081fb22ade8d5d7227dbdb870d72`;
- `evaluate.py`: `a3a6073645819cdb8d58fbbd55a3213c2eff780e`.

The materializer blob is byte-identical to the materializer used in the prior successful RC2 producer-conformance gate. It is not a successor producer implementation.

The evaluator is permitted to compare that unchanged CAL projection against both the production C2 adapter and the exact frozen RC2 reference copied inside the Apparatus promotion subject. It is not permitted to modify CAL semantic output, `compose()`, the materializer, or Contract C.

Any post-freeze change to one of the three experiment blobs above requires a successor experiment identity and must not be scored under this receipt.
