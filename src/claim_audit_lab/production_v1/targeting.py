"""Bounded deterministic target authoring and conformance for CAL V1 research.

This module is intentionally outside the frozen semantic kernel. It derives only the
typed proposition fields already consumed by the two active CAL V1 semantic families,
and it rejects claim forms it cannot map unambiguously.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any, cast

from claim_audit_lab.contracts.cb_models import CBClaim
from claim_audit_lab.contracts.factual_context import ContractBIntakeView, load_contract_b_intake
from claim_audit_lab.production_v1 import CONTRACT_B_VERSION, SUPPORTED_SEMANTIC_FAMILIES
from claim_audit_lab.production_v1.bundle_input import (
    PreparedContractBInput,
    prepare_contract_b_input,
    target_sha256,
)
from claim_audit_lab.production_v1.semantic.models import SemanticFamily


class TargetAuthoringError(ValueError):
    """Raised when an exact Contract B claim cannot be safely authored as a CAL target."""


class TargetConformanceError(ValueError):
    """Raised when a typed target does not conform to the exact Contract B claim text."""


_ENTITY = r"[A-Z][A-Za-z0-9-]*(?:\s+[A-Z][A-Za-z0-9-]*)?"
_MEASURE = r"share|rate|percentage|proportion|output|count|volume|score|yield"
_COMPARISON = re.compile(
    rf"^(?P<lhs>{_ENTITY})\s+had\s+(?:a\s+)?"
    rf"(?P<relation>(?i:higher|greater|larger|lower|smaller|more|fewer|less))\s+"
    rf"(?P<measure>(?i:{_MEASURE}))\s+than\s+(?P<rhs>{_ENTITY})\.?$"
)
_COMPARISON_DIRECTION = {
    "higher": "MORE_THAN",
    "greater": "MORE_THAN",
    "larger": "MORE_THAN",
    "more": "MORE_THAN",
    "lower": "LESS_THAN",
    "smaller": "LESS_THAN",
    "fewer": "LESS_THAN",
    "less": "LESS_THAN",
}

_EVENT_VERBS = {
    "reviewed": "review",
    "signed": "sign",
    "inspected": "inspect",
    "released": "release",
    "approved": "approve",
    "archived": "archive",
    "processed": "process",
    "verified": "verify",
    "recorded": "record",
}
_EVENT_SIDE = re.compile(
    rf"^(?P<subject>{_ENTITY})\s+"
    r"(?P<verb>reviewed|signed|inspected|released|approved|archived|processed|verified|recorded)"
    r"\s+(?P<object>[A-Za-z0-9-]+(?:\s+[A-Za-z0-9-]+){0,5})$"
)
_TEMPORAL_CUE = re.compile(r"\b(before|after)\b", re.IGNORECASE)


def _claim_for_id(intake: ContractBIntakeView, claim_id: str) -> CBClaim:
    matches = [claim for claim in intake.bundle.claims if claim.claim_id == claim_id]
    if len(matches) != 1:
        raise TargetAuthoringError(
            f"claim_id must resolve exactly once in Contract B bundle: {claim_id}"
        )
    return matches[0]


def _require_contract_b(intake: ContractBIntakeView) -> None:
    observed = intake.bundle.manifest.schema_version
    if observed != CONTRACT_B_VERSION:
        raise TargetAuthoringError(
            f"target authoring requires released Contract B {CONTRACT_B_VERSION}, got {observed}"
        )


def _strict_comparison_fields(claim_text: str) -> dict[str, str] | None:
    match = _COMPARISON.fullmatch(" ".join(claim_text.strip().split()))
    if match is None:
        return None
    return {
        "lhs_entity": match.group("lhs"),
        "rhs_entity": match.group("rhs"),
        "comparison_direction": _COMPARISON_DIRECTION[match.group("relation").casefold()],
    }


def _event_side(text: str) -> tuple[str, str, str, str] | None:
    match = _EVENT_SIDE.fullmatch(" ".join(text.strip().split()))
    if match is None:
        return None
    return (
        match.group("subject").casefold(),
        _EVENT_VERBS[match.group("verb").casefold()],
        match.group("object").casefold(),
        "positive",
    )


def _direct_event_order_fields(claim_text: str) -> dict[str, str] | None:
    text = " ".join(claim_text.strip().split())
    if text.endswith("."):
        text = text[:-1]
    cues = list(_TEMPORAL_CUE.finditer(text))
    if len(cues) != 1:
        return None
    cue = cues[0]
    left = _event_side(text[: cue.start()])
    right = _event_side(text[cue.end() :])
    if left is None or right is None:
        return None
    return {
        "left_subject": left[0],
        "left_predicate": left[1],
        "left_object": left[2],
        "left_polarity": left[3],
        "temporal_relation": cue.group(1).upper(),
        "right_subject": right[0],
        "right_predicate": right[1],
        "right_object": right[2],
        "right_polarity": right[3],
    }


def _authored_candidates(claim_text: str) -> list[tuple[SemanticFamily, dict[str, str]]]:
    candidates: list[tuple[SemanticFamily, dict[str, str]]] = []
    comparison = _strict_comparison_fields(claim_text)
    if comparison is not None:
        candidates.append((SemanticFamily.STRICT_COMPARISON, comparison))
    event_order = _direct_event_order_fields(claim_text)
    if event_order is not None:
        candidates.append((SemanticFamily.DIRECT_EVENT_ORDER, event_order))
    return candidates


def author_target(claim_id: str, claim_text: str) -> dict[str, Any]:
    """Author one canonical typed target from one exact claim text.

    The authoring aperture is deliberately narrower than the semantic runtime. Claim
    forms that are outside the explicit grammar, ambiguous between families, or imply
    currently unsupported negative-event semantics are rejected rather than guessed.
    """
    if not claim_id.strip():
        raise TargetAuthoringError("claim_id must be non-empty")
    if not claim_text.strip():
        raise TargetAuthoringError("claim_text must be non-empty")
    candidates = _authored_candidates(claim_text)
    if len(candidates) != 1:
        reason = "unsupported claim form" if not candidates else "ambiguous semantic family"
        raise TargetAuthoringError(f"{reason}: {claim_id}")
    family, fields = candidates[0]
    if family.value not in SUPPORTED_SEMANTIC_FAMILIES:
        raise TargetAuthoringError(f"semantic family is not active: {family.value}")
    return {
        "claim_id": claim_id,
        "proposition": {
            "proposition_id": claim_id,
            "text_sha256": hashlib.sha256(claim_text.encode("utf-8")).hexdigest(),
            "semantic_family": family.value,
            "fields": fields,
        },
    }


def canonical_target_bytes(target: Mapping[str, Any]) -> bytes:
    """Serialize an authored target deterministically."""
    return (
        json.dumps(dict(target), sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"
    ).encode("utf-8")


def author_target_from_bundle(bundle_dir: Path, claim_id: str) -> dict[str, Any]:
    """Author a target from the exact claim text in one released Contract B bundle."""
    intake = load_contract_b_intake(bundle_dir)
    _require_contract_b(intake)
    claim = _claim_for_id(intake, claim_id)
    return author_target(claim.claim_id, claim.claim_text)


def write_target_file(path: Path, target: Mapping[str, Any]) -> str:
    """Write a new target file without overwriting any existing path."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as handle:
            raw = canonical_target_bytes(target)
            handle.write(raw)
    except FileExistsError as exc:
        raise TargetAuthoringError(f"refusing to overwrite target path: {path}") from exc
    except OSError as exc:
        raise TargetAuthoringError(f"cannot write target {path}: {exc}") from exc
    return target_sha256(raw)


