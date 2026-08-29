"""Frozen acceptance entry point for the RC1 research-only sidecar."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EVALUATOR = ROOT / "docs" / "research" / "rc1_receipt_replay_evaluator.py"


def test_rc1_bounded_receipt_replay_gate() -> None:
    completed = subprocess.run(
        [sys.executable, str(EVALUATOR), "--json"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["acceptance"] is True
    assert payload["candidate"]["all_pass"] is True
    assert payload["candidate"]["passed_count"] == 10
    assert payload["weak_control"]["all_pass"] is False
    assert payload["weak_control"]["failed_gates"]
