"""Fail-closed CAL intake for the optional Contract-B v1.2 factual-context extension.

CAL retains the complete validated extension as an intake/audit ledger but
constructs a narrower semantic-measurement context that excludes nomination and
review metadata, rejected candidates, and upstream proposition judgments.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from claim_audit_lab.contracts.bundle_loader import (
    BundleContents,
    BundleIntegrityError,
    load_bundle,
)

EXTENSION_PATH = Path("extensions/contract-b-factual-context-v1.json")
PROHIBITED_KEYS = frozenset(
    {
        "support",
        "refutation",
        "proposition_specific_relation",
        "semantic_validity",
        "temporal_applicability",
        "authority_applicability",
        "supplier_applicability",
        "completeness_conclusion",
        "decision_participation",
        "audit_support_verdict",
        "verdict",
        "abstention",
    }
)


class FactualContextIntakeError(BundleIntegrityError):
    """Raised when a present extension violates the promoted Contract-B profile."""


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ExplicitValue(_Strict):
    state: Literal["known", "unknown"]
    value: Any | None

    @model_validator(mode="after")
    def validate_state(self) -> ExplicitValue:
        if self.state == "known" and self.value is None:
            raise ValueError("known state requires a non-null value")
        if self.state == "unknown" and self.value is not None:
            raise ValueError("unknown state requires null value")
        return self


class ClaimContext(_Strict):
    claim_id: str = Field(min_length=1)
    origin: ExplicitValue
    atomicity: ExplicitValue


class ContextFact(_Strict):
    fact_id: str = Field(min_length=1)
    predicate: str = Field(min_length=1)
    value: Any
    assertion_mode: str = Field(min_length=1)
    provenance_passage_id: str = Field(min_length=1)


class SourceContext(_Strict):
    source_id: str = Field(min_length=1)
    context_facts: list[ContextFact] = Field(default_factory=list)


class Anchor(_Strict):
    type: str = Field(min_length=1)
    value: Any


class PassageContext(_Strict):
    passage_id: str = Field(min_length=1)
    anchors: list[Anchor] = Field(default_factory=list)


class HistoryLink(_Strict):
    link_id: str = Field(min_length=1)
    claim_id: str = Field(min_length=1)
    passage_id: str = Field(min_length=1)
    nomination: dict[str, Any]
    review: dict[str, Any]

    @model_validator(mode="after")
    def validate_review(self) -> HistoryLink:
        if self.review.get("decision") not in {"accepted", "rejected", "needs-review"}:
            raise ValueError("review.decision must be accepted, rejected, or needs-review")
        return self


class HistoryCountCheck(_Strict):
    claim_id: str = Field(min_length=1)
    candidate: int = Field(ge=0)
    reviewed: int = Field(ge=0)
    admitted: int = Field(ge=0)


class ApertureObservation(_Strict):
    claim_id: str = Field(min_length=1)
    search_scope: dict[str, Any]
    outcome: ExplicitValue
    limitations: list[Any] = Field(default_factory=list)


class ContractBFactualContext(_Strict):
    # The Contract-B wire key is intentionally `schema`; BaseModel.schema is a legacy API.
    schema: Literal["contract-b-factual-context-v1"]  # type: ignore[assignment]
    history_complete: Literal[True]
    claims: list[ClaimContext] = Field(default_factory=list)
    sources: list[SourceContext] = Field(default_factory=list)
    passages: list[PassageContext] = Field(default_factory=list)
    history: list[HistoryLink] = Field(default_factory=list)
    history_count_checks: list[HistoryCountCheck] = Field(default_factory=list)
    aperture: list[ApertureObservation] = Field(default_factory=list)


@dataclass(frozen=True)
class ContractBIntakeView:
    """Validated Contract-B bundle plus optional promoted context views."""

    bundle: BundleContents
    extension_state: Literal["legacy_absent", "absent", "present"]
    intake_ledger: dict[str, Any] | None
    semantic_context: dict[str, Any] | None


def _json_key(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def _normalized_object(extension: ContractBFactualContext) -> dict[str, Any]:
    data = extension.model_dump(mode="json")
    data["claims"] = sorted(data["claims"], key=lambda row: row["claim_id"])
    data["sources"] = sorted(data["sources"], key=lambda row: row["source_id"])
    for source in data["sources"]:
        source["context_facts"] = sorted(source["context_facts"], key=lambda row: row["fact_id"])
    data["passages"] = sorted(data["passages"], key=lambda row: row["passage_id"])
    for passage in data["passages"]:
        passage["anchors"] = sorted(
            passage["anchors"], key=lambda row: (row["type"], _json_key(row["value"]))
        )
    data["history"] = sorted(data["history"], key=lambda row: row["link_id"])
    data["history_count_checks"] = sorted(
        data["history_count_checks"], key=lambda row: row["claim_id"]
    )
    data["aperture"] = sorted(data["aperture"], key=lambda row: row["claim_id"])
    for aperture in data["aperture"]:
        aperture["limitations"] = sorted(aperture["limitations"], key=_json_key)
    return data


def canonical_bytes(extension: ContractBFactualContext) -> bytes:
    return (
        json.dumps(
            _normalized_object(extension),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _walk_prohibited(value: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in PROHIBITED_KEYS:
                errors.append(f"prohibited proposition-specific field: {child_path}")
            errors.extend(_walk_prohibited(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(_walk_prohibited(child, f"{path}[{index}]"))
    return errors


def _duplicates(values: list[str]) -> list[str]:
    counts = Counter(values)
    return sorted(value for value, count in counts.items() if count > 1)


def _identity_sets(bundle: BundleContents) -> tuple[set[str], set[str], set[str], dict[str, str]]:
    claim_ids = {claim.claim_id for claim in bundle.claims}
    source_ids = set(bundle.source_profiles)
    passage_ids: set[str] = set()
    passage_source: dict[str, str] = {}
    for source_id, passages in bundle.passages.items():
        for passage in passages:
            passage_ids.add(passage.passage_id)
            prior = passage_source.get(passage.passage_id)
            if prior is not None and prior != source_id:
                raise FactualContextIntakeError(
                    "passage_id is not globally unique across canonical sources: "
                    f"{passage.passage_id}"
                )
            passage_source[passage.passage_id] = source_id
    return claim_ids, source_ids, passage_ids, passage_source


def _validate_extension(bundle: BundleContents, extension: ContractBFactualContext) -> None:
    errors = _walk_prohibited(extension.model_dump(mode="json"))
    claim_ids, source_ids, passage_ids, _ = _identity_sets(bundle)

    groups = {
        "claim_id": [row.claim_id for row in extension.claims],
        "source_id": [row.source_id for row in extension.sources],
        "passage_id": [row.passage_id for row in extension.passages],
        "link_id": [row.link_id for row in extension.history],
        "history_count_check.claim_id": [row.claim_id for row in extension.history_count_checks],
        "aperture.claim_id": [row.claim_id for row in extension.aperture],
    }
    for label, values in groups.items():
        duplicate = _duplicates(values)
        if duplicate:
            errors.append(f"duplicate {label}: {', '.join(duplicate)}")

    for claim in extension.claims:
        if claim.claim_id not in claim_ids:
            errors.append(f"unknown canonical claim reference: {claim.claim_id}")
    for source in extension.sources:
        if source.source_id not in source_ids:
            errors.append(f"unknown canonical source reference: {source.source_id}")
        duplicate_facts = _duplicates([fact.fact_id for fact in source.context_facts])
        if duplicate_facts:
            errors.append(
                f"duplicate fact_id in source {source.source_id}: {', '.join(duplicate_facts)}"
            )
        for fact in source.context_facts:
            if fact.provenance_passage_id not in passage_ids:
                errors.append(f"unknown provenance passage reference: {fact.provenance_passage_id}")
    for passage in extension.passages:
        if passage.passage_id not in passage_ids:
            errors.append(f"unknown canonical passage reference: {passage.passage_id}")
    for link in extension.history:
        if link.claim_id not in claim_ids:
            errors.append(f"unknown history claim reference: {link.claim_id}")
        if link.passage_id not in passage_ids:
            errors.append(f"unknown history passage reference: {link.passage_id}")
    for aperture in extension.aperture:
        if aperture.claim_id not in claim_ids:
            errors.append(f"unknown aperture claim reference: {aperture.claim_id}")

    derived: dict[str, list[int]] = defaultdict(lambda: [0, 0, 0])
    for link in extension.history:
        row = derived[link.claim_id]
        row[0] += 1
        decision = link.review["decision"]
        if decision != "needs-review":
            row[1] += 1
        if decision == "accepted":
            row[2] += 1
    for check in extension.history_count_checks:
        supplied = (check.candidate, check.reviewed, check.admitted)
        expected = tuple(derived.get(check.claim_id, [0, 0, 0]))
        if supplied != expected:
            errors.append(
                f"history count mismatch for {check.claim_id}: "
                f"supplied={supplied}, derived={expected}"
            )

    if errors:
        raise FactualContextIntakeError("; ".join(errors))


def _semantic_context(bundle: BundleContents, extension: ContractBFactualContext) -> dict[str, Any]:
    _, _, _, passage_source = _identity_sets(bundle)
    claim_context = {row.claim_id: row for row in extension.claims}
    source_context = {row.source_id: row for row in extension.sources}
    passage_context = {row.passage_id: row for row in extension.passages}

    admitted: dict[str, set[str]] = defaultdict(set)
    for link in extension.history:
        if link.review["decision"] == "accepted":
            admitted[link.claim_id].add(link.passage_id)

    claims: list[dict[str, Any]] = []
    for claim_id in sorted(set(claim_context) | set(admitted)):
        claim_row = claim_context.get(claim_id)
        passage_rows: list[dict[str, Any]] = []
        for passage_id in sorted(admitted.get(claim_id, set())):
            source_id = passage_source[passage_id]
            source_row = source_context.get(source_id)
            passage_row = passage_context.get(passage_id)
            passage_rows.append(
                {
                    "passage_id": passage_id,
                    "source_id": source_id,
                    "anchors": (
                        [anchor.model_dump(mode="json") for anchor in passage_row.anchors]
                        if passage_row is not None
                        else []
                    ),
                    "context_facts": (
                        [fact.model_dump(mode="json") for fact in source_row.context_facts]
                        if source_row is not None
                        else []
                    ),
                }
            )
        claims.append(
            {
                "claim_id": claim_id,
                "origin": (
                    claim_row.origin.model_dump(mode="json") if claim_row is not None else None
                ),
                "atomicity": (
                    claim_row.atomicity.model_dump(mode="json") if claim_row is not None else None
                ),
                "admitted_passages": passage_rows,
            }
        )
    return {"schema": "contract-b-cal-semantic-context-v1", "claims": claims}


def load_contract_b_intake(
    bundle_dir: Path,
    *,
    deviations_dir: Path | None = None,
) -> ContractBIntakeView:
    """Load real C-B intake and, when present, the promoted optional extension."""
    bundle_dir = bundle_dir.resolve()
    bundle = load_bundle(bundle_dir, deviations_dir=deviations_dir)
    version = (bundle_dir / "CONTRACT_VERSION").read_text(encoding="utf-8").strip()
    extension_path = bundle_dir / EXTENSION_PATH

    if not extension_path.exists():
        state: Literal["legacy_absent", "absent"] = (
            "legacy_absent" if version in {"1.0.0", "1.1.0"} else "absent"
        )
        return ContractBIntakeView(
            bundle=bundle,
            extension_state=state,
            intake_ledger=None,
            semantic_context=None,
        )
    if version != "1.2.0":
        raise FactualContextIntakeError(
            f"present factual-context extension requires Contract B 1.2.0, got {version!r}"
        )

    raw = extension_path.read_bytes()
    try:
        data = json.loads(
            raw.decode("utf-8"),
            parse_constant=lambda value: (_ for _ in ()).throw(
                ValueError(f"non-finite JSON value is forbidden: {value}")
            ),
        )
        extension = ContractBFactualContext.model_validate(data)
    except (UnicodeDecodeError, json.JSONDecodeError, ValidationError, ValueError) as exc:
        raise FactualContextIntakeError(f"extension schema/JSON validation failed: {exc}") from exc

    _validate_extension(bundle, extension)
    if raw != canonical_bytes(extension):
        raise FactualContextIntakeError("extension JSON is not in canonical normalized form")

    return ContractBIntakeView(
        bundle=bundle,
        extension_state="present",
        intake_ledger=_normalized_object(extension),
        semantic_context=_semantic_context(bundle, extension),
    )


__all__ = [
    "ContractBFactualContext",
    "ContractBIntakeView",
    "FactualContextIntakeError",
    "canonical_bytes",
    "load_contract_b_intake",
]
