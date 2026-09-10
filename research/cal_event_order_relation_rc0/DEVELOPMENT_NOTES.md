# Pre-science development notes

No event-order proposition-relation cohort had been added or executed when this note was written.

Static adversarial review of the first `relation.py` candidate found a composition identity seam: `compose_temporal_relations` required each relation record to carry the same `claim_id` as the supplied proposition, but did not also require the relation record's exact authenticated proposition projection to equal the supplied proposition projection.

Because exact proposition content may change while retaining the same claim ID, a caller could potentially mix relation records derived under different same-ID temporal propositions at composition time even though each individual derivation used an authenticated proposition binding.

The first draft remains preserved in `relation.py`. The decisive candidate is `candidate.py`, which adds exact relation-record proposition-projection equality before delegating to the frozen scoreless composition table. The decisive cohort will be added only after that wrapper is frozen.

This is a pre-science candidate refinement, not a post-reveal repair.
