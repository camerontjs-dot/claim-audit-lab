from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from claim_audit_lab.production_v1.targeting import (
    TargetAuthoringError,
    author_target,
    canonical_target_bytes,
)

EXPECTED_KEYS = {"lhs_entity", "rhs_entity", "comparison_direction"}


def fields(target: dict[str, Any]) -> dict[str, str]:
    proposition = target["proposition"]
    if proposition["semantic_family"] != "strict_comparison":
        raise AssertionError(f"wrong family: {proposition['semantic_family']}")
    result = proposition["fields"]
    if set(result) != EXPECTED_KEYS:
        raise AssertionError(f"wrong strict_comparison fields: {sorted(result)}")
    return result


def authored(case_id: str, claim: str) -> dict[str, Any]:
    first = author_target(case_id, claim)
    second = author_target(case_id, claim)
    if canonical_target_bytes(first) != canonical_target_bytes(second):
        raise AssertionError("nondeterministic authoring")
    return first


def harmless_variant(claim: str) -> str:
    return "  ".join(claim.rstrip(".").split())


def evaluate(cases_path: Path) -> dict[str, Any]:
    spec = json.loads(cases_path.read_text(encoding="utf-8"))
    failures: list[dict[str, Any]] = []
    authored_targets: dict[str, dict[str, Any]] = {}
    pair_rows: dict[str, list[dict[str, Any]]] = {}

    for row in spec["claims"]:
        case_id = row["case_id"]
        try:
            target = authored(case_id, row["claim"])
            fmap = fields(target)
            if fmap["comparison_direction"] != row["direction"]:
                raise AssertionError(
                    f"direction {fmap['comparison_direction']} != {row['direction']}"
                )
            authored_targets[case_id] = target
            pair_rows.setdefault(row["pair_id"], []).append({**row, "fields": fmap})

            variant = authored(case_id + "-meta", harmless_variant(row["claim"]))
            variant_fields = fields(variant)
            if variant_fields != fmap:
                raise AssertionError("harmless punctuation/whitespace changed semantic fields")
            if (
                variant["proposition"]["text_sha256"]
                == target["proposition"]["text_sha256"]
            ):
                raise AssertionError("exact claim-text binding did not change on text mutation")
        except Exception as exc:
            failures.append(
                {"case_id": case_id, "kind": "authentic_claim", "detail": repr(exc)}
            )

    for pair_id, rows in sorted(pair_rows.items()):
        if len(rows) != 2:
            failures.append(
                {"case_id": pair_id, "kind": "pair", "detail": f"expected 2 rows, got {len(rows)}"}
            )
            continue
        a, b = rows
        fa, fb = a["fields"], b["fields"]
        try:
            if a["pair_mode"] != b["pair_mode"]:
                raise AssertionError("pair mode mismatch")
            if a["pair_mode"] == "same_sides_direction_flip":
                if fa["lhs_entity"] != fb["lhs_entity"] or fa["rhs_entity"] != fb["rhs_entity"]:
                    raise AssertionError("forward/inverse pair changed comparison sides")
                if fa["comparison_direction"] == fb["comparison_direction"]:
                    raise AssertionError("forward/inverse pair did not invert direction")
            elif a["pair_mode"] == "side_swap_same_direction":
                if fa["lhs_entity"] != fb["rhs_entity"] or fa["rhs_entity"] != fb["lhs_entity"]:
                    raise AssertionError("paired claim did not swap comparison sides")
                if fa["comparison_direction"] != fb["comparison_direction"]:
                    raise AssertionError("side-swap pair unexpectedly changed direction")
            else:
                raise AssertionError(f"unknown pair mode {a['pair_mode']}")
        except Exception as exc:
            failures.append({"case_id": pair_id, "kind": "pair", "detail": repr(exc)})

    for row in spec["existing_supported"]:
        try:
            target = authored(row["case_id"], row["claim"])
            fmap = fields(target)
            expected = {
                "lhs_entity": "Alpha",
                "rhs_entity": "Beta",
                "comparison_direction": row["direction"],
            }
            if fmap != expected:
                raise AssertionError(f"canonical #184 fields drifted: {fmap!r}")
        except Exception as exc:
            failures.append(
                {"case_id": row["case_id"], "kind": "existing_supported", "detail": repr(exc)}
            )

    negative_observations: dict[str, str] = {}
    for row in spec["negative_controls"]:
        case_id = row["case_id"]
        try:
            target = author_target(case_id, row["claim"])
        except TargetAuthoringError as exc:
            negative_observations[case_id] = f"REFUSED:{exc}"
            if case_id == "NEG-OTHER-FAMILY":
                failures.append(
                    {
                        "case_id": case_id,
                        "kind": "family_separation",
                        "detail": "direct-event control was refused rather than classified into its existing family",
                    }
                )
            continue
        family = target["proposition"]["semantic_family"]
        negative_observations[case_id] = f"AUTHORED:{family}"
        if case_id == "NEG-OTHER-FAMILY":
            if family != "direct_event_order":
                failures.append(
                    {
                        "case_id": case_id,
                        "kind": "family_separation",
                        "detail": f"other-family claim misclassified as {family}",
                    }
                )
        else:
            failures.append(
                {
                    "case_id": case_id,
                    "kind": "unsafe_acceptance",
                    "detail": f"negative control authored as {family}",
                }
            )

    collision_observations: dict[str, Any] = {}
    field_model_collision = False
    for row in spec["collision_controls"]:
        case_id = row["case_id"]
        try:
            original = authored(case_id + "-original", row["original"])
            original_fields = fields(original)
        except Exception as exc:
            failures.append(
                {
                    "case_id": case_id,
                    "kind": "collision_control_original_unrepresentable",
                    "detail": repr(exc),
                }
            )
            continue

        try:
            mutation = authored(case_id + "-mutation", row["mutation"])
        except TargetAuthoringError as exc:
            collision_observations[case_id] = {
                "mutation": "REFUSED",
                "detail": str(exc),
            }
            continue
        except Exception as exc:
            failures.append(
                {"case_id": case_id, "kind": "collision_control", "detail": repr(exc)}
            )
            continue

        mutation_fields = fields(mutation)
        same = mutation_fields == original_fields
        collision_observations[case_id] = {
            "mutation": "AUTHORED",
            "fields_changed": not same,
        }
        if same:
            field_model_collision = True
            failures.append(
                {
                    "case_id": case_id,
                    "kind": "target_field_collision",
                    "detail": "material claim mutation authored to identical strict_comparison fields",
                }
            )

    for row in spec["metamorphic_controls"]:
        try:
            a = fields(authored(row["case_id"] + "-a", row["a"]))
            b = fields(authored(row["case_id"] + "-b", row["b"]))
            if row["mode"] != "swap_sides_direction_flip":
                raise AssertionError("unknown metamorphic mode")
            if a["lhs_entity"] != b["rhs_entity"] or a["rhs_entity"] != b["lhs_entity"]:
                raise AssertionError("side swap not preserved")
            if a["comparison_direction"] == b["comparison_direction"]:
                raise AssertionError("side swap did not invert direction")
        except Exception as exc:
            failures.append(
                {"case_id": row["case_id"], "kind": "metamorphic", "detail": repr(exc)}
            )

    if not failures:
        disposition = "SUPPORTED_FOR_REAL_CLAIM_COMPARISON_AUTHORING_SUCCESSOR"
    elif field_model_collision:
        disposition = "FALSIFIED_EXISTING_TARGET_FIELD_MODEL_INSUFFICIENT"
    else:
        disposition = "FALSIFIED_AUTHORING_EXTENSION_NOT_DISCRIMINATING"

    return {
        "schema": "cal-v1-real-claim-comparison-authoring-rc0-result",
        "issue": 193,
        "cohort_sha256": spec["frozen_cohort_sha256"],
        "authentic_claim_count": len(spec["claims"]),
        "authentic_claims_authored": len(authored_targets),
        "negative_observations": negative_observations,
        "collision_observations": collision_observations,
        "failures": failures,
        "disposition": disposition,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    report = evaluate(Path(args.cases))
    out = Path(args.out)
    if out.exists():
        raise RuntimeError(f"refusing to overwrite {out}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))
    return 0 if report["disposition"] == "SUPPORTED_FOR_REAL_CLAIM_COMPARISON_AUTHORING_SUCCESSOR" else 1


if __name__ == "__main__":
    raise SystemExit(main())
