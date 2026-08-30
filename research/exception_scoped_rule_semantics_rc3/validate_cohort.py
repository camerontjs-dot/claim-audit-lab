"""Validate the frozen RC3 cohort without executing any model or candidate mechanism."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

EXPECTED_SHA256 = "01b0d436ccf9ed812f9bb26d64f4ddd1a656e26175ee007f1fe9594a2a203785"
ROOT = Path(__file__).resolve().parent
PRIMARY_FAMILIES = (
    "explicit_opposite_exception",
    "bare_exception_exclusion",
    "separate_process_exception",
    "temporary_exception",
    "narrow_obligation_exemption",
    "nested_qualified_exception",
    "only_and_exclusion",
)
LABELS = ("entailment", "neutral", "contradiction")


def load_and_validate() -> dict:
    from build_cohort import build, canonical_bytes
    raw = canonical_bytes(build())
    actual = hashlib.sha256(raw).hexdigest()
    if actual != EXPECTED_SHA256:
        raise RuntimeError(f"cohort SHA256 mismatch: {actual}")

    data = json.loads(raw)
    cases = data["cases"]
    if len(cases) != 110:
        raise RuntimeError(f"expected 110 total cases, got {len(cases)}")
    ids = [case["case_id"] for case in cases]
    if len(ids) != len(set(ids)):
        raise RuntimeError("duplicate case IDs")
    if any(not case_id.startswith("XR3-") for case_id in ids):
        raise RuntimeError("all RC3 cases must use the XR3 namespace")

    primary = [case for case in cases if case["primary"]]
    if len(primary) != 84:
        raise RuntimeError(f"expected 84 primary cases, got {len(primary)}")
    if Counter(case["target"] for case in primary) != Counter(
        {"entailment": 28, "neutral": 28, "contradiction": 28}
    ):
        raise RuntimeError("primary label balance changed")

    for family in PRIMARY_FAMILIES:
        subset = [case for case in primary if case["family"] == family]
        if len(subset) != 12:
            raise RuntimeError(f"{family}: expected 12 primary cases")
        counts = Counter(case["target"] for case in subset)
        if counts != Counter({"entailment": 4, "neutral": 4, "contradiction": 4}):
            raise RuntimeError(f"{family}: label balance changed: {counts}")

    if any(case["target"] not in LABELS for case in primary):
        raise RuntimeError("all primary cases require a three-way target")
    if any(not case["semantic_rationale"].strip() for case in cases):
        raise RuntimeError("every case requires a semantic rationale")

    metamorphic = [case for case in cases if case["family"] == "metamorphic"]
    if len(metamorphic) != 20:
        raise RuntimeError(f"expected 20 metamorphic cases, got {len(metamorphic)}")

    ambiguous = [case for case in cases if case["family"] == "evaluator_ambiguous"]
    if len(ambiguous) != 6:
        raise RuntimeError(f"expected 6 ambiguous cases, got {len(ambiguous)}")
    if any(case["target"] is not None or case["primary"] for case in ambiguous):
        raise RuntimeError("ambiguous cases must be targetless and non-primary")

    by_id = {case["case_id"]: case for case in cases}
    pairs = data["mutation_pairs"]
    if len(pairs) != 10:
        raise RuntimeError(f"expected 10 mutation pairs, got {len(pairs)}")
    for pair in pairs:
        before = by_id[pair["before"]]
        after = by_id[pair["after"]]
        if before["target"] != pair["expected_before"]:
            raise RuntimeError(f"{pair['pair_id']} before target drift")
        if after["target"] != pair["expected_after"]:
            raise RuntimeError(f"{pair['pair_id']} after target drift")
        if before.get("mutation_pair_id") != pair["pair_id"]:
            raise RuntimeError(f"{pair['pair_id']} before linkage drift")
        if after.get("mutation_pair_id") != pair["pair_id"]:
            raise RuntimeError(f"{pair['pair_id']} after linkage drift")

    critical = Counter(
        case["critical_error_type"]
        for case in primary
        if case["critical_error_type"] is not None
    )
    required = {
        "exception_not_negation",
        "narrow_to_broad",
        "alternate_to_no_process",
        "temporary_to_permanent",
    }
    if not required <= set(critical):
        raise RuntimeError(f"missing critical error probes: {required - set(critical)}")

    return data


if __name__ == "__main__":
    data = load_and_validate()
    print(
        json.dumps(
            {
                "cohort_sha256": EXPECTED_SHA256,
                "total_cases": len(data["cases"]),
                "primary_cases": sum(case["primary"] for case in data["cases"]),
                "mutation_pairs": len(data["mutation_pairs"]),
                "evaluator_ambiguous": sum(
                    case["family"] == "evaluator_ambiguous" for case in data["cases"]
                ),
            },
            indent=2,
            sort_keys=True,
        )
    )
