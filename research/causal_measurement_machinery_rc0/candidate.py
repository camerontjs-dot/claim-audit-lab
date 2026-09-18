"""Competing proposal instruments for CAL Causal Measurement Machinery RC0."""

from __future__ import annotations

import re

from .cohort import CausalAtom, Kind, Observation, Status


def _clean(text: str) -> str:
    return " ".join(text.strip().split()).removesuffix(".")


def _hard_hazard(text: str) -> str | None:
    low = text.casefold()
    if re.search(
        r"\b(report|study|article)\b.*\b(says?|said|reported|claims?)\b",
        low,
    ):
        return "reporting scope"
    if " may " in f" {low} " or " might " in f" {low} ":
        return "epistemic modality"
    if " and " in f" {low} " or " or " in f" {low} ":
        return "relation composition"
    if "risk factor" in low:
        return "ambiguous risk-factor language"
    if "predicts" in low:
        return "prediction is not frozen relation authority"
    if "associated with" in low:
        return "generic association"
    if "explains" in low:
        return "explanation is not frozen causal kind"
    if "sufficient for" in low:
        return "logical sufficiency"
    if "manipulated" in low and "changed" in low:
        return "experimental context without explicit relation assertion"
    return None


def _claim(cause: str, effect: str, kind: Kind) -> Observation:
    return Observation.claimed(CausalAtom(cause.casefold(), effect.casefold(), kind))


def direct_kind_grammar(text: str) -> Observation:
    """Bounded direct grammar over all six frozen Gate-0 relation kinds."""

    compact = _clean(text)
    hazard = _hard_hazard(compact)
    if hazard is not None:
        return Observation.unresolved(hazard)

    patterns: tuple[tuple[str, Kind], ...] = (
        (
            r"(?P<cause>A|X) causes (?P<effect>B|Y)",
            Kind.CAUSES,
        ),
        (
            r"(?P<cause>A|X) contributes to (?P<effect>B|Y)",
            Kind.CONTRIBUTES_TO,
        ),
        (
            r"(?P<cause>A|X) prevents (?P<effect>B|Y)",
            Kind.PREVENTS,
        ),
        (
            r"(?P<cause>A|X) correlates with (?P<effect>B|Y)",
            Kind.CORRELATES_WITH,
        ),
        (
            r"(?P<cause>A|X) precedes (?P<effect>B|Y)",
            Kind.PRECEDES,
        ),
        (
            r"(?P<cause>A|X) co-occurs with (?P<effect>B|Y)",
            Kind.CO_OCCURS,
        ),
    )
    for pattern, kind in patterns:
        match = re.fullmatch(pattern, compact, re.IGNORECASE)
        if match is not None:
            return _claim(match.group("cause"), match.group("effect"), kind)

    return Observation.unresolved("outside bounded direct kind grammar")


def _diagnostic_assertion(text: str) -> Observation | None:
    compact = _clean(text)

    caused = re.fullmatch(
        r"(?P<effect>B) is caused by (?P<cause>A)",
        compact,
        re.IGNORECASE,
    )
    if caused is not None:
        return _claim(caused.group("cause"), caused.group("effect"), Kind.CAUSES)

    prevented = re.fullmatch(
        r"(?P<effect>B) is prevented by (?P<cause>A)",
        compact,
        re.IGNORECASE,
    )
    if prevented is not None:
        return _claim(
            prevented.group("cause"),
            prevented.group("effect"),
            Kind.PREVENTS,
        )

    contributing = re.fullmatch(
        r"(?P<cause>A) is a contributing factor to (?P<effect>B)",
        compact,
        re.IGNORECASE,
    )
    if contributing is not None:
        return _claim(
            contributing.group("cause"),
            contributing.group("effect"),
            Kind.CONTRIBUTES_TO,
        )

    correlated = re.fullmatch(
        r"(?P<cause>A) and (?P<effect>B) are correlated",
        compact,
        re.IGNORECASE,
    )
    if correlated is not None:
        return _claim(
            correlated.group("cause"),
            correlated.group("effect"),
            Kind.CORRELATES_WITH,
        )

    before = re.fullmatch(
        r"(?P<cause>A) occurs before (?P<effect>B)",
        compact,
        re.IGNORECASE,
    )
    if before is not None:
        return _claim(
            before.group("cause"),
            before.group("effect"),
            Kind.PRECEDES,
        )

    together = re.fullmatch(
        r"(?P<cause>A) occurs together with (?P<effect>B)",
        compact,
        re.IGNORECASE,
    )
    if together is not None:
        return _claim(
            together.group("cause"),
            together.group("effect"),
            Kind.CO_OCCURS,
        )

    return None


def broad_assertion_classifier(text: str) -> Observation:
    """Broad assertion classifier used to expose causal laundering."""

    compact = _clean(text)

    direct = direct_kind_grammar(compact)
    if direct.status is Status.CLAIMED:
        return direct

    diagnostic = _diagnostic_assertion(compact)
    if diagnostic is not None:
        return diagnostic

    low = compact.casefold()

    if "causes" in low and "a" in low and "b" in low:
        return _claim("a", "b", Kind.CAUSES)
    if "risk factor" in low:
        return _claim("a", "b", Kind.CONTRIBUTES_TO)
    if "predicts" in low or "explains" in low:
        return _claim("a", "b", Kind.CAUSES)
    if "associated with" in low:
        return _claim("a", "b", Kind.CORRELATES_WITH)
    if "manipulated" in low and "changed" in low:
        return _claim("a", "b", Kind.CAUSES)

    return Observation.unresolved("broad classifier found no bounded assertion")


def conservative_assertion_hybrid(text: str) -> Observation:
    """Permit only direct or preregistered explicit-assertion surfaces."""

    direct = direct_kind_grammar(text)
    if direct.status is Status.CLAIMED:
        return direct
    if _hard_hazard(_clean(text)) is not None:
        return direct
    diagnostic = _diagnostic_assertion(text)
    if diagnostic is not None:
        return diagnostic
    return direct


INSTRUMENTS = {
    "direct_kind_grammar": direct_kind_grammar,
    "broad_assertion_classifier": broad_assertion_classifier,
    "conservative_assertion_hybrid": conservative_assertion_hybrid,
}
