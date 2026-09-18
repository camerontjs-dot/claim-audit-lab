"""Print deterministic comparison results for causal RC0 instruments."""

from __future__ import annotations

import json
from dataclasses import asdict

from .candidate import INSTRUMENTS
from .evaluator import evaluate, metamorphic_failures


def main() -> None:
    payload = {}
    for name, strategy in INSTRUMENTS.items():
        row = asdict(evaluate(strategy))
        row["metamorphic_failures"] = list(metamorphic_failures(strategy))
        payload[name] = row
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
