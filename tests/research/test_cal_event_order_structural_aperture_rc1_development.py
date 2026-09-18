from research.cal_event_order_structural_aperture_rc1.development_controls import (
    failures,
)


def test_revealed_leaks_close_and_narrow_direct_positives_survive() -> None:
    assert failures() == ()
