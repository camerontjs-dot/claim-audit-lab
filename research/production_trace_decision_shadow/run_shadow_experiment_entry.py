"""Bootstrap the preregistered shadow runner with truthful fixture-module loading.

The frozen E2E fixture defines dataclasses. Python 3.11 dataclass processing
requires the dynamically loaded module to be present in ``sys.modules`` while
its class bodies execute. This wrapper changes only that import mechanic and
then delegates to the preregistered orchestration unchanged.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

from research.production_trace_decision_shadow import run_shadow_experiment as shadow


def _load_fixture_module(project: Path) -> ModuleType:
    tests_path = project / "tests"
    if str(tests_path) not in sys.path:
        sys.path.insert(0, str(tests_path))
    path = project / shadow.CORPUS_PATH
    spec = importlib.util.spec_from_file_location("cal_shadow_frozen_e2e_cases", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load frozen diagnostic corpus module {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    shadow._load_fixture_module = _load_fixture_module
    return shadow.main()


if __name__ == "__main__":
    raise SystemExit(main())
