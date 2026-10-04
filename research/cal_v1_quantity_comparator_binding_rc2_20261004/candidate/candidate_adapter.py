"""Frozen-evaluator adapter. The contract imports analyze()."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from quantity_binding import analyze  # noqa: E402

__all__ = ["analyze"]
