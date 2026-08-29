"""Preregistered metamorphic acceptance checks for the production-trace shadow."""

from research.production_trace_decision_shadow.metamorphic_controls import run_controls


def test_all_preregistered_metamorphic_controls_pass() -> None:
    report = run_controls()
    failures = [item for item in report["results"] if not item["pass"]]
    assert report["n_controls"] == 6
    assert report["all_passed"], failures
