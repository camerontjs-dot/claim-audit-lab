"""No-inference contracts for the preregistered E3 structured direct harness."""

from __future__ import annotations

import json
import runpy
from pathlib import Path

import pytest
import yaml

from claim_audit_lab import __version__
from claim_audit_lab.v1.config import hash_audit_config
from claim_audit_lab.v1.explicit_claims import ExplicitClaimRequest, run_explicit_claim_audit
from claim_audit_lab.v1.models import (
    AuditRequest,
    AuditTrace,
    ExtractedFeatures,
    SupportSignal,
    Verdict,
)
from scripts.simple_logic_gold_structured_lane import (
    _write_absent_or_identical,
    assemble_baseline_requests,
    assemble_irrelevant_evidence,
    assemble_reversed_evidence,
    assemble_stable_id_renaming,
    assemble_wording_variants,
    load_structured_inputs,
    run_structured_lane,
    run_structured_suite,
    suite_is_green,
)

_PROJECT = Path(__file__).resolve().parents[3]
_OUTPUT = (
    _PROJECT / "outputs/simple-logic-gold/v0.1-frozen-rev01-2026-07-15/e3-structured-direct-v0.1"
)
_FROZEN = _PROJECT / "outputs/simple-logic-gold/v0.1-frozen-rev01-2026-07-15/frozen-gold.json"


def _inputs():
    return load_structured_inputs(
        _FROZEN,
        _OUTPUT / "explicit-structure-v0.1.yaml",
        _OUTPUT / "wording-variants-v0.1.yaml",
    )


def _verdict_for(request: AuditRequest) -> Verdict:
    evidence = " ".join(passage.text for passage in request.passages).lower()
    claim = request.claim_text.lower()
    if "not in drawer a" in evidence and "drawer a" in claim:
        return Verdict(support_verdict="contradicted")
    if "failed inspection" in evidence and "valve v2 passed" in claim:
        return Verdict(support_verdict="contradicted")
    if "not sealed" in evidence and "parcel was sealed" in claim:
        return Verdict(support_verdict="contradicted")
    if "drawer a contains the brass key" in claim:
        return Verdict(support_verdict="supported")
    if "located in drawer a" in claim:
        return Verdict(support_verdict="contradicted")
    if claim in evidence:
        return Verdict(support_verdict="supported")
    return Verdict(support_verdict="not_checkable", support_verdict_reason="no_entail_signal")


def _auditor(request: AuditRequest) -> AuditTrace:
    return AuditTrace(
        claim_id=request.claim_id,
        claim_text=request.claim_text,
        retrieval=[],
        entailment=[],
        features=ExtractedFeatures(),
        support_signal=SupportSignal(label="neutral", max_entailment_score=0.0),
        rules_fired=[],
        verdict=_verdict_for(request),
        audit_config_hash=hash_audit_config(request.audit_config),
        library_version=__version__,
    )


def _explicit_runner(request: ExplicitClaimRequest):
    return run_explicit_claim_audit(request, auditor=_auditor)


def _matching_explicit_runner(request: ExplicitClaimRequest):
    relation_to_verdict = {
        "supports": "supported",
        "refutes": "contradicted",
        "insufficient": "not_checkable",
        "retrieval_gap": "not_checkable",
    }
    expected_by_id = {
        item["runtime_atom_id"]: item["expected_relation"]
        for case in assemble_baseline_requests(_inputs())
        for item in case.runtime_expectations
    }

    def atomic_runner(atomic_request: AuditRequest) -> AuditTrace:
        runtime_id = atomic_request.claim_id.removeprefix("metamorphic-renamed-")
        relation = expected_by_id[runtime_id]
        return _auditor(atomic_request).model_copy(
            update={"verdict": Verdict(support_verdict=relation_to_verdict[relation])}
        )

    return run_explicit_claim_audit(request, auditor=atomic_runner)


def _semantic_projection(result: dict[str, object]) -> str:
    return json.dumps(
        {
            "targets": [
                (item["base_case_id"], item["frozen_target_id"], item["observed_relation"])
                for item in result["frozen_semantic_targets"]
            ],
            "atoms": [
                (item["base_case_id"], item["expected_relation"], item["observed_relation"])
                for item in result["runtime_atoms"]
            ],
            "parents": [
                (item["base_case_id"], item["observed_parent_verdict"])
                for item in result["frozen_parents"]
            ],
        },
        sort_keys=True,
    )


def _write_yaml(path: Path, document: dict[str, object]) -> None:
    path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")


