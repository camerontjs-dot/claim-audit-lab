"""Decisive pressure runner for the frozen CAL polarity successor.

The matrix, cohort, and this file are frozen before execution. The runner does
not repair the candidate, rewrite expectations, or replace a preserved output.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import traceback
from pathlib import Path
from typing import Any

CAMPAIGN = Path(__file__).resolve().parent
REPO = CAMPAIGN.parents[1]
sys.path.insert(0, str(REPO / "src"))

from weak_systems import (  # noqa: E402
    collapse_scoped_comparison,
    ignore_assertion_polarity,
    resolver_identity_wildcard,
    structural_target_ok,
)

SUBJECT = "64b6c7702696c851057c1cf0b2c105b1c81db543"
SEMANTIC = "caa0048f8f511ec3c4aa1ce713766f2219a04bc1"
PINNED_SHA = "sha256:" + "11" * 32


def _tagged(repeat: str) -> str:
    return "sha256:" + (repeat * 64)[:64]


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _public(value: object) -> str:
    text = str(value)
    for marker in ("/Users/", "/private/", "/var/folders/", "/tmp/"):
        while marker in text:
            start = text.index(marker)
            end = start
            while end < len(text) and text[end] not in " '\"\n\t,":
                end += 1
            text = text[:start] + "<local-path>" + text[end:]
    return text


def _git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(REPO), *args], text=True).strip()


def _load(name: str) -> dict[str, Any]:
    return json.loads((CAMPAIGN / name).read_text(encoding="utf-8"))


def _apparatus_repo() -> Path:
    for parent in [REPO, *REPO.parents]:
        candidate = parent / "30_projects" / "apparatus-contracts" / "workbench"
        if candidate.is_dir():
            return candidate
    raise RuntimeError("apparatus workbench unavailable")


def _assert_frozen_blobs() -> str | None:
    freeze = _load("HARNESS_FREEZE.json")
    blobs = freeze.get("blobs")
    if not isinstance(blobs, dict) or not blobs:
        return "harness freeze has no blobs"
    for name, expected in blobs.items():
        path = CAMPAIGN / name
        if not path.is_file():
            return f"frozen file missing: {name}"
        observed = subprocess.check_output(["git", "hash-object", str(path)], text=True).strip()
        if observed != expected:
            return f"frozen blob drift: {name}"
    return None


def _conclusion_for(claim: str, evidence: list[str], source_sha256: str | None = None) -> dict[str, Any]:
    from claim_audit_lab.production_v1.semantic.engine import audit
    from claim_audit_lab.production_v1.semantic.models import (
        AdmittedPassage,
        AuditContext,
        EvidenceWorld,
        SemanticFamily,
    )
    from claim_audit_lab.production_v1.targeting import TargetAuthoringError, author_target

    try:
        target = author_target("probe", claim)
    except TargetAuthoringError as exc:
        return {"authoring": "refused", "detail": _public(exc), "conclusion": None}
    family = SemanticFamily(target["proposition"]["semantic_family"])
    passages = []
    for index, text in enumerate(evidence):
        passages.append(
            AdmittedPassage.create(
                f"p{index}",
                f"s{index}",
                text,
                source_sha256 or ("sha256:" + _sha256(f"source-{index}".encode())),
            )
        )
    world = EvidenceWorld.create(
        "1.2.0",
        "cal-v1-pressure-rc0",
        "sha256:" + _sha256(b"cal-v1-pressure-rc0"),
        tuple(passages),
        {"contract_b_factual_context_state": "present", "campaign": "polarity-successor-pressure-rc0"},
    )
    result = audit(AuditContext(claim, _proposition(target), world))
    return {
        "authoring": "authored",
        "family": family.value,
        "fields": target["proposition"]["fields"],
        "conclusion": result.conclusion.value,
        "failure_code": None if result.failure_code is None else result.failure_code.value,
        "trace_count": len(result.traces),
    }


def _proposition(target: dict[str, Any]):
    from claim_audit_lab.production_v1.semantic.models import SemanticFamily, TypedProposition

    proposition = target["proposition"]
    return TypedProposition.create(
        proposition["proposition_id"],
        SemanticFamily(proposition["semantic_family"]),
        proposition["fields"],
        text_sha256=proposition["text_sha256"],
    )


def _classify_semantic(case: dict[str, Any], observed: dict[str, Any]) -> dict[str, Any]:
    kind = case["expected_kind"]
    if kind == "authoring_refusal":
        if observed["authoring"] == "refused":
            classification = case["match_class"]
        elif observed["conclusion"] in case["critical_conclusions"]:
            classification = "CRITICAL_FAIL"
        else:
            classification = "CRITICAL_FAIL" if observed["conclusion"] in {"supported", "contradicted"} else "DEVIATION"
        return {**observed, "case_id": case["case_id"], "classification": classification, "note": case["note"]}
    conclusion = observed.get("conclusion")
    if observed["authoring"] == "refused":
        classification = "AUTHORING_LIMIT"
    elif conclusion == case["expected_conclusion"]:
        classification = case["match_class"]
    elif conclusion in case["critical_conclusions"]:
        classification = "CRITICAL_FAIL"
    elif conclusion == "not_checkable" and case.get("not_checkable_class"):
        classification = case["not_checkable_class"]
    elif conclusion in {"supported", "contradicted"}:
        classification = "CRITICAL_FAIL"
    else:
        classification = "DEVIATION"
    return {
        **observed,
        "case_id": case["case_id"],
        "expected_conclusion": case["expected_conclusion"],
        "classification": classification,
        "note": case["note"],
    }


def _run_semantic(matrix: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for case in matrix["cases"]:
        if case["expected_kind"] == "authoring_refusal":
            observed = _conclusion_for(case["claim"], ["Alpha had a higher rate than Beta."])
            observed["evidence_not_used"] = True
        else:
            observed = _conclusion_for(case["claim"], case["evidence"], case.get("source_sha256"))
        rows.append(_classify_semantic(case, observed))
    by_id = {row["case_id"]: row for row in rows}
    if "SC-ORDER-A" in by_id and "SC-ORDER-B" in by_id:
        same = by_id["SC-ORDER-A"].get("conclusion") == by_id["SC-ORDER-B"].get("conclusion")
        if not same:
            for case_id in ("SC-ORDER-A", "SC-ORDER-B"):
                by_id[case_id]["classification"] = "CRITICAL_FAIL"
                by_id[case_id]["order_nondeterminism"] = True
        else:
            by_id["SC-ORDER-A"]["order_match"] = True
            by_id["SC-ORDER-B"]["order_match"] = True
    return rows


def _authority_rows() -> list[dict[str, Any]]:
    from claim_audit_lab.production_v1.parent_bound import (
        ParentBoundPipelineError,
        _load_authority_modules,
        verify_external_authorities,
    )
    from claim_audit_lab.production_v1.semantic.decomposition import (
        BoundAuditOutcome,
        Conclusion,
        DecompositionDeclaration,
        DecompositionRefusal,
        DecompositionState,
        PropositionRef,
        recompose,
    )
    from claim_audit_lab.production_v1.semantic.engine import audit, compose
    from claim_audit_lab.production_v1.semantic.models import (
        AdmittedPassage,
        AuditContext,
        EvidenceWorld,
    )
    from claim_audit_lab.production_v1.targeting import author_target

    rows: list[dict[str, Any]] = []

    def add(case_id: str, classification: str, detail: str) -> None:
        rows.append({"case_id": case_id, "classification": classification, "detail": _public(detail)})

    target = author_target("auth", "Alpha had a higher rate than Beta.")
    proposition = _proposition(target)
    good = AdmittedPassage.create("p0", "s0", "Alpha had a higher rate than Beta.")
    broken = AdmittedPassage(
        good.passage_id,
        good.source_id,
        good.text,
        "sha256:" + "00" * 32,
        good.source_sha256,
    )
    try:
        EvidenceWorld.create(
            "1.2.0",
            "world-a",
            PINNED_SHA,
            (broken,),
            {"contract_b_factual_context_state": "present"},
        ).verify()
        audit_context_error = "passage hash mutation was accepted"
        add("AUTH-PASSAGE-HASH", "CRITICAL_FAIL", audit_context_error)
    except ValueError as exc:
        add("AUTH-PASSAGE-HASH", "PASS", exc)

    substituted = AdmittedPassage.create("p0", "s0", good.text, "sha256:" + "22" * 32)
    world = EvidenceWorld.create(
        "1.2.0",
        "world-a",
        PINNED_SHA,
        (substituted,),
        {"contract_b_factual_context_state": "present"},
    )
    decided = audit(AuditContext(target["claim_id"], proposition, world))
    if decided.conclusion.value in {"supported", "contradicted", "not_checkable"}:
        add("AUTH-SOURCE-HASH-UNBOUND", "INTERFACE_GAP", f"source hash substitution still decided {decided.conclusion.value}")
    else:
        add("AUTH-SOURCE-HASH-UNBOUND", "DEVIATION", decided.conclusion.value)

    other = EvidenceWorld.create(
        "1.2.0",
        "world-b",
        "sha256:" + "33" * 32,
        (AdmittedPassage.create("p0", "s0", good.text),),
        {"contract_b_factual_context_state": "present"},
    )
    first = audit(AuditContext("Alpha had a higher rate than Beta.", proposition, world))
    try:
        compose(AuditContext("Alpha had a higher rate than Beta.", proposition, other), first.traces)
        add("AUTH-CROSS-WORLD", "CRITICAL_FAIL", "cross-world traces composed")
    except Exception as exc:
        add("AUTH-CROSS-WORLD", "PASS", type(exc).__name__ + ": " + _public(exc))

    child_a = BoundAuditOutcome.create(
        proposition_id="c1",
        text_sha256=_tagged("a"),
        audit_result_sha256=_tagged("b"),
        conclusion=Conclusion.SUPPORTED,
    )
    child_b = BoundAuditOutcome.create(
        proposition_id="c2",
        text_sha256=_tagged("c"),
        audit_result_sha256=_tagged("d"),
        conclusion=Conclusion.SUPPORTED,
    )
    declaration = DecompositionDeclaration(
        root=PropositionRef("root", _tagged("e")),
        state=DecompositionState.DECLARED,
        decomposition_id="pressure-all-of",
        operator="all_of",
        children=(
            PropositionRef("c1", _tagged("a"), 1),
            PropositionRef("c2", _tagged("c"), 2),
        ),
    )
    stale = BoundAuditOutcome.create(
        proposition_id="c1",
        text_sha256=_tagged("f"),
        audit_result_sha256=_tagged("b"),
        conclusion=Conclusion.SUPPORTED,
    )
    for case_id, outcomes, expected in (
        ("AUTH-STALE-CHILD", (stale, child_b), "CHILD_TEXT_BINDING_MISMATCH"),
        ("AUTH-MISSING-CHILD", (child_a,), "MISSING_CHILD_RESULT"),
        ("AUTH-EXTRA-CHILD", (child_a, child_b, BoundAuditOutcome.create(proposition_id="c3", text_sha256=_tagged("1"), audit_result_sha256=_tagged("2"), conclusion=Conclusion.NOT_CHECKABLE)), "EXTRA_CHILD_RESULT"),
    ):
        try:
            recompose(declaration, child_outcomes=outcomes)
            add(case_id, "CRITICAL_FAIL", "recomposed without rejection")
        except DecompositionRefusal as exc:
            add(case_id, "PASS" if exc.code == expected else "DEVIATION", exc.code)

    stolen = BoundAuditOutcome(
        proposition_id="c2",
        text_sha256=_tagged("c"),
        audit_result_sha256=_tagged("d"),
        conclusion=Conclusion.SUPPORTED,
        result_id=child_a.result_id,
    )
    try:
        recompose(declaration, child_outcomes=(child_a, stolen))
        add("AUTH-REPLAY-RESULT-ID", "CRITICAL_FAIL", "reused result id composed")
    except DecompositionRefusal as exc:
        add("AUTH-REPLAY-RESULT-ID", "PASS", exc.code)

    bad_sequence = DecompositionDeclaration(
        root=PropositionRef("root", _tagged("e")),
        state=DecompositionState.DECLARED,
        decomposition_id="pressure-all-of",
        operator="all_of",
        children=(
            PropositionRef("c1", _tagged("a"), 2),
            PropositionRef("c2", _tagged("c"), 1),
        ),
    )
    try:
        recompose(bad_sequence, child_outcomes=(child_a, child_b))
        add("AUTH-CHILD-SEQUENCE", "CRITICAL_FAIL", "bad child sequence composed")
    except DecompositionRefusal as exc:
        add("AUTH-CHILD-SEQUENCE", "PASS", exc.code)

    forward = recompose(declaration, child_outcomes=(child_a, child_b))
    backward = recompose(declaration, child_outcomes=(child_b, child_a))
    same = forward.conclusion == backward.conclusion
    add("AUTH-CHILD-SUPPLY-ORDER", "PASS" if same else "CRITICAL_FAIL", forward.conclusion.value)

    try:
        EvidenceWorld.create("", "world-a", PINNED_SHA, (good,), {"contract_b_factual_context_state": "present"}).verify()
        add("AUTH-MISSING-VERSION", "CRITICAL_FAIL", "empty version accepted")
    except ValueError as exc:
        add("AUTH-MISSING-VERSION", "PASS", exc)

    extra_world = EvidenceWorld.create(
        "1.2.0",
        "world-a",
        PINNED_SHA,
        (good,),
        {"contract_b_factual_context_state": "present", "unknown_state": "extra"},
    )
    extra_result = audit(AuditContext("Alpha had a higher rate than Beta.", proposition, extra_world))
    add(
        "AUTH-EXTRA-APERTURE",
        "INTERFACE_GAP",
        f"unknown aperture state decided {extra_result.conclusion.value}",
    )

    apparatus = _apparatus_repo()
    try:
        verify_external_authorities(
            contract_c_root=apparatus,
            rc2_root=apparatus,
            resolver_root=apparatus,
        )
        add("AUTH-WRONG-CONTRACT-C", "CRITICAL_FAIL", "live apparatus HEAD verified as pinned Contract C")
        add("AUTH-WRONG-RESOLVER", "CRITICAL_FAIL", "live apparatus HEAD verified as pinned resolver")
    except ParentBoundPipelineError as exc:
        detail = _public(exc)
        add("AUTH-WRONG-CONTRACT-C", "PASS", detail)
        add("AUTH-WRONG-RESOLVER", "PASS", detail)

    held = _exact_authority_roots()
    if held is None:
        add("AUTH-EXACT-AUTHORITY", "DEVIATION", "pinned detached checkouts unavailable")
        add("AUTH-SEMANTIC-MISMATCH", "DEVIATION", "pinned candidate file unavailable")
    else:
        base, exact = held
        try:
            try:
                verify_external_authorities(**exact)
                add("AUTH-EXACT-AUTHORITY", "PASS", "pinned checkouts verified")
            except ParentBoundPipelineError as exc:
                add("AUTH-EXACT-AUTHORITY", "DEVIATION", exc)
            mutated = Path(tempfile.mkdtemp(prefix="cal-pressure-mismatch-"))
            source = exact["contract_c_root"] / "research/contract_c_cal_v1_polarity_authority_successor_rc0_20261003/candidate_rc0.py"
            destination = mutated / "research/contract_c_cal_v1_polarity_authority_successor_rc0_20261003/candidate_rc0.py"
            destination.parent.mkdir(parents=True)
            text = source.read_text(encoding="utf-8").replace(SEMANTIC, "0" * 40, 1)
            destination.write_text(text, encoding="utf-8")
            try:
                _load_authority_modules(contract_c_root=mutated, rc2_root=exact["rc2_root"])
                add("AUTH-SEMANTIC-MISMATCH", "CRITICAL_FAIL", "wrong semantic identity loaded")
            except ParentBoundPipelineError as exc:
                add("AUTH-SEMANTIC-MISMATCH", "PASS", exc)
            except Exception as exc:
                add("AUTH-SEMANTIC-MISMATCH", "DEVIATION", type(exc).__name__ + ": " + _public(exc))
            shutil.rmtree(mutated, ignore_errors=True)
        finally:
            _remove_authority_worktrees(base, exact)
    return rows


def _remove_authority_worktrees(base: Path, roots: dict[str, Path]) -> None:
    apparatus = _apparatus_repo()
    for path in roots.values():
        subprocess.run(
            ["git", "-C", str(apparatus), "worktree", "remove", "--force", str(path)],
            capture_output=True,
            text=True,
        )
    shutil.rmtree(base, ignore_errors=True)


def _exact_authority_roots() -> tuple[Path, dict[str, Path]] | None:
    apparatus = _apparatus_repo()
    base = Path(tempfile.mkdtemp(prefix="cal-pressure-auth-"))
    specs = {
        "contract_c_root": "c183d2d12306ee30c509169a58db55e7430fe8c5",
        "rc2_root": "b42c827acb0a9fe65353354d709add0e27bab307",
        "resolver_root": "292168222f83c67a24190b4846eebe84392e3d04",
    }
    roots: dict[str, Path] = {}
    for name, commit in specs.items():
        path = base / name
        completed = subprocess.run(
            ["git", "-C", str(apparatus), "worktree", "add", "--detach", str(path), commit],
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            _remove_authority_worktrees(base, roots)
            return None
        roots[name] = path
    return base, roots


def _probe_main() -> int:
    if os.environ.get("CAL_PRESSURE_DECISIVE") != "1":
        print("probe refused outside decisive execution", file=sys.stderr)
        return 2
    matrix = _load("MATRIX.json")
    case = next(row for row in matrix["cases"] if row["case_id"] == "SC-DID-NOT")
    observed = _conclusion_for(case["claim"], case["evidence"])
    print(observed.get("conclusion"))
    return 0


def _operational(source_conclusion: str | None) -> list[dict[str, Any]]:
    from claim_audit_lab.production_v1.execution import OutputSafetyError, _destination_available
    from claim_audit_lab.production_v1.targeting import TargetAuthoringError, write_target_file

    rows = []
    roots = Path(tempfile.mkdtemp(prefix="cal-pressure-ops-"))
    left = roots / "left"
    right = roots / "right"
    left.mkdir()
    right.mkdir()
    env = os.environ.copy()
    env["CAL_PRESSURE_DECISIVE"] = "1"
    env["PYTHONPATH"] = str(REPO / "src")
    commands = []
    for folder, locale, tz, seed in (
        (left, "C", "UTC", "0"),
        (right, "en_US.UTF-8", "America/Toronto", "1"),
    ):
        probe_env = env.copy()
        probe_env.update({"LC_ALL": locale, "TZ": tz, "PYTHONHASHSEED": seed})
        completed = subprocess.run(
            [sys.executable, str(CAMPAIGN / "evaluate.py"), "--probe"],
            cwd=str(REPO),
            env=probe_env,
            capture_output=True,
            text=True,
        )
        (folder / "stdout.txt").write_text(completed.stdout, encoding="utf-8")
        commands.append(completed)
    same_roots = commands[0].stdout == commands[1].stdout and commands[0].returncode == 0
    rows.append({"case_id": "OPS-DET-ROOTS", "classification": "PASS" if same_roots else "CRITICAL_FAIL", "detail": "two locale roots"})
    rows.append({"case_id": "OPS-LOCALE", "classification": "PASS" if same_roots else "CRITICAL_FAIL", "detail": commands[0].stdout.strip() + "/" + commands[1].stdout.strip()})

    target_path = roots / "target.json"
    from claim_audit_lab.production_v1.targeting import author_target

    authored = author_target("ops", "Alpha had a higher rate than Beta.")
    write_target_file(target_path, authored)
    try:
        write_target_file(target_path, authored)
        rows.append({"case_id": "OPS-OVERWRITE", "classification": "CRITICAL_FAIL", "detail": "overwrite accepted"})
    except TargetAuthoringError as exc:
        rows.append({"case_id": "OPS-OVERWRITE", "classification": "PASS", "detail": _public(exc)})
    file_path = roots / "not-a-dir"
    file_path.write_text("x", encoding="utf-8")
    try:
        _destination_available(file_path)
        rows.append({"case_id": "OPS-NONDIR", "classification": "CRITICAL_FAIL", "detail": "file output accepted"})
    except OutputSafetyError as exc:
        rows.append({"case_id": "OPS-NONDIR", "classification": "PASS", "detail": _public(exc)})
    link = roots / "link"
    link.symlink_to(left)
    try:
        _destination_available(link)
        rows.append({"case_id": "OPS-SYMLINK", "classification": "CRITICAL_FAIL", "detail": "symlink output accepted"})
    except OutputSafetyError as exc:
        rows.append({"case_id": "OPS-SYMLINK", "classification": "PASS", "detail": _public(exc)})

    distinct_a = roots / "conc-a"
    distinct_b = roots / "conc-b"
    errors: list[str] = []

    def write_distinct(path: Path) -> None:
        path.mkdir()
        _destination_available(path)
        (path / "result.json").write_text(source_conclusion or "", encoding="utf-8")

    threads = [threading.Thread(target=write_distinct, args=(path,)) for path in (distinct_a, distinct_b)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    distinct_ok = (distinct_a / "result.json").read_text(encoding="utf-8") == (distinct_b / "result.json").read_text(encoding="utf-8")
    rows.append({"case_id": "OPS-CONCURRENT", "classification": "PASS" if distinct_ok else "DEVIATION", "detail": "distinct outputs"})

    shared = roots / "shared"
    shared.mkdir()
    (shared / "existing.json").write_text("{}", encoding="utf-8")
    collisions = []

    def collide() -> None:
        try:
            _destination_available(shared)
            collisions.append("accepted")
        except OutputSafetyError:
            collisions.append("rejected")

    pair = [threading.Thread(target=collide) for _ in range(2)]
    for thread in pair:
        thread.start()
    for thread in pair:
        thread.join()
    rows.append({
        "case_id": "OPS-COLLISION",
        "classification": "PASS" if collisions.count("rejected") == 2 else "CRITICAL_FAIL" if "accepted" in collisions else "DEVIATION",
        "detail": ",".join(collisions),
    })
    empty = roots / "empty-race"
    empty.mkdir()
    empty_results: list[str] = []

    def touch_empty() -> None:
        try:
            _destination_available(empty)
            empty_results.append("accepted")
        except OutputSafetyError:
            empty_results.append("rejected")

    empty_threads = [threading.Thread(target=touch_empty) for _ in range(2)]
    for thread in empty_threads:
        thread.start()
    for thread in empty_threads:
        thread.join()
    if empty_results.count("accepted") == 2:
        empty_class = "INTERFACE_GAP"
    elif empty_results.count("rejected") == 2:
        empty_class = "PASS"
    else:
        empty_class = "DEVIATION"
    rows.append({"case_id": "OPS-EMPTY-RACE", "classification": empty_class, "detail": ",".join(empty_results)})
    try:
        rows.extend(_package_rows(source_conclusion))
    finally:
        shutil.rmtree(roots, ignore_errors=True)
    return rows


def _package_rows(source_conclusion: str | None) -> list[dict[str, Any]]:
    dist = Path(tempfile.mkdtemp(prefix="cal-pressure-dist-"))
    build = subprocess.run(
        ["uv", "build", "--wheel", "--sdist", "--out-dir", str(dist)],
        cwd=str(REPO),
        capture_output=True,
        text=True,
    )
    rows = []
    if build.returncode != 0:
        detail = _public(build.stderr[-400:])
        shutil.rmtree(dist, ignore_errors=True)
        return [
            {"case_id": "OPS-WHEEL", "classification": "DEVIATION", "detail": detail},
            {"case_id": "OPS-SDIST", "classification": "DEVIATION", "detail": detail},
        ]
    artifacts = {path.suffix: path for path in dist.iterdir()}
    wheel = next((path for path in dist.iterdir() if path.name.endswith(".whl")), None)
    sdist = next((path for path in dist.iterdir() if path.name.endswith(".tar.gz")), None)
    for case_id, artifact in (("OPS-WHEEL", wheel), ("OPS-SDIST", sdist)):
        if artifact is None:
            rows.append({"case_id": case_id, "classification": "DEVIATION", "detail": "artifact missing"})
            continue
        env_dir = dist / case_id
        created = subprocess.run(
            ["uv", "venv", "--python", "3.11", str(env_dir)],
            capture_output=True,
            text=True,
        )
        if created.returncode != 0:
            rows.append({"case_id": case_id, "classification": "DEVIATION", "detail": _public(created.stderr[-300:])})
            continue
        installed = subprocess.run(
            ["uv", "pip", "install", "--python", str(env_dir / "bin" / "python"), str(artifact)],
            capture_output=True,
            text=True,
        )
        if installed.returncode != 0:
            rows.append({"case_id": case_id, "classification": "DEVIATION", "detail": _public(installed.stderr[-300:])})
            continue
        probe = (
            "import hashlib,os\n"
            "from claim_audit_lab.production_v1.semantic.engine import audit\n"
            "from claim_audit_lab.production_v1.semantic.models import AdmittedPassage, AuditContext, EvidenceWorld, SemanticFamily, TypedProposition\n"
            "from claim_audit_lab.production_v1.targeting import author_target\n"
            "claim='Alpha had a higher rate than Beta.'\n"
            "evidence='Alpha did not have a higher rate than Beta.'\n"
            "target=author_target('pkg', claim)\n"
            "prop=target['proposition']\n"
            "passage=AdmittedPassage.create('p0','s0',evidence)\n"
            "world=EvidenceWorld.create('1.2.0','pkg','sha256:'+'ab'*32,(passage,),{'contract_b_factual_context_state':'present'})\n"
            "typed=TypedProposition.create(prop['proposition_id'], SemanticFamily(prop['semantic_family']), prop['fields'], text_sha256=prop['text_sha256'])\n"
            "print(audit(AuditContext(claim, typed, world)).conclusion.value)\n"
        )
        completed = subprocess.run(
            [str(env_dir / "bin" / "python"), "-c", probe],
            capture_output=True,
            text=True,
        )
        observed = completed.stdout.strip()
        ok = completed.returncode == 0 and observed == "contradicted" and observed == source_conclusion
        rows.append({
            "case_id": case_id,
            "classification": "PASS" if ok else "CRITICAL_FAIL" if observed in {"supported", "contradicted"} and observed != "contradicted" else "DEVIATION",
            "detail": f"sha256={_sha256(artifact.read_bytes())} conclusion={observed or _public(completed.stderr[-200:])}",
            "artifact_sha256": _sha256(artifact.read_bytes()),
            "artifact_name": artifact.name,
        })
    del artifacts
    shutil.rmtree(dist, ignore_errors=True)
    return rows


def _weak_rows(semantic_rows: list[dict[str, Any]], authority_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_semantic = {row["case_id"]: row for row in semantic_rows}
    by_authority = {row["case_id"]: row for row in authority_rows}
    negation = by_semantic["SC-DID-NOT"]
    weak_negation = ignore_assertion_polarity(
        "Alpha had a higher rate than Beta.",
        ["Alpha did not have a higher rate than Beta."],
    )
    scoped = "Alpha had a higher rate than Beta among adults in 2024."
    weak_scope = collapse_scoped_comparison(scoped)
    real_scope = by_semantic["SC-SCOPED-CLAIM"]
    from claim_audit_lab.production_v1.bundle_input import BundleTargetValidationError, _validate_target
    from claim_audit_lab.production_v1.targeting import author_target

    authored = author_target("weak", "Alpha had a higher rate than Beta.")
    mutated = json.loads(json.dumps(authored))
    mutated["proposition"]["fields"]["comparison_direction"] = "LESS_THAN"
    structural_real = True
    try:
        _validate_target(mutated)
    except BundleTargetValidationError:
        structural_real = False
    conformance_rejects = mutated["proposition"]["fields"] != author_target("weak", "Alpha had a higher rate than Beta.")["proposition"]["fields"]
    weak_structural = structural_target_ok(mutated)
    mismatch = by_authority.get("AUTH-SEMANTIC-MISMATCH", {})
    real_rejects_identity = mismatch.get("classification") == "PASS"
    weak_accepts_identity = resolver_identity_wildcard("0" * 40, SEMANTIC)
    gates = [
        {
            "case_id": "WEAK-IGNORE-POLARITY",
            "real": negation.get("conclusion"),
            "weak": weak_negation,
            "discriminates": negation.get("conclusion") == "contradicted" and weak_negation == "supported",
        },
        {
            "case_id": "WEAK-COLLAPSE-SCOPE",
            "real": real_scope.get("authoring"),
            "weak": weak_scope,
            "discriminates": real_scope.get("authoring") == "refused" and weak_scope is not None,
        },
        {
            "case_id": "WEAK-STRUCTURAL-ONLY",
            "real_structural_accepts": structural_real,
            "real_conformance_rejects": conformance_rejects,
            "weak": weak_structural,
            "discriminates": conformance_rejects and weak_structural,
        },
        {
            "case_id": "WEAK-RESOLVER-WILDCARD",
            "real_rejects": real_rejects_identity,
            "weak_accepts": weak_accepts_identity,
            "discriminates": real_rejects_identity and weak_accepts_identity,
        },
    ]
    return gates


def _real_rows() -> list[dict[str, Any]]:
    cohort = _load("COHORT.json")
    rows = []
    for case in cohort["cases"]:
        if case["status"] == "NO_ELIGIBLE_ACTIVE_FAMILY_CLAIM":
            rows.append({**case, "classification": "NO_ELIGIBLE_ACTIVE_FAMILY_CLAIM", "cal_called": False})
            continue
        observed = _conclusion_for(case["claim"], [case["passage"]])
        relation = case.get("source_relation")
        conclusion = observed.get("conclusion")
        if observed["authoring"] == "refused":
            classification = "AUTHORING_LIMIT"
        elif relation == "supports" and conclusion == "supported":
            classification = "PASS"
        elif relation == "refutes" and conclusion == "contradicted":
            classification = "PASS"
        elif conclusion == "not_checkable":
            classification = "ROBUSTNESS_LIMIT"
        elif conclusion in {"supported", "contradicted"}:
            classification = "CRITICAL_FAIL"
        else:
            classification = "DEVIATION"
        rows.append({
            "case_id": case["case_id"],
            "source_id": case["source_id"],
            "family_hypothesis": case.get("family_hypothesis"),
            "source_relation": relation,
            "authoring": observed["authoring"],
            "conclusion": conclusion,
            "failure_code": observed.get("failure_code"),
            "classification": classification,
        })
    return rows


def _representatives(semantic: list[dict[str, Any]], real: list[dict[str, Any]]) -> dict[str, Any]:
    def first(rows: list[dict[str, Any]], predicate) -> dict[str, Any] | None:
        return next((row for row in rows if predicate(row)), None)

    return {
        "correct": first(semantic, lambda row: row["case_id"] == "SC-DID-NOT"),
        "abstention": first(semantic, lambda row: row["case_id"] == "SC-NOT-HIGHER-VS-LOWER"),
        "authoring_refusal": first(real, lambda row: row.get("classification") == "AUTHORING_LIMIT")
        or first(semantic, lambda row: row["case_id"] == "SC-SCOPED-CLAIM"),
        "negative_control": first(semantic, lambda row: row["case_id"] == "SC-NEVER"),
    }


def _disposition(rows: list[dict[str, Any]], gates: list[dict[str, Any]]) -> str:
    classes = {row.get("classification") for row in rows}
    if "CRITICAL_FAIL" in classes:
        return "PRESSURE_FALSIFIED_CRITICAL_SEMANTIC_FAILURE"
    if any(not gate.get("discriminates") for gate in gates):
        return "PRESSURE_INCONCLUSIVE_EVALUATOR_NOT_DISCRIMINATING"
    if "DEVIATION" in classes and "PASS" not in classes and "AUTHORING_LIMIT" not in classes:
        return "PRESSURE_INCONCLUSIVE_APPARATUS_INVALID"
    return "PRESSURE_SUPPORTED_NO_CRITICAL_FAIL_WITH_DOCUMENTED_LIMITS"


def execute() -> int:
    output = CAMPAIGN / "evidence" / "decisive-run-01"
    if output.exists():
        print("decisive output already exists", file=sys.stderr)
        return 2
    if _git("rev-parse", "HEAD^{tree}") and _git("status", "--porcelain"):
        print("worktree is dirty; freeze before execution", file=sys.stderr)
        return 2
    if _git("rev-parse", "HEAD") == SUBJECT:
        print("HEAD is still the product commit; campaign files are not frozen", file=sys.stderr)
        return 2
    if subprocess.run(
        ["git", "-C", str(REPO), "merge-base", "--is-ancestor", SUBJECT, "HEAD"],
        capture_output=True,
    ).returncode != 0:
        print("product commit is not an ancestor", file=sys.stderr)
        return 2
    drift = _assert_frozen_blobs()
    if drift:
        print(drift, file=sys.stderr)
        return 2
    matrix = _load("MATRIX.json")
    output.mkdir(parents=True)
    os.environ["CAL_PRESSURE_DECISIVE"] = "1"
    try:
        semantic = _run_semantic(matrix)
        authority = _authority_rows()
        did_not = next(row for row in semantic if row["case_id"] == "SC-DID-NOT")
        operational = _operational(did_not.get("conclusion"))
        weak = _weak_rows(semantic, authority)
        real = _real_rows()
        combined = semantic + authority + operational + real
        result = {
            "schema": "cal-v1-polarity-successor-pressure-result-rc0",
            "subject": SUBJECT,
            "semantic_implementation": SEMANTIC,
            "head": _git("rev-parse", "HEAD"),
            "tree": _git("rev-parse", "HEAD^{tree}"),
            "python": sys.version.split()[0],
            "semantic": semantic,
            "authority": authority,
            "operational": operational,
            "weak_gates": weak,
            "real": real,
            "representatives": _representatives(semantic, real),
            "counts": _counts(combined),
            "disposition": _disposition(combined, weak),
        }
        code = 0 if result["disposition"] != "PRESSURE_INCONCLUSIVE_APPARATUS_INVALID" else 1
    except Exception:
        result = {
            "schema": "cal-v1-polarity-successor-pressure-result-rc0",
            "subject": SUBJECT,
            "semantic_implementation": SEMANTIC,
            "head": _git("rev-parse", "HEAD"),
            "tree": _git("rev-parse", "HEAD^{tree}"),
            "python": sys.version.split()[0],
            "disposition": "PRESSURE_INCONCLUSIVE_APPARATUS_INVALID",
            "error": _public(traceback.format_exc()),
        }
        code = 1
    (output / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(result["disposition"])
    if "counts" in result:
        print(json.dumps(result["counts"], sort_keys=True))
    return code


def _counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        key = str(row.get("classification"))
        counts[key] = counts.get(key, 0) + 1
    counts["rows"] = len(rows)
    return counts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--probe", action="store_true")
    args = parser.parse_args()
    if args.probe:
        return _probe_main()
    if args.execute:
        return execute()
    print("frozen runner; pass --execute for the decisive run")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
