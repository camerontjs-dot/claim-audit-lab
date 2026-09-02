"""Research-only consumer for the frozen RC8J typed authority gate.

This module does not implement authority semantics. It accepts a callable owned by
the separately frozen authority programme, validates the returned terminal state,
and records that authority separately from epistemic use / Contract-C projection.

Even a research `WARRANTED` result remains blocked from strengthening CAL or
creating a positive Contract-C projection in this experiment. That mapping is a
separate, unestablished boundary.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable

RC8J_FREEZE_COMMIT = "8e75c6782bb95c3763d06230b9c5df2b6af44054"
RC8J_CANDIDATE_BLOB = "f55156e43e0c1b4a7868bc8339585b8892edda38"
RC8J_CANDIDATE_PATH = "research/semantic_authority_machinery_rc8/authority_contract_rc8j.py"

_ALLOWED_STATUS = {"WARRANTED", "REJECTED", "UNRESOLVED", "NO_ASSESSMENT"}


class ExternalAuthorityContractError(RuntimeError):
    """Raised when the external frozen evaluator violates the consumption interface."""


def consume_external_authority(
    case: dict[str, Any],
    evaluator: Callable[[dict[str, Any]], dict[str, Any]],
    *,
    fixture_only: bool,
) -> dict[str, Any]:
    """Execute an externally owned authority evaluator without inheriting its semantics.

    The input is deep-copied so the external evaluator cannot mutate the integration
    record in place. The returned state is kept internal and is not converted into a
    CAL verdict or Contract-C positive semantic state by this adapter.
    """
    observed = evaluator(deepcopy(case))
    if not isinstance(observed, dict):
        raise ExternalAuthorityContractError("external authority evaluator returned non-object")

    status = observed.get("authority_status")
    reason = observed.get("reason")
    if status not in _ALLOWED_STATUS:
        raise ExternalAuthorityContractError(f"unsupported external authority status: {status!r}")
    if not isinstance(reason, str) or not reason:
        raise ExternalAuthorityContractError("external authority evaluator returned invalid reason")

    return {
        "execution_state": case.get("execution_state"),
        "authority": {
            "status": status,
            "reason": reason,
            "research_dependency": {
                "freeze_commit": RC8J_FREEZE_COMMIT,
                "candidate_path": RC8J_CANDIDATE_PATH,
                "candidate_blob": RC8J_CANDIDATE_BLOB,
            },
        },
        "fixture_only": fixture_only,
        "epistemic_use": {
            "state": "blocked_positive_projection_not_established",
            "may_strengthen_cal_conclusion": False,
            "may_project_positive_contract_c": False,
        },
    }
