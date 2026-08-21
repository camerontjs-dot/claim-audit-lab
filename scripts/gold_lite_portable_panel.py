"""Run and compare provider-neutral Gold Lite model annotations.

This script extends the DEV-only Gold Lite rehearsal to GPT, local MLX, and
operator-supplied model responses. Model annotations are diagnostic reference
channels only. They do not create human gold, validate CAL, or clear Phase 4.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import itertools
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Literal

from pydantic import ValidationError

_panel = importlib.import_module(
    "scripts.gold_lite_model_panel" if __package__ else "gold_lite_model_panel"
)
_review = importlib.import_module("scripts.gold_lite_review" if __package__ else "gold_lite_review")

DEV_LABEL = _panel.DEV_LABEL
MODEL_OUTPUT_SCHEMA = _panel.MODEL_OUTPUT_SCHEMA
MODEL_REVIEW_SCHEMA = _panel.MODEL_REVIEW_SCHEMA
OUTPUT_JSON_SCHEMA = _panel.OUTPUT_JSON_SCHEMA
SYSTEM_PROMPT = _panel.SYSTEM_PROMPT
ModelCoderOutput = _panel.ModelCoderOutput
aggregate_model_reviews = _panel.aggregate_model_reviews
build_blinded_prompt = _panel.build_blinded_prompt
build_parent_prompt = _panel.build_parent_prompt
normalize_model_output = _panel.normalize_model_output
parent_output_schema = _panel.parent_output_schema

ReviewExport = _review.ReviewExport
ReviewPacket = _review.ReviewPacket
load_review_export = _review.load_review_export
load_review_packet = _review.load_review_packet
validate_review_export = _review.validate_review_export

PORTABLE_MANIFEST_SCHEMA = "gold-lite-portable-panel-manifest-v0.1"
PORTABLE_REQUEST_SCHEMA = "gold-lite-portable-model-request-v0.1"
PORTABLE_RECEIPT_SCHEMA = "gold-lite-portable-model-receipt-v0.1"
COMPARISON_SCHEMA = "gold-lite-cross-model-comparison-v0.2"
SUCCESS_FINISH_REASONS = frozenset({"completed", "end_turn", "stop"})
REQUEST_MODES = frozenset({"full-packet", "one-parent-per-call"})
LABELS = ("supports", "refutes", "insufficient", "retrieval_gap")


def prepare_portable_panel(
    packet: ReviewPacket,
    out_dir: Path,
    *,
    provider: str,
    runtime: str,
    model_ids: list[str],
    request_mode: Literal["full-packet", "one-parent-per-call"],
    max_tokens: int,
    independence_boundary: str,
) -> dict[str, Any]:
    """Write frozen, provider-neutral requests for one or more models."""
    if request_mode not in REQUEST_MODES:
        raise ValueError(f"unsupported request mode: {request_mode}")
    if not provider.strip() or not runtime.strip():
        raise ValueError("provider and runtime must be non-empty")
    if not model_ids or len(set(model_ids)) != len(model_ids):
        raise ValueError("model_ids must be a non-empty unique list")
    if max_tokens <= 0:
        raise ValueError("max_tokens must be positive")

    model_specs = [
        {
            "provider": provider,
            "model_id": model_id,
            "runtime": runtime,
            "model_dir": _model_dir(provider, model_id),
        }
        for model_id in model_ids
    ]
    parent_specs = [
        {
            "parent_id": parent.parent_id,
            "request_dir": f"p{index:02d}",
            "prompt_sha256": _sha256_text(build_parent_prompt(packet, parent)),
        }
        for index, parent in enumerate(packet.parents, start=1)
    ]
    manifest = {
        "schema_version": PORTABLE_MANIFEST_SCHEMA,
        "label": DEV_LABEL,
        "panel_id": (
            f"{packet.rehearsal_id}-{_slug(provider)}-{_slug(request_mode)}-portable-panel-v0.1"
        ),
        "packet_sha256": packet.packet_sha256,
        "request_mode": request_mode,
        "max_tokens_per_request": max_tokens,
        "models": model_specs,
        "parents": parent_specs,
        "independence_boundary": independence_boundary,
    }
    _write_json_absent_or_identical(out_dir / "panel-manifest.json", manifest)
    _write_absent_or_identical(out_dir / "README.md", _panel_readme(manifest))

    for model in model_specs:
        model_dir = out_dir / model["model_dir"]
        if request_mode == "full-packet":
            request = _portable_request(
                packet,
                provider=provider,
                runtime=runtime,
                model_id=model["model_id"],
                max_tokens=max_tokens,
            )
            _write_json_absent_or_identical(model_dir / "request.json", request)
            continue
        for parent, parent_spec in zip(packet.parents, parent_specs, strict=True):
            request = _portable_request(
                packet,
                provider=provider,
                runtime=runtime,
                model_id=model["model_id"],
                max_tokens=max_tokens,
                parent=parent,
            )
            _write_json_absent_or_identical(
                model_dir / parent_spec["request_dir"] / "request.json",
                request,
            )
    return manifest


def prepare_external_kit(packet: ReviewPacket, out_dir: Path) -> None:
    """Write paste-ready full and parent prompts for Grok, Gemini, or another model."""
    _write_absent_or_identical(out_dir / "system-prompt.txt", SYSTEM_PROMPT + "\n")
    _write_absent_or_identical(
        out_dir / "full-packet" / "user-prompt.txt",
        build_blinded_prompt(packet) + "\n",
    )
    _write_json_absent_or_identical(
        out_dir / "full-packet" / "output-schema.json",
        OUTPUT_JSON_SCHEMA,
    )
    _write_absent_or_identical(
        out_dir / "full-packet" / "paste-ready-prompt.txt",
        _paste_ready_prompt(build_blinded_prompt(packet), OUTPUT_JSON_SCHEMA),
    )
    for index, parent in enumerate(packet.parents, start=1):
        parent_dir = out_dir / "one-parent-per-call" / f"p{index:02d}"
        prompt = build_parent_prompt(packet, parent)
        _write_absent_or_identical(parent_dir / "user-prompt.txt", prompt + "\n")
        _write_json_absent_or_identical(
            parent_dir / "output-schema.json",
            parent_output_schema(packet, parent),
        )
        _write_absent_or_identical(
            parent_dir / "paste-ready-prompt.txt",
            _paste_ready_prompt(prompt, parent_output_schema(packet, parent)),
        )
    _write_absent_or_identical(out_dir / "README.md", _external_kit_readme(packet))


def validate_portable_receipt(
    packet: ReviewPacket,
    request_path: Path,
    receipt_path: Path,
    out_path: Path,
    *,
    panel_manifest: dict[str, Any],
    expected_parent_ids: list[str] | None = None,
) -> dict[str, Any]:
    """Validate one raw portable receipt and bind it to packet provenance."""
    request = _load_json_object(request_path)
    expected_request = _canonical_portable_request(
        packet,
        request_path,
        panel_manifest,
        expected_parent_ids=expected_parent_ids,
    )
    if request != expected_request:
        raise ValueError(
            "prepared portable request is not canonical for the packet and panel manifest"
        )
    receipt = _load_json_object(receipt_path)
    if request.get("schema_version") != PORTABLE_REQUEST_SCHEMA:
        raise ValueError(f"unsupported portable request schema in {request_path}")
    if receipt.get("schema_version") != PORTABLE_RECEIPT_SCHEMA:
        raise ValueError(f"unsupported portable receipt schema in {receipt_path}")
    request_sha256 = _canonical_sha256(request)
    if receipt.get("request_sha256") != request_sha256:
        raise ValueError("portable receipt request hash does not match prepared request")
    for field in ("provider", "model_id"):
        if receipt.get(field) != request.get(field):
            raise ValueError(
                f"portable receipt {field} drift: "
                f"requested={request.get(field)!r} got={receipt.get(field)!r}"
            )
    finish_reason = receipt.get("finish_reason")
    if finish_reason not in SUCCESS_FINISH_REASONS:
        raise ValueError(f"model response did not end cleanly: {finish_reason}")
    response_text = receipt.get("response_text")
    if not isinstance(response_text, str) or not response_text.strip():
        raise ValueError("portable receipt is missing response_text")
    response_sha256 = _sha256_text(response_text)
    recorded_response_hash = receipt.get("response_sha256")
    if recorded_response_hash is not None and recorded_response_hash != response_sha256:
        raise ValueError("portable receipt response hash drift")

    raw_output, parse_mode = extract_model_output(response_text)
    try:
        output = ModelCoderOutput.model_validate(raw_output)
    except ValidationError as exc:
        raise ValueError(f"invalid model-coder output: {exc}") from exc
    called_at = receipt.get("called_at_utc")
    if not isinstance(called_at, str) or not called_at:
        raise ValueError("portable receipt is missing called_at_utc")
    provider = str(request["provider"])
    model_id = str(request["model_id"])
    review, parent_results = normalize_model_output(
        packet,
        output,
        model_id=model_id,
        exported_at_utc=called_at,
        expected_parent_ids=expected_parent_ids,
        reviewer=f"{provider}:{model_id}",
    )
    artifact = {
        "schema_version": MODEL_REVIEW_SCHEMA,
        "label": DEV_LABEL,
        "panel_id": panel_manifest["panel_id"],
        "packet_sha256": packet.packet_sha256,
        "provider": provider,
        "runtime": request["runtime"],
        "model_id": model_id,
        "prompt_sha256": request["prompt_sha256"],
        "request_sha256": request_sha256,
        "response_receipt_sha256": _sha256_file(receipt_path),
        "response_sha256": response_sha256,
        "finish_reason": finish_reason,
        "parse_mode": parse_mode,
        "protocol_exact_json": parse_mode == "exact-json",
        "usage": receipt.get("usage"),
        "runtime_receipt": receipt.get("runtime"),
        "review": review.model_dump(mode="json"),
        "parent_results": parent_results,
    }
    runtime_status, runtime_gaps = _runtime_receipt_provenance(
        provider,
        receipt.get("runtime"),
    )
    if runtime_status == "complete":
        artifact["runtime_provenance"] = {
            "status": runtime_status,
            "gaps": runtime_gaps,
        }
    _write_json_absent_or_identical(out_path, artifact)
    return artifact


def extract_model_output(response_text: str) -> tuple[dict[str, Any], str]:
    """Extract one schema-marked JSON object without repairing model content."""
    stripped = response_text.strip()
    try:
        exact = json.loads(stripped)
    except json.JSONDecodeError:
        exact = None
    if isinstance(exact, dict) and exact.get("schema_version") == MODEL_OUTPUT_SCHEMA:
        return exact, "exact-json"

    fenced = re.fullmatch(r"```(?:json)?\s*(\{.*\})\s*```", stripped, flags=re.DOTALL)
    if fenced:
        try:
            value = json.loads(fenced.group(1))
        except json.JSONDecodeError:
            value = None
        if isinstance(value, dict) and value.get("schema_version") == MODEL_OUTPUT_SCHEMA:
            return value, "fenced-json"

    decoder = json.JSONDecoder()
    candidates: list[dict[str, Any]] = []
    for match in re.finditer(r"\{", response_text):
        try:
            value, _ = decoder.raw_decode(response_text[match.start() :])
        except json.JSONDecodeError:
            continue
        if not isinstance(value, dict) or value.get("schema_version") != MODEL_OUTPUT_SCHEMA:
            continue
        candidates.append(value)
    if len(candidates) != 1:
        raise ValueError(
            "response must contain exactly one recoverable model-coder JSON object; "
            f"found {len(candidates)}"
        )
    return candidates[0], "embedded-json"


def finalize_portable_panel(packet: ReviewPacket, run_dir: Path) -> list[dict[str, Any]]:
    """Validate all receipts and write one combined review per configured model."""
    manifest = _load_json_object(run_dir / "panel-manifest.json")
    if manifest.get("schema_version") != PORTABLE_MANIFEST_SCHEMA:
        raise ValueError("unsupported portable panel manifest schema")
    if manifest.get("packet_sha256") != packet.packet_sha256:
        raise ValueError("portable panel packet hash does not match packet")
    mode = manifest.get("request_mode")
    if mode not in REQUEST_MODES:
        raise ValueError(f"unsupported portable panel request mode: {mode}")
    models = manifest.get("models")
    parent_specs = manifest.get("parents")
    if not isinstance(models, list) or not models:
        raise ValueError("portable panel models must be a non-empty list")
    if not isinstance(parent_specs, list) or len(parent_specs) != len(packet.parents):
        raise ValueError("portable panel parent specs do not match packet")
    _validate_portable_parent_specs(packet, parent_specs)

    combined_artifacts: list[dict[str, Any]] = []
    for model_spec in models:
        if not isinstance(model_spec, dict):
            raise ValueError("portable model spec must be an object")
        provider = str(model_spec.get("provider", ""))
        model_id = str(model_spec.get("model_id", ""))
        runtime = str(model_spec.get("runtime", ""))
        expected_model_dir = _model_dir(provider, model_id)
        if model_spec.get("model_dir") != expected_model_dir:
            raise ValueError("portable model_dir does not match the configured provider/model")
        if not provider or not model_id or not runtime:
            raise ValueError("portable model spec fields must be non-empty strings")
        model_dir = _safe_child(run_dir, expected_model_dir, label="model_dir")
        valid_children: list[dict[str, Any]] = []
        failures: list[dict[str, Any]] = []
        timestamps: list[str] = []

        request_units: list[tuple[Path, list[str], str]]
        if mode == "full-packet":
            request_units = [
                (model_dir, [parent.parent_id for parent in packet.parents], "full-packet")
            ]
        else:
            request_units = []
            for index, parent in enumerate(packet.parents, start=1):
                expected_request_dir = f"p{index:02d}"
                request_units.append(
                    (
                        _safe_child(model_dir, expected_request_dir, label="request_dir"),
                        [parent.parent_id],
                        expected_request_dir,
                    )
                )

        for request_dir, expected_parent_ids, request_label in request_units:
            receipt_path = request_dir / "model-response.json"
            if not receipt_path.is_file():
                failure_set_path = request_dir / "model-review-failure.json"
                if failure_set_path.is_file():
                    existing_set = _load_json_object(failure_set_path)
                    existing_failures = existing_set.get("failures")
                    if not isinstance(existing_failures, list) or len(existing_failures) != len(
                        expected_parent_ids
                    ):
                        raise ValueError(f"invalid preserved failure set: {failure_set_path}")
                    for parent_id, failure in zip(
                        expected_parent_ids,
                        existing_failures,
                        strict=True,
                    ):
                        if not (
                            isinstance(failure, dict)
                            and failure.get("provider") == provider
                            and failure.get("model_id") == model_id
                            and failure.get("parent_id") == parent_id
                            and failure.get("finish_reason") == "not-run"
                            and failure.get("response_receipt_sha256") is None
                        ):
                            raise ValueError(
                                f"preserved missing-response failure drift: {failure_set_path}"
                            )
                    failures.extend(existing_failures)
                    continue
                missing = [
                    {
                        "schema_version": "gold-lite-model-review-failure-v0.1",
                        "label": DEV_LABEL,
                        "panel_id": manifest["panel_id"],
                        "packet_sha256": packet.packet_sha256,
                        "provider": provider,
                        "model_id": model_id,
                        "parent_id": parent_id,
                        "request_dir": request_label,
                        "finish_reason": "not-run",
                        "response_receipt_sha256": None,
                        "reason": f"missing expected portable response in {request_label}",
                    }
                    for parent_id in expected_parent_ids
                ]
                failures.extend(missing)
                _write_json_absent_or_identical(
                    failure_set_path,
                    {
                        "schema_version": "gold-lite-model-review-failure-set-v0.1",
                        "failures": missing,
                    },
                )
                continue
            receipt = _load_json_object(receipt_path)
            called_at = receipt.get("called_at_utc")
            if isinstance(called_at, str) and called_at:
                timestamps.append(called_at)
            try:
                child = validate_portable_receipt(
                    packet,
                    request_dir / "request.json",
                    receipt_path,
                    request_dir / "model-review.json",
                    panel_manifest=manifest,
                    expected_parent_ids=expected_parent_ids,
                )
            except ValueError as exc:
                for parent_id in expected_parent_ids:
                    failure = {
                        "schema_version": "gold-lite-model-review-failure-v0.1",
                        "label": DEV_LABEL,
                        "panel_id": manifest["panel_id"],
                        "packet_sha256": packet.packet_sha256,
                        "provider": provider,
                        "model_id": model_id,
                        "parent_id": parent_id,
                        "request_dir": request_label,
                        "finish_reason": receipt.get("finish_reason"),
                        "response_receipt_sha256": _sha256_file(receipt_path),
                        "reason": str(exc),
                    }
                    failures.append(failure)
                _write_json_absent_or_identical(
                    request_dir / "model-review-failure.json",
                    {
                        "schema_version": "gold-lite-model-review-failure-set-v0.1",
                        "failures": failures[-len(expected_parent_ids) :],
                    },
                )
                continue
            valid_children.append(child)

        child_reviews = [ReviewExport.model_validate(item["review"]) for item in valid_children]
        exported_at = max(timestamps) if timestamps else "unavailable"
        combined_review = ReviewExport(
            schema_version="gold-lite-review-v0.1",
            rehearsal_id=packet.rehearsal_id,
            packet_sha256=packet.packet_sha256,
            reviewer=f"{provider}:{model_id}",
            exported_at_utc=exported_at,
            decompositions=[
                decision for review in child_reviews for decision in review.decompositions
            ],
            decisions=[decision for review in child_reviews for decision in review.decisions],
        )
        parent_results = validate_review_export(packet, combined_review, require_complete=False)
        source_reviews = [
            {
                "request_sha256": item["request_sha256"],
                "response_receipt_sha256": item["response_receipt_sha256"],
                "parse_mode": item["parse_mode"],
                "protocol_exact_json": item["protocol_exact_json"],
                "usage": item["usage"],
            }
            for item in valid_children
        ]
        runtime_fingerprints = [
            item["runtime_receipt"]
            for item in valid_children
            if isinstance(item.get("runtime_receipt"), dict)
            and isinstance(item["runtime_receipt"].get("rendered_input_sha256"), str)
        ]
        combined = {
            "schema_version": MODEL_REVIEW_SCHEMA,
            "label": DEV_LABEL,
            "panel_id": manifest["panel_id"],
            "packet_sha256": packet.packet_sha256,
            "provider": provider,
            "runtime": model_spec.get("runtime"),
            "model_id": model_id,
            "request_mode": mode,
            "source_reviews": source_reviews,
            "failed_parent_reviews": failures,
            "review": combined_review.model_dump(mode="json"),
            "parent_results": [result.model_dump(mode="json") for result in parent_results],
        }
        if runtime_fingerprints:
            combined["runtime_fingerprints"] = runtime_fingerprints
        combined_name = (
            "combined-model-review.json" if mode == "full-packet" else "model-review.json"
        )
        _write_json_absent_or_identical(model_dir / combined_name, combined)
        combined_artifacts.append(combined)

    if len(combined_artifacts) >= 2:
        consensus = aggregate_model_reviews(
            packet,
            combined_artifacts,
            panel_manifest={
                "panel_id": manifest["panel_id"],
                "independence_boundary": manifest["independence_boundary"],
            },
        )
        _write_json_absent_or_identical(run_dir / "strict-model-consensus.json", consensus)
    _write_absent_or_identical(
        run_dir / "RESULT.md",
        _portable_result_markdown(packet, manifest, combined_artifacts),
    )
    return combined_artifacts


def build_cross_model_comparison(
    packet: ReviewPacket,
    artifacts: list[dict[str, Any]],
    *,
    reference: ReviewExport | None = None,
) -> dict[str, Any]:
    """Build non-gold diagnostics now and optional neutral-reference metrics later."""
    if len(artifacts) < 2:
        raise ValueError("cross-model comparison requires at least two model artifacts")
    if reference is not None:
        validate_review_export(packet, reference, require_complete=True)

    models: dict[str, dict[str, Any]] = {}
    source_fingerprints: dict[str, str] = {}
    for artifact in artifacts:
        if artifact.get("schema_version") != MODEL_REVIEW_SCHEMA:
            raise ValueError("unsupported model-review artifact schema")
        if artifact.get("packet_sha256") != packet.packet_sha256:
            raise ValueError("model artifact packet hash does not match comparison packet")
        review = ReviewExport.model_validate(artifact["review"])
        validate_review_export(packet, review, require_complete=False)
        model_id = str(artifact.get("model_id", ""))
        if not model_id:
            raise ValueError("comparison artifact requires model_id")
        provider = _artifact_provider(artifact, review, model_id=model_id)
        key = f"{provider}/{model_id}"
        if key in models:
            raise ValueError(f"duplicate comparison model: {key}")
        source_fingerprint = _artifact_source_fingerprint(artifact)
        if source_fingerprint is not None:
            prior = source_fingerprints.get(source_fingerprint)
            if prior is not None:
                raise ValueError(f"duplicate model source receipts: {prior} and {key}")
            source_fingerprints[source_fingerprint] = key
        models[key] = {
            "artifact": artifact,
            "review": review,
            "provider": provider,
            "model_id": model_id,
            "decompositions": {item.parent_id: item for item in review.decompositions},
            "decisions": {item.atom_id: item for item in review.decisions},
        }

    reference_decisions = (
        {item.atom_id: item for item in reference.decisions} if reference is not None else {}
    )
    pairwise = _comparison_pairwise(packet, models)
    pairwise_by_model: dict[str, list[float]] = defaultdict(list)
    for row in pairwise:
        rate = row["exact_label_rate"]
        if rate is None:
            continue
        pairwise_by_model[row["model_a"]].append(rate)
        pairwise_by_model[row["model_b"]].append(rate)

    model_rows: list[dict[str, Any]] = []
    for key, model in models.items():
        review = model["review"]
        artifact = model["artifact"]
        decisions = model["decisions"]
        label_counts = Counter(item.label for item in review.decisions)
        source_reviews = artifact.get("source_reviews")
        if isinstance(source_reviews, list):
            valid_response_units = len(source_reviews)
            exact_json_units: int | None = sum(
                item.get("protocol_exact_json") is True
                for item in source_reviews
                if isinstance(item, dict)
            )
        elif isinstance(artifact.get("source_parent_reviews"), list):
            valid_response_units = len(artifact["source_parent_reviews"])
            exact_json_units = valid_response_units
        else:
            valid_response_units = 1 if review.decompositions else 0
            exact_json_units = valid_response_units if key.startswith("anthropic/") else None
        row: dict[str, Any] = {
            "model_key": key,
            "provider": model["provider"],
            "model_id": model["model_id"],
            "runtime": artifact.get("runtime"),
            "valid_parent_reviews": len(review.decompositions),
            "approved_decompositions": sum(
                item.status == "approved" for item in review.decompositions
            ),
            "atom_labels": len(review.decisions),
            "sure_atom_labels": sum(item.confidence == "sure" for item in review.decisions),
            "label_counts": {label: label_counts.get(label, 0) for label in LABELS},
            "valid_response_units": valid_response_units,
            "exact_json_response_units": exact_json_units,
            "failed_parent_reviews": len(artifact.get("failed_parent_reviews", [])),
            "mean_pairwise_exact_label_rate": _rounded_mean(pairwise_by_model[key]),
        }
        runtime_fingerprints = artifact.get("runtime_fingerprints")
        if isinstance(runtime_fingerprints, list) and runtime_fingerprints:
            row["runtime_fingerprints"] = runtime_fingerprints
        runtime_status, runtime_gaps = _artifact_runtime_provenance(artifact, model["provider"])
        row["runtime_provenance_status"] = runtime_status
        row["runtime_provenance_gaps"] = runtime_gaps
        if reference is not None:
            row["reference"] = _reference_metrics(decisions, reference_decisions)
        model_rows.append(row)

    atom_rows: list[dict[str, Any]] = []
    for parent in packet.parents:
        for atom in parent.atoms:
            votes = {
                key: {
                    "label": model["decisions"][atom.atom_id].label,
                    "confidence": model["decisions"][atom.atom_id].confidence,
                }
                for key, model in models.items()
                if atom.atom_id in model["decisions"]
            }
            counts = Counter(vote["label"] for vote in votes.values())
            max_count = max(counts.values()) if counts else 0
            modal = sorted(label for label, count in counts.items() if count == max_count)
            atom_row = {
                "parent_id": parent.parent_id,
                "atom_id": atom.atom_id,
                "text": atom.text,
                "votes": votes,
                "label_counts": dict(sorted(counts.items())),
                "available_votes": len(votes),
                "missing_votes": len(models) - len(votes),
                "distinct_labels": len(counts),
                "modal_labels": modal,
                "available_unanimous": len(counts) == 1 and bool(votes),
                "all_models_unanimous": len(counts) == 1 and len(votes) == len(models),
            }
            if reference is not None:
                atom_row["reference_label"] = reference_decisions[atom.atom_id].label
            else:
                atom_row["human_reference_label"] = None
            atom_rows.append(atom_row)

    comparison = {
        "schema_version": COMPARISON_SCHEMA,
        "label": ("DEV cross-model diagnostic comparison; not gold, validation, or gate evidence"),
        "packet_sha256": packet.packet_sha256,
        "reference_status": (
            "complete-reference" if reference is not None else "pending-human-reference"
        ),
        "reference_reviewer": reference.reviewer if reference is not None else None,
        "comparison_limit": (
            "The supplied complete reference enables reference-relative scoring but is not "
            "described as human gold by this comparison. Human-gold status requires separate "
            "sealed provenance. Models and providers remain correlated."
            if reference is not None
            else "Until a complete human reference exists, completion, distributions, and "
            "pairwise agreement measure model behavior only. They do not measure correctness. "
            "Models and providers are correlated and must not be counted as independent human "
            "coders."
        ),
        "counts": {
            "models": len(models),
            "parents": len(packet.parents),
            "atoms": sum(len(parent.atoms) for parent in packet.parents),
            "all_models_unanimous_atoms": sum(row["all_models_unanimous"] for row in atom_rows),
            "available_unanimous_atoms": sum(row["available_unanimous"] for row in atom_rows),
            "runtime_provenance_complete_models": sum(
                row["runtime_provenance_status"] == "complete" for row in model_rows
            ),
            "runtime_provenance_incomplete_models": sum(
                row["runtime_provenance_status"] != "complete" for row in model_rows
            ),
        },
        "models": model_rows,
        "pairwise_exact_label_agreement": pairwise,
        "atoms": sorted(
            atom_rows,
            key=lambda row: (-row["distinct_labels"], -row["missing_votes"], row["atom_id"]),
        ),
    }
    return comparison


def _portable_request(
    packet: ReviewPacket,
    *,
    provider: str,
    runtime: str,
    model_id: str,
    max_tokens: int,
    parent: Any | None = None,
) -> dict[str, Any]:
    user_prompt = (
        build_parent_prompt(packet, parent) if parent is not None else build_blinded_prompt(packet)
    )
    output_schema = (
        parent_output_schema(packet, parent) if parent is not None else OUTPUT_JSON_SCHEMA
    )
    return {
        "schema_version": PORTABLE_REQUEST_SCHEMA,
        "label": DEV_LABEL,
        "provider": provider,
        "runtime": runtime,
        "model_id": model_id,
        "packet_sha256": packet.packet_sha256,
        "parent_ids": (
            [parent.parent_id]
            if parent is not None
            else [item.parent_id for item in packet.parents]
        ),
        "system_prompt": SYSTEM_PROMPT,
        "user_prompt": user_prompt,
        "prompt_sha256": _sha256_text(f"{SYSTEM_PROMPT}\n\n{user_prompt}"),
        "output_schema": output_schema,
        "max_output_tokens": max_tokens,
    }


def _validate_portable_parent_specs(
    packet: ReviewPacket,
    parent_specs: list[Any],
) -> None:
    for index, (parent, parent_spec) in enumerate(
        zip(packet.parents, parent_specs, strict=True), start=1
    ):
        if not isinstance(parent_spec, dict):
            raise ValueError("portable parent spec must be an object")
        if (
            parent_spec.get("parent_id") != parent.parent_id
            or parent_spec.get("request_dir") != f"p{index:02d}"
            or parent_spec.get("prompt_sha256") != _sha256_text(build_parent_prompt(packet, parent))
        ):
            raise ValueError("portable parent spec order, path, or prompt hash drift")


def _canonical_portable_request(
    packet: ReviewPacket,
    request_path: Path,
    manifest: dict[str, Any],
    *,
    expected_parent_ids: list[str] | None,
) -> dict[str, Any]:
    """Rebuild the only provider-neutral request admitted for this packet unit."""
    if manifest.get("schema_version") != PORTABLE_MANIFEST_SCHEMA:
        raise ValueError("unsupported portable panel manifest schema")
    if manifest.get("packet_sha256") != packet.packet_sha256:
        raise ValueError("portable panel manifest packet hash does not match packet")
    mode = manifest.get("request_mode")
    if mode not in REQUEST_MODES:
        raise ValueError(f"unsupported portable panel request mode: {mode}")
    max_tokens = manifest.get("max_tokens_per_request")
    if not isinstance(max_tokens, int) or max_tokens <= 0:
        raise ValueError("portable panel manifest has invalid max token setting")

    parent_specs = manifest.get("parents")
    if not isinstance(parent_specs, list) or len(parent_specs) != len(packet.parents):
        raise ValueError("portable panel parent specs do not match packet")
    _validate_portable_parent_specs(packet, parent_specs)

    parent: Any | None = None
    if mode == "full-packet":
        canonical_parent_ids = [item.parent_id for item in packet.parents]
        if expected_parent_ids is not None and expected_parent_ids != canonical_parent_ids:
            raise ValueError("full-packet portable request parent coverage drift")
        model_dir_name = request_path.parent.name
    else:
        if expected_parent_ids is None or len(expected_parent_ids) != 1:
            raise ValueError("parent portable request requires one expected parent ID")
        parent = next(
            (item for item in packet.parents if item.parent_id == expected_parent_ids[0]),
            None,
        )
        if parent is None:
            raise ValueError(f"unknown expected parent ID: {expected_parent_ids[0]}")
        parent_spec = next(
            (
                item
                for item in parent_specs
                if isinstance(item, dict) and item.get("parent_id") == parent.parent_id
            ),
            None,
        )
        if (
            parent_spec is None
            or parent_spec.get("request_dir") != request_path.parent.name
            or parent_spec.get("prompt_sha256") != _sha256_text(build_parent_prompt(packet, parent))
        ):
            raise ValueError("portable parent request path or prompt hash drift")
        model_dir_name = request_path.parent.parent.name

    model_specs = manifest.get("models")
    if not isinstance(model_specs, list) or not model_specs:
        raise ValueError("portable panel manifest is missing model specs")
    matches = [
        item
        for item in model_specs
        if isinstance(item, dict) and item.get("model_dir") == model_dir_name
    ]
    if len(matches) != 1:
        raise ValueError("portable request path does not identify one configured model")
    model_spec = matches[0]
    provider = model_spec.get("provider")
    runtime = model_spec.get("runtime")
    model_id = model_spec.get("model_id")
    if not all(isinstance(item, str) and item for item in (provider, runtime, model_id)):
        raise ValueError("portable model spec fields must be non-empty strings")
    expected_model_dir = _model_dir(provider, model_id)
    if model_spec.get("model_dir") != expected_model_dir:
        raise ValueError("portable model_dir does not match the configured provider/model")
    return _portable_request(
        packet,
        provider=provider,
        runtime=runtime,
        model_id=model_id,
        max_tokens=max_tokens,
        parent=parent,
    )


def _comparison_pairwise(
    packet: ReviewPacket, models: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for model_a, model_b in itertools.combinations(models, 2):
        decisions_a = models[model_a]["decisions"]
        decisions_b = models[model_b]["decisions"]
        comparable = 0
        exact = 0
        for parent in packet.parents:
            for atom in parent.atoms:
                a = decisions_a.get(atom.atom_id)
                b = decisions_b.get(atom.atom_id)
                if a is None or b is None:
                    continue
                comparable += 1
                exact += a.label == b.label
        rows.append(
            {
                "model_a": model_a,
                "model_b": model_b,
                "comparable_atoms": comparable,
                "exact_label_atoms": exact,
                "exact_label_rate": round(exact / comparable, 4) if comparable else None,
            }
        )
    return rows


def _reference_metrics(decisions: dict[str, Any], reference: dict[str, Any]) -> dict[str, Any]:
    comparable = sorted(set(decisions) & set(reference))
    exact = sum(decisions[atom_id].label == reference[atom_id].label for atom_id in comparable)
    model_counts = Counter(decisions[atom_id].label for atom_id in comparable)
    reference_counts = Counter(reference[atom_id].label for atom_id in comparable)
    observed = exact / len(comparable) if comparable else 0.0
    expected = (
        sum(
            (model_counts[label] / len(comparable)) * (reference_counts[label] / len(comparable))
            for label in LABELS
        )
        if comparable
        else 0.0
    )
    kappa = (observed - expected) / (1.0 - expected) if comparable and expected < 1.0 else None
    confusion = {
        predicted: {
            actual: sum(
                decisions[atom_id].label == predicted and reference[atom_id].label == actual
                for atom_id in comparable
            )
            for actual in LABELS
        }
        for predicted in LABELS
    }
    return {
        "comparable_atoms": len(comparable),
        "exact_label_atoms": exact,
        "exact_label_rate": round(observed, 4) if comparable else None,
        "cohen_kappa": round(kappa, 4) if kappa is not None else None,
        "confusion_predicted_by_reference": confusion,
    }


def _artifact_provider(
    artifact: dict[str, Any],
    review: ReviewExport,
    *,
    model_id: str,
) -> str:
    provider = artifact.get("provider")
    if isinstance(provider, str) and provider:
        expected_reviewer = f"{provider}:{model_id}"
        if review.reviewer != expected_reviewer:
            raise ValueError(
                "model artifact identity drift: "
                f"expected reviewer={expected_reviewer!r} got={review.reviewer!r}"
            )
        return provider
    expected_anthropic = f"anthropic-api:{model_id}"
    if provider is None and review.reviewer == expected_anthropic:
        return "anthropic"
    raise ValueError("model artifact is missing canonical provider/reviewer identity")


def _runtime_receipt_provenance(
    provider: str,
    runtime: Any,
) -> tuple[str, list[str]]:
    if provider not in {"codex-cli", "mlx-local"}:
        return "provider-unclassified", ["provider-specific runtime proof is not defined"]
    if not isinstance(runtime, dict):
        return "legacy-incomplete", ["runtime receipt is missing"]

    gaps: list[str] = []
    if not _is_sha256(runtime.get("bridge_script_sha256")):
        gaps.append("bridge_script_sha256 missing")
    if not _is_sha256(runtime.get("rendered_input_sha256")):
        gaps.append("rendered_input_sha256 missing")
    if provider == "codex-cli":
        if not _is_sha256(runtime.get("events_sha256")):
            gaps.append("events_sha256 missing")
        audit = runtime.get("tool_event_audit")
        if not (
            isinstance(audit, dict)
            and audit.get("status") == "passed"
            and audit.get("violations") == []
        ):
            gaps.append("passed tool_event_audit missing")
    else:
        revision = runtime.get("model_revision")
        if not isinstance(revision, str) or re.fullmatch(r"[a-f0-9]{7,64}", revision) is None:
            gaps.append("resolved model_revision missing")
        if runtime.get("model_resolution") != "local-huggingface-cache-snapshot":
            gaps.append("local snapshot resolution proof missing")
        if runtime.get("finish_reason_source") != "mlx_lm.stream_generate":
            gaps.append("native stream finish metadata missing")
        if not _is_sha256(runtime.get("chat_template_sha256")):
            gaps.append("chat_template_sha256 missing")
    return ("complete", []) if not gaps else ("legacy-incomplete", gaps)


def _artifact_runtime_provenance(
    artifact: dict[str, Any],
    provider: str,
) -> tuple[str, list[str]]:
    if provider == "anthropic":
        return "complete", []
    if provider not in {"codex-cli", "mlx-local"}:
        return "provider-unclassified", ["provider-specific runtime proof is not defined"]
    fingerprints = artifact.get("runtime_fingerprints")
    source_reviews = artifact.get("source_reviews")
    if not isinstance(fingerprints, list) or not fingerprints:
        return "legacy-incomplete", ["combined artifact has no runtime fingerprints"]
    if isinstance(source_reviews, list) and len(fingerprints) != len(source_reviews):
        return "legacy-incomplete", ["runtime fingerprint coverage does not match source reviews"]
    gaps: list[str] = []
    for index, runtime in enumerate(fingerprints, start=1):
        status, item_gaps = _runtime_receipt_provenance(provider, runtime)
        if status != "complete":
            gaps.extend(f"source {index}: {gap}" for gap in item_gaps)
    return ("complete", []) if not gaps else ("legacy-incomplete", gaps)


def _artifact_source_fingerprint(artifact: dict[str, Any]) -> str | None:
    hashes: set[str] = set()
    for collection_name in (
        "source_reviews",
        "source_parent_reviews",
        "failed_parent_reviews",
    ):
        collection = artifact.get(collection_name)
        if not isinstance(collection, list):
            continue
        for item in collection:
            if not isinstance(item, dict):
                continue
            for field in ("response_receipt_sha256", "api_response_sha256"):
                value = item.get(field)
                if _is_sha256(value):
                    hashes.add(value)
    for field in ("response_receipt_sha256", "api_response_sha256"):
        value = artifact.get(field)
        if _is_sha256(value):
            hashes.add(value)
    return _canonical_sha256(sorted(hashes)) if hashes else None


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"sha256:[a-f0-9]{64}", value) is not None


def _rounded_mean(values: list[float]) -> float | None:
    return round(sum(values) / len(values), 4) if values else None


def _comparison_model_label(model: dict[str, Any]) -> str:
    model_id = str(model["model_id"])
    runtime = model.get("runtime")
    if isinstance(runtime, str) and "no-thinking" in runtime:
        return f"{model_id} [no-thinking]"
    if isinstance(runtime, str) and "phi-native" in runtime:
        return f"{model_id} [native preflight]"
    return model_id


def _paste_ready_prompt(user_prompt: str, output_schema: dict[str, Any]) -> str:
    return f"""<system_instruction>
{SYSTEM_PROMPT}
</system_instruction>

