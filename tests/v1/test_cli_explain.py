"""Contract for the ``claim-audit explain`` command.

The command exists to put CAL's abstention reasons on a surface a reviewer can
read. The properties under test are that it is *read-only* over recorded traces,
that it never renames the verdict it was given, and that it names an abstention
rather than emitting one undifferentiated ``not_checkable``.

These build their own traces so the suite stays green in a clean checkout — the
sealed corpora live outside version control. ``tests/v1/test_explanation.py``
carries the counts-reproduce-the-sealed-decomposition test, guarded on their
presence.
"""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from claim_audit_lab.cli import app

runner = CliRunner()


def _trace(
    claim_id: str,
    *,
    verdict: str,
    rule_id: str,
    reason: str,
    label: str,
    logits: tuple[float, float, float],
    score: float = 0.82,
) -> dict[str, object]:
    """A minimal recorded trace in the shape the v1 pipeline writes."""
    return {
        "claim_id": claim_id,
        "claim_text": f"Claim body for {claim_id}.",
        "retrieval": [{"passage_id": "doc#p1", "score": score}],
        "entailment": [
            {
                "passage_id": "doc#p1",
                "label": label,
                "score": max(_softmax(logits)),
                "raw_logits": list(logits),
            }
        ],
        "features": {
            "numerical_values": [],
            "has_explicit_negation": False,
            "has_universal_quantifier": False,
            "modal_strength": "asserts",
            "claim_token_count": 9,
            "compound_claim": False,
            "sentence_type": "declarative",
        },
        "support_signal": {
            "label": label,
            "max_entailment_score": max(_softmax(logits)),
            "contributing_passage_id": "doc#p1",
        },
        "rules_fired": [{"rule_id": rule_id, "reason": reason}],
        "verdict": {
            "support_verdict": verdict,
            "support_verdict_reason": None,
            "audit_flags": [],
            "citation_status": "not_applicable",
            "audit_confidence": "medium",
        },
        "audit_config_hash": "sha256:" + "0" * 64,
        "library_version": "0.3.0",
    }


def _softmax(logits: tuple[float, float, float]) -> list[float]:
    import math

    mx = max(logits)
    exps = [math.exp(x - mx) for x in logits]
    total = sum(exps)
    return [e / total for e in exps]


def _floor_miss_trace(claim_id: str) -> dict[str, object]:
    """A floor miss as the pipeline really records it.

    Verified against outputs/2026-08-02-qms-claim-generation/scaled-30 —
    retrieval candidates are recorded, ``entailment`` is empty because nothing
    cleared the floor, and no passage contributed.
    """
    trace = _trace(
        claim_id,
        verdict="not_checkable",
        rule_id="A2_retrieval_empty",
        reason="no passage cleared the retrieval floor",
        label="neutral",
        logits=(-2.0, 6.0, -2.0),
        score=0.39,
    )
    trace["entailment"] = []
    trace["support_signal"] = {
        "label": "neutral",
        "max_entailment_score": 0.0,
        "contributing_passage_id": None,
    }
    return trace


def _write_corpus(traces_dir: Path) -> None:
    """Three traces spanning a supported verdict and two distinct abstentions."""
    traces_dir.mkdir(parents=True, exist_ok=True)
    corpus = {
        "c001": _trace(
            "c001",
            verdict="supported",
            rule_id="B5_degree",
            reason="entail 0.99 >= supported_threshold=0.7",
            label="entail",
            logits=(6.0, 0.0, -2.0),
        ),
        "c002": _trace(
            "c002",
            verdict="not_checkable",
            rule_id="B5_degree",
            reason="neutral support signal — no entailment",
            label="neutral",
            logits=(-2.0, 6.0, -2.0),
        ),
        "c003": _floor_miss_trace("c003"),
    }
    for claim_id, payload in corpus.items():
        (traces_dir / f"{claim_id}.json").write_text(
            json.dumps(payload, indent=2), encoding="utf-8"
        )


def test_explain_writes_reports_and_names_abstentions(tmp_path: Path) -> None:
    traces_dir = tmp_path / "traces"
    out_dir = tmp_path / "explanations"
    _write_corpus(traces_dir)

    result = runner.invoke(app, ["explain", str(traces_dir), "--out-dir", str(out_dir)])

    assert result.exit_code == 0, result.output
    assert "Explained 3 traces" in result.output

    payload = json.loads((out_dir / "explanations.json").read_text())
    assert len(payload) == 3

    by_id = {entry["claim_id"]: entry for entry in payload}

    # A verdict is never renamed by its explanation.
    assert by_id["c001"]["verdict"] == "supported"
    assert by_id["c001"]["abstention_class"] is None

    # An abstention is named, and carries a reviewer next step.
    for claim_id in ("c002", "c003"):
        assert by_id[claim_id]["verdict"] == "not_checkable"
        assert by_id[claim_id]["abstention_class"] is not None
        assert by_id[claim_id]["next_step"]

    # The two abstentions are distinguished, not collapsed into one bucket.
    assert by_id["c002"]["abstention_class"] != by_id["c003"]["abstention_class"]
    assert by_id["c003"]["abstention_class"] == "no_evidence_admitted"

    report = (out_dir / "explanations.md").read_text()
    assert "## Why it abstained" in report
    assert "no_evidence_admitted" in report
    assert "No model was run and no verdict was re-decided." in report


