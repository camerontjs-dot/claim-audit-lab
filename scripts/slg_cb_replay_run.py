"""E4 Unit 4 step 2: run CAL through the C-B loader and compare with the direct lane.

Loads each lane's sealed Evidence Bundler packet through CAL's existing
fail-closed C-B intake (``build_request_index``), audits every atom claim with
the real pinned pipeline, and compares the observed relation per atom against
the preserved direct-evidence outcomes from the Unit 3b pair-invariance run.
Every direct-versus-C-B difference is listed as a retrieval/bundling
diagnostic, never merged into one accuracy number. DEV evidence, never a gate.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from claim_audit_lab.v1.config import load_default_audit_config
from claim_audit_lab.v1.runner import run_default_audit

try:
    from scripts.pilot001_premise_granularity_run04 import build_request_index
    from scripts.simple_logic_gold_direct_lane import _map_cal_verdict
except ModuleNotFoundError as exc:
    if exc.name != "scripts":
        raise
    from pilot001_premise_granularity_run04 import (  # type: ignore[no-redef]
        build_request_index,
    )
    from simple_logic_gold_direct_lane import _map_cal_verdict  # type: ignore[no-redef]


def replay_lane(packet: Path, config: Any) -> dict[str, dict[str, Any]]:
    """Audit every bundled atom claim through the real pipeline; key by claim_id."""
    requests = build_request_index(packet, config)
    lane: dict[str, dict[str, Any]] = {}
    for claim_id, request in sorted(requests.items()):
        trace = run_default_audit(request)
        lane[claim_id] = {
            "cb_support_verdict": trace.verdict.support_verdict,
            "cb_support_verdict_reason": trace.verdict.support_verdict_reason,
            "cb_observed_relation": _map_cal_verdict(trace.verdict.support_verdict),
            "cb_flags": list(trace.verdict.audit_flags),
            "cb_passage_count": len(request.passages),
            "trace": trace.model_dump(mode="json"),
        }
    return lane


def compare(direct_run: dict[str, Any], cb_lane: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Per-atom direct vs C-B relations with differences as diagnostics."""
    rows = []
    diagnostics = []
    for atom in direct_run["atoms"]:
        atom_id = atom["atom_id"]
        cb = cb_lane[atom_id]
        same = atom["cal_observed_relation"] == cb["cb_observed_relation"]
        row = {
            "atom_id": atom_id,
            "expected_relation": atom["expected_relation"],
            "direct_observed": atom["cal_observed_relation"],
            "cb_observed": cb["cb_observed_relation"],
            "same_outcome": same,
        }
        rows.append(row)
        if not same:
            diagnostics.append(
                {
                    **row,
                    "cb_reason": cb["cb_support_verdict_reason"],
                    "cb_flags": cb["cb_flags"],
                    "note": "retrieval/bundling diagnostic — not merged into accuracy",
                }
            )
    return {
        "atoms": rows,
        "diagnostics": diagnostics,
        "summary": {
            "atoms": len(rows),
            "same_outcome": sum(r["same_outcome"] for r in rows),
            "differences": len(diagnostics),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packets", type=Path, required=True)
    parser.add_argument("--pair-run", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    config = load_default_audit_config()
    payload: dict[str, Any] = {
        "schema_version": "slg-cb-replay-v0.1",
        "label": "DEV diagnostic only; not validation or gate evidence",
        "lanes": {},
    }
    for lane_name, run_file in (("plain", "plain-run.json"), ("domain", "domain-run.json")):
        direct_run = json.loads((args.pair_run / run_file).read_text(encoding="utf-8"))
        first = replay_lane(args.packets / lane_name, config)
        second = replay_lane(args.packets / lane_name, config)
        if json.dumps(first, sort_keys=True) != json.dumps(second, sort_keys=True):
            raise ValueError(f"{lane_name}: C-B replay is not repeat-identical")
        payload["lanes"][lane_name] = {
            "comparison": compare(direct_run, first),
            "traces": {claim_id: record["trace"] for claim_id, record in first.items()},
        }

    args.out.mkdir(parents=True, exist_ok=True)
    target = args.out / "cb-comparison.json"
    text = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if target.exists() and target.read_text(encoding="utf-8") != text:
        raise FileExistsError(f"refusing to replace non-identical output: {target}")
    target.write_text(text, encoding="utf-8")
    print(
        json.dumps(
            {lane: data["comparison"]["summary"] for lane, data in payload["lanes"].items()},
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
