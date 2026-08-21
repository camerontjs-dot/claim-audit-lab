"""End-to-end real-inference receipt contracts (Phase 2 Unit 3 / B13).

This is the Phase-2 crux: the same ``run_audit`` orchestrator proven
byte-reproducible with stubs (``test_pipeline_e2e.py``) must produce a stable
decision receipt when the real ``BiEncoderRetriever`` + ``DeBERTaEntailer`` are
injected. The orchestrator is unchanged; only the two injected layers differ
from the stub harness.

Each fixture is 5 claims × 3 passages, run through real retriever + real entailer
+ real aggregator + real rules. It asserts two deliberately separate contracts:

* Within one locked environment, the complete raw ``AuditTrace`` is byte-identical
  on consecutive runs.
* Across supported CPU environments, a portable decision receipt must match the
  committed trace. It contains the pinned model/rule provenance, claim features,
  retrieval rank, NLI labels, support-signal passage identities, rule IDs, and
  verdict. It intentionally excludes score telemetry and score-formatted rule
  prose, because the pinned model runtime produces materially different but
  decision-equivalent float values on macOS and Linux.

The full raw scores remain in every ``AuditTrace`` and are required to be finite.
Goldens under ``fixtures/traces/inference/`` are historical raw diagnostics; this
test projects them into the portable receipt and does not regenerate them.
"""

from __future__ import annotations

import json
import math
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


def _raw_trace(trace: AuditTrace) -> str:
    """Serialize the complete, environment-local trace without normalization."""
    return trace.model_dump_json(indent=2) + "\n"


def _portable_receipt(trace: AuditTrace) -> str:
    """Serialize the cross-host decision contract, excluding float telemetry.

    Model scores stay in the raw trace for inspection, but are not a portable
    receipt field: the pinned inference stack has different floating-point
    kernels on macOS and Linux. Every retained field can affect (or explain) a
    decision: provenance, features, retrieval/entailment ordering and labels,
    aggregation identities, fired rules, and final verdict.
    """
    probe = trace.negation_probe
    receipt = {
        "receipt_schema": "cal-real-inference-decision-v1",
        "audit_config_hash": trace.audit_config_hash,
        "library_version": trace.library_version,
        "model_revisions": {
            "retriever": _CONFIG.retriever.model_dump(mode="json"),
            "entailer": _CONFIG.entailer.model_dump(mode="json"),
            "rules_file_sha": _CONFIG.rules_file_sha,
        },
        "claim": {
            "claim_id": trace.claim_id,
            "claim_text": trace.claim_text,
            "features": trace.features.model_dump(mode="json"),
        },
        "retrieval_rank": [result.passage_id for result in trace.retrieval],
        "entailment": [
            {"passage_id": result.passage_id, "label": result.label} for result in trace.entailment
        ],
        "support_signal": {
            "label": trace.support_signal.label,
            "contributing_passage_id": trace.support_signal.contributing_passage_id,
            "best_entail_passage_id": trace.support_signal.best_entail_passage_id,
            "best_contradict_passage_id": trace.support_signal.best_contradict_passage_id,
        },
        "rules_fired": [rule.rule_id for rule in trace.rules_fired],
        "verdict": trace.verdict.model_dump(mode="json"),
        "negation_probe": (
            None
            if probe is None
            else {
                "negated_claim": probe.negated_claim,
                "abstained": probe.abstained,
                "result": (
                    None
                    if probe.result is None
                    else {"passage_id": probe.result.passage_id, "label": probe.result.label}
                ),
            }
        ),
    }
    return json.dumps(receipt, indent=2, sort_keys=True) + "\n"


def _assert_raw_scores_are_finite(trace: AuditTrace) -> None:
    """Raw model telemetry remains available, but is not cross-host byte-stable."""
    results = [*trace.entailment]
    if trace.negation_probe and trace.negation_probe.result:
        results.append(trace.negation_probe.result)
    for result in results:
        assert all(math.isfinite(value) for value in result.raw_logits)
        assert math.isfinite(result.score)
        if result.p_entail is not None:
            assert math.isfinite(result.p_entail)
        if result.p_contradict is not None:
            assert math.isfinite(result.p_contradict)


def test_case_names_unique() -> None:
    assert len({case.name for case in CASES}) == len(CASES)


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.name)
def test_e2e_real_inference_receipt_matches_golden(
    case: Case, layers: tuple[BiEncoderRetriever, DeBERTaEntailer]
) -> None:
    first_trace = _run(case, layers)
    second_trace = _run(case, layers)
    assert _raw_trace(first_trace) == _raw_trace(second_trace), (
        f"{case.name}: same-environment real-inference traces diverged"
    )
    _assert_raw_scores_are_finite(first_trace)
    _assert_raw_scores_are_finite(second_trace)

    golden = _TRACES_DIR / f"{case.name}.json"
    assert golden.is_file(), f"missing golden trace: {golden}"
    golden_trace = AuditTrace.model_validate_json(golden.read_text(encoding="utf-8"))
    assert _portable_receipt(golden_trace) == _portable_receipt(first_trace), (
        f"{case.name}: portable decision receipt drifted from golden"
    )


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
    assert len({result.passage_id for result in trace.retrieval}) == len(case.passages)
    assert [result.passage_id for result in trace.retrieval] == [
        result.passage_id
        for result in sorted(trace.retrieval, key=lambda result: result.score, reverse=True)
    ]
    admitted = [r for r in trace.retrieval if r.score >= _CONFIG.retrieval_floor]
    assert len(trace.entailment) == len(admitted)
    assert {e.passage_id for e in trace.entailment} == {r.passage_id for r in admitted}
    assert trace.rules_fired
