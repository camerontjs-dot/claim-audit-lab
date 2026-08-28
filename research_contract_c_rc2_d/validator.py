"""Independent validator for RC2-D attribution receipts.

This module intentionally imports no Claim Audit Lab production implementation.
It validates only receipt structure, policy binding, and whether the declared
causal class is logically supported by the frozen mutation observations carried
inside the receipt.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

RECEIPT_MARKER = "contract-c-rc2-d-attribution-v0"
REQUIRED_ASSESSMENTS = (
    "eligibility",
    "semantic_validity",
    "aperture_completeness",
    "temporal_applicability",
    "citation",
)
_ALLOWED_CLASSES = {
    "single_necessary",
    "independent_sufficient_alternatives",
    "jointly_sufficient",
    "redundant_non_deciding",
}


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


def policy_hash(policy: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_bytes(policy)).hexdigest()


def _outcome(receipt: dict[str, Any], name: str) -> dict[str, Any] | None:
    mutations = receipt.get("mutation_observations")
    if not isinstance(mutations, dict):
        return None
    value = mutations.get(name)
    return value if isinstance(value, dict) else None


def _verdict(outcome: dict[str, Any] | None) -> str | None:
    if outcome is None:
        return None
    value = outcome.get("final_verdict")
    return value if isinstance(value, str) else None


def validate_receipt(receipt: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if receipt.get("research_receipt") != RECEIPT_MARKER:
        errors.append("unexpected research receipt marker")

    policy = receipt.get("policy")
    if not isinstance(policy, dict):
        errors.append("policy missing")
    else:
        canonical = policy.get("canonical")
        if not isinstance(canonical, dict):
            errors.append("canonical policy missing")
        else:
            observed_hash = policy_hash(canonical)
            if policy.get("sha256") != observed_hash:
                errors.append("policy hash mismatch")
            if policy.get("config_id") != canonical.get("config_id"):
                errors.append("config_id is not bound to canonical policy")

    assessments = receipt.get("generic_assessments")
    if not isinstance(assessments, dict):
        errors.append("generic assessments missing")
    else:
        for name in REQUIRED_ASSESSMENTS:
            value = assessments.get(name)
            if not isinstance(value, dict):
                errors.append(f"generic assessment missing: {name}")
            elif value.get("state") != "not_performed":
                errors.append(f"generic assessment not not_performed: {name}")

    baseline = receipt.get("baseline")
    if not isinstance(baseline, dict):
        errors.append("baseline outcome missing")
        return errors
    target = baseline.get("final_verdict")
    if not isinstance(target, str):
        errors.append("baseline final verdict missing")
        return errors

    causal = receipt.get("causal_claim")
    if not isinstance(causal, dict):
        errors.append("causal claim missing")
        return errors
    classification = causal.get("classification")
    if classification not in _ALLOWED_CLASSES:
        errors.append("unsupported causal classification")
        return errors
    if causal.get("target_verdict") != target:
        errors.append("causal target does not match baseline verdict")

    members = causal.get("members")
    if not isinstance(members, list) or not members or not all(
        isinstance(member, str) and member for member in members
    ):
        errors.append("causal members missing")
        members = []

    mutations = receipt.get("mutation_observations")
    if not isinstance(mutations, dict):
        errors.append("mutation observations missing")
        return errors

    edges = receipt.get("dependency_edges")
    if not isinstance(edges, list) or not edges or not all(
        isinstance(edge, dict) for edge in edges
    ):
        errors.append("dependency edges missing")
        edges = []
    edge_sources = {
        edge.get("from") for edge in edges if isinstance(edge.get("from"), str)
    }

    if classification == "single_necessary":
        removal_name = causal.get("removal_mutation")
        if not isinstance(removal_name, str):
            errors.append("single-necessary removal mutation missing")
        else:
            removal = _outcome(receipt, removal_name)
            if removal is None:
                errors.append("single-necessary removal observation missing")
            elif _verdict(removal) == target:
                errors.append("single-necessary removal did not change target verdict")

    elif classification == "independent_sufficient_alternatives":
        if len(members) < 2:
            errors.append("independent alternatives require at least two members")
        isolated = causal.get("isolated_mutations")
        if not isinstance(isolated, dict):
            errors.append("independent isolated mutations missing")
        else:
            for member in members:
                mutation_name = isolated.get(member)
                if not isinstance(mutation_name, str):
                    errors.append(f"isolated mutation missing for {member}")
                    continue
                observation = _outcome(receipt, mutation_name)
                if observation is None:
                    errors.append(f"isolated observation missing for {member}")
                elif _verdict(observation) != target:
                    errors.append(f"isolated member not sufficient: {member}")
        none_name = causal.get("none_mutation")
        if not isinstance(none_name, str):
            errors.append("independent none mutation missing")
        else:
            none_observation = _outcome(receipt, none_name)
            if none_observation is None:
                errors.append("independent none observation missing")
            elif _verdict(none_observation) == target:
                errors.append("independent alternatives target survives with no member")

        co_maximal = receipt.get("co_maximal_support_refs")
        if not isinstance(co_maximal, list) or sorted(co_maximal) != sorted(members):
            errors.append("co-maximal support set does not preserve all alternatives")

    elif classification == "jointly_sufficient":
        if len(members) < 2:
            errors.append("joint basis requires at least two members")
        isolated = causal.get("isolated_mutations")
        if not isinstance(isolated, dict):
            errors.append("joint isolated mutations missing")
        else:
            for member in members:
                mutation_name = isolated.get(member)
                if not isinstance(mutation_name, str):
                    errors.append(f"joint isolated mutation missing for {member}")
                    continue
                observation = _outcome(receipt, mutation_name)
                if observation is None:
                    errors.append(f"joint isolated observation missing for {member}")
                elif _verdict(observation) == target:
                    errors.append(f"joint member alone still produces target: {member}")
        none_name = causal.get("none_mutation")
        if isinstance(none_name, str):
            none_observation = _outcome(receipt, none_name)
            if none_observation is None:
                errors.append("joint none observation missing")
            elif _verdict(none_observation) == target:
                errors.append("joint target survives with neither member")

    elif classification == "redundant_non_deciding":
        removal_name = causal.get("removal_mutation")
        if not isinstance(removal_name, str):
            errors.append("redundant removal mutation missing")
        else:
            removal = _outcome(receipt, removal_name)
            if removal is None:
                errors.append("redundant removal observation missing")
            elif _verdict(removal) != target:
                errors.append("declared redundant state changes terminal verdict")
        residual = receipt.get("residual_non_deciding")
        if not isinstance(residual, list) or not residual:
            errors.append("redundant receipt lacks residual/non-deciding state")

    for member in members:
        if member not in edge_sources:
            errors.append(f"causal member lacks dependency edge: {member}")

    causal_members = set(members)
    residual = receipt.get("residual_non_deciding", [])
    if classification != "redundant_non_deciding" and isinstance(residual, list):
        overlap = causal_members & {item for item in residual if isinstance(item, str)}
        if overlap:
            errors.append("state is both causal and residual: " + ",".join(sorted(overlap)))

    return errors


def validate_suite(suite: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    receipts = suite.get("receipts")
    if not isinstance(receipts, list) or not receipts:
        return ["suite receipts missing"]

    seen: set[str] = set()
    for index, receipt in enumerate(receipts):
        if not isinstance(receipt, dict):
            errors.append(f"receipt {index} is not an object")
            continue
        family = receipt.get("family_id")
        if not isinstance(family, str):
            errors.append(f"receipt {index} family id missing")
            family = f"index-{index}"
        elif family in seen:
            errors.append(f"duplicate family id: {family}")
        seen.add(family)
        for error in validate_receipt(receipt):
            errors.append(f"{family}: {error}")

    required = {
        "threshold_no_rule",
        "credential_needs_source",
        "low_reliability_residual",
        "unclassified_not_checkable",
        "absolute_wording_joint",
        "tied_independent_support",
    }
    missing = sorted(required - seen)
    if missing:
        errors.append("required families missing: " + ",".join(missing))
    return errors
