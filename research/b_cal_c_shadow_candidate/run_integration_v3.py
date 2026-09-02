"""Apparatus-only successor to the preserved v2 validator-loading failure.

The v2 semantic candidate reached the immutable Contract-C validator import but
loaded that module without registering its name in ``sys.modules``. Because the
frozen validator uses postponed annotations, Pydantic could not resolve names
such as ``Literal`` through the dynamic module namespace.

This runner changes no candidate semantics. It preserves v2 unchanged, replaces
only its dynamic-module loader with the standard registered-module pattern, and
then executes v2's existing ``main`` function.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

import run_integration_v2 as predecessor


def _load_registered_module(path: Path, name: str) -> Any:
    """Load a frozen Python module with a resolvable annotation namespace."""
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop(name, None)
        raise
    return module


def main() -> int:
    predecessor._load_module = _load_registered_module
    return predecessor.main()


if __name__ == "__main__":
    raise SystemExit(main())
