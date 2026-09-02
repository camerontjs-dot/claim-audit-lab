from .cohort import build_cases
from .evaluate import qualification


def test_qualification_falsifies_weak_controls() -> None:
    result = qualification()
    assert result["state"] == "QUALIFIED"
    assert all(v["unsafe_warranted_atoms"] > 0 for v in result["weak_controls"].values())


def test_mutation_axes_present() -> None:
    axes = {row["mutation_axis"] for row in build_cases()}
    assert "source_span" in axes
    assert "narrator_assertion_scope" in axes
    assert "comparison_direction" in axes
    assert "necessity_direction" in axes
    assert "unsupported_extra_modifier" in axes
    assert "out_of_jurisdiction_semantic_family" in axes
