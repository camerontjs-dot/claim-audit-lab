from __future__ import annotations

import json

from .apparatus import CASES
from .candidate import compose_applicability


def main() -> None:
    rows = []
    for case in CASES:
        rows.append(
            {
                "case_id": case.case_id,
                "expected": case.expected.value,
                "observed": compose_applicability(
                    case.norm,
                    case.membership,
                    case.query,
                ).value,
            }
        )
    print(json.dumps(rows, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
