"""Print the frozen RC7F-B1 hardening observations before acceptance."""

from __future__ import annotations

import json
from dataclasses import asdict

from .apparatus import CASES, failures, observe


def main() -> None:
    observations = []
    for case in CASES:
        observed = observe(case.text)
        observations.append(
            {
                "case_id": case.case_id,
                "bucket": case.bucket.value,
                "text": case.text,
                "expected": asdict(case.expected) if case.expected is not None else None,
                "observed": asdict(observed) if observed is not None else None,
            }
        )
    print(
        json.dumps(
            {
                "failures": failures(),
                "observations": observations,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