def test_manifest_binding_and_derived_denominators_are_exact() -> None:
    inputs = _inputs()
    cases = assemble_baseline_requests(inputs)

    assert [case.base_case_id for case in cases] == [f"SLG-{number:02d}" for number in range(1, 13)]
    assert sum(len(case.request.atoms) for case in cases) == 21
    assert [case.mode for case in cases[3:5]] == [
        "explicit_finite_all_of",
        "explicit_finite_all_of",
    ]
    assert [atom.claim_text for atom in cases[3].request.atoms] == [
        "Valve V1 passed inspection.",
        "Valve V2 passed inspection.",
        "Valve V3 passed inspection.",
    ]
    assert [item["expected_relation"] for item in cases[4].runtime_expectations] == [
        "supports",
        "refutes",
        "supports",
    ]
    assert all(
        atom.provenance.reference_sha256 == inputs.frozen_sha256
        for case in cases[:3]
        for atom in case.request.atoms
    )
    parent_ids = {case.request.parent_claim_id for case in cases}
    runtime_ids = {atom.atom_id for case in cases for atom in case.request.atoms}
    assert parent_ids.isdisjoint(runtime_ids)
    assert all(
        atom.provenance.reference_sha256 == inputs.structure_sha256
        for case in cases[3:5]
        for atom in case.request.atoms
    )


def test_stubbed_runner_reports_three_layers_and_is_byte_identical() -> None:
    cases = assemble_baseline_requests(_inputs())
    first = run_structured_lane(cases, _explicit_runner)
    second = run_structured_lane(cases, _explicit_runner)

    assert first == second
    assert first["summary"] == {
        "frozen_semantic_targets": 17,
        "comparable_frozen_semantic_targets": 15,
        "runtime_atoms": 21,
        "comparable_runtime_atoms": 19,
        "frozen_parents": 12,
        "comparable_frozen_parents": 10,
    }
    assert (
        sum(
            item["route"] == "structured_parent_for_frozen_universal_target"
            for item in first["frozen_semantic_targets"]
        )
        == 2
    )
    assert sum(item["comparable"] is False for item in first["frozen_semantic_targets"]) == 2
    assert sum(item["comparable"] is False for item in first["frozen_parents"]) == 2
    assert all("explicit_trace" in item for item in first["frozen_parents"])
    assert all(item["request_sha256"].startswith("sha256:") for item in first["runtime_atoms"])
    assert all(
        item["provenance"]["reference_sha256"].startswith("sha256:")
        for item in first["runtime_atoms"]
    )
    assert all(
        item["source_bindings"]["frozen_file_sha256"] == _inputs().frozen_sha256
        for item in first["runtime_atoms"]
    )


def test_all_four_preregistered_transforms_are_mechanically_constructed() -> None:
    inputs = _inputs()
    baseline = assemble_baseline_requests(inputs)
    baseline_result = run_structured_lane(baseline, _explicit_runner)
    transforms = [
        assemble_stable_id_renaming(baseline),
        assemble_reversed_evidence(baseline),
        assemble_irrelevant_evidence(baseline),
    ]
    for transformed in transforms:
        assert _semantic_projection(
            run_structured_lane(transformed, _explicit_runner)
        ) == _semantic_projection(baseline_result)

    wording = assemble_wording_variants(baseline, inputs)
    assert len(wording) == 3
    assert all(
        case.request.parent_claim_text == case.request.atoms[0].claim_text for case in wording
    )
    wording_result = run_structured_lane(wording, _explicit_runner)
    assert [item["observed_relation"] for item in wording_result["frozen_semantic_targets"]] == [
        "supports",
        "refutes",
        "insufficient",
    ]
    assert [item["variant_id"] for item in wording_result["runtime_atoms"]] == [
        "SLG-01-a1",
        "SLG-02-a1",
        "SLG-03-a1",
    ]


