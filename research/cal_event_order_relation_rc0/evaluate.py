"""Decisive evaluator for CAL Event-Ordering Proposition Relation RC0."""
from __future__ import annotations

import argparse
from copy import deepcopy
from dataclasses import asdict, replace
import hashlib
import importlib.util
import inspect
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Callable

from research.cal_measurement_envelope_rc0.envelope import (
    AdmittedPassage,
    AuditContext,
    measure_passage,
)
from research.cal_event_order_authority_rc0 import candidate as event_candidate
from research.cal_event_order_relation_rc0 import candidate

EVENT_HEAD = "e8d33913db66ad21027dffdf731d50f7a0977c8f"
EVENT_BLOB = "3e29b0e2ec5d9ba2d873d1584e76635147e421aa"
EVENT_PATH = "research/event_ordering_measurement_rc7fc/event_order.py"
RC8J_HEAD = "8e75c6782bb95c3763d06230b9c5df2b6af44054"
RC8J_BLOBS = {
    "research/semantic_authority_machinery_rc8/authority_contract_rc8j.py": "f55156e43e0c1b4a7868bc8339585b8892edda38",
    "research/semantic_authority_machinery_rc8/authority_contract_rc8h.py": "4b872e455d52d7a682bb719889860d2cac7909a7",
    "research/semantic_authority_machinery_rc8/authority_contract_rc8f.py": "efc50481be3179332cecb449c3c9c91da7c3dfaa",
    "research/semantic_authority_machinery_rc8/authority_contract_rc8d.py": "f04f2dc529d3f1a7666d39a3bf9c8a9df87842d1",
    "research/semantic_authority_machinery_rc8/authority_contract_rc8b.py": "edf84bb5aae0dd217e3f780e7a49767440b7c1e5",
}
CANDIDATE_FREEZE = "94ea0c7531aeb852520f34bd56393b63a4b5ac75"
CANDIDATE_BLOBS = {
    "research/cal_event_order_relation_rc0/relation.py": "70f9eff65330c4182b5ac3bd1a11d13059326ed6",
    "research/cal_event_order_relation_rc0/candidate.py": "7e964d85eb80298b9b0d5b84eff32e14bed4b013",
    "research/cal_event_order_authority_rc0/event_authority.py": "88df954235069e98582e731f48e46e5b257da93f",
    "research/cal_event_order_authority_rc0/candidate.py": "36a8d1fbd9e52ec743757f750f744ad4553b5698",
    "research/cal_measurement_envelope_rc0/envelope.py": "f8ce6362f6ccc165cdad29f314721bb26a21f871",
}
ATOM_KEY = b"cal-event-order-relation-rc0-atom-key-0000000001"
PROP_KEY = b"cal-event-order-relation-rc0-prop-key-0000000001"
ATOM_KEY_ID = "cal-event-order-relation-rc0-atom"
PROP_KEY_ID = "cal-event-order-relation-rc0-prop"
SCHEMA = "cal-event-order-relation-rc0-evaluation-v1"


