"""Arm K child. Imports the frozen RC0 kernel lane without modifying it."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_RC0 = _REPO / "research" / "cal_v1_independent_judges_candidate_rc0_20261004"
sys.path.insert(0, str(_RC0))
sys.path.insert(1, str(_REPO / "src"))

from kernel_lane import judge  # noqa: E402


def main() -> int:
    raw = sys.stdin.buffer.read()
    sys.stdout.write(json.dumps(judge(raw), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
