"""End-to-end byte-identity over REAL inference (Phase 2 Unit 3 / B13).

This is the Phase-2 crux: the same ``run_audit`` orchestrator proven
byte-reproducible with stubs (``test_pipeline_e2e.py``) must stay byte-identical
when the real ``BiEncoderRetriever`` + ``DeBERTaEntailer`` are injected — the
property the calibration gate (Phase 4) and DECISIONS.md § 2026-06-21 § 9 depend
on. The orchestrator is unchanged; only the two injected layers differ from the
stub harness.

Each fixture is 5 claims × 3 passages, run through real retriever + real entailer
+ real aggregator + real rules. Two assertions: two consecutive runs produce
byte-identical ``AuditTrace`` JSON, and that JSON matches a committed golden under
``fixtures/traces/inference/``. Regenerate the goldens with
``CAL_WRITE_GOLDENS=1 .venv/bin/python -m pytest tests/v1/test_byte_identity.py``.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import pytest

from claim_audit_lab.v1.config import load_default_audit_config
from claim_audit_lab.v1.impl.aggregator import MaxEntailmentAggregator
from claim_audit_lab.v1.impl.entailer import DeBERTaEntailer
from claim_audit_lab.v1.impl.features import DefaultFeatureExtractor
from claim_audit_lab.v1.impl.retriever import BiEncoderRetriever
from claim_audit_lab.v1.impl.rules import VerdictRules
from claim_audit_lab.v1.models import AuditRequest, AuditTrace, Passage, SupportVerdict
from claim_audit_lab.v1.pipeline import run_audit

_CONFIG = load_default_audit_config()
_TRACES_DIR = Path(__file__).parent / "fixtures" / "traces" / "inference"


def _p(pid: str, text: str) -> Passage:
    return Passage(passage_id=pid, text=text)


@dataclass(frozen=True)
class Case:
    """One end-to-end real-inference fixture: a claim, its 3 candidate passages,
    and the expected support verdict (locked so the goldens are not the only guard)."""

    name: str
    claim_id: str
    claim: str
    passages: list[Passage]
    expected_verdict: SupportVerdict


CASES: list[Case] = [
    # inf-01 / inf-03 are the cases the neutral-masking fix corrected: a
    # confidently-neutral passage (p2) used to outrank the real entail/contradict
    # signal on p1 and flip the verdict to not_checkable (DECISIONS.md § 2026-06-29).
    Case(
        name="inf-01-supported-encryption",
        claim_id="inf-01",
        claim="Customer data is encrypted at rest.",
        passages=[
            _p("p1", "All stored customer data is encrypted at rest using AES-256."),
            _p("p2", "The service maintained 99.95 percent uptime over the last quarter."),
            _p("p3", "The local weather forecast predicts rain on Thursday afternoon."),
        ],
        expected_verdict="supported",
    ),
    Case(
        name="inf-02-contradicted-logging",
        claim_id="inf-02",
        claim="The platform does not log administrator actions.",
        passages=[
            _p("p1", "Every administrator action is recorded in an immutable audit log."),
            _p("p2", "The platform logs all administrator actions for compliance."),
            _p("p3", "This recipe calls for two cups of flour and a pinch of salt."),
        ],
        expected_verdict="contradicted",
    ),
    Case(
        name="inf-03-numeric-uptime",
        claim_id="inf-03",
        claim="The service meets 99 percent uptime.",
        passages=[
            _p("p1", "The service meets 95 percent uptime under normal load."),
            _p("p2", "Availability is monitored continuously by the operations team."),
            _p("p3", "The local weather forecast predicts rain on Thursday afternoon."),
        ],
        expected_verdict="contradicted",
    ),
    Case(
        name="inf-04-opinion-out-of-scope",
        claim_id="inf-04",
        claim="In my opinion the dashboard is the best feature.",
        passages=[
            _p("p1", "The dashboard shows live operational metrics."),
            _p("p2", "Users can configure the dashboard layout."),
            _p("p3", "This recipe calls for two cups of flour and a pinch of salt."),
        ],
        expected_verdict="not_checkable",
    ),
    Case(
        name="inf-05-no-evidence",
        claim_id="inf-05",
        claim="The compound reduces infection risk in clinical trials.",
        passages=[
            _p("p1", "This recipe calls for two cups of flour and a pinch of salt."),
            _p("p2", "The local weather forecast predicts rain on Thursday afternoon."),
            _p("p3", "The cafeteria menu changes every week."),
        ],
        expected_verdict="not_checkable",
    ),
]


@pytest.fixture(scope="module")
def layers() -> tuple[BiEncoderRetriever, DeBERTaEntailer]:
    return BiEncoderRetriever(revision=_CONFIG.retriever), DeBERTaEntailer(
        revision=_CONFIG.entailer
    )


def _run(case: Case, layers: tuple[BiEncoderRetriever, DeBERTaEntailer]) -> AuditTrace:
    retriever, entailer = layers
    request = AuditRequest(
        claim_id=case.claim_id,
        claim_text=case.claim,
        passages=case.passages,
        audit_config=_CONFIG,
    )
    return run_audit(
        request,
        feature_extractor=DefaultFeatureExtractor(),
        retriever=retriever,
        entailer=entailer,
        aggregator=MaxEntailmentAggregator(),
        rules=VerdictRules(rules_file_sha=_CONFIG.rules_file_sha),
    )


def _dump(trace: AuditTrace) -> str:
    return trace.model_dump_json(indent=2) + "\n"


def test_case_names_unique() -> None:
    assert len({case.name for case in CASES}) == len(CASES)


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.name)
def test_e2e_real_inference_byte_identical_and_golden(
    case: Case, layers: tuple[BiEncoderRetriever, DeBERTaEntailer]
) -> None:
    first = _dump(_run(case, layers))
    second = _dump(_run(case, layers))
    assert first == second, f"{case.name}: two real-inference runs diverged"

    golden = _TRACES_DIR / f"{case.name}.json"
    if os.environ.get("CAL_WRITE_GOLDENS"):
        golden.parent.mkdir(parents=True, exist_ok=True)
        golden.write_text(first, encoding="utf-8")
    assert golden.is_file(), f"missing golden trace: {golden} (run with CAL_WRITE_GOLDENS=1)"
    assert golden.read_text(encoding="utf-8") == first, f"{case.name}: trace drifted from golden"


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.name)
def test_e2e_trace_is_well_formed(
    case: Case, layers: tuple[BiEncoderRetriever, DeBERTaEntailer]
) -> None:
    trace = _run(case, layers)
    assert trace.claim_id == case.claim_id
    assert trace.verdict.support_verdict == case.expected_verdict, case.name
    assert trace.audit_config_hash.startswith("sha256:")
    assert trace.library_version
    # Real retrieval over 3 passages returns ranked candidates; only candidates
    # at or above the retrieval floor are entailed (Decision F4).
    assert len(trace.retrieval) == len(case.passages)
    admitted = [r for r in trace.retrieval if r.score >= _CONFIG.retrieval_floor]
    assert len(trace.entailment) == len(admitted)
    assert {e.passage_id for e in trace.entailment} == {r.passage_id for r in admitted}
    assert trace.rules_fired