<user_message>
{user_prompt}
</user_message>

<required_output_json_schema>
{json.dumps(output_schema, indent=2, sort_keys=True, ensure_ascii=False)}
</required_output_json_schema>
"""


def _panel_readme(manifest: dict[str, Any]) -> str:
    model_lines = "\n".join(
        f"- `{item['provider']}` / `{item['model_id']}` via `{item['runtime']}`"
        for item in manifest["models"]
    )
    return f"""# Portable Gold Lite model panel

**DEV diagnostic artifact only — not human gold, validation, or gate evidence.**

- packet: `{manifest["packet_sha256"]}`
- request mode: `{manifest["request_mode"]}`
- maximum output tokens per request: `{manifest["max_tokens_per_request"]}`

Models:

{model_lines}

Every raw response must be preserved as `model-response.json` beside its immutable
`request.json`. Finalization validates request hashes, exact packet IDs, atom coverage,
candidate IDs, and passage provenance before a model vote enters comparison output.

Boundary: {manifest["independence_boundary"]}
"""


def _external_kit_readme(packet: ReviewPacket) -> str:
    return f"""# Grok / Gemini / external-model handoff kit

**DEV diagnostic artifact only — not human gold, validation, or gate evidence.**

Packet: `{packet.packet_sha256}`

Use one fresh chat per model. Disable browsing, tools, memory, and cross-chat context if the
surface permits it. Do not show any model another model's answer, CAL output, old human labels,
or the existing assistance sheet.

