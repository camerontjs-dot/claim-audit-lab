from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

from contract_c_rc1_research.consumers import (
    CONSUMERS,
    InsufficientPackage,
    assessment_state_probe,
    investigation_probe,
    publication_probe,
    sop_conformance_probe,
)
from contract_c_rc1_research.independent_projector import (
    project_publication_review,
    render_compact_report,
)
from contract_c_rc1_research.projector import (
    build_result_set,
    project_production_trace,
    render_human_report,
    thin_projection,
    validate_package,
    validate_result_set,
    with_result_identity,
)

FIXTURES = Path(__file__).parent / "fixtures" / "contract_c_rc1"
CAL_SHA = "33a928db97316a3652d57df9cafb8ca240305233"


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _mutate(base: dict, dotted: str, value: object) -> dict:
    result = copy.deepcopy(base)
    cursor = result
    parts = dotted.split(".")
    for part in parts[:-1]:
        cursor = cursor[part]
    cursor[parts[-1]] = copy.deepcopy(value)
    return with_result_identity(result)


def _synthetic_base() -> dict:
    fixture = _load("semantic-state-matrix.json")
    return with_result_identity(fixture["base"])


def _surrogate_binding(trace: dict) -> dict[str, str]:
    # Metamorphic-only context. This is deliberately NOT claimed to be an actual
    # Contract-B bundle binding; exact lineage is tested separately as an unmet
    # production-trace requirement in the research record.
    raw = json.dumps(trace, sort_keys=True).encode()
    return {
        "contract_version": "fixture-surrogate",
        "bundle_id": "audit-trace-fixture-only",
        "bundle_sha256": "sha256:" + hashlib.sha256(raw).hexdigest(),
    }


def test_production_frozen_same_verdict_cases_preserve_different_residual_state() -> None:
    no_evidence = _load("c0-no-evidence.json")
    no_entail = _load("c0-no-entail.json")

    assert no_evidence["verdict"]["support_verdict"] == "not_checkable"
    assert no_entail["verdict"]["support_verdict"] == "not_checkable"
    assert no_evidence["verdict"]["support_verdict_reason"] == "no_evidence"
    assert no_entail["verdict"]["support_verdict_reason"] == "no_entail_signal"
    assert no_evidence["entailment"] == []
    assert no_entail["entailment"][0]["label"] == "neutral"


def test_telemetry_mutation_is_invariant_but_semantic_measurement_is_not() -> None:
    trace = _load("c0-no-entail.json")
    binding = _surrogate_binding(trace)
    original = project_production_trace(trace, contract_b_binding=binding, cal_code_sha=CAL_SHA)

    mutated = copy.deepcopy(trace)
    mutated["retrieval"][0]["score"] = 0.81
    mutated["entailment"][0]["raw_logits"] = [99.0, -40.0, 12.0]
    mutated["features"]["claim_token_count"] = 999
    mutated["rules_fired"][0]["reason"] = "debug prose changed"
    projected = project_production_trace(mutated, contract_b_binding=binding, cal_code_sha=CAL_SHA)
    assert projected == original

    semantic = copy.deepcopy(trace)
    semantic["support_signal"]["max_entailment_score"] = 0.31
    changed = project_production_trace(semantic, contract_b_binding=binding, cal_code_sha=CAL_SHA)
    assert changed != original
    assert changed["measurements"][-1]["score"] == 0.31


def test_reproducibility_identity_mutations_are_not_telemetry() -> None:
    trace = _load("c0-no-entail.json")
    binding = _surrogate_binding(trace)
    original = project_production_trace(trace, contract_b_binding=binding, cal_code_sha=CAL_SHA)

    config_changed = copy.deepcopy(trace)
    config_changed["audit_config_hash"] = "sha256:" + "d" * 64
    config_projected = project_production_trace(
        config_changed, contract_b_binding=binding, cal_code_sha=CAL_SHA
    )
    assert config_projected["result_id"] != original["result_id"]

    code_projected = project_production_trace(
        trace, contract_b_binding=binding, cal_code_sha="f" * 40
    )
    assert code_projected["result_id"] != original["result_id"]


def test_candidate_c1_compression_fails_on_frozen_production_traces() -> None:
    observed = {}
    for name in (
        "c0-no-entail.json",
        "c0-inf-02-contradicted-logging.json",
        "c0-inf-03-numeric-uptime.json",
    ):
        trace = _load(name)
        c0_bytes = len(json.dumps(trace, sort_keys=True, separators=(",", ":")).encode())
        c1 = project_production_trace(
            trace, contract_b_binding=_surrogate_binding(trace), cal_code_sha=CAL_SHA
        )
        c1_bytes = len(json.dumps(c1, sort_keys=True, separators=(",", ":")).encode())
        observed[name] = (c0_bytes, c1_bytes)
        assert c1_bytes > c0_bytes

    assert observed == {
        "c0-no-entail.json": (902, 1730),
        "c0-inf-02-contradicted-logging.json": (1713, 1930),
        "c0-inf-03-numeric-uptime.json": (1582, 1729),
    }


