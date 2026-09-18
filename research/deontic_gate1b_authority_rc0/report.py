"""Print deontic Gate-1B RC0 candidate observations."""

from __future__ import annotations

import json

from .candidate import complete_and_warrant_deontic
from .cohort import CLEAN
from .evaluator import MUTATIONS, observe_clean, observe_mutation


def main() -> None:
    rows = []
    for case in CLEAN:
        observed = observe_clean(case, complete_and_warrant_deontic)
        rows.append(
            {
                "case_id": case.case_id,
                "kind": "clean",
                "text": case.text,
                "authority_status": observed.authority_status,
            }
        )
    for case in MUTATIONS:
        observed = observe_mutation(case, complete_and_warrant_deontic)
        rows.append(
            {
                "case_id": case.case_id,
                "kind": "mutated_measurement",
                "source_case_id": case.source_case_id,
                "authority_status": observed.authority_status,
            }
        )
    print(json.dumps(rows, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
