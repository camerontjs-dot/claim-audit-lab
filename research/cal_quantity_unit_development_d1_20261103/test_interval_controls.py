"""Exposed point/bound controls from direct arithmetic, not parser internals."""
from __future__ import annotations

import json
from candidate import analyze


def main() -> int:
    predicates = {
        "less than": lambda x, t: x < t,
        "more than": lambda x, t: x > t,
        "at most": lambda x, t: x <= t,
        "at least": lambda x, t: x >= t,
        "not less than": lambda x, t: x >= t,
        "not more than": lambda x, t: x <= t,
        "not": lambda x, t: x != t,
        "": lambda x, t: x == t,
    }
    failures = []
    count = 0
    for wording, predicate in predicates.items():
        for value in range(-3, 4):
            for threshold in range(-3, 4):
                claim = f"The margin was {wording} {threshold} percentage points."
                evidence = f"The margin was {value} percentage points."
                expected = "supports" if predicate(value, threshold) else "refutes"
                actual = analyze(claim, evidence)["relation"]
                count += 1
                if actual != expected:
                    failures.append({"claim": claim, "evidence": evidence, "expected": expected, "actual": actual})
    print(json.dumps({"evidence_class": "EXPOSED_ARITHMETIC_DEVELOPMENT_CONTROLS", "probes": count, "failures": failures, "passed": not failures}, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