def _target_parts(target: Mapping[str, Any]) -> tuple[str, dict[str, str]]:
    proposition = target.get("proposition")
    if not isinstance(proposition, dict):
        raise TargetConformanceError("target proposition must be an object")
    family = proposition.get("semantic_family")
    fields = proposition.get("fields")
    if not isinstance(family, str) or not isinstance(fields, dict):
        raise TargetConformanceError("target proposition family/fields are invalid")
    if not all(isinstance(key, str) and isinstance(value, str) for key, value in fields.items()):
        raise TargetConformanceError("target proposition fields must be string-to-string")
    return family, cast(dict[str, str], fields)


def validate_target_conformance(bundle_dir: Path, target_path: Path) -> dict[str, Any]:
    """Require exact semantic conformance between a target and its Contract B claim.

    Existing structural/binding validation runs first. Conformance then independently
    authors the canonical target from the exact claim text and requires the target's
    active semantic family and complete field map to match it exactly.
    """
    prepared: PreparedContractBInput = prepare_contract_b_input(bundle_dir, target_path)
    expected = author_target(
        cast(str, prepared.target["claim_id"]),
        prepared.context.original_claim,
    )
    actual_family, actual_fields = _target_parts(prepared.target)
    expected_family, expected_fields = _target_parts(expected)
    if actual_family != expected_family:
        raise TargetConformanceError(
            "target semantic_family does not conform to the exact Contract B claim text"
        )
    if actual_fields != expected_fields:
        raise TargetConformanceError(
            "target fields do not conform exactly to the authored supported-family semantics"
        )
    expected_bytes = canonical_target_bytes(expected)
    return {
        "schema": "cal-v1-target-conformance-receipt-rc0",
        "status": "CONFORMANT",
        "claim_id": cast(str, prepared.target["claim_id"]),
        "semantic_family": actual_family,
        "input_target_sha256": prepared.target_sha256,
        "canonical_authored_target_sha256": target_sha256(expected_bytes),
        "contract_b_version": prepared.context.evidence_world.contract_b_version,
        "bundle_id": prepared.context.evidence_world.bundle_id,
    }


__all__ = [
    "TargetAuthoringError",
    "TargetConformanceError",
    "author_target",
    "author_target_from_bundle",
    "canonical_target_bytes",
    "validate_target_conformance",
    "write_target_file",
]
