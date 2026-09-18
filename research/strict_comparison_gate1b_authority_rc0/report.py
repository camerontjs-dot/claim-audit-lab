"""Print all strict Gate-1B observations."""

from __future__ import annotations

import json

from .apparatus import CASES, observe


def main() -> None:
    rows = []
    for case in CASES:
        observation = observe(case)
        rows.append(
            {
                "case_id": case.case_id,
                "text": case.text,
                "should_warrant": case.should_warrant,
                "measurement_status": observation.measurement_status,
                "authority_status": observation.authority_status,
                "refusal_code": observation.refusal_code,
            }
        )
    print(json.dumps(rows, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
