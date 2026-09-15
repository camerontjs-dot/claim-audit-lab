from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from claim_audit_lab.production_v1.bundle_input import BundleTargetValidationError, load_target


def test_canonical_target_rejects_proposition_id_alias(tmp_path: Path) -> None:
    claim = "Women had a higher rate than Men."
    target = {
        "claim_id": "claim-1",
        "proposition": {
            "proposition_id": "alias-1",
            "text_sha256": hashlib.sha256(claim.encode("utf-8")).hexdigest(),
            "semantic_family": "strict_comparison",
            "fields": {
                "lhs_entity": "Women",
                "rhs_entity": "Men",
                "comparison_direction": "MORE_THAN",
            },
        },
    }
    path = tmp_path / "target.json"
    path.write_text(json.dumps(target), encoding="utf-8")

    with pytest.raises(BundleTargetValidationError, match="exact Contract B claim_id"):
        load_target(path)
