"""Pressure the frozen PR #96 event-order authority candidate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from research.cal_event_order_authority_rc0 import evaluate as parent


POSITIVE: tuple[tuple[str, str], ...] = (
    (
        "EOA-POS-01",
        "Talia reviewed packet u before Ravi signed ledger c.",
    ),
    (
        "EOA-POS-02",
        "Talia did not review packet u after Ravi signed ledger c.",
    ),
)

PRESSURE: tuple[tuple[str, str], ...] = (
    (
        "EOA-U01-REPORTING",
        "The report says Talia reviewed packet u before Ravi signed ledger c.",
    ),
    (
        "EOA-U02-EPISTEMIC",
        "Perhaps Talia reviewed packet u before Ravi signed ledger c.",
    ),
    (
        "EOA-U03-CONDITIONAL",
        "If Talia reviewed packet u before Ravi signed ledger c.",
    ),
    (
        "EOA-U04-RELATION-NEGATION",
        "Talia reviewed packet u not before Ravi signed ledger c.",
    ),
    (
        "EOA-U05-IMMEDIATE",
        "Talia reviewed packet u immediately before Ravi signed ledger c.",
    ),
    (
        "EOA-U06-SHORTLY",
        "Talia reviewed packet u shortly before Ravi signed ledger c.",
    ),
    (
        "EOA-U07-CAUSAL-TAIL",
        "Talia reviewed packet u before Ravi signed ledger c because QA requested it.",
    ),
    (
        "EOA-U08-THIRD-EVENT-AND",
        "Talia reviewed packet u before Ravi signed ledger c and Ivo released form j.",
    ),
    (
        "EOA-U09-THIRD-EVENT-OR",
        "Talia reviewed packet u before Ravi signed ledger c or Mona inspected batch w.",
    ),
    (
        "EOA-U10-MULTIPLE-CUES",
        "Talia reviewed packet u before Ravi signed ledger c after Mona inspected batch w.",
    ),
    (
        "EOA-U11-CALENDAR",
        "Before 2025, the registry was empty.",
    ),
    (
        "EOA-U12-NARRATIVE",
        "After lunch, the office reopened.",
    ),
)


def _observe(
    *,
    event_module: Any,
    rc8j_root: Path,
    case_id: str,
    source: str,
) -> dict[str, Any]:
    context = parent._context(case_id, source)
    receipt = parent._measure(event_module, context)
    observed = parent._completion_observation(
        context=context,
        receipt=receipt,
        rc8j_root=rc8j_root,
    )
    return {
        "case_id": case_id,
        "source": source,
        "measurement_status": receipt.measurement_status,
        "measurement_receipt_id": receipt.receipt_id,
        **observed,
    }


def execute(*, repo_root: Path, event_root: Path, rc8j_root: Path) -> dict[str, Any]:
    parent._require_candidate_blobs(repo_root)
    parent._require_dependency(
        event_root,
        parent.EVENT_HEAD,
        {parent.EVENT_PATH: parent.EVENT_BLOB},
    )
    parent._require_dependency(rc8j_root, parent.RC8J_HEAD, parent.RC8J_BLOBS)
    event = parent._load_module(
        "event_order_pressure_frozen_rc7fc",
        event_root / parent.EVENT_PATH,
    )

    positive_rows = [
        _observe(
            event_module=event,
            rc8j_root=rc8j_root,
            case_id=case_id,
            source=source,
        )
        for case_id, source in POSITIVE
    ]
    pressure_rows = [
        _observe(
            event_module=event,
            rc8j_root=rc8j_root,
            case_id=case_id,
            source=source,
        )
        for case_id, source in PRESSURE
    ]

    positive_failures = tuple(
        row["case_id"]
        for row in positive_rows
        if row["completion"] != "COMPLETED" or not row["warranted"]
    )
    completion_leaks = tuple(
        row["case_id"]
        for row in pressure_rows
        if row["completion"] == "COMPLETED"
    )
    unsafe_warrants = tuple(
        row["case_id"]
        for row in pressure_rows
        if row["warranted"]
    )

    disposition = (
        "SUPPORTED_EVENT_ORDER_AUTHORITY_PRESSURE_RC0"
        if not positive_failures and not completion_leaks and not unsafe_warrants
        else "FALSIFIED_EVENT_ORDER_AUTHORITY_PRESSURE_RC0"
    )
    return {
        "schema": "cal-event-order-authority-pressure-rc0-v1",
        "frozen_subject_head": "3a4b5f24f813843eae3857ed3444fb12b1cb8182",
        "research_disposition": disposition,
        "positive_failures": list(positive_failures),
        "semantic_completion_leaks": list(completion_leaks),
        "unsafe_warranted_leaks": list(unsafe_warrants),
        "positive_observations": positive_rows,
        "pressure_observations": pressure_rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--event-root", type=Path, required=True)
    parser.add_argument("--rc8j-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = execute(
        repo_root=args.repo_root.resolve(),
        event_root=args.event_root.resolve(),
        rc8j_root=args.rc8j_root.resolve(),
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "research_disposition": result["research_disposition"],
                "positive_failures": result["positive_failures"],
                "semantic_completion_leaks": result["semantic_completion_leaks"],
                "unsafe_warranted_leaks": result["unsafe_warranted_leaks"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
