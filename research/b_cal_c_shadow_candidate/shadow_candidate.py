"""Research-only B -> CAL -> C shadow integration core.

This module intentionally lives under research/. It does not alter the released
CAL execution path and it does not implement semantic warrant. Bounded research
measurements are observations/proposals only until a separately owned authority
module establishes a warrant receipt.
"""
from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass
from typing import Any, Callable

CANDIDATE_ID = "b-cal-c-shadow-v1"
AUTHORITY_INTERFACE_VERSION = "cal-semantic-warrant-interface-draft-v1"

# Exact evidence implementations consumed by the integration runner. The runner
# imports these from detached checkouts at these immutable commits rather than
# copying their branches into production.
INSTRUMENT_EVIDENCE = {
    "comparison": {
        "commit": "0ecdedc5cea970485a635508255f3670ab231c33",
        "module": "research/comparative_relation_measurement_rc7fb1/comparator.py",
        "disposition": "bounded_safe_measurement_candidate",
    },
    "event_ordering": {
        "commit": "e8d33913db66ad21027dffdf731d50f7a0977c8f",
        "module": "research/event_ordering_measurement_rc7fc/event_order.py",
        "disposition": "bounded_safe_measurement_candidate",
    },
    "permission_composition": {
        "commit": "9e1f28c3e4f217561e4364e1560539bdf4870298",
        "module": "research/deontic_permission_composition_rc7fd/permission_compose.py",
        "disposition": "bounded_safe_measurement_candidate",
    },
}

# Preserved falsifier. The assertion/scope line did not meet the zero-false-
# permit requirement, so this integration track may not use it as warrant.
ASSERTION_SCOPE_FALSIFIER = "ead5a6b795298be09fa99fef7b5f796565304840"


class AuthorityBoundaryError(RuntimeError):
    """Raised when this integration track is asked to invent semantic warrant."""


