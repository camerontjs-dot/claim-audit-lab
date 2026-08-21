"""Focused no-inference tests for the Lane A scaled-corpus first-cell harness."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from claim_audit_lab.v1.config import load_default_audit_config
from scripts import slg_scaled_first_cell_run02 as first_cell_run02
from scripts import slg_scaled_rejected_control_run02 as rejected_run02
from scripts.slg_scaled_first_cell_prepare import (
    FACT_ID,
    FACT_TEXT,
    PASSAGE_IDS,
    TITLE,
    build_content_and_passages,
    split_candidate,
    verify_sha256_manifest,
)
from scripts.slg_scaled_first_cell_run import build_measurement_summary
from scripts.slg_scaled_rejected_control_run import (
    CANDIDATE_RAW_SHA256 as REJECTED_CANDIDATE_RAW_SHA256,
)
from scripts.slg_scaled_rejected_control_run import (
    REJECTION_RECEIPT_SHA256,
    build_quarantine_fields,
)
from scripts.slg_scaled_rejected_control_run02 import (
    build_quarantine_fields as build_run02_quarantine_fields,
)
from scripts.slg_scaled_rejected_control_run02 import (
    preload_default_models,
    require_offline_environment,
)


def _candidate_with_255_words() -> str:
    paragraphs = [" ".join(f"p{index}w{word}" for word in range(42)) for index in range(5)]
    paragraphs.append(" ".join(f"p6w{word}" for word in range(45)))
    return TITLE + "\n\n" + "\n\n".join(paragraphs) + "\n"


def test_split_candidate_requires_exact_shape_and_word_count() -> None:
    title, paragraphs = split_candidate(_candidate_with_255_words())
    assert title == TITLE
    assert len(paragraphs) == 6
    assert sum(len(paragraph.split()) for paragraph in paragraphs) == 255


def test_split_candidate_rejects_a_missing_paragraph() -> None:
    raw = _candidate_with_255_words().rsplit("\n\n", 1)[0] + "\n"
    with pytest.raises(ValueError, match="title plus six paragraphs"):
        split_candidate(raw)


def test_build_content_inserts_fact_after_third_filler_and_recomputes_offsets() -> None:
    paragraphs = [f"Filler paragraph {index}." for index in range(1, 7)]
    content, passages = build_content_and_passages(TITLE, paragraphs)

    assert [passage["passage_id"] for passage in passages] == list(PASSAGE_IDS)
    assert passages[3]["passage_id"] == FACT_ID
    assert passages[3]["text"] == FACT_TEXT
    for passage in passages:
        assert content[passage["char_start"] : passage["char_end"]] == passage["text"]
    assert content.endswith("\n")


def test_build_content_rejects_non_six_paragraph_input() -> None:
    with pytest.raises(ValueError, match="expected six filler paragraphs"):
        build_content_and_passages(TITLE, ["one", "two"])


def test_verify_sha256_manifest_uses_temporary_paths(tmp_path: Path) -> None:
    payload = tmp_path / "payload.txt"
    payload.write_text("fixture\n", encoding="utf-8")
    digest = hashlib.sha256(payload.read_bytes()).hexdigest()
    manifest = tmp_path / "SHA256SUMS"
    manifest.write_text(f"{digest}  payload.txt\n", encoding="utf-8")

    assert verify_sha256_manifest(tmp_path, manifest) == {"payload.txt": digest}


def test_verify_sha256_manifest_rejects_path_traversal(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside-first-cell.txt"
    outside.write_text("outside\n", encoding="utf-8")
    digest = hashlib.sha256(outside.read_bytes()).hexdigest()
    manifest = tmp_path / "SHA256SUMS"
    manifest.write_text(f"{digest}  ../{outside.name}\n", encoding="utf-8")

    with pytest.raises(ValueError, match="path escapes root"):
        verify_sha256_manifest(tmp_path, manifest)


def _baseline() -> dict[str, object]:
    return {
        "cal_support_verdict": "supported",
        "cal_observed_relation": "supports",
    }


def _trace(*, include_fact: bool = True, verdict: str = "supported") -> dict[str, object]:
    retrieval = (
        [{"passage_id": FACT_ID, "score": 0.91}, {"passage_id": "filler-p01", "score": 0.5}]
        if include_fact
        else [{"passage_id": "filler-p01", "score": 0.5}]
    )
    return {
        "retrieval": retrieval,
        "entailment": [{"passage_id": FACT_ID, "label": "entail", "score": 0.99, "raw_logits": []}],
        "support_signal": {
            "contributing_passage_id": FACT_ID if include_fact else "filler-p01",
            "max_entailment_score": 0.99,
        },
        "verdict": {
            "support_verdict": verdict,
            "support_verdict_reason": None,
            "audit_flags": [],
        },
        "rules_fired": [{"rule_id": "B5_degree", "reason": "fixture"}],
    }


def test_measurement_summary_classifies_a_fully_stable_cell() -> None:
    summary = build_measurement_summary(_trace(), _baseline(), retrieval_floor=0.40)  # type: ignore[arg-type]
    assert summary["primary"] == {
        "verdict_stable_vs_preserved_t1": True,
        "fact_retrieved": True,
        "fact_at_or_above_floor": True,
        "fact_is_contributing_passage": True,
        "t2_verdict_supported": True,
        "classification": "stable",
        "failure_classes": [],
    }
    assert summary["secondary"]["fact_retrieval_rank"] == 1


def test_measurement_summary_reports_fact_loss_and_verdict_flip_separately() -> None:
    summary = build_measurement_summary(  # type: ignore[arg-type]
        _trace(include_fact=False, verdict="not_checkable"),
        _baseline(),
        retrieval_floor=0.40,
    )
    assert summary["primary"]["classification"] == "first_cell_failure"
    assert summary["primary"]["failure_classes"] == [
        "fact_outside_top_k",
        "fact_not_contributing",
        "verdict_flip",
    ]
    assert summary["secondary"]["fact_retrieval_rank"] is None


def test_rejected_control_quarantine_survives_a_stable_downstream_result() -> None:
    screen = {
        "reasons": ["banned outcome verb morphology hit"],
        "banned_outcome_verb_hits": {"return": ["returned"]},
    }
    result = {
        "diagnostic_comparison": {"primary": {"classification": "stable"}},
        **build_quarantine_fields(screen),
    }

    assert result["input_admissibility"] == "rejected"
    assert result["authority"] == "invalid-input diagnostic only"
    assert result["included_in_lane_a_results"] is False
    assert result["candidate_raw_sha256"] == "sha256:" + REJECTED_CANDIDATE_RAW_SHA256
    assert result["rejection_receipt_sha256"] == "sha256:" + REJECTION_RECEIPT_SHA256
    assert result["rejection_reasons"] == ["banned outcome verb morphology hit"]
    assert result["rejection_hits"] == {"return": ["returned"]}
    assert "cannot rehabilitate" in result["interpretation_rule"]


def test_run02_offline_contract_requires_both_flags() -> None:
    with pytest.raises(ValueError, match="TRANSFORMERS_OFFLINE=1"):
        require_offline_environment({"HF_HUB_OFFLINE": "1"})

    assert require_offline_environment({"HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1"}) == {
        "HF_HUB_OFFLINE": "1",
        "TRANSFORMERS_OFFLINE": "1",
    }


def test_run02_model_preflight_loads_exact_revisions_without_cal_inference() -> None:
    config = load_default_audit_config()
    calls: list[tuple[str, str, str]] = []

    def retriever_loader(model_id: str, revision: str) -> object:
        calls.append(("retriever", model_id, revision))
        return object()

    def entailer_loader(model_id: str, revision: str) -> object:
        calls.append(("entailer", model_id, revision))
        return object()

    receipt = preload_default_models(
        config,
        retriever_loader=retriever_loader,
        entailer_loader=entailer_loader,
    )

    assert calls == [
        ("retriever", config.retriever.model_id, config.retriever.hf_revision_sha),
        ("entailer", config.entailer.model_id, config.entailer.hf_revision_sha),
    ]
    assert receipt["status"] == "loaded_from_local_cache_before_attempt_start"
    assert receipt["cal_inference_performed"] is False


def test_run02_quarantine_preserves_every_terminal_rejection_reason() -> None:
    screen = {
        "body_word_count": 197,
        "body_word_count_ok": False,
        "forbidden_subject_hits": [],
        "banned_outcome_or_derivation_hits": ["storage"],
        "exact_or_normalized_proposition_hits": [],
        "reasons": [
            "body word count outside contract",
            "banned outcome verb derivation hit",
        ],
    }

    quarantine = build_run02_quarantine_fields(screen)

    assert quarantine["input_admissibility"] == "rejected"
    assert quarantine["included_in_lane_a_results"] is False
    assert quarantine["rejection_evidence"] == screen
    assert "cannot rehabilitate" in quarantine["interpretation_rule"]


def test_run02_preflight_failure_leaves_output_absent_and_skips_audit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    audit_called = False

    def stop_preflight(*args: object, **kwargs: object) -> None:
        raise RuntimeError("preflight stopped")

    def forbidden_audit(*args: object, **kwargs: object) -> None:
        nonlocal audit_called
        audit_called = True
        raise AssertionError("CAL audit must not run after a preflight failure")

    monkeypatch.setattr(rejected_run02, "preflight", stop_preflight)
    monkeypatch.setattr(rejected_run02, "run_default_audit", forbidden_audit)
    out = tmp_path / "generation-04-run-01"

    with pytest.raises(RuntimeError, match="preflight stopped"):
        rejected_run02.run_once(
            tmp_path / "candidate",
            tmp_path / "baseline.json",
            tmp_path / "preregistration.md",
            "preregistration-sha256",
            "runner-sha256",
            out,
        )

    assert not out.exists()
    assert audit_called is False


def test_lane_a_run02_preflight_failure_leaves_output_absent_and_skips_cal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    cal_called = False

    def stop_preflight(*args: object, **kwargs: object) -> None:
        raise RuntimeError("preflight stopped")

    def forbidden_cal(*args: object, **kwargs: object) -> None:
        nonlocal cal_called
        cal_called = True
        raise AssertionError("CAL must not run after first-cell preflight failure")

    monkeypatch.setattr(first_cell_run02, "preflight", stop_preflight)
    monkeypatch.setattr(first_cell_run02.base, "run_default_audit", forbidden_cal)
    out = tmp_path / "measured-run-01"

    with pytest.raises(RuntimeError, match="preflight stopped"):
        first_cell_run02.run_once(
            tmp_path / "packet",
            tmp_path / "preparation-receipt.json",
            "preparation-sha256",
            "manifest-sha256",
            tmp_path / "frozen-preregistration.md",
            tmp_path / "superseding-preregistration.md",
            "superseding-preregistration-sha256",
            "runner-sha256",
            tmp_path / "baseline.json",
            out,
        )

    assert not out.exists()
    assert cal_called is False
