from __future__ import annotations

import json

from .apparatus import CASES, oracle
from .candidate import compose_change


def main() -> None:
    rows = []
    for case in CASES:
        rows.append(
            {
                "case_id": case.case_id,
                "expected": oracle(case).value,
                "observed": compose_change(case.left, case.right, case.query).value,
            }
        )
    print(json.dumps(rows, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
