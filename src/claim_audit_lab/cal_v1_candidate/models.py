from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from typing import Any, Mapping


class SemanticFamily(str, Enum):
    STRICT_COMPARISON = "strict_comparison"
    DIRECT_EVENT_ORDER = "direct_event_order"
    PERMISSION_EXCEPTION = "permission_exception"
    ASSERTION_SCOPE = "assertion_scope"
    UNSUPPORTED = "unsupported"


class CategoricalRelation(str, Enum):
    SUPPORTS = "SUPPORTS"
    REFUTES = "REFUTES"
    IRRELEVANT = "IRRELEVANT"
    UNRESOLVED = "UNRESOLVED"


class Conclusion(str, Enum):
    SUPPORTED = "supported"
    CONTRADICTED = "contradicted"
    NOT_CHECKABLE = "not_checkable"
    NOT_COMPOSED = "not_composed"


class FailureCode(str, Enum):
    UPSTREAM_APERTURE_INSUFFICIENT = "UPSTREAM_APERTURE_INSUFFICIENT"
    EVIDENCE_NOT_ADMITTED = "EVIDENCE_NOT_ADMITTED"
    MEASUREMENT_NOT_APPLICABLE = "MEASUREMENT_NOT_APPLICABLE"
    MEASUREMENT_MISS = "MEASUREMENT_MISS"
    SOURCE_COMPLETION_FAILED = "SOURCE_COMPLETION_FAILED"
    SEMANTIC_AUTHORITY_UNRESOLVED = "SEMANTIC_AUTHORITY_UNRESOLVED"
    PROPOSITION_BINDING_FAILED = "PROPOSITION_BINDING_FAILED"
    RELATION_UNRESOLVED = "RELATION_UNRESOLVED"
    MIXED_RELATIONS = "MIXED_RELATIONS"
    COMMON_EVIDENCE_WORLD_MISMATCH = "COMMON_EVIDENCE_WORLD_MISMATCH"
    UNSUPPORTED_SEMANTIC_FAMILY = "UNSUPPORTED_SEMANTIC_FAMILY"
    RESULT_PROJECTION_FAILED = "RESULT_PROJECTION_FAILED"


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def sha256_hex(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def stable_id(namespace: str, value: Any) -> str:
    return f"{namespace}:{sha256_hex(canonical_json_bytes(value))}"


def _frozen_fields(fields: Mapping[str, str]) -> tuple[tuple[str, str], ...]:
    return tuple(sorted((str(key), str(value)) for key, value in fields.items()))


@dataclass(frozen=True, slots=True)
class TypedProposition:
    proposition_id: str
    semantic_family: SemanticFamily
    fields: tuple[tuple[str, str], ...]

    @classmethod
    def create(
        cls,
        proposition_id: str,
        semantic_family: SemanticFamily,
        fields: Mapping[str, str],
    ) -> TypedProposition:
        if not proposition_id.strip():
            raise ValueError("proposition_id must be non-empty")
        return cls(proposition_id, semantic_family, _frozen_fields(fields))

    def field_map(self) -> dict[str, str]:
        return dict(self.fields)

    @property
    def sha256(self) -> str:
        return sha256_hex(
            canonical_json_bytes(
                {
                    "proposition_id": self.proposition_id,
                    "semantic_family": self.semantic_family.value,
                    "fields": dict(self.fields),
                }
            )
        )


@dataclass(frozen=True, slots=True)
class AdmittedPassage:
    passage_id: str
    source_id: str
    text: str
    text_sha256: str

    @classmethod
    def create(cls, passage_id: str, source_id: str, text: str) -> AdmittedPassage:
        return cls(passage_id, source_id, text, sha256_hex(text.encode()))

    def verify(self) -> None:
        if self.text_sha256 != sha256_hex(self.text.encode()):
            raise ValueError(f"passage hash mismatch: {self.passage_id}")


@dataclass(frozen=True, slots=True)
class EvidenceWorld:
    contract_b_version: str
    bundle_id: str
    bundle_hash: str
    admitted_passages: tuple[AdmittedPassage, ...]
    aperture_state: str
    root_id: str | None = None
    child_id: str | None = None

    def verify(self) -> None:
        if not self.contract_b_version or not self.bundle_id or not self.bundle_hash:
            raise ValueError("Contract B version, bundle_id, and bundle_hash are required")
        seen: set[str] = set()
        for passage in self.admitted_passages:
            passage.verify()
            if passage.passage_id in seen:
                raise ValueError(f"duplicate passage_id: {passage.passage_id}")
            seen.add(passage.passage_id)

    @property
    def evidence_world_sha256(self) -> str:
        self.verify()
        material = {
            "contract_b_version": self.contract_b_version,
            "bundle_id": self.bundle_id,
            "bundle_hash": self.bundle_hash,
            "admitted_passages": [
                {
                    "passage_id": passage.passage_id,
                    "source_id": passage.source_id,
                    "text_sha256": passage.text_sha256,
                }
                for passage in self.admitted_passages
            ],
            "aperture_state": self.aperture_state,
            "root_id": self.root_id,
            "child_id": self.child_id,
        }
        return sha256_hex(canonical_json_bytes(material))

    def passage(self, passage_id: str) -> AdmittedPassage:
        for passage in self.admitted_passages:
            if passage.passage_id == passage_id:
                return passage
        raise KeyError(passage_id)


@dataclass(frozen=True, slots=True)
class AuditContext:
    original_claim: str
    proposition: TypedProposition
    evidence_world: EvidenceWorld

    def verify(self) -> None:
        if not self.original_claim.strip():
            raise ValueError("original_claim must be non-empty")
        self.evidence_world.verify()

    @property
    def context_sha256(self) -> str:
        self.verify()
        return sha256_hex(
            canonical_json_bytes(
                {
                    "original_claim": self.original_claim,
                    "proposition_sha256": self.proposition.sha256,
                    "evidence_world_sha256": self.evidence_world.evidence_world_sha256,
                }
            )
        )
