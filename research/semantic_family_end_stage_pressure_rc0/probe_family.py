from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


def _activate(root: Path) -> None:
    sys.path.insert(0, str(root))
    sys.path.insert(0, str(root / "src"))


def _context(text: str, family: Any) -> Any:
    from claim_audit_lab.production_v1.semantic.models import (
        AdmittedPassage,
        AuditContext,
        EvidenceWorld,
        TypedProposition,
    )

    digest = hashlib.sha256(text.encode()).hexdigest()
    passage = AdmittedPassage.create("p1", "pressure-source", text)
    world = EvidenceWorld.create(
        "1.2.0",
        f"pressure-{digest[:12]}",
        f"sha256:{hashlib.sha256(('bundle:' + text).encode()).hexdigest()}",
        (passage,),
        {
            "search_scope": {"corpus": "semantic-family-end-stage-pressure-rc0"},
            "outcome": {"state": "unknown", "value": None},
            "limitations": [],
        },
    )
    proposition = TypedProposition.create(
        f"pressure-{digest[:12]}",
        family,
        {},
        text_sha256=digest,
    )
    return AuditContext(text, proposition, world)


def _not_warranted(stage: str, detail: str) -> dict[str, str]:
    return {"status": "NOT_WARRANTED", "stage": stage, "detail": detail}


def _warranted() -> dict[str, str]:
    return {"status": "WARRANTED", "stage": "authority", "detail": ""}


def probe_strict(text: str) -> dict[str, str]:
    from claim_audit_lab.production_v1.semantic.measurements import (
        measure_strict_comparison,
    )
    from claim_audit_lab.production_v1.semantic.models import SemanticFamily
    from research.strict_comparison_gate1b_authority_rc1.candidate import (
        complete_and_warrant_strict,
    )

    context = _context(text, SemanticFamily.STRICT_COMPARISON)
    receipt = measure_strict_comparison(context, "p1")
    status = str(receipt.raw_measurement().get("status"))
    if status != "CLAIMED":
        return _not_warranted("measurement", status)
    try:
        complete_and_warrant_strict(context, receipt, "p1")
    except Exception as exc:
        return _not_warranted("authority", f"{type(exc).__name__}: {exc}")
    return _warranted()


def probe_event_order(text: str) -> dict[str, str]:
    from claim_audit_lab.production_v1.semantic.measurements import (
        measure_direct_event_order,
    )
    from claim_audit_lab.production_v1.semantic.models import SemanticFamily
    from research.direct_event_order_gate1b_authority_rc1.candidate import (
        complete_and_warrant_event_order,
    )

    context = _context(text, SemanticFamily.DIRECT_EVENT_ORDER)
    receipt = measure_direct_event_order(context, "p1")
    status = str(receipt.raw_measurement().get("status"))
    if status != "CLAIMED":
        return _not_warranted("measurement", status)
    try:
        complete_and_warrant_event_order(context, receipt, "p1")
    except Exception as exc:
        return _not_warranted("authority", f"{type(exc).__name__}: {exc}")
    return _warranted()


def probe_deontic(text: str) -> dict[str, str]:
    from research.deontic_gate1b_authority_rc0.candidate import (
        complete_and_warrant_deontic,
    )
    from research.deontic_measurement_machinery_rc0.candidate import direct_grammar
    from research.deontic_measurement_machinery_rc0.cohort import Status

    measured = direct_grammar(text)
    if measured.status is not Status.CLAIMED or measured.norm is None:
        return _not_warranted("measurement", measured.status.value)
    try:
        complete_and_warrant_deontic(text, measured.norm)
    except Exception as exc:
        return _not_warranted("authority", f"{type(exc).__name__}: {exc}")
    return _warranted()


def probe_population(text: str) -> dict[str, str]:
    from research.population_gate1b_authority_rc0.candidate import (
        complete_and_warrant_population,
    )
    from research.population_measurement_machinery_rc0.candidate import (
        conservative_hybrid,
    )
    from research.population_measurement_machinery_rc0.cohort import Status

    measured = conservative_hybrid(text)
    if measured.status is not Status.CLAIMED or measured.atom is None:
        return _not_warranted("measurement", measured.status.value)
    try:
        complete_and_warrant_population(text, measured.atom)
    except Exception as exc:
        return _not_warranted("authority", f"{type(exc).__name__}: {exc}")
    return _warranted()


