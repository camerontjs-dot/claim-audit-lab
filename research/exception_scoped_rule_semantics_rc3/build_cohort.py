"""Materialize the frozen RC3 cohort from auditable JSONL shards."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SHARDS = (
    "01_explicit_opposite_exception.jsonl",
    "02_bare_exception_exclusion.jsonl",
    "03_separate_process_exception.jsonl",
    "04_temporary_exception.jsonl",
    "05_narrow_obligation_exemption.jsonl",
    "06_nested_qualified_exception.jsonl",
    "07_only_and_exclusion.jsonl",
    "08_metamorphic.jsonl",
    "09_evaluator_ambiguous.jsonl",
)
EXPECTED_SHA256 = "01b0d436ccf9ed812f9bb26d64f4ddd1a656e26175ee007f1fe9594a2a203785"


def build() -> dict:
    data = json.loads((ROOT / "COHORT_META.json").read_text())
    cases: list[dict] = []
    for shard in SHARDS:
        for line in (ROOT / "cohort_cases" / shard).read_text().splitlines():
            if line.strip():
                cases.append(json.loads(line))
    data["cases"] = cases
    data["mutation_pairs"] = json.loads((ROOT / "MUTATION_PAIRS.json").read_text())
    return data


def canonical_bytes(data: dict) -> bytes:
    return (json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()


def frozen_sha256() -> str:
    return hashlib.sha256(canonical_bytes(build())).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data = build()
    raw = canonical_bytes(data)
    actual = hashlib.sha256(raw).hexdigest()
    if actual != EXPECTED_SHA256:
        raise RuntimeError(f"cohort SHA256 mismatch: {actual}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(raw)
    print(json.dumps({"cohort_sha256": actual, "cases": len(data["cases"])}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
