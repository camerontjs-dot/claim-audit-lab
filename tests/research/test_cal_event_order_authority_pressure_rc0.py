from pathlib import Path

import pytest

from research.cal_event_order_authority_pressure_rc0.pressure import execute


@pytest.mark.skip(reason="executed by dedicated workflow with frozen dependency checkouts")
def test_pressure_placeholder() -> None:
    # The dedicated workflow supplies exact frozen RC7F-C and RC8J checkouts.
    execute(
        repo_root=Path("."),
        event_root=Path("_deps/event"),
        rc8j_root=Path("_deps/rc8j"),
    )
