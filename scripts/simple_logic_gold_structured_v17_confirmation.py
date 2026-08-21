"""E3 structured confirmation of the cal-rules-v1.7.0 landing (authorized 2026-07-16).

Runs the frozen Simple Logic Gold structured suite through the *current landed
package* (A1 guard + A4 negation-consistency) and preserves the result beside —
never over — the below-target run-01 baseline. Expected per
``plans/adr-v1-slg09-negation-consistency.md``: all comparable layers green.
"""

from __future__ import annotations

import json
from pathlib import Path

from scripts.simple_logic_gold_structured_lane import (
    _write_absent_or_identical,
    load_structured_inputs,
    run_structured_suite,
    suite_is_green,
)
from scripts.simple_logic_gold_structured_real_run import canonical_output_dir


def confirmation_output_dir() -> Path:
    """Return the v1.7.0 confirmation directory (distinct from the run-01 baseline)."""
    return canonical_output_dir().parent / "e3-structured-direct-v1.7.0-confirmation"


def main() -> None:
    from claim_audit_lab.v1.runner import run_default_explicit_claim_audit

    baseline_dir = canonical_output_dir()
    output_dir = confirmation_output_dir()
    inputs = load_structured_inputs(
        baseline_dir.parent / "frozen-gold.json",
        baseline_dir / "explicit-structure-v0.1.yaml",
        baseline_dir / "wording-variants-v0.1.yaml",
    )
    suite = run_structured_suite(inputs, run_default_explicit_claim_audit)
    _write_absent_or_identical(output_dir / "structured-direct-run-01.json", suite)
    green = suite_is_green(suite)
    print(json.dumps({"green": green, "out": str(output_dir)}, sort_keys=True))
    if not green:
        raise SystemExit("v1.7.0 structured confirmation below target; stop for planner review")


if __name__ == "__main__":
    main()
