"""Execute frozen CAL #188 apparatus against the immutable CAL subject.

Owner: issue #188. Calls real CAL engines/CLIs. No implementation repair.
Inputs: --out new custody directory and pinned CAL/EB environment paths.
Outputs: exact inputs, process streams, native outputs and append-only observations.
"""
import argparse
import dataclasses
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import traceback
from datetime import datetime, timezone
from unittest.mock import patch

ROOT = Path(__file__).parent
SUBJECT = "6bb0d60f3e2286123f56de5657de4e97d6374c63"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, default=str) + "\n")


def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def tree(path):
    return {p.relative_to(path).as_posix(): sha(p.read_bytes())
            for p in sorted(path.rglob("*")) if p.is_file()}


def serial(value):
    if dataclasses.is_dataclass(value):
        return serial(dataclasses.asdict(value))
    if isinstance(value, dict):
        return {k: serial(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(v) for v in value]
    return value.value if hasattr(value, "value") else value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    freeze = json.loads((ROOT / "HARNESS_FREEZE.json").read_text())
    for name, digest in freeze["files"].items():
        assert sha((ROOT / name).read_bytes()) == digest, "frozen apparatus changed: " + name
    # Imports and all CAL calls occur only after the complete freeze verification.
    from claim_audit_lab.production_v1 import execution as execution
    from claim_audit_lab.production_v1.bundle_input import prepare_contract_b_input
    from claim_audit_lab.production_v1.semantic.models import AdmittedPassage, AuditContext, EvidenceWorld, SemanticFamily, TypedProposition
    from claim_audit_lab.production_v1.semantic.engine import audit, compose, PassageTrace
    from claim_audit_lab.production_v1.semantic.measurements import measure_strict_comparison, measure_direct_event_order
    from claim_audit_lab.production_v1.semantic.authority import complete_and_warrant, AuthorityRefusal
    from claim_audit_lab.production_v1.semantic.relations import derive_relation, RelationRefusal
    from claim_audit_lab.production_v1.targeting import author_target, TargetAuthoringError, validate_target_conformance

    inspect = execution.inspect_record()
    assert inspect["semantic_implementation_sha"] == "847cc970642bb648dc994b929c2053b5c9d4648c"
    assert inspect["supported_semantic_families"] == ["strict_comparison", "direct_event_order"]
    dump(out / "INSPECT.json", inspect)
    env = dict(os.environ)
    wheel_py = Path(env["CAL188_WHEEL_PYTHON"])
    sdist_py = Path(env["CAL188_SDIST_PYTHON"])
    wheel_cli = wheel_py.parent / "claim-audit-v1"
    os.environ["CAL_PRESSURE_CLI"] = str(wheel_cli)
    os.environ["CAL_PRESSURE_OUT"] = str(out / "historical")
    spec = importlib.util.spec_from_file_location("cal188_historical", ROOT / "historical_182.py")
    history = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(history)
    matrix = json.loads((ROOT / "MATRIX.json").read_text())
    cohort = {r["case_id"]: r for r in json.loads((ROOT / "COHORT.json").read_text())["cases"]}
    observations = []
    critical = []
    first_negative = None
    base_bundles = {}
    commands = []

    def proc(case_root, label, module, command, python=None, env_overrides=None):
        python = python or sys.executable
        runenv = dict(env)
        if str(python) in {str(wheel_py), str(sdist_py)}:
            runenv.pop("PYTHONPATH", None)
        runenv.update(env_overrides or {})
        argv = [str(python), "-m", module, *map(str, command)]
        p = subprocess.run(argv, cwd=out, env=runenv, capture_output=True, timeout=90)
        (case_root / (label + ".stdout")).write_bytes(p.stdout)
        (case_root / (label + ".stderr")).write_bytes(p.stderr)
        rec = {"label": label, "argv": argv, "returncode": p.returncode,
               "stdout_sha256": sha(p.stdout), "stderr_sha256": sha(p.stderr),
               "pythonpath_present": "PYTHONPATH" in runenv}
        commands.append(rec)
        return rec

    def bundle(family):
        if family in base_bundles:
            return base_bundles[family]
        dest = out / "bases" / family
        if family == "strict_comparison":
            b = history.build_bundle(dest, "S-C1-SUPPORT")
            claim_id = "C1"
        else:
            from evidence_bundler.v1 import build_package
            from evidence_bundler.v1.contract_b import INTEGRATION_CONFIG, project_contract_b
            initial = history.initial_package()
            rows = [r for r in initial["candidates"] if r["proposition_id"] == "C2" and r["source_id"] == "S-C2-SUPPORT" and r["selection_state"] == "retained"]
            assert len(rows) == 1
            package = build_package(contract_a=history.contract_a(), config=INTEGRATION_CONFIG,
                                    admission={("C2", rows[0]["passage_id"]): "accepted"})
            project_contract_b(package=package, compatibility_carrier=history.carrier(), out_dir=dest)
            b = dest / "contract_b"
            claim_id = "C2"
        claim = history.C1_TEXT if claim_id == "C1" else history.C2_TEXT
        t = dest / "authored.json"
        t.write_bytes(encode(author_target(claim_id, claim)))
        validate_target_conformance(b, t)
        base_bundles[family] = (b, t, claim_id)
        return b, t, claim_id

    def context(family, claim, texts, world_id="cal188-world"):
        target = author_target("C1", claim)
        prop = TypedProposition.create("C1", SemanticFamily(family), target["proposition"]["fields"], text_sha256=sha(claim.encode()))
        passages = tuple(AdmittedPassage.create(f"p{i}", f"s{i}", text, "sha256:" + sha(f"source-{i}".encode())) for i, text in enumerate(texts))
        world = EvidenceWorld.create("1.2.0", world_id, "sha256:" + sha(world_id.encode()), passages,
                                     {"contract_b_factual_context_state": "present", "observation": {"scope": "pressure"}})
        return AuditContext(claim, prop, world)

    def note(row):
        nonlocal first_negative
        row["recorded_at_utc"] = datetime.now(timezone.utc).isoformat()
        observations.append(row)
        with (out / "observations.jsonl").open("a") as handle:
            handle.write(json.dumps(row, default=str, ensure_ascii=False) + "\n")
        if row["classification"] in {"ROBUSTNESS_LIMIT", "INTERFACE_GAP", "CRITICAL_FAIL", "APPARATUS_INVALID"} and first_negative is None:
            first_negative = row
            dump(out / "FIRST_MEANINGFUL_NEGATIVE.json", row)
        if row["classification"] == "CRITICAL_FAIL":
            critical.append(row)
            dump(out / "RELEASE_PROGRESSION_STOP.json", {"subject": SUBJECT, "falsifier": row, "release_allowed": False})
        print(row["case_id"], row["classification"], flush=True)

    original_record = history.record
    def historical_record(*a, **kw):
        original_record(*a, **kw)
        r = history.RESULTS[-1]
        # Every historical row is persisted at first observation, before further
        # cases, with its original classification and exact expected/observed.
        with (out / "historical-observations.jsonl").open("a") as f:
            f.write(json.dumps(r, default=str) + "\n")
        if r["status"] in {"CRITICAL_FAIL", "ROBUSTNESS_LIMIT", "INTERFACE_GAP"}:
            note({"case_id": "H182-" + r["probe_id"], "domain": "H_DETAIL", "classification": r["status"], "observed": r, "actual_subject": SUBJECT})
        if r["status"] == "CRITICAL_FAIL":
            raise RuntimeError("historical critical falsifier; stop")
    history.record = historical_record

    apparatus_invalid = False
    for case in matrix["cases"]:
        if critical or apparatus_invalid:
            note({"case_id": case["case_id"], "domain": case["domain"], "classification": "NOT_RUN", "reason": "stop rule"})
            continue
        cr = out / "cases" / case["case_id"]
        cr.mkdir(parents=True)
        dump(cr / "EXPECTED.json", case)
        observed = {}
        classification = "PASS"
        try:
            op = case["operation"]
            if op == "historical":
                history.main()
                raw = json.loads((out / "historical" / "pressure-results.json").read_text())
                observed = {"unchanged_harness_sha256": sha((ROOT / "historical_182.py").read_bytes()), "actual_subject": SUBJECT,
                            "historical_embedded_candidate": raw["subject_commit"], "counts": raw["counts"], "raw_receipt_sha256": sha((out / "historical" / "pressure-results.json").read_bytes())}
            elif op == "real":
                real = cohort[case["cohort_case_id"]]
                dump(cr / "INPUT.json", real)
                assert sha(real["evidence_text"].encode()) == real["evidence_text_sha256"]
                try:
                    target = author_target(real["case_id"], real["claim_text"])
                except TargetAuthoringError as exc:
                    observed = {"authoring": "REFUSED", "error": str(exc), "semantic_execution": "NOT_RUN", "raw_source_sha256": real["raw_source_sha256"], "evidence_text_sha256": real["evidence_text_sha256"]}
                    classification = "ROBUSTNESS_LIMIT"
                else:
                    (cr / "target.json").write_bytes(encode(target))
                    family = target["proposition"]["semantic_family"]
                    passages = (AdmittedPassage.create(real["case_id"] + "-p", real["source_id"], real["evidence_text"], "sha256:" + real["raw_source_sha256"]),)
                    world = EvidenceWorld.create("1.2.0", "cal188-real-" + real["source_id"], "sha256:" + sha(encode(real)), passages,
                        {"contract_b_factual_context_state": "present", "observation": {"source_first": True, "locator": real["locator"]}})
                    ctx = AuditContext(real["claim_text"], TypedProposition.create(real["case_id"], SemanticFamily(family), target["proposition"]["fields"], text_sha256=sha(real["claim_text"].encode())), world)
                    result = audit(ctx)
                    observed = {"authoring": "AUTHORED", "internal_semantic_result": serial(result)}
                    expected = "supported" if real["expected_source_relation"] == "supports" else "contradicted"
                    classification = "PASS" if result.conclusion.value == expected else "ROBUSTNESS_LIMIT" if result.conclusion.value == "not_checkable" else "CRITICAL_FAIL"
            elif op in {"target", "bypass"}:
                b, t, cid = bundle(case["family"])
                target = json.loads(t.read_bytes())
                fields = target["proposition"]["fields"]
                direction = "comparison_direction" if case["family"] == "strict_comparison" else "temporal_relation"
                lhs = "lhs_entity" if case["family"] == "strict_comparison" else "left_subject"
                mutation = case.get("mutation", "inversion")
                if mutation == "missing": fields.pop(lhs)
                elif mutation == "extra-semantic": fields["time_scope"] = "2025"
                elif mutation == "unsupported-direction": fields[direction] = "SIDEWAYS"
                elif mutation == "claim-hash": target["proposition"]["text_sha256"] = "0" * 64
                elif mutation == "claim-id": target["claim_id"] = "OTHER"
                elif mutation == "proposition-id": target["proposition"]["proposition_id"] = "OTHER"
                elif mutation == "orientation":
                    if case["family"] == "strict_comparison": fields["lhs_entity"], fields["rhs_entity"] = fields["rhs_entity"], fields["lhs_entity"]
                    else:
                        for k in ("subject", "predicate", "object", "polarity"): fields["left_" + k], fields["right_" + k] = fields["right_" + k], fields["left_" + k]
                elif mutation == "inversion": fields[direction] = "LESS_THAN" if direction == "comparison_direction" else "AFTER"
                elif mutation == "family-substitution": target["proposition"]["semantic_family"] = "direct_event_order" if case["family"] == "strict_comparison" else "strict_comparison"
                elif mutation == "unknown-top": target["extra"] = "x"
                elif mutation == "unknown-nested": target["proposition"]["extra"] = "x"
                elif mutation == "whitespace-field": fields[lhs] = " " + fields[lhs] + " "
                elif mutation == "punctuation-field": fields[lhs] += ","
                elif mutation == "confusable": fields[lhs] = fields[lhs].replace("a", "а").replace("A", "Α")
                elif mutation == "long-field": fields[lhs] = "A" * 8192
                raw = encode(target)
                if mutation == "duplicate-keys": raw = raw.replace(b'"claim_id":', b'"claim_id":"' + cid.encode() + b'","claim_id":', 1)
                elif mutation == "malformed-json": raw = raw[:-3]
                elif mutation == "invalid-utf8": raw = b"\xff" + raw
                elif mutation == "format-only": raw = (" \n" + json.dumps(target, indent=3) + " \n").encode()
                p = cr / "target.json"; p.write_bytes(raw)
                vr = proc(cr, "validate", "claim_audit_lab.production_v1.bundle_cli", ["validate-bundle", b, p])
                cf = proc(cr, "conform", "claim_audit_lab.production_v1.target_cli", ["conform", b, p])
                workflow_out = cr / "supported-workflow-output"
                observed = {"structural": vr, "conformance": cf, "supported_execution_calls": 0, "supported_output_present": False}
                accepted = cf["returncode"] == 0
                if accepted:
                    observed["supported_execution"] = proc(cr, "supported-run", "claim_audit_lab.production_v1.bundle_cli", ["run-bundle", b, p, "--out-dir", workflow_out])
                    observed["supported_execution_calls"] = 1
                    observed["supported_output_present"] = workflow_out.exists()
                if op == "bypass":
                    rr = proc(cr, "raw-run", "claim_audit_lab.production_v1.bundle_cli", ["run-bundle", b, p, "--out-dir", cr / "raw-output"])
                    observed["raw_run"] = rr
                    if rr["returncode"] == 0:
                        observed["raw_result"] = json.loads((cr / "raw-output" / "result.json").read_bytes())
                    classification = "CRITICAL_FAIL" if accepted else "INTERFACE_GAP" if vr["returncode"] == 0 and rr["returncode"] == 0 else "PASS"
                else:
                    classification = "PASS" if accepted == case["conform_accept"] else "CRITICAL_FAIL" if accepted else "ROBUSTNESS_LIMIT"
                    if classification == "PASS" and vr["returncode"] == 0 and not accepted:
                        observed["raw_precondition_gap"] = True
            elif op in {"semantic", "binding"}:
                family = case["family"]
                claim = case.get("claim", history.C1_TEXT if family == "strict_comparison" else history.C2_TEXT)
                texts = case.get("texts", [claim])
                ctx = context(family, claim, texts)
                dump(cr / "CONTEXT.json", serial(ctx))
                if op == "semantic":
                    result = audit(ctx)
                    observed = serial(result)
                    expected = case["expected"]
                    value = result.conclusion.value
                    if expected == "refuted_or_abstain": classification = "CRITICAL_FAIL" if value == "supported" else "PASS"
                    elif value == expected: classification = "PASS"
                    elif value == "not_checkable" and case.get("coverage"): classification = "ROBUSTNESS_LIMIT"
                    else: classification = "CRITICAL_FAIL"
                    if len(result.traces) != len(texts): classification = "CRITICAL_FAIL"
                else:
                    mutation = case["mutation"]
                    measure = measure_strict_comparison if family == "strict_comparison" else measure_direct_event_order
                    receipt = measure(ctx, "p0")
                    authority = complete_and_warrant(ctx, receipt, "p0")
                    relation = derive_relation(ctx, authority)
                    dump(cr / "OLD_RECEIPTS.json", serial({"measurement": receipt, "authority": authority, "relation": relation}))
                    changed = ctx
                    ps = list(ctx.evidence_world.admitted_passages)
                    if mutation == "passage-hash": ps[0] = dataclasses.replace(ps[0], text_sha256="sha256:" + "0" * 64)
                    elif mutation == "source-hash-invalid": ps[0] = dataclasses.replace(ps[0], source_sha256="invalid")
                    elif mutation == "duplicate-id": ps.append(ps[0])
                    elif mutation == "passage-id": ps[0] = dataclasses.replace(ps[0], passage_id="foreign-id")
                    elif mutation == "source-identity-stale": ps[0] = dataclasses.replace(ps[0], source_sha256="sha256:" + "0" * 64, source_id="foreign-source")
                    elif mutation == "source-substitution-stale": ps[0] = AdmittedPassage.create("p0", "s0", texts[0].replace("higher", "lower").replace("before", "after"), "sha256:" + sha(b"foreign-source"))
                    world = dataclasses.replace(ctx.evidence_world, admitted_passages=tuple(ps))
                    if mutation == "aperture-stale": world = dataclasses.replace(world, aperture_observation_json='{"changed":true}')
                    if mutation in {"stale-measurement", "foreign-authority", "foreign-relation"}: world = dataclasses.replace(world, bundle_id="foreign-world")
                    changed = dataclasses.replace(ctx, evidence_world=world)
                    if mutation == "claim-identity-stale": changed = dataclasses.replace(changed, original_claim=claim + " ")
                    dump(cr / "MUTATED_CONTEXT.json", serial(changed))
                    try:
                        if mutation in {"passage-hash", "source-hash-invalid", "duplicate-id"}: result = audit(changed)
                        elif mutation in {"foreign-authority", "forged-authority"}: result = derive_relation(changed, dataclasses.replace(authority, authority_id="semantic-authority:" + "0" * 64) if mutation == "forged-authority" else authority)
                        elif mutation == "foreign-relation": result = compose(changed, (PassageTrace("p0", receipt, authority, relation, None, None),))
                        else: result = complete_and_warrant(changed, receipt, "p0")
                    except (ValueError, AuthorityRefusal, RelationRefusal) as exc:
                        observed = {"refused": True, "exception": type(exc).__name__, "error": str(exc)}
                    else:
                        observed = {"refused": False, "result": serial(result)}
                        classification = "CRITICAL_FAIL"
            elif op == "same-world":
                b, t, cid = bundle(case["family"])
                clone = cr / "different-path-world"; shutil.copytree(b, clone)
                execution.run_contract_b_bundle(b, t, cr / "a")
                execution.run_contract_b_bundle(clone, t, cr / "b")
                observed = {"a": tree(cr / "a"), "b": tree(cr / "b")}
                classification = "PASS" if observed["a"] == observed["b"] else "CRITICAL_FAIL"
            elif op == "operational":
                b, t, cid = bundle("strict_comparison")
                control = case["control"]
                module = "claim_audit_lab.production_v1.bundle_cli"
                def run(label, path, py=None, changes=None):
                    return proc(cr, label, module, ["run-bundle", b, t, "--out-dir", path], py, changes)
                if control in {"replay", "source-wheel", "wheel-sdist", "environment"}:
                    py_a = wheel_py if control == "wheel-sdist" else None
                    py_b = sdist_py if control == "wheel-sdist" else wheel_py if control == "source-wheel" else None
                    a = run("a", cr / "a", py_a)
                    changes = {"LC_ALL": "C", "TZ": "Pacific/Honolulu", "PYTHONHASHSEED": "314159", "NO_COLOR": "1"} if control == "environment" else None
                    bb = run("b", cr / "b", py_b, changes)
                    observed = {"a": a, "b": bb, "hashes_a": tree(cr / "a"), "hashes_b": tree(cr / "b")}
                    classification = "PASS" if a["returncode"] == bb["returncode"] == 0 and observed["hashes_a"] == observed["hashes_b"] else "CRITICAL_FAIL"
                elif control in {"overwrite", "file", "symlink", "dangling-symlink"}:
                    dest = cr / "dest"
                    if control == "overwrite": dest.mkdir(); (dest / "sentinel").write_text("keep")
                    elif control == "file": dest.write_text("keep")
                    else:
                        real = cr / "real"
                        if control == "symlink": real.mkdir()
                        dest.symlink_to(real, target_is_directory=True)
                    before = tree(cr)
                    rr = run("run", dest)
                    observed = {"run": rr, "destination_symlink": dest.is_symlink(), "sentinel": (dest / "sentinel").read_text() if control == "overwrite" else dest.read_text() if control == "file" else None,
                                "real_files": tree(cr / "real") if control in {"symlink", "dangling-symlink"} else None}
                    safe = rr["returncode"] != 0 and (observed["sentinel"] == "keep" if control in {"overwrite", "file"} else observed["destination_symlink"] and not observed["real_files"])
                    classification = "PASS" if safe else "CRITICAL_FAIL"
                elif control in {"same-output", "distinct-output"}:
                    paths = [cr / "a", cr / ("a" if control == "same-output" else "b")]
                    ps = [subprocess.Popen([str(wheel_cli), "run-bundle", str(b), str(t), "--out-dir", str(p)], cwd=out, env={k: v for k, v in env.items() if k != "PYTHONPATH"}, stdout=subprocess.PIPE, stderr=subprocess.PIPE) for p in paths]
                    for i, p in enumerate(ps):
                        so, se = p.communicate(timeout=90)
                        (cr / f"writer-{i}.stdout").write_bytes(so); (cr / f"writer-{i}.stderr").write_bytes(se)
                    codes = [p.returncode for p in ps]
                    leftovers = [p.name for p in cr.glob(".*.tmp-*")]
                    valid = (paths[0] / "result.json").exists() and json.loads((paths[0] / "result.json").read_bytes())["result"]["conclusion"] == "supported"
                    observed = {"returncodes": codes, "valid_complete_output": valid, "leftovers": leftovers, "output_a": tree(paths[0]), "output_b": tree(paths[1])}
                    safe = codes.count(0) == 1 if control == "same-output" else codes == [0, 0] and observed["output_a"] == observed["output_b"]
                    classification = "PASS" if safe and valid and not leftovers else "CRITICAL_FAIL"
                elif control in {"partial-failure", "symlink-race"}:
                    dest = cr / "dest"
                    if control == "partial-failure":
                        injection = patch.object(execution.os, "replace", side_effect=OSError("preregistered apparatus finalization fault"))
                    else:
                        real = cr / "real"; real.mkdir()
                        original_mkdtemp = execution.tempfile.mkdtemp
                        def create_link(*a, **kw):
                            temp = original_mkdtemp(*a, **kw)
                            dest.symlink_to(real, target_is_directory=True)
                            return temp
                        injection = patch.object(execution.tempfile, "mkdtemp", side_effect=create_link)
                    with injection:
                        try: execution.run_contract_b_bundle(b, t, dest)
                        except execution.OutputSafetyError as exc: observed = {"refused": True, "error": str(exc)}
                        else: observed = {"refused": False}
                    observed.update({"temporary_leftovers": [p.name for p in cr.glob(".dest.tmp-*")], "final_output_present": (dest / "result.json").exists()})
                    classification = "PASS" if observed["refused"] and not observed["temporary_leftovers"] and not observed["final_output_present"] else "CRITICAL_FAIL"
                elif control == "manifest-hashes":
                    execution.run_contract_b_bundle(b, t, cr / "run")
                    manifest = json.loads((cr / "run" / "manifest.json").read_bytes())
                    mismatches = [name for name, digest in manifest["files"].items() if "sha256:" + sha((cr / "run" / name).read_bytes()) != digest]
                    observed = {"mismatches": mismatches, "files": tree(cr / "run")}
                    classification = "PASS" if not mismatches else "CRITICAL_FAIL"
            else:
                raise ValueError("unimplemented frozen case operation: " + op)
        except Exception as exc:
            observed = {"exception": type(exc).__name__, "error": str(exc), "traceback": traceback.format_exc()}
            (cr / "error.txt").write_text(observed["traceback"])
            classification = "CRITICAL_FAIL" if critical else "APPARATUS_INVALID"
            apparatus_invalid = not critical
        dump(cr / "OBSERVED.json", observed)
        dump(cr / "FILE_HASHES.json", tree(cr))
        note({"case_id": case["case_id"], "domain": case["domain"], "classification": classification,
              "expected": case, "observed": observed, "evidence_path": str(cr.relative_to(out)), "evidence_tree": tree(cr)})

    counts = {}
    domains = {}
    for row in observations:
        if row["domain"] == "H_DETAIL": continue
        counts[row["classification"]] = counts.get(row["classification"], 0) + 1
        d = domains.setdefault(row["domain"], {})
        d[row["classification"]] = d.get(row["classification"], 0) + 1
    disposition = "PRESSURE_FALSIFIED_CRITICAL_SEMANTIC_FAILURE" if critical else "PRESSURE_INCONCLUSIVE_APPARATUS_INVALID" if apparatus_invalid else "PRESSURE_SUPPORTED_NO_CRITICAL_FAIL_WITH_DOCUMENTED_LIMITS"
    dump(out / "COMMANDS.json", commands)
    report = {"schema": "cal188-pressure-results-v1", "subject_commit": SUBJECT,
              "harness_freeze_sha256": sha((ROOT / "HARNESS_FREEZE.json").read_bytes()),
              "cohort_sha256": sha((ROOT / "COHORT.json").read_bytes()), "disposition": disposition,
              "counts": counts, "domains": domains, "critical_failures": critical,
              "first_meaningful_negative": first_negative, "results": observations,
              "release_progression": "STOPPED" if critical else "NOT_AUTHORIZED",
              "real_semantic_accuracy": "NOT_ESTABLISHED", "human_gold": False,
              "observations_sha256": sha((out / "observations.jsonl").read_bytes())}
    dump(out / "RESULTS.json", report)
    dump(out / "ARTIFACT_INDEX.json", tree(out))
    print(json.dumps({"disposition": disposition, "counts": counts, "domains": domains}), flush=True)
    return 1 if critical else 2 if apparatus_invalid else 0


if __name__ == "__main__":
    raise SystemExit(main())
