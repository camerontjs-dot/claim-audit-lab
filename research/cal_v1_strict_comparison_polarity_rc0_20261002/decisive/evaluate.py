"""Decisive evaluator for the strict-comparison polarity successor.

The sibling CASES.json file is the frozen case identity. This runner executes
the real CAL authoring and audit path and writes one result file. It does not
repair cases, expectations, or semantic outcomes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import warnings
from pathlib import Path
from typing import Any

warnings.filterwarnings(
    "ignore",
    message=r'Field name "schema" in "ContractBFactualContext"',
)

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from claim_audit_lab.production_v1.semantic.engine import audit  # noqa: E402
from claim_audit_lab.production_v1.semantic.models import (  # noqa: E402
    AdmittedPassage,
    AuditContext,
    EvidenceWorld,
    SemanticFamily,
    TypedProposition,
)
from claim_audit_lab.production_v1.targeting import TargetAuthoringError, author_target  # noqa: E402

CASE_FIELDS = (
    "measurement_status",
    "polarity_diagnostic",
    "authority_present",
    "assertion_polarity",
    "left",
    "relation",
    "right",
    "categorical_relation",
)


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()


def _load_cases(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    cases = payload.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("decisive cases payload is empty")
    seen: set[str] = set()
    for case in cases:
        case_id = case.get("case_id")
        if not isinstance(case_id, str) or case_id in seen:
            raise ValueError(f"duplicate or blank case_id: {case_id}")
        seen.add(case_id)
        if not isinstance(case.get("evidence"), list) or not case["evidence"]:
            raise ValueError(f"{case_id} has no evidence")
    return payload


def _passage_observation(trace: Any) -> dict[str, Any]:
    measurement = trace.measurement
    raw = measurement.raw_measurement() if measurement is not None else {}
    proposals = raw.get("proposals")
    proposal = proposals[0] if isinstance(proposals, list) and len(proposals) == 1 else None
    if not isinstance(proposal, dict):
        proposal = None
    diagnostics = dict(measurement.diagnostics) if measurement is not None else {}
    atom = trace.authority.atom.field_map() if trace.authority is not None else None
    relation = trace.relation.categorical_relation.value if trace.relation is not None else None
    return {
        "passage_id": trace.passage_id,
        "measurement_status": raw.get("status"),
        "polarity_diagnostic": diagnostics.get("polarity"),
        "proposal": proposal,
        "atom_fields": atom,
        "categorical_relation": relation,
        "failure_code": None if trace.failure_code is None else trace.failure_code.value,
        "detail": trace.detail,
        "instrument_id": None if measurement is None else measurement.instrument_id,
        "instrument_version": None if measurement is None else measurement.instrument_version,
    }


def _observed_value(passage: dict[str, Any], field: str) -> Any:
    atom = passage.get("atom_fields") or {}
    if field == "measurement_status":
        return passage.get("measurement_status")
    if field == "polarity_diagnostic":
        return passage.get("polarity_diagnostic")
    if field == "authority_present":
        return passage.get("atom_fields") is not None
    if field == "categorical_relation":
        return passage.get("categorical_relation")
    if field in {"assertion_polarity", "left", "relation", "right"}:
        return atom.get(field)
    raise KeyError(field)


def _execute_case(case: dict[str, Any]) -> dict[str, Any]:
    claim = case["claim"]
    target = author_target(case["case_id"], claim)
    family = target["proposition"]["semantic_family"]
    if family != SemanticFamily.STRICT_COMPARISON.value:
        raise ValueError(f"{case['case_id']} authored {family}")
    proposition = TypedProposition.create(
        target["proposition"]["proposition_id"],
        SemanticFamily.STRICT_COMPARISON,
        target["proposition"]["fields"],
        text_sha256=target["proposition"]["text_sha256"],
    )
    passages = tuple(
        AdmittedPassage.create(
            f"p{index}",
            f"s{index}",
            text,
            "sha256:" + _sha256(f"source-{index}".encode()),
        )
        for index, text in enumerate(case["evidence"])
    )
    world = EvidenceWorld.create(
        "1.2.0",
        "cal190-polarity-rc0",
        "sha256:" + _sha256(b"cal190-polarity-rc0"),
        passages,
        {
            "contract_b_factual_context_state": "present",
            "observation": {"scope": "strict-comparison-polarity-rc0"},
        },
    )
    result = audit(AuditContext(claim, proposition, world))
    observed_passages = [_passage_observation(trace) for trace in result.traces]
    mismatches: list[dict[str, Any]] = []
    if result.conclusion.value != case["expected_conclusion"]:
        mismatches.append(
            {
                "field": "conclusion",
                "expected": case["expected_conclusion"],
                "observed": result.conclusion.value,
            }
        )
    expected_passages = case.get("expected_passages")
    if expected_passages is not None:
        if len(expected_passages) != len(observed_passages):
            mismatches.append(
                {
                    "field": "passage_count",
                    "expected": len(expected_passages),
                    "observed": len(observed_passages),
                }
            )
        else:
            for index, expected in enumerate(expected_passages):
                observed = observed_passages[index]
                for field in CASE_FIELDS:
                    if field not in expected:
                        continue
                    actual = _observed_value(observed, field)
                    if actual != expected[field]:
                        mismatches.append(
                            {
                                "passage_index": index,
                                "field": field,
                                "expected": expected[field],
                                "observed": actual,
                            }
                        )
                proposal = observed.get("proposal") or {}
                atom = observed.get("atom_fields") or {}
                if (
                    "assertion_polarity" in proposal
                    and "assertion_polarity" in atom
                    and proposal["assertion_polarity"] != atom["assertion_polarity"]
                ):
                    mismatches.append(
                        {
                            "passage_index": index,
                            "field": "polarity_boundary",
                            "expected": proposal["assertion_polarity"],
                            "observed": atom["assertion_polarity"],
                        }
                    )
    return {
        "case_id": case["case_id"],
        "role": case["role"],
        "property": case.get("property"),
        "frozen_controls": case.get("frozen_controls", []),
        "claim": claim,
        "evidence": case["evidence"],
        "authored_fields": target["proposition"]["fields"],
        "expected_conclusion": case["expected_conclusion"],
        "observed_conclusion": result.conclusion.value,
        "failure_code": None if result.failure_code is None else result.failure_code.value,
        "passages": observed_passages,
        "mismatches": mismatches,
        "matched": not mismatches,
    }


def evaluate(cases_path: Path) -> dict[str, Any]:
    payload = _load_cases(cases_path)
    rows: list[dict[str, Any]] = []
    apparatus: list[dict[str, str]] = []
    for case in payload["cases"]:
        try:
            rows.append(_execute_case(case))
        except (TargetAuthoringError, OSError, ValueError, subprocess.CalledProcessError) as exc:
            apparatus.append(
                {
                    "case_id": str(case.get("case_id")),
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                }
            )
            rows.append(
                {
                    "case_id": case.get("case_id"),
                    "role": case.get("role"),
                    "matched": False,
                    "apparatus_error": f"{type(exc).__name__}: {exc}",
                }
            )
    matched = [row for row in rows if row.get("matched") is True]
    failed = [row for row in rows if row.get("matched") is not True]
    if apparatus:
        disposition = "INCONCLUSIVE_APPARATUS_INVALID"
    elif failed:
        disposition = "FALSIFIED_REPRESENTATION_INSUFFICIENT"
    else:
        disposition = "SUPPORTED_FOR_POLARITY_SUCCESSOR_QUALIFICATION"
    return {
        "schema": "cal-v1-strict-comparison-polarity-rc0-decisive-result",
        "head": _git("rev-parse", "HEAD"),
        "tree": _git("rev-parse", "HEAD^{tree}"),
        "cases_sha256": _sha256(cases_path.read_bytes()),
        "evaluator_sha256": _sha256(Path(__file__).read_bytes()),
        "case_count": len(rows),
        "matched_count": len(matched),
        "failed_count": len(failed),
        "apparatus_errors": apparatus,
        "mechanical_disposition": disposition,
        "results": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, default=Path(__file__).with_name("CASES.json"))
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    destination = args.out.resolve()
    if destination.exists():
        print(f"refusing to overwrite decisive output: {destination}", file=sys.stderr)
        return 2
    try:
        report = evaluate(args.cases.resolve())
    except Exception as exc:
        destination.mkdir(parents=True, exist_ok=False)
        failure = {
            "schema": "cal-v1-strict-comparison-polarity-rc0-decisive-result",
            "mechanical_disposition": "INCONCLUSIVE_APPARATUS_INVALID",
            "error_type": type(exc).__name__,
            "error": str(exc),
        }
        (destination / "decisive-result.json").write_text(
            json.dumps(failure, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    destination.mkdir(parents=True, exist_ok=False)
    (destination / "decisive-result.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        f"{report['mechanical_disposition']} "
        f"{report['matched_count']}/{report['case_count']}"
    )
    return 0 if report["mechanical_disposition"].startswith("SUPPORTED") else 1


if __name__ == "__main__":
    raise SystemExit(main())
