"""Emit frozen semantic-authority receipts for the preregistered RC2 cases."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from research.semantic_authority_jurisdiction_rc2.authority import (
    Quantity,
    assess_absence_boundary,
    assess_numeric_relation,
)
from research.semantic_authority_jurisdiction_rc2.native_descriptor import (
    from_contract_b_fixture,
)


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    receipts = {
        "CG-12a": asdict(
            assess_numeric_relation(
                claim=Quantity(
                    "deviation_recording_deadline",
                    "deviation_general",
                    5,
                    "business_day",
                    "max",
                ),
                evidence=Quantity(
                    "deviation_recording_deadline",
                    "deviation_general",
                    1,
                    "business_day",
                    "max",
                ),
                target_id="CG-12a",
                receipt_id="num-cg12a",
            )
        ),
        "CG-24-wrong-scope": asdict(
            assess_numeric_relation(
                claim=Quantity(
                    "deviation_recording_deadline",
                    "building_4",
                    5,
                    "business_day",
                    "max",
                ),
                evidence=Quantity(
                    "deviation_recording_deadline",
                    "contract_lab",
                    5,
                    "business_day",
                    "max",
                ),
                target_id="CG-24",
                receipt_id="num-cg24-wrong",
            )
        ),
        "CG-24-in-scope": asdict(
            assess_numeric_relation(
                claim=Quantity(
                    "deviation_recording_deadline",
                    "building_4",
                    5,
                    "business_day",
                    "max",
                ),
                evidence=Quantity(
                    "deviation_recording_deadline",
                    "building_4",
                    1,
                    "business_day",
                    "max",
                ),
                target_id="CG-24",
                receipt_id="num-cg24-right",
            )
        ),
        "CG-08a": asdict(
            assess_absence_boundary(
                boundary="exhaustive",
                topic="storage conditions for retention samples",
                named_gaps=(),
                claimed_material_is_named_gap=False,
                target_id="CG-08a",
                receipt_id="boundary-cg08a",
            )
        ),
        "CG-08b": asdict(
            assess_absence_boundary(
                boundary="bounded",
                topic="storage conditions for retention samples",
                named_gaps=(),
                claimed_material_is_named_gap=False,
                target_id="CG-08b",
                receipt_id="boundary-cg08b",
            )
        ),
        "CG-21": asdict(
            assess_absence_boundary(
                boundary="named_missing_material",
                topic="storage conditions for retention samples",
                named_gaps=(
                    "storage conditions for retention samples",
                    "photostability chamber calibration",
                ),
                claimed_material_is_named_gap=True,
                target_id="CG-21",
                receipt_id="boundary-cg21",
            )
        ),
        "CG-09a": asdict(
            assess_absence_boundary(
                boundary="exhaustive",
                topic="deviations detected after batch release",
                named_gaps=(),
                claimed_material_is_named_gap=False,
                target_id="CG-09a",
                receipt_id="boundary-cg09a",
            )
        ),
        "CG-09b": asdict(
            assess_absence_boundary(
                boundary="bounded",
                topic="deviations detected after batch release",
                named_gaps=(),
                claimed_material_is_named_gap=False,
                target_id="CG-09b",
                receipt_id="boundary-cg09b",
            )
        ),
        "CG-22": asdict(
            assess_absence_boundary(
                boundary="named_missing_material",
                topic="deviations detected after batch release",
                named_gaps=("escalation of repeat deviations",),
                claimed_material_is_named_gap=False,
                target_id="CG-22",
                receipt_id="boundary-cg22",
            )
        ),
    }
    descriptor = asdict(from_contract_b_fixture(root))
    result = {
        "schema": "cal-semantic-authority-jurisdiction-rc2",
        "production_changed": False,
        "threshold_tuning": False,
        "new_model_execution": False,
        "cal_native_descriptor": descriptor,
        "semantic_receipts": receipts,
    }
    out = root / "artifacts/semantic-authority-jurisdiction-rc2/RESULTS.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
