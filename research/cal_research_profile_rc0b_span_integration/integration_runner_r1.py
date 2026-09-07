"""Mechanical path-resolution wrapper for the frozen RC0B evaluator.

Run 34133179604 stopped before candidate execution because the exact Contract-B
validator was invoked from its own checkout while receiving a repository-relative
bundle path. This wrapper changes no candidate, cohort, expectation, resolver, or
semantic operation. It resolves CLI filesystem paths before calling the frozen
RC0B evaluator unchanged.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import integration_runner as frozen


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rc7fb1-root", type=Path, required=True)
    parser.add_argument("--rc8j-root", type=Path, required=True)
    parser.add_argument("--apparatus-b", type=Path, required=True)
    parser.add_argument("--apparatus-c", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    args.rc7fb1_root = args.rc7fb1_root.resolve()
    args.rc8j_root = args.rc8j_root.resolve()
    args.apparatus_b = args.apparatus_b.resolve()
    args.apparatus_c = args.apparatus_c.resolve()
    args.out = args.out.resolve()

    result = frozen.execute(args)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 2 if result.get("research_disposition") == "APPARATUS_FAILURE" else 0


if __name__ == "__main__":
    raise SystemExit(main())
