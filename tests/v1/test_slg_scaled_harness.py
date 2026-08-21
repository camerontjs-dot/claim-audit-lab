"""No-inference safety tests for the reusable Lane A scaled-corpus harness."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import slg_scaled_run
from scripts.slg_scaled_admit import write_once_or_same
from scripts.slg_scaled_prepare import build_content_and_passages


def test_admission_artifacts_are_write_once_but_exact_repeats_are_idempotent(
    tmp_path: Path,
) -> None:
    path = tmp_path / "admission.json"
    write_once_or_same(path, {"admitted": True, "hash": "sha256:a"})
    first = path.read_bytes()
    write_once_or_same(path, {"hash": "sha256:a", "admitted": True})
    assert path.read_bytes() == first
    with pytest.raises(FileExistsError, match="admission history"):
        write_once_or_same(path, {"admitted": True, "hash": "sha256:b"})


def test_scaled_construction_keeps_facts_separate_clustered_passages_cited_to_all_atoms() -> None:
    paragraphs = [f"Filler {index}" for index in range(1, 7)]
    facts = [
        {"fact_id": "fact-a", "text": "Fact A."},
        {"fact_id": "fact-b", "text": "Fact B."},
    ]
    content, passages = build_content_and_passages(
        "Title", paragraphs, facts, ["atom-a", "atom-b"], 3, "filler"
    )
    assert [passage["passage_id"] for passage in passages] == [
        "filler-p01",
        "filler-p02",
        "filler-p03",
        "fact-a",
        "fact-b",
        "filler-p04",
        "filler-p05",
        "filler-p06",
    ]
    assert all(passage["used_for_claims"] == ["atom-a", "atom-b"] for passage in passages)
    assert all(content[p["char_start"] : p["char_end"]] == p["text"] for p in passages)


def test_summary_reports_fact_loss_and_verdict_flip_independently() -> None:
    trace = {
        "retrieval": [{"passage_id": "src/fact-a", "score": 0.39}],
        "entailment": [],
        "support_signal": {
            "contributing_passage_id": "src/filler-p01",
            "max_entailment_score": 0.1,
        },
        "verdict": {
            "support_verdict": "not_checkable",
            "support_verdict_reason": "no_entail_signal",
            "audit_flags": [],
        },
        "rules_fired": [],
    }
    baseline = {"cal_support_verdict": "supported", "cal_observed_relation": "supports"}
    summary = slg_scaled_run.build_measurement_summary(
        trace, baseline, ["fact-a", "fact-b"], retrieval_floor=0.40
    )
    assert summary["primary"]["failure_classes"] == [
        "fact_outside_top_k",
        "fact_below_floor",
        "fact_not_contributing",
        "no_entail_signal",
        "verdict_flip",
    ]


def test_summary_accepts_preserved_no_entail_signal_for_insufficient_baseline() -> None:
    trace = {
        "retrieval": [{"passage_id": "src/fact-a", "score": 0.80}],
        "entailment": [{"passage_id": "src/fact-a", "label": "neutral", "score": 0.99}],
        "support_signal": {
            "contributing_passage_id": "src/fact-a",
            "max_entailment_score": 0.99,
        },
        "verdict": {
            "support_verdict": "not_checkable",
            "support_verdict_reason": "no_entail_signal",
            "audit_flags": [],
        },
        "rules_fired": [],
    }
    baseline = {
        "cal_support_verdict": "not_checkable",
        "cal_observed_relation": "insufficient",
        "trace": {"verdict": {"support_verdict_reason": "no_entail_signal"}},
    }

    summary = slg_scaled_run.build_measurement_summary(
        trace, baseline, ["fact-a"], retrieval_floor=0.40
    )

    assert summary["primary"]["classification"] == "stable"
    assert summary["primary"]["failure_classes"] == []
    assert summary["comparison"]["support_verdict_reason_stable"] is True


def test_summary_reports_support_verdict_reason_drift() -> None:
    trace = {
        "retrieval": [{"passage_id": "src/fact-a", "score": 0.80}],
        "entailment": [{"passage_id": "src/fact-a", "label": "neutral", "score": 0.99}],
        "support_signal": {
            "contributing_passage_id": "src/fact-a",
            "max_entailment_score": 0.99,
        },
        "verdict": {
            "support_verdict": "not_checkable",
            "support_verdict_reason": "missing_needed",
            "audit_flags": [],
        },
        "rules_fired": [],
    }
    baseline = {
        "cal_support_verdict": "not_checkable",
        "cal_observed_relation": "insufficient",
        "trace": {"verdict": {"support_verdict_reason": "no_entail_signal"}},
    }

    summary = slg_scaled_run.build_measurement_summary(
        trace, baseline, ["fact-a"], retrieval_floor=0.40
    )

    assert summary["primary"]["classification"] == "cell_failure"
    assert summary["primary"]["failure_classes"] == ["support_verdict_reason_flip"]
    assert summary["comparison"]["support_verdict_reason_stable"] is False


def test_preflight_failure_leaves_output_absent_and_never_calls_cal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    called = False

    def stop(*args: object, **kwargs: object) -> None:
        raise RuntimeError("preflight stopped")

    def forbidden(*args: object, **kwargs: object) -> None:
        nonlocal called
        called = True
        raise AssertionError("CAL must not run")

    monkeypatch.setattr(slg_scaled_run, "preflight", stop)
    monkeypatch.setattr(slg_scaled_run, "run_default_audit", forbidden)
    out = tmp_path / "measured-run-01"
    with pytest.raises(RuntimeError, match="preflight stopped"):
        slg_scaled_run.run_once(*([tmp_path] * 10), out)
    assert not out.exists()
    assert called is False


def test_failed_started_attempt_is_preserved_and_rerun_is_blocked(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    real_preflight = slg_scaled_run.preflight
    out = tmp_path / "measured-run-01"
    request = type("Request", (), {"claim_id": "atom-a"})()
    baseline = {"cal_support_verdict": "supported", "cal_observed_relation": "supports"}
    preparation = {
        "world_id": "SLG-X",
        "tier": "T2",
        "construction": {"fact_ids": ["fact-a"]},
    }
    config = type("Config", (), {"top_k": 5, "retrieval_floor": 0.4})()
    readiness = {"cal_inference_performed": False}

    monkeypatch.setattr(
        slg_scaled_run,
        "preflight",
        lambda *args: (request, baseline, preparation, config, readiness),
    )
    monkeypatch.setattr(
        slg_scaled_run,
        "run_default_audit",
        lambda request: (_ for _ in ()).throw(RuntimeError("model failed")),
    )
    with pytest.raises(RuntimeError, match="model failed"):
        slg_scaled_run.run_once(*([tmp_path] * 10), out)
    assert json.loads((out / "attempt-start.json").read_text())["status"] == "inference_starting"
    assert json.loads((out / "attempt-error.json").read_text())["rerun_allowed"] is False
    assert (out / "SHA256SUMS").is_file()

    monkeypatch.setattr(slg_scaled_run, "preflight", real_preflight)
    with pytest.raises(FileExistsError, match="rerun forbidden"):
        slg_scaled_run.preflight(
            tmp_path,
            "x",
            "x",
            tmp_path,
            "x",
            "x",
            "x",
            tmp_path,
            "x",
            "atom-a",
            out,
        )
