from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from collections.abc import Callable
from dataclasses import replace
from pathlib import Path
from typing import Any

from evidence_bundler.v1 import build_package
from evidence_bundler.v1.contract_a import compute_handoff_sha256
from evidence_bundler.v1.contract_b import (
    CONTRACT_B_PRODUCTION_LOCK,
    INTEGRATION_CONFIG,
    INTEGRATION_CONFIG_SHA256,
    INTEGRATION_PROFILE_ID,
    project_contract_b,
)

from claim_audit_lab.production_v1.semantic.authority import (
    AuthorityRefusal,
    complete_and_warrant,
)
from claim_audit_lab.production_v1.semantic.engine import audit
from claim_audit_lab.production_v1.semantic.measurements import measure_strict_comparison
from claim_audit_lab.production_v1.semantic.models import (
    AdmittedPassage,
    AuditContext,
    EvidenceWorld,
    SemanticFamily,
    TypedProposition,
)
from claim_audit_lab.production_v1.semantic.relations import RelationRefusal, derive_relation

CANDIDATE = "61cab64149cb6119e4dbe1fe18496f3ccf89002f"
EB_HEAD = "4e1f6fe00e7c350b28f52bfea14f1f8988847884"
B_LOCK = "c314e53bd91c0736aa4370a364673b069aceb43e"
PRESSURE_OUT = Path(os.environ.get("CAL_PRESSURE_OUT", "pressure-output"))
WHEEL_CLI = Path(os.environ["CAL_PRESSURE_CLI"])
EB_REPO = Path(os.environ["CAL_EB_INTEGRATION_REPO"]).resolve()

RESULTS: list[dict[str, Any]] = []


