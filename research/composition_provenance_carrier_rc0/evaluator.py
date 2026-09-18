"""Frozen evaluator for composition provenance carrier RC0."""

from __future__ import annotations

from .apparatus import WEAKS, failures


def weak_failures() -> dict[str, tuple[int, ...]]:
    return {name: failures(strategy) for name, strategy in WEAKS}
