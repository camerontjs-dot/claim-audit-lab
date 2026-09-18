from __future__ import annotations

import json

from .apparatus import CASES
from .candidate import compose_occurrence_order


def main() -> None:
    rows = []
    for case in CASES:
        observed = compose_occurrence_order(
            case.first_occurrence,
            case.second_occurrence,
            case.order,
            case.query,
        )
        rows.append(
            {
                "case_id": case.case_id,
                "expected": case.expected.value,
                "observed": observed.value,
            }
        )
    print(json.dumps(rows, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
