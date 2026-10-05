"""Dependence and topology fixtures. These are not natural-claim results."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_CANDIDATE = Path(__file__).resolve().parent
sys.path.insert(0, str(_CANDIDATE))

from codec import canonical, digest  # noqa: E402
from dispatch import run_process  # noqa: E402
from evaluate import envelope_bytes, evaluate_envelope  # noqa: E402
from synthesize import synthesize  # noqa: E402

POLICY = {
    "schema": "cal-independent-judges-natural-rc1-policy",
    "calibration_status": "MECHANICAL_FIXTURE_POLICY",
    "minimum": "1",
    "lanes": {
        "quantity_relation": {
            "role": "relation",
            "weight": "1",
            "group": "quantity-text",
            "required": False,
        },
        "event_order": {
            "role": "relation",
            "weight": "1",
            "group": "event-order-text",
            "required": False,
        },
        "scope_guard": {
            "role": "guard",
            "weight": "0",
            "group": "scope-guard",
            "required": True,
        },
        "attribution_guard": {
            "role": "guard",
            "weight": "0",
            "group": "attribution-guard",
            "required": True,
        },
    },
}


def _support_bytes() -> bytes:
    return envelope_bytes(
        "Output decreased 2 percent in 2020.",
        [{"id": "e1", "text": "Output decreased 2 percent in 2020."}],
    )


def _receipt(process_id: str, role: str, conclusion: str, raw: bytes, group_role: str = "relation") -> dict:
    del group_role
    return {
        "process_id": process_id,
        "input_sha256": digest(raw),
        "execution": "completed",
        "applicability": "applicable" if conclusion != "not_applicable" else "not_applicable",
        "role": role,
        "conclusion": conclusion,
        "warrant": "qualified",
        "material_loss": False,
        "local_material_conflict": False,
    }


def _check(name: str, condition: bool, failures: list[str]) -> None:
    if not condition:
        failures.append(name)


def main() -> int:
    failures: list[str] = []
    support = _support_bytes()
    result = evaluate_envelope(support, POLICY)
    _check("fixture support arm C", result["C"]["conclusion"] == "supported", failures)
    _check("fixture support arm B", result["B"]["conclusion"] == "supported", failures)
    _check("router runs quantity", "quantity_relation" in result["R"]["router"]["processes"], failures)

    shifted = envelope_bytes(
        "Output decreased 2 percent in 2021.",
        [{"id": "e1", "text": "Output decreased 2 percent in 2020."}],
    )
    shifted_result = evaluate_envelope(shifted, POLICY)
    _check("original year mismatch abstains", shifted_result["C"]["conclusion"] == "not_checkable", failures)
    _check("lossy year strip false-supports", shifted_result["B"]["conclusion"] == "supported", failures)
    _check("lossy transform records removal", shifted_result["B"]["loss"]["material_tokens_removed"] is True, failures)

    conflict = envelope_bytes(
        "Output decreased 2 percent in 2020.",
        [
            {"id": "e1", "text": "Output decreased 2 percent in 2020."},
            {"id": "e2", "text": "Output increased 2 percent in 2020."},
        ],
    )
    conflict_result = evaluate_envelope(conflict, POLICY)
    _check("live passage conflict abstains", conflict_result["C"]["conclusion"] == "not_checkable", failures)

    # Clone cap: two copies, same group, threshold 2. Summing would decide. The cap must not.
    cap_policy = json.loads(json.dumps(POLICY))
    cap_policy["minimum"] = "2"
    cap_policy["lanes"]["quantity_relation_clone"] = {
        "role": "relation",
        "weight": "1",
        "group": "quantity-text",
        "required": False,
    }
    first = run_process(support, lane="quantity_relation")
    second = run_process(support, lane="quantity_relation", process_id="quantity_relation_clone")
    idle_event = _receipt("event_order", "relation", "not_applicable", support)
    idle_event["execution"] = "completed"
    guards = [
        run_process(support, lane="scope_guard")["receipt"],
        run_process(support, lane="attribution_guard")["receipt"],
    ]
    cap = synthesize(
        support,
        [first["receipt"], second["receipt"], idle_event, *guards],
        cap_policy,
    )
    _check("clone cap does not reach threshold 2", cap["conclusion"] == "not_checkable", failures)
    _check("clone score stays at one", cap["scores"]["supports"] == "1", failures)

    # Same bytes, two prompt names, still one group.
    os.environ["CAL_PROMPT_NAME"] = "prompt-alpha"
    prompted_a = run_process(support, lane="quantity_relation", process_id="quantity_relation")
    os.environ["CAL_PROMPT_NAME"] = "prompt-beta"
    prompted_b = run_process(support, lane="quantity_relation", process_id="quantity_relation_clone")
    os.environ.pop("CAL_PROMPT_NAME", None)
    prompted = synthesize(
        support,
        [prompted_a["receipt"], prompted_b["receipt"], idle_event, *guards],
        cap_policy,
    )
    _check("prompt name does not add weight", prompted["conclusion"] == "not_checkable", failures)
    _check(
        "prompt names recorded",
        prompted_a["receipt"].get("prompt_name") == "prompt-alpha"
        and prompted_b["receipt"].get("prompt_name") == "prompt-beta",
        failures,
    )

    # Self-awarded weight cannot cross a threshold the policy weight misses.
    scored = run_process(support, lane="quantity_relation", self_score=True)
    self_policy = json.loads(json.dumps(POLICY))
    self_policy["minimum"] = "2"
    self_result = synthesize(
        support,
        [scored["receipt"], idle_event, *guards],
        self_policy,
    )
    _check("self score ignored", self_result["conclusion"] == "not_checkable", failures)
    _check("self score marked ignored", any(key.endswith(":self_score") for key in self_result["exclusions"]), failures)

    # Irrelevant lanes do not force abstention when a real lane supports.
    extras = []
    wide = json.loads(json.dumps(POLICY))
    for index in range(6):
        process_id = f"event_order_extra_{index}"
        wide["lanes"][process_id] = {
            "role": "relation",
            "weight": "3",
            "group": f"irrelevant-{index}",
            "required": False,
        }
        extra = run_process(support, lane="event_order", process_id=process_id)["receipt"]
        extras.append(extra)
    proliferated = synthesize(
        support,
        [first["receipt"], idle_event, *extras, *guards],
        wide,
    )
    _check("irrelevant proliferation still supports", proliferated["conclusion"] == "supported", failures)

    # Minority refutation on sealed receipts. Live copies of one judge cannot
    # disagree with themselves on identical bytes; this control is the weighting rule.
    minority_policy = {
        "schema": "control",
        "minimum": "1",
        "lanes": {
            "support_a": {"role": "relation", "weight": "1", "group": "correlated", "required": False},
            "support_b": {"role": "relation", "weight": "1", "group": "correlated", "required": False},
            "support_c": {"role": "relation", "weight": "1", "group": "correlated", "required": False},
            "minority_refute": {"role": "relation", "weight": "1", "group": "minority", "required": False},
        },
    }
    raw = canonical({"claim": "control", "evidence": []})
    receipts = [
        _receipt("support_a", "relation", "supports", raw),
        _receipt("support_b", "relation", "supports", raw),
        _receipt("support_c", "relation", "supports", raw),
        _receipt("minority_refute", "relation", "refutes", raw),
    ]
    minority = synthesize(raw, receipts, minority_policy)
    _check("minority refutation blocks", minority["conclusion"] == "not_checkable", failures)
    _check("conflict blocker present", "material_conflict" in minority["blockers"], failures)
    _check("correlated supports do not sum past one", minority["scores"]["supports"] == "1", failures)

    duplicate = envelope_bytes(
        "Output decreased 2 percent in 2020.",
        [
            {"id": "e1", "text": "Output decreased 2 percent in 2020."},
            {"id": "e2", "text": "Output decreased 2 percent in 2020."},
        ],
    )
    duplicated = evaluate_envelope(duplicate, POLICY)
    _check("duplicate passage does not change support", duplicated["C"]["conclusion"] == "supported", failures)
    _check(
        "duplicate passage score stays one",
        duplicated["C"]["synthesis"]["scores"]["supports"] == "1",
        failures,
    )

    # Required scope violation against an otherwise supportive relation receipt.
    violated_guard = _receipt("scope_guard", "guard", "violated", support)
    clean_attr = _receipt("attribution_guard", "guard", "not_applicable", support)
    scoped = synthesize(
        support,
        [first["receipt"], idle_event, violated_guard, clean_attr],
        POLICY,
    )
    _check("scope violation blocks support", scoped["conclusion"] == "not_checkable", failures)
    _check("scope violation blocker present", "guard_violation" in scoped["blockers"], failures)

    report = {"passed": not failures, "failures": failures}
    print(json.dumps(report, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
