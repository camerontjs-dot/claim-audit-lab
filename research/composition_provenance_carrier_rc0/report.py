from __future__ import annotations

import json

from .apparatus import CASES, mutation_failures, verify_receipt
from .candidate import bind_composition


def main() -> None:
    rows = []
    for request in CASES:
        receipt = bind_composition(request)
        rows.append(
            {
                "module_id": request.module_id,
                "relation": request.relation.value,
                "receipt_id": receipt.receipt_id,
                "verified": verify_receipt(receipt, request),
            }
        )
    print(
        json.dumps(
            {
                "cases": rows,
                "mutation_failures": mutation_failures(bind_composition),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
