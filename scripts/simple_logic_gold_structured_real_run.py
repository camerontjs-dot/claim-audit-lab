"""Authorized-only entry point for the E3 structured direct real-model suite."""

from __future__ import annotations

from pathlib import Path

from scripts.simple_logic_gold_structured_lane import (
    _write_absent_or_identical,
    load_structured_inputs,
    run_structured_suite,
    suite_is_green,
)


def canonical_output_dir() -> Path:
    """Return the outer CAL project's only authorized E3 result directory."""
    return (
        Path(__file__).resolve().parents[2]
        / "outputs/simple-logic-gold/v0.1-frozen-rev01-2026-07-15/e3-structured-direct-v0.1"
    )


def main() -> None:
    """Run once, preserve the suite, then report whether it met the preregistration."""
    from claim_audit_lab.v1.runner import run_default_explicit_claim_audit

    output_dir = canonical_output_dir()
    inputs = load_structured_inputs(
        output_dir.parent / "frozen-gold.json",
        output_dir / "explicit-structure-v0.1.yaml",
        output_dir / "wording-variants-v0.1.yaml",
    )
    suite = run_structured_suite(inputs, run_default_explicit_claim_audit)
    _write_absent_or_identical(output_dir / "structured-direct-run-01.json", suite)
    if not suite_is_green(suite):
        raise SystemExit("structured E3 suite preserved below target; stop for planner review")


if __name__ == "__main__":
    main()
