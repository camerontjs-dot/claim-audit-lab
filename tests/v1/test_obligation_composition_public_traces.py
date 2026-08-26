"""Public-fixture compatibility checks for the relation-preserving shadow.

These tests deliberately use only trace fixtures committed to the public repository.
They do not reconstruct eligibility, semantic validity, or aperture that was never
recorded.  The goal is narrower: prove that the richer evidence-state projection can
consume real stored CAL traces without rerunning inference or mutating production data.
"""

from __future__ import annotations

from pathlib import Path

from claim_audit_lab.v1.evidence_state import (
    project_evidence_state,
    with_derived_channel_probabilities,
)
from claim_audit_lab.v1.models import AuditTrace

_FIXTURES = Path(__file__).resolve().parent / "fixtures" / "traces"


def _public_traces() -> list[AuditTrace]:
    paths = sorted(_FIXTURES.rglob("*.json"))
    assert len(paths) == 30, "fixture inventory changed; review the research compatibility gate"
    return [AuditTrace.model_validate_json(path.read_text(encoding="utf-8")) for path in paths]


def test_f01_all_public_trace_fixtures_project_to_two_channel_state() -> None:
    original = _public_traces()
    before = tuple(trace.model_dump_json() for trace in original)

    enriched = with_derived_channel_probabilities(original)
    projections = tuple(project_evidence_state(trace) for trace in enriched)

    assert len(projections) == 30
    assert all(projection.state != "unmeasured" for projection in projections)
    assert tuple(trace.model_dump_json() for trace in original) == before


def test_f02_projection_preserves_admitted_passage_identity() -> None:
    enriched = with_derived_channel_probabilities(_public_traces())

    for trace in enriched:
        projection = project_evidence_state(trace)
        admitted = tuple(result.passage_id for result in trace.entailment)
        assert projection.admitted_passage_ids == admitted
        assert {item.passage_id for item in projection.support_candidates}.issubset(set(admitted))
        assert {item.passage_id for item in projection.refutation_candidates}.issubset(set(admitted))


def test_f03_projection_is_deterministic_over_public_trace_fixtures() -> None:
    enriched = with_derived_channel_probabilities(_public_traces())

    first = tuple(project_evidence_state(trace).model_dump_json() for trace in enriched)
    second = tuple(project_evidence_state(trace).model_dump_json() for trace in enriched)

    assert first == second
