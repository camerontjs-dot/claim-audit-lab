"""NLI entailer implementation for CAL v1.

Real ``MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli`` inference, pinned to the HF
revision SHA in ``AuditConfig.entailer.hf_revision_sha``. CPU only, deterministic
(see :mod:`claim_audit_lab.v1.impl._determinism`). Each ``(claim, premise)`` pair
is scored as an NLI hypothesis/premise pair per the MNLI/FEVER convention —
``tokenizer(premise, claim)`` — and the three-class logits are mapped to the v1
``EntailLabel`` via the model's own ``config.id2label`` (entailment → ``entail``,
neutral → ``neutral``, contradiction → ``contradict``).

The **unrounded** three logits are recorded in ``EntailResult.raw_logits`` in the
model's native class order so downstream consumers can re-derive labels under
different thresholds without re-running the model (DECISIONS.md § 2026-06-21 § 9).
``score`` is the softmax probability of the predicted (argmax) class.

The model + tokenizer are loaded once per process (module-level cache keyed by
model id + revision). See ``plans/phases/phase-2-inference-layers.md``.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from typing import Any

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from claim_audit_lab.v1.impl._determinism import enforce_cpu_determinism
from claim_audit_lab.v1.models import EntailLabel, EntailResult, ModelRevision

enforce_cpu_determinism()

# DeBERTa-v3-mnli-fever-anli native class order → v1 EntailLabel.
_HF_LABEL_TO_ENTAIL: dict[str, EntailLabel] = {
    "entailment": "entail",
    "neutral": "neutral",
    "contradiction": "contradict",
}


@cache
def _load_model(model_id: str, revision_sha: str) -> tuple[Any, Any, tuple[EntailLabel, ...]]:
    """Load (and cache) the pinned NLI model + tokenizer and its label order.

    The model/tokenizer carry ``Any`` types — ``transformers``' ``Auto*``
    factories are not statically typed at our call sites. The label order is
    derived from the model's own ``config.id2label`` so a revision bump that
    reordered the classes would be reflected, not silently mismatched.
    """
    tokenizer = AutoTokenizer.from_pretrained(model_id, revision=revision_sha)
    model = AutoModelForSequenceClassification.from_pretrained(model_id, revision=revision_sha)
    model.eval()
    id2label: dict[int, str] = model.config.id2label
    label_order = tuple(
        _HF_LABEL_TO_ENTAIL[id2label[index].lower()] for index in range(len(id2label))
    )
    return model, tokenizer, label_order


@dataclass(frozen=True)
class DeBERTaEntailer:
    """DeBERTa-v3 NLI cross-encoder pinned to a specific HF model revision."""

    revision: ModelRevision

    def entail(self, claim: str, premise: str, passage_id: str) -> EntailResult:
        """Return the NLI label + score + raw logits for ``(claim, premise)``.

        Tokenizes ``(premise, claim)`` per the MNLI/FEVER convention, runs a
        single forward pass in ``eval()`` + ``no_grad()``, and maps the argmax
        class to the v1 ``EntailLabel`` via the model's ``id2label``. The raw
        three logits are captured unrounded in the model's native class order.
        """
        if not self.revision.hf_revision_sha.strip():
            raise ValueError(
                "DeBERTaEntailer requires a pinned hf_revision_sha; refusing to load "
                "an unpinned model revision (trace reproducibility depends on it)."
            )
        model, tokenizer, label_order = _load_model(
            self.revision.model_id, self.revision.hf_revision_sha
        )
        encoded = tokenizer(premise, claim, return_tensors="pt", truncation=True)
        with torch.no_grad():
            logits = model(**encoded).logits[0]
        probabilities = torch.softmax(logits, dim=-1)
        predicted = int(torch.argmax(logits))
        raw = tuple(float(value) for value in logits)
        return EntailResult(
            passage_id=passage_id,
            label=label_order[predicted],
            score=float(probabilities[predicted]),
            raw_logits=(raw[0], raw[1], raw[2]),
        )


__all__ = ["DeBERTaEntailer"]
