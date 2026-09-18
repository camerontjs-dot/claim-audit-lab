"""Print direct-event-order Gate-1B RC1 candidate observations."""

from __future__ import annotations

import json

from .candidate import complete_and_warrant_event_order
from .cohort import CASES
from .evaluator import observe


def main() -> None:
    rows = []
    for case in CASES:
        observation = observe(case, complete_and_warrant_event_order)
        rows.append(
            {
                "case_id": case.case_id,
                "text": case.text,
                "expected": case.expected.value,
                "measurement_status": observation.measurement_status,
                "authority_status": observation.authority_status,
            }
        )
    print(json.dumps(rows, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
