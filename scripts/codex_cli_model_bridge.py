"""Execute a prepared Gold Lite request through a cold Codex CLI session."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REQUEST_SCHEMA = "gold-lite-portable-model-request-v0.1"
RECEIPT_SCHEMA = "gold-lite-portable-model-receipt-v0.1"


def run_prepared_request(
    request_path: Path,
    out_path: Path,
    events_path: Path,
    *,
    codex_bin: str,
    reasoning_effort: str,
) -> dict[str, Any]:
    """Run one stateless, no-tools Codex annotation and preserve its raw events."""
    _preflight_paths(request_path, out_path, events_path)
    request = _load_json_object(request_path)
    if request.get("schema_version") != REQUEST_SCHEMA:
        raise ValueError("unsupported portable request schema")
    if request.get("provider") != "codex-cli":
        raise ValueError("Codex bridge only accepts provider=codex-cli")
    model_id = request.get("model_id")
    if not isinstance(model_id, str) or not model_id:
        raise ValueError("portable request is missing model_id")
    output_schema = request.get("output_schema")
    if not isinstance(output_schema, dict):
        raise ValueError("portable request is missing output_schema")
    prompt = _combined_prompt(request)

    with tempfile.TemporaryDirectory(prefix="cal-gold-lite-codex-") as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        schema_path = temp_dir / "output-schema.json"
        message_path = temp_dir / "last-message.json"
        schema_path.write_text(
            json.dumps(output_schema, sort_keys=True, ensure_ascii=False),
            encoding="utf-8",
        )
        command = [
            codex_bin,
            "exec",
            "--ignore-user-config",
            "--ignore-rules",
            "--ephemeral",
            "--skip-git-repo-check",
            "--sandbox",
            "read-only",
            "-C",
            str(temp_dir),
            "-m",
            model_id,
            "-c",
            f'model_reasoning_effort="{reasoning_effort}"',
            "--output-schema",
            str(schema_path),
            "--output-last-message",
            str(message_path),
            "--json",
            "-",
        ]
        completed = subprocess.run(
            command,
            input=prompt,
            text=True,
            capture_output=True,
            check=False,
        )
        response_text = message_path.read_text(encoding="utf-8") if message_path.is_file() else ""

    event_violations = _tool_event_violations(completed.stdout)
    _write_new(events_path, completed.stdout)
    called_at = datetime.now(UTC).isoformat()
    if event_violations:
        finish_reason = "protocol_violation"
    elif completed.returncode == 0 and response_text:
        finish_reason = "completed"
    else:
        finish_reason = "error"
    receipt = {
        "schema_version": RECEIPT_SCHEMA,
        "request_sha256": _canonical_sha256(request),
        "called_at_utc": called_at,
        "provider": "codex-cli",
        "model_id": model_id,
        "finish_reason": finish_reason,
        "response_text": response_text,
        "response_sha256": _sha256_text(response_text),
        "usage": _usage_from_events(completed.stdout),
        "runtime": {
            "codex_binary": codex_bin,
            "bridge_script_sha256": _sha256_file(Path(__file__)),
            "reasoning_effort": reasoning_effort,
            "returncode": completed.returncode,
            "max_output_tokens_enforced": False,
            "events_sha256": _sha256_text(completed.stdout),
            "rendered_input_sha256": _sha256_text(prompt),
            "tool_event_audit": {
                "status": "failed" if event_violations else "passed",
                "violations": event_violations,
            },
            "stderr": completed.stderr,
            "constraints": (
                "ephemeral; ignored user rules/config; read-only sandbox; JSONL event stream "
                "audited for tool-bearing items"
            ),
        },
    }
    _write_json_new(out_path, receipt)
    if event_violations:
        raise RuntimeError(
            "Codex CLI emitted prohibited or unauditable events; "
            f"raw receipt preserved at {out_path}"
        )
    if completed.returncode != 0:
        raise RuntimeError(
            f"Codex CLI returned {completed.returncode}; raw receipt preserved at {out_path}"
        )
    return receipt


def _preflight_paths(request_path: Path, out_path: Path, events_path: Path) -> None:
    resolved = [path.resolve() for path in (request_path, out_path, events_path)]
    if len(set(resolved)) != 3:
        raise ValueError("request, receipt, and events paths must be distinct")
    for path in (out_path, events_path):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite existing receipt: {path}")


def _tool_event_violations(events: str) -> list[str]:
    """Fail closed when Codex events contain tool work or cannot be audited."""
    allowed_item_types = {"agent_message", "reasoning"}
    allowed_event_types = {
        "thread.started",
        "turn.started",
        "item.started",
        "item.completed",
        "turn.completed",
    }
    forbidden_terms = ("tool", "command", "shell", "exec", "web", "browser", "mcp", "file")
    violations: list[str] = []
    parsed_events = 0
    agent_messages = 0
    completed_turns = 0
    for line_number, line in enumerate(events.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            violations.append(f"line {line_number}: invalid JSON event")
            continue
        if not isinstance(event, dict):
            violations.append(f"line {line_number}: event is not an object")
            continue
        parsed_events += 1
        event_type = event.get("type")
        if not isinstance(event_type, str):
            violations.append(f"line {line_number}: event type is missing")
        elif event_type not in allowed_event_types:
            violations.append(f"line {line_number}: unrecognized event type {event_type!r}")
        elif any(term in event_type.lower() for term in forbidden_terms):
            violations.append(f"line {line_number}: prohibited event type {event_type!r}")
        if event_type == "turn.completed":
            completed_turns += 1
        item = event.get("item")
        if isinstance(event_type, str) and event_type.startswith("item.") and item is None:
            violations.append(f"line {line_number}: item lifecycle event is missing its item")
        elif item is not None:
            if not isinstance(item, dict):
                violations.append(f"line {line_number}: event item is not an object")
                continue
            item_type = item.get("type")
            if item_type not in allowed_item_types:
                violations.append(f"line {line_number}: prohibited item type {item_type!r}")
            elif item_type == "agent_message" and event_type == "item.completed":
                agent_messages += 1
    if parsed_events == 0:
        violations.append("event stream contains no auditable JSON events")
    if agent_messages == 0:
        violations.append("event stream contains no completed agent_message item")
    if completed_turns == 0:
        violations.append("event stream contains no turn.completed event")
    return violations


def _combined_prompt(request: dict[str, Any]) -> str:
    system_prompt = request.get("system_prompt")
    user_prompt = request.get("user_prompt")
    if not isinstance(system_prompt, str) or not isinstance(user_prompt, str):
        raise ValueError("portable request must contain string system_prompt and user_prompt")
    return f"""You are completing one sealed annotation request. Do not call tools, browse,
