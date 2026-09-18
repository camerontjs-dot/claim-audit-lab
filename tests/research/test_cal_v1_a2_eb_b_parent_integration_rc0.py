from __future__ import annotations

import hashlib
import json
import os
import subprocess
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

pytest.importorskip("evidence_bundler.v1")

from evidence_bundler.v1 import build_package
from evidence_bundler.v1.contract_a import compute_handoff_sha256
from evidence_bundler.v1.contract_b import (
    CONTRACT_B_PRODUCTION_LOCK,
    INTEGRATION_CONFIG,
    INTEGRATION_CONFIG_SHA256,
    INTEGRATION_PROFILE_ID,
    project_contract_b,
)

from claim_audit_lab.production_v1.execution import run_contract_b_bundle
from claim_audit_lab.production_v1.semantic.decomposition import (
    BoundAuditOutcome,
    DecompositionDeclaration,
    DecompositionRefusal,
    DecompositionState,
    PropositionRef,
    recompose,
)
from claim_audit_lab.production_v1.semantic.models import Conclusion

EB_HEAD = "4e1f6fe00e7c350b28f52bfea14f1f8988847884"
B_LOCK = "c314e53bd91c0736aa4370a364673b069aceb43e"

C1_TEXT = "Alpha had a higher rate than Beta."
C1_REFUTE_TEXT = "Alpha had a lower rate than Beta."
C2_TEXT = "Alice reviewed dossier before Bob archived dossier."
ROOT_TEXT = (
    "Alpha had a higher rate than Beta, and "
    "Alice reviewed dossier before Bob archived dossier."
)

SOURCES = (
    ("S-C1-SUPPORT", C1_TEXT),
    ("S-C1-REFUTE", C1_REFUTE_TEXT),
    ("S-C2-SUPPORT", C2_TEXT),
    ("S-D01", "Alpha calibration records describe sampling frequency."),
    ("S-D02", "Beta calibration records describe sampling frequency."),
    ("S-D03", "Alice prepared the dossier for review."),
    ("S-D04", "Bob stored archival metadata for the dossier."),
    ("S-D05", "Gamma had a higher output than Delta."),
    ("S-D06", "Quality staff inspected batch documentation."),
    ("S-D07", "The archive contains unrelated maintenance notes."),
)


@dataclass(frozen=True)
class Case:
    case_id: str
    c1_source: str
    admit_c2: bool
    expected_c1: Conclusion
    expected_c2: Conclusion
    expected_parent: Conclusion


CASES = (
    Case(
        "PIPE01",
        "S-C1-SUPPORT",
        True,
        Conclusion.SUPPORTED,
        Conclusion.SUPPORTED,
        Conclusion.SUPPORTED,
    ),
    Case(
        "PIPE02",
        "S-C1-REFUTE",
        True,
        Conclusion.CONTRADICTED,
        Conclusion.SUPPORTED,
        Conclusion.CONTRADICTED,
    ),
    Case(
        "PIPE03",
        "S-C1-SUPPORT",
        False,
        Conclusion.SUPPORTED,
        Conclusion.NOT_CHECKABLE,
        Conclusion.NOT_CHECKABLE,
    ),
    Case(
        "PIPE04",
        "S-C1-REFUTE",
        False,
        Conclusion.CONTRADICTED,
        Conclusion.NOT_CHECKABLE,
        Conclusion.CONTRADICTED,
    ),
)


