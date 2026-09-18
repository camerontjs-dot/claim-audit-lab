from research.strict_comparison_hardening_rc0.apparatus import CASES, Bucket, failures, observe


def test_frozen_comparator_replays_deterministically() -> None:
    first = tuple(observe(case.text) for case in CASES)
    second = tuple(observe(case.text) for case in CASES)
    assert first == second


def test_must_retain_has_no_regression() -> None:
    assert failures()["must_retain_failures"] == ()


def test_claimed_diagnostics_are_exact() -> None:
    assert failures()["diagnostic_wrong_claims"] == ()


def test_modifier_and_scope_traps_fail_closed() -> None:
    assert failures()["fail_closed_unsafe"] == ()


def test_corpus_contains_all_three_buckets() -> None:
    assert {case.bucket for case in CASES} == {
        Bucket.MUST_RETAIN,
        Bucket.DIAGNOSTIC,
        Bucket.FAIL_CLOSED,
    }
