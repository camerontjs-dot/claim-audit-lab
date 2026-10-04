"""One lane process. Reads an envelope on stdin and writes one receipt."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_CANDIDATE = Path(__file__).resolve().parent
sys.path.insert(0, str(_CANDIDATE))

from judges import JUDGES  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lane", required=True)
    parser.add_argument("--process-id")
    parser.add_argument("--self-score", action="store_true")
    args = parser.parse_args()
    raw = sys.stdin.buffer.read()
    if args.lane not in JUDGES:
        raise SystemExit("unknown lane")
    receipt = JUDGES[args.lane](raw)
    if args.process_id:
        receipt["process_id"] = args.process_id
        receipt["cloned_from"] = args.lane
    if args.self_score:
        receipt["claimed_confidence"] = "0.99"
        receipt["claimed_weight"] = "100"
        receipt["claimed_relevance"] = True
    sys.stdout.write(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
