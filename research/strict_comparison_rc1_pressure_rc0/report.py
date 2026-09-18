"""Print all RC1 strict-comparison pressure observations."""

from __future__ import annotations

import json

from .apparatus import CASES, row, unsafe_cases


def main() -> None:
    print(
        json.dumps(
            {
                "unsafe_cases": unsafe_cases(),
                "observations": [row(case) for case in CASES],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