@dataclass(frozen=True)
class MeasurementInstrument:
    family: str
    measure: Callable[[str], dict[str, Any]]
    implementation_commit: str


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def sha256_hex(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def result_set_identity(value: dict[str, Any]) -> str:
    payload = copy.deepcopy(value)
    payload.pop("result_set_id", None)
    return "result-set:" + sha256_hex(canonical_bytes(payload))


def _authority_state_for_measurement(result: dict[str, Any]) -> dict[str, Any]:
    """Classify measurement state without granting authority.

    `CLAIMED` means only that the instrument emitted a proposal. The assertion
    and interpretation warrant needed to turn that proposal into an epistemic
    premise is outside this track and therefore remains unresolved.
    """
    status = result.get("status")
    if status == "CLAIMED":
        return {
            "state": "insufficient_authority",
            "reason": "measurement_proposal_has_no_established_warrant_receipt",
            "may_strengthen_conclusion": False,
        }
    if status == "UNRESOLVED":
        return {
            "state": "semantic_relation_unknown",
            "reason": "instrument_observed_a_cue_but_did_not_resolve_supported_attachment",
            "may_strengthen_conclusion": False,
        }
    if status == "NOT_APPLICABLE":
        return {
            "state": "operator_inapplicable",
            "reason": "instrument_reports_no_supported_family_surface",
            "may_strengthen_conclusion": False,
        }
    return {
        "state": "execution_failure",
        "reason": f"unrecognized_measurement_status:{status!r}",
        "may_strengthen_conclusion": False,
    }


def measure_text(
    text: str,
    instruments: list[MeasurementInstrument],
    *,
    passage_id: str,
) -> list[dict[str, Any]]:
    observations: list[dict[str, Any]] = []
    for instrument in instruments:
        try:
            result = instrument.measure(text)
        except Exception as exc:  # noqa: BLE001 - failures are evidence in this research runtime
            observations.append(
                {
                    "family": instrument.family,
                    "instrument_commit": instrument.implementation_commit,
                    "passage_id": passage_id,
                    "measurement": None,
                    "authority": {
                        "state": "execution_failure",
                        "reason": f"{type(exc).__name__}:{exc}",
                        "may_strengthen_conclusion": False,
                    },
                }
            )
            continue
        observations.append(
            {
                "family": instrument.family,
                "instrument_commit": instrument.implementation_commit,
                "passage_id": passage_id,
                "measurement": result,
                "authority": _authority_state_for_measurement(result),
            }
        )
    return observations


def require_external_warrant(receipt: dict[str, Any] | None) -> None:
    """Declare the plug point without implementing the parallel authority track.

    Even an object claiming `established` is not accepted here because this
    experiment has no authority to define or verify that receipt. Future work may
    replace this fail-closed function with the separately promoted authority
    module without changing Contracts B or C.
    """
    if receipt is None:
        raise AuthorityBoundaryError("no semantic warrant receipt supplied")
    state = receipt.get("state")
    if state == "semantic_unknown":
        raise AuthorityBoundaryError("source-established semantic relation is unknown")
    if state == "extraction_unresolved":
        raise AuthorityBoundaryError("interpretation/extraction is unresolved")
    if state == "insufficient_authority":
        raise AuthorityBoundaryError("receipt explicitly records insufficient authority")
    if state == "established":
        raise AuthorityBoundaryError(
            "established receipt verification belongs to the parallel authority track"
        )
    raise AuthorityBoundaryError(f"unsupported authority receipt state: {state!r}")


def candidate_internal_record(
    *,
    claim_id: str,
    selection_basis: str,
    observations: list[dict[str, Any]],
    excluded_passage_ids: list[str],
    aperture_observation: dict[str, Any] | None,
) -> dict[str, Any]:
    authority_states = [item["authority"]["state"] for item in observations]
    proposal_count = sum(
        1
        for item in observations
        if isinstance(item.get("measurement"), dict)
        and item["measurement"].get("status") == "CLAIMED"
    )
    return {
        "claim_id": claim_id,
        "selection_basis": selection_basis,
        "semantic_measurements": observations,
        "proposal_count": proposal_count,
        "authority_states": authority_states,
        "semantic_authority": {
            "state": "insufficient_authority",
            "reason": "no_verified_semantic_warrant_module_or_receipt",
            "may_strengthen_conclusion": False,
            "interface_version": AUTHORITY_INTERFACE_VERSION,
        },
        "excluded_passage_ids": sorted(set(excluded_passage_ids)),
        "aperture_observation": aperture_observation,
        "aperture_completeness_conclusion": None,
        "typed_population_operator": {
            "state": "not_executed",
            "reason": "no_authorized_text_to_typed_population_mapping_in_frozen_B_input",
        },
        "deterministic_numeric_operator": {
            "state": "not_executed",
            "reason": "assertion_scope_warrant_not_established_for_raw_text",
        },
    }


def _shadow_policy() -> dict[str, Any]:
    return {
        "candidate": CANDIDATE_ID,
        "authority_interface": AUTHORITY_INTERFACE_VERSION,
        "authority_default": "unresolved",
        "established_receipt_verification": "not_implemented_fail_closed",
        "measurement_instruments": INSTRUMENT_EVIDENCE,
        "assertion_scope_falsifier": ASSERTION_SCOPE_FALSIFIER,
        "unwarranted_measurement_may_strengthen_conclusion": False,
        "source_trust_may_grant_semantic_authority": False,
        "instrument_agreement_may_grant_semantic_authority": False,
    }


def project_shadow_contract_c(
    legacy_contract_c: dict[str, Any],
    *,
    semantic_implementation_sha: str,
    internal_records: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Project a conservative shadow result into frozen Contract C 1.0.0.

    Legacy contribution and scalar-measurement receipts are retained as
    observations. Causal attribution is removed because the candidate has no
    established semantic warrant. Detailed RC7F proposals stay in the internal
    record because Contract C has no structured proposal field and they are not
    authorized premises.
    """
    if len(semantic_implementation_sha) != 40 or any(
        ch not in "0123456789abcdef" for ch in semantic_implementation_sha
    ):
        raise ValueError("semantic_implementation_sha must be 40 lowercase hex characters")

    shadow = copy.deepcopy(legacy_contract_c)
    policy = _shadow_policy()
    shadow["producer"] = {
        "semantic_implementation_sha": semantic_implementation_sha,
        "policy": {
            "sha256": sha256_hex(canonical_bytes(policy)),
            "canonical": policy,
        },
    }
    shadow["execution"] = {"state": "completed"}

    for prop in shadow["propositions"]:
        claim_id = prop["proposition"]["proposition_id"]
        if claim_id not in internal_records:
            raise ValueError(f"missing internal candidate record for {claim_id}")

        contribution_ids = [row["contribution_id"] for row in prop["contributions"]]
        prop["execution"] = {"state": "completed", "completion": "not_checkable"}
        prop["assessments"] = {
            "eligibility": {"state": "not_performed"},
            "semantic_validity": {"state": "performed", "value": "unknown"},
            "aperture_completeness": {"state": "not_performed"},
            "temporal_applicability": {"state": "not_performed"},
        }
        prop["conclusion"] = {
            "reported_verdict": "not_checkable",
            "terminal_branch": "shadow_authority_unresolved",
            "causal_form": "redundant_non_deciding",
            "basis_members": [],
            "residual_contribution_ids": contribution_ids,
            "rule_roles": [],
        }

    shadow.pop("result_set_id", None)
    shadow["result_set_id"] = result_set_identity(shadow)
    return shadow


def classify_legacy_shadow_divergence(
    legacy_contract_c: dict[str, Any], shadow_contract_c: dict[str, Any]
) -> list[dict[str, Any]]:
    legacy = {
        row["proposition"]["proposition_id"]: row for row in legacy_contract_c["propositions"]
    }
    shadow = {
        row["proposition"]["proposition_id"]: row for row in shadow_contract_c["propositions"]
    }
    rows: list[dict[str, Any]] = []
    for claim_id in sorted(legacy):
        old = legacy[claim_id]
        new = shadow[claim_id]
        old_verdict = old["conclusion"]["reported_verdict"] if old.get("conclusion") else None
        new_verdict = new["conclusion"]["reported_verdict"] if new.get("conclusion") else None
        if old_verdict == new_verdict:
            primary = "no_terminal_divergence"
        elif new_verdict == "not_checkable":
            primary = "authority_unresolved"
        else:
            primary = "unsupported_candidate_strengthening"
        rows.append(
            {
                "claim_id": claim_id,
                "legacy_verdict": old_verdict,
                "shadow_verdict": new_verdict,
                "primary_class": primary,
            }
        )
    return rows
