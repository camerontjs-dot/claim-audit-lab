from __future__ import annotations

import json

from .candidate import complete_and_warrant_strict_rc2
from .evaluator import CASES, observe


def main() -> None:
    rows = []
    for case in CASES:
        measurement, authority = observe(case, complete_and_warrant_strict_rc2)
        rows.append(
            {
                "case_id": case.case_id,
                "text": case.text,
                "expected": "WARRANTED" if case.should_warrant else "REFUSED",
                "measurement": measurement,
                "authority": authority,
            }
        )
    print(json.dumps(rows, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
