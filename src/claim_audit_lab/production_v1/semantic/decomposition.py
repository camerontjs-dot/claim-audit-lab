"""Exact Contract A root/child recomposition for CAL V1 RC0."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any

from .models import Conclusion, canonical_json_bytes

_HASH = re.compile(r"^sha256:[0-9a-f]{64}$")


class DecompositionState(str, Enum):  # noqa: UP042
    NOT_DECOMPOSED = "not_decomposed"
    FAILED = "failed"
    UNKNOWN = "unknown"
    DECLARED = "declared"


class DecompositionRefusal(ValueError):
    """Raised when parent/child recomposition structure is not exact."""

    def __init__(self, code: str, detail: str):
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _sha(value: object) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _require_hash(value: str, label: str) -> None:
    if _HASH.fullmatch(value) is None:
        raise DecompositionRefusal("INVALID_HASH_BINDING", label)


@dataclass(frozen=True, slots=True)
class PropositionRef:
    proposition_id: str
    text_sha256: str
    sequence: int | None = None

    def verify(self) -> None:
        if not self.proposition_id.strip():
            raise DecompositionRefusal("INVALID_PROPOSITION_ID", "blank proposition_id")
        _require_hash(self.text_sha256, self.proposition_id)
        if self.sequence is not None and self.sequence < 1:
            raise DecompositionRefusal("INVALID_SEQUENCE", self.proposition_id)


@dataclass(frozen=True, slots=True)
class DecompositionDeclaration:
    root: PropositionRef
    state: DecompositionState
    decomposition_id: str | None = None
    operator: str | None = None
    children: tuple[PropositionRef, ...] = ()

    def verify(self) -> None:
        self.root.verify()
        if self.root.sequence is not None:
            raise DecompositionRefusal("INVALID_ROOT_SEQUENCE", self.root.proposition_id)

        if self.state is not DecompositionState.DECLARED:
            if self.decomposition_id is not None or self.operator is not None or self.children:
                raise DecompositionRefusal(
                    "ROOT_ONLY_SHAPE_VIOLATION",
                    self.state.value,
                )
            return

        if not self.decomposition_id or not self.decomposition_id.strip():
            raise DecompositionRefusal("MISSING_DECOMPOSITION_ID", "declared all_of")
        if self.operator != "all_of":
            raise DecompositionRefusal("UNSUPPORTED_DECOMPOSITION_OPERATOR", str(self.operator))
        if len(self.children) < 2:
            raise DecompositionRefusal("INVALID_CHILD_CARDINALITY", "all_of requires >= 2")

        child_ids: set[str] = set()
        child_hashes: set[tuple[str, str]] = set()
        expected_sequences = tuple(range(1, len(self.children) + 1))
        actual_sequences = tuple(child.sequence for child in self.children)
        if actual_sequences != expected_sequences:
            raise DecompositionRefusal(
                "INVALID_CHILD_SEQUENCE",
                f"expected={expected_sequences},actual={actual_sequences}",
            )
        for child in self.children:
            child.verify()
            if child.sequence is None:
                raise DecompositionRefusal("INVALID_CHILD_SEQUENCE", child.proposition_id)
            if child.proposition_id == self.root.proposition_id:
                raise DecompositionRefusal("CHILD_EQUALS_ROOT", child.proposition_id)
            if child.proposition_id in child_ids:
                raise DecompositionRefusal("DUPLICATE_CHILD_ID", child.proposition_id)
            key = (child.proposition_id, child.text_sha256)
            if key in child_hashes:
                raise DecompositionRefusal("DUPLICATE_CHILD_BINDING", child.proposition_id)
            child_ids.add(child.proposition_id)
            child_hashes.add(key)


_ALLOWED_CHILD_CONCLUSIONS = {
    Conclusion.SUPPORTED,
    Conclusion.CONTRADICTED,
    Conclusion.NOT_CHECKABLE,
}


@dataclass(frozen=True, slots=True)
class BoundAuditOutcome:
    proposition_id: str
    text_sha256: str
    audit_result_sha256: str
    conclusion: Conclusion
    result_id: str

    @classmethod
    def create(
        cls,
        *,
        proposition_id: str,
        text_sha256: str,
        audit_result_sha256: str,
        conclusion: Conclusion,
    ) -> BoundAuditOutcome:
        if not proposition_id.strip():
            raise DecompositionRefusal("INVALID_PROPOSITION_ID", "blank result proposition")
        _require_hash(text_sha256, proposition_id)
        _require_hash(audit_result_sha256, f"audit_result:{proposition_id}")
        if conclusion not in _ALLOWED_CHILD_CONCLUSIONS:
            raise DecompositionRefusal("UNQUALIFIED_CHILD_CONCLUSION", conclusion.value)
        material = {
            "proposition_id": proposition_id,
            "text_sha256": text_sha256,
            "audit_result_sha256": audit_result_sha256,
            "conclusion": conclusion.value,
        }
        return cls(
            proposition_id=proposition_id,
            text_sha256=text_sha256,
            audit_result_sha256=audit_result_sha256,
            conclusion=conclusion,
            result_id=f"cal-child-result:{_sha(material)}",
        )

    def verify(self) -> None:
        expected = BoundAuditOutcome.create(
            proposition_id=self.proposition_id,
            text_sha256=self.text_sha256,
            audit_result_sha256=self.audit_result_sha256,
            conclusion=self.conclusion,
        )
        if self.result_id != expected.result_id:
            raise DecompositionRefusal("CHILD_RESULT_ID_MISMATCH", self.proposition_id)


@dataclass(frozen=True, slots=True)
class DecompositionReceipt:
    receipt_id: str
    root_proposition_id: str
    root_text_sha256: str
    decomposition_state: DecompositionState
    decomposition_id: str | None
    operator: str
    ordered_child_bindings: tuple[tuple[str, str, str, str], ...]
    root_result_id: str | None
    parent_conclusion: Conclusion


@dataclass(frozen=True, slots=True)
class DecompositionResult:
    conclusion: Conclusion
    receipt: DecompositionReceipt


def _receipt_material(
    declaration: DecompositionDeclaration,
    *,
    ordered_children: tuple[BoundAuditOutcome, ...],
    root_outcome: BoundAuditOutcome | None,
    conclusion: Conclusion,
) -> dict[str, Any]:
    return {
        "root_proposition_id": declaration.root.proposition_id,
        "root_text_sha256": declaration.root.text_sha256,
        "decomposition_state": declaration.state.value,
        "decomposition_id": declaration.decomposition_id,
        "operator": "single" if declaration.state is not DecompositionState.DECLARED else "all_of",
        "ordered_children": [
            {
                "proposition_id": child.proposition_id,
                "text_sha256": child.text_sha256,
                "result_id": child.result_id,
                "conclusion": child.conclusion.value,
            }
            for child in ordered_children
        ],
        "root_result_id": None if root_outcome is None else root_outcome.result_id,
        "parent_conclusion": conclusion.value,
    }


def _bind_receipt(
    declaration: DecompositionDeclaration,
    *,
    ordered_children: tuple[BoundAuditOutcome, ...],
    root_outcome: BoundAuditOutcome | None,
    conclusion: Conclusion,
) -> DecompositionReceipt:
    material = _receipt_material(
        declaration,
        ordered_children=ordered_children,
        root_outcome=root_outcome,
        conclusion=conclusion,
    )
    return DecompositionReceipt(
        receipt_id=_sha(material),
        root_proposition_id=declaration.root.proposition_id,
        root_text_sha256=declaration.root.text_sha256,
        decomposition_state=declaration.state,
        decomposition_id=declaration.decomposition_id,
        operator=str(material["operator"]),
        ordered_child_bindings=tuple(
            (
                str(child["proposition_id"]),
                str(child["text_sha256"]),
                str(child["result_id"]),
                str(child["conclusion"]),
            )
            for child in material["ordered_children"]
        ),
        root_result_id=None if root_outcome is None else root_outcome.result_id,
        parent_conclusion=conclusion,
    )


def verify_decomposition_receipt(
    receipt: DecompositionReceipt,
    declaration: DecompositionDeclaration,
    *,
    child_outcomes: tuple[BoundAuditOutcome, ...] = (),
    root_outcome: BoundAuditOutcome | None = None,
) -> bool:
    try:
        result = recompose(
            declaration,
            child_outcomes=child_outcomes,
            root_outcome=root_outcome,
        )
    except DecompositionRefusal:
        return False
    return receipt == result.receipt


def _verify_root_binding(
    declaration: DecompositionDeclaration,
    root_outcome: BoundAuditOutcome,
) -> None:
    root_outcome.verify()
    if (
        root_outcome.proposition_id != declaration.root.proposition_id
        or root_outcome.text_sha256 != declaration.root.text_sha256
    ):
        raise DecompositionRefusal(
            "ROOT_RESULT_BINDING_MISMATCH",
            root_outcome.proposition_id,
        )


def _ordered_declared_children(
    declaration: DecompositionDeclaration,
    outcomes: tuple[BoundAuditOutcome, ...],
) -> tuple[BoundAuditOutcome, ...]:
    indexed: dict[str, BoundAuditOutcome] = {}
    for outcome in outcomes:
        outcome.verify()
        if outcome.proposition_id in indexed:
            raise DecompositionRefusal("DUPLICATE_CHILD_RESULT", outcome.proposition_id)
        indexed[outcome.proposition_id] = outcome

    declared_ids = {child.proposition_id for child in declaration.children}
    supplied_ids = set(indexed)
    missing = declared_ids - supplied_ids
    extra = supplied_ids - declared_ids
    if missing:
        raise DecompositionRefusal("MISSING_CHILD_RESULT", ",".join(sorted(missing)))
    if extra:
        raise DecompositionRefusal("EXTRA_CHILD_RESULT", ",".join(sorted(extra)))

    ordered: list[BoundAuditOutcome] = []
    seen_result_ids: set[str] = set()
    for child in declaration.children:
        outcome = indexed[child.proposition_id]
        if outcome.text_sha256 != child.text_sha256:
            raise DecompositionRefusal(
                "CHILD_TEXT_BINDING_MISMATCH",
                child.proposition_id,
            )
        if outcome.result_id in seen_result_ids:
            raise DecompositionRefusal(
                "REUSED_CHILD_RESULT_ID",
                child.proposition_id,
            )
        seen_result_ids.add(outcome.result_id)
        ordered.append(outcome)
    return tuple(ordered)


def recompose(
    declaration: DecompositionDeclaration,
    *,
    child_outcomes: tuple[BoundAuditOutcome, ...] = (),
    root_outcome: BoundAuditOutcome | None = None,
) -> DecompositionResult:
    declaration.verify()

    if declaration.state is not DecompositionState.DECLARED:
        if child_outcomes:
            raise DecompositionRefusal("ROOT_ONLY_HAS_CHILD_RESULTS", declaration.state.value)
        if root_outcome is None:
            raise DecompositionRefusal("MISSING_ROOT_RESULT", declaration.state.value)
        _verify_root_binding(declaration, root_outcome)
        receipt = _bind_receipt(
            declaration,
            ordered_children=(),
            root_outcome=root_outcome,
            conclusion=root_outcome.conclusion,
        )
        return DecompositionResult(root_outcome.conclusion, receipt)

    if root_outcome is not None:
        raise DecompositionRefusal("DECLARED_ALLOF_HAS_ROOT_RESULT", declaration.root.proposition_id)

    ordered = _ordered_declared_children(declaration, child_outcomes)
    conclusions = tuple(outcome.conclusion for outcome in ordered)

    if Conclusion.CONTRADICTED in conclusions:
        conclusion = Conclusion.CONTRADICTED
    elif all(value is Conclusion.SUPPORTED for value in conclusions):
        conclusion = Conclusion.SUPPORTED
    else:
        conclusion = Conclusion.NOT_CHECKABLE

    receipt = _bind_receipt(
        declaration,
        ordered_children=ordered,
        root_outcome=None,
        conclusion=conclusion,
    )
    return DecompositionResult(conclusion, receipt)


__all__ = [
    "BoundAuditOutcome",
    "DecompositionDeclaration",
    "DecompositionReceipt",
    "DecompositionRefusal",
    "DecompositionResult",
    "DecompositionState",
    "PropositionRef",
    "recompose",
    "verify_decomposition_receipt",
]
