#!/usr/bin/env python3
"""Independent stdlib-only structural consumer for an Evidence Bundler V1 package.

This consumer intentionally imports no Evidence Bundler or CAL semantic code.
It validates and reconstructs only the evidence-world structure needed at the
CAL ingress boundary.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

EB_HEAD = "c4e3f97ec8f0bd36180954c3aa382418925bf947"
CONTRACT_A_RELEASE = "529c92b49a34d5c610618551a8737f019f9fa332"
CONTRACT_A_VALIDATOR = "42e5f5b3bf38d677445e9d01ea130ba604e53409"
ENGINE_ID = "evidence_bundler_okapi_bm25_v1"
EXPECTED_ACCEPTED = {
    "cal-eb-v1:child:1": "CAL-EB-V1-S1",
    "cal-eb-v1:child:2": "CAL-EB-V1-S2",
}
FORBIDDEN_SEMANTIC_KEYS = {
    "support",
    "supports",
    "refute",
    "refutes",
    "refutation",
    "verdict",
    "semantic_relation",
    "relation_hint",
    "evidence_role",
}


class StructuralValidationError(ValueError):
    pass


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


def hash_json(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def hash_text(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def handoff_hash(value: dict[str, Any]) -> str:
    payload = dict(value)
    payload.pop("handoff_sha256", None)
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def package_hash(value: dict[str, Any]) -> str:
    payload = dict(value)
    payload.pop("package_sha256", None)
    return hash_json(payload)


def query_id(
    contract_a_sha256: str,
    proposition_id: str,
    text_sha256: str,
    lane: str,
    config_sha256: str,
) -> str:
    digest = hash_json(
        {
            "contract_a_sha256": contract_a_sha256,
            "proposition_id": proposition_id,
            "text_sha256": text_sha256,
            "retrieval_lane": lane,
            "config_sha256": config_sha256,
        }
    ).removeprefix("sha256:")
    return "query:" + digest[:32]


def retrieval_id(qid: str) -> str:
    digest = hash_json({"query_id": qid, "engine": ENGINE_ID}).removeprefix("sha256:")
    return "retrieval:" + digest[:32]


def passage_id(row: dict[str, Any]) -> str:
    digest = hash_json(
        {
            "source_id": row["source_id"],
            "source_content_sha256": row["source_content_sha256"],
            "char_start": row["char_start"],
            "char_end": row["char_end"],
            "passage_sha256": row["passage_sha256"],
        }
    ).removeprefix("sha256:")
    return "passage:" + digest[:32]


def exact_keys(value: Any, expected: set[str], path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise StructuralValidationError(f"{path} must be object")
    if set(value) != expected:
        raise StructuralValidationError(f"{path} key mismatch")
    return value


def array(value: Any, path: str) -> list[Any]:
    if not isinstance(value, list):
        raise StructuralValidationError(f"{path} must be array")
    return value


def semantic_key_scan(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key).lower() in FORBIDDEN_SEMANTIC_KEYS:
                raise StructuralValidationError(f"semantic authority key forbidden at {path}.{key}")
            semantic_key_scan(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            semantic_key_scan(child, f"{path}[{index}]")


def validate_contract_a(value: Any) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    root = exact_keys(
        value,
        {
            "schema",
            "handoff_id",
            "producer",
            "work",
            "root_proposition",
            "decomposition",
            "sources",
            "handoff_sha256",
        },
        "$.contract_a",
    )
    if root["schema"] != "contract-a-wire-candidate-rc2":
        raise StructuralValidationError("Contract A schema mismatch")
    if root["handoff_sha256"] != handoff_hash(root):
        raise StructuralValidationError("Contract A whole-object hash mismatch")

    root_prop = exact_keys(
        root["root_proposition"],
        {"proposition_id", "text", "text_sha256"},
        "$.contract_a.root_proposition",
    )
    if root_prop["text_sha256"] != hash_text(str(root_prop["text"])):
        raise StructuralValidationError("root proposition text hash mismatch")

    decomposition = exact_keys(
        root["decomposition"],
        {"state", "decomposition_id", "operator", "children"},
        "$.contract_a.decomposition",
    )
    if decomposition["state"] != "declared" or decomposition["operator"] != "all_of":
        raise StructuralValidationError("fixture requires declared all_of decomposition")
    children = array(decomposition["children"], "$.contract_a.decomposition.children")
    if len(children) < 2:
        raise StructuralValidationError("declared all_of requires at least two children")
    targets: list[dict[str, Any]] = []
    for index, raw in enumerate(children, start=1):
        child = exact_keys(
            raw,
            {"proposition_id", "text", "text_sha256", "sequence"},
            f"child[{index}]",
        )
        if child["sequence"] != index:
            raise StructuralValidationError("child sequence mismatch")
        if child["text_sha256"] != hash_text(str(child["text"])):
            raise StructuralValidationError("child text hash mismatch")
        targets.append(
            {
                "proposition_id": child["proposition_id"],
                "text": child["text"],
                "text_sha256": child["text_sha256"],
                "role": "declared_child",
                "sequence": index,
            }
        )

    source_ids: set[str] = set()
    for raw in array(root["sources"], "$.contract_a.sources"):
        source = exact_keys(
            raw,
            {"source_id", "media_type", "content", "content_sha256"},
            "source",
        )
        source_id = str(source["source_id"])
        if source_id in source_ids:
            raise StructuralValidationError("duplicate source id")
        source_ids.add(source_id)
        if source["content_sha256"] != hash_text(str(source["content"])):
            raise StructuralValidationError("source content hash mismatch")
    return root, targets


def validate_and_reconstruct(value: Any) -> dict[str, Any]:
    semantic_key_scan(value)
    root = exact_keys(
        value,
        {
            "schema",
            "contract_version",
            "producer",
            "contract_a_authority",
            "contract_a",
            "config",
            "config_sha256",
            "execution_state",
            "primary_targets",
            "retrieval_plans",
            "retrieval_executions",
            "candidates",
            "diagnostics",
            "package_sha256",
        },
        "$",
    )
    if root["schema"] != "evidence-bundler-v1-package-candidate-1":
        raise StructuralValidationError("package schema mismatch")
    if root["package_sha256"] != package_hash(root):
        raise StructuralValidationError("package whole-object hash mismatch")

    authority = exact_keys(
        root["contract_a_authority"],
        {"contract_version", "release_commit", "validator_blob"},
        "$.contract_a_authority",
    )
    if authority != {
        "contract_version": "2.0.0",
        "release_commit": CONTRACT_A_RELEASE,
        "validator_blob": CONTRACT_A_VALIDATOR,
    }:
        raise StructuralValidationError("Contract A authority pin mismatch")

    contract_a, expected_targets = validate_contract_a(root["contract_a"])
    if root["primary_targets"] != expected_targets:
        raise StructuralValidationError("primary targets do not derive exactly from Contract A")

    config = exact_keys(
        root["config"],
        {
            "candidate_depth",
            "retained_k",
            "chunk_max_chars",
            "chunk_overlap_chars",
            "root_diagnostic",
            "retrieval_engine",
            "tokenizer",
            "bm25_k1",
            "bm25_b",
            "source_scope_policy",
            "query_strategy",
        },
        "$.config",
    )
    if root["config_sha256"] != hash_json(config):
        raise StructuralValidationError("config identity mismatch")
    if config["retrieval_engine"] != ENGINE_ID:
        raise StructuralValidationError("retrieval engine mismatch")
    if config["root_diagnostic"] is not False:
        raise StructuralValidationError("fixture must keep root diagnostic disabled")

    sources = {str(row["source_id"]): row for row in contract_a["sources"]}
    source_ids = sorted(sources)
    targets = {str(row["proposition_id"]): row for row in expected_targets}

    plan_keys = {
        "retrieval_id",
        "query_id",
        "proposition_id",
        "retrieval_lane",
        "query_text_sha256",
        "requested_source_ids",
        "intended_retrieval_ids",
    }
    plans: dict[str, dict[str, Any]] = {}
    for raw in array(root["retrieval_plans"], "$.retrieval_plans"):
        plan = exact_keys(raw, plan_keys, "retrieval plan")
        proposition_id = str(plan["proposition_id"])
        target = targets.get(proposition_id)
        if target is None or plan["retrieval_lane"] != "declared_child":
            raise StructuralValidationError("invalid normative lane")
        qid = query_id(
            str(contract_a["handoff_sha256"]),
            proposition_id,
            str(target["text_sha256"]),
            "declared_child",
            str(root["config_sha256"]),
        )
        rid = retrieval_id(qid)
        if plan["query_id"] != qid or plan["retrieval_id"] != rid:
            raise StructuralValidationError("content-derived query/retrieval identity mismatch")
        if plan["requested_source_ids"] != source_ids or plan["intended_retrieval_ids"] != [rid]:
            raise StructuralValidationError("source scope or intended retrieval mismatch")
        plans[rid] = plan
    if len(plans) != len(targets):
        raise StructuralValidationError("one retrieval plan required per target")

    execution_keys = {
        "retrieval_id",
        "status",
        "searched_source_ids",
        "returned_source_ids",
        "returned_count",
        "candidate_depth_limit",
        "candidate_depth_hit",
        "aperture_state",
    }
    executions: dict[str, dict[str, Any]] = {}
    for raw in array(root["retrieval_executions"], "$.retrieval_executions"):
        execution = exact_keys(raw, execution_keys, "retrieval execution")
        rid = str(execution["retrieval_id"])
        if rid not in plans or execution["status"] != "completed":
            raise StructuralValidationError("fixture retrieval must be completed")
        count = execution["returned_count"]
        if not isinstance(count, int) or isinstance(count, bool):
            raise StructuralValidationError("returned_count type invalid")
        if not 0 <= count <= int(config["candidate_depth"]):
            raise StructuralValidationError("returned_count bounds invalid")
        if execution["searched_source_ids"] != source_ids:
            raise StructuralValidationError("searched source scope mismatch")
        hit = count == config["candidate_depth"]
        expected_aperture = "bounded_at_limit" if hit else "bounded_under_limit"
        if execution["candidate_depth_hit"] != hit or execution["aperture_state"] != expected_aperture:
            raise StructuralValidationError("aperture state mismatch")
        executions[rid] = execution
    if len(executions) != len(plans):
        raise StructuralValidationError("execution coverage mismatch")

    candidate_keys = {
        "retrieval_id",
        "query_id",
        "proposition_id",
        "retrieval_lane",
        "passage_id",
        "source_id",
        "source_content_sha256",
        "char_start",
        "char_end",
        "passage_sha256",
        "text",
        "nomination_rank",
        "selection_state",
        "admission_state",
    }
    ranks: dict[str, list[int]] = {rid: [] for rid in plans}
    returned_sources: dict[str, set[str]] = {rid: set() for rid in plans}
    accepted: list[dict[str, Any]] = []
    candidates = array(root["candidates"], "$.candidates")
    for raw in candidates:
        row = exact_keys(raw, candidate_keys, "candidate")
        rid = str(row["retrieval_id"])
        plan = plans.get(rid)
        if plan is None:
            raise StructuralValidationError("candidate retrieval unknown")
        if (
            row["query_id"] != plan["query_id"]
            or row["proposition_id"] != plan["proposition_id"]
            or row["retrieval_lane"] != "declared_child"
        ):
            raise StructuralValidationError("candidate plan binding mismatch")
        source = sources.get(str(row["source_id"]))
        if source is None or row["source_content_sha256"] != source["content_sha256"]:
            raise StructuralValidationError("candidate source binding mismatch")
        start, end = row["char_start"], row["char_end"]
        if not isinstance(start, int) or not isinstance(end, int) or start < 0 or end <= start:
            raise StructuralValidationError("candidate offsets invalid")
        text = str(row["text"])
        if str(source["content"])[start:end] != text:
            raise StructuralValidationError("candidate bytes/offsets mismatch")
        if row["passage_sha256"] != hash_text(text) or row["passage_id"] != passage_id(row):
            raise StructuralValidationError("candidate passage identity mismatch")
        rank = row["nomination_rank"]
        if not isinstance(rank, int) or isinstance(rank, bool) or rank < 1:
            raise StructuralValidationError("candidate rank invalid")
        expected_selection = "retained" if rank <= config["retained_k"] else "not_retained"
        if row["selection_state"] != expected_selection:
            raise StructuralValidationError("candidate selection state mismatch")
        if expected_selection == "retained":
            if row["admission_state"] not in {"accepted", "rejected", "needs-review"}:
                raise StructuralValidationError("retained admission state invalid")
        elif row["admission_state"] != "not_applicable":
            raise StructuralValidationError("non-retained candidate cannot be admitted")
        ranks[rid].append(rank)
        returned_sources[rid].add(str(row["source_id"]))
        if row["admission_state"] == "accepted":
            accepted.append(
                {
                    "proposition_id": row["proposition_id"],
                    "proposition_text": targets[str(row["proposition_id"])]["text"],
                    "proposition_text_sha256": targets[str(row["proposition_id"])]["text_sha256"],
                    "retrieval_lane": row["retrieval_lane"],
                    "source_id": row["source_id"],
                    "source_content_sha256": row["source_content_sha256"],
                    "passage_id": row["passage_id"],
                    "char_start": row["char_start"],
                    "char_end": row["char_end"],
                    "passage_sha256": row["passage_sha256"],
                    "text": row["text"],
                    "admission_state": row["admission_state"],
                    "aperture_state": executions[rid]["aperture_state"],
                }
            )

    for rid, execution in executions.items():
        if sorted(ranks[rid]) != list(range(1, execution["returned_count"] + 1)):
            raise StructuralValidationError("candidate rank/count mismatch")
        if sorted(returned_sources[rid]) != execution["returned_source_ids"]:
            raise StructuralValidationError("returned source set mismatch")

    diagnostics = exact_keys(root["diagnostics"], {"root_retrieval"}, "$.diagnostics")
    if diagnostics["root_retrieval"] is not None:
        raise StructuralValidationError("fixture must not use root diagnostic rescue")
    if root["execution_state"] != "complete":
        raise StructuralValidationError("fixture execution must be complete")

    observed = {str(row["proposition_id"]): str(row["source_id"]) for row in accepted}
    if observed != EXPECTED_ACCEPTED or len(accepted) != 2:
        raise StructuralValidationError(
            f"accepted structural projection mismatch: observed={observed!r}"
        )
    return {
        "schema": "cal-eb-v1-structural-projection-v1",
        "eb_head": EB_HEAD,
        "package_sha256": root["package_sha256"],
        "accepted_evidence": sorted(accepted, key=lambda row: str(row["proposition_id"])),
        "support_refutation_or_verdict_semantics_consumed": False,
    }


def reseal(value: dict[str, Any]) -> dict[str, Any]:
    value["package_sha256"] = package_hash(value)
    return value


def expect_refused(name: str, mutated: dict[str, Any]) -> dict[str, Any]:
    try:
        validate_and_reconstruct(reseal(mutated))
    except StructuralValidationError as exc:
        return {"name": name, "refused": True, "reason": str(exc)}
    return {"name": name, "refused": False, "reason": None}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    package = json.loads(args.package.read_text(encoding="utf-8"))
    projection = validate_and_reconstruct(package)

    mutations: list[dict[str, Any]] = []
    changed = deepcopy(package)
    changed["contract_a"]["decomposition"]["children"][0]["text"] += " changed"
    mutations.append(expect_refused("proposition_text_substitution", changed))

    changed = deepcopy(package)
    changed["retrieval_plans"][0]["retrieval_lane"] = "root"
    mutations.append(expect_refused("normative_lane_substitution", changed))

    changed = deepcopy(package)
    changed["candidates"][0]["text"] += " changed"
    mutations.append(expect_refused("passage_bytes_substitution", changed))

    changed = deepcopy(package)
    changed["retrieval_plans"][0]["query_id"] = "query:" + "0" * 32
    mutations.append(expect_refused("query_identity_substitution", changed))

    changed = deepcopy(package)
    nonretained = next(
        (row for row in changed["candidates"] if row["selection_state"] == "not_retained"),
        None,
    )
    if nonretained is None:
        raise StructuralValidationError("fixture must include a non-retained mutation control")
    nonretained["admission_state"] = "accepted"
    mutations.append(expect_refused("nonretained_admission_laundering", changed))

    changed = deepcopy(package)
    changed["retrieval_executions"][0]["aperture_state"] = "bounded_at_limit"
    changed["retrieval_executions"][0]["candidate_depth_hit"] = True
    mutations.append(expect_refused("aperture_state_substitution", changed))

    changed = deepcopy(package)
    changed["verdict"] = "supported"
    mutations.append(expect_refused("semantic_authority_injection", changed))

    receipt = {
        "schema": "cal-eb-v1-structural-consumer-receipt-v1",
        "eb_head": EB_HEAD,
        "valid_package_accepted": True,
        "projection": projection,
        "mutations": mutations,
        "all_mutations_refused": all(bool(row["refused"]) for row in mutations),
        "consumer_imports_evidence_bundler": False,
        "consumer_imports_cal_semantic_engine": False,
        "production_promotion_authorized": False,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, sort_keys=True))
    return 0 if receipt["all_mutations_refused"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
