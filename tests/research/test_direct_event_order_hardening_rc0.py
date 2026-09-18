from research.direct_event_order_hardening_rc0.apparatus import CASES, Bucket, failures, observe


def test_frozen_instrument_replays_exactly() -> None:
    assert tuple(observe(case.text) for case in CASES) == tuple(
        observe(case.text) for case in CASES
    )


def test_must_retain_has_no_regression() -> None:
    assert failures()["must_retain_failures"] == ()


def test_claimed_diagnostics_are_exact() -> None:
    assert failures()["diagnostic_wrong_claims"] == ()


def test_scope_modifier_and_composition_traps_fail_closed() -> None:
    assert failures()["fail_closed_unsafe"] == ()


def test_all_buckets_are_present() -> None:
    assert {case.bucket for case in CASES} == {
        Bucket.MUST_RETAIN,
        Bucket.DIAGNOSTIC,
        Bucket.FAIL_CLOSED,
    }
