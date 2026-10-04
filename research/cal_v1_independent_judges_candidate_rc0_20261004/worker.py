"""One-shot lane process. Reads the envelope from stdin and writes one receipt."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

_CANDIDATE = Path(__file__).resolve().parent
_REPO = _CANDIDATE.parents[1]
sys.path.insert(0, str(_CANDIDATE))
sys.path.insert(0, str(_REPO / "src"))

_FORBIDDEN = {"EXPECTATIONS.json", "SEMANTIC_CASES.json", "POLICY.json"}
_OPENED: set[str] = set()
_FORBIDDEN_READ = False


def _label(path: str) -> str:
    name = Path(path).name
    if name in _FORBIDDEN:
        return f"forbidden:{name}"
    text = path.replace("\\", "/")
    if "/site-packages/" in text:
        return "installed_dependency"
    if "/claim_audit_lab/" in text or "/claim_audit_lab.egg-info/" in text:
        return "cal_product_package"
    if "/cal_v1_independent_judges_candidate_rc0_20261004/" in text:
        return "candidate_module"
    if "/lib/python" in text or "/Python.framework/" in text:
        return "python_stdlib"
    if text.startswith("/System/Library/") or text.startswith("/usr/lib/"):
        return "platform_runtime"
    return "other"


def _install_trace() -> None:
    if os.environ.get("RC0_TRACE_OPEN") != "1":
        return

    def hook(event: str, args: tuple[Any, ...]) -> None:
        global _FORBIDDEN_READ
        if event != "open" or not args:
            return
        path = args[0]
        if isinstance(path, bytes):
            path = path.decode("utf-8", "replace")
        label = _label(str(path))
        _OPENED.add(label)
        if label.startswith("forbidden:"):
            _FORBIDDEN_READ = True

    sys.addaudithook(hook)


def _load(lane: str) -> Any:
    if lane == "kernel_legacy":
        from kernel_lane import judge
    elif lane == "original_relation":
        from comparison_relation import judge
    elif lane == "scope_guard":
        from constraint_guard import judge
    elif lane == "event_order":
        from event_order import judge
    else:
        raise ValueError("unknown lane")
    return judge


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lane", required=True)
    parser.add_argument("--crash", action="store_true")
    parser.add_argument("--sleep", type=float, default=0.0)
    args = parser.parse_args()
    raw = sys.stdin.buffer.read()
    if args.crash:
        raise SystemExit(3)
    if args.sleep:
        time.sleep(args.sleep)
    _install_trace()
    try:
        receipt = _load(args.lane)(raw)
    except Exception as exc:
        receipt = {
            "process_id": args.lane,
            "execution": "failed",
            "applicability": "unknown",
            "role": "relation",
            "conclusion": "unresolved",
            "warrant": "unqualified",
            "material_loss": False,
            "error": type(exc).__name__,
        }
    receipt["worker_pid"] = os.getpid()
    mark = os.environ.get("RC0_PRIVATE_MARK")
    if mark:
        receipt["private_mark"] = mark
    if os.environ.get("RC0_TRACE_OPEN") == "1":
        receipt["open_classes"] = sorted(_OPENED)
        receipt["forbidden_read"] = _FORBIDDEN_READ
    sys.stdout.write(json.dumps(receipt, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
