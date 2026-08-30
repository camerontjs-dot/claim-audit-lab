#!/usr/bin/env python3
"""Run the preregistered Cohort-A-derived NLI measurement discrimination RC0."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import platform
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from scripts import build_construction_gold as construction

PRIMARY_TARGETS = {
    "restates": "entailment",
    "weakens": "entailment",
    "contradicts": "contradiction",
    "overgeneralizes": "neutral",
}

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

EXPECTED_BUILDER_CASES = 33
EXPECTED_BUILDER_BLOB = "2c677ee29fd121cf1c76b1476664474aa09dc982"
FILLER_SENTENCES = (
    "The archive room stores blue binders beside a numbered shelving map.",
    "The reception desk records visitor badges at the start and end of each day.",
    "Parking permits are renewed by the facilities office at the end of the month.",
    "The cafeteria menu is posted near the north entrance before lunch service.",
    "Meeting rooms on the second floor use a separate reservation calendar.",
    "Courier packages are logged at the loading desk before internal delivery.",
    "The library catalog records book location, loan status, and return date.",
    "Office plants are inspected by facilities staff during the weekly walk-through.",
    "Printer supplies are stored in a cabinet beside the general administration area.",
    "The building directory lists departments alphabetically near the main elevator.",
)


def _canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _sha_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_canonical_bytes(value))


def _normalize_label(label: str) -> str:
    low = label.lower()
    for target in ("entailment", "neutral", "contradiction"):
        if target in low:
            return target
    raise ValueError(f"unrecognized NLI label: {label!r}")


def _label_order(model: Any) -> tuple[str, ...]:
    id2label = model.config.id2label
    order = tuple(_normalize_label(str(id2label[i])) for i in range(len(id2label)))
    if set(order) != {"entailment", "neutral", "contradiction"} or len(order) != 3:
        raise ValueError(f"model does not expose an unambiguous three-way NLI label map: {order}")
    return order


def _native_max_length(model: Any, tokenizer: Any) -> int:
    candidates: list[int] = []
    config_max = getattr(model.config, "max_position_embeddings", None)
    if isinstance(config_max, int) and 8 <= config_max <= 100_000:
        candidates.append(config_max)
    tok_max = getattr(tokenizer, "model_max_length", None)
    if isinstance(tok_max, int) and 8 <= tok_max <= 100_000:
        candidates.append(tok_max)
    if not candidates:
        raise ValueError("cannot establish a finite model/tokenizer context limit")
    return min(candidates)


@dataclass(frozen=True)
class InputCase:
    case_id: str
    claim: str
    target: str
    relation: str
    decisive_premise: str


def build_primary_cases() -> list[InputCase]:
    corpus = construction.build()
    problems = construction.validate(corpus)
    if problems:
        raise RuntimeError("construction corpus validation failed: " + "; ".join(problems[:5]))
    if corpus["n_cases"] != EXPECTED_BUILDER_CASES:
        raise RuntimeError(f"expected {EXPECTED_BUILDER_CASES} construction cases")

    selected: list[InputCase] = []
    for case in corpus["cases"]:
        relation = str(case["relation"])
        if relation not in PRIMARY_TARGETS:
            continue
        support_passages = [p for p in case["passages"] if p["role"] == "support"]
        if not support_passages:
            raise RuntimeError(f"{case['case_id']}: primary case has no support-role premise")
        premise = "\n\n".join(str(p["text"]) for p in support_passages)
        selected.append(
            InputCase(
                case_id=str(case["case_id"]),
                claim=str(case["claim_text"]),
                target=PRIMARY_TARGETS[relation],
                relation=relation,
                decisive_premise=premise,
            )
        )
    if not selected:
        raise RuntimeError("primary plain-NLI slice is empty")
    return selected


def _filler_block(repetitions: int) -> str:
    rows: list[str] = []
    for i in range(repetitions):
        sentence = FILLER_SENTENCES[i % len(FILLER_SENTENCES)]
        rows.append(f"Administrative note {i + 1}: {sentence}")
    return "\n".join(rows)


def freeze_inputs(tokenizer: Any) -> dict[str, Any]:
    """Freeze short/head/tail premises using only the incumbent tokenizer."""
    primary = build_primary_cases()
    frozen_cases: list[dict[str, Any]] = []

    for case in primary:
        filler_count = 1
        while True:
            filler = _filler_block(filler_count)
            tail = filler + "\n\nDECISIVE EVIDENCE:\n" + case.decisive_premise
            token_count = len(tokenizer(tail, case.claim, truncation=False)["input_ids"])
            if token_count > 700:
                break
            filler_count += 1
            if filler_count > 200:
                raise RuntimeError(f"{case.case_id}: failed to construct aperture stress input")
        if token_count >= 1100:
            raise RuntimeError(f"{case.case_id}: aperture stress grew beyond preregistered bound")

        head = case.decisive_premise + "\n\nIRRELEVANT APPENDIX:\n" + filler
        short = case.decisive_premise
        frozen_cases.append(
            {
                "case_id": case.case_id,
                "relation": case.relation,
                "target": case.target,
                "claim": case.claim,
                "premises": {
                    "short": short,
                    "stress_head": head,
                    "stress_tail": tail,
                },
                "incumbent_untruncated_tokens": {
                    name: len(tokenizer(premise, case.claim, truncation=False)["input_ids"])
                    for name, premise in (
                        ("short", short),
                        ("stress_head", head),
                        ("stress_tail", tail),
                    )
                },
                "filler_sentence_count": filler_count,
            }
        )

    diagnostic = construction.build()
    diagnostic_relations = sorted(
        {
            str(case["relation"])
            for case in diagnostic["cases"]
            if str(case["relation"]) not in PRIMARY_TARGETS
        }
    )
    return {
        "schema_version": "cal-nli-measurement-discrimination-input-v0.1",
        "builder_blob": EXPECTED_BUILDER_BLOB,
        "primary_target_map": PRIMARY_TARGETS,
        "excluded_diagnostic_relations": diagnostic_relations,
        "n_primary_cases": len(frozen_cases),
        "cases": frozen_cases,
    }


def _score_one(
    model: Any,
    tokenizer: Any,
    order: tuple[str, ...],
    claim: str,
    premise: str,
) -> dict[str, Any]:
    max_length = _native_max_length(model, tokenizer)
    raw_ids = tokenizer(premise, claim, truncation=False)["input_ids"]
    encoded = tokenizer(
        premise,
        claim,
        return_tensors="pt",
        truncation=True,
        max_length=max_length,
    )
    with torch.no_grad():
        logits = model(**encoded).logits[0]
    probs = torch.softmax(logits, dim=-1)
    predicted_index = int(torch.argmax(logits))
    return {
        "predicted": order[predicted_index],
        "raw_logits": [float(x) for x in logits],
        "probabilities": {order[i]: float(probs[i]) for i in range(3)},
        "native_max_length": max_length,
        "untruncated_tokens": len(raw_ids),
        "encoded_tokens": int(encoded["input_ids"].shape[1]),
        "truncated": len(raw_ids) > max_length,
    }


def _determinism_check(
    model: Any,
    tokenizer: Any,
    order: tuple[str, ...],
    inputs: dict[str, Any],
) -> dict[str, Any]:
    sentinels = inputs["cases"][: min(3, len(inputs["cases"]))]
    rows = []
    for case in sentinels:
        first = _score_one(model, tokenizer, order, case["claim"], case["premises"]["short"])
        second = _score_one(model, tokenizer, order, case["claim"], case["premises"]["short"])
        logits_equal = all(
            abs(a - b) <= 1e-6
            for a, b in zip(first["raw_logits"], second["raw_logits"], strict=True)
        )
        row = {
            "case_id": case["case_id"],
            "label_equal": first["predicted"] == second["predicted"],
            "logits_equal_atol_1e-6": logits_equal,
        }
        if not row["label_equal"] or not row["logits_equal_atol_1e-6"]:
            raise RuntimeError(f"determinism check failed: {row}")
        rows.append(row)
    return {"passed": True, "rows": rows}


def _summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    variants = ("short", "stress_head", "stress_tail")
    summary: dict[str, Any] = {}
    for variant in variants:
        vrows = [r for r in rows if r["variant"] == variant]
        correct = [r for r in vrows if r["predicted"] == r["target"]]
        by_target: dict[str, dict[str, int]] = {}
        for target in ("entailment", "neutral", "contradiction"):
            trows = [r for r in vrows if r["target"] == target]
            by_target[target] = {
                "n": len(trows),
                "correct": sum(r["predicted"] == target for r in trows),
            }
        summary[variant] = {
            "n": len(vrows),
            "correct": len(correct),
            "exact_relation_match": (len(correct) / len(vrows)) if vrows else None,
            "by_target": by_target,
            "neutral_to_contradiction_false_adverse": sum(
                r["target"] == "neutral" and r["predicted"] == "contradiction" for r in vrows
            ),
            "contradiction_to_neutral_loss": sum(
                r["target"] == "contradiction" and r["predicted"] == "neutral" for r in vrows
            ),
            "truncated_cases": sum(bool(r["truncated"]) for r in vrows),
        }

    by_case: dict[str, dict[str, dict[str, Any]]] = {}
    for row in rows:
        by_case.setdefault(row["case_id"], {})[row["variant"]] = row
    summary["short_to_stress"] = {
        "head_label_stability": sum(
            vals["short"]["predicted"] == vals["stress_head"]["predicted"]
            for vals in by_case.values()
        ),
        "tail_label_stability": sum(
            vals["short"]["predicted"] == vals["stress_tail"]["predicted"]
            for vals in by_case.values()
        ),
        "head_correctness_retained": sum(
            vals["short"]["predicted"] == vals["short"]["target"]
            and vals["stress_head"]["predicted"] == vals["stress_head"]["target"]
            for vals in by_case.values()
        ),
        "tail_correctness_retained": sum(
            vals["short"]["predicted"] == vals["short"]["target"]
            and vals["stress_tail"]["predicted"] == vals["stress_tail"]["target"]
            for vals in by_case.values()
        ),
        "n_cases": len(by_case),
    }
    return summary


def run(output_dir: Path) -> dict[str, Any]:
    torch.set_grad_enabled(False)
    torch.manual_seed(0)

    incumbent_name, incumbent_id, incumbent_revision = MODELS[0]
    incumbent_tokenizer = AutoTokenizer.from_pretrained(incumbent_id, revision=incumbent_revision)
    inputs = freeze_inputs(incumbent_tokenizer)
    input_bytes = _canonical_bytes(inputs)
    input_hash = _sha_bytes(input_bytes)
    _write_json(output_dir / "INPUTS.json", inputs)
    (output_dir / "INPUTS.sha256").write_text(input_hash + "\n", encoding="utf-8")

    results: dict[str, Any] = {}
    for name, model_id, revision in MODELS:
        tokenizer = AutoTokenizer.from_pretrained(model_id, revision=revision)
        model = AutoModelForSequenceClassification.from_pretrained(model_id, revision=revision)
        model.eval()
        order = _label_order(model)
        determinism = _determinism_check(model, tokenizer, order, inputs)

        rows: list[dict[str, Any]] = []
        for case in inputs["cases"]:
            for variant in ("short", "stress_head", "stress_tail"):
                scored = _score_one(
                    model,
                    tokenizer,
                    order,
                    str(case["claim"]),
                    str(case["premises"][variant]),
                )
                rows.append(
                    {
                        "case_id": case["case_id"],
                        "relation": case["relation"],
                        "target": case["target"],
                        "variant": variant,
                        **scored,
                    }
                )
        results[name] = {
            "model_id": model_id,
            "revision": revision,
            "label_order": list(order),
            "determinism": determinism,
            "summary": _summarize(rows),
            "rows": rows,
        }
        _write_json(output_dir / f"{name}.json", results[name])
        del model
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    # Cross-model discriminators are computed only after every model result is frozen.
    names = [m[0] for m in MODELS]
    case_lookup: dict[str, dict[str, dict[str, dict[str, Any]]]] = {}
    for name in names:
        for row in results[name]["rows"]:
            case_lookup.setdefault(row["case_id"], {}).setdefault(row["variant"], {})[name] = row

    long_only_tail_recoveries = []
    large_short_improvements = []
    large_short_regressions = []
    for case_id, variants in sorted(case_lookup.items()):
        short = variants["short"]
        tail = variants["stress_tail"]
        target = short["incumbent_base"]["target"]

        inc_short_ok = short["incumbent_base"]["predicted"] == target
        large_short_ok = short["same_family_large"]["predicted"] == target
        if large_short_ok and not inc_short_ok:
            large_short_improvements.append(case_id)
        if inc_short_ok and not large_short_ok:
            large_short_regressions.append(case_id)

        inc_tail_ok = tail["incumbent_base"]["predicted"] == target
        large_tail_ok = tail["same_family_large"]["predicted"] == target
        long_tail_ok = tail["long_context_base"]["predicted"] == target
        if long_tail_ok and not inc_tail_ok and not large_tail_ok:
            long_only_tail_recoveries.append(case_id)

    result = {
        "schema_version": "cal-nli-measurement-discrimination-result-v0.1",
        "input_sha256": input_hash,
        "models": {
            name: {
                "model_id": results[name]["model_id"],
                "revision": results[name]["revision"],
                "summary": results[name]["summary"],
            }
            for name in names
        },
        "cross_model": {
            "large_short_improvements_over_incumbent": large_short_improvements,
            "large_short_regressions_vs_incumbent": large_short_regressions,
            "long_only_stress_tail_recoveries": long_only_tail_recoveries,
        },
        "threshold_tuning_performed": False,
        "production_behavior_changed": False,
        "operator_owned_cases_used_for_ranking": False,
        "runtime": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "torch": importlib.metadata.version("torch"),
            "transformers": importlib.metadata.version("transformers"),
            "device": "cpu",
        },
    }
    _write_json(output_dir / "RESULTS.json", result)
    (output_dir / "RESULTS.sha256").write_text(
        _sha_bytes(_canonical_bytes(result)) + "\n", encoding="utf-8"
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
