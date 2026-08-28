# Contract C RC1 research code

This directory is research-only machinery for CAL PR #15. It is intentionally outside `src/` and does not alter the production audit path.

It contains:

- `projector.py`: a candidate C0 to C1 projector, validation, deterministic human report derivation, and a multi-proposition result-set envelope;
- `consumers.py`: deliberately plural research consumer probes used for field-family ablation;
- `independent_projector.py`: a mechanically isolated projector that imports neither CAL nor the producer projector.

The mechanically isolated projector is **not** claimed to be independently authored. An attempt to commission an isolated consumer through the available MainFrame Conduit surface found no active adapters. That limitation is preserved in `docs/research/contract-c-failed-attempts-rc1.md`.

No Contract-C version is assigned here. The names and shapes are experimental labels only.