1. Try `full-packet/paste-ready-prompt.txt` first.
2. Ask the model to return only the JSON object. Preserve the raw answer exactly.
3. Record provider, exact displayed model/version, date/time, and whether the surface enforced
   structured output.
4. If the full packet truncates or drifts, use the ten files under `one-parent-per-call/` in ten
   fresh chats or ten stateless API calls.
5. Return the raw files to CAL for hash-bound import and validation.

Do not manually repair IDs, labels, or rationales. A failed or malformed response is useful
protocol-compliance evidence and must remain visible.
"""


def _portable_result_markdown(
    packet: ReviewPacket,
    manifest: dict[str, Any],
    artifacts: list[dict[str, Any]],
) -> str:
    rows = []
    for artifact in artifacts:
        review = ReviewExport.model_validate(artifact["review"])
        rows.append(
            "| {provider} | `{model}` | {parents}/{total_parents} | {atoms}/{total_atoms} | "
            "{failures} |".format(
                provider=artifact["provider"],
                model=artifact["model_id"],
                parents=len(review.decompositions),
                total_parents=len(packet.parents),
                atoms=len(review.decisions),
                total_atoms=sum(len(parent.atoms) for parent in packet.parents),
                failures=len(artifact["failed_parent_reviews"]),
            )
        )
    return """# Portable Gold Lite panel result

