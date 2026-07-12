"""Tests for the ``calibrate`` command and engine (Phase 4 Unit 1 / B17).

Split by cost: the metric/crosswalk/render/assembly logic is exercised with
hand-authored data and stub traces (no model loads) — that is the correctness
backbone and the coverage floor. A small number of real-inference tests confirm
the wired command runs clean over the synthetic packet, that its numbers match
the stub-derived ones, and that two runs are byte-identical.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError
from typer.testing import CliRunner

from claim_audit_lab.cli import app
from claim_audit_lab.v1.calibrate import (
    CalibrationGold,
    GoldClaim,
    _chance_corrected,
    _library_version,
    _recall_floor,
    _rule_fire_tallies,
    adverse_rate,
    cohens_kappa,
    cohens_kappa_ci,
    compute_calibration,
    confusion_matrix,
    crosswalk_gold,
    exact_agreement,
    gwet_ac2,
    load_gold,
    render_report,
    run_calibration,
    weighted_kappa,
)
from claim_audit_lab.v1.config import load_audit_config
from claim_audit_lab.v1.models import (
    AuditRequest,
    AuditTrace,
    ExtractedFeatures,
    RuleFired,
    SupportSignal,
    SupportVerdict,
    Verdict,
)
from tests.v1.testing.bundles import CALIBRATION_CASES, build_calibration_packet

FIXTURES = Path(__file__).parent / "fixtures" / "calibration-synthetic"
GOLD_PATH = FIXTURES / "gold.yaml"
CONFIG_PATH = FIXTURES / "audit-config.yaml"

# The committed inference goldens fix these real-model verdicts for the 12-claim
# packet (the five base contents reused under twelve claim_ids).
EXPECTED_VERDICTS: dict[str, SupportVerdict] = {
    "syn-01": "supported",
    "syn-02": "contradicted",
    "syn-03": "contradicted",
    "syn-04": "supported",
    "syn-05": "not_checkable",
    "syn-06": "not_checkable",
    "syn-07": "supported",
    "syn-08": "contradicted",
    "syn-09": "contradicted",
    "syn-10": "not_checkable",
    "syn-11": "supported",
    "syn-12": "contradicted",
}

# A small fixed hand-worked (gold, CAL) example for the pure-metric unit tests --
# independent of the packet. Cohen's kappa = 0.52/0.72 = 0.7222; on-scale n=3 with
# weighted-kappa ≈ 0.94915, Gwet AC2 ≈ 0.95263 (hand-validated).
HAND_PAIRS: list[tuple[SupportVerdict, SupportVerdict]] = [
    ("supported", "supported"),
    ("contradicted", "contradicted"),
    ("unsupported", "contradicted"),
    ("not_checkable", "not_checkable"),
    ("not_checkable", "not_checkable"),
]

runner = CliRunner()


def _trace(claim_id: str, verdict: SupportVerdict, flags: tuple[str, ...] = ()) -> AuditTrace:
    return AuditTrace(
        claim_id=claim_id,
        claim_text=f"claim {claim_id}",
        retrieval=[],
        entailment=[],
        features=ExtractedFeatures(),
        support_signal=SupportSignal(label="entail", max_entailment_score=0.9),
        rules_fired=[],
        verdict=Verdict(support_verdict=verdict, audit_flags=list(flags)),  # type: ignore[arg-type]
        audit_config_hash="sha256:" + "a" * 64,
        library_version="test",
    )


def _stub_traces() -> dict[str, AuditTrace]:
    return {cid: _trace(cid, verdict) for cid, verdict in EXPECTED_VERDICTS.items()}


# --- Metric units ----------------------------------------------------------------


def test_exact_agreement_counts_diagonal() -> None:
    assert exact_agreement(HAND_PAIRS) == (4, 5)
    assert exact_agreement([]) == (0, 0)


def test_cohens_kappa_matches_hand_value() -> None:
    # po=0.8, pe=0.28 -> (0.8-0.28)/(1-0.28)
    assert cohens_kappa(HAND_PAIRS) == pytest.approx(0.52 / 0.72)


def test_cohens_kappa_edges() -> None:
    assert cohens_kappa([]) == 0.0
    perfect: list[tuple[SupportVerdict, SupportVerdict]] = [("supported", "supported")] * 3
    assert cohens_kappa(perfect) == 1.0


def test_cohens_kappa_ci_brackets_kappa() -> None:
    low, high = cohens_kappa_ci(HAND_PAIRS)
    assert low <= cohens_kappa(HAND_PAIRS) <= high
    assert -1.0 <= low and high <= 1.0
    # degenerate: empty and single-category both collapse to a point interval.
    assert cohens_kappa_ci([]) == (0.0, 0.0)
    perfect: list[tuple[SupportVerdict, SupportVerdict]] = [("supported", "supported")] * 2
    assert cohens_kappa_ci(perfect) == (1.0, 1.0)


def test_weighted_kappa_and_ac2_match_hand_values() -> None:
    wk, on_scale_n = weighted_kappa(HAND_PAIRS)
    ac2, on_scale_n2 = gwet_ac2(HAND_PAIRS)
    assert on_scale_n == 3 and on_scale_n2 == 3
    assert wk == pytest.approx(0.94915, abs=1e-3)
    assert ac2 == pytest.approx(0.95263, abs=1e-3)


def test_weighted_metrics_empty_on_scale() -> None:
    off: list[tuple[SupportVerdict, SupportVerdict]] = [("not_checkable", "not_checkable")]
    assert weighted_kappa(off) == (0.0, 0)
    assert gwet_ac2(off) == (0.0, 0)


def test_chance_corrected_degenerate_branches() -> None:
    assert _chance_corrected(0.5, 0.4, 0) == 0.0  # n == 0
    assert _chance_corrected(1.0, 1.0, 4) == 1.0  # pe == 1, perfect
    assert _chance_corrected(0.5, 1.0, 4) == 0.0  # pe == 1, imperfect


def test_confusion_matrix_cells() -> None:
    matrix = confusion_matrix(HAND_PAIRS)
    assert matrix["supported"]["supported"] == 1
    assert matrix["unsupported"]["contradicted"] == 1
    assert matrix["contradicted"]["contradicted"] == 1
    assert matrix["not_checkable"]["not_checkable"] == 2
    assert matrix["partially_supported"]["supported"] == 0


def test_adverse_rate_excludes_not_checkable() -> None:
    labels: list[SupportVerdict] = ["supported", "contradicted", "unsupported", "not_checkable"]
    assert adverse_rate(labels) == (2, 3)


# --- Crosswalk -------------------------------------------------------------------


def test_crosswalk_reasonable_inference_becomes_supported_inferred() -> None:
    verdict = crosswalk_gold("reasonable_inference", [])
    assert verdict.support_verdict == "supported"
    assert verdict.audit_flags == ["inferred"]


def test_crosswalk_overconfident_becomes_overstated() -> None:
    verdict = crosswalk_gold("supported", ["overconfident"])
    assert verdict.support_verdict == "supported"
    assert verdict.audit_flags == ["overstated"]


def test_crosswalk_missing_needed_becomes_citation_status() -> None:
    verdict = crosswalk_gold("not_checkable", ["missing_needed"])
    assert verdict.citation_status == "missing_needed"
    assert verdict.audit_flags == []


def test_crosswalk_passthrough_flags_and_identity() -> None:
    verdict = crosswalk_gold("partially_supported", ["source_scope_error", "false_caution"])
    assert verdict.support_verdict == "partially_supported"
    assert verdict.audit_flags == ["source_scope_error", "false_caution"]


# --- Gold loader -----------------------------------------------------------------


def test_load_gold_reads_committed_fixture() -> None:
    gold = load_gold(GOLD_PATH)
    assert isinstance(gold, CalibrationGold)
    assert [c.claim_id for c in gold.claims] == [f"syn-{i:02d}" for i in range(1, 13)]
    assert gold.starved_claim_ids == ["syn-01", "syn-04", "syn-09"]


def test_load_gold_rejects_bad_verdict(tmp_path: Path) -> None:
    bad = tmp_path / "gold.yaml"
    bad.write_text(
        "gold_version: x\nclaims:\n  - claim_id: a\n    condition: c\n"
        "    model: m\n    gold_verdict: bogus\n",
        encoding="utf-8",
    )
    with pytest.raises(ValidationError):
        load_gold(bad)


def test_gold_claim_forbids_extra_fields() -> None:
    with pytest.raises(ValidationError):
        GoldClaim.model_validate(
            {"claim_id": "a", "condition": "c", "model": "m", "gold_verdict": "supported", "x": 1}
        )


def test_load_gold_rejects_malformed_yaml(tmp_path: Path) -> None:
    bad = tmp_path / "gold.yaml"
    bad.write_text("gold_version: x\nclaims: [unclosed\n", encoding="utf-8")
    with pytest.raises(ValueError, match="malformed gold YAML"):
        load_gold(bad)


def test_load_audit_config_rejects_malformed_and_non_mapping(tmp_path: Path) -> None:
    malformed = tmp_path / "cfg.yaml"
    malformed.write_text("top_k: [1, 2\n", encoding="utf-8")
    with pytest.raises(ValueError, match="malformed audit_config YAML"):
        load_audit_config(malformed)

    non_mapping = tmp_path / "cfg2.yaml"
    non_mapping.write_text("- a\n- b\n", encoding="utf-8")
    with pytest.raises(ValueError, match="must be a mapping"):
        load_audit_config(non_mapping)


# --- Assembly (stub traces, no models) -------------------------------------------


def test_compute_calibration_matches_hand_values() -> None:
    gold = load_gold(GOLD_PATH)
    config = load_audit_config(CONFIG_PATH)
    result = compute_calibration(_stub_traces(), gold, config)

    assert result.n_claims == 12
    assert result.agreement.n_agree == 10
    assert result.agreement.cohens_kappa == pytest.approx(13 / 17)
    assert result.agreement.on_scale_n == 9
    # Prevalence-robust ordinal metrics over the 9-pair on-scale subset (locked to
    # the engine's output; the single U->C miss is ordinally adjacent so both stay high).
    assert result.agreement.weighted_kappa == pytest.approx(0.9854, abs=1e-4)
    assert result.agreement.gwet_ac2 == pytest.approx(0.9860, abs=1e-4)
    assert result.recall_floor.starved_total == 3
    assert result.recall_floor.supported == 2
    assert result.recall_floor.adverse == 1
    assert result.confusion["unsupported"]["contradicted"] == 1
    assert result.confusion["partially_supported"]["not_checkable"] == 1
    assert result.confusion["not_checkable"]["not_checkable"] == 2

    flags = {t.flag: t for t in result.flags}
    assert (flags["overstated"].gold_count, flags["overstated"].cal_count) == (1, 0)
    assert (flags["inferred"].gold_count, flags["source_scope_error"].gold_count) == (1, 1)

    conditions = {row.group: row for row in result.per_condition}
    assert [row.group for row in result.per_condition] == ["cond-A", "cond-B", "cond-C", "cond-D"]
    assert (conditions["cond-A"].cal_adverse, conditions["cond-A"].cal_checkable) == (2, 3)
    assert (conditions["cond-B"].cal_adverse, conditions["cond-B"].cal_checkable) == (0, 1)
    assert (conditions["cond-D"].cal_adverse, conditions["cond-D"].cal_checkable) == (1, 2)
    assert (conditions["cond-D"].gold_adverse, conditions["cond-D"].gold_checkable) == (1, 3)

    models = {row.group: row for row in result.per_model}
    assert [row.group for row in result.per_model] == ["model-x", "model-y"]
    assert (models["model-x"].cal_adverse, models["model-x"].cal_checkable) == (2, 5)
    assert (models["model-y"].cal_adverse, models["model-y"].cal_checkable) == (3, 4)
    assert (models["model-y"].gold_adverse, models["model-y"].gold_checkable) == (3, 5)


def test_compute_calibration_rejects_misaligned_gold() -> None:
    config = load_audit_config(CONFIG_PATH)
    gold = CalibrationGold(
        gold_version="x",
        claims=[GoldClaim(claim_id="ghost", condition="c", model="m", gold_verdict="supported")],
    )
    with pytest.raises(ValueError, match="gold claims absent from packet"):
        compute_calibration({"syn-01": _trace("syn-01", "supported")}, gold, config)


def test_compute_calibration_rejects_extra_audited_claim() -> None:
    config = load_audit_config(CONFIG_PATH)
    gold = CalibrationGold(
        gold_version="x",
        claims=[GoldClaim(claim_id="syn-01", condition="c", model="m", gold_verdict="supported")],
    )
    traces = {"syn-01": _trace("syn-01", "supported"), "extra": _trace("extra", "supported")}
    with pytest.raises(ValueError, match="audited claims absent from gold"):
        compute_calibration(traces, gold, config)


def test_compute_calibration_rejects_unknown_starved_id() -> None:
    config = load_audit_config(CONFIG_PATH)
    gold = CalibrationGold(
        gold_version="x",
        starved_claim_ids=["nope"],
        claims=[GoldClaim(claim_id="syn-01", condition="c", model="m", gold_verdict="supported")],
    )
    with pytest.raises(ValueError, match="starved_claim_ids not in gold"):
        compute_calibration({"syn-01": _trace("syn-01", "supported")}, gold, config)


def test_library_version_helper() -> None:
    assert _library_version({"a": _trace("a", "supported")}) == "test"
    assert _library_version({})  # falls back to installed package metadata
    mixed = {
        "a": _trace("a", "supported"),
        "b": _trace("a", "supported").model_copy(update={"library_version": "other"}),
    }
    with pytest.raises(ValueError, match="inconsistent library_version"):
        _library_version(mixed)


# --- run_calibration over the real packet, stub auditor (no models) --------------


def test_recall_floor_buckets_every_outcome() -> None:
    cal = {
        "a": Verdict(support_verdict="supported"),
        "b": Verdict(support_verdict="partially_supported"),
        "c": Verdict(support_verdict="unsupported"),
        "d": Verdict(support_verdict="not_checkable"),
    }
    floor = _recall_floor(["a", "b", "c", "d"], cal)
    assert floor.starved_total == 4
    bucket = (floor.supported, floor.partially_supported, floor.adverse, floor.not_checkable)
    assert bucket == (1, 1, 1, 1)


def _stub_auditor() -> Callable[[AuditRequest], AuditTrace]:
    def audit(request: AuditRequest) -> AuditTrace:
        return _trace(request.claim_id, EXPECTED_VERDICTS[request.claim_id])

    return audit


def test_run_calibration_loads_packet_and_scores(tmp_path: Path) -> None:
    packet = build_calibration_packet(tmp_path / "packet")
    result, traces = run_calibration(
        packet,
        load_gold(GOLD_PATH),
        load_audit_config(CONFIG_PATH),
        auditor=_stub_auditor(),
        deviations_dir=tmp_path / "dev",
    )
    assert set(traces) == set(EXPECTED_VERDICTS)
    assert result.agreement.n_agree == 10


def test_run_calibration_rejects_duplicate_claim_id(tmp_path: Path) -> None:
    from shutil import copytree

    packet = build_calibration_packet(tmp_path / "packet")
    copytree(packet / "bundle-syn-01", packet / "bundle-dup")  # same claim_id, new dir
    with pytest.raises(ValueError, match="duplicate claim_id"):
        run_calibration(
            packet,
            load_gold(GOLD_PATH),
            load_audit_config(CONFIG_PATH),
            auditor=_stub_auditor(),
            deviations_dir=tmp_path / "dev",
        )


# --- Report rendering ------------------------------------------------------------


def test_render_report_fixed_section_order() -> None:
    gold = load_gold(GOLD_PATH)
    config = load_audit_config(CONFIG_PATH)
    result = compute_calibration(_stub_traces(), gold, config)
    report = render_report(result, pinned_at="2026-06-22T00:00:00Z")

    expected_headers = [
        "# CAL v1 Calibration Report",
        "## 1. Recall floor on starved claims",
        "## 2. Agreement and reliability",
        "## 3. Support-verdict confusion (gold rows x CAL columns)",
        "## 4. Flags axis (gold vs CAL counts)",
        "## 5. Per-condition adverse rate",
        "## 6. Per-model adverse rate",
        "## 7. Rule fire rates",
        "## Trace metadata",
    ]
    positions = [report.index(header) for header in expected_headers]
    assert positions == sorted(positions)
    assert "Generated: 2026-06-22T00:00:00Z" in report
    assert "Cohen's kappa: 0.7647" in report


def test_rule_fire_rates_tally_once_per_claim_and_render() -> None:
    # Two claims fire B5; one also fires C6b twice (tallied once per claim).
    fired_twice = _trace("a", "supported").model_copy(
        update={
            "rules_fired": [
                RuleFired(rule_id="B5_degree", reason="x"),
                RuleFired(rule_id="C6b_strength_scope", reason="y"),
                RuleFired(rule_id="C6b_strength_scope", reason="z"),
            ]
        }
    )
    fired_once = _trace("b", "supported").model_copy(
        update={"rules_fired": [RuleFired(rule_id="B5_degree", reason="x")]}
    )
    tallies = _rule_fire_tallies({"a": fired_twice, "b": fired_once})
    assert [(t.rule_id, t.fired) for t in tallies] == [
        ("B5_degree", 2),
        ("C6b_strength_scope", 1),
    ]

    gold = load_gold(GOLD_PATH)
    config = load_audit_config(CONFIG_PATH)
    traces = _stub_traces()
    traces["syn-01"] = traces["syn-01"].model_copy(
        update={"rules_fired": [RuleFired(rule_id="B5_degree", reason="x")]}
    )
    result = compute_calibration(traces, gold, config)
    report = render_report(result, pinned_at="2026-01-01T00:00:00Z")
    assert "| B5_degree | 1/12 (8.3%) |" in report


def test_render_report_timestamp_is_pinned_not_wall_clock() -> None:
    gold = load_gold(GOLD_PATH)
    config = load_audit_config(CONFIG_PATH)
    result = compute_calibration(_stub_traces(), gold, config)
    first = render_report(result, pinned_at="2026-01-01T00:00:00Z")
    second = render_report(result, pinned_at="2099-12-31T23:59:59Z")
    # Reports differ only by the pinned timestamp line.
    assert first != second
    assert first.replace("2026-01-01T00:00:00Z", "X") == second.replace("2099-12-31T23:59:59Z", "X")


# --- CLI / real-inference -------------------------------------------------------


@pytest.fixture(scope="module")
def real_packet(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return build_calibration_packet(tmp_path_factory.mktemp("packet"))


def _invoke(packet: Path, out: Path, traces_out: Path) -> object:
    return runner.invoke(
        app,
        [
            "calibrate",
            "--packet",
            str(packet),
            "--gold",
            str(GOLD_PATH),
            "--config",
            str(CONFIG_PATH),
            "--out",
            str(out),
            "--traces-out",
            str(traces_out),
            "--pinned-at",
            "2026-06-22T00:00:00Z",
        ],
    )


def test_calibrate_cli_writes_report_and_traces(real_packet: Path, tmp_path: Path) -> None:
    out = tmp_path / "report.md"
    traces_out = tmp_path / "traces"
    result = _invoke(real_packet, out, traces_out)

    assert result.exit_code == 0, result.output
    assert "Cohen's kappa: 0.7647" in out.read_text(encoding="utf-8")
    for claim_id, verdict in EXPECTED_VERDICTS.items():
        trace_path = traces_out / f"{claim_id}.json"
        assert trace_path.is_file()
        trace = AuditTrace.model_validate_json(trace_path.read_text(encoding="utf-8"))
        assert trace.verdict.support_verdict == verdict, claim_id


def test_calibrate_cli_is_byte_identical_across_runs(real_packet: Path, tmp_path: Path) -> None:
    first_out, second_out = tmp_path / "a.md", tmp_path / "b.md"
    first_traces, second_traces = tmp_path / "ta", tmp_path / "tb"
    assert _invoke(real_packet, first_out, first_traces).exit_code == 0  # type: ignore[attr-defined]
    assert _invoke(real_packet, second_out, second_traces).exit_code == 0  # type: ignore[attr-defined]

    assert first_out.read_bytes() == second_out.read_bytes()
    for claim_id in EXPECTED_VERDICTS:
        a = (first_traces / f"{claim_id}.json").read_bytes()
        b = (second_traces / f"{claim_id}.json").read_bytes()
        assert a == b, claim_id


def test_calibrate_cli_rejects_bad_gold(tmp_path: Path) -> None:
    bad_gold = tmp_path / "gold.yaml"
    bad_gold.write_text(yaml.safe_dump({"gold_version": "x", "claims": "nope"}), encoding="utf-8")
    result = runner.invoke(
        app,
        [
            "calibrate",
            "--packet",
            str(tmp_path),
            "--gold",
            str(bad_gold),
            "--config",
            str(CONFIG_PATH),
            "--out",
            str(tmp_path / "r.md"),
            "--traces-out",
            str(tmp_path / "t"),
            "--pinned-at",
            "2026-06-22T00:00:00Z",
        ],
    )
    assert result.exit_code == 2
    assert "invalid --config or --gold" in result.output


def test_calibrate_cli_rejects_corrupt_packet(real_packet: Path, tmp_path: Path) -> None:
    from shutil import copytree

    packet = tmp_path / "packet"
    copytree(real_packet, packet)
    # Tamper a passage file's bytes so its SHA256SUMS entry no longer matches.
    passage = packet / "bundle-syn-01" / "evidence" / "src-001" / "passages" / "pass-001.yaml"
    passage.write_text(passage.read_text(encoding="utf-8") + "# tampered\n", encoding="utf-8")
    result = _invoke(packet, tmp_path / "r.md", tmp_path / "t")
    assert result.exit_code == 1  # type: ignore[attr-defined]
    assert "packet audit failed" in result.output  # type: ignore[attr-defined]


def test_calibration_cases_cover_the_verdict_spread() -> None:
    assert {case.claim_id for case in CALIBRATION_CASES} == set(EXPECTED_VERDICTS)
