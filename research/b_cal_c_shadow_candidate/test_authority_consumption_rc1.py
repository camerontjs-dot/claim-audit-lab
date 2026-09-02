from __future__ import annotations

import pytest

from authority_consumption_rc1 import (
    ExternalAuthorityContractError,
    consume_external_authority,
)


def _case() -> dict[str, object]:
    return {"execution_state": "completed", "payload": {"unchanged": True}}


def test_warranted_remains_blocked_from_epistemic_projection() -> None:
    case = _case()

    def evaluator(receipt: dict[str, object]) -> dict[str, str]:
        receipt["payload"] = {"unchanged": False}
        return {
            "authority_status": "WARRANTED",
            "reason": "ALL_REQUIRED_WARRANT_ESTABLISHED",
        }

    result = consume_external_authority(case, evaluator, fixture_only=True)

    assert case["payload"] == {"unchanged": True}
    assert result["authority"]["status"] == "WARRANTED"
    assert result["epistemic_use"] == {
        "state": "blocked_positive_projection_not_established",
        "may_strengthen_cal_conclusion": False,
        "may_project_positive_contract_c": False,
    }
    assert result["fixture_only"] is True


@pytest.mark.parametrize(
    ("status", "reason"),
    [
        ("REJECTED", "AUTHORITY_CLAIM_MISMATCH"),
        ("UNRESOLVED", "AUTHORITY_CLAIM_BINDING_UNRESOLVED"),
        ("NO_ASSESSMENT", "EXECUTION_FAILED"),
    ],
)
def test_nonpositive_states_are_preserved(status: str, reason: str) -> None:
    result = consume_external_authority(
        _case(),
        lambda _case: {"authority_status": status, "reason": reason},
        fixture_only=False,
    )
    assert result["authority"]["status"] == status
    assert result["authority"]["reason"] == reason
    assert result["epistemic_use"]["may_strengthen_cal_conclusion"] is False
    assert result["epistemic_use"]["may_project_positive_contract_c"] is False


def test_invalid_external_status_fails_closed() -> None:
    with pytest.raises(ExternalAuthorityContractError, match="unsupported external authority status"):
        consume_external_authority(
            _case(),
            lambda _case: {"authority_status": "ESTABLISHED", "reason": "not-rc8j"},
            fixture_only=True,
        )


def test_missing_reason_fails_closed() -> None:
    with pytest.raises(ExternalAuthorityContractError, match="invalid reason"):
        consume_external_authority(
            _case(),
            lambda _case: {"authority_status": "UNRESOLVED", "reason": ""},
            fixture_only=True,
        )