def test_explain_leaves_input_traces_untouched(tmp_path: Path) -> None:
    """The command reads recorded traces; it must never write back to them."""
    traces_dir = tmp_path / "traces"
    _write_corpus(traces_dir)
    before = {p.name: p.read_bytes() for p in sorted(traces_dir.glob("*.json"))}

    result = runner.invoke(app, ["explain", str(traces_dir), "--out-dir", str(tmp_path / "out")])

    assert result.exit_code == 0, result.output
    after = {p.name: p.read_bytes() for p in sorted(traces_dir.glob("*.json"))}
    assert before == after


def test_explain_rejects_an_empty_directory(tmp_path: Path) -> None:
    empty = tmp_path / "empty"
    empty.mkdir()

    result = runner.invoke(app, ["explain", str(empty), "--out-dir", str(tmp_path / "out")])

    assert result.exit_code == 2
    assert "no trace JSON found" in result.output


def test_explain_reports_a_malformed_trace_by_name(tmp_path: Path) -> None:
    traces_dir = tmp_path / "traces"
    _write_corpus(traces_dir)
    (traces_dir / "broken.json").write_text('{"claim_id": "nope"}', encoding="utf-8")

    result = runner.invoke(app, ["explain", str(traces_dir), "--out-dir", str(tmp_path / "out")])

    assert result.exit_code == 2
    assert "broken.json" in result.output


# --------------------------------------------------------------------------
# source_boundary: the parameter that decides whether an absence is informative
# --------------------------------------------------------------------------


def test_boundary_note_flips_meaning_between_exhaustive_and_bounded(tmp_path: Path) -> None:
    """The same abstention reads as a miss or as correct, depending on the boundary."""
    traces_dir = tmp_path / "traces"
    _write_corpus(traces_dir)

    notes = {}
    for boundary in ("exhaustive", "bounded"):
        out = tmp_path / boundary
        result = runner.invoke(
            app,
            ["explain", str(traces_dir), "--out-dir", str(out), "--source-boundary", boundary],
        )
        assert result.exit_code == 0, result.output
        payload = json.loads((out / "explanations.json").read_text())
        by_id = {e["claim_id"]: e for e in payload}
        assert by_id["c003"]["source_boundary"] == boundary
        notes[boundary] = by_id["c003"]["boundary_note"]

    assert notes["exhaustive"] and notes["bounded"]
    assert notes["exhaustive"] != notes["bounded"]
    # Exhaustive: the silence is informative, so abstaining understates the evidence.
    assert "complete source" in notes["exhaustive"]
    # Bounded: abstaining is the right answer, not a miss.
    assert "correct answer" in notes["bounded"]


def test_undeclared_boundary_licenses_no_absence_reasoning(tmp_path: Path) -> None:
    """Undeclared must stay undeclared — a default here would reintroduce the ambiguity."""
    traces_dir = tmp_path / "traces"
    _write_corpus(traces_dir)

    result = runner.invoke(app, ["explain", str(traces_dir), "--out-dir", str(tmp_path / "o")])

    assert result.exit_code == 0, result.output
    assert "undeclared" in result.output
    payload = json.loads((tmp_path / "o" / "explanations.json").read_text())
    assert all(e["source_boundary"] is None for e in payload)
    assert all(e["boundary_note"] is None for e in payload)


def test_boundary_note_only_attaches_to_boundary_sensitive_abstentions(tmp_path: Path) -> None:
    """A supported verdict has no absence to reason about, whatever the boundary."""
    traces_dir = tmp_path / "traces"
    _write_corpus(traces_dir)

    result = runner.invoke(
        app,
        [
            "explain",
            str(traces_dir),
            "--out-dir",
            str(tmp_path / "o"),
            "--source-boundary",
            "exhaustive",
        ],
    )

    assert result.exit_code == 0, result.output
    by_id = {
        e["claim_id"]: e for e in json.loads((tmp_path / "o" / "explanations.json").read_text())
    }
    assert by_id["c001"]["verdict"] == "supported"
    assert by_id["c001"]["boundary_note"] is None
    assert by_id["c003"]["boundary_note"] is not None


def test_named_missing_material_defers_to_the_named_gaps(tmp_path: Path) -> None:
    traces_dir = tmp_path / "traces"
    _write_corpus(traces_dir)

    result = runner.invoke(
        app,
        [
            "explain",
            str(traces_dir),
            "--out-dir",
            str(tmp_path / "o"),
            "--source-boundary",
            "named_missing_material",
        ],
    )

    assert result.exit_code == 0, result.output
    by_id = {
        e["claim_id"]: e for e in json.loads((tmp_path / "o" / "explanations.json").read_text())
    }
    assert "named gaps" in by_id["c003"]["boundary_note"]


def test_explain_rejects_an_unknown_boundary(tmp_path: Path) -> None:
    traces_dir = tmp_path / "traces"
    _write_corpus(traces_dir)

    result = runner.invoke(
        app,
        [
            "explain",
            str(traces_dir),
            "--out-dir",
            str(tmp_path / "o"),
            "--source-boundary",
            "whatever",
        ],
    )

    assert result.exit_code == 2
    assert "must be one of" in result.output