def tagged(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def status_for(kind: str, passed: bool) -> str:
    if passed:
        return "PASS"
    if kind == "critical":
        return "CRITICAL_FAIL"
    if kind == "robustness":
        return "ROBUSTNESS_LIMIT"
    if kind == "interface":
        return "INTERFACE_GAP"
    return "OBSERVATION"


def record(
    probe_id: str,
    kind: str,
    expected: Any,
    observed: Any,
    passed: bool,
    detail: str = "",
) -> None:
    RESULTS.append(
        {
            "probe_id": probe_id,
            "kind": kind,
            "status": status_for(kind, passed),
            "expected": expected,
            "observed": observed,
            "detail": detail,
        }
    )


def capture(probe_id: str, kind: str, expected: Any, fn: Callable[[], Any]) -> Any:
    try:
        observed = fn()
        passed = observed == expected
        record(probe_id, kind, expected, observed, passed)
        return observed
    except Exception as exc:
        record(
            probe_id,
            kind,
            expected,
            {"exception": type(exc).__name__, "message": str(exc)},
            False,
        )
        return None


def direct_context(
    family: SemanticFamily,
    fields: dict[str, str],
    texts: list[str],
    *,
    claim: str,
    bundle_id: str = "pressure-direct",
) -> AuditContext:
    passages = tuple(
        AdmittedPassage.create(
            f"p{index}",
            f"s{index}",
            text,
            source_sha256=tagged(f"source-{index}"),
        )
        for index, text in enumerate(texts, start=1)
    )
    world = EvidenceWorld.create(
        contract_b_version="1.2.0",
        bundle_id=bundle_id,
        bundle_hash=tagged(bundle_id),
        admitted_passages=passages,
        aperture_observation={
            "contract_b_factual_context_state": "present",
            "observation": {"pressure": "direct"},
        },
    )
    proposition = TypedProposition.create(
        "C1",
        family,
        fields,
        text_sha256=sha(claim),
    )
    return AuditContext(claim, proposition, world)


COMPARISON_CLAIM = "Women had a higher rate than Men."
COMPARISON_FIELDS = {
    "lhs_entity": "Women",
    "rhs_entity": "Men",
    "comparison_direction": "MORE_THAN",
}
EVENT_CLAIM = "Alice reviewed dossier before Bob archived dossier."
EVENT_FIELDS = {
    "left_subject": "alice",
    "left_predicate": "review",
    "left_object": "dossier",
    "left_polarity": "positive",
    "temporal_relation": "BEFORE",
    "right_subject": "bob",
    "right_predicate": "archive",
    "right_object": "dossier",
    "right_polarity": "positive",
}


def direct_snapshot(context: AuditContext) -> dict[str, Any]:
    result = audit(context)
    return {
        "conclusion": result.conclusion.value,
        "failure_code": None if result.failure_code is None else result.failure_code.value,
        "relations": sorted(
            {
                trace.relation.categorical_relation.value
                for trace in result.traces
                if trace.relation is not None
            }
        ),
        "trace_failures": [
            None if trace.failure_code is None else trace.failure_code.value
            for trace in result.traces
        ],
    }


def expect_direct(
    probe_id: str,
    texts: list[str],
    *,
    family: SemanticFamily,
    fields: dict[str, str],
    claim: str,
    conclusion: str,
    failure_code: str | None,
    relations: list[str],
    kind: str = "critical",
) -> dict[str, Any]:
    observed = direct_snapshot(direct_context(family, fields, texts, claim=claim))
    expected = {
        "conclusion": conclusion,
        "failure_code": failure_code,
        "relations": relations,
    }
    passed = (
        observed["conclusion"] == conclusion
        and observed["failure_code"] == failure_code
        and observed["relations"] == relations
    )
    record(probe_id, kind, expected, observed, passed)
    return observed


def robust_equivalent(
    probe_id: str,
    text: str,
    *,
    family: SemanticFamily,
    fields: dict[str, str],
    claim: str,
) -> None:
    observed = direct_snapshot(direct_context(family, fields, [text], claim=claim))
    if observed["conclusion"] == "supported":
        record(probe_id, "robustness", "supported", observed, True)
    elif observed["conclusion"] == "contradicted":
        record(
            probe_id,
            "critical",
            "supported or fail-closed",
            observed,
            False,
            "Equivalent phrasing flipped direction.",
        )
    else:
        record(
            probe_id,
            "robustness",
            "supported",
            observed,
            False,
            "Equivalent phrasing fell outside the bounded grammar.",
        )


def expect_not_terminal(probe_id: str, text: str, *, family: SemanticFamily, fields: dict[str, str], claim: str) -> None:
    observed = direct_snapshot(direct_context(family, fields, [text], claim=claim))
    passed = observed["conclusion"] == "not_checkable"
    record(
        probe_id,
        "critical",
        "not_checkable",
        observed,
        passed,
        "Scope/reporting/negative surfaces must not become support/refute.",
    )


def run_semantic_pressure() -> None:
    expect_direct(
        "CMP-01-exact-support",
        ["Women had a higher rate than Men."],
        family=SemanticFamily.STRICT_COMPARISON,
        fields=COMPARISON_FIELDS,
        claim=COMPARISON_CLAIM,
        conclusion="supported",
        failure_code=None,
        relations=["SUPPORTS"],
    )
    expect_direct(
        "CMP-02-exact-refute",
        ["Women had a lower rate than Men."],
        family=SemanticFamily.STRICT_COMPARISON,
        fields=COMPARISON_FIELDS,
        claim=COMPARISON_CLAIM,
        conclusion="contradicted",
        failure_code=None,
        relations=["REFUTES"],
    )
    expect_direct(
        "CMP-03-swapped-inverse-support",
        ["Men had a lower rate than Women."],
        family=SemanticFamily.STRICT_COMPARISON,
        fields=COMPARISON_FIELDS,
        claim=COMPARISON_CLAIM,
        conclusion="supported",
        failure_code=None,
        relations=["SUPPORTS"],
    )
    expect_direct(
        "CMP-04-mixed-relations",
        [
            "Women had a higher rate than Men.",
            "Women had a lower rate than Men.",
        ],
        family=SemanticFamily.STRICT_COMPARISON,
        fields=COMPARISON_FIELDS,
        claim=COMPARISON_CLAIM,
        conclusion="not_checkable",
        failure_code="MIXED_RELATIONS",
        relations=["REFUTES", "SUPPORTS"],
    )
    expect_direct(
        "CMP-05-unrelated-only",
        ["Quality staff inspected batch documentation."],
        family=SemanticFamily.STRICT_COMPARISON,
        fields=COMPARISON_FIELDS,
        claim=COMPARISON_CLAIM,
        conclusion="not_checkable",
        failure_code="MEASUREMENT_NOT_APPLICABLE",
        relations=[],
    )
    expect_direct(
        "EVT-01-exact-support",
        ["Alice reviewed dossier before Bob archived dossier."],
        family=SemanticFamily.DIRECT_EVENT_ORDER,
        fields=EVENT_FIELDS,
        claim=EVENT_CLAIM,
        conclusion="supported",
        failure_code=None,
        relations=["SUPPORTS"],
    )
    expect_direct(
        "EVT-02-exact-refute",
        ["Alice reviewed dossier after Bob archived dossier."],
        family=SemanticFamily.DIRECT_EVENT_ORDER,
        fields=EVENT_FIELDS,
        claim=EVENT_CLAIM,
        conclusion="contradicted",
        failure_code=None,
        relations=["REFUTES"],
    )
    expect_direct(
        "EVT-03-swapped-inverse-support",
        ["Bob archived dossier after Alice reviewed dossier."],
        family=SemanticFamily.DIRECT_EVENT_ORDER,
        fields=EVENT_FIELDS,
        claim=EVENT_CLAIM,
        conclusion="supported",
        failure_code=None,
        relations=["SUPPORTS"],
    )
    expect_direct(
        "EVT-04-mixed-relations",
        [
            "Alice reviewed dossier before Bob archived dossier.",
            "Alice reviewed dossier after Bob archived dossier.",
        ],
        family=SemanticFamily.DIRECT_EVENT_ORDER,
        fields=EVENT_FIELDS,
        claim=EVENT_CLAIM,
        conclusion="not_checkable",
        failure_code="MIXED_RELATIONS",
        relations=["REFUTES", "SUPPORTS"],
    )
    expect_direct(
        "EVT-05-negative-unresolved-precedence",
        [
            "Alice reviewed dossier before Bob archived dossier.",
            "Alice did not review dossier before Bob archived dossier.",
        ],
        family=SemanticFamily.DIRECT_EVENT_ORDER,
        fields=EVENT_FIELDS,
        claim=EVENT_CLAIM,
        conclusion="not_checkable",
        failure_code="RELATION_UNRESOLVED",
        relations=["SUPPORTS", "UNRESOLVED"],
    )

    unsupported = direct_snapshot(
        direct_context(
            SemanticFamily.PERMISSION_EXCEPTION,
            {"placeholder": "value"},
            ["Women had a higher rate than Men."],
            claim=COMPARISON_CLAIM,
        )
    )
    record(
        "SEM-01-unsupported-family",
        "critical",
        {
            "conclusion": "not_checkable",
            "failure_code": "UNSUPPORTED_SEMANTIC_FAMILY",
        },
        unsupported,
        unsupported["conclusion"] == "not_checkable"
        and unsupported["failure_code"] == "UNSUPPORTED_SEMANTIC_FAMILY",
    )

    ctx = direct_context(
        SemanticFamily.STRICT_COMPARISON,
        COMPARISON_FIELDS,
        ["Women had a higher rate than Men."],
        claim=COMPARISON_CLAIM,
    )
    receipt = measure_strict_comparison(ctx, "p1")
    foreign = direct_context(
        SemanticFamily.STRICT_COMPARISON,
        COMPARISON_FIELDS,
        ["Women had a higher rate than Men."],
        claim=COMPARISON_CLAIM,
        bundle_id="pressure-foreign",
    )
    try:
        complete_and_warrant(foreign, receipt, "p1")
    except AuthorityRefusal as exc:
        record(
            "AUTH-01-foreign-measurement-context",
            "critical",
            "AuthorityRefusal",
            {"code": exc.code, "detail": exc.detail},
            True,
        )
    else:
        record("AUTH-01-foreign-measurement-context", "critical", "AuthorityRefusal", "accepted", False)

    try:
        complete_and_warrant(ctx, replace(receipt, instrument_id="pressure-forged"), "p1")
    except AuthorityRefusal as exc:
        record(
            "AUTH-02-forged-instrument-id",
            "critical",
            "AuthorityRefusal",
            {"code": exc.code, "detail": exc.detail},
            True,
        )
    else:
        record("AUTH-02-forged-instrument-id", "critical", "AuthorityRefusal", "accepted", False)

    authority = complete_and_warrant(ctx, receipt, "p1")
    try:
        derive_relation(ctx, replace(authority, authority_id="semantic-authority:" + "0" * 64))
    except RelationRefusal as exc:
        record(
            "AUTH-03-forged-authority-id",
            "critical",
            "RelationRefusal",
            {"code": exc.code, "detail": exc.detail},
            True,
        )
    else:
        record("AUTH-03-forged-authority-id", "critical", "RelationRefusal", "accepted", False)

    for suffix, text in (
        ("higher", "Women had a higher rate than Men."),
        ("greater", "Women had a greater rate than Men."),
        ("larger", "Women had a larger rate than Men."),
        ("exceeded", "Women exceeded Men."),
        ("swapped-lower", "Men had a lower rate than Women."),
        ("uppercase-cue", "Women had a HIGHER rate than Men."),
        ("post-noun-cue", "Women had a rate higher than Men."),
        ("plural-measure", "Women had higher rates than Men."),
        ("lowercase-entities", "women had a higher rate than men."),
        ("article-right", "Women had a higher rate than the Men."),
        ("temporal-tail", "Women had a higher rate than Men in 2025."),
    ):
        robust_equivalent(
            f"ROB-CMP-{suffix}",
            text,
            family=SemanticFamily.STRICT_COMPARISON,
            fields=COMPARISON_FIELDS,
            claim=COMPARISON_CLAIM,
        )

    expect_not_terminal(
        "ROB-CMP-reporting-prefix",
        "Study reported Women had a higher rate than Men.",
        family=SemanticFamily.STRICT_COMPARISON,
        fields=COMPARISON_FIELDS,
        claim=COMPARISON_CLAIM,
    )

    for suffix, text in (
        ("exact", "Alice reviewed dossier before Bob archived dossier."),
        ("swapped-after", "Bob archived dossier after Alice reviewed dossier."),
        ("article-objects", "Alice reviewed the dossier before Bob archived the dossier."),
        ("lowercase-actors", "alice reviewed dossier before bob archived dossier."),
        ("comma-cue", "Alice reviewed dossier, before Bob archived dossier."),
    ):
        robust_equivalent(
            f"ROB-EVT-{suffix}",
            text,
            family=SemanticFamily.DIRECT_EVENT_ORDER,
            fields=EVENT_FIELDS,
            claim=EVENT_CLAIM,
        )

    expect_not_terminal(
        "ROB-EVT-reporting-prefix",
        "Study reported Alice reviewed dossier before Bob archived dossier.",
        family=SemanticFamily.DIRECT_EVENT_ORDER,
        fields=EVENT_FIELDS,
        claim=EVENT_CLAIM,
    )
    expect_not_terminal(
        "ROB-EVT-negative",
        "Alice did not review dossier before Bob archived dossier.",
        family=SemanticFamily.DIRECT_EVENT_ORDER,
        fields=EVENT_FIELDS,
        claim=EVENT_CLAIM,
    )

    start = time.perf_counter()
    for _ in range(500):
        result = audit(ctx)
        if result.conclusion.value != "supported":
            raise AssertionError(result)
    elapsed = time.perf_counter() - start
    record(
        "OBS-01-direct-throughput-500",
        "observation",
        "record elapsed seconds",
        {"seconds": round(elapsed, 6), "audits_per_second": round(500 / elapsed, 2)},
        False,
    )


C1_TEXT = "Alpha had a higher rate than Beta."
C1_REFUTE_TEXT = "Alpha had a lower rate than Beta."
C2_TEXT = "Alice reviewed dossier before Bob archived dossier."
ROOT_TEXT = (
    "Alpha had a higher rate than Beta, and Alice reviewed dossier before Bob archived dossier."
)
SOURCES = (
    ("S-C1-SUPPORT", C1_TEXT),
    ("S-C1-REFUTE", C1_REFUTE_TEXT),
    ("S-C2-SUPPORT", C2_TEXT),
    ("S-D01", "Alpha calibration records describe sampling frequency."),
    ("S-D02", "Beta calibration records describe sampling frequency."),
    ("S-D03", "Alice prepared the dossier for review."),
    ("S-D04", "Bob stored archival metadata for the dossier."),
    ("S-D05", "Gamma had a higher output than Delta."),
    ("S-D06", "Quality staff inspected batch documentation."),
    ("S-D07", "The archive contains unrelated maintenance notes."),
)


def contract_a() -> dict[str, Any]:
    value: dict[str, Any] = {
        "schema": "contract-a-wire-candidate-rc2",
        "handoff_id": "cal-v1-pressure-20260919",
        "producer": {"producer_id": "cal-v1-pressure", "producer_version": "research"},
        "work": {"work_id": "cal-v1-slice1-pressure"},
        "root_proposition": {
            "proposition_id": "ROOT",
            "text": ROOT_TEXT,
            "text_sha256": tagged(ROOT_TEXT),
        },
        "decomposition": {
            "state": "declared",
            "decomposition_id": "D-PRESSURE",
            "operator": "all_of",
            "children": [
                {
                    "proposition_id": "C1",
                    "text": C1_TEXT,
                    "text_sha256": tagged(C1_TEXT),
                    "sequence": 1,
                },
                {
                    "proposition_id": "C2",
                    "text": C2_TEXT,
                    "text_sha256": tagged(C2_TEXT),
                    "sequence": 2,
                },
            ],
        },
        "sources": [
            {
                "source_id": source_id,
                "media_type": "text/plain; charset=utf-8",
                "content": text,
                "content_sha256": tagged(text),
            }
            for source_id, text in SOURCES
        ],
        "handoff_sha256": "sha256:" + "0" * 64,
    }
    value["handoff_sha256"] = compute_handoff_sha256(value)
    return value


def carrier() -> dict[str, Any]:
    return json.loads(
        (
            EB_REPO
            / "research"
            / "eb_v1_integration_candidate"
            / "contract_b_compatibility_carrier.json"
        ).read_text(encoding="utf-8")
    )


def initial_package() -> dict[str, Any]:
    package = build_package(contract_a=contract_a(), config=INTEGRATION_CONFIG)
    assert package["config_sha256"] == INTEGRATION_CONFIG_SHA256
    assert INTEGRATION_PROFILE_ID == "eb-v1-integration-10x3-rc0"
    return package


def retained_id(initial: dict[str, Any], source_id: str) -> str:
    rows = [
        row
        for row in initial["candidates"]
        if row["proposition_id"] == "C1"
        and row["source_id"] == source_id
        and row["selection_state"] == "retained"
    ]
    assert len(rows) == 1, (source_id, rows)
    return str(rows[0]["passage_id"])


def build_bundle(root: Path, source_id: str) -> Path:
    initial = initial_package()
    package = build_package(
        contract_a=contract_a(),
        config=INTEGRATION_CONFIG,
        admission={("C1", retained_id(initial, source_id)): "accepted"},
    )
    receipt = project_contract_b(
        package=package,
        compatibility_carrier=carrier(),
        out_dir=root,
    )
    assert receipt["contract_b_authority"] == {
        "version": "1.2.0",
        "production_lock": B_LOCK,
    }
    return root / "contract_b"


def target(fields: dict[str, str] | None = None, *, text_hash: str | None = None) -> dict[str, Any]:
    return {
        "claim_id": "C1",
        "proposition": {
            "proposition_id": "C1",
            "text_sha256": text_hash or sha(C1_TEXT),
            "semantic_family": "strict_comparison",
            "fields": fields or {
                "lhs_entity": "Alpha",
                "rhs_entity": "Beta",
                "comparison_direction": "MORE_THAN",
            },
        },
    }


def write_json(path: Path, value: Any, *, pretty: bool = False) -> None:
    if pretty:
        path.write_text(json.dumps(value, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    else:
        path.write_text(
            json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )


def cli(prefix: list[str], *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [*prefix, *args],
        text=True,
        capture_output=True,
        check=False,
    )


def read_result(out_dir: Path) -> dict[str, Any]:
    return json.loads((out_dir / "result.json").read_text(encoding="utf-8"))


def dir_bytes(path: Path) -> dict[str, bytes]:
    return {
        p.relative_to(path).as_posix(): p.read_bytes()
        for p in sorted(path.rglob("*"))
        if p.is_file()
    }


def run_real_pipeline_pressure() -> None:
    actual_eb = subprocess.check_output(
        ["git", "-C", str(EB_REPO), "rev-parse", "HEAD"], text=True
    ).strip()
    capture("XREPO-01-exact-eb-head", "critical", EB_HEAD, lambda: actual_eb)
    capture("XREPO-02-contract-b-lock", "critical", B_LOCK, lambda: CONTRACT_B_PRODUCTION_LOCK)

    root = PRESSURE_OUT / "work"
    root.mkdir(parents=True, exist_ok=True)
    support_bundle = build_bundle(root / "support-eb", "S-C1-SUPPORT")
    refute_bundle = build_bundle(root / "refute-eb", "S-C1-REFUTE")
    target_path = root / "target.json"
    write_json(target_path, target())

    wheel_prefix = [str(WHEEL_CLI)]
    source_prefix = [sys.executable, "-m", "claim_audit_lab.production_v1.bundle_cli"]

    inspect = cli(wheel_prefix, "inspect", "--json")
    try:
        inspect_json = json.loads(inspect.stdout)
    except Exception:
        inspect_json = {"stdout": inspect.stdout, "stderr": inspect.stderr}
    inspect_pass = (
        inspect.returncode == 0
        and inspect_json.get("distribution_version") == "0.6.0"
        and inspect_json.get("authorization", {}).get("automatic_action_allowed") is False
        and inspect_json.get("supported_semantic_families")
        == ["strict_comparison", "direct_event_order"]
    )
    record(
        "CLI-01-inspect-authority",
        "critical",
        {
            "distribution_version": "0.6.0",
            "automatic_action_allowed": False,
            "families": ["strict_comparison", "direct_event_order"],
        },
        {"returncode": inspect.returncode, "record": inspect_json},
        inspect_pass,
    )

    for case, bundle, expected, relation in (
        ("support", support_bundle, "supported", "SUPPORTS"),
        ("refute", refute_bundle, "contradicted", "REFUTES"),
    ):
        valid = cli(wheel_prefix, "validate-bundle", str(bundle), str(target_path))
        out = root / f"wheel-{case}"
        run = cli(wheel_prefix, "run-bundle", str(bundle), str(target_path), "--out-dir", str(out))
        observed: dict[str, Any] = {
            "validate_rc": valid.returncode,
            "run_rc": run.returncode,
            "validate_stdout": valid.stdout.strip(),
            "run_stderr": run.stderr.strip(),
        }
        if run.returncode == 0:
            rec = read_result(out)
            observed.update(
                {
                    "conclusion": rec["result"]["conclusion"],
                    "failure_code": rec["result"]["failure_code"],
                    "relations": rec["composition"]["relation_categories"],
                    "input_mode": rec["input"]["mode"],
                }
            )
        passed = (
            valid.returncode == 0
            and valid.stdout.strip() == "VALID"
            and run.returncode == 0
            and observed.get("conclusion") == expected
            and observed.get("failure_code") is None
            and observed.get("relations") == [relation]
            and observed.get("input_mode") == "contract_b_bundle"
        )
        record(
            f"CLI-02-real-{case}",
            "critical",
            {"conclusion": expected, "relation": relation, "input_mode": "contract_b_bundle"},
            observed,
            passed,
        )

    replay_a = root / "replay-a"
    replay_b = root / "replay-b"
    ra = cli(wheel_prefix, "run-bundle", str(support_bundle), str(target_path), "--out-dir", str(replay_a))
    rb = cli(wheel_prefix, "run-bundle", str(support_bundle), str(target_path), "--out-dir", str(replay_b))
    same = ra.returncode == rb.returncode == 0 and dir_bytes(replay_a) == dir_bytes(replay_b)
    record(
        "DET-01-byte-replay",
        "critical",
        "byte-identical directories",
        {"rc_a": ra.returncode, "rc_b": rb.returncode, "equal": same},
        same,
    )

    source_out = root / "source-equivalence"
    wheel_out = root / "wheel-equivalence"
    rs = cli(source_prefix, "run-bundle", str(support_bundle), str(target_path), "--out-dir", str(source_out))
    rw = cli(wheel_prefix, "run-bundle", str(support_bundle), str(target_path), "--out-dir", str(wheel_out))
    eq = rs.returncode == rw.returncode == 0 and dir_bytes(source_out) == dir_bytes(wheel_out)
    record(
        "DET-02-source-wheel-equivalence",
        "critical",
        "byte-identical directories",
        {"source_rc": rs.returncode, "wheel_rc": rw.returncode, "equal": eq},
        eq,
    )

    pretty_target = root / "target-pretty.json"
    write_json(pretty_target, target(), pretty=True)
    pretty_out = root / "pretty-target"
    rp = cli(wheel_prefix, "run-bundle", str(support_bundle), str(pretty_target), "--out-dir", str(pretty_out))
    if rp.returncode == 0:
        canonical_rec = read_result(replay_a)
        pretty_rec = read_result(pretty_out)
        observed = {
            "canonical_conclusion": canonical_rec["result"]["conclusion"],
            "pretty_conclusion": pretty_rec["result"]["conclusion"],
            "canonical_context": canonical_rec["evidence_world"]["audit_context_sha256"],
            "pretty_context": pretty_rec["evidence_world"]["audit_context_sha256"],
            "primary_input_hash_equal": (
                canonical_rec["input"]["primary_input_sha256"]
                == pretty_rec["input"]["primary_input_sha256"]
            ),
        }
        passed = (
            observed["canonical_conclusion"] == observed["pretty_conclusion"] == "supported"
            and observed["canonical_context"] == observed["pretty_context"]
            and observed["primary_input_hash_equal"] is False
        )
    else:
        observed = {"returncode": rp.returncode, "stderr": rp.stderr}
        passed = False
    record(
        "DET-03-target-format-metamorphism",
        "critical",
        "same semantic context/conclusion; different exact input hash",
        observed,
        passed,
    )

    manifest = json.loads((replay_a / "manifest.json").read_text(encoding="utf-8"))
    mismatches = []
    for name, expected_hash in manifest["files"].items():
        actual = "sha256:" + hashlib.sha256((replay_a / name).read_bytes()).hexdigest()
        if actual != expected_hash:
            mismatches.append({"file": name, "expected": expected_hash, "actual": actual})
    record(
        "ART-01-manifest-hashes",
        "critical",
        "all emitted artifact hashes match",
        mismatches,
        not mismatches,
    )

    # Target binding / parser pressure.
    bad_hash = root / "bad-hash.json"
    write_json(bad_hash, target(text_hash="0" * 64))
    proc = cli(wheel_prefix, "validate-bundle", str(support_bundle), str(bad_hash))
    record("TGT-01-text-hash-mismatch", "critical", "reject", proc.returncode, proc.returncode != 0)

    mismatch = target()
    mismatch["proposition"]["proposition_id"] = "C2"
    mismatch_path = root / "id-mismatch.json"
    write_json(mismatch_path, mismatch)
    proc = cli(wheel_prefix, "validate-bundle", str(support_bundle), str(mismatch_path))
    record("TGT-02-proposition-id-mismatch", "critical", "reject", proc.returncode, proc.returncode != 0)

    unknown = target()
    unknown["proposition"]["semantic_family"] = "made_up_family"
    unknown_path = root / "unknown-family.json"
    write_json(unknown_path, unknown)
    proc = cli(wheel_prefix, "validate-bundle", str(support_bundle), str(unknown_path))
    record("TGT-03-unknown-family", "critical", "reject", proc.returncode, proc.returncode != 0)

    duplicate_path = root / "duplicate-key.json"
    duplicate_path.write_text(
        '{"claim_id":"C1","claim_id":"C1","proposition":'
        + json.dumps(target()["proposition"], separators=(",", ":"))
        + "}\n",
        encoding="utf-8",
    )
    proc = cli(wheel_prefix, "validate-bundle", str(support_bundle), str(duplicate_path))
    record("TGT-04-duplicate-json-key", "critical", "reject", proc.returncode, proc.returncode != 0)

    for suffix, fields in (
        ("missing-fields", {"lhs_entity": "Alpha"}),
        (
            "bad-direction",
            {
                "lhs_entity": "Alpha",
                "rhs_entity": "Beta",
                "comparison_direction": "SIDEWAYS",
            },
        ),
    ):
        path = root / f"{suffix}.json"
        write_json(path, target(fields))
        validation = cli(wheel_prefix, "validate-bundle", str(support_bundle), str(path))
        if validation.returncode != 0:
            record(
                f"IFACE-{suffix}",
                "interface",
                "early reject or fail-closed execution",
                {"validate_rc": validation.returncode, "outcome": "early_reject"},
                True,
            )
            continue
        out = root / f"{suffix}-out"
        run = cli(wheel_prefix, "run-bundle", str(support_bundle), str(path), "--out-dir", str(out))
        observed: dict[str, Any] = {"validate_rc": validation.returncode, "run_rc": run.returncode}
        if run.returncode == 0:
            rec = read_result(out)
            observed.update(
                {
                    "conclusion": rec["result"]["conclusion"],
                    "failure_code": rec["result"]["failure_code"],
                }
            )
        safe = (
            run.returncode == 0
            and observed.get("conclusion") == "not_checkable"
            and observed.get("failure_code") == "PROPOSITION_BINDING_FAILED"
        )
        if safe:
            record(
                f"IFACE-{suffix}",
                "interface",
                "validate-bundle rejects semantically malformed active-family fields",
                observed,
                False,
                "Execution fails closed, but validation accepted the malformed semantic target.",
            )
        else:
            record(
                f"IFACE-{suffix}",
                "critical",
                "early reject or not_checkable / PROPOSITION_BINDING_FAILED",
                observed,
                False,
                "Malformed active-family target did not fail closed in the expected way.",
            )

    # Bundle integrity pressure.
    passage_mut = root / "bundle-passage-mut"
    shutil.copytree(support_bundle, passage_mut)
    passage = next(passage_mut.glob("evidence/*/passages/*.yaml"))
    passage.write_text(passage.read_text(encoding="utf-8") + "\n# pressure mutation\n", encoding="utf-8")
    proc = cli(wheel_prefix, "validate-bundle", str(passage_mut), str(target_path))
    record("BND-01-passage-byte-mutation", "critical", "reject", proc.returncode, proc.returncode != 0)

    missing_version = root / "bundle-missing-version"
    shutil.copytree(support_bundle, missing_version)
    (missing_version / "CONTRACT_VERSION").unlink()
    proc = cli(wheel_prefix, "validate-bundle", str(missing_version), str(target_path))
    record("BND-02-missing-contract-version", "critical", "reject", proc.returncode, proc.returncode != 0)

    escape = root / "bundle-sha-path-escape"
    shutil.copytree(support_bundle, escape)
    sums = escape / "SHA256SUMS"
    sums.write_text(("0" * 64) + "  ../escape.txt\n" + sums.read_text(encoding="utf-8"), encoding="utf-8")
    proc = cli(wheel_prefix, "validate-bundle", str(escape), str(target_path))
    record("BND-03-sha-path-traversal", "critical", "reject", proc.returncode, proc.returncode != 0)

    # Output safety.
    nonempty = root / "nonempty-output"
    nonempty.mkdir()
    sentinel = nonempty / "sentinel.txt"
    sentinel.write_text("keep", encoding="utf-8")
    proc = cli(wheel_prefix, "run-bundle", str(support_bundle), str(target_path), "--out-dir", str(nonempty))
    record(
        "OUT-01-nonempty-refusal",
        "critical",
        "reject without mutation",
        {"returncode": proc.returncode, "sentinel": sentinel.read_text(encoding="utf-8")},
        proc.returncode != 0 and sentinel.read_text(encoding="utf-8") == "keep",
    )

    file_out = root / "file-output"
    file_out.write_text("keep", encoding="utf-8")
    proc = cli(wheel_prefix, "run-bundle", str(support_bundle), str(target_path), "--out-dir", str(file_out))
    record(
        "OUT-02-file-path-refusal",
        "critical",
        "reject without mutation",
        {"returncode": proc.returncode, "content": file_out.read_text(encoding="utf-8")},
        proc.returncode != 0 and file_out.read_text(encoding="utf-8") == "keep",
    )

    real_dir = root / "symlink-real"
    real_dir.mkdir()
    symlink = root / "symlink-output"
    symlink.symlink_to(real_dir, target_is_directory=True)
    proc = cli(wheel_prefix, "run-bundle", str(support_bundle), str(target_path), "--out-dir", str(symlink))
    record(
        "OUT-03-symlink-refusal",
        "critical",
        "reject",
        {"returncode": proc.returncode, "real_dir_files": list(real_dir.iterdir())},
        proc.returncode != 0 and not list(real_dir.iterdir()),
    )

    # Concurrency.
    distinct_a = root / "concurrent-a"
    distinct_b = root / "concurrent-b"
    pa = subprocess.Popen(
        [*wheel_prefix, "run-bundle", str(support_bundle), str(target_path), "--out-dir", str(distinct_a)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    pb = subprocess.Popen(
        [*wheel_prefix, "run-bundle", str(support_bundle), str(target_path), "--out-dir", str(distinct_b)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    pa.communicate()
    pb.communicate()
    passed = pa.returncode == pb.returncode == 0 and dir_bytes(distinct_a) == dir_bytes(distinct_b)
    record(
        "CONC-01-distinct-output",
        "critical",
        "both succeed with identical bytes",
        {"rc_a": pa.returncode, "rc_b": pb.returncode, "equal": passed},
        passed,
    )

    same = root / "concurrent-same"
    p1 = subprocess.Popen(
        [*wheel_prefix, "run-bundle", str(support_bundle), str(target_path), "--out-dir", str(same)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    p2 = subprocess.Popen(
        [*wheel_prefix, "run-bundle", str(support_bundle), str(target_path), "--out-dir", str(same)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    p1.communicate()
    p2.communicate()
    leftovers = list(root.glob(".concurrent-same.tmp-*"))
    valid_output = (same / "result.json").is_file() and read_result(same)["result"]["conclusion"] == "supported"
    one_writer = sorted([p1.returncode, p2.returncode]).count(0) == 1
    record(
        "CONC-02-same-output-contention",
        "critical",
        "exactly one writer; valid final output; no temp leftovers",
        {
            "returncodes": [p1.returncode, p2.returncode],
            "valid_output": valid_output,
            "temp_leftovers": [p.name for p in leftovers],
        },
        one_writer and valid_output and not leftovers,
    )


def write_outputs() -> None:
    PRESSURE_OUT.mkdir(parents=True, exist_ok=True)
    counts: dict[str, int] = {}
    for row in RESULTS:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    payload = {
        "schema": "cal-v1-slice1-pressure-results-v1",
        "subject_commit": CANDIDATE,
        "evidence_bundler_head": EB_HEAD,
        "contract_b_lock": B_LOCK,
        "counts": counts,
        "results": RESULTS,
    }
    (PRESSURE_OUT / "pressure-results.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# CAL V1 Slice 1 pressure-test results",
        "",
        f"- subject: \`{CANDIDATE}\`",
        f"- counts: \`{json.dumps(counts, sort_keys=True)}\`",
        "",
        "| Probe | Status | Expected | Observed |",
        "|---|---|---|---|",
    ]
    for row in RESULTS:
        expected = json.dumps(row["expected"], sort_keys=True, ensure_ascii=False).replace("|", "\\|")
        observed = json.dumps(row["observed"], sort_keys=True, ensure_ascii=False).replace("|", "\\|")
        lines.append(f"| {row['probe_id']} | {row['status']} | {expected} | {observed} |")
    (PRESSURE_OUT / "pressure-summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


def main() -> int:
    run_semantic_pressure()
    run_real_pipeline_pressure()
    write_outputs()
    return 1 if any(row["status"] == "CRITICAL_FAIL" for row in RESULTS) else 0


if __name__ == "__main__":
    raise SystemExit(main())