def test_validation_fails_closed_on_structure_or_variant_drift(tmp_path: Path) -> None:
    structure = tmp_path / "structure.yaml"
    variants = tmp_path / "variants.yaml"
    structure_document = yaml.safe_load(
        (_OUTPUT / "explicit-structure-v0.1.yaml").read_text(encoding="utf-8")
    )
    structure_document["cases"][0]["parent_claim_id"] = "slg-02-runtime-a1"
    _write_yaml(structure, structure_document)
    variants.write_text(
        (_OUTPUT / "wording-variants-v0.1.yaml").read_text(encoding="utf-8"), encoding="utf-8"
    )
    with pytest.raises(ValueError, match="globally disjoint"):
        load_structured_inputs(_FROZEN, structure, variants)


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (
            lambda document: document["cases"][3].update({"mode": "inherit_frozen"}),
            "inherit_frozen entry",
        ),
        (
            lambda document: document["cases"][4]["runtime_atoms"][1].update(
                {"expected_relation": "supports"}
            ),
            "finite relation vector",
        ),
    ],
)
def test_structure_rejects_tampered_finite_roster(
    tmp_path: Path, mutate: object, message: str
) -> None:
    structure = tmp_path / "structure.yaml"
    document = yaml.safe_load(
        (_OUTPUT / "explicit-structure-v0.1.yaml").read_text(encoding="utf-8")
    )
    mutate(document)
    _write_yaml(structure, document)
    with pytest.raises(ValueError, match=message):
        load_structured_inputs(_FROZEN, structure, _OUTPUT / "wording-variants-v0.1.yaml")


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda document: document["variants"].pop(), "exactly the preregistered ordered set"),
        (
            lambda document: document["variants"][0].update({"parent_claim_text": ""}),
            "parent text",
        ),
        (
            lambda document: document["variants"][1].update({"variant_id": "SLG-01-a1"}),
            "duplicate variant_id",
        ),
    ],
)
def test_variants_reject_tampered_roster_text_and_ids(
    tmp_path: Path, mutate: object, message: str
) -> None:
    variants = tmp_path / "variants.yaml"
    document = yaml.safe_load((_OUTPUT / "wording-variants-v0.1.yaml").read_text(encoding="utf-8"))
    mutate(document)
    _write_yaml(variants, document)
    with pytest.raises(ValueError, match=message):
        load_structured_inputs(_FROZEN, _OUTPUT / "explicit-structure-v0.1.yaml", variants)


def test_unmapped_degree_does_not_reduce_comparability() -> None:
    def unsupported_auditor(request: AuditRequest) -> AuditTrace:
        return _auditor(request).model_copy(
            update={"verdict": Verdict(support_verdict="unsupported")}
        )

    def unsupported_explicit_runner(request: ExplicitClaimRequest):
        return run_explicit_claim_audit(request, auditor=unsupported_auditor)

    result = run_structured_lane(assemble_baseline_requests(_inputs()), unsupported_explicit_runner)
    comparable = [item for item in result["frozen_semantic_targets"] if item["comparable"]]
    assert len(comparable) == 15
    assert all(item["observed_relation"] is None and item["match"] is False for item in comparable)


def test_public_explicit_runner_shape_is_called_once_per_case_and_rejects_atomic_runner() -> None:
    cases = assemble_baseline_requests(_inputs())
    calls: list[str] = []

    def counting_runner(request: ExplicitClaimRequest):
        calls.append(request.parent_claim_id)
        return _matching_explicit_runner(request)

    run_structured_lane(cases, counting_runner)
    assert len(calls) == 12
    with pytest.raises((AttributeError, TypeError)):
        run_structured_lane(cases, _auditor)  # type: ignore[arg-type]


def test_explicit_trace_from_a_different_request_fails_closed() -> None:
    cases = assemble_baseline_requests(_inputs())
    foreign_trace = _matching_explicit_runner(cases[1].request)

    def foreign_runner(_: ExplicitClaimRequest):
        return foreign_trace

    with pytest.raises(ValueError, match="request_sha256"):
        run_structured_lane([cases[0]], foreign_runner)


def test_suite_reports_fixed_denominators_identity_and_all_transforms() -> None:
    calls: list[str] = []

    def counting_runner(request: ExplicitClaimRequest):
        calls.append(request.parent_claim_id)
        return _matching_explicit_runner(request)

    suite = run_structured_suite(_inputs(), counting_runner)
    assert len(calls) == 63
    assert suite["baseline_scores"] == {
        "frozen_semantic_targets": {"denominator": 15, "matching": 15, "failures": []},
        "runtime_construction_atoms": {"denominator": 19, "matching": 19, "failures": []},
        "frozen_parents": {"denominator": 10, "matching": 10, "failures": []},
    }
    assert suite["exact_baseline_rerun"]["serialized_byte_identical"] is True
    for transform in suite["metamorphic"].values():
        assert transform["invariance"]["frozen_semantic_targets"] == {
            "denominator": 15,
            "failures": [],
        }
        assert transform["invariance"]["runtime_atoms"] == {
            "denominator": 19,
            "failures": [],
        }
        assert transform["invariance"]["frozen_parents"] == {
            "denominator": 10,
            "failures": [],
        }
    assert suite["wording_variants"]["frozen_semantic_targets"] == {
        "denominator": 3,
        "matching": 3,
        "failures": [],
    }
    assert suite_is_green(suite) is True


