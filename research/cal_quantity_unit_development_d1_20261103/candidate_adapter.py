"""Exact local development entry point; no evaluator or expected-label imports."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

_path = Path(__file__).with_name("candidate.py")
_spec = importlib.util.spec_from_file_location("cal_quantity_unit_development_d1", _path)
assert _spec is not None and _spec.loader is not None
_candidate = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _candidate
_spec.loader.exec_module(_candidate)
analyze = _candidate.analyze

__all__ = ["analyze"]
