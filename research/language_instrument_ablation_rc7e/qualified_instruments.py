"""Pre-held-out corrected wrappers for RC7E.

These wrappers preserve the original preregistered adapters while making only
pre-held-out apparatus corrections discovered before any held-out corpus exists.
"""
from __future__ import annotations

from collections import defaultdict

from research.language_instrument_ablation_rc7e.equivalence import atom_key
from research.language_instrument_ablation_rc7e.instruments import (
    DebertaNLI,
    SuParSDP,
    instrument_identities,
)


class QualifiedSuParSDP(SuParSDP):
    """SuPar DM semantic-dependency parser with the documented model alias."""

    identity = {
        **SuParSDP.identity,
        "model": "biaffine-sdp-en",
        "preregistered_model_alias": "sdp-biaffine-en",
        "preheldout_deviation": "RC7E-D02-model-alias-correction",
    }

    def _load(self):
        if self.parser is not None or self.error:
            return
        try:
            import stanza
            from supar import Parser

            self.prep = stanza.Pipeline(
                lang="en",
                processors="tokenize,pos,lemma",
                use_gpu=False,
                verbose=False,
                download_method=None,
            )
            self.parser = Parser.load(self.identity["model"])
        except Exception as exc:
            self.error = f"{type(exc).__name__}:{exc}"


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
    identities["deberta_nli"] = ProvenancedDebertaNLI.identity
    return identities