def _git(root: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return proc.stdout.strip()


def _require_dependency(root: Path, head: str, blobs: dict[str, str]) -> None:
    actual_head = _git(root, "rev-parse", "HEAD")
    if actual_head != head:
        raise RuntimeError(f"dependency head mismatch: {actual_head} != {head}")
    for path, expected in blobs.items():
        actual = _git(root, "hash-object", path)
        if actual != expected:
            raise RuntimeError(f"dependency blob mismatch {path}: {actual} != {expected}")


def _require_candidate_blobs(root: Path) -> None:
    for path, expected in CANDIDATE_BLOBS.items():
        actual = _git(root, "hash-object", path)
        if actual != expected:
            raise RuntimeError(f"frozen candidate blob drift {path}: {actual} != {expected}")


def _load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _sha(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def _rc8j(root: Path, case: dict[str, Any]) -> dict[str, Any]:
    code = (
        "import json,sys; "
        "from research.semantic_authority_machinery_rc8.authority_contract_rc8j import assess_authority; "
        "case=json.load(sys.stdin); json.dump(assess_authority(case),sys.stdout,sort_keys=True)"
    )
    env = dict(os.environ)
    env["PYTHONPATH"] = str(root)
    proc = subprocess.run(
        [sys.executable, "-c", code],
        cwd=root,
        env=env,
        input=json.dumps(case, sort_keys=True),
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"RC8J execution failed: {proc.stderr or proc.stdout}")
    value = json.loads(proc.stdout)
    if not isinstance(value, dict):
        raise RuntimeError("RC8J returned non-object")
    return value


def _context(*, case_id: str, source: str, claim_id: str, claim_text: str) -> AuditContext:
    return AuditContext.create(
        audit_id=f"CAL-EVENT-RELATION-{case_id}",
        original_claim_id=claim_id,
        original_claim_text=claim_text,
        proposition_id=claim_id,
        proposition_payload={
            "family": "event_ordering",
            "claim_text": claim_text,
            "research_scope": "event_order_proposition_relation_rc0",
        },
        decomposition_path=(claim_id,),
        contract_b_version="1.2.0",
        bundle_id=f"bundle-{case_id.casefold()}",
        bundle_hash=_sha(f"bundle:{case_id}:{source}:{claim_text}"),
        admitted_passages=(
            AdmittedPassage(
                source_id=f"source-{case_id.casefold()}",
                passage_id=f"passage-{case_id.casefold()}",
                passage_sha256=_sha(source),
                passage_text=source,
            ),
        ),
    )


def _event(row: dict[str, Any]) -> candidate.EventSemantics:
    return candidate.EventSemantics(
        subject=str(row["subject"]),
        predicate=str(row["predicate"]),
        object=str(row["object"]),
        polarity=str(row["polarity"]),
    )


def _claim_text(prop: dict[str, Any]) -> str:
    return "event-order-proposition:" + json.dumps(prop, sort_keys=True, separators=(",", ":"))


def _proposition(*, claim_id: str, row: dict[str, Any], claim_text: str | None = None) -> candidate.TemporalProposition:
    return candidate.TemporalProposition(
        claim_id=claim_id,
        claim_text=claim_text or _claim_text(row),
        left_event=_event(row["left_event"]),
        relation=str(row["relation"]),
        right_event=_event(row["right_event"]),
    )


def _prepare_case(
    *,
    event_module: Any,
    rc8j_root: Path,
    case_id: str,
    source: str,
    proposition: candidate.TemporalProposition,
) -> tuple[AuditContext, dict[str, Any], dict[str, Any]]:
    context = _context(
        case_id=case_id,
        source=source,
        claim_id=proposition.claim_id,
        claim_text=proposition.claim_text,
    )
    passage_id = context.admitted_passage_ids[0]
    measurement = measure_passage(
        context=context,
        passage_id=passage_id,
        instrument_id=event_candidate.EVENT_INSTRUMENT_ID,
        instrument_version=str(event_module.VERSION),
        semantic_family=event_candidate.EVENT_FAMILY,
        measure_fn=event_module.measure,
    )
    if measurement.measurement_status != "CLAIMED":
        raise RuntimeError(f"{case_id}: RC7F-C did not measure CLAIMED")
    atom = event_candidate.complete_event_order_atom(
        context=context,
        receipt=measurement,
        passage_id=passage_id,
    )
    case = event_candidate.build_rc8j_case(atom=atom)
    warrant = candidate.issue_event_atom_warrant(
        case=case,
        authority_evaluator=lambda value: _rc8j(rc8j_root, value),
        key=ATOM_KEY,
        key_id=ATOM_KEY_ID,
    )
    return context, case, warrant


def _derive(
    *,
    case: dict[str, Any],
    warrant: dict[str, Any],
    proposition: candidate.TemporalProposition,
) -> candidate.TemporalRelationRecord:
    binding = candidate.issue_proposition_binding(
        proposition=proposition,
        key=PROP_KEY,
        key_id=PROP_KEY_ID,
    )
    return candidate.derive_temporal_relation(
        case=case,
        proposition=proposition,
        atom_warrant=warrant,
        atom_trusted_keys={ATOM_KEY_ID: ATOM_KEY},
        proposition_binding=binding,
        proposition_trusted_keys={PROP_KEY_ID: PROP_KEY},
    )


def _expect_refusal(code: str, fn: Callable[[], Any]) -> dict[str, Any]:
    try:
        fn()
    except candidate.RelationRefusal as exc:
        if exc.code != code:
            raise AssertionError(f"expected {code}, got {exc.code}: {exc.detail}") from exc
        return {"pass": True, "code": exc.code, "detail": exc.detail}
    raise AssertionError(f"expected refusal {code}")


def _tamper_mac(receipt: dict[str, Any]) -> dict[str, Any]:
    value = deepcopy(receipt)
    value["mac"] = "0" * 64
    return value


def execute(*, repo_root: Path, event_root: Path, rc8j_root: Path, cohort_path: Path) -> dict[str, Any]:
    _require_candidate_blobs(repo_root)
    _require_dependency(event_root, EVENT_HEAD, {EVENT_PATH: EVENT_BLOB})
    _require_dependency(rc8j_root, RC8J_HEAD, RC8J_BLOBS)
    event_module = _load_module("cal_event_relation_frozen_rc7fc", event_root / EVENT_PATH)
    cohort = json.loads(cohort_path.read_text(encoding="utf-8"))
    if cohort.get("candidate_freeze_before_cohort") != CANDIDATE_FREEZE:
        raise RuntimeError("cohort does not bind exact candidate freeze")

    claim_id = "TEMPORAL-CLAIM-001"
    relation_controls: dict[str, Any] = {}
    relation_failures = 0
    prepared: dict[str, tuple[dict[str, Any], dict[str, Any], candidate.TemporalProposition, candidate.TemporalRelationRecord]] = {}
    for row in cohort["relation_controls"]:
        prop_row = row["proposition"]
        proposition = _proposition(claim_id=claim_id, row=prop_row)
        _, case, warrant = _prepare_case(
            event_module=event_module,
            rc8j_root=rc8j_root,
            case_id=str(row["case_id"]),
            source=str(row["source"]),
            proposition=proposition,
        )
        relation = _derive(case=case, warrant=warrant, proposition=proposition)
        conclusion = candidate.compose_temporal_relations(
            proposition=proposition,
            relations=(relation,),
        )
        passed = (
            relation.relation == row["expected_relation"]
            and conclusion.disposition == row["expected_disposition"]
            and conclusion.verdict == row["expected_verdict"]
        )
        if not passed:
            relation_failures += 1
        relation_controls[str(row["case_id"])] = {
            "pass": passed,
            "relation": asdict(relation),
            "conclusion": asdict(conclusion),
        }
        prepared[str(row["case_id"])] = (case, warrant, proposition, relation)

    base_case, base_warrant, base_prop, base_relation = prepared["TR-P01-SAME-SUPPORT"]
    assert base_relation.relation == "SUPPORTS"

    # Weak same-claim proposition substitution control.
    mutated_prop = replace(base_prop, relation="AFTER", claim_text=base_prop.claim_text + ":after")
    weak_base = candidate.weak_claim_id_only_relation(
        case=base_case,
        proposition=base_prop,
        atom_warrant=base_warrant,
        atom_trusted_keys={ATOM_KEY_ID: ATOM_KEY},
    )
    weak_mutated = candidate.weak_claim_id_only_relation(
        case=base_case,
        proposition=mutated_prop,
        atom_warrant=base_warrant,
        atom_trusted_keys={ATOM_KEY_ID: ATOM_KEY},
    )
    weak_claim_id_control = (
        weak_base.relation == "SUPPORTS" and weak_mutated.relation == "REFUTES"
    )

    base_binding = candidate.issue_proposition_binding(
        proposition=base_prop,
        key=PROP_KEY,
        key_id=PROP_KEY_ID,
    )
    stale_direction = _expect_refusal(
        "PROPOSITION_DIGEST_MISMATCH",
        lambda: candidate.derive_temporal_relation(
            case=base_case,
            proposition=mutated_prop,
            atom_warrant=base_warrant,
            atom_trusted_keys={ATOM_KEY_ID: ATOM_KEY},
            proposition_binding=base_binding,
            proposition_trusted_keys={PROP_KEY_ID: PROP_KEY},
        ),
    )
    left_sub_prop = replace(
        base_prop,
        left_event=candidate.EventSemantics("mallory", "review", "dossier", "positive"),
    )
    stale_left_event = _expect_refusal(
        "PROPOSITION_DIGEST_MISMATCH",
        lambda: candidate.derive_temporal_relation(
            case=base_case,
            proposition=left_sub_prop,
            atom_warrant=base_warrant,
            atom_trusted_keys={ATOM_KEY_ID: ATOM_KEY},
            proposition_binding=base_binding,
            proposition_trusted_keys={PROP_KEY_ID: PROP_KEY},
        ),
    )
    changed_text_prop = replace(base_prop, claim_text=base_prop.claim_text + " changed")
    stale_claim_text = _expect_refusal(
        "PROPOSITION_DIGEST_MISMATCH",
        lambda: candidate.verify_proposition_binding(
            proposition=changed_text_prop,
            receipt=base_binding,
            trusted_keys={PROP_KEY_ID: PROP_KEY},
        ),
    )
    wrong_prop_key = _expect_refusal(
        "PROPOSITION_MAC_MISMATCH",
        lambda: candidate.verify_proposition_binding(
            proposition=base_prop,
            receipt=base_binding,
            trusted_keys={PROP_KEY_ID: b"wrong-proposition-key-material-000000000000001"},
        ),
    )
    prop_mac_tamper = _expect_refusal(
        "PROPOSITION_MAC_MISMATCH",
        lambda: candidate.verify_proposition_binding(
            proposition=base_prop,
            receipt=_tamper_mac(base_binding),
            trusted_keys={PROP_KEY_ID: PROP_KEY},
        ),
    )

    swapped_prop = prepared["TR-P03-SWAPPED-INVERSE-SUPPORT"][2]
    # Rebind exact claim ID/text shape to the base claim identity for stale-receipt control.
    swapped_same_claim = replace(swapped_prop, claim_id=base_prop.claim_id)
    stale_swapped = _expect_refusal(
        "PROPOSITION_DIGEST_MISMATCH",
        lambda: candidate.derive_temporal_relation(
            case=base_case,
            proposition=swapped_same_claim,
            atom_warrant=base_warrant,
            atom_trusted_keys={ATOM_KEY_ID: ATOM_KEY},
            proposition_binding=base_binding,
            proposition_trusted_keys={PROP_KEY_ID: PROP_KEY},
        ),
    )
    fresh_swapped_binding = candidate.issue_proposition_binding(
        proposition=swapped_same_claim,
        key=PROP_KEY,
        key_id=PROP_KEY_ID,
    )
    fresh_swapped_relation = candidate.derive_temporal_relation(
        case=base_case,
        proposition=swapped_same_claim,
        atom_warrant=base_warrant,
        atom_trusted_keys={ATOM_KEY_ID: ATOM_KEY},
        proposition_binding=fresh_swapped_binding,
        proposition_trusted_keys={PROP_KEY_ID: PROP_KEY},
    )
    assert fresh_swapped_relation.relation == "SUPPORTS"

    # Atom-warrant stale replay controls.
    changed_case_relation = deepcopy(base_case)
    changed_case_relation["proposal"]["fields"]["temporal_relation"] = "AFTER"
    stale_atom_relation = _expect_refusal(
        "ATOM_WARRANT_SUBJECT_MISMATCH",
        lambda: candidate.verify_event_atom_warrant(
            case=changed_case_relation,
            receipt=base_warrant,
            trusted_keys={ATOM_KEY_ID: ATOM_KEY},
        ),
    )
    changed_case_consistent = deepcopy(changed_case_relation)
    changed_case_consistent["field_warrants"]["temporal_relation"]["value"] = "AFTER"
    stale_atom_consistent = _expect_refusal(
        "ATOM_WARRANT_SUBJECT_MISMATCH",
        lambda: candidate.verify_event_atom_warrant(
            case=changed_case_consistent,
            receipt=base_warrant,
            trusted_keys={ATOM_KEY_ID: ATOM_KEY},
        ),
    )
    atom_identity_controls: dict[str, Any] = {}
    for name, mutate in {
        "source": lambda case: case.__setitem__("raw_source_id", "FOREIGN-SOURCE"),
        "claim": lambda case: case.__setitem__("raw_claim_id", "FOREIGN-CLAIM"),
        "atom": lambda case: case.__setitem__("target_atom_id", "event-atom:foreign"),
    }.items():
        mutated = deepcopy(base_case)
        mutate(mutated)
        atom_identity_controls[name] = _expect_refusal(
            "ATOM_WARRANT_SUBJECT_MISMATCH",
            lambda mutated=mutated: candidate.verify_event_atom_warrant(
                case=mutated,
                receipt=base_warrant,
                trusted_keys={ATOM_KEY_ID: ATOM_KEY},
            ),
        )
    wrong_atom_key = _expect_refusal(
        "ATOM_WARRANT_MAC_MISMATCH",
        lambda: candidate.verify_event_atom_warrant(
            case=base_case,
            receipt=base_warrant,
            trusted_keys={ATOM_KEY_ID: b"wrong-atom-key-material-00000000000000000000001"},
        ),
    )
    atom_mac_tamper = _expect_refusal(
        "ATOM_WARRANT_MAC_MISMATCH",
        lambda: candidate.verify_event_atom_warrant(
            case=base_case,
            receipt=_tamper_mac(base_warrant),
            trusted_keys={ATOM_KEY_ID: ATOM_KEY},
        ),
    )
    nonwarranted_issuance = _expect_refusal(
        "ATOM_WARRANT_ISSUANCE_REFUSED",
        lambda: candidate.issue_event_atom_warrant(
            case=changed_case_relation,
            authority_evaluator=lambda value: _rc8j(rc8j_root, value),
            key=ATOM_KEY,
            key_id=ATOM_KEY_ID,
        ),
    )

    # Composition uses separately warranted evidence atoms against one exact proposition.
    composition_prop = base_prop
    sources = cohort["composition_sources"]
    composition_relations: dict[str, candidate.TemporalRelationRecord] = {}
    for name, source in sources.items():
        _, case, warrant = _prepare_case(
            event_module=event_module,
            rc8j_root=rc8j_root,
            case_id=f"COMP-{name.upper()}",
            source=str(source),
            proposition=composition_prop,
        )
        composition_relations[name] = _derive(
            case=case,
            warrant=warrant,
            proposition=composition_prop,
        )
    assert composition_relations["support"].relation == "SUPPORTS"
    assert composition_relations["refute"].relation == "REFUTES"
    assert composition_relations["irrelevant"].relation == "IRRELEVANT"
    assert composition_relations["unresolved"].relation == "UNRESOLVED"

    mixed_ab = candidate.compose_temporal_relations(
        proposition=composition_prop,
        relations=(composition_relations["support"], composition_relations["refute"]),
    )
    mixed_ba = candidate.compose_temporal_relations(
        proposition=composition_prop,
        relations=(composition_relations["refute"], composition_relations["support"]),
    )
    mixed_order_invariant = asdict(mixed_ab) == asdict(mixed_ba)
    assert mixed_ab.disposition == "abstained"
    assert mixed_ab.reason_code == "mixed_categorical_relations"
    support_irrelevant = candidate.compose_temporal_relations(
        proposition=composition_prop,
        relations=(composition_relations["support"], composition_relations["irrelevant"]),
    )
    assert support_irrelevant.verdict == "supported"
    support_unresolved = candidate.compose_temporal_relations(
        proposition=composition_prop,
        relations=(composition_relations["support"], composition_relations["unresolved"]),
    )
    assert support_unresolved.disposition == "abstained"
    assert support_unresolved.reason_code == "unresolved_categorical_relation"

    mismatched_relation = prepared["TR-P02-SAME-REFUTE"][3]
    composition_prop_mismatch = _expect_refusal(
        "COMPOSITION_PROPOSITION_MISMATCH",
        lambda: candidate.compose_temporal_relations(
            proposition=base_prop,
            relations=(base_relation, mismatched_relation),
        ),
    )
    nonwarranted = replace(base_relation, warranted=False)
    nonwarranted_composition = _expect_refusal(
        "COMPOSITION_NONWARRANTED_DECIDING_RELATION",
        lambda: candidate.compose_temporal_relations(
            proposition=base_prop,
            relations=(nonwarranted,),
        ),
    )

    diagnostic_case = deepcopy(base_case)
    diagnostic_case["score"] = 0.99
    diagnostic_case["confidence"] = 0.01
    diagnostic_case["reader_agreement_count"] = 999
    diagnostic_binding = candidate.issue_proposition_binding(
        proposition=base_prop,
        key=PROP_KEY,
        key_id=PROP_KEY_ID,
    )
    diagnostic_relation = candidate.derive_temporal_relation(
        case=diagnostic_case,
        proposition=base_prop,
        atom_warrant=base_warrant,
        atom_trusted_keys={ATOM_KEY_ID: ATOM_KEY},
        proposition_binding=diagnostic_binding,
        proposition_trusted_keys={PROP_KEY_ID: PROP_KEY},
    )
    diagnostic_invariant = diagnostic_relation == base_relation

    forbidden_names = {"score", "confidence", "threshold", "channel", "relation_hint"}
    signatures = {
        "proposition": set(inspect.signature(candidate.TemporalProposition).parameters),
        "derive": set(inspect.signature(candidate.derive_temporal_relation).parameters),
        "compose": set(inspect.signature(candidate.compose_temporal_relations).parameters),
    }
    forbidden_interface_absent = all(not (forbidden_names & names) for names in signatures.values())
    try:
        candidate.TemporalProposition(
            claim_id=base_prop.claim_id,
            claim_text=base_prop.claim_text,
            left_event=base_prop.left_event,
            relation=base_prop.relation,
            right_event=base_prop.right_event,
            score=0.99,  # type: ignore[call-arg]
        )
    except TypeError:
        scalar_input_rejected = True
    else:
        scalar_input_rejected = False

    proposition_controls = {
        "weak_claim_id_only_control": {
            "pass": weak_claim_id_control,
            "baseline_relation": weak_base.relation,
            "mutated_relation": weak_mutated.relation,
        },
        "stale_direction": stale_direction,
        "stale_left_event": stale_left_event,
        "stale_claim_text": stale_claim_text,
        "wrong_key": wrong_prop_key,
        "mac_tamper": prop_mac_tamper,
        "stale_swapped_inverse": stale_swapped,
        "fresh_swapped_inverse_relation": fresh_swapped_relation.relation,
    }
    atom_controls = {
        "stale_relation": stale_atom_relation,
        "stale_consistent_payload": stale_atom_consistent,
        "identity_substitutions": atom_identity_controls,
        "wrong_key": wrong_atom_key,
        "mac_tamper": atom_mac_tamper,
        "nonwarranted_issuance": nonwarranted_issuance,
    }
    composition_controls = {
        "mixed": asdict(mixed_ab),
        "mixed_order_invariant": mixed_order_invariant,
        "support_plus_irrelevant": asdict(support_irrelevant),
        "support_plus_unresolved": asdict(support_unresolved),
        "proposition_mismatch": composition_prop_mismatch,
        "nonwarranted_deciding_relation": nonwarranted_composition,
    }
    all_pass = (
        relation_failures == 0
        and weak_claim_id_control
        and fresh_swapped_relation.relation == "SUPPORTS"
        and mixed_order_invariant
        and diagnostic_invariant
        and forbidden_interface_absent
        and scalar_input_rejected
    )
    disposition = "SUPPORTED_WITH_BOUNDS" if all_pass else "FALSIFIED_EVENT_ORDER_RELATION_CANDIDATE"

    return {
        "schema": SCHEMA,
        "research_disposition": disposition,
        "candidate_freeze": CANDIDATE_FREEZE,
        "relation_controls": relation_controls,
        "proposition_binding_controls": proposition_controls,
        "atom_warrant_controls": atom_controls,
        "composition_controls": composition_controls,
        "interface_controls": {
            "diagnostic_metadata_invariant": diagnostic_invariant,
            "forbidden_scalar_or_polarity_names_absent": forbidden_interface_absent,
            "scalar_input_rejected": scalar_input_rejected,
        },
        "summary": {
            "relation_control_failures": relation_failures,
            "weak_claim_id_control_valid": weak_claim_id_control,
            "mixed_order_invariant": mixed_order_invariant,
            "diagnostic_metadata_invariant": diagnostic_invariant,
            "unsafe_nonwarranted_deciding_relation": False,
        },
        "interpretation": {
            "negative_event_deciding_semantics_established": False,
            "cross_passage_temporal_inference_established": False,
            "contract_c_temporal_projection_established": False,
            "released_cal_v1_causal_role": False,
            "production_promotion_authorized": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--event-root", type=Path, required=True)
    parser.add_argument("--rc8j-root", type=Path, required=True)
    parser.add_argument("--cohort", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = execute(
        repo_root=args.repo_root.resolve(),
        event_root=args.event_root.resolve(),
        rc8j_root=args.rc8j_root.resolve(),
        cohort_path=args.cohort.resolve(),
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    print(json.dumps({"research_disposition": result["research_disposition"], **result["summary"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
