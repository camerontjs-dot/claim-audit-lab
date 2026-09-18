from research.strict_comparison_gate1b_authority_rc0.apparatus import CLEAN, LOSSY, observe


def test_clean_sources_warrant() -> None:
    for case in CLEAN:
        observation = observe(case)
        assert observation.measurement_status == "CLAIMED", case.case_id
        assert observation.authority_status == "WARRANTED", case.case_id
        assert observation.authority is not None


def test_lossy_measurements_reproduce_then_authority_refuses() -> None:
    for case in LOSSY:
        observation = observe(case)
        assert observation.measurement_status == "CLAIMED", case.case_id
        assert observation.authority_status == "REFUSED", case.case_id
        assert observation.authority is None


def test_refusals_are_source_completion_or_authority_refusals() -> None:
    for case in LOSSY:
        observation = observe(case)
        assert observation.refusal_code in {
            "SOURCE_COMPLETION_FAILED",
            "SEMANTIC_AUTHORITY_UNRESOLVED",
        }, case.case_id


def test_replay_is_exact() -> None:
    first = tuple(observe(case) for case in CLEAN + LOSSY)
    second = tuple(observe(case) for case in CLEAN + LOSSY)
    assert first == second
