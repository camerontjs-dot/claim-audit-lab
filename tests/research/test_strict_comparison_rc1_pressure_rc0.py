from claim_audit_lab.cal_v1_candidate.models import Conclusion

from research.strict_comparison_rc1_pressure_rc0.apparatus import CASES, execute, unsafe_cases


def test_positive_control_still_decides() -> None:
    result = execute(CASES[0])
    assert result.conclusion is Conclusion.SUPPORTED


def test_all_modifier_pressure_cases_fail_closed() -> None:
    assert unsafe_cases() == ()


def test_pressure_replay_is_deterministic() -> None:
    first = tuple(execute(case) for case in CASES)
    second = tuple(execute(case) for case in CASES)
    assert first == second
