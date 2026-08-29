"""Pre-freeze RC1A real-execution acceptance evaluator.

This is evaluator apparatus, not candidate code. Once the designated RC1A
freeze commit records its blob identity, it must not be edited within RC1A.
A corrected evaluator after freeze requires a separately named successor.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Mapping

from claim_audit_lab.contracts.bundle_loader import load_bundle
from claim_audit_lab.v1 import pipeline as v1_pipeline
from claim_audit_lab.v1.config import load_default_audit_config
from claim_audit_lab.v1.impl.aggregator import MaxEntailmentAggregator
from claim_audit_lab.v1.impl.features import DefaultFeatureExtractor
from claim_audit_lab.v1.impl.rules import VerdictRules
from claim_audit_lab.v1.intake import bundle_to_requests
from claim_audit_lab.v1.models import (
    AuditRequest,
    AuditTrace,
    EntailResult,
    Passage,
    RetrievalResult,
)

ROOT = Path(__file__).resolve().parents[2]
CANDIDATE_PATH = ROOT / "docs" / "research" / "rc1a_candidate.py"

ASSESSMENT_STATES = {
    "performed-positive",
    "performed-adverse",
    "performed-unknown",
    "not-performed",
    "not-applicable",
    "failed",
}
PARTICIPATION_STATES = {"deciding", "residual", "excluded", "unresolved"}
POLICIES = {"ALLOW_PRIMARY_OR_SECONDARY", "PRIMARY_ONLY"}

PROTECTED_GIT_OBJECTS = {
    "src/claim_audit_lab/v1/runner.py": "db53f49745876b6158da0c233fb80916bbeaabaf",
    "src/claim_audit_lab/v1/pipeline.py": "dd67d0d35590d3052826ad697ce9fd11222fff6f",
    "src/claim_audit_lab/v1/intake.py": "d8b304a4259ec128e656f07ca628d8a0a88ddd69",
    "src/claim_audit_lab/v1/models.py": "755e0ef1757055905f3c8b76b7edc5e8ddc1fefd",
    "src/claim_audit_lab/contracts/contract_c.py": "d6b32a44ef11109fe0ee91efa212d3904badf58c",
    "src/claim_audit_lab/v1/impl/aggregator.py": "b1f9e2309ae3d024bc609b83cc546acb30be6e9b",
    "src/claim_audit_lab/v1/impl/entailer.py": "aaf9415e74ec2f04357ecf5346491d92f3e2d0d3",
    "src/claim_audit_lab/v1/impl/retriever.py": "279a287e10f5466b8d2985291080bc0183c72a52",
    "src/claim_audit_lab/v1/impl/rules.py": "bc388d64a5a53db0d33610ab6ff84bd93a811b46",
    "src/claim_audit_lab/v1/configs/cal-rules-v1.13.0.yaml": "ac8147f6624164e9081a4ec365cd3920c25df96d",
    "tests/v1/test_pipeline_e2e.py": "48a22cfab82ea0a2abd8d1c80d0da32a3dacd260",
    "tests/v1/testing/stubs.py": "c7fa94569234caaf5f2134f672737097e5c70111",
    "tests/v1/fixtures/traces": "7d6735da5f23f78efae479d3c99c1fd2f075f935",
    "tests/fixtures/cb/evidence-bundle-minimal": "5bcfa0a27877cb7ceebf22cd8960e907f6f92083",
}

_LOGITS = {
    "entail": (2.0, -1.0, -1.0),
    "neutral": (0.0, 0.0, 0.0),
    "contradict": (-1.0, -1.0, 2.0),
}


@dataclass(frozen=True)
class EntailSpec:
    label: str
    score: float
    p_entail: float | None = None
    p_contradict: float | None = None


@dataclass(frozen=True)
class FrozenRetriever:
    scores: Mapping[str, float] = field(default_factory=dict)

    def retrieve(
        self, claim: str, passages: list[Passage], top_k: int
    ) -> list[RetrievalResult]:
        del claim
        ranked = sorted(
            passages,
            key=lambda p: self.scores.get(p.passage_id, 0.0),
            reverse=True,
        )
        return [
            RetrievalResult(
                passage_id=p.passage_id,
                score=self.scores.get(p.passage_id, 0.0),
            )
            for p in ranked[:top_k]
        ]


@dataclass(frozen=True)
class FrozenEntailer:
    responses: Mapping[str, EntailSpec] = field(default_factory=dict)
    claim_responses: Mapping[str, EntailSpec] = field(default_factory=dict)

    def entail(self, claim: str, premise: str, passage_id: str) -> EntailResult:
        del premise
        spec = self.claim_responses.get(
            claim,
            self.responses.get(passage_id, EntailSpec("neutral", 0.0)),
        )
        return EntailResult(
            passage_id=passage_id,
            label=spec.label,
            score=spec.score,
            raw_logits=_LOGITS[spec.label],
            p_entail=spec.p_entail,
            p_contradict=spec.p_contradict,
        )


@dataclass(frozen=True)
class RegressionCase:
    name: str
    claim: str
    passages: tuple[Passage, ...]
    retrieval_scores: Mapping[str, float]
    entail: Mapping[str, EntailSpec]
    expected_verdict: str
    expected_reason: str | None = None
    expected_flags: tuple[str, ...] = ()
    source_boundary: str | None = None
    claimed_material_is_a_named_gap: bool = False
    claim_responses: Mapping[str, EntailSpec] = field(default_factory=dict)


def _p(
    text: str,
    pid: str = "p-1",
    trust: str = "primary",
    **meta: str,
) -> Passage:
    return Passage(
        passage_id=pid,
        text=text,
        source_meta={"trust_level": trust, **meta},
    )


_CLAIM = "The platform validates submitted input records."

REGRESSION_CASES = (
    RegressionCase(
        "supported",
        _CLAIM,
        (_p(_CLAIM),),
        {"p-1": 0.90},
        {"p-1": EntailSpec("entail", 0.95)},
        "supported",
    ),
    RegressionCase(
        "partially-supported",
        _CLAIM,
        (_p(_CLAIM),),
        {"p-1": 0.90},
        {"p-1": EntailSpec("entail", 0.55)},
        "partially_supported",
    ),
    RegressionCase(
        "unsupported",
        _CLAIM,
        (_p(_CLAIM),),
        {"p-1": 0.90},
        {"p-1": EntailSpec("contradict", 0.50)},
        "unsupported",
    ),
    RegressionCase(
        "contradicted",
        "The platform does not log administrator actions.",
        (_p("The platform logs administrator actions."),),
        {"p-1": 0.90},
        {"p-1": EntailSpec("entail", 0.90)},
        "contradicted",
    ),
    RegressionCase(
        "not-checkable-no-evidence",
        _CLAIM,
        (_p(_CLAIM),),
        {"p-1": 0.20},
        {"p-1": EntailSpec("entail", 0.95)},
        "not_checkable",
        "no_evidence",
    ),
    RegressionCase(
        "not-checkable-no-entail",
        _CLAIM,
        (_p(_CLAIM),),
        {"p-1": 0.90},
        {"p-1": EntailSpec("neutral", 0.30)},
        "not_checkable",
        "no_entail_signal",
    ),
    RegressionCase(
        "conflicting-evidence",
        _CLAIM,
        (
            _p(_CLAIM, "p-1"),
            _p("The platform never validates submitted input records.", "p-2"),
        ),
        {"p-1": 0.95, "p-2": 0.94},
        {
            "p-1": EntailSpec(
                "entail", 0.96, p_entail=0.96, p_contradict=0.01
            ),
            "p-2": EntailSpec(
                "contradict", 0.95, p_entail=0.01, p_contradict=0.95
            ),
        },
        "not_checkable",
        "conflicting_evidence",
    ),
    RegressionCase(
        "filtered-non-deciding",
        _CLAIM,
        (
            _p(_CLAIM, "p-1"),
            _p("The platform never validates records.", "p-2"),
        ),
        {"p-1": 0.90, "p-2": 0.30},
        {
            "p-1": EntailSpec("neutral", 0.95),
            "p-2": EntailSpec("contradict", 0.95),
        },
        "not_checkable",
        "no_entail_signal",
    ),
    RegressionCase(
        "inference-shaped",
        "The platform retains audit logs securely.",
        (_p("The system stores activity records with strong encryption."),),
        {"p-1": 0.90},
        {"p-1": EntailSpec("entail", 0.90)},
        "supported",
        expected_flags=("inferred",),
    ),
    RegressionCase(
        "absence-exhaustive-source-boundary",
        "The guidance does not address storage conditions for retention samples.",
        (_p("Long-term testing must cover at least 12 months at submission."),),
        {"p-1": 0.90},
        {"p-1": EntailSpec("contradict", 0.98)},
        "supported",
        source_boundary="exhaustive",
    ),
)


class CountingRunner:
    """Observable delegate to the exact current production run_audit callable."""

    def __init__(self) -> None:
        self.calls: list[AuditRequest] = []
        self.outputs: list[AuditTrace] = []

    def __call__(self, request: AuditRequest, **kwargs: Any) -> AuditTrace:
        self.calls.append(request)
        trace = v1_pipeline.run_audit(request, **kwargs)
        self.outputs.append(trace)
        return trace


def _config() -> Any:
    return load_default_audit_config()


def make_request(case: RegressionCase) -> AuditRequest:
    return AuditRequest(
        claim_id=f"rc1a-{case.name}",
        claim_text=case.claim,
        passages=list(case.passages),
        audit_config=_config(),
        source_boundary=case.source_boundary,
        claimed_material_is_a_named_gap=case.claimed_material_is_a_named_gap,
    )


def make_layers(case: RegressionCase) -> dict[str, Any]:
    config = _config()
    return {
        "feature_extractor": DefaultFeatureExtractor(),
        "retriever": FrozenRetriever(case.retrieval_scores),
        "entailer": FrozenEntailer(case.entail, case.claim_responses),
        "aggregator": MaxEntailmentAggregator(),
        "rules": VerdictRules(rules_file_sha=config.rules_file_sha),
    }


def direct_run(case: RegressionCase) -> AuditTrace:
    return v1_pipeline.run_audit(make_request(case), **make_layers(case))


def trace_bytes(trace: AuditTrace) -> bytes:
    return (trace.model_dump_json(indent=2) + "\n").encode()


def semantic_measurement_bytes(trace: AuditTrace) -> bytes:
    payload = {
        "features": trace.features.model_dump(mode="json"),
        "retrieval": [row.model_dump(mode="json") for row in trace.retrieval],
        "entailment": [row.model_dump(mode="json") for row in trace.entailment],
        "support_signal": trace.support_signal.model_dump(mode="json"),
        "negation_probe": (
            trace.negation_probe.model_dump(mode="json")
            if trace.negation_probe is not None
            else None
        ),
    }
    return (
        json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode()


def verdict_bytes(trace: AuditTrace) -> bytes:
    return (
        json.dumps(
            trace.verdict.model_dump(mode="json"),
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _load_module(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_candidate() -> ModuleType:
    if not CANDIDATE_PATH.is_file():
        raise FileNotFoundError(CANDIDATE_PATH)
    return _load_module(CANDIDATE_PATH, "rc1a_candidate")


def _assessor(
    outcome: str | Exception,
) -> tuple[Callable[..., str], list[str]]:
    calls: list[str] = []

    def assess(passage_id: str, passage: Passage, trace: AuditTrace) -> str:
        del passage, trace
        calls.append(passage_id)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    return assess, calls


def _failure_injector(
    exc: Exception,
) -> tuple[Callable[[str], None], list[str]]:
    calls: list[str] = []

    def inject(stage: str) -> None:
        calls.append(stage)
        raise exc

    return inject, calls


def _call_subject(
    subject: ModuleType | Any,
    case: RegressionCase,
    *,
    assessment_plan: Mapping[str, str] | None = None,
    assessor: Callable[..., str] | None = None,
    policy_id: str = "ALLOW_PRIMARY_OR_SECONDARY",
    aggregation_mode: str | None = None,
    causal_replay_ids: tuple[str, ...] = (),
    failure_injector: Callable[[str], None] | None = None,
    request: AuditRequest | None = None,
    runner: CountingRunner | None = None,
) -> tuple[dict[str, Any], CountingRunner]:
    request = request or make_request(case)
    runner = runner or CountingRunner()
    plan = assessment_plan
    if plan is None:
        plan = {p.passage_id: "not-applicable" for p in request.passages}
    if assessor is None:
        assessor, _ = _assessor("positive")
    result = subject.run_captured_audit(
        request,
        audit_runner=runner,
        assessment_plan=dict(plan),
        assessor=assessor,
        policy_id=policy_id,
        aggregation_mode=aggregation_mode,
        causal_replay_ids=causal_replay_ids,
        failure_injector=failure_injector,
        **make_layers(case),
    )
    if not isinstance(result, dict) or set(result) != {"trace", "receipt"}:
        raise AssertionError("candidate result must be exactly {'trace', 'receipt'}")
    if not isinstance(result["receipt"], dict):
        raise AssertionError("receipt must be a dict")
    return result, runner


def _assert_direct_expected(case: RegressionCase, trace: AuditTrace) -> None:
    assert trace.verdict.support_verdict == case.expected_verdict
    assert trace.verdict.support_verdict_reason == case.expected_reason
    assert tuple(trace.verdict.audit_flags) == case.expected_flags


def _git_object(path: str) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", f"HEAD:{path}"],
        cwd=ROOT,
        text=True,
    ).strip()


def verify_protected_git_objects() -> dict[str, str]:
    observed: dict[str, str] = {}
    for path, expected in PROTECTED_GIT_OBJECTS.items():
        actual = _git_object(path)
        if actual != expected:
            raise AssertionError(
                f"protected object drift: {path}: {actual} != {expected}"
            )
        observed[path] = actual
    return observed


def _receipt_state(result: dict[str, Any]) -> str:
    return str(result["receipt"].get("execution", {}).get("state"))


def evaluate_candidate(
    subject: ModuleType,
) -> tuple[dict[str, bool], dict[str, Any]]:
    gates = {f"gate_{i:02d}": False for i in range(1, 14)}
    receipts: dict[str, Any] = {"regression": {}, "diagnostics": {}}

    regression_ok = True
    real_execution_ok = True
    semantic_ok = True
    verdict_ok = True
    trace_ok = True
    for case in REGRESSION_CASES:
        direct = direct_run(case)
        _assert_direct_expected(case, direct)
        request = make_request(case)
        result, runner = _call_subject(subject, case, request=request)
        wrapped = result["trace"]
        if not isinstance(wrapped, AuditTrace):
            regression_ok = False
            real_execution_ok = False
            semantic_ok = False
            verdict_ok = False
            trace_ok = False
            continue
        real_execution_ok &= (
            len(runner.calls) == 1
            and len(runner.outputs) == 1
            and runner.calls[0] is request
            and wrapped is runner.outputs[0]
        )
        semantic_ok &= (
            semantic_measurement_bytes(direct)
            == semantic_measurement_bytes(wrapped)
        )
        verdict_ok &= verdict_bytes(direct) == verdict_bytes(wrapped)
        trace_ok &= trace_bytes(direct) == trace_bytes(wrapped)
        receipts["regression"][case.name] = {
            "direct_semantic_sha256": sha256(semantic_measurement_bytes(direct)),
            "wrapped_semantic_sha256": sha256(semantic_measurement_bytes(wrapped)),
            "direct_verdict_sha256": sha256(verdict_bytes(direct)),
            "wrapped_verdict_sha256": sha256(verdict_bytes(wrapped)),
            "direct_trace_sha256": sha256(trace_bytes(direct)),
            "wrapped_trace_sha256": sha256(trace_bytes(wrapped)),
            "verdict": direct.verdict.model_dump(mode="json"),
        }
    gates["gate_01"] = regression_ok and real_execution_ok
    gates["gate_02"] = regression_ok and semantic_ok
    gates["gate_03"] = regression_ok and verdict_ok
    gates["gate_04"] = regression_ok and trace_ok

    ladder_case = REGRESSION_CASES[0]
    ladder_observed: dict[str, str] = {}
    ladder_ok = True
    ladder_rows: tuple[tuple[str, str, str | Exception, int, str], ...] = (
        ("performed-positive", "perform", "positive", 1, "successful"),
        ("performed-adverse", "perform", "adverse", 1, "successful"),
        ("performed-unknown", "perform", "unknown", 1, "successful"),
        ("not-performed", "not-performed", "positive", 0, "successful"),
        ("not-applicable", "not-applicable", "positive", 0, "successful"),
        (
            "failed",
            "perform",
            RuntimeError("rc1a-assessment-failure"),
            1,
            "assessment_failure",
        ),
    )
    for (
        expected_state,
        plan_value,
        assessor_outcome,
        expected_calls,
        expected_exec,
    ) in ladder_rows:
        assessor_fn, calls = _assessor(assessor_outcome)
        result, _ = _call_subject(
            subject,
            ladder_case,
            assessment_plan={"p-1": plan_value},
            assessor=assessor_fn,
        )
        observed_state = (
            result["receipt"]
            .get("assessments", {})
            .get("p-1", {})
            .get("state")
        )
        ladder_observed[expected_state] = str(observed_state)
        ladder_ok &= (
            observed_state == expected_state
            and len(calls) == expected_calls
            and _receipt_state(result) == expected_exec
        )
        if expected_state == "failed":
            ladder_ok &= result["receipt"].get("epistemic_conclusion") is None
    ladder_ok &= set(ladder_observed.values()) == ASSESSMENT_STATES

    background_case = RegressionCase(
        "trust-not-assessment",
        _CLAIM,
        (_p(_CLAIM, trust="background"),),
        {"p-1": 0.90},
        {"p-1": EntailSpec("entail", 0.95)},
        "supported",
        expected_flags=("source_scope_error",),
    )
    assessor_fn, calls = _assessor("positive")
    bg_result, _ = _call_subject(
        subject,
        background_case,
        assessment_plan={"p-1": "perform"},
        assessor=assessor_fn,
    )
    ladder_ok &= (
        bg_result["receipt"]
        .get("assessments", {})
        .get("p-1", {})
        .get("state")
        == "performed-positive"
        and len(calls) == 1
    )
    gates["gate_05"] = ladder_ok
    receipts["diagnostics"]["assessment_ladder"] = ladder_observed

    participation_case = RegressionCase(
        "participation",
        _CLAIM,
        (
            _p(_CLAIM, "p-deciding", trust="primary"),
            _p("Secondary corroboration.", "p-residual", trust="secondary"),
            _p("Adverse assessment item.", "p-excluded", trust="primary"),
            _p("Unresolved assessment item.", "p-unresolved", trust="primary"),
        ),
        {
            "p-deciding": 0.95,
            "p-residual": 0.80,
            "p-excluded": 0.70,
            "p-unresolved": 0.60,
        },
        {
            "p-deciding": EntailSpec("entail", 0.95),
            "p-residual": EntailSpec("neutral", 0.40),
            "p-excluded": EntailSpec("neutral", 0.40),
            "p-unresolved": EntailSpec("neutral", 0.40),
        },
        "supported",
    )
    outcomes = {
        "p-deciding": "positive",
        "p-residual": "positive",
        "p-excluded": "adverse",
        "p-unresolved": "unknown",
    }
    p_calls: list[str] = []

    def p_assessor(pid: str, passage: Passage, trace: AuditTrace) -> str:
        del passage, trace
        p_calls.append(pid)
        return outcomes[pid]

    p_result, _ = _call_subject(
        subject,
        participation_case,
        assessment_plan={pid: "perform" for pid in outcomes},
        assessor=p_assessor,
        policy_id="PRIMARY_ONLY",
    )
    p_states = {
        pid: row.get("state")
        for pid, row in p_result["receipt"].get("participation", {}).items()
    }
    gates["gate_06"] = (
        set(p_states.values()) == PARTICIPATION_STATES
        and p_states.get("p-deciding") == "deciding"
        and p_states.get("p-residual") == "residual"
        and p_states.get("p-excluded") == "excluded"
        and p_states.get("p-unresolved") == "unresolved"
        and set(p_calls) == set(outcomes)
    )
    receipts["diagnostics"]["participation"] = p_states

    policy_case = RegressionCase(
        "policy-counterfactual",
        _CLAIM,
        (_p(_CLAIM, trust="secondary"),),
        {"p-1": 0.90},
        {"p-1": EntailSpec("entail", 0.95)},
        "supported",
    )
    a1, _ = _assessor("positive")
    allow, _ = _call_subject(
        subject,
        policy_case,
        assessment_plan={"p-1": "perform"},
        assessor=a1,
        policy_id="ALLOW_PRIMARY_OR_SECONDARY",
    )
    a2, _ = _assessor("positive")
    primary, _ = _call_subject(
        subject,
        policy_case,
        assessment_plan={"p-1": "perform"},
        assessor=a2,
        policy_id="PRIMARY_ONLY",
    )
    allow_p = (
        allow["receipt"].get("participation", {}).get("p-1", {}).get("state")
    )
    primary_p = (
        primary["receipt"].get("participation", {}).get("p-1", {}).get("state")
    )
    allow_policy = allow["receipt"].get("policy", {})
    primary_policy = primary["receipt"].get("policy", {})
    policy_trace_same = (
        isinstance(allow["trace"], AuditTrace)
        and isinstance(primary["trace"], AuditTrace)
        and trace_bytes(allow["trace"]) == trace_bytes(primary["trace"])
        and semantic_measurement_bytes(allow["trace"])
        == semantic_measurement_bytes(primary["trace"])
    )
    gates["gate_07"] = (
        allow_p == "deciding"
        and primary_p == "residual"
        and allow_policy.get("id") == "ALLOW_PRIMARY_OR_SECONDARY"
        and primary_policy.get("id") == "PRIMARY_ONLY"
        and bool(allow_policy.get("inputs"))
        and bool(primary_policy.get("inputs"))
        and allow_policy.get("effects") != primary_policy.get("effects")
        and policy_trace_same
    )

    injected = RuntimeError("RC1A_INJECTED_WRAPPER_FAILURE")
    injector, inject_calls = _failure_injector(injected)
    fail_result, fail_runner = _call_subject(
        subject,
        ladder_case,
        assessment_plan={"p-1": "perform"},
        failure_injector=injector,
    )
    unknown_assessor, _ = _assessor("unknown")
    unknown_result, _ = _call_subject(
        subject,
        ladder_case,
        assessment_plan={"p-1": "perform"},
        assessor=unknown_assessor,
    )
    np_result, _ = _call_subject(
        subject,
        ladder_case,
        assessment_plan={"p-1": "not-performed"},
    )
    nc_result, _ = _call_subject(subject, REGRESSION_CASES[4])
    agg_result, _ = _call_subject(
        subject,
        REGRESSION_CASES[0],
        aggregation_mode="no_authorized_composition",
    )
    failure_execution = fail_result["receipt"].get("execution", {})
    distinct_signatures = {
        (
            _receipt_state(fail_result),
            fail_result["receipt"]
            .get("assessments", {})
            .get("p-1", {})
            .get("state"),
            fail_result["receipt"].get("aggregation", {}).get("state"),
        ),
        (
            _receipt_state(unknown_result),
            unknown_result["receipt"]
            .get("assessments", {})
            .get("p-1", {})
            .get("state"),
            unknown_result["receipt"].get("aggregation", {}).get("state"),
        ),
        (
            _receipt_state(np_result),
            np_result["receipt"]
            .get("assessments", {})
            .get("p-1", {})
            .get("state"),
            np_result["receipt"].get("aggregation", {}).get("state"),
        ),
        (
            _receipt_state(nc_result),
            nc_result["trace"].verdict.support_verdict
            if nc_result["trace"]
            else None,
            nc_result["trace"].verdict.support_verdict_reason
            if nc_result["trace"]
            else None,
        ),
        (
            _receipt_state(agg_result),
            agg_result["receipt"].get("aggregation", {}).get("state"),
            None,
        ),
    }
    gates["gate_08"] = (
        failure_execution.get("state") == "wrapper_failure"
        and failure_execution.get("stage") == "pre_run"
        and failure_execution.get("failure_type") == "RuntimeError"
        and failure_execution.get("failure_message")
        == "RC1A_INJECTED_WRAPPER_FAILURE"
        and inject_calls == ["pre_run"]
        and len(fail_runner.calls) == 0
        and len(fail_runner.outputs) == 0
        and fail_result["trace"] is None
        and fail_result["receipt"].get("epistemic_conclusion") is None
        and len(distinct_signatures) == 5
    )
    receipts["diagnostics"]["failure_capture"] = failure_execution

    distributed = RegressionCase(
        "distributed-unresolved",
        "The platform validates records and archives them.",
        (
            _p("The platform validates submitted records.", "p-1"),
            _p("The platform archives submitted records.", "p-2"),
        ),
        {"p-1": 0.95, "p-2": 0.94},
        {
            "p-1": EntailSpec("entail", 0.60),
            "p-2": EntailSpec("entail", 0.60),
        },
        "partially_supported",
    )
    dist_result, _ = _call_subject(
        subject,
        distributed,
        aggregation_mode="no_authorized_composition",
    )
    aggregation = dist_result["receipt"].get("aggregation", {})
    gates["gate_09"] = (
        aggregation.get("state") == "unresolved"
        and set(aggregation.get("passage_ids", [])) == {"p-1", "p-2"}
        and aggregation.get("composed_result") is None
    )

    causal = RegressionCase(
        "causal-replay",
        _CLAIM,
        (
            _p(_CLAIM, "p-1"),
            _p("Unrelated administrative note.", "p-2"),
        ),
        {"p-1": 0.95, "p-2": 0.80},
        {
            "p-1": EntailSpec("entail", 0.95),
            "p-2": EntailSpec("neutral", 0.40),
        },
        "supported",
    )
    no_replay, no_replay_runner = _call_subject(subject, causal)
    replay, replay_runner = _call_subject(
        subject,
        causal,
        causal_replay_ids=("p-1", "p-2"),
    )
    no_basis = no_replay["receipt"].get("causal_basis", {})
    basis = replay["receipt"].get("causal_basis", {})
    p1 = basis.get("p-1", {})
    p2 = basis.get("p-2", {})
    gates["gate_10"] = (
        no_basis == {}
        and len(no_replay_runner.calls) == 1
        and len(replay_runner.calls) == 3
        and p1.get("available") is True
        and p1.get("necessary") is True
        and p1.get("baseline_verdict") != p1.get("intervention_verdict")
        and p2.get("available") is True
        and p2.get("necessary") is False
        and p2.get("baseline_verdict") == p2.get("intervention_verdict")
    )
    receipts["diagnostics"]["causal_basis"] = basis

    mutated_meta = RegressionCase(
        "causal-replay-metadata-mutated",
        causal.claim,
        tuple(
            Passage(
                passage_id=p.passage_id,
                text=p.text,
                source_meta={
                    **p.source_meta,
                    "irrelevant_note": "MUTATED",
                },
            )
            for p in causal.passages
        ),
        causal.retrieval_scores,
        causal.entail,
        causal.expected_verdict,
    )
    base_assessor, _ = _assessor("positive")
    base_result, _ = _call_subject(
        subject,
        causal,
        assessment_plan={"p-1": "perform", "p-2": "perform"},
        assessor=base_assessor,
        causal_replay_ids=("p-1", "p-2"),
    )
    mut_assessor, _ = _assessor("positive")
    mut_result, _ = _call_subject(
        subject,
        mutated_meta,
        assessment_plan={"p-1": "perform", "p-2": "perform"},
        assessor=mut_assessor,
        causal_replay_ids=("p-1", "p-2"),
    )
    gates["gate_11"] = (
        isinstance(base_result["trace"], AuditTrace)
        and isinstance(mut_result["trace"], AuditTrace)
        and semantic_measurement_bytes(base_result["trace"])
        == semantic_measurement_bytes(mut_result["trace"])
        and verdict_bytes(base_result["trace"])
        == verdict_bytes(mut_result["trace"])
        and base_result["receipt"].get("assessments")
        == mut_result["receipt"].get("assessments")
        and base_result["receipt"].get("participation")
        == mut_result["receipt"].get("participation")
        and base_result["receipt"].get("causal_basis")
        == mut_result["receipt"].get("causal_basis")
    )

    fail_closed = False
    try:
        _call_subject(subject, ladder_case, assessment_plan={})
    except (ValueError, RuntimeError) as exc:
        fail_closed = (
            "assessment" in str(exc).lower()
            or "receipt" in str(exc).lower()
        )
    gates["gate_12"] = fail_closed

    bundle = load_bundle(
        ROOT / "tests" / "fixtures" / "cb" / "evidence-bundle-minimal"
    )
    requests = bundle_to_requests(bundle, _config())
    boundary_ok = len(requests) >= 1
    if boundary_ok:
        request = requests[0]
        ids = [p.passage_id for p in request.passages]
        intake_case = RegressionCase(
            "contract-b-intake",
            request.claim_text,
            tuple(request.passages),
            {pid: 0.95 for pid in ids},
            {pid: EntailSpec("neutral", 0.30) for pid in ids},
            "not_checkable",
            "no_entail_signal",
        )
        runner = CountingRunner()
        result, runner = _call_subject(
            subject,
            intake_case,
            request=request,
            runner=runner,
            assessment_plan={pid: "not-applicable" for pid in ids},
        )
        boundary_ok &= (
            len(runner.calls) == 1
            and len(runner.outputs) == 1
            and runner.calls[0] is request
            and result["trace"] is runner.outputs[0]
            and isinstance(result["trace"], AuditTrace)
            and result["trace"].claim_id == request.claim_id
            and all("passage_hash" in p.source_meta for p in request.passages)
        )
    gates["gate_13"] = boundary_ok

    receipts["gates"] = gates
    return gates, receipts


# Intentionally weak controls. These are part of the apparatus self-test.


class _W1PostHoc:
    def __init__(self, trace: AuditTrace) -> None:
        self.trace = trace

    def run_captured_audit(
        self,
        request: AuditRequest,
        *,
        audit_runner: Any,
        **kwargs: Any,
    ) -> dict[str, Any]:
        del request, audit_runner, kwargs
        return {
            "trace": self.trace,
            "receipt": {
                "execution": {"state": "successful"},
                "assessments": {},
                "participation": {},
                "policy": {},
                "aggregation": {},
                "causal_basis": {},
                "epistemic_conclusion": self.trace.verdict.model_dump(mode="json"),
            },
        }


class _W2TrustAsAssessment:
    def run_captured_audit(
        self,
        request: AuditRequest,
        *,
        audit_runner: Any,
        assessment_plan: Mapping[str, str],
        assessor: Callable[..., str],
        policy_id: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        del assessment_plan, assessor
        trace = audit_runner(
            request,
            **{k: v for k, v in kwargs.items() if k in _LAYER_KEYS},
        )
        assessments = {}
        for p in request.passages:
            state = (
                "performed-positive"
                if p.source_meta.get("trust_level") == "primary"
                else "performed-adverse"
            )
            assessments[p.passage_id] = {"state": state}
        return {
            "trace": trace,
            "receipt": {
                "execution": {"state": "successful"},
                "assessments": assessments,
                "participation": {},
                "policy": {"id": policy_id},
                "aggregation": {},
                "causal_basis": {},
                "epistemic_conclusion": trace.verdict.model_dump(mode="json"),
            },
        }


class _W3TerminalOnly:
    def run_captured_audit(
        self,
        request: AuditRequest,
        *,
        audit_runner: Any,
        policy_id: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        trace = audit_runner(
            request,
            **{k: v for k, v in kwargs.items() if k in _LAYER_KEYS},
        )
        return {
            "trace": trace,
            "receipt": {
                "execution": {"state": "successful"},
                "terminal_reason": trace.verdict.support_verdict_reason,
                "policy": {"id": policy_id},
                "epistemic_conclusion": trace.verdict.model_dump(mode="json"),
            },
        }


class _W4CausalEchoer:
    def run_captured_audit(
        self,
        request: AuditRequest,
        *,
        audit_runner: Any,
        policy_id: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        trace = audit_runner(
            request,
            **{k: v for k, v in kwargs.items() if k in _LAYER_KEYS},
        )
        basis = {
            result.passage_id: {"available": True, "necessary": True}
            for result in trace.retrieval
        }
        return {
            "trace": trace,
            "receipt": {
                "execution": {"state": "successful"},
                "assessments": {},
                "participation": {},
                "policy": {"id": policy_id},
                "aggregation": {},
                "causal_basis": basis,
                "epistemic_conclusion": trace.verdict.model_dump(mode="json"),
            },
        }


class _W5PolicyIdOnly:
    def run_captured_audit(
        self,
        request: AuditRequest,
        *,
        audit_runner: Any,
        policy_id: str,
        assessment_plan: Mapping[str, str],
        assessor: Callable[..., str],
        **kwargs: Any,
    ) -> dict[str, Any]:
        trace = audit_runner(
            request,
            **{k: v for k, v in kwargs.items() if k in _LAYER_KEYS},
        )
        assessments = {}
        participation = {}
        for p in request.passages:
            if assessment_plan[p.passage_id] == "perform":
                outcome = assessor(p.passage_id, p, trace)
                assessments[p.passage_id] = {"state": f"performed-{outcome}"}
            else:
                assessments[p.passage_id] = {
                    "state": assessment_plan[p.passage_id]
                }
            participation[p.passage_id] = {"state": "deciding"}
        return {
            "trace": trace,
            "receipt": {
                "execution": {"state": "successful"},
                "assessments": assessments,
                "participation": participation,
                "policy": {"id": policy_id},
                "aggregation": {},
                "causal_basis": {},
                "epistemic_conclusion": trace.verdict.model_dump(mode="json"),
            },
        }


class _W6SilentDefault(_W5PolicyIdOnly):
    def run_captured_audit(
        self,
        request: AuditRequest,
        *,
        assessment_plan: Mapping[str, str],
        **kwargs: Any,
    ) -> dict[str, Any]:
        defaulted = {
            p.passage_id: assessment_plan.get(p.passage_id, "not-performed")
            for p in request.passages
        }
        return super().run_captured_audit(
            request,
            assessment_plan=defaulted,
            **kwargs,
        )


_LAYER_KEYS = {"feature_extractor", "retriever", "entailer", "aggregator", "rules"}


def evaluate_weak_controls() -> dict[str, dict[str, Any]]:
    case = REGRESSION_CASES[0]
    results: dict[str, dict[str, Any]] = {}

    runner = CountingRunner()
    w1 = _W1PostHoc(direct_run(case))
    w1_result, runner = _call_subject(w1, case, runner=runner)
    post_hoc = (
        len(runner.calls) == 0
        and len(runner.outputs) == 0
        and isinstance(w1_result["trace"], AuditTrace)
    )
    results["W1"] = {
        "expected_defect": (
            "post-hoc sidecar does not prove real execution/input-boundary capture"
        ),
        "failed_gates": ["gate_01", "gate_13"] if post_hoc else [],
        "rejected": post_hoc,
    }

    adverse, calls = _assessor("adverse")
    w2_result, _ = _call_subject(
        _W2TrustAsAssessment(),
        case,
        assessment_plan={"p-1": "perform"},
        assessor=adverse,
    )
    w2_state = (
        w2_result["receipt"]
        .get("assessments", {})
        .get("p-1", {})
        .get("state")
    )
    w2_bad = w2_state != "performed-adverse" or len(calls) != 1
    results["W2"] = {
        "expected_defect": "source trust masquerades as proposition assessment",
        "failed_gates": ["gate_05"] if w2_bad else [],
        "rejected": w2_bad,
    }

    w3_result, _ = _call_subject(_W3TerminalOnly(), case)
    has_typed = bool(w3_result["receipt"].get("assessments")) and bool(
        w3_result["receipt"].get("participation")
    )
    results["W3"] = {
        "expected_defect": (
            "terminal reason only; no typed assessment/participation"
        ),
        "failed_gates": (
            ["gate_05", "gate_06", "gate_12"] if not has_typed else []
        ),
        "rejected": not has_typed,
    }

    w4_result, w4_runner = _call_subject(
        _W4CausalEchoer(),
        case,
        causal_replay_ids=(),
    )
    bad_basis = (
        bool(w4_result["receipt"].get("causal_basis"))
        and len(w4_runner.calls) == 1
    )
    results["W4"] = {
        "expected_defect": (
            "decision participation echoed as exact causal necessity without intervention"
        ),
        "failed_gates": ["gate_10"] if bad_basis else [],
        "rejected": bad_basis,
    }

    policy_case = RegressionCase(
        "weak-policy",
        _CLAIM,
        (_p(_CLAIM, trust="secondary"),),
        {"p-1": 0.90},
        {"p-1": EntailSpec("entail", 0.95)},
        "supported",
    )
    assess1, _ = _assessor("positive")
    allow, _ = _call_subject(
        _W5PolicyIdOnly(),
        policy_case,
        assessment_plan={"p-1": "perform"},
        assessor=assess1,
        policy_id="ALLOW_PRIMARY_OR_SECONDARY",
    )
    assess2, _ = _assessor("positive")
    primary, _ = _call_subject(
        _W5PolicyIdOnly(),
        policy_case,
        assessment_plan={"p-1": "perform"},
        assessor=assess2,
        policy_id="PRIMARY_ONLY",
    )
    same_participation = (
        allow["receipt"].get("participation")
        == primary["receipt"].get("participation")
    )
    results["W5"] = {
        "expected_defect": "policy identity logged without derived policy effect",
        "failed_gates": ["gate_07"] if same_participation else [],
        "rejected": same_participation,
    }

    silently_succeeded = True
    try:
        _call_subject(_W6SilentDefault(), case, assessment_plan={})
    except Exception:
        silently_succeeded = False
    results["W6"] = {
        "expected_defect": "missing epistemic state silently defaulted",
        "failed_gates": ["gate_12"] if silently_succeeded else [],
        "rejected": silently_succeeded,
    }
    return results


def _all_weak_rejected(
    results: Mapping[str, Mapping[str, Any]],
) -> bool:
    return set(results) == {"W1", "W2", "W3", "W4", "W5", "W6"} and all(
        row.get("rejected") and row.get("failed_gates")
        for row in results.values()
    )


def run_apparatus() -> tuple[dict[str, Any], bool]:
    protected = verify_protected_git_objects()
    weak = evaluate_weak_controls()
    output: dict[str, Any] = {
        "apparatus": "CAL Epistemic Methodology RC1A",
        "protected_git_objects": protected,
        "weak_controls": weak,
        "candidate_present": CANDIDATE_PATH.is_file(),
    }
    ok = _all_weak_rejected(weak)
    if CANDIDATE_PATH.is_file():
        candidate = load_candidate()
        gates, receipts = evaluate_candidate(candidate)
        output["candidate_gates"] = gates
        output["candidate_receipts"] = receipts
        ok = ok and all(gates.values())
    return output, ok


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output, ok = run_apparatus()
    text = json.dumps(output, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    print(text)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
