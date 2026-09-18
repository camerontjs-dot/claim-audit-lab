from __future__ import annotations

import json

from .apparatus import CASES, verify_receipt
from .candidate import compose_timed_state


def main() -> None:
    rows = []
    for case in CASES:
        receipt = compose_timed_state(case.state, case.scope, case.query)
        rows.append(
            {
                "case_id": case.case_id,
                "relation": receipt.relation.value,
                "verified": verify_receipt(
                    receipt,
                    case.state,
                    case.scope,
                    case.query,
                ),
            }
        )
    print(json.dumps(rows, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
