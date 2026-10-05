"""Process-isolated dispatch. Each child receives only the supplied bytes."""

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
_WORKER = _CANDIDATE / "worker.py"
_KERNEL = _CANDIDATE / "kernel_worker.py"
ROLES = {
    "quantity_relation": "relation",
    "event_order": "relation",
    "scope_guard": "guard",
    "attribution_guard": "guard",
    "kernel_legacy": "relation",
}


def _env() -> dict[str, str]:
    env = {
        "PATH": "/usr/bin:/bin",
        "PYTHONNOUSERSITE": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
        "LC_ALL": "C.UTF-8",
        "LANG": "C.UTF-8",
    }
    prompt = os.environ.get("CAL_PROMPT_NAME")
    if prompt:
        env["CAL_PROMPT_NAME"] = prompt
    return env


def run_process(
    raw: bytes,
    *,
    lane: str,
    process_id: str | None = None,
    self_score: bool = False,
    python: str | None = None,
    timeout: float = 30.0,
) -> dict[str, Any]:
    identity = process_id or lane
    role = ROLES[lane if lane in ROLES else "quantity_relation"]
    if lane == "kernel_legacy":
        command = [python or sys.executable, str(_KERNEL)]
    else:
        command = [python or sys.executable, str(_WORKER), "--lane", lane]
        if process_id:
            command.extend(["--process-id", process_id])
        if self_score:
            command.append("--self-score")
        role = ROLES[lane]
    with tempfile.TemporaryDirectory(prefix="cal-rc1-") as work:
        try:
            completed = subprocess.run(
                command,
                input=raw,
                capture_output=True,
                cwd=work,
                env=_env(),
                timeout=timeout,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return _failed(identity, role, raw, "timeout")
    if completed.returncode != 0 or not completed.stdout:
        return _failed(identity, role, raw, "failed")
    try:
        receipt = json.loads(completed.stdout.decode("utf-8"))
    except json.JSONDecodeError:
        return _failed(identity, role, raw, "failed")
    if receipt.get("input_sha256") != digest(raw):
        failed = _failed(identity, role, raw, "failed")
        failed["receipt"]["error"] = "input_binding_mismatch"
        return failed
    return {
        "process_id": identity,
        "state": "completed",
        "supplied_sha256": digest(raw),
        "returncode": completed.returncode,
        "binding_ok": True,
        "receipt": receipt,
    }


def _failed(process_id: str, role: str, raw: bytes, state: str) -> dict[str, Any]:
    receipt = {
        "process_id": process_id,
        "input_sha256": digest(raw),
        "execution": "failed" if state == "failed" else "timeout",
        "applicability": "unknown",
        "role": role,
        "conclusion": "unresolved",
        "warrant": "unqualified",
        "material_loss": False,
    }
    return {
        "process_id": process_id,
        "state": state,
        "supplied_sha256": digest(raw),
        "returncode": None,
        "binding_ok": False,
        "receipt": receipt,
    }


def not_run(process_id: str, role: str, raw: bytes) -> dict[str, Any]:
    receipt = {
        "process_id": process_id,
        "input_sha256": digest(raw),
        "execution": "not_run",
        "applicability": "not_run",
        "role": role,
        "conclusion": "not_run",
        "warrant": "qualified",
        "material_loss": False,
        "reason": "router_did_not_select_this_process",
    }
    return {
        "process_id": process_id,
        "state": "not_run",
        "supplied_sha256": digest(raw),
        "returncode": None,
        "binding_ok": True,
        "receipt": receipt,
    }