inspect files, consult memory, or ask questions. Use only the packet text below. Return the final
JSON object and nothing else.

<system_instruction>
{system_prompt}
</system_instruction>

<user_message>
{user_prompt}
</user_message>
"""


def _usage_from_events(events: str) -> dict[str, Any] | None:
    usage: dict[str, Any] | None = None
    for line in events.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue
        candidate = event.get("usage")
        if isinstance(candidate, dict):
            usage = candidate
        turn = event.get("turn")
        if isinstance(turn, dict) and isinstance(turn.get("usage"), dict):
            usage = turn["usage"]
    return usage


def _load_json_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"could not load prepared request {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError("prepared request must be a JSON object")
    return value


def _canonical_sha256(value: Any) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return _sha256_text(encoded)


def _sha256_text(value: str) -> str:
    return f"sha256:{hashlib.sha256(value.encode('utf-8')).hexdigest()}"


def _sha256_file(path: Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def _write_new(path: Path, text: str) -> None:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite existing receipt: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json_new(path: Path, value: Any) -> None:
    _write_new(path, json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--events", type=Path, required=True)
    parser.add_argument("--codex-bin", default="codex")
    parser.add_argument(
        "--reasoning-effort",
        choices=["none", "minimal", "low", "medium", "high", "xhigh"],
        default="low",
    )
    return parser


def main() -> None:
    args = _parser().parse_args()
    try:
        receipt = run_prepared_request(
            args.request,
            args.out,
            args.events,
            codex_bin=args.codex_bin,
            reasoning_effort=args.reasoning_effort,
        )
    except (FileExistsError, RuntimeError, ValueError) as exc:
        raise SystemExit(str(exc)) from exc
    print(f"model: {receipt['model_id']}")
    print(f"finish_reason: {receipt['finish_reason']}")
    print(f"wrote: {args.out}")


if __name__ == "__main__":
    main()
