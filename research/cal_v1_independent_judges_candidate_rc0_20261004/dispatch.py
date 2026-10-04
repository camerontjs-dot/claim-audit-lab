"""Process-isolated dispatch. Each lane receives only the supplied bytes."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from codec import digest

_CANDIDATE = Path(__file__).resolve().parent
_REPO = _CANDIDATE.parents[1]
_WORKER = _CANDIDATE / "worker.py"
LANES = (
    ("kernel_legacy", "relation"),
    ("original_relation", "relation"),
    ("scope_guard", "guard"),
    ("event_order", "relation"),
)


def child_env(extra: dict[str, str] | None = None) -> dict[str, str]:
    env = {
        "PATH": "/usr/bin:/bin",
        "PYTHONNOUSERSITE": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONPATH": str(_REPO / "src"),
        "LC_ALL": "C.UTF-8",
        "LANG": "C.UTF-8",
    }
    if extra:
        env.update(extra)
    return env


def redact(text: str) -> str:
    cleaned = text.replace(str(_REPO), "<repo>").replace(str(_CANDIDATE), "<candidate>")
    if "/Users/" in cleaned or "/tmp/" in cleaned or "/private/" in cleaned:
        cleaned = "<path-redacted>"
    return cleaned


def run_lane(
    raw: bytes,
    lane: str,
    *,
    role: str,
    python: str,
    extra_env: dict[str, str] | None = None,
    extra_args: list[str] | None = None,
    timeout: float = 30.0,
) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="cal-lane-") as work:
        try:
            completed = subprocess.run(
                [python, str(_WORKER), "--lane", lane, *(extra_args or [])],
                input=raw,
                capture_output=True,
                cwd=work,
                env=child_env(extra_env),
                timeout=timeout,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            return {
                "process_id": lane,
                "role": role,
                "state": "timeout",
                "supplied_sha256": digest(raw),
                "returncode": None,
                "binding_ok": False,
                "stderr": redact((exc.stderr or b"").decode("utf-8", "replace")[:500]),
                "receipt": _state_receipt(lane, role, raw, "timeout"),
            }
    stderr = redact(completed.stderr.decode("utf-8", "replace")[:500])
    if completed.returncode != 0 or not completed.stdout:
        return {
            "process_id": lane,
            "role": role,
            "state": "failed",
            "supplied_sha256": digest(raw),
            "returncode": completed.returncode,
            "binding_ok": False,
            "stderr": stderr,
            "receipt": _state_receipt(lane, role, raw, "failed"),
        }
    try:
        receipt = json.loads(completed.stdout.decode("utf-8"))
    except json.JSONDecodeError:
        return {
            "process_id": lane,
            "role": role,
            "state": "failed",
            "supplied_sha256": digest(raw),
            "returncode": completed.returncode,
            "binding_ok": False,
            "stderr": stderr,
            "receipt": _state_receipt(lane, role, raw, "failed"),
        }
    binding_ok = receipt.get("input_sha256") == digest(raw)
    state = "completed" if binding_ok else "failed"
    if not binding_ok:
        receipt = _state_receipt(lane, role, raw, "failed")
        receipt["error"] = "input_binding_mismatch"
    return {
        "process_id": lane,
        "role": role,
        "state": state,
        "supplied_sha256": digest(raw),
        "returncode": completed.returncode,
        "binding_ok": binding_ok,
        "stderr": stderr,
        "receipt": receipt,
        "worker_pid": receipt.get("worker_pid"),
        "open_classes": receipt.get("open_classes", []),
        "forbidden_read": receipt.get("forbidden_read", False),
    }


def _state_receipt(lane: str, role: str, raw: bytes, execution: str) -> dict[str, Any]:
    conclusion = "unresolved"
    applicability = "unknown"
    if execution == "timeout":
        conclusion = "unresolved"
        applicability = "unknown"
    return {
        "process_id": lane,
        "input_sha256": digest(raw),
        "execution": execution if execution in {"failed", "timeout"} else "failed",
        "applicability": applicability,
        "role": role,
        "conclusion": conclusion,
        "warrant": "unqualified",
        "material_loss": False,
        "state": execution,
    }


def dispatch(
    raw: bytes,
    *,
    python: str | None = None,
    order: tuple[str, ...] | None = None,
    lane_env: dict[str, dict[str, str]] | None = None,
    lane_args: dict[str, list[str]] | None = None,
    timeout: float = 30.0,
    lane_timeouts: dict[str, float] | None = None,
    trace_open: bool = False,
) -> list[dict[str, Any]]:
    """Run the requested lanes in order. Each child starts only after the previous receipt is stored."""
    selected = order or tuple(lane for lane, _role in LANES)
    roles = dict(LANES)
    interpreter = python or sys.executable
    sealed: list[dict[str, Any]] = []
    for lane in selected:
        extra = dict((lane_env or {}).get(lane, {}))
        if trace_open:
            extra["RC0_TRACE_OPEN"] = "1"
        sealed.append(
            run_lane(
                raw,
                lane,
                role=roles[lane],
                python=interpreter,
                extra_env=extra,
                extra_args=(lane_args or {}).get(lane),
                timeout=(lane_timeouts or {}).get(lane, timeout),
            )
        )
    return sealed
