from __future__ import annotations

import json

from .candidate import complete_and_warrant_typed_binary
from .evaluator import failures


def main() -> None:
    print(json.dumps({"failures": failures(complete_and_warrant_typed_binary)}, indent=2))


if __name__ == "__main__":
    main()
