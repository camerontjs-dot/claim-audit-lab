"""Execute frozen RC3 exception/scoped-rule semantic discrimination.

Post-freeze apparatus only. The scientific cohort and S4/S5 mechanisms are
imported from the preregistration commit and are never modified here.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import torch
from sklearn.metrics import f1_score
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from research.exception_scoped_rule_semantics_rc3.build_cohort import (
    EXPECTED_SHA256,
    build,
    canonical_bytes,
)
from research.exception_scoped_rule_semantics_rc3.mechanisms import (
    decompose_for_nli,
    typed_relation,
)
from research.nli_independent_calibration_rc2.run_calibration import (
    MODELS,
    adverse_conservative,
    label_order,
    score_case,
)

LABELS = ("entailment", "neutral", "contradiction")
SYSTEMS = (
    "S0_incumbent",
    "S1_same_family_large",
    "S2_long_context",
    "S3_adverse_conservative",
    "S4_decomposition_incumbent",
    "S5_typed_scoped_rule",
)
CRITICAL_PROHIBITED_OUTPUT = {
    "exception_not_negation": "entailment",
    "narrow_to_broad": "entailment",
    "alternate_to_no_process": "entailment",
    "temporary_to_permanent": "entailment",
}


def _macro_f1(targets: list[str], outputs: list[str]) -> float:
    return float(
        f1_score(
            targets,
            outputs,
            labels=list(LABELS),
            average="macro",
            zero_division=0,
        )
    )


def confusion(targets: list[str], outputs: list[str]) -> dict[str, dict[str, int]]:
    columns = list(LABELS) + ["unresolved"]
    matrix = {target: {output: 0 for output in columns} for target in LABELS}
    for target, output in zip(targets, outputs, strict=True):
        matrix[target][output] += 1
    return matrix


def system_metrics(cases: list[dict[str, Any]], outputs: dict[str, str]) -> dict[str, Any]:
    targets = [str(case["target"]) for case in cases]
    preds = [outputs[case["case_id"]] for case in cases]
    decided_idx = [i for i, output in enumerate(preds) if output != "unresolved"]
    exact = sum(pred == target for pred, target in zip(preds, targets, strict=True))
    decided_targets = [targets[i] for i in decided_idx]
    decided_preds = [preds[i] for i in decided_idx]
    per_family: dict[str, Any] = {}
    for family in sorted({str(case["family"]) for case in cases}):
        family_cases = [case for case in cases if case["family"] == family]
        family_targets = [str(case["target"]) for case in family_cases]
        family_preds = [outputs[case["case_id"]] for case in family_cases]
        family_exact = sum(
            pred == target
            for pred, target in zip(family_preds, family_targets, strict=True)
        )
        per_family[family] = {
            "n": len(family_cases),
            "correct": family_exact,
            "accuracy_all_unresolved_wrong": family_exact / len(family_cases),
            "macro_f1_all_unresolved_wrong": _macro_f1(family_targets, family_preds),
            "unresolved": sum(pred == "unresolved" for pred in family_preds),
            "false_adverse": sum(
                pred == "contradiction" and target != "contradiction"
                for pred, target in zip(family_preds, family_targets, strict=True)
            ),
        }

    return {
        "n": len(cases),
        "correct": exact,
        "accuracy_all_unresolved_wrong": exact / len(cases),
        "macro_f1_all_unresolved_wrong": _macro_f1(targets, preds),
        "decided": len(decided_idx),
        "coverage": len(decided_idx) / len(cases),
        "selective_accuracy": (
            sum(
                decided_preds[i] == decided_targets[i]
                for i in range(len(decided_idx))
            )
            / len(decided_idx)
            if decided_idx
            else None
        ),
        "macro_f1_decided": (
            _macro_f1(decided_targets, decided_preds) if decided_idx else None
        ),
        "unresolved": len(cases) - len(decided_idx),
        "wrong_decided": sum(preds[i] != targets[i] for i in decided_idx),
        "neutral_to_contradiction": sum(
            target == "neutral" and pred == "contradiction"
            for pred, target in zip(preds, targets, strict=True)
        ),
        "entailment_to_contradiction": sum(
            target == "entailment" and pred == "contradiction"
            for pred, target in zip(preds, targets, strict=True)
        ),
        "contradiction_to_neutral": sum(
            target == "contradiction" and pred == "neutral"
            for pred, target in zip(preds, targets, strict=True)
        ),
        "false_adverse": sum(
            pred == "contradiction" and target != "contradiction"
            for pred, target in zip(preds, targets, strict=True)
        ),
        "confusion": confusion(targets, preds),
        "per_family": per_family,
    }


def critical_error_metrics(
    cases: list[dict[str, Any]], outputs: dict[str, str]
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    observed_types = sorted(
        {
            str(case["critical_error_type"])
            for case in cases
            if case.get("critical_error_type") is not None
        }
    )
    for error_type in observed_types:
        subset = [case for case in cases if case.get("critical_error_type") == error_type]
        prohibited = CRITICAL_PROHIBITED_OUTPUT.get(error_type)
        any_incorrect = [
            case["case_id"]
            for case in subset
            if outputs[case["case_id"]] != case["target"]
        ]
        signature_failures = (
            [
                case["case_id"]
                for case in subset
                if outputs[case["case_id"]] == prohibited
                and outputs[case["case_id"]] != case["target"]
            ]
            if prohibited is not None
            else []
        )
        result[error_type] = {
            "n": len(subset),
            "prohibited_output": prohibited,
            "any_incorrect": len(any_incorrect),
            "any_incorrect_case_ids": any_incorrect,
            "semantic_signature_error": len(signature_failures),
            "semantic_signature_error_rate": len(signature_failures) / len(subset),
            "semantic_signature_case_ids": signature_failures,
        }
    return result


def mutation_metrics(
    mutation_pairs: list[dict[str, Any]], outputs: dict[str, str]
) -> dict[str, Any]:
    rows = []
    exact = 0
    for pair in mutation_pairs:
        before = outputs[pair["before"]]
        after = outputs[pair["after"]]
        ok = before == pair["expected_before"] and after == pair["expected_after"]
        exact += int(ok)
        rows.append(
            {
                **pair,
                "observed_before": before,
                "observed_after": after,
                "pair_consistent": ok,
            }
        )
    return {
        "n_pairs": len(mutation_pairs),
        "exact_consistent_pairs": exact,
        "mutation_consistency": exact / len(mutation_pairs),
        "pairs": rows,
    }


def matched_pair_metrics(
    cases: list[dict[str, Any]], outputs: dict[str, str]
) -> dict[str, Any]:
    """Use shared-premise controlled hypotheses as frozen matched comparisons."""
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for case in cases:
        groups[str(case["premise"])].append(case)

    group_rows = [group for group in groups.values() if len(group) >= 2]
    pairs = list(
        itertools.chain.from_iterable(
            itertools.combinations(group, 2) for group in group_rows
        )
    )
    consistent = 0
    failures: list[list[str]] = []
    for left, right in pairs:
        ok = (
            outputs[left["case_id"]] == left["target"]
            and outputs[right["case_id"]] == right["target"]
        )
        consistent += int(ok)
        if not ok:
            failures.append([left["case_id"], right["case_id"]])

    group_exact = sum(
        all(outputs[case["case_id"]] == case["target"] for case in group)
        for group in group_rows
    )
    return {
        "definition": (
            "All unordered hypothesis pairs sharing an identical frozen premise; "
            "a pair is consistent only when both relations match independent gold."
        ),
        "matched_groups": len(group_rows),
        "matched_groups_all_correct": group_exact,
        "matched_group_consistency": (
            group_exact / len(group_rows) if group_rows else None
        ),
        "matched_pairs": len(pairs),
        "matched_pairs_consistent": consistent,
        "matched_pair_consistency": consistent / len(pairs) if pairs else None,
        "failed_pairs": failures,
    }


def disagreement_metrics(
    primary_cases: list[dict[str, Any]],
    model_measurements: dict[str, dict[str, dict[str, Any]]],
) -> dict[str, Any]:
    unanimous: list[dict[str, Any]] = []
    disagreement: list[dict[str, Any]] = []
    polar: list[dict[str, Any]] = []
    for case in primary_cases:
        cid = case["case_id"]
        votes = [
            model_measurements[name][cid]["predicted"] for name, _, _ in MODELS
        ]
        if len(set(votes)) == 1:
            unanimous.append(case)
        else:
            disagreement.append(case)
        if "entailment" in votes and "contradiction" in votes:
            polar.append(case)

    def incumbent_error_rate(subset: list[dict[str, Any]]) -> float | None:
        if not subset:
            return None
        return sum(
            model_measurements["incumbent_base"][case["case_id"]]["predicted"]
            != case["target"]
            for case in subset
        ) / len(subset)

    unanimous_rate = incumbent_error_rate(unanimous)
    disagreement_rate = incumbent_error_rate(disagreement)
    relative_risk = (
        disagreement_rate / unanimous_rate
        if disagreement_rate is not None
        and unanimous_rate is not None
        and unanimous_rate > 0
        else None
    )
    return {
        "n": len(primary_cases),
        "unanimous_cases": len(unanimous),
        "disagreement_cases": len(disagreement),
        "model_disagreement_incidence": len(disagreement) / len(primary_cases),
        "incumbent_error_rate_unanimous": unanimous_rate,
        "incumbent_error_rate_disagreement": disagreement_rate,
        "relative_error_risk_disagreement_vs_unanimity": relative_risk,
        "polar_conflict_cases": len(polar),
        "unanimous_error_case_ids": [
            case["case_id"]
            for case in unanimous
            if model_measurements["incumbent_base"][case["case_id"]]["predicted"]
            != case["target"]
        ],
        "disagreement_case_ids": [case["case_id"] for case in disagreement],
        "polar_conflict_case_ids": [case["case_id"] for case in polar],
    }


def run(output_dir: Path) -> dict[str, Any]:
    cohort = build()
    raw = canonical_bytes(cohort)
    actual_sha = hashlib.sha256(raw).hexdigest()
    if actual_sha != EXPECTED_SHA256:
        raise RuntimeError(f"frozen cohort mismatch: {actual_sha}")

    cases = cohort["cases"]
    primary_cases = [case for case in cases if case.get("primary") is True]
    mutation_cases = [
        case
        for case in cases
        if case.get("primary") is False and case.get("target") in LABELS
    ]
    ambiguous_cases = [case for case in cases if case.get("target") is None]
    if len(primary_cases) != 84 or len(mutation_cases) != 20 or len(ambiguous_cases) != 6:
        raise RuntimeError("RC3 cohort partition changed")

    torch.set_grad_enabled(False)
    torch.manual_seed(0)

    model_measurements: dict[str, dict[str, dict[str, Any]]] = {}
    model_metadata: dict[str, Any] = {}
    decomposition_measurements: dict[str, dict[str, Any]] = {}

    for name, model_id, revision in MODELS:
        tokenizer = AutoTokenizer.from_pretrained(model_id, revision=revision)
        model = AutoModelForSequenceClassification.from_pretrained(
            model_id, revision=revision
        )
        model.eval()
        order = label_order(model)
        scored: dict[str, dict[str, Any]] = {}
        for case in cases:
            scored[case["case_id"]] = score_case(
                model,
                tokenizer,
                order,
                case["premise"],
                case["hypothesis"],
            )

        for case in cases[:3]:
            again = score_case(
                model,
                tokenizer,
                order,
                case["premise"],
                case["hypothesis"],
            )
            first = scored[case["case_id"]]
            if again["predicted"] != first["predicted"]:
                raise RuntimeError(f"{name}: nondeterministic sentinel label")
            if any(
                abs(a - b) > 1e-6
                for a, b in zip(
                    again["canonical_logits"],
                    first["canonical_logits"],
                    strict=True,
                )
            ):
                raise RuntimeError(f"{name}: nondeterministic sentinel logits")

        model_measurements[name] = scored
        model_metadata[name] = {
            "model_id": model_id,
            "revision": revision,
            "label_order_native": list(order),
        }

        if name == "incumbent_base":
            for case in cases:
                decomposed = decompose_for_nli(case["premise"])
                decomposition_measurements[case["case_id"]] = {
                    "decomposed_premise": decomposed,
                    "changed": decomposed != case["premise"],
                    "measurement": score_case(
                        model,
                        tokenizer,
                        order,
                        decomposed,
                        case["hypothesis"],
                    ),
                }

    typed_measurements: dict[str, dict[str, Any]] = {}
    for case in cases:
        relation, reason, state = typed_relation(case["premise"], case["hypothesis"])
        typed_measurements[case["case_id"]] = {
            "predicted": relation,
            "reason": reason,
            "state": state,
        }

    outputs: dict[str, dict[str, str]] = {system: {} for system in SYSTEMS}
    for case in cases:
        cid = case["case_id"]
        votes = [
            model_measurements[name][cid]["predicted"] for name, _, _ in MODELS
        ]
        outputs["S0_incumbent"][cid] = model_measurements["incumbent_base"][cid][
            "predicted"
        ]
        outputs["S1_same_family_large"][cid] = model_measurements[
            "same_family_large"
        ][cid]["predicted"]
        outputs["S2_long_context"][cid] = model_measurements["long_context_base"][cid][
            "predicted"
        ]
        outputs["S3_adverse_conservative"][cid] = adverse_conservative(votes)
        outputs["S4_decomposition_incumbent"][cid] = decomposition_measurements[cid][
            "measurement"
        ]["predicted"]
        outputs["S5_typed_scoped_rule"][cid] = typed_measurements[cid]["predicted"]

    primary_metrics = {
        system: system_metrics(primary_cases, outputs[system]) for system in SYSTEMS
    }
    critical_metrics = {
        system: critical_error_metrics(primary_cases, outputs[system])
        for system in SYSTEMS
    }
    mutation = {
        system: mutation_metrics(cohort["mutation_pairs"], outputs[system])
        for system in SYSTEMS
    }
    matched = {
        system: matched_pair_metrics(primary_cases, outputs[system])
        for system in SYSTEMS
    }
    disagreement = disagreement_metrics(primary_cases, model_measurements)

    ambiguous_diagnostics = []
    for case in ambiguous_cases:
        cid = case["case_id"]
        ambiguous_diagnostics.append(
            {
                "case_id": cid,
                "family": case["family"],
                "premise": case["premise"],
                "hypothesis": case["hypothesis"],
                "semantic_rationale": case["semantic_rationale"],
                "outputs": {system: outputs[system][cid] for system in SYSTEMS},
            }
        )

    measurements = {
        "schema_version": "cal-exception-scoped-rule-semantics-rc3-measurements-v0.1",
        "authority": "non_authoritative_research",
        "cohort_sha256": "sha256:" + actual_sha,
        "model_metadata": model_metadata,
        "model_measurements": model_measurements,
        "decomposition_measurements": decomposition_measurements,
        "typed_measurements": typed_measurements,
        "system_outputs": outputs,
    }
    results = {
        "schema_version": "cal-exception-scoped-rule-semantics-rc3-results-v0.1",
        "authority": "non_authoritative_research",
        "cohort_sha256": "sha256:" + actual_sha,
        "counts": {
            "all": len(cases),
            "primary": len(primary_cases),
            "mutation_cases": len(mutation_cases),
            "mutation_pairs": len(cohort["mutation_pairs"]),
            "evaluator_ambiguous": len(ambiguous_cases),
        },
        "primary_metrics": primary_metrics,
        "critical_semantic_error_metrics": critical_metrics,
        "mutation_metrics": mutation,
        "matched_pair_metrics": matched,
        "disagreement": disagreement,
        "evaluator_ambiguous_diagnostics": ambiguous_diagnostics,
        "production_behavior_changed": False,
        "promotion_authorized": False,
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    measurement_path = output_dir / "MEASUREMENTS.json"
    result_path = output_dir / "RESULTS.json"
    measurement_path.write_text(
        json.dumps(measurements, indent=2, sort_keys=True) + "\n"
    )
    result_path.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")

    print(
        json.dumps(
            {
                "cohort_sha256": actual_sha,
                "primary_metrics": {
                    system: {
                        "accuracy": primary_metrics[system][
                            "accuracy_all_unresolved_wrong"
                        ],
                        "macro_f1": primary_metrics[system][
                            "macro_f1_all_unresolved_wrong"
                        ],
                        "coverage": primary_metrics[system]["coverage"],
                        "selective_accuracy": primary_metrics[system][
                            "selective_accuracy"
                        ],
                        "false_adverse": primary_metrics[system]["false_adverse"],
                    }
                    for system in SYSTEMS
                },
                "mutation_consistency": {
                    system: mutation[system]["mutation_consistency"]
                    for system in SYSTEMS
                },
            },
            indent=2,
            sort_keys=True,
        )
    )
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    run(args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