def test_suite_preserves_repeat_and_metamorphic_failures_without_shrinking_denominators() -> None:
    calls = 0

    def drift_runner(request: ExplicitClaimRequest):
        nonlocal calls
        calls += 1
        if calls == 13:

            def drift_atomic_runner(atomic_request: AuditRequest) -> AuditTrace:
                return _auditor(atomic_request).model_copy(
                    update={"verdict": Verdict(support_verdict="unsupported")}
                )

            return run_explicit_claim_audit(request, auditor=drift_atomic_runner)
        if request.parent_claim_id.startswith("metamorphic-renamed-"):

            def renamed_drift_runner(atomic_request: AuditRequest) -> AuditTrace:
                return _auditor(atomic_request).model_copy(
                    update={"verdict": Verdict(support_verdict="unsupported")}
                )

            return run_explicit_claim_audit(request, auditor=renamed_drift_runner)
        return _matching_explicit_runner(request)

    suite = run_structured_suite(_inputs(), drift_runner)
    assert suite["exact_baseline_rerun"]["serialized_byte_identical"] is False
    renamed = suite["metamorphic"]["stable_id_renaming"]["invariance"]
    assert renamed["frozen_semantic_targets"]["denominator"] == 15
    assert renamed["runtime_atoms"]["denominator"] == 19
    assert renamed["frozen_parents"]["denominator"] == 10
    assert renamed["frozen_semantic_targets"]["failures"]
    assert renamed["frozen_semantic_targets"]["failures"][0] == {
        "base_case_id": "SLG-01",
        "frozen_target_id": "SLG-01-a1",
        "baseline_observed": "supports",
        "transformed_observed": None,
    }
    assert renamed["runtime_atoms"]["failures"][0] == {
        "base_case_id": "SLG-01",
        "runtime_atom_position": 1,
        "expected_relation": "supports",
        "baseline_observed": "supports",
        "transformed_observed": None,
        "baseline_runtime_atom_id": "slg-01-runtime-a1",
        "transformed_runtime_atom_id": "metamorphic-renamed-slg-01-runtime-a1",
    }
    assert suite_is_green(suite) is False


def test_suite_serialization_is_deterministic_and_absent_or_identical(tmp_path: Path) -> None:
    first = run_structured_suite(_inputs(), _matching_explicit_runner)
    second = run_structured_suite(_inputs(), _matching_explicit_runner)
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    output = tmp_path / "suite.json"
    _write_absent_or_identical(output, first)
    _write_absent_or_identical(output, second)
    with pytest.raises(FileExistsError):
        _write_absent_or_identical(output, {"drift": True})


def test_real_entrypoint_import_is_inert() -> None:
    entrypoint = _PROJECT / "workbench/scripts/simple_logic_gold_structured_real_run.py"
    result_path = _OUTPUT / "structured-direct-run-01.json"
    existed_before = result_path.exists()
    bytes_before = result_path.read_bytes() if existed_before else None
    entry_namespace = runpy.run_path(str(entrypoint), run_name="not_main")
    assert entry_namespace["canonical_output_dir"]() == _OUTPUT
    assert result_path.exists() is existed_before
    if existed_before:
        assert result_path.read_bytes() == bytes_before
    assert (
        _PROJECT
        / "workbench/outputs/simple-logic-gold/v0.1-frozen-rev01-2026-07-15"
        / "e3-structured-direct-v0.1/structured-direct-run-01.json"
    ).exists() is False
    source = entrypoint.read_text(encoding="utf-8")
    assert "from claim_audit_lab.v1.runner import run_default_explicit_claim_audit" in source


def test_absent_or_identical_write_and_no_production_case_branching() -> None:
    output = _OUTPUT / "missing-test-output.json"
    payload = {"stable": ["receipt"]}
    _write_absent_or_identical(output, payload)
    _write_absent_or_identical(output, payload)
    with pytest.raises(FileExistsError):
        _write_absent_or_identical(output, {"stable": ["drift"]})
    output.unlink()

    production_sources = [
        _PROJECT / "workbench/src/claim_audit_lab/v1/explicit_claims.py",
        _PROJECT / "workbench/src/claim_audit_lab/v1/runner.py",
    ]
    production = "\n".join(path.read_text(encoding="utf-8") for path in production_sources)
    assert "SLG-" not in production
    assert "simple-logic-gold" not in production
    harness = (_PROJECT / "workbench/scripts/simple_logic_gold_structured_lane.py").read_text(
        encoding="utf-8"
    )
    assert "from claim_audit_lab.v1.runner import" not in harness
