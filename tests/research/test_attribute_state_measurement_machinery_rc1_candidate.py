from research.attribute_state_measurement_machinery_rc1.candidate import INSTRUMENTS
from research.attribute_state_measurement_machinery_rc1.cohort import CASES
from research.attribute_state_measurement_machinery_rc1.evaluator import evaluate,metamorphic_failures


def test_replay_exact() -> None:
    for strategy in INSTRUMENTS.values():
        first=tuple(strategy(case.text) for case in CASES)
        second=tuple(strategy(case.text) for case in CASES)
        assert first==second


def test_at_least_one_path_qualifies() -> None:
    reports={name:evaluate(strategy) for name,strategy in INSTRUMENTS.items()}
    assert [name for name,report in reports.items() if report.qualifiable],reports


def test_qualifiable_paths_pass_metamorphics() -> None:
    reports={name:evaluate(strategy) for name,strategy in INSTRUMENTS.items()}
    for name,report in reports.items():
        if report.qualifiable:
            assert metamorphic_failures(INSTRUMENTS[name])==(),name
