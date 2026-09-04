"""Research-only atomic RC8J authority plus categorical relation derivation.

RC2 removes RC1's caller-supplied authority-result seam. The public operation
captures one case value, evaluates that value with an injected frozen RC8J
implementation, refuses every non-WARRANTED result, and only then derives the
bounded categorical relation from the captured value.

This module does not modify RC8J, production CAL, or the scoreless composer.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable

from categorical_warranted_relation_rc1 import (
    ComparisonProposition,
    WarrantedRelationReceipt,
    compose_categorical_relations,
    derive_categorical_relation as _derive_frozen_rc1_relation,
)


AuthorityEvaluator = Callable[[dict[str, Any]], dict[str, Any]]
_ALLOWED_AUTHORITY_STATUSES = {"WARRANTED", "REJECTED", "UNRESOLVED", "NO_ASSESSMENT"}


class AtomicAuthorityRefusal(ValueError):
    """Raised when the exact captured case is not WARRANTED by RC8J."""

    def __init__(self, status: str, reason: str):
        self.status = status
        self.reason = reason
        super().__init__(f"atomic categorical relation requires WARRANTED authority, got {status}/{reason}")


def _observe_authority(
    case_snapshot: dict[str, Any],
    authority_evaluator: AuthorityEvaluator,
) -> tuple[str, str]:
    """Evaluate a value-identical copy while retaining an untouched relation snapshot.

    The extra copy makes the relation input independent of accidental mutation by
    the authority evaluator itself. No authority result can be supplied by the
    RC2 caller.
    """
    observed = authority_evaluator(deepcopy(case_snapshot))
    if not isinstance(observed, dict):
        raise TypeError("RC8J authority evaluator returned a non-object")

    status = observed.get("authority_status")
    reason = observed.get("reason")
    if status not in _ALLOWED_AUTHORITY_STATUSES:
        raise ValueError(f"unexpected RC8J authority status: {status!r}")
    if not isinstance(reason, str) or not reason:
        raise ValueError("RC8J authority evaluator returned an invalid reason")
    return status, reason


def assess_and_derive_categorical_relation(
    *,
    case: dict[str, Any],
    proposition: ComparisonProposition,
    authority_evaluator: AuthorityEvaluator,
) -> WarrantedRelationReceipt:
    """Atomically assess exact case value then derive a bounded categorical relation.

    There is deliberately no ``authority_result`` parameter. A deep-copied case
    snapshot is captured before authority evaluation. Frozen RC8J is evaluated on
    a value-identical copy of that snapshot; relation derivation consumes the
    untouched captured snapshot only if RC8J returns WARRANTED.
    """
    if not isinstance(case, dict):
        raise TypeError("atomic categorical relation requires a case object")

    case_snapshot = deepcopy(case)
    status, reason = _observe_authority(case_snapshot, authority_evaluator)
    if status != "WARRANTED":
        raise AtomicAuthorityRefusal(status, reason)

    # Reuse the frozen RC1 categorical relation table only after RC2 has generated
    # the authority observation internally for this exact captured case value.
    # The caller cannot inject or replay this internal authority object.
    internal_authority = {
        "authority": {
            "status": status,
            "reason": reason,
        }
    }
    return _derive_frozen_rc1_relation(
        case=case_snapshot,
        authority_result=internal_authority,
        proposition=proposition,
    )


__all__ = [
    "AtomicAuthorityRefusal",
    "ComparisonProposition",
    "WarrantedRelationReceipt",
    "assess_and_derive_categorical_relation",
    "compose_categorical_relations",
]
