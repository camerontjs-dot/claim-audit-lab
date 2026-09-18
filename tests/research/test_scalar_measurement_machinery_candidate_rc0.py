from research.scalar_measurement_machinery_rc0.candidate import INSTRUMENTS
from research.scalar_measurement_machinery_rc0.cohort import CASES
from research.scalar_measurement_machinery_rc0.evaluator import (
    evaluate,
    metamorphic_failures,
)


def test_instruments_replay_exactly() -> None:
    for strategy in INSTRUMENTS.values():
        first = tuple(strategy(case.text, case.target) for case in CASES)
        second = tuple(strategy(case.text, case.target) for case in CASES)
        assert first == second


def test_at_least_one_path_is_qualifiable_for_gate1b() -> None:
    reports = {name: evaluate(strategy) for name, strategy in INSTRUMENTS.items()}
    assert [name for name, report in reports.items() if report.qualifiable], reports


def test_qualifiable_paths_pass_metamorphic_controls() -> None:
    reports = {name: evaluate(strategy) for name, strategy in INSTRUMENTS.items()}
    for name, report in reports.items():
        if report.qualifiable:
            assert metamorphic_failures(INSTRUMENTS[name]) == (), name
