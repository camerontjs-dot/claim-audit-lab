"""Max-entailment aggregator for CAL v1.

Pure data manipulation — no external dependencies. The v1 aggregator reports the
**strongest support-bearing** passage as the claim-level support signal: it takes
the highest-scoring ``entail``/``contradict`` result, and only falls back to a
neutral signal when *every* candidate is neutral. Concatenated-premise and M×N
aggregators are documented in ``AggregationStrategy`` but deferred to v2.

**Why neutral abstains rather than competes.** Each ``EntailResult.score`` is the
softmax probability of the passage's argmax label, so a confidently-*neutral*
passage carries a high score that means "confident this passage is irrelevant",
*not* "confident the claim is unsupported". Ranking by raw score across all labels
therefore let a confidently-neutral passage mask a confidently-entail/contradict
one (real-inference finding, DECISIONS.md § 2026-06-29). Excluding neutral from
the selection fixes that: the signal is the strongest *position* a passage takes
on the claim. The rule is one sentence — "the strongest support-or-contradiction
signal wins; neutral passages don't count."

The aggregator still does not decide a verdict; the rules layer does (the A4
contradiction gate + the B5 degree thresholds live there). One residual the rules
layer cannot recover from a single signal: when one passage strongly *entails* and
another strongly *contradicts* the same claim, the higher-scoring of the two wins
and the other is not surfaced — genuinely conflicting evidence, left as a
documented, Phase-4-gated limitation (the two-signal upgrade is the fix if
calibration shows it matters). See DECISIONS.md § 2026-06-21 § 1 and § 5, and
§ 2026-06-29 (the neutral-masking fix).
"""

from __future__ import annotations

from dataclasses import dataclass

from claim_audit_lab.v1.models import EntailResult, SupportSignal


@dataclass(frozen=True)
class MaxEntailmentAggregator:
    """Take the highest-scoring support-bearing (non-neutral) result; neutral abstains."""

    def aggregate(self, entailment_results: list[EntailResult]) -> SupportSignal:
        """Return the support signal of the strongest support-bearing passage.

        Selects the highest-scoring ``entail``/``contradict`` result; if every
        candidate is neutral (or there are none), falls back to the highest-scoring
        neutral result — yielding a ``neutral`` signal that the rules layer reads as
        ``no_entail_signal``. Deterministic: ``max`` keeps the first of equal scores,
        so input order breaks ties.
        """
        if not entailment_results:
            return SupportSignal(
                label="neutral",
                max_entailment_score=0.0,
                contributing_passage_id=None,
            )
        support_bearing = [r for r in entailment_results if r.label != "neutral"]
        candidates = support_bearing or entailment_results
        top = max(candidates, key=lambda r: r.score)
        return SupportSignal(
            label=top.label,
            max_entailment_score=top.score,
            contributing_passage_id=top.passage_id,
        )


__all__ = ["MaxEntailmentAggregator"]