def test_c1_is_richer_than_thin_projection_for_same_headline_verdict() -> None:
    fixture = _load("semantic-state-matrix.json")
    base = _synthetic_base()
    counter = _mutate(
        base,
        "conclusion.residual.counterevidence_ids",
        fixture["same_verdict_variants"]["counterevidence"][
            "conclusion.residual.counterevidence_ids"
        ],
    )

    assert base["conclusion"]["reported_verdict"] == counter["conclusion"]["reported_verdict"]
    assert thin_projection(base) == thin_projection(counter)
    assert publication_probe(base) == "publish_review"
    assert publication_probe(counter) == "review"


def test_same_verdict_semantic_variants_change_legitimate_consumer_behavior() -> None:
    fixture = _load("semantic-state-matrix.json")
    base = _synthetic_base()
    variants = fixture["same_verdict_variants"]

    expected = {
        "eligibility_unknown": (sop_conformance_probe, "indeterminate"),
        "eligibility_negative": (sop_conformance_probe, "indeterminate_applicability"),
        "validity_unknown": (sop_conformance_probe, "indeterminate"),
        "validity_negative": (sop_conformance_probe, "indeterminate_invalid_evidence"),
        "aperture_unknown": (publication_probe, "review"),
        "aperture_incomplete": (publication_probe, "review"),
        "temporal_historical": (sop_conformance_probe, "indeterminate_applicability"),
        "unresolved_residual": (investigation_probe, "further_investigation"),
    }
    for name, (probe, expected_result) in expected.items():
        dotted, value = next(iter(variants[name].items()))
        candidate = _mutate(base, dotted, value)
        assert candidate["conclusion"]["reported_verdict"] == "supported"
        assert thin_projection(candidate)["reported_verdict"] == "supported"
        assert probe(candidate) == expected_result

    different_basis = _mutate(
        base,
        "conclusion.basis.evidence_ids",
        variants["different_basis"]["conclusion.basis.evidence_ids"],
    )
    assert different_basis["conclusion"]["reported_verdict"] == "supported"
    assert different_basis["conclusion"]["basis"] != base["conclusion"]["basis"]


def test_unknown_absent_failure_not_applicable_and_negative_are_behaviorally_distinct() -> None:
    fixture = _load("semantic-state-matrix.json")
    base = _synthetic_base()
    controls = fixture["assessment_state_controls"]

    absent = copy.deepcopy(base)
    del absent["assessments"]["semantic_validity"]
    assert assessment_state_probe(absent, "semantic_validity") == "incompatible_absent"

    expected = {
        "not_performed": "hold_assessment_required",
        "performed_unknown": "hold_unresolved",
        "failed": "hold_execution_failure",
        "not_applicable": "not_applicable",
        "explicit_negative": "explicit_negative",
    }
    for name, posture in expected.items():
        candidate = copy.deepcopy(base)
        candidate["assessments"]["semantic_validity"] = copy.deepcopy(controls[name])
        assert assessment_state_probe(candidate, "semantic_validity") == posture


def test_partial_execution_never_becomes_adverse_subject_finding() -> None:
    package = _synthetic_base()
    package["execution"] = {
        "status": "partial",
        "failures": [
            {
                "code": "semantic_operator_failure",
                "message": "validity operator did not complete",
                "proposition_id": "rc1-p1",
            }
        ],
        "deviations": [],
    }
    package["assessments"]["semantic_validity"] = {
        "state": "failed",
        "failure": {"code": "operator_failure", "message": "operator unavailable"},
    }
    package = with_result_identity(package)

    assert validate_package(package) == []
    assert publication_probe(package) == "hold"
    view = project_publication_review(package)
    assert view["review_posture"] == "hold_execution_incomplete"
    assert view["reported_verdict"] == "supported"  # preserved prior semantic result, not rewritten


def test_missing_evidence_reference_is_structural_failure_not_negative_verdict() -> None:
    package = _synthetic_base()
    package["conclusion"]["basis"]["evidence_ids"] = ["missing-evidence"]
    package = with_result_identity(package)
    errors = validate_package(package)
    assert errors == ["decision basis references missing evidence: missing-evidence"]
    assert package["conclusion"]["reported_verdict"] == "supported"


def test_report_derivation_is_deterministic_and_report_reverse_is_lossy() -> None:
    package = _synthetic_base()
    report_a = render_human_report(package, renderer_policy_id="rc1-human-renderer-policy-a")
    report_b = render_human_report(package, renderer_policy_id="rc1-human-renderer-policy-a")
    assert report_a == report_b
    assert package["result_id"] in report_a

    # The report intentionally does not carry exact Contract-B bundle hash,
    # producer code SHA, raw semantic measurements, or reassessment lineage.
    assert package["identity"]["contract_b"]["bundle_sha256"] not in report_a
    assert package["identity"]["producer_code_sha"] not in report_a
    assert "0.91" not in report_a
    assert "prior_result_id" not in report_a


