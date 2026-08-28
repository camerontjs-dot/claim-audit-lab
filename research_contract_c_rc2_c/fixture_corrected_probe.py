"""RC2-C probe with the recorded irrelevant-state fixture correction only."""

from __future__ import annotations

from claim_audit_lab.models import EvidenceBundle

from research_contract_c_rc2_c import dependency_probe as base

_ORIGINAL_FROZEN_INPUTS = base.frozen_inputs


def frozen_inputs(
    *,
    counterevidence: bool = True,
    irrelevant_support: bool = False,
):
    """Keep unrelated bundle evidence real but outside the candidate set."""
    claim, bundle, support, counters = _ORIGINAL_FROZEN_INPUTS(
        counterevidence=counterevidence,
        irrelevant_support=False,
    )
    if irrelevant_support:
        unrelated = base._source(
            "source-irrelevant",
            "excerpt-irrelevant",
            "A separate note describes report formatting.",
        )
        bundle = EvidenceBundle(sources=[*bundle.sources, unrelated])
    return claim, bundle, support, counters


base.frozen_inputs = frozen_inputs
run_experiment = base.run_experiment


if __name__ == "__main__":
    raise SystemExit(base.main())
