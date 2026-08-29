"""Acceptance entry point for CAL Epistemic Methodology RC1A."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_rc1a_frozen_apparatus(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    receipt = tmp_path / "rc1a-apparatus-receipt.json"
    subprocess.run(
        [
            sys.executable,
            str(root / "docs" / "research" / "rc1a_evaluator.py"),
            "--output",
            str(receipt),
        ],
        cwd=root,
        check=True,
    )
    assert receipt.is_file()
