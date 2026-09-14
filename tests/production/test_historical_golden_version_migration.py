from __future__ import annotations

import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
GOLDEN_ROOT = PROJECT_ROOT / "tests" / "v1" / "fixtures" / "traces"
PROTECTED_MAIN_SHA = "32275a239b68af383a56bca843e28cbc1e343976"


def test_historical_goldens_only_change_the_distribution_version() -> None:
    goldens = sorted(GOLDEN_ROOT.rglob("*.json"))
    assert len(goldens) == 30

    for path in goldens:
        relative = path.relative_to(PROJECT_ROOT).as_posix()
        baseline = subprocess.run(
            ["git", "show", f"{PROTECTED_MAIN_SHA}:{relative}"],
            check=True,
            capture_output=True,
        ).stdout
        assert b'"0.5.0"' in baseline
        assert path.read_bytes() == baseline.replace(b'"0.5.0"', b'"0.6.0"')