def test_independent_projector_uses_only_candidate_package() -> None:
    package = _synthetic_base()
    view = project_publication_review(package)
    report = render_compact_report(package, renderer_policy_id="independent-compact-a")
    assert view["result_id"] == package["result_id"]
    assert view["review_posture"] == "eligible_for_publication_review"
    assert package["result_id"] in report

    source = Path("contract_c_rc1_research/independent_projector.py").read_text(encoding="utf-8")
    assert "claim_audit_lab" not in source
    assert "contract_c_rc1.projector" not in source


def test_field_family_ablation_records_actual_consumer_failures() -> None:
    base = _synthetic_base()
    failures: dict[str, set[str]] = {}
    for family in (
        "identity",
        "evidence",
        "measurements",
        "assessments",
        "conclusion",
        "reassessment",
        "execution",
    ):
        candidate = copy.deepcopy(base)
        del candidate[family]
        failed: set[str] = set()
        for name, consumer in CONSUMERS.items():
            try:
                consumer(candidate)
            except (InsufficientPackage, KeyError, TypeError, ValueError):
                failed.add(name)
        failures[family] = failed

    assert failures == {
        "identity": {"publication", "sop_conformance", "investigation", "reconstruction"},
        "evidence": {"publication", "sop_conformance", "investigation", "reconstruction"},
        "measurements": {"reconstruction"},
        "assessments": {"publication", "sop_conformance", "investigation", "reconstruction"},
        "conclusion": {"publication", "sop_conformance", "investigation", "reconstruction"},
        "reassessment": {"investigation"},
        "execution": {"publication", "sop_conformance", "investigation", "reconstruction"},
    }


def test_supersession_identity_separates_recomputed_and_changed_input_results() -> None:
    original = _synthetic_base()

    recomputed = copy.deepcopy(original)
    recomputed["identity"]["audit_config_sha256"] = "sha256:" + "d" * 64
    recomputed["reassessment"] = {
        "relation": "recomputed",
        "prior_result_id": original["result_id"],
    }
    recomputed = with_result_identity(recomputed)

    superseding = copy.deepcopy(recomputed)
    superseding["identity"]["contract_b"]["bundle_sha256"] = "sha256:" + "e" * 64
    superseding["reassessment"] = {
        "relation": "superseding",
        "prior_result_id": recomputed["result_id"],
    }
    superseding = with_result_identity(superseding)

    assert len({original["result_id"], recomputed["result_id"], superseding["result_id"]}) == 3
    assert (
        original["identity"]["contract_b"]["bundle_sha256"]
        == recomputed["identity"]["contract_b"]["bundle_sha256"]
    )
    assert (
        original["identity"]["audit_config_sha256"]
        != recomputed["identity"]["audit_config_sha256"]
    )
    assert (
        recomputed["identity"]["contract_b"]["bundle_sha256"]
        != superseding["identity"]["contract_b"]["bundle_sha256"]
    )


def test_partial_result_set_preserves_completed_and_failed_propositions() -> None:
    completed = _synthetic_base()
    failed = copy.deepcopy(completed)
    failed["identity"]["proposition"] = {
        "proposition_id": "rc1-p2",
        "text": "A second proposition whose semantic operator failed.",
        "text_sha256": "",
    }
    failed["identity"]["proposition"]["text_sha256"] = (
        "sha256:"
        + hashlib.sha256(failed["identity"]["proposition"]["text"].encode()).hexdigest()
    )
    failed["conclusion"] = {
        "reported_verdict": None,
        "reason_code": "execution_failed",
        "audit_flags": [],
        "basis": {"evidence_ids": [], "rule_ids": []},
        "residual": {"counterevidence_ids": [], "unresolved_evidence_ids": []},
    }
    failed["assessments"]["semantic_validity"] = {
        "state": "failed",
        "failure": {"code": "operator_failure", "message": "semantic operator unavailable"},
    }
    failed["execution"] = {
        "status": "failed",
        "failures": [
            {
                "code": "semantic_operator_failure",
                "message": "semantic operator unavailable",
                "proposition_id": "rc1-p2",
            }
        ],
        "deviations": [],
    }
    failed = with_result_identity(failed)

    binding = copy.deepcopy(completed["identity"]["contract_b"])
    result_set = build_result_set(
        [completed, failed],
        contract_b_binding=binding,
        run_execution={
            "status": "partial",
            "failures": [
                {
                    "code": "proposition_failed",
                    "proposition_id": "rc1-p2",
                    "message": "one proposition did not complete",
                }
            ],
            "deviations": [],
        },
    )

    assert validate_result_set(result_set) == []
    assert result_set["execution"]["status"] == "partial"
    assert result_set["results"][0]["conclusion"]["reported_verdict"] == "supported"
    assert result_set["results"][1]["conclusion"]["reported_verdict"] is None
    assert result_set["results"][1]["execution"]["status"] == "failed"


def test_currentness_is_not_embedded_in_immutable_result() -> None:
    package = _synthetic_base()
    assert "current" not in package["reassessment"]
    assert package["reassessment"]["relation"] == "original"


def test_synthetic_base_is_valid() -> None:
    assert validate_package(_synthetic_base()) == []