def probe_scalar(text: str) -> dict[str, str]:
    from research.scalar_gate1b_authority_rc0.candidate import (
        complete_and_warrant_scalar,
    )
    from research.scalar_measurement_machinery_rc0.candidate import (
        conservative_numeric_hybrid,
    )
    from research.scalar_measurement_machinery_rc0.cohort import BATCH_YIELD, Status

    measured = conservative_numeric_hybrid(text, BATCH_YIELD)
    if measured.status is not Status.CLAIMED or measured.atom is None:
        return _not_warranted("measurement", measured.status.value)
    try:
        complete_and_warrant_scalar(text, BATCH_YIELD, measured.atom)
    except Exception as exc:
        return _not_warranted("authority", f"{type(exc).__name__}: {exc}")
    return _warranted()


def probe_occurrence(text: str) -> dict[str, str]:
    from research.event_occurrence_gate1b_authority_rc0.candidate import (
        complete_and_warrant_event_occurrence,
    )
    from research.event_occurrence_measurement_machinery_rc0.candidate import (
        conservative_event_hybrid,
    )
    from research.event_occurrence_measurement_machinery_rc0.cohort import Status

    measured = conservative_event_hybrid(text)
    if measured.status is not Status.CLAIMED or measured.atom is None:
        return _not_warranted("measurement", measured.status.value)
    try:
        complete_and_warrant_event_occurrence(text, measured.atom)
    except Exception as exc:
        return _not_warranted("authority", f"{type(exc).__name__}: {exc}")
    return _warranted()


def probe_attribute(text: str) -> dict[str, str]:
    from research.attribute_state_gate1b_authority_rc0.candidate import (
        complete_and_warrant_attribute_state,
    )
    from research.attribute_state_measurement_machinery_rc1.candidate import (
        conservative_state_hybrid,
    )
    from research.attribute_state_measurement_machinery_rc1.cohort import Status

    measured = conservative_state_hybrid(text)
    if measured.status is not Status.CLAIMED or measured.atom is None:
        return _not_warranted("measurement", measured.status.value)
    try:
        complete_and_warrant_attribute_state(text, measured.atom)
    except Exception as exc:
        return _not_warranted("authority", f"{type(exc).__name__}: {exc}")
    return _warranted()


def probe_typed(text: str) -> dict[str, str]:
    from research.typed_binary_gate1b_authority_rc1.candidate import (
        complete_and_warrant_typed_binary,
    )
    from research.typed_binary_measurement_machinery_rc1.candidate import (
        conservative_relation_hybrid,
    )
    from research.typed_binary_measurement_machinery_rc1.cohort import Status

    measured = conservative_relation_hybrid(text)
    if measured.status is not Status.CLAIMED or measured.atom is None:
        return _not_warranted("measurement", measured.status.value)
    try:
        complete_and_warrant_typed_binary(text, measured.atom)
    except Exception as exc:
        return _not_warranted("authority", f"{type(exc).__name__}: {exc}")
    return _warranted()


def probe_causal(text: str) -> dict[str, str]:
    from research.causal_gate1b_authority_rc0.candidate import (
        complete_and_warrant_causal_assertion,
    )
    from research.causal_measurement_machinery_rc0.candidate import (
        conservative_assertion_hybrid,
    )
    from research.causal_measurement_machinery_rc0.cohort import Status

    measured = conservative_assertion_hybrid(text)
    if measured.status is not Status.CLAIMED or measured.atom is None:
        return _not_warranted("measurement", measured.status.value)
    try:
        complete_and_warrant_causal_assertion(text, measured.atom)
    except Exception as exc:
        return _not_warranted("authority", f"{type(exc).__name__}: {exc}")
    return _warranted()


PROBES = {
    "strict_comparison": probe_strict,
    "direct_event_order": probe_event_order,
    "deontic_norm": probe_deontic,
    "population_membership": probe_population,
    "scalar_value": probe_scalar,
    "event_occurrence": probe_occurrence,
    "attribute_state": probe_attribute,
    "typed_binary_relation": probe_typed,
    "explicit_causal_assertion": probe_causal,
}


def main() -> None:
    family = sys.argv[1]
    root = Path(sys.argv[2]).resolve()
    cases_path = Path(sys.argv[3]).resolve()
    _activate(root)

    probe = PROBES[family]
    cases = json.loads(cases_path.read_text())
    rows = []
    for case in cases:
        try:
            observed = probe(case["text"])
        except Exception as exc:
            observed = {
                "status": "PROBE_ERROR",
                "stage": "probe",
                "detail": f"{type(exc).__name__}: {exc}",
            }
        rows.append(
            {
                "case_id": case["case_id"],
                "family": family,
                **observed,
            }
        )
    print(json.dumps(rows, sort_keys=True))


if __name__ == "__main__":
    main()
