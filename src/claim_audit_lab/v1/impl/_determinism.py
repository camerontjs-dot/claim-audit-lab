"""CPU-only determinism baseline for the v1 inference layers.

The byte-identical-trace property (DECISIONS.md § 2026-06-21 § 9) has to survive
*real* model inference, not just the Phase-1 stubs. On CPU, two run-to-run
variance sources matter: multi-threaded reduction ordering and any seeded
initialization. Pinning torch to a single thread and a fixed manual seed removes
both, which is what lets the Phase-2 end-to-end byte-identity test hold over the
pinned MiniLM + DeBERTa revisions.

:func:`enforce_cpu_determinism` is called at module load by
:mod:`claim_audit_lab.v1.impl.retriever` and
:mod:`claim_audit_lab.v1.impl.entailer`, so the baseline is in force before any
inference runs. CPU only — no CUDA/MPS paths are taken. See the ADR in
DECISIONS.md § Phase 2 Unit 1.
"""

from __future__ import annotations

import torch

#: v1 determinism baseline — single-threaded CPU, fixed seed (ADR-locked).
NUM_THREADS = 1
MANUAL_SEED = 0


def enforce_cpu_determinism() -> None:
    """Pin torch to single-threaded CPU execution with a fixed manual seed."""
    torch.set_num_threads(NUM_THREADS)
    torch.manual_seed(MANUAL_SEED)


__all__ = ["MANUAL_SEED", "NUM_THREADS", "enforce_cpu_determinism"]
