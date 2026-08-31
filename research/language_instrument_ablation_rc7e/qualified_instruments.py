"""Pre-held-out corrected wrappers for RC7E.

These wrappers preserve the original preregistered adapters while making only
pre-held-out apparatus corrections discovered before any held-out corpus exists.
"""
from __future__ import annotations

from collections import defaultdict

from research.language_instrument_ablation_rc7e.contract import make_receipt
from research.language_instrument_ablation_rc7e.equivalence import atom_key
from research.language_instrument_ablation_rc7e.instruments import (
    DebertaNLI,
    SuParSDP,
    instrument_identities,
)


class QualifiedSuParSDP(SuParSDP):
    """Preserved unavailable SuPar lane after bounded pre-held-out qualification.

    The documented model alias was corrected and the exact upstream checkpoint
    then failed under modern PyTorch safe deserialization. RC7E does not weaken
    pickle safety or pin an obsolete PyTorch solely to retain category coverage.
    """

    identity = {
        **SuParSDP.identity,
        "model": "biaffine-sdp-en",
        "preregistered_model_alias": "sdp-biaffine-en",
        "preheldout_deviations": [
            "RC7E-D02-model-alias-correction",
            "RC7E-D06-pruned-after-safe-runtime-qualification",
        ],
        "selected_for_scientific_run": False,
        "qualification_failure_run": 33444767215,
        "qualification_failure_artifact": 9777713249,
        "qualification_failure_artifact_digest": "sha256:c403a5e47af93fcaf00a6150fa61bd0bc77facc11705c95fc3a19a814a6479cc",
        "failure_class": "PyTorch>=2.6 safe-deserialization incompatibility with legacy SuPar checkpoint",
        "maintenance_evidence": "upstream last observed code commit 2023-09-03; upstream issues #147/#149 reproduce modern PyTorch loading failure",
    }

    def run(self, raw):
        return make_receipt(
            raw,
            instrument_id="supar_sdp_unavailable",
            instrument_identity=self.identity,
            measurement_principle="semantic dependency graph (qualified unavailable)",
            status="UNRESOLVED",
            proposed_dimensions=[],
            anchors=[],
            candidate_atoms=[],
            native_scores=[],
            jurisdiction=[],
            limitations=[
                "preregistered semantic-dependency lane excluded before held-out construction",
                "legacy checkpoint requires weakening modern safe deserialization or an older/unofficial runtime",
                "no scientific semantic-graph measurement is claimed in RC7E",
            ],
            residue=["semantic_dependency_graph_unavailable"],
            runtime={
                "load_status": "PRUNED_PRE_HELD_OUT",
                "qualification_run": 33444767215,
                "reason": "legacy checkpoint fails modern PyTorch safe deserialization; not rescued solely for coverage",
            },
            native_output=[],
        )


class ProvenancedDebertaNLI(DebertaNLI):
    """Bounded NLI with explicit lineage back to proposal-origin instruments."""

    identity = {
        **DebertaNLI.identity,
        "proposal_origin_provenance": "canonical typed-atom support set",
        "preheldout_deviation": "RC7E-D05-preserve-nli-proposal-origin",
    }

    def measure(self, raw, typed):
        receipt = super().measure(raw, typed)
        support = defaultdict(set)
        for row in typed:
            atom = row.get("atom")
            dim = row.get("dimension")
            origin = row.get("proposal_instrument_id")
            if isinstance(atom, dict) and dim and origin:
                support[atom_key(dim, atom)].add(origin)

        for item in receipt.get("native_output", []):
            atom = item.get("proposal_atom")
            dim = item.get("proposal_dimension")
            if isinstance(atom, dict) and dim:
                item["proposal_instrument_ids"] = sorted(support.get(atom_key(dim, atom), set()))

        for row in receipt.get("native_scores", []):
            item = row.get("measurement")
            if isinstance(item, dict):
                atom = item.get("proposal_atom")
                dim = item.get("proposal_dimension")
                if isinstance(atom, dict) and dim:
                    item["proposal_instrument_ids"] = sorted(support.get(atom_key(dim, atom), set()))

        receipt["instrument_identity"] = self.identity
        receipt["limitations"] = [
            *receipt.get("limitations", []),
            "proposal-origin provenance is preserved; NLI remains relation measurement only",
        ]
        return receipt


def instrument_identities_v2():
    identities = instrument_identities()
    identities["supar_sdp"] = QualifiedSuParSDP.identity
    identities["supar_sdp_unavailable"] = QualifiedSuParSDP.identity
    identities["deberta_nli"] = ProvenancedDebertaNLI.identity
    return identities