def _tagged(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def _tagged_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _contract_a() -> dict[str, Any]:
    value: dict[str, Any] = {
        "schema": "contract-a-wire-candidate-rc2",
        "handoff_id": "cal-v1-pipeline-integration-rc0",
        "producer": {
            "producer_id": "cal-v1-integration-research",
            "producer_version": "rc0",
        },
        "work": {"work_id": "cal-v1-a2-eb-b-parent-integration-rc0"},
        "root_proposition": {
            "proposition_id": "ROOT",
            "text": ROOT_TEXT,
            "text_sha256": _tagged(ROOT_TEXT),
        },
        "decomposition": {
            "state": "declared",
            "decomposition_id": "D-PIPE-RC0",
            "operator": "all_of",
            "children": [
                {
                    "proposition_id": "C1",
                    "text": C1_TEXT,
                    "text_sha256": _tagged(C1_TEXT),
                    "sequence": 1,
                },
                {
                    "proposition_id": "C2",
                    "text": C2_TEXT,
                    "text_sha256": _tagged(C2_TEXT),
                    "sequence": 2,
                },
            ],
        },
        "sources": [
            {
                "source_id": source_id,
                "media_type": "text/plain; charset=utf-8",
                "content": text,
                "content_sha256": _tagged(text),
            }
            for source_id, text in SOURCES
        ],
        "handoff_sha256": "sha256:" + "0" * 64,
    }
    value["handoff_sha256"] = compute_handoff_sha256(value)
    return value


def _eb_repo() -> Path:
    raw = os.environ.get("CAL_EB_INTEGRATION_REPO")
    if not raw:
        pytest.skip("exact Evidence Bundler checkout is not installed for this run")
    repo = Path(raw).resolve()
    actual = subprocess.check_output(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        text=True,
    ).strip()
    assert actual == EB_HEAD
    return repo


def _carrier() -> dict[str, Any]:
    path = (
        _eb_repo()
        / "research"
        / "eb_v1_integration_candidate"
        / "contract_b_compatibility_carrier.json"
    )
    return json.loads(path.read_text(encoding="utf-8"))


def _initial_package() -> dict[str, Any]:
    package = build_package(contract_a=_contract_a(), config=INTEGRATION_CONFIG)
    assert package["config_sha256"] == INTEGRATION_CONFIG_SHA256
    assert INTEGRATION_PROFILE_ID == "eb-v1-integration-10x3-rc0"
    assert package["config"]["candidate_depth"] == 10
    assert package["config"]["retained_k"] == 3
    return package


def _retained_passage_id(
    package: dict[str, Any],
    proposition_id: str,
    source_id: str,
) -> str:
    rows = [
        row
        for row in package["candidates"]
        if row["proposition_id"] == proposition_id
        and row["source_id"] == source_id
        and row["selection_state"] == "retained"
    ]
    observed = [
        (row["source_id"], row["nomination_rank"], row["selection_state"])
        for row in package["candidates"]
        if row["proposition_id"] == proposition_id
    ]
    assert len(rows) == 1, (
        "preregistered decisive source was not uniquely retained: "
        f"{proposition_id}/{source_id}; observed={observed}"
    )
    return str(rows[0]["passage_id"])


def _admission(case: Case, initial: dict[str, Any]) -> dict[tuple[str, str], str]:
    decisions: dict[tuple[str, str], str] = {
        ("C1", _retained_passage_id(initial, "C1", case.c1_source)): "accepted"
    }
    if case.admit_c2:
        decisions[("C2", _retained_passage_id(initial, "C2", "S-C2-SUPPORT"))] = "accepted"
    return decisions


def _target(proposition_id: str) -> dict[str, Any]:
    if proposition_id == "C1":
        text = C1_TEXT
        family = "strict_comparison"
        fields = {
            "lhs_entity": "Alpha",
            "rhs_entity": "Beta",
            "comparison_direction": "MORE_THAN",
        }
    elif proposition_id == "C2":
        text = C2_TEXT
        family = "direct_event_order"
        fields = {
            "left_subject": "alice",
            "left_predicate": "review",
            "left_object": "dossier",
            "left_polarity": "positive",
            "temporal_relation": "BEFORE",
            "right_subject": "bob",
            "right_predicate": "archive",
            "right_object": "dossier",
            "right_polarity": "positive",
        }
    else:
        raise AssertionError(proposition_id)
    return {
        "claim_id": proposition_id,
        "proposition": {
            "proposition_id": proposition_id,
            "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "semantic_family": family,
            "fields": fields,
        },
    }


def _write_target(path: Path, proposition_id: str) -> None:
    path.write_text(
        json.dumps(_target(proposition_id), sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


def _declaration(contract_a: dict[str, Any]) -> DecompositionDeclaration:
    root = contract_a["root_proposition"]
    decomposition = contract_a["decomposition"]
    return DecompositionDeclaration(
        root=PropositionRef(
            str(root["proposition_id"]),
            str(root["text_sha256"]),
        ),
        state=DecompositionState.DECLARED,
        decomposition_id=str(decomposition["decomposition_id"]),
        operator=str(decomposition["operator"]),
        children=tuple(
            PropositionRef(
                str(row["proposition_id"]),
                str(row["text_sha256"]),
                int(row["sequence"]),
            )
            for row in decomposition["children"]
        ),
    )


def _run_child(
    *,
    bundle_dir: Path,
    proposition_id: str,
    root: Path,
) -> tuple[BoundAuditOutcome, bytes, dict[str, Any]]:
    target_path = root / f"{proposition_id}.target.json"
    _write_target(target_path, proposition_id)
    out_dir = root / f"{proposition_id}.cal"
    run_contract_b_bundle(bundle_dir, target_path, out_dir)

    result_bytes = (out_dir / "result.json").read_bytes()
    record = json.loads(result_bytes)
    conclusion = Conclusion(record["result"]["conclusion"])
    child = next(
        row
        for row in _contract_a()["decomposition"]["children"]
        if row["proposition_id"] == proposition_id
    )
    outcome = BoundAuditOutcome.create(
        proposition_id=proposition_id,
        text_sha256=str(child["text_sha256"]),
        audit_result_sha256=_tagged_bytes(result_bytes),
        conclusion=conclusion,
    )
    return outcome, result_bytes, record


def _execute_case(case: Case, root: Path) -> dict[str, Any]:
    contract_a = _contract_a()
    initial = _initial_package()
    admission = _admission(case, initial)
    package = build_package(
        contract_a=contract_a,
        config=INTEGRATION_CONFIG,
        admission=admission,
    )

    case_dir = root / case.case_id
    case_dir.mkdir(parents=True)
    receipt = project_contract_b(
        package=package,
        compatibility_carrier=_carrier(),
        out_dir=case_dir / "eb",
    )
    assert receipt["contract_b_authority"] == {
        "version": "1.2.0",
        "production_lock": CONTRACT_B_PRODUCTION_LOCK,
    }
    assert CONTRACT_B_PRODUCTION_LOCK == B_LOCK
    assert receipt["native_package_sha256"] == package["package_sha256"]

    bundle_dir = case_dir / "eb" / "contract_b"
    c1, c1_bytes, c1_record = _run_child(
        bundle_dir=bundle_dir,
        proposition_id="C1",
        root=case_dir,
    )
    c2, c2_bytes, c2_record = _run_child(
        bundle_dir=bundle_dir,
        proposition_id="C2",
        root=case_dir,
    )

    parent = recompose(
        _declaration(contract_a),
        child_outcomes=(c1, c2),
    )

    return {
        "contract_a": contract_a,
        "package": package,
        "projection_receipt": receipt,
        "admission": admission,
        "c1": c1,
        "c2": c2,
        "c1_bytes": c1_bytes,
        "c2_bytes": c2_bytes,
        "c1_record": c1_record,
        "c2_record": c2_record,
        "parent": parent,
    }


@pytest.mark.parametrize("case", CASES, ids=lambda value: value.case_id)
def test_frozen_four_case_pipeline_matrix(case: Case, tmp_path: Path) -> None:
    result = _execute_case(case, tmp_path)

    assert result["c1"].conclusion is case.expected_c1
    assert result["c2"].conclusion is case.expected_c2
    assert result["parent"].conclusion is case.expected_parent

    contract_a = result["contract_a"]
    children = contract_a["decomposition"]["children"]
    assert result["c1"].proposition_id == children[0]["proposition_id"]
    assert result["c2"].proposition_id == children[1]["proposition_id"]

    for proposition_id, record in (
        ("C1", result["c1_record"]),
        ("C2", result["c2_record"]),
    ):
        accepted = {
            row["passage_id"]
            for row in result["package"]["candidates"]
            if row["proposition_id"] == proposition_id
            and row["selection_state"] == "retained"
            and row["admission_state"] == "accepted"
        }
        assert set(record["evidence_world"]["admitted_passage_ids"]) == accepted
        nonretained = {
            row["passage_id"]
            for row in result["package"]["candidates"]
            if row["proposition_id"] == proposition_id
            and row["selection_state"] == "not_retained"
        }
        assert not (set(record["evidence_world"]["admitted_passage_ids"]) & nonretained)

    bound = result["parent"].receipt.ordered_child_bindings
    assert tuple(row[0] for row in bound) == ("C1", "C2")
    assert tuple(row[2] for row in bound) == (
        result["c1"].result_id,
        result["c2"].result_id,
    )


def test_pipeline_replay_is_byte_and_receipt_deterministic(tmp_path: Path) -> None:
    first = _execute_case(CASES[0], tmp_path / "first")
    second = _execute_case(CASES[0], tmp_path / "second")

    assert first["package"] == second["package"]
    assert first["projection_receipt"] == second["projection_receipt"]
    assert first["c1_bytes"] == second["c1_bytes"]
    assert first["c2_bytes"] == second["c2_bytes"]
    assert first["parent"] == second["parent"]


def test_nonretained_candidate_cannot_be_admitted(tmp_path: Path) -> None:
    initial = _initial_package()
    row = next(
        row
        for row in initial["candidates"]
        if row["proposition_id"] == "C1" and row["selection_state"] == "not_retained"
    )
    with pytest.raises(Exception, match="retained normative candidates"):
        build_package(
            contract_a=_contract_a(),
            config=INTEGRATION_CONFIG,
            admission={("C1", str(row["passage_id"])): "accepted"},
        )


def test_target_child_identity_swap_refuses_at_cal_boundary(tmp_path: Path) -> None:
    _execute_case(CASES[0], tmp_path / "base")
    bundle = tmp_path / "base" / CASES[0].case_id / "eb" / "contract_b"
    target = _target("C1")
    target["claim_id"] = "C2"
    path = tmp_path / "swapped-target.json"
    path.write_text(json.dumps(target), encoding="utf-8")
    with pytest.raises(Exception, match="proposition_id must equal"):
        run_contract_b_bundle(bundle, path, tmp_path / "bad-run")


def test_target_text_hash_mutation_refuses_at_cal_boundary(tmp_path: Path) -> None:
    _execute_case(CASES[0], tmp_path / "base")
    bundle = tmp_path / "base" / CASES[0].case_id / "eb" / "contract_b"
    target = _target("C1")
    target["proposition"]["text_sha256"] = "0" * 64
    path = tmp_path / "bad-hash-target.json"
    path.write_text(json.dumps(target), encoding="utf-8")
    with pytest.raises(Exception, match="does not bind the exact Contract B claim text"):
        run_contract_b_bundle(bundle, path, tmp_path / "bad-hash-run")


def test_parent_refuses_missing_and_extra_child_results(tmp_path: Path) -> None:
    result = _execute_case(CASES[0], tmp_path)
    declaration = _declaration(result["contract_a"])

    with pytest.raises(DecompositionRefusal, match="MISSING_CHILD_RESULT"):
        recompose(declaration, child_outcomes=(result["c1"],))

    extra = BoundAuditOutcome.create(
        proposition_id="C3",
        text_sha256="sha256:" + "c" * 64,
        audit_result_sha256="sha256:" + "d" * 64,
        conclusion=Conclusion.SUPPORTED,
    )
    with pytest.raises(DecompositionRefusal, match="EXTRA_CHILD_RESULT"):
        recompose(declaration, child_outcomes=(result["c1"], result["c2"], extra))


def test_parent_is_invariant_to_supplied_child_result_order(tmp_path: Path) -> None:
    result = _execute_case(CASES[1], tmp_path)
    declaration = _declaration(result["contract_a"])
    forward = recompose(declaration, child_outcomes=(result["c1"], result["c2"]))
    reverse = recompose(declaration, child_outcomes=(result["c2"], result["c1"]))
    assert forward == reverse


def test_native_child_result_mutation_changes_parent_receipt_binding(tmp_path: Path) -> None:
    result = _execute_case(CASES[0], tmp_path)
    declaration = _declaration(result["contract_a"])
    original = result["parent"]

    mutated_bytes = result["c1_bytes"] + b" "
    replacement = BoundAuditOutcome.create(
        proposition_id=result["c1"].proposition_id,
        text_sha256=result["c1"].text_sha256,
        audit_result_sha256=_tagged_bytes(mutated_bytes),
        conclusion=result["c1"].conclusion,
    )
    changed = recompose(declaration, child_outcomes=(replacement, result["c2"]))
    assert changed.conclusion is original.conclusion
    assert changed.receipt.receipt_id != original.receipt.receipt_id


def test_compatibility_carrier_mutation_is_downstream_of_native_eb_identity(
    tmp_path: Path,
) -> None:
    initial = _initial_package()
    package = build_package(
        contract_a=_contract_a(),
        config=INTEGRATION_CONFIG,
        admission=_admission(CASES[0], initial),
    )
    carrier = _carrier()
    mutated = deepcopy(carrier)
    mutated["source_profile"]["notes"] = "integration mutation control"

    first = project_contract_b(
        package=package,
        compatibility_carrier=carrier,
        out_dir=tmp_path / "first",
    )
    second = project_contract_b(
        package=package,
        compatibility_carrier=mutated,
        out_dir=tmp_path / "second",
    )

    assert first["native_package_sha256"] == second["native_package_sha256"]
    assert first["native_package_sha256"] == package["package_sha256"]
    assert first["compatibility_carrier_sha256"] != second["compatibility_carrier_sha256"]
    assert first["receipt_sha256"] != second["receipt_sha256"]


def test_contract_a_child_order_changes_parent_receipt_identity(tmp_path: Path) -> None:
    result = _execute_case(CASES[0], tmp_path)
    original = result["parent"]

    contract_a = deepcopy(result["contract_a"])
    children = contract_a["decomposition"]["children"]
    contract_a["decomposition"]["children"] = [
        {**children[1], "sequence": 1},
        {**children[0], "sequence": 2},
    ]
    declaration = _declaration(contract_a)
    changed = recompose(declaration, child_outcomes=(result["c1"], result["c2"]))

    assert changed.conclusion is original.conclusion
    assert changed.receipt.receipt_id != original.receipt.receipt_id
