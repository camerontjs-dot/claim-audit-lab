"""Research-only native Contract E-style descriptor emission for CAL assessment authority."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class AssessmentDescriptor:
    participant: str
    actor: str
    operation: str
    target_class: str
    target_id: str
    current_hash: str
    authority_domain: str


def from_contract_b_fixture(root: Path) -> AssessmentDescriptor:
    bundle = root / "tests/fixtures/cb/evidence-bundle-minimal"
    manifest = yaml.safe_load((bundle / "bundle_manifest.yaml").read_text())
    claim = yaml.safe_load((bundle / "claims/clm-001.yaml").read_text())
    return AssessmentDescriptor(
        participant="claim-audit-lab",
        actor="claim-audit-lab",
        operation="assessment.issue",
        target_class="contract_b_claim",
        target_id=f"{manifest['bundle_id']}::{claim['claim_id']}",
        current_hash=manifest["bundle"]["bundle_hash"],
        authority_domain="assessment_mandate",
    )
