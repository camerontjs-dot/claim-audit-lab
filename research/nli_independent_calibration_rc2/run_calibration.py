#!/usr/bin/env python3
"""Run RC2 independent disagreement replication and held-out temperature calibration."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
import platform
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
import torch
from scipy.optimize import minimize_scalar
from scipy.special import logsumexp
from sklearn.metrics import f1_score
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from research.nli_independent_calibration_rc2.build_cohort import (
    build,
    canonical_bytes,
    validate,
)

EXPECTED_COHORT_SHA256 = "c5f64d6ad73d198aef575b5274280363bb71fc99aac78197e3abf13b13599f2d"
MODELS: tuple[tuple[str, str, str], ...] = (
    (
        "incumbent_base",
        "MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli",
        "6f5cf0a2b59cabb106aca4c287eed12e357e90eb",
    ),
    (
        "same_family_large",
        "MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli",
        "0de4830e69aa5710af98b05f2c4d001d0edc0e52",
    ),
    (
        "long_context_base",
        "tasksource/deberta-base-long-nli",
        "d6e08f68489c9ac015ba3071f90ac0976cbc1fff",
    ),
)
LABELS = ("entailment", "neutral", "contradiction")
LABEL_TO_INDEX = {label: i for i, label in enumerate(LABELS)}


def normalize_label(label: str) -> str:
    low = label.lower()
    for target in LABELS:
        if target in low:
            return target
    raise ValueError(f"unrecognized NLI label: {label!r}")


def label_order(model: Any) -> tuple[str, ...]:
    id2label = model.config.id2label
    order = tuple(normalize_label(str(id2label[i])) for i in range(len(id2label)))
    if len(order) != 3 or set(order) != set(LABELS):
        raise ValueError(f"ambiguous/incompatible three-way label map: {order}")
    return order


def native_max_length(model: Any, tokenizer: Any) -> int:
    vals: list[int] = []
    config_max = getattr(model.config, "max_position_embeddings", None)
    if isinstance(config_max, int) and 8 <= config_max <= 100_000:
        vals.append(config_max)
    tokenizer_max = getattr(tokenizer, "model_max_length", None)
    if isinstance(tokenizer_max, int) and 8 <= tokenizer_max <= 100_000:
        vals.append(tokenizer_max)
    if not vals:
        raise ValueError("cannot establish finite context limit")
    return min(vals)


def reorder_logits(raw_logits: list[float], order: tuple[str, ...]) -> np.ndarray:
    by_label = {order[i]: raw_logits[i] for i in range(3)}
    return np.array([by_label[label] for label in LABELS], dtype=np.float64)


def softmax(logits: np.ndarray) -> np.ndarray:
    shifted = logits - np.max(logits)
    exp = np.exp(shifted)
    return exp / exp.sum()


def score_case(
    model: Any,
    tokenizer: Any,
    order: tuple[str, ...],
    premise: str,
    hypothesis: str,
) -> dict[str, Any]:
    max_length = native_max_length(model, tokenizer)
    raw = tokenizer(premise, hypothesis, truncation=False)
    if len(raw["input_ids"]) > 512 and max_length <= 512:
        raise RuntimeError(
            f"RC2 semantic case exceeds 512-token aperture: {len(raw['input_ids'])}"
        )
    encoded = tokenizer(
        premise,
        hypothesis,
        return_tensors="pt",
        truncation=True,
        max_length=max_length,
    )
    with torch.no_grad():
        raw_logits_tensor = model(**encoded).logits[0]
    raw_logits = [float(x) for x in raw_logits_tensor]
    canonical_logits = reorder_logits(raw_logits, order)
    probs = softmax(canonical_logits)
    pred = LABELS[int(np.argmax(canonical_logits))]
    return {
        "predicted": pred,
        "canonical_logits": [float(x) for x in canonical_logits],
        "probabilities": {LABELS[i]: float(probs[i]) for i in range(3)},
        "untruncated_tokens": len(raw["input_ids"]),
        "encoded_tokens": int(encoded["input_ids"].shape[1]),
        "native_max_length": max_length,
        "truncated": len(raw["input_ids"]) > max_length,
    }


def multiclass_nll(logits: np.ndarray, targets: np.ndarray, temperature: float) -> float:
    scaled = logits / temperature
    return float(
        np.mean(logsumexp(scaled, axis=1) - scaled[np.arange(len(targets)), targets])
    )


def fit_temperature(logits: np.ndarray, targets: np.ndarray) -> float:
    result = minimize_scalar(
        lambda t: multiclass_nll(logits, targets, float(t)),
        bounds=(0.05, 20.0),
        method="bounded",
        options={"xatol": 1e-8, "maxiter": 500},
    )
    if not result.success:
        raise RuntimeError(f"temperature optimization failed: {result.message}")
    return float(result.x)


def probabilities_from_logits(logits: np.ndarray, temperature: float = 1.0) -> np.ndarray:
    scaled = logits / temperature
    shifted = scaled - scaled.max(axis=1, keepdims=True)
    exp = np.exp(shifted)
    return exp / exp.sum(axis=1, keepdims=True)


def brier_score(probs: np.ndarray, targets: np.ndarray) -> float:
    one_hot = np.zeros_like(probs)
    one_hot[np.arange(len(targets)), targets] = 1.0
    return float(np.mean(np.sum((probs - one_hot) ** 2, axis=1)))


def ece_10(probs: np.ndarray, targets: np.ndarray) -> float:
    conf = probs.max(axis=1)
    pred = probs.argmax(axis=1)
    correct = pred == targets
    total = len(targets)
    ece = 0.0
    for i in range(10):
        lo = i / 10.0
        hi = (i + 1) / 10.0
        if i == 9:
            mask = (conf >= lo) & (conf <= hi)
        else:
            mask = (conf >= lo) & (conf < hi)
        count = int(mask.sum())
        if count:
            ece += (count / total) * abs(float(correct[mask].mean()) - float(conf[mask].mean()))
    return float(ece)


def reliability_metrics(
    logits: np.ndarray,
    targets: np.ndarray,
    temperature: float,
) -> dict[str, Any]:
    probs = probabilities_from_logits(logits, temperature)
    pred = probs.argmax(axis=1)
    correct_mask = pred == targets
    return {
        "nll": multiclass_nll(logits, targets, temperature),
        "brier": brier_score(probs, targets),
        "ece_10": ece_10(probs, targets),
        "mean_confidence_correct": (
            float(probs.max(axis=1)[correct_mask].mean()) if correct_mask.any() else None
        ),
        "mean_confidence_incorrect": (
            float(probs.max(axis=1)[~correct_mask].mean()) if (~correct_mask).any() else None
        ),
    }


def confusion(outputs: list[str], targets: list[str]) -> dict[str, dict[str, int]]:
    columns = list(LABELS) + ["unresolved"]
    matrix = {
        target: {output: 0 for output in columns}
        for target in LABELS
    }
    for target, output in zip(targets, outputs, strict=True):
        matrix[target][output] += 1
    return matrix


def system_metrics(outputs: list[str], targets: list[str]) -> dict[str, Any]:
    decided = [i for i, output in enumerate(outputs) if output != "unresolved"]
    exact = sum(outputs[i] == targets[i] for i in range(len(outputs)))
    y_true_decided = [targets[i] for i in decided]
    y_pred_decided = [outputs[i] for i in decided]
    macro = (
        float(f1_score(y_true_decided, y_pred_decided, labels=list(LABELS), average="macro", zero_division=0))
        if decided
        else None
    )
    return {
        "n": len(outputs),
        "decided": len(decided),
        "coverage": len(decided) / len(outputs),
        "exact_correct_all": exact,
        "accuracy_all_unresolved_wrong": exact / len(outputs),
        "selective_accuracy": (
            sum(outputs[i] == targets[i] for i in decided) / len(decided)
            if decided
            else None
        ),
        "macro_f1_decided": macro,
        "wrong_decided": sum(outputs[i] != targets[i] for i in decided),
        "unresolved": len(outputs) - len(decided),
        "false_adverse": sum(
            outputs[i] == "contradiction" and targets[i] != "contradiction"
            for i in decided
        ),
        "neutral_to_contradiction": sum(
            targets[i] == "neutral" and outputs[i] == "contradiction"
            for i in decided
        ),
        "entailment_to_contradiction": sum(
            targets[i] == "entailment" and outputs[i] == "contradiction"
            for i in decided
        ),
        "contradiction_to_neutral": sum(
            targets[i] == "contradiction" and outputs[i] == "neutral"
            for i in decided
        ),
        "contradiction_to_entailment": sum(
            targets[i] == "contradiction" and outputs[i] == "entailment"
            for i in decided
        ),
        "confusion": confusion(outputs, targets),
    }


def majority(votes: list[str]) -> str:
    label, count = Counter(votes).most_common(1)[0]
    return label if count >= 2 else "unresolved"


def adverse_conservative(votes: list[str]) -> str:
    counts = Counter(votes)
    if counts["contradiction"] == 3:
        return "contradiction"
    if counts["entailment"] >= 2 and counts["contradiction"] == 0:
        return "entailment"
    if counts["neutral"] >= 2 and counts["contradiction"] == 0:
        return "neutral"
    return "unresolved"


def disagreement_metrics(rows: list[dict[str, Any]], model_names: list[str]) -> dict[str, Any]:
    unanimous = []
    disagreement = []
    polar = []
    correct_vote_present = 0
    for row in rows:
        votes = [row["model_outputs"][name]["predicted"] for name in model_names]
        if row["target"] in votes:
            correct_vote_present += 1
        if len(set(votes)) == 1:
            unanimous.append(row)
        else:
            disagreement.append(row)
        if "entailment" in votes and "contradiction" in votes:
            polar.append(row)

    def inc_error_rate(subset: list[dict[str, Any]]) -> float | None:
        if not subset:
            return None
        return sum(
            row["model_outputs"]["incumbent_base"]["predicted"] != row["target"]
            for row in subset
        ) / len(subset)

    d_rate = inc_error_rate(disagreement)
    u_rate = inc_error_rate(unanimous)
    relative_risk: float | None
    if d_rate is None or u_rate is None or u_rate == 0:
        relative_risk = None
    else:
        relative_risk = d_rate / u_rate

    return {
        "n": len(rows),
        "unanimous_cases": len(unanimous),
        "unanimous_incumbent_error_rate": u_rate,
        "disagreement_cases": len(disagreement),
        "disagreement_incumbent_error_rate": d_rate,
        "relative_risk_disagreement_vs_unanimity": relative_risk,
        "correct_label_present_in_votes": correct_vote_present,
        "polar_conflict_cases": len(polar),
        "polar_conflict_incumbent_error_rate": inc_error_rate(polar),
        "disagreement_case_ids": [row["case_id"] for row in disagreement],
        "unanimous_error_case_ids": [
            row["case_id"]
            for row in unanimous
            if row["model_outputs"]["incumbent_base"]["predicted"] != row["target"]
        ],
    }


def run(output_dir: Path) -> dict[str, Any]:
    cohort = build()
    problems = validate(cohort)
    if problems:
        raise RuntimeError("cohort validation failed: " + "; ".join(problems))
    cohort_raw = canonical_bytes(cohort)
    cohort_sha = hashlib.sha256(cohort_raw).hexdigest()
    if cohort_sha != EXPECTED_COHORT_SHA256:
        raise RuntimeError(f"cohort freeze mismatch: {cohort_sha}")

    torch.set_grad_enabled(False)
    torch.manual_seed(0)

    model_rows: dict[str, dict[str, dict[str, Any]]] = {}
    model_meta: dict[str, Any] = {}
    temperatures: dict[str, float] = {}
    calibration_reliability: dict[str, Any] = {}
    evaluation_reliability: dict[str, Any] = {}

    for name, model_id, revision in MODELS:
        tokenizer = AutoTokenizer.from_pretrained(model_id, revision=revision)
        model = AutoModelForSequenceClassification.from_pretrained(model_id, revision=revision)
        model.eval()
        order = label_order(model)

        scored: dict[str, dict[str, Any]] = {}
        for case in cohort["cases"]:
            scored[case["case_id"]] = score_case(
                model, tokenizer, order, case["premise"], case["hypothesis"]
            )

        # Determinism sentinels, before interpretation.
        for case in cohort["cases"][:3]:
            again = score_case(model, tokenizer, order, case["premise"], case["hypothesis"])
            first = scored[case["case_id"]]
            if again["predicted"] != first["predicted"]:
                raise RuntimeError(f"{name}: nondeterministic sentinel label")
            if any(
                abs(a - b) > 1e-6
                for a, b in zip(
                    again["canonical_logits"], first["canonical_logits"], strict=True
                )
            ):
                raise RuntimeError(f"{name}: nondeterministic sentinel logits")

        model_rows[name] = scored
        model_meta[name] = {
            "model_id": model_id,
            "revision": revision,
            "label_order_native": list(order),
        }

        calibration_cases = [c for c in cohort["cases"] if c["split"] == "calibration"]
        cal_logits = np.array(
            [scored[c["case_id"]]["canonical_logits"] for c in calibration_cases],
            dtype=np.float64,
        )
        cal_targets = np.array(
            [LABEL_TO_INDEX[c["target"]] for c in calibration_cases], dtype=np.int64
        )
        temp = fit_temperature(cal_logits, cal_targets)
        temperatures[name] = temp
        calibration_reliability[name] = {
            "temperature": temp,
            "native": reliability_metrics(cal_logits, cal_targets, 1.0),
            "calibrated": reliability_metrics(cal_logits, cal_targets, temp),
        }

        evaluation_cases = [c for c in cohort["cases"] if c["split"] == "evaluation"]
        eval_logits = np.array(
            [scored[c["case_id"]]["canonical_logits"] for c in evaluation_cases],
            dtype=np.float64,
        )
        eval_targets = np.array(
            [LABEL_TO_INDEX[c["target"]] for c in evaluation_cases], dtype=np.int64
        )
        native_probs = probabilities_from_logits(eval_logits, 1.0)
        calibrated_probs = probabilities_from_logits(eval_logits, temp)
        if not np.array_equal(native_probs.argmax(axis=1), calibrated_probs.argmax(axis=1)):
            raise RuntimeError(f"{name}: scalar temperature changed argmax labels")
        evaluation_reliability[name] = {
            "temperature": temp,
            "native": reliability_metrics(eval_logits, eval_targets, 1.0),
            "calibrated": reliability_metrics(eval_logits, eval_targets, temp),
        }

        del model
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    frozen_rows: list[dict[str, Any]] = []
    for case in cohort["cases"]:
        frozen_rows.append(
            {
                **case,
                "model_outputs": {
                    name: model_rows[name][case["case_id"]]
                    for name, _, _ in MODELS
                },
            }
        )

    eval_rows = [row for row in frozen_rows if row["split"] == "evaluation"]
    targets = [row["target"] for row in eval_rows]
    names = [name for name, _, _ in MODELS]

    s0 = [row["model_outputs"]["incumbent_base"]["predicted"] for row in eval_rows]
    s1 = [
        majority([row["model_outputs"][name]["predicted"] for name in names])
        for row in eval_rows
    ]
    s2 = [
        adverse_conservative(
            [row["model_outputs"][name]["predicted"] for name in names]
        )
        for row in eval_rows
    ]

    uncalibrated_mean_outputs: list[str] = []
    calibrated_mean_outputs: list[str] = []
    for row in eval_rows:
        native_vectors = []
        calibrated_vectors = []
        for name in names:
            logits = np.array(
                row["model_outputs"][name]["canonical_logits"], dtype=np.float64
            )
            native_vectors.append(softmax(logits))
            calibrated_vectors.append(softmax(logits / temperatures[name]))
        native_mean = np.mean(np.stack(native_vectors), axis=0)
        calibrated_mean = np.mean(np.stack(calibrated_vectors), axis=0)
        uncalibrated_mean_outputs.append(LABELS[int(np.argmax(native_mean))])
        calibrated_mean_outputs.append(LABELS[int(np.argmax(calibrated_mean))])

    systems = {
        "S0_incumbent": system_metrics(s0, targets),
        "S1_majority": system_metrics(s1, targets),
        "S2_adverse_conservative": system_metrics(s2, targets),
        "S3_uncalibrated_probability_mean": system_metrics(
            uncalibrated_mean_outputs, targets
        ),
        "S4_calibrated_probability_mean": system_metrics(
            calibrated_mean_outputs, targets
        ),
    }

    individual_eval = {}
    for name in names:
        outputs = [row["model_outputs"][name]["predicted"] for row in eval_rows]
        individual_eval[name] = system_metrics(outputs, targets)

    result = {
        "schema_version": "cal-independent-nli-calibration-rc2-result-v0.1",
        "cohort_sha256": "sha256:" + cohort_sha,
        "models": model_meta,
        "temperatures": temperatures,
        "calibration_reliability": calibration_reliability,
        "evaluation_reliability": evaluation_reliability,
        "individual_evaluation": individual_eval,
        "systems_evaluation": systems,
        "disagreement_evaluation": disagreement_metrics(eval_rows, names),
        "evaluation_rows": [
            {
                "case_id": row["case_id"],
                "family": row["family"],
                "target": row["target"],
                "votes": {
                    name: row["model_outputs"][name]["predicted"] for name in names
                },
                "S0_incumbent": s0[i],
                "S1_majority": s1[i],
                "S2_adverse_conservative": s2[i],
                "S3_uncalibrated_probability_mean": uncalibrated_mean_outputs[i],
                "S4_calibrated_probability_mean": calibrated_mean_outputs[i],
            }
            for i, row in enumerate(eval_rows)
        ],
        "score_normalization": "model-specific scalar temperature scaling on calibration split only",
        "learned_ensemble_weights": False,
        "evaluation_threshold_tuning": False,
        "production_behavior_changed": False,
        "runtime": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "torch": importlib.metadata.version("torch"),
            "transformers": importlib.metadata.version("transformers"),
            "scipy": importlib.metadata.version("scipy"),
            "sklearn": importlib.metadata.version("scikit-learn"),
            "device": "cpu",
        },
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "MEASUREMENTS.json").write_text(
        json.dumps(
            {
                "schema_version": "cal-independent-nli-calibration-rc2-measurements-v0.1",
                "cohort_sha256": "sha256:" + cohort_sha,
                "rows": frozen_rows,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )
    (output_dir / "RESULTS.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n"
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.output_dir)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
