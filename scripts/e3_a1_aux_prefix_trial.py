"""Test the preregistered ``aux`` extension to the E3 A1 parser guard."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from claim_audit_lab.v1 import features
from claim_audit_lab.v1.models import SentenceType

try:
    from scripts import e3_a1_negative_prefix_trial as prior
    from scripts.simple_logic_gold_structured_lane import _write_absent_or_identical
except ModuleNotFoundError as exc:
    if exc.name != "scripts":
        raise
    import e3_a1_negative_prefix_trial as prior  # type: ignore[no-redef]
    from simple_logic_gold_structured_lane import (  # type: ignore[no-redef]
        _write_absent_or_identical,
    )

_PRIOR_SUITE_SHA256 = "a5da53cd31dc19fa738827fe8867051b3074a346956e9eaee26451fefbf31951"
_PRIOR_SUMMARY_SHA256 = "da0f9c0fcff070687f3a50b4cfa520f91b8837877d34817c49f8811a3721319e"
_ALLOWED_IMPERATIVE_PREFIX_DEPS = frozenset({"intj", "advmod", "neg", "aux"})
_SUBJECT_DEPS = frozenset({"nsubj", "nsubjpass", "expl"})
_VERBAL_POS = frozenset({"VERB", "AUX"})
_CANARIES: tuple[tuple[str, SentenceType], ...] = (
    (
        "The guidance links annual reviews to statistical process control and trend analysis.",
        "declarative",
    ),
    (
        "Change control systems must document impacts and involve the quality unit.",
        "declarative",
    ),
    ("Valve V1 passed inspection.", "declarative"),
    ("Valve V2 passed inspection.", "declarative"),
    ("Valve V3 passed inspection.", "declarative"),
    ("Validate the system before release.", "imperative"),
    ("Please validate the system before release.", "imperative"),
    ("Kindly validate the system before release.", "imperative"),
    ("Never release the batch.", "imperative"),
    ("Do not release the batch.", "imperative"),
    ("Not all valves passed inspection.", "declarative"),
    ("No release occurred.", "declarative"),
    ("The batch was not released.", "declarative"),
    ("Do release the batch.", "imperative"),
    ("Please do not release the batch.", "imperative"),
    ("The system does not release the batch.", "declarative"),
    ("Can users release the batch?", "question"),
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def candidate_sentence_type(claim: str) -> SentenceType:
    """Apply the fixed ``aux`` prefix set plus the secondary-subject guard."""
    current = features.sentence_type(claim)
    if current != "imperative":
        return current
    doc = features._parse(claim)
    root = next(token for token in doc if token.dep_ == "ROOT")
    prefix = [token for token in doc[: root.i] if not token.is_space and not token.is_punct]
    if not all(token.dep_ in _ALLOWED_IMPERATIVE_PREFIX_DEPS for token in prefix):
        return "declarative"
    if any(
        token is not root
        and token.pos_ in _VERBAL_POS
        and any(child.dep_ in _SUBJECT_DEPS for child in token.children)
        for token in doc
    ):
        return "declarative"
    return "imperative"


def canary_report() -> dict[str, Any]:
    """Return the complete fixed 17-canary receipt."""
    records: list[dict[str, Any]] = []
    for claim, expected in _CANARIES:
        doc = features._parse(claim)
        observed = candidate_sentence_type(claim)
        records.append(
            {
                "claim": claim,
                "expected": expected,
                "current": features.sentence_type(claim),
                "candidate": observed,
                "match": observed == expected,
                "parse": [
                    {
                        "text": token.text,
                        "pos": token.pos_,
                        "dep": token.dep_,
                        "head": token.head.text,
                    }
                    for token in doc
                ],
            }
        )
    failures = [
        {
            "claim": record["claim"],
            "expected": record["expected"],
            "observed": record["candidate"],
        }
        for record in records
        if not record["match"]
    ]
    return {
        "denominator": len(records),
        "matching": len(records) - len(failures),
        "failures": failures,
        "records": records,
    }


def _candidate_suite_bytes(suite: dict[str, Any]) -> bytes:
    return (json.dumps(suite, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def build_trial_payload(project_root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    """Run the aux candidate through the immutable prior replay machinery."""
    prior_dir = project_root / "outputs/2026-07-15-e3-a1-negative-prefix-guard"
    prior_suite_path = prior_dir / "e3-candidate-suite.json"
    prior_summary_path = prior_dir / "trial-summary.json"
    if _sha256(prior_suite_path) != _PRIOR_SUITE_SHA256:
        raise ValueError("prior candidate-suite raw SHA-256 drift")
    if _sha256(prior_summary_path) != _PRIOR_SUMMARY_SHA256:
        raise ValueError("prior trial-summary raw SHA-256 drift")
    prior_summary = json.loads(prior_summary_path.read_text(encoding="utf-8"))

    original_candidate = prior.candidate_sentence_type
    prior.candidate_sentence_type = candidate_sentence_type
    try:
        replay_summary, candidate_suite = prior.build_trial_payload(project_root)
    finally:
        prior.candidate_sentence_type = original_candidate

    candidate_suite_sha = hashlib.sha256(_candidate_suite_bytes(candidate_suite)).hexdigest()
    canaries = canary_report()
    e3_identical = candidate_suite_sha == _PRIOR_SUITE_SHA256
    pilot_identical = replay_summary["pilot_001_dev"] == prior_summary["pilot_001_dev"]
    criteria = {
        "canaries": not canaries["failures"],
        "e3_candidate_byte_identity": e3_identical,
        "pilot_dev_replay_identity": pilot_identical,
        "e3_replay": replay_summary["criteria"]["e3_replay"],
        "pilot_dev_replay": replay_summary["criteria"]["pilot_dev_replay"],
    }
    summary = {
        **replay_summary,
        "schema_version": "e3-a1-aux-prefix-trial-v0.1",
        "label": "DEV craft trial only; not validation, gate evidence, or landing authority",
        "candidate_rule": {
            "allowed_pre_root_dependencies": sorted(_ALLOWED_IMPERATIVE_PREFIX_DEPS),
            "secondary_subject_dependencies": sorted(_SUBJECT_DEPS),
            "secondary_verbal_pos": sorted(_VERBAL_POS),
        },
        "canaries": canaries,
        "prior_candidate_suite_sha256": _PRIOR_SUITE_SHA256,
        "candidate_suite_sha256": candidate_suite_sha,
        "criteria": criteria,
        "all_criteria_pass": all(criteria.values()),
        "recommended_verdict": "keep" if all(criteria.values()) else "iterate",
        "next_hypothesis": None,
    }
    return summary, candidate_suite


def run_trial(project_root: Path, output_dir: Path) -> dict[str, Any]:
    """Execute the recorded replay and write absent-or-identical artifacts."""
    summary, candidate_suite = build_trial_payload(project_root)
    _write_absent_or_identical(output_dir / "trial-summary.json", summary)
    _write_absent_or_identical(output_dir / "e3-candidate-suite.json", candidate_suite)
    return summary


def main() -> None:
    workbench = Path(__file__).resolve().parents[1]
    project_root = workbench.parent
    output_dir = project_root / "outputs/2026-07-15-e3-a1-aux-prefix-guard"
    summary = run_trial(project_root, output_dir)
    print(
        json.dumps(
            {
                "criteria": summary["criteria"],
                "recommended_verdict": summary["recommended_verdict"],
            },
            separators=(",", ":"),
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