**DEV diagnostic result only — not human gold, validation, or gate evidence.**

| provider | model | valid parents | valid atoms | failed parents |
|---|---|---:|---:|---:|
{rows}

Pairwise agreement, when present, describes model similarity rather than correctness. Human
accuracy remains unavailable until Cameron completes a packet-bound review.

Boundary: {boundary}
""".format(rows="\n".join(rows), boundary=manifest["independence_boundary"])


def comparison_markdown(comparison: dict[str, Any]) -> str:
    parent_total = comparison["counts"]["parents"]
    atom_total = comparison["counts"]["atoms"]
    neutral_reference = comparison["reference_status"] == "complete-reference"
    rows: list[str] = []
    for model in comparison["models"]:
        reference = model.get("reference", model.get("human_reference", {}))
        rows.append(
            "| {provider} | `{model_id}` | {runtime_provenance} | {parents}/{parent_total} | "
            "{atoms}/{atom_total} | {exact_json} | {sure} | {pairwise} | "
            "{reference_exact} |".format(
                provider=model["provider"],
                model_id=_comparison_model_label(model),
                runtime_provenance=model["runtime_provenance_status"],
                parents=model["valid_parent_reviews"],
                parent_total=parent_total,
                atoms=model["atom_labels"],
                atom_total=atom_total,
                exact_json=(
                    "—"
                    if model["exact_json_response_units"] is None
                    else f"{model['exact_json_response_units']}/{model['valid_response_units']}"
                ),
                sure=model["sure_atom_labels"],
                pairwise=(
                    "—"
                    if model["mean_pairwise_exact_label_rate"] is None
                    else f"{model['mean_pairwise_exact_label_rate']:.4f}"
                ),
                reference_exact=(
                    "pending"
                    if not reference
                    else f"{reference['exact_label_atoms']}/{reference['comparable_atoms']}"
                ),
            )
        )
    atom_rows = [
        "| `{atom_id}` | {available} | {missing} | {labels} | {modal} |".format(
            atom_id=atom["atom_id"],
            available=atom["available_votes"],
            missing=atom["missing_votes"],
            labels=atom["distinct_labels"],
            modal=", ".join(atom["modal_labels"]) or "—",
        )
        for atom in comparison["atoms"]
    ]
    reference_name = "reference" if neutral_reference else "human reference"
    reference_column = "reference exact" if neutral_reference else "human exact"
    reference_note = (
        "The supplied reference enables reference-relative scoring only; this report does not "
        "describe it as human gold without separate sealed provenance."
        if neutral_reference
        else "Until the human reference is complete, the final column is intentionally `pending`; "
        "pairwise\nagreement measures similarity, not correctness."
    )
    closing_note = (
        "A model comparison target remains a neutral reference here. Only a separately sealed "
        "human review may be described as human gold."
        if neutral_reference
        else "Every modal label remains a model suggestion. Cameron's evidence-bound decision is "
        "the only\nhuman reference for this rehearsal."
    )
    model_header = (
        "| provider | model | runtime provenance | parents | atoms | exact JSON | sure | mean | "
        f"{reference_column} |"
    )
    return """# Gold Lite cross-model DEV comparison

