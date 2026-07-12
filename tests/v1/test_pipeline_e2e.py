"""End-to-end CAL v1 pipeline tests (Phase 1 Unit 3 / B9).

Drives the production :func:`claim_audit_lab.v1.pipeline.run_audit` orchestrator
with the *real* ``DefaultFeatureExtractor`` + ``MaxEntailmentAggregator`` +
``VerdictRules`` and the test-only ``StubRetriever`` / ``StubEntailer``, over
synthetic fixtures that reach every Phase A gate, every Phase B degree exit, and
every Phase C adjustment — plus the composition rule (a claim that trips both
``6a -> contradicted`` and a ``6b`` overreach must stay ``contradicted``) and all
three ``not_checkable`` reasons.

Two properties are asserted: the expected verdict + flags + fired rules per
fixture, and **byte-identical** ``AuditTrace`` JSON across two runs and against a
committed golden under ``fixtures/traces/`` (the trace-reproducibility property).
Regenerate the goldens with ``CAL_WRITE_GOLDENS=1 .venv/bin/python -m pytest
tests/v1/test_pipeline_e2e.py``.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import pytest

from claim_audit_lab.v1.config import load_default_audit_config
from claim_audit_lab.v1.impl.aggregator import MaxEntailmentAggregator
from claim_audit_lab.v1.impl.features import DefaultFeatureExtractor
from claim_audit_lab.v1.impl.rules import VerdictRules
from claim_audit_lab.v1.models import (
    AuditFlag,
    AuditRequest,
    AuditTrace,
    EntailLabel,
    Passage,
    SupportVerdict,
    VerdictReason,
)
from claim_audit_lab.v1.pipeline import run_audit
from v1.testing import EntailSpec, StubEntailer, StubRetriever

_CONFIG = load_default_audit_config()
_TRACES_DIR = Path(__file__).parent / "fixtures" / "traces"

# Deterministic per-label logits — recorded in the trace, never read by the rules.
_LOGITS: dict[EntailLabel, tuple[float, float, float]] = {
    "entail": (2.0, -1.0, -1.0),
    "neutral": (0.0, 0.0, 0.0),
    "contradict": (-1.0, -1.0, 2.0),
}

# The shared "ordinary declarative" claim used by the gate / degree fixtures.
_CLAIM = "The platform validates submitted input records."


def _spec(label: EntailLabel, score: float) -> EntailSpec:
    return (label, score, _LOGITS[label])


def _p(text: str, *, pid: str = "p-1", trust: str | None = None) -> Passage:
    return Passage(
        passage_id=pid,
        text=text,
        source_meta={"trust_level": trust} if trust is not None else {},
    )


@dataclass(frozen=True)
class Case:
    """One end-to-end fixture: inputs + expected verdict, flags, and fired rules."""

    name: str
    claim_id: str
    claim: str
    passages: list[Passage]
    retrieval_scores: dict[str, float]
    entail: dict[str, EntailSpec]
    verdict: SupportVerdict
    reason: VerdictReason | None
    flags: list[AuditFlag]
    rule_ids: set[str]


CASES: list[Case] = [
    # --- Phase B degrees (verbatim passage, no Phase C noise) ---------------
    Case(
        name="01-supported-verbatim",
        claim_id="e2e-01",
        claim=_CLAIM,
        passages=[_p(_CLAIM)],
        retrieval_scores={"p-1": 0.90},
        entail={"p-1": _spec("entail", 0.95)},
        verdict="supported",
        reason=None,
        flags=[],
        rule_ids={"B5_degree"},
    ),
    Case(
        name="02-supported-inferred",
        claim_id="e2e-02",
        claim="The platform retains audit logs securely.",
        passages=[_p("The system stores activity records with strong encryption.")],
        retrieval_scores={"p-1": 0.90},
        entail={"p-1": _spec("entail", 0.90)},
        verdict="supported",
        reason=None,
        flags=["inferred"],
        rule_ids={"B5_degree", "C6c_inferred"},
    ),
    Case(
        name="03-partially-supported",
        claim_id="e2e-03",
        claim=_CLAIM,
        passages=[_p(_CLAIM)],
        retrieval_scores={"p-1": 0.90},
        entail={"p-1": _spec("entail", 0.55)},
        verdict="partially_supported",
        reason=None,
        flags=[],
        rule_ids={"B5_degree"},
    ),
    Case(
        name="04-unsupported",
        claim_id="e2e-04",
        claim=_CLAIM,
        passages=[_p(_CLAIM)],
        retrieval_scores={"p-1": 0.90},
        entail={"p-1": _spec("contradict", 0.50)},
        verdict="unsupported",
        reason=None,
        flags=[],
        rule_ids={"B5_degree"},
    ),
    # --- Phase A gates (short-circuit) --------------------------------------
    Case(
        name="05-contradicted-hard",
        claim_id="e2e-05",
        claim=_CLAIM,
        passages=[_p(_CLAIM)],
        retrieval_scores={"p-1": 0.90},
        entail={"p-1": _spec("contradict", 0.92)},
        verdict="contradicted",
        reason=None,
        flags=[],
        rule_ids={"A4_hard_contradiction"},
    ),
    Case(
        name="06-contradicted-negation",
        claim_id="e2e-06",
        claim="The platform does not log administrator actions.",
        passages=[_p("The platform logs administrator actions.")],
        retrieval_scores={"p-1": 0.90},
        entail={"p-1": _spec("entail", 0.90)},
        verdict="contradicted",
        reason=None,
        flags=[],
        rule_ids={"A3_negation_backstop"},
    ),
    Case(
        name="13-not-checkable-opinion",
        claim_id="e2e-13",
        claim="In my opinion the dashboard is the best feature.",
        passages=[_p("The dashboard shows live metrics.")],
        retrieval_scores={"p-1": 0.90},
        entail={"p-1": _spec("neutral", 0.30)},
        verdict="not_checkable",
        reason="out_of_scope",
        flags=[],
        rule_ids={"A1_scope"},
    ),
    Case(
        name="14-not-checkable-short",
        claim_id="e2e-14",
        claim="Systems work.",
        passages=[_p("Systems work as expected under load.")],
        retrieval_scores={"p-1": 0.90},
        entail={"p-1": _spec("neutral", 0.30)},
        verdict="not_checkable",
        reason="out_of_scope",
        flags=[],
        rule_ids={"A1_scope"},
    ),
    Case(
        name="15-not-checkable-no-evidence",
        claim_id="e2e-15",
        claim=_CLAIM,
        passages=[_p(_CLAIM)],
        retrieval_scores={"p-1": 0.20},
        entail={"p-1": _spec("entail", 0.95)},
        verdict="not_checkable",
        reason="no_evidence",
        flags=[],
        rule_ids={"A2_retrieval_empty"},
    ),
    Case(
        name="16-not-checkable-no-entail",
        claim_id="e2e-16",
        claim=_CLAIM,
        passages=[_p(_CLAIM)],
        retrieval_scores={"p-1": 0.90},
        entail={"p-1": _spec("neutral", 0.30)},
        verdict="not_checkable",
        reason="no_entail_signal",
        flags=[],
        rule_ids={"B5_degree"},
    ),
    # --- Phase C adjustments + composition ----------------------------------
    Case(
        name="07-composition-numeric-overstated",
        claim_id="e2e-07",
        claim="The system must reach 95 percent uptime.",
        passages=[_p("The system typically reaches 80 percent uptime.")],
        retrieval_scores={"p-1": 0.90},
        entail={"p-1": _spec("entail", 0.90)},
        verdict="contradicted",
        reason=None,
        flags=["overstated"],
        rule_ids={"B5_degree", "C6a_numeric", "C6b_strength_scope"},
    ),
    Case(
        name="08-numeric-noncrux-partial",
        claim_id="e2e-08",
        claim="The service meets 95 percent uptime and 40 percent capacity.",
        passages=[_p("The service meets 95 percent uptime and 70 percent capacity.")],
        retrieval_scores={"p-1": 0.90},
        entail={"p-1": _spec("entail", 0.90)},
        verdict="partially_supported",
        reason=None,
        flags=[],
        rule_ids={"B5_degree", "C6a_numeric"},
    ),
    Case(
        name="09-overstated-from-supported",
        claim_id="e2e-09",
        claim="All submitted records pass schema validation.",
        passages=[_p("Most submitted entries satisfy the schema checks.")],
        retrieval_scores={"p-1": 0.90},
        entail={"p-1": _spec("entail", 0.90)},
        verdict="partially_supported",
        reason=None,
        flags=["overstated"],
        rule_ids={"B5_degree", "C6b_strength_scope"},
    ),
    Case(
        name="10-overstated-from-partial",
        claim_id="e2e-10",
        claim="Every transaction must be encrypted at rest.",
        passages=[_p("Some transactions are encrypted before storage.")],
        retrieval_scores={"p-1": 0.90},
        entail={"p-1": _spec("entail", 0.60)},
        verdict="partially_supported",
        reason=None,
        flags=["overstated"],
        rule_ids={"B5_degree", "C6b_strength_scope"},
    ),
    Case(
        name="11-source-scope-error",
        claim_id="e2e-11",
        claim="The compound reduces infection risk in trials.",
        passages=[_p("The compound reduces infection risk in trials.", trust="background")],
        retrieval_scores={"p-1": 0.90},
        entail={"p-1": _spec("entail", 0.90)},
        verdict="supported",
        reason=None,
        flags=["source_scope_error"],
        rule_ids={"B5_degree", "C6d_source_scope"},
    ),
    Case(
        name="12-false-caution",
        claim_id="e2e-12",
        claim="The results may improve reporting accuracy.",
        passages=[_p("The results may improve reporting accuracy.")],
        retrieval_scores={"p-1": 0.90},
        entail={"p-1": _spec("entail", 0.90)},
        verdict="supported",
        reason=None,
        flags=["false_caution"],
        rule_ids={"B5_degree", "C6f_false_caution"},
    ),
    # Ambiguous-unit numeric claim (mg/kg) through the full pipeline — the
    # real-world path the percent-only fixtures cannot reach. Exercises
    # quantulum3's deterministic no-classifier mode end-to-end. 6a crux mismatch.
    Case(
        name="17-numeric-ambiguous-unit",
        claim_id="e2e-17",
        claim="The compound was dosed at 5 mg/kg.",
        passages=[_p("The compound was dosed at 9 mg/kg.")],
        retrieval_scores={"p-1": 0.90},
        entail={"p-1": _spec("entail", 0.90)},
        verdict="contradicted",
        reason=None,
        flags=[],
        rule_ids={"B5_degree", "C6a_numeric"},
    ),
    # --- Decision F regression fixtures (the 2026-07-02 review probe cases;
    # adr-v1-rules-v1.4.0-semantic-fixes.md). Each locked the OLD behaviour's
    # false degrade/inversion; under v1.4.0 the NLI signal must survive. ------
    Case(
        name="18-negation-agreeing-absence",
        claim_id="e2e-18",
        claim="The final formulation does not contain animal-derived ingredients.",
        passages=[_p("The final formulation contains no animal-derived ingredients.")],
        retrieval_scores={"p-1": 0.90},
        entail={"p-1": _spec("entail", 0.95)},
        verdict="supported",
        reason=None,
        flags=[],
        rule_ids={"B5_degree"},
    ),
    Case(
        name="19-strong-claim-plain-paraphrase",
        claim_id="e2e-19",
        claim="All deviation reports must be approved by the quality unit before batch release.",
        passages=[
            _p("The quality unit reviews and approves deviation reports before batch release.")
        ],
        retrieval_scores={"p-1": 0.90},
        entail={"p-1": _spec("entail", 0.92)},
        verdict="supported",
        reason=None,
        flags=[],
        rule_ids={"B5_degree"},
    ),
    Case(
        name="20-approx-numeric-tolerated",
        claim_id="e2e-20",
        claim="Approximately 40 percent of stability samples showed moisture uptake.",
        passages=[
            _p("Moisture uptake was observed in 39.6 percent of the stability samples tested.")
        ],
        retrieval_scores={"p-1": 0.90},
        entail={"p-1": _spec("entail", 0.90)},
        verdict="supported",
        reason=None,
        flags=["inferred"],
        rule_ids={"B5_degree", "C6c_inferred"},
    ),
    Case(
        name="21-year-vs-measure-abstains",
        claim_id="e2e-21",
        claim="In 2024 the facility processed batches for export.",
        passages=[_p("The facility throughput reached 85 percent in review.")],
        retrieval_scores={"p-1": 0.90},
        entail={"p-1": _spec("entail", 0.90)},
        verdict="supported",
        reason=None,
        flags=["inferred"],
        rule_ids={"B5_degree", "C6c_inferred"},
    ),
    # Decision F4: a sub-floor passage cannot produce the winning signal — the
    # canned contradict on p-2 (below the 0.40 floor) is never entailed, so the
    # A4 gate cannot fire from it; the on-floor neutral yields no_entail_signal.
    Case(
        name="22-subfloor-contradict-filtered",
        claim_id="e2e-22",
        claim=_CLAIM,
        passages=[_p(_CLAIM, pid="p-1"), _p("The platform never validates records.", pid="p-2")],
        retrieval_scores={"p-1": 0.90, "p-2": 0.30},
        entail={"p-1": _spec("neutral", 0.95), "p-2": _spec("contradict", 0.95)},
        verdict="not_checkable",
        reason="no_entail_signal",
        flags=[],
        rule_ids={"B5_degree"},
    ),
]


def _run(case: Case) -> AuditTrace:
    request = AuditRequest(
        claim_id=case.claim_id,
        claim_text=case.claim,
        passages=case.passages,
        audit_config=_CONFIG,
    )
    return run_audit(
        request,
        feature_extractor=DefaultFeatureExtractor(),
        retriever=StubRetriever(scores=case.retrieval_scores),
        entailer=StubEntailer(responses=case.entail),
        aggregator=MaxEntailmentAggregator(),
        rules=VerdictRules(rules_file_sha=_CONFIG.rules_file_sha),
    )


def _dump(trace: AuditTrace) -> str:
    return trace.model_dump_json(indent=2) + "\n"


def test_case_names_unique() -> None:
    assert len({case.name for case in CASES}) == len(CASES)


def test_every_verdict_label_covered() -> None:
    # The full SupportVerdict vocabulary must be reachable end-to-end.
    assert {case.verdict for case in CASES} == {
        "supported",
        "partially_supported",
        "unsupported",
        "contradicted",
        "not_checkable",
    }


def test_all_not_checkable_reasons_covered() -> None:
    reasons = {case.reason for case in CASES if case.verdict == "not_checkable"}
    assert reasons == {"out_of_scope", "no_evidence", "no_entail_signal"}


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.name)
def test_e2e_verdict(case: Case) -> None:
    trace = _run(case)
    assert trace.verdict.support_verdict == case.verdict, case.name
    assert trace.verdict.support_verdict_reason == case.reason, case.name
    assert set(trace.verdict.audit_flags) == set(case.flags), case.name
    assert {fired.rule_id for fired in trace.rules_fired} == case.rule_ids, case.name
    # Trace lineage is always stamped.
    assert trace.audit_config_hash.startswith("sha256:")
    assert trace.library_version
    assert trace.claim_id == case.claim_id


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.name)
def test_e2e_byte_identical_and_golden(case: Case) -> None:
    first = _dump(_run(case))
    second = _dump(_run(case))
    assert first == second, f"{case.name}: two runs diverged"

    golden = _TRACES_DIR / f"{case.name}.json"
    if os.environ.get("CAL_WRITE_GOLDENS"):
        golden.parent.mkdir(parents=True, exist_ok=True)
        golden.write_text(first, encoding="utf-8")
    assert golden.is_file(), f"missing golden trace: {golden} (run with CAL_WRITE_GOLDENS=1)"
    assert golden.read_text(encoding="utf-8") == first, f"{case.name}: trace drifted from golden"
