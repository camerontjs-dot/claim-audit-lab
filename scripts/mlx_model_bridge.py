"""Execute prepared Gold Lite requests with the scaffold-study MLX model set.

Run this file with the Homebrew ``mlx-lm`` Python. It intentionally uses only
the standard library plus the already-installed ``mlx-lm`` and
``huggingface-hub`` runtime so the scaffold-study repository stays read-only.
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import importlib.metadata
import json
import os
import platform
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REQUEST_SCHEMA = "gold-lite-portable-model-request-v0.1"
RECEIPT_SCHEMA = "gold-lite-portable-model-receipt-v0.1"
MLX_MODEL_ALLOWLIST = (
    "lmstudio-community/Phi-4-mini-reasoning-MLX-4bit",
    "mlx-community/Qwen3-8B-4bit",
    "mlx-community/Meta-Llama-3.1-8B-Instruct-4bit",
    "mlx-community/gemma-3-12b-it-qat-4bit",
)


def run_model_directory(
    model_dir: Path,
    *,
    disable_thinking: bool = False,
) -> list[dict[str, Any]]:
    """Load one model once, then execute every prepared request in order."""
    request_paths = sorted(model_dir.glob("p*/request.json"))
    if not request_paths and (model_dir / "request.json").is_file():
        request_paths = [model_dir / "request.json"]
    if not request_paths:
        raise ValueError(f"no prepared requests under {model_dir}")
    requests = [_load_json_object(path) for path in request_paths]
    model_ids = {str(request.get("model_id", "")) for request in requests}
    providers = {str(request.get("provider", "")) for request in requests}
    if len(model_ids) != 1 or len(providers) != 1:
        raise ValueError("all requests in one model directory must share provider and model_id")
    model_id = next(iter(model_ids))
    if next(iter(providers)) != "mlx-local":
        raise ValueError("MLX bridge only accepts provider=mlx-local")
    if model_id not in MLX_MODEL_ALLOWLIST:
        raise ValueError(f"model is not in the scaffold-study MLX set: {model_id}")
    if disable_thinking and "Qwen3" not in model_id:
        raise ValueError("--disable-thinking is only supported for the Qwen3 study model")
    for request in requests:
        if request.get("schema_version") != REQUEST_SCHEMA:
            raise ValueError("unsupported portable request schema")
    out_paths = [request_path.parent / "model-response.json" for request_path in request_paths]
    for out_path in out_paths:
        if out_path.exists():
            raise FileExistsError(f"refusing to overwrite existing receipt: {out_path}")

    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"

    import mlx.core as mx
    import mlx_lm
    from mlx_lm.sample_utils import make_sampler

    snapshot_path, revision = _cached_snapshot(model_id)
    print(f"loading: {model_id}", flush=True)
    model, tokenizer = mlx_lm.load(str(snapshot_path))
    version = importlib.metadata.version("mlx-lm")
    sampler = make_sampler(temp=0.0)
    chat_template_sha256 = _chat_template_sha256(tokenizer)
    receipts: list[dict[str, Any]] = []
    try:
        for index, (request_path, request) in enumerate(
            zip(request_paths, requests, strict=True), start=1
        ):
            out_path = request_path.parent / "model-response.json"
            print(f"request {index}/{len(requests)}: {request_path.parent.name}", flush=True)
            called_at = datetime.now(UTC).isoformat()
            rendered_input_sha256: str | None = None
            try:
                rendered, chat_template_mode = _render_prompt(
                    tokenizer,
                    request,
                    disable_thinking=disable_thinking,
                )
                rendered_input_sha256 = _sha256_text(rendered)
                max_tokens = int(request["max_output_tokens"])
                chunks: list[str] = []
                final_response: Any | None = None
                for generation_response in mlx_lm.stream_generate(
                    model,
                    tokenizer,
                    prompt=rendered,
                    max_tokens=max_tokens,
                    sampler=sampler,
                ):
                    chunks.append(str(generation_response.text))
                    final_response = generation_response
                if final_response is None or final_response.finish_reason not in {
                    "stop",
                    "length",
                }:
                    raise RuntimeError("mlx_lm stream ended without finish metadata")
                response_text = "".join(chunks)
                output_tokens = int(final_response.generation_tokens)
                finish_reason = str(final_response.finish_reason)
                runtime_error = None
                input_tokens = int(final_response.prompt_tokens)
            except Exception as exc:  # preserve one failed unit and continue
                response_text = ""
                output_tokens = 0
                input_tokens = None
                finish_reason = "error"
                runtime_error = f"{type(exc).__name__}: {exc}"
                chat_template_mode = "failed-before-generation"
            receipt = {
                "schema_version": RECEIPT_SCHEMA,
                "request_sha256": _canonical_sha256(request),
                "called_at_utc": called_at,
                "provider": "mlx-local",
                "model_id": model_id,
                "finish_reason": finish_reason,
                "response_text": response_text,
                "response_sha256": _sha256_text(response_text),
                "usage": {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                },
                "runtime": {
                    "api_endpoint": "mlx://local",
                    "bridge_script_sha256": _sha256_file(Path(__file__)),
                    "mlx_lm_version": version,
                    "model_revision": revision,
                    "model_resolution": "local-huggingface-cache-snapshot",
                    "quantization": _quantization(model_id),
                    "temperature": 0.0,
                    "thinking_mode": "disabled" if disable_thinking else "native-default",
                    "chat_template_mode": chat_template_mode,
                    "chat_template_sha256": chat_template_sha256,
                    "rendered_input_sha256": rendered_input_sha256,
                    "finish_reason_source": "mlx_lm.stream_generate",
                    "python": sys.version.split()[0],
                    "platform": platform.platform(),
                    "error": runtime_error,
                },
            }
            _write_json_new(out_path, receipt)
            receipts.append(receipt)
    finally:
        del model
        del tokenizer
        gc.collect()
        clear = getattr(mx, "clear_cache", None)
        if callable(clear):
            clear()
    return receipts


def _render_prompt(
    tokenizer: Any,
    request: dict[str, Any],
    *,
    disable_thinking: bool,
) -> tuple[str, str]:
    system_prompt = request.get("system_prompt")
    user_prompt = request.get("user_prompt")
    output_schema = request.get("output_schema")
    if (
        not isinstance(system_prompt, str)
        or not isinstance(user_prompt, str)
        or not isinstance(output_schema, dict)
    ):
        raise ValueError(
            "portable request must contain system_prompt, user_prompt, and output_schema"
        )
    schema_block = json.dumps(output_schema, indent=2, sort_keys=True, ensure_ascii=False)
    user_content = (
        f"{user_prompt}\n\n<required_output_json_schema>\n{schema_block}\n"
        "</required_output_json_schema>"
    )
    apply = getattr(tokenizer, "apply_chat_template", None)
    if not callable(apply):
        return f"{system_prompt}\n\n{user_content}", "plain-with-schema"
    try:
        kwargs = {
            "tokenize": False,
            "add_generation_prompt": True,
        }
        if disable_thinking:
            kwargs["enable_thinking"] = False
        rendered = apply(
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            **kwargs,
        )
        suffix = "-no-thinking" if disable_thinking else ""
        return str(rendered), f"native-system-user-with-schema{suffix}"
    except Exception:
        kwargs = {
            "tokenize": False,
            "add_generation_prompt": True,
        }
        if disable_thinking:
            kwargs["enable_thinking"] = False
        rendered = apply(
            [
                {
                    "role": "user",
                    "content": f"<system_instruction>\n{system_prompt}\n"
                    f"</system_instruction>\n\n{user_content}",
                }
            ],
            **kwargs,
        )
        suffix = "-no-thinking" if disable_thinking else ""
        return str(rendered), f"native-single-user-fallback-with-schema{suffix}"


def _cached_snapshot(model_id: str) -> tuple[Path, str]:
    from huggingface_hub import snapshot_download

    try:
        snapshot = Path(snapshot_download(model_id, local_files_only=True)).resolve()
    except Exception as exc:
        raise ValueError(f"model snapshot is not available in the local cache: {model_id}") from exc
    if not snapshot.is_dir():
        raise ValueError(f"cached model snapshot is not a directory: {snapshot}")
    if re.fullmatch(r"[a-f0-9]{7,64}", snapshot.name):
        return snapshot, snapshot.name
    main_ref = snapshot.parent.parent / "refs" / "main"
    if main_ref.is_file():
        candidate = main_ref.read_text(encoding="utf-8").strip()
        if re.fullmatch(r"[a-f0-9]{7,64}", candidate):
            return snapshot, candidate
    raise ValueError(f"cached model snapshot revision is unresolved: {snapshot}")


def _chat_template_sha256(tokenizer: Any) -> str | None:
    template = getattr(tokenizer, "chat_template", None)
    if isinstance(template, str):
        return _sha256_text(template)
    return None


def _quantization(model_id: str) -> str:
    lowered = model_id.lower()
    if "qat-4bit" in lowered:
        return "qat-4bit"
    if "4bit" in lowered:
        return "4bit"
    return "unknown"


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


def _write_json_new(path: Path, value: Any) -> None:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite existing receipt: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-dir", type=Path, required=True)
    parser.add_argument("--disable-thinking", action="store_true")
    return parser


def main() -> None:
    args = _parser().parse_args()
    try:
        receipts = run_model_directory(
            args.model_dir,
            disable_thinking=args.disable_thinking,
        )
    except (FileExistsError, ValueError) as exc:
        raise SystemExit(str(exc)) from exc
    print(f"receipts: {len(receipts)}")
    print(f"clean_stops: {sum(item['finish_reason'] == 'stop' for item in receipts)}")


if __name__ == "__main__":
    main()
