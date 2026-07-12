"""Run one prepared Anthropic Messages API request through the research harness runtime.

This bridge deliberately owns no CAL judgement logic. It loads the API credential from
the Basic Research Harness environment, counts the prepared input, performs exactly one
Messages API call, and preserves the raw response in an additive file.

Usage::

    <basic-research-harness>/anthropic-env/bin/python \
      scripts/anthropic_api_bridge.py \
      --request <prepared-request.json> \
      --response <new-raw-response.json> \
      --env-file <basic-research-harness>/.env
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

BRIDGE_SCHEMA = "anthropic-api-bridge-response-v0.1"


def canonical_sha256(value: Any) -> str:
    """Hash JSON data without depending on presentation whitespace."""
    canonical = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return f"sha256:{hashlib.sha256(canonical.encode('utf-8')).hexdigest()}"


def run_prepared_request(
    request_path: Path,
    response_path: Path,
    *,
    env_file: Path,
    max_input_tokens: int,
    client: Any | None = None,
) -> dict[str, Any]:
    """Count and execute exactly one prepared request, refusing any overwrite."""
    if response_path.exists():
        raise FileExistsError(f"refusing to overwrite API response: {response_path}")
    try:
        request_body = json.loads(request_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"could not load prepared request {request_path}: {exc}") from exc
    if not isinstance(request_body, dict):
        raise ValueError("prepared Anthropic request must be a JSON object")

    if client is None:
        from anthropic import Anthropic
        from dotenv import load_dotenv

        loaded = load_dotenv(env_file, override=False)
        if not loaded:
            raise ValueError(f"could not load Anthropic environment file: {env_file}")
        client = Anthropic()

    count_body = {
        key: value
        for key, value in request_body.items()
        if key not in {"max_tokens", "temperature", "top_k", "top_p", "stop_sequences"}
    }
    token_count = client.messages.count_tokens(**count_body)
    if token_count.input_tokens > max_input_tokens:
        raise ValueError(
            "prepared request exceeds input-token guard: "
            f"{token_count.input_tokens} > {max_input_tokens}"
        )

    response = client.messages.create(**request_body)
    envelope = {
        "schema_version": BRIDGE_SCHEMA,
        "request_sha256": canonical_sha256(request_body),
        "called_at_utc": datetime.now(UTC).isoformat(),
        "counted_input_tokens": token_count.input_tokens,
        "response": response.model_dump(mode="json"),
    }
    response_path.parent.mkdir(parents=True, exist_ok=True)
    response_path.write_text(
        json.dumps(envelope, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return envelope


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--response", type=Path, required=True)
    parser.add_argument("--env-file", type=Path, required=True)
    parser.add_argument("--max-input-tokens", type=int, default=100_000)
    return parser


def main() -> None:
    args = _parser().parse_args()
    try:
        result = run_prepared_request(
            args.request,
            args.response,
            env_file=args.env_file,
            max_input_tokens=args.max_input_tokens,
        )
    except (FileExistsError, TypeError, ValueError) as exc:
        raise SystemExit(str(exc)) from exc
    response = result["response"]
    print(f"model: {response.get('model')}")
    print(f"counted_input_tokens: {result['counted_input_tokens']}")
    print(f"stop_reason: {response.get('stop_reason')}")
    print(f"wrote: {args.response}")


if __name__ == "__main__":
    main()