**This is a model-behavior baseline, not gold, validation, or gate evidence.**

- packet: `{packet}`
- {reference_name}: `{reference}`
- models: {models}
- all-model unanimous atoms: {unanimous}/{atoms}
- runtime provenance complete: {runtime_complete}/{models}

{reference_note}

{model_header}
|---|---|---|---:|---:|---:|---:|---:|---:|
{model_rows}

## Disagreement queue

| atom | available votes | missing votes | distinct labels | modal label(s) |
|---|---:|---:|---:|---|
{atom_rows}

{closing_note}
""".format(
        packet=comparison["packet_sha256"],
        reference=comparison["reference_status"],
        reference_name=reference_name,
        reference_note=reference_note,
        model_header=model_header,
        models=comparison["counts"]["models"],
        unanimous=comparison["counts"]["all_models_unanimous_atoms"],
        atoms=comparison["counts"]["atoms"],
        runtime_complete=comparison["counts"]["runtime_provenance_complete_models"],
        model_rows="\n".join(rows),
        atom_rows="\n".join(atom_rows),
        closing_note=closing_note,
    )


def _load_artifacts(paths: list[Path]) -> list[dict[str, Any]]:
    return [_load_json_object(path) for path in paths]


def _load_json_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"could not load JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object in {path}")
    return value


def _write_json_absent_or_identical(path: Path, value: Any) -> None:
    _write_absent_or_identical(path, _canonical_json(value) + "\n")


def _write_absent_or_identical(path: Path, text: str) -> None:
    encoded = text.encode("utf-8")
    if path.exists():
        if path.read_bytes() != encoded:
            raise FileExistsError(f"refusing to overwrite non-identical artifact: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encoded)


def _canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False)


def _canonical_sha256(value: Any) -> str:
    return _sha256_text(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    )


def _sha256_text(value: str) -> str:
    return f"sha256:{hashlib.sha256(value.encode('utf-8')).hexdigest()}"


def _sha256_file(path: Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _model_dir(provider: str, model_id: str) -> str:
    return f"{_slug(provider)}--{_slug(model_id)}"


def _safe_child(base: Path, relative: str, *, label: str) -> Path:
    """Resolve a manifest path only when it is a direct contained child."""
    candidate_relative = Path(relative)
    if (
        not relative
        or candidate_relative.is_absolute()
        or len(candidate_relative.parts) != 1
        or candidate_relative.name in {".", ".."}
    ):
        raise ValueError(f"unsafe portable {label}: {relative!r}")
    resolved_base = base.resolve()
    candidate = base / candidate_relative
    resolved_candidate = candidate.resolve()
    if resolved_candidate.parent != resolved_base:
        raise ValueError(f"portable {label} escapes its run directory: {relative!r}")
    return candidate


def _prepare_command(args: argparse.Namespace) -> None:
    packet = load_review_packet(args.packet)
    manifest = prepare_portable_panel(
        packet,
        args.out_dir,
        provider=args.provider,
        runtime=args.runtime,
        model_ids=args.models,
        request_mode=args.request_mode,
        max_tokens=args.max_tokens,
        independence_boundary=args.independence_boundary,
    )
    print(f"panel_id: {manifest['panel_id']}")
    print(f"models: {len(manifest['models'])}")
    print(f"request_mode: {manifest['request_mode']}")
    print(f"wrote: {args.out_dir}")


def _prepare_external_command(args: argparse.Namespace) -> None:
    packet = load_review_packet(args.packet)
    prepare_external_kit(packet, args.out_dir)
    print(f"packet_sha256: {packet.packet_sha256}")
    print(f"wrote: {args.out_dir}")


def _finalize_command(args: argparse.Namespace) -> None:
    packet = load_review_packet(args.packet)
    artifacts = finalize_portable_panel(packet, args.run_dir)
    print(f"models: {len(artifacts)}")
    print(
        f"valid_parent_reviews: {sum(len(item['review']['decompositions']) for item in artifacts)}"
    )
    print(f"wrote: {args.run_dir / 'RESULT.md'}")


def _compare_command(args: argparse.Namespace) -> None:
    packet = load_review_packet(args.packet)
    reference = load_review_export(args.reference) if args.reference else None
    comparison = build_cross_model_comparison(
        packet,
        _load_artifacts(args.reviews),
        reference=reference,
    )
    _write_json_absent_or_identical(args.out_dir / "model-comparison.json", comparison)
    _write_absent_or_identical(
        args.out_dir / "MODEL_COMPARISON.md",
        comparison_markdown(comparison),
    )
    print(f"models: {comparison['counts']['models']}")
    print(f"reference_status: {comparison['reference_status']}")
    print(f"wrote: {args.out_dir / 'MODEL_COMPARISON.md'}")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare = subparsers.add_parser("prepare", help="Prepare a provider-neutral model panel.")
    prepare.add_argument("--packet", type=Path, required=True)
    prepare.add_argument("--out-dir", type=Path, required=True)
    prepare.add_argument("--provider", required=True)
    prepare.add_argument("--runtime", required=True)
    prepare.add_argument("--models", nargs="+", required=True)
    prepare.add_argument("--request-mode", choices=sorted(REQUEST_MODES), required=True)
    prepare.add_argument("--max-tokens", type=int, default=4_000)
    prepare.add_argument("--independence-boundary", required=True)
    prepare.set_defaults(func=_prepare_command)

    external = subparsers.add_parser(
        "prepare-external-kit",
        help="Prepare paste-ready full and parent prompts for external model surfaces.",
    )
    external.add_argument("--packet", type=Path, required=True)
    external.add_argument("--out-dir", type=Path, required=True)
    external.set_defaults(func=_prepare_external_command)

    finalize = subparsers.add_parser(
        "finalize",
        help="Validate portable receipts and combine each model's review.",
    )
    finalize.add_argument("--packet", type=Path, required=True)
    finalize.add_argument("--run-dir", type=Path, required=True)
    finalize.set_defaults(func=_finalize_command)

    compare = subparsers.add_parser(
        "compare",
        help="Compare validated model reviews, optionally against a complete reference.",
    )
    compare.add_argument("--packet", type=Path, required=True)
    compare.add_argument("--reviews", type=Path, nargs="+", required=True)
    compare.add_argument("--reference", type=Path)
    compare.add_argument("--out-dir", type=Path, required=True)
    compare.set_defaults(func=_compare_command)
    return parser


def main() -> None:
    args = _parser().parse_args()
    try:
        args.func(args)
    except (FileExistsError, ValidationError, ValueError) as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    main()
