"""Process-isolation probes. Refuses to overwrite an existing probe run."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

_CANDIDATE = Path(__file__).resolve().parent
_REPO = _CANDIDATE.parents[1]
sys.path.insert(0, str(_CANDIDATE))

from codec import canonical, digest
from dispatch import dispatch

_OUT = _CANDIDATE / "execution" / "isolation-01"


def _git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(_REPO), *args], text=True).strip()


def _source_dirty() -> str:
    """Receipts under execution/ are outputs. Any other dirt means the freeze moved."""
    allowed = "research/cal_v1_independent_judges_candidate_rc0_20261004/execution/"
    bad: list[str] = []
    for line in _git("status", "--porcelain", "-uall").splitlines():
        if not line.strip():
            continue
        path = line[3:]
        if line.startswith("?? ") and (path == allowed[:-1] or path.startswith(allowed)):
            continue
        bad.append(line)
    return "\n".join(bad)


def _project(receipt: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in receipt.items()
        if key not in {"worker_pid", "private_mark", "open_classes", "forbidden_read"}
    }


def _require(label: str, condition: bool, failures: list[str]) -> None:
    if not condition:
        failures.append(label)


def main() -> int:
    if _OUT.exists():
        raise SystemExit("isolation-01 already exists; refusing to overwrite the first probe")
    if _source_dirty():
        raise SystemExit("candidate tree is dirty; freeze the candidate before the isolation probe")
    head = _git("rev-parse", "HEAD")
    raw = canonical(
        {
            "claim": "Gamma had a higher score than Delta.",
            "evidence": [{"id": "p", "text": "Gamma had a higher score than Delta."}],
        }
    )
    other = canonical(
        {
            "claim": "Gamma had a lower score than Delta.",
            "evidence": [{"id": "p", "text": "Gamma had a higher score than Delta."}],
        }
    )
    failures: list[str] = []
    baseline = dispatch(raw, trace_open=True)
    _require("four lanes", len(baseline) == 4, failures)
    _require("all bound", all(item["binding_ok"] for item in baseline), failures)
    _require("same bytes", all(item["supplied_sha256"] == digest(raw) for item in baseline), failures)
    pids = [item["worker_pid"] for item in baseline]
    _require("distinct pids", len(set(pids)) == 4, failures)
    _require("no forbidden reads", all(not item["forbidden_read"] for item in baseline), failures)
    _require(
        "open classes known",
        all(
            set(item.get("open_classes") or []).issubset(
                {
                    "candidate_module",
                    "python_stdlib",
                    "installed_dependency",
                    "cal_product_package",
                    "platform_runtime",
                }
            )
            for item in baseline
        ),
        failures,
    )
    reversed_run = dispatch(raw, order=("event_order", "scope_guard", "original_relation", "kernel_legacy"))
    forward = sorted((_project(item["receipt"]) for item in baseline), key=lambda row: row["process_id"])
    backward = sorted((_project(item["receipt"]) for item in reversed_run), key=lambda row: row["process_id"])
    _require("order invariant", forward == backward, failures)

    marked = dispatch(raw, lane_env={"event_order": {"RC0_PRIVATE_MARK": "lane-local"}})
    event = next(item for item in marked if item["process_id"] == "event_order")
    others = [item for item in marked if item["process_id"] != "event_order"]
    _require("private mark stays on one lane", event["receipt"].get("private_mark") == "lane-local", failures)
    _require("other lanes unmarked", all("private_mark" not in item["receipt"] for item in others), failures)
    unmarked = {item["process_id"]: _project(item["receipt"]) for item in baseline}
    for item in others:
        _require(
            f"mark did not change {item['process_id']}",
            _project(item["receipt"]) == unmarked[item["process_id"]],
            failures,
        )

    crashed = dispatch(raw, lane_args={"original_relation": ["--crash"]})
    crash = next(item for item in crashed if item["process_id"] == "original_relation")
    _require("crash is failed execution", crash["state"] == "failed", failures)
    _require("crash is not not_applicable", crash["receipt"]["applicability"] != "not_applicable", failures)
    _require(
        "crash does not starve",
        all(item["binding_ok"] for item in crashed if item["process_id"] != "original_relation"),
        failures,
    )

    timed = dispatch(
        raw,
        lane_args={"scope_guard": ["--sleep", "5"]},
        lane_timeouts={"scope_guard": 0.4},
    )
    timeout = next(item for item in timed if item["process_id"] == "scope_guard")
    _require("timeout state", timeout["state"] == "timeout", failures)
    _require("timeout receipt distinct", timeout["receipt"]["execution"] == "timeout", failures)
    _require(
        "timeout does not starve",
        all(item["binding_ok"] for item in timed if item["process_id"] != "scope_guard"),
        failures,
    )

    second = dispatch(other, order=("original_relation",))
    _require(
        "no stale stdin",
        second[0]["receipt"]["input_sha256"] == digest(other)
        and second[0]["receipt"]["input_sha256"] != digest(raw),
        failures,
    )
    consumed = second[0]["receipt"].get("consumed_passage_ids", [])
    _require("consumed ids are declared", set(consumed).issubset({"p"}), failures)

    _OUT.parent.mkdir(parents=True, exist_ok=True)
    _OUT.mkdir(parents=False)
    report = {
        "evidence_class": "PROCESS_ISOLATION_PROBE_NOT_SEMANTIC_UTILITY",
        "candidate_commit": head,
        "models_used": False,
        "failures": failures,
        "passed": not failures,
        "pids_distinct": len(set(pids)) == 4,
        "notes": [
            "Children ran with cwd outside the repository and an environment that does not inherit the parent.",
            "A receipt hash was checked against the bytes the parent wrote.",
            "Timeout remains timeout rather than not_applicable or failed.",
            "not_run is not produced here; the routed arm records not_run separately.",
        ],
    }
    (_OUT / "REPORT.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"passed": report["passed"], "failures": failures}, sort_keys=True))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
