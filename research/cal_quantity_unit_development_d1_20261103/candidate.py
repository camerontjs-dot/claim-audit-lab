"""Bounded, informed quantity/unit development instrument; no model or file I/O.

Parsing each original string is independent. Relation selection happens only
after both documents have observations. This is not a natural-language parser,
an admitted CAL process, or a replacement for upstream provenance/admission.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import hashlib
import re
from typing import Any

INSTRUMENT_ID = "cal-quantity-unit-informed-development-d1"
V3_VERSION = "cal-rc3-quantity-basis-evaluator-v3-prep1"
NUM = r"[+-]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?"
UNIT = r"(?:percentage[ -]points?\b|basis[ -]points?\b|percent\b|bps?\b|pp\b|%)"
QUANTITY = re.compile(rf"(?<![\w.])(?P<number>{NUM})\s*(?P<unit>{UNIT})(?!\w)", re.I)
UNIT_CUE = re.compile(rf"(?<!\w){UNIT}(?!\w)", re.I)
QUANT_CUE = re.compile(r"\b(?:was|is|were|are|increased|decreased|rose|fell|grew|declined)\b", re.I)
YEAR = r"(?:19|20)\d{2}"
PREFIX = rf"(?:(?P<prefix>In\s+(?P<year>{YEAR}),\s*))?"
SUBJECT = r"(?P<article>the\s+)?(?P<subject>[^\d,;.!?\n]+?)"
TAIL = rf"(?:\s+in\s+(?P<end_year>{YEAR}))?"
VERB = r"increased|rose|grew|decreased|fell|declined|dropped"
ENDPOINT = re.compile(
    rf"{PREFIX}{SUBJECT}\s+(?P<verb>{VERB})\s+from\s+"
    rf"(?P<n1>{NUM})\s*(?P<u1>{UNIT})\s+to\s+"
    rf"(?P<n2>{NUM})\s*(?P<u2>{UNIT}){TAIL}", re.I,
)
CHANGE = re.compile(
    rf"{PREFIX}{SUBJECT}\s+(?P<verb>{VERB})\s+(?:by\s+)?"
    rf"(?P<n1>{NUM})\s*(?P<u1>{UNIT}){TAIL}", re.I,
)
LEVEL = re.compile(
    rf"{PREFIX}{SUBJECT}\s+(?:was|were|is|are)\s+"
    rf"(?P<neg>not\s+)?(?P<compare>less\s+than|more\s+than|greater\s+than|"
    rf"at\s+least|at\s+most|equal\s+to)?\s*"
    rf"(?P<n1>{NUM})\s*(?P<u1>{UNIT}){TAIL}", re.I,
)
SPLIT = re.compile(r"\s+while\s+|\s*;\s*|(?<!\d)\.\s+|(?<=\d)\.(?!\d)\s+", re.I)
INCREASE = {"increased", "rose", "grew"}
ABSOLUTE = {"percentage_point_change", "basis_point_change"}


def unit_identity(token: str) -> str:
    token = re.sub(r"[\s-]+", " ", token.casefold())
    if token in {"percent", "%"}:
        return "percent"
    if token in {"percentage point", "percentage points"}:
        return "percentage_point"
    if token in {"basis point", "basis points", "bp", "bps"}:
        return "basis_point"
    return "unknown"


def number(token: str) -> Fraction:
    return Fraction(token.replace(",", ""))


@dataclass(frozen=True)
class Interval:
    lo: Fraction | None
    hi: Fraction | None
    lo_closed: bool = False
    hi_closed: bool = False

    def intersection(self, other: Interval) -> Interval | None:
        if self.lo is None or (other.lo is not None and other.lo > self.lo):
            lo, lc = other.lo, other.lo_closed
        elif other.lo is None or self.lo > other.lo:
            lo, lc = self.lo, self.lo_closed
        else:
            lo, lc = self.lo, self.lo_closed and other.lo_closed
        if self.hi is None or (other.hi is not None and other.hi < self.hi):
            hi, hc = other.hi, other.hi_closed
        elif other.hi is None or self.hi < other.hi:
            hi, hc = self.hi, self.hi_closed
        else:
            hi, hc = self.hi, self.hi_closed and other.hi_closed
        if lo is not None and hi is not None and (lo > hi or (lo == hi and not (lc and hc))):
            return None
        return Interval(lo, hi, lc if lo is not None else False, hc if hi is not None else False)


def intervals(comparator: str, value: Fraction) -> tuple[Interval, ...]:
    if comparator in {"level_eq", "increase", "decrease", "increase_from_to", "decrease_from_to"}:
        return (Interval(value, value, True, True),)
    if comparator == "less_than":
        return (Interval(None, value),)
    if comparator == "more_than":
        return (Interval(value, None),)
    if comparator == "not_less_than":
        return (Interval(value, None, True),)
    if comparator == "not_more_than":
        return (Interval(None, value, False, True),)
    if comparator == "not_equal":
        return (Interval(None, value), Interval(value, None))
    raise ValueError("unregistered comparator")


def intersect(left: tuple[Interval, ...], right: tuple[Interval, ...]) -> tuple[Interval, ...]:
    return tuple(x for a in left for b in right if (x := a.intersection(b)) is not None)


def entails(evidence: tuple[Interval, ...], claim: tuple[Interval, ...]) -> bool:
    return all(any(piece.intersection(target) == piece for target in claim) for piece in evidence)


@dataclass(frozen=True)
class Observation:
    measure: str
    years: tuple[str, ...]
    unit: str
    role: str
    comparator: str
    value: Fraction
    span: tuple[int, int]
    derivation: str | None = None
    ambiguity: str | None = None

    def canonical(self) -> tuple[Interval, ...]:
        value = self.value / 100 if self.role == "basis_point_change" else self.value
        return intervals(self.comparator, value)

    def public(self) -> dict[str, Any]:
        return {
            "measure": self.measure, "time_scope": list(self.years),
            "lexical_unit": self.unit, "quantity_role": self.role,
            "comparator": self.comparator, "exact_value": str(self.value),
            "basis_span": list(self.span), "derivation": self.derivation,
            "ambiguity_reason": self.ambiguity,
        }


@dataclass(frozen=True)
class Document:
    text: str
    observations: tuple[Observation, ...]
    units: tuple[dict[str, Any], ...]
    numbers: tuple[dict[str, Any], ...]
    unparsed: tuple[tuple[int, int], ...]
    quantitative: bool


def _role(unit: str, change: bool, measure: str) -> str:
    if unit == "percentage_point":
        return "percentage_point_change"
    if unit == "basis_point":
        return "basis_point_change"
    if unit == "percent":
        return "percent_relative_change" if change or measure == "change" or measure.endswith(" change") else "percent_level"
    return "unknown"


def _parse_clause(text: str, offset: int) -> list[Observation]:
    for kind, pattern in (("endpoints", ENDPOINT), ("change", CHANGE), ("level", LEVEL)):
        m = pattern.fullmatch(text)
        if m is None:
            continue
        subject = re.sub(r"\s+", " ", m.group("subject").casefold()).strip()
        # A bounded nominal phrase, not an arbitrary prefix before a quantity.
        if not subject or any(not (c.isalpha() or c in " -'’") for c in subject):
            return []
        if re.search(r"\b(?:if|unless|not|no|may|might|could|would|should|either|or|and)\b", subject):
            return []
        years = tuple(x for x in (m.group("year"), m.group("end_year")) if x)
        if len(years) > 1:
            return []
        start = 0 if m.group("prefix") else m.start("subject")
        span = (offset + start, offset + len(text))
        measure = subject if kind == "level" or subject.endswith(" change") or subject == "change" else subject + " change"
        value = number(m.group("n1"))
        unit = unit_identity(m.group("u1"))
        role = _role(unit, kind != "level", measure)
        ambiguity = "unregistered_pp" if unit == "unknown" else None
        if kind == "level":
            cmp_text = re.sub(r"\s+", " ", (m.group("compare") or "").casefold())
            cmp = {"": "level_eq", "equal to": "level_eq", "less than": "less_than", "more than": "more_than", "greater than": "more_than", "at least": "not_less_than", "at most": "not_more_than"}[cmp_text]
            if m.group("neg"):
                cmp = {"level_eq": "not_equal", "less_than": "not_less_than", "more_than": "not_more_than", "not_less_than": "less_than", "not_more_than": "more_than"}[cmp]
            return [Observation(measure, years, unit, role, cmp, value, span, ambiguity=ambiguity)]
        up = m.group("verb").casefold() in INCREASE
        cmp = "increase" if up else "decrease"
        if kind == "change":
            if value <= 0:
                return []
            return [Observation(measure, years, unit, role, cmp, value if up else -value, span, ambiguity=ambiguity)]
        unit2 = unit_identity(m.group("u2"))
        end = number(m.group("n2"))
        if unit != "percent" or unit2 != "percent":
            return []
        delta = end - value
        if (up and delta <= 0) or (not up and delta >= 0):
            return []
        cmp += "_from_to"
        result = [Observation(measure, years, "percent", "percentage_point_change", cmp, delta, span, "endpoints_to_pp")]
        # Relative change at zero/negative baseline is deliberately unsupported.
        if value > 0:
            result.append(Observation(measure, years, "percent", "percent_relative_change", cmp, delta / value * 100, span, "endpoints_to_relative_percent"))
        return result
    return []


def parse_document(text: str) -> Document:
    """Pure source-only parse; never receives a claim, labels, or peer output."""
    if not isinstance(text, str):
        raise TypeError("original input must be text")
    units, nums = [], []
    for m in QUANTITY.finditer(text):
        units.append({"span": list(m.span("unit")), "normalized_identity": unit_identity(m.group("unit"))})
        nums.append({"span": list(m.span("number")), "value": m.group("number")})
    quantitative = bool(UNIT_CUE.search(text) or (re.search(r"\d", text) and QUANT_CUE.search(text)))
    observations, unparsed = [], []
    cursor = 0
    for sep in [*SPLIT.finditer(text), None]:
        end = sep.start() if sep else len(text)
        raw = text[cursor:end]
        lo = cursor + len(raw) - len(raw.lstrip())
        part = raw.strip().rstrip(".").rstrip()
        if part:
            rows = _parse_clause(part, lo)
            observations.extend(rows)
            if not rows:
                unparsed.append((lo, lo + len(part)))
        cursor = sep.end() if sep else end
    return Document(text, tuple(observations), tuple(units), tuple(nums), tuple(unparsed), quantitative)


def _family(role: str) -> str:
    return "absolute_percentage_change" if role in ABSOLUTE else role


def _conversions(claim: Observation, evidence: Observation, cdoc: Document, edoc: Document) -> list[str]:
    if evidence.derivation:
        return [evidence.derivation]
    if {claim.role, evidence.role} == ABSOLUTE:
        return ["100bp=1pp"]
    if claim.unit == evidence.unit == "basis_point":
        tokens = [d.text[t["span"][0]:t["span"][1]].casefold() for d in (cdoc, edoc) for t in d.units]
        if any(t in {"bp", "bps"} for t in tokens):
            return ["bp_lexical_variant"]
    return []


def _compatibility(claim: Observation, evidence: Observation) -> str | None:
    if claim.ambiguity or evidence.ambiguity:
        return "unknown_abbreviation"
    if claim.measure != evidence.measure:
        return "measure_mismatch"
    if claim.years != evidence.years:
        return "year_scope_mismatch"
    if _family(claim.role) != _family(evidence.role):
        is_explicit_change = claim.comparator.startswith(("increase", "decrease")) or evidence.comparator.startswith(("increase", "decrease"))
        return "unit_role_mismatch" if is_explicit_change or claim.unit == evidence.unit else "unit_mismatch"
    return None


def _side(doc: Document, row: Observation | None, not_applicable: bool) -> dict[str, Any]:
    return {
        "unit_tokens": [] if not_applicable else list(doc.units),
        "numeric_tokens": [] if not_applicable else list(doc.numbers),
        "quantity_role": "not_applicable" if not_applicable else (row.role if row else "unknown"),
        "measure": row.measure if row and not not_applicable else None,
        "comparator": "not_applicable" if not_applicable else (row.comparator if row else "unknown"),
        "time_scope": list(row.years) if row and not not_applicable else [],
        "consumed_spans": [] if not_applicable or not doc.text else [[0, len(doc.text)]],
        "ambiguity_reason": row.ambiguity if row else None,
    }


def analyze(claim: str, evidence: str) -> dict[str, Any]:
    """Assess one original pair. Unsupported or conflicting inputs abstain."""
    cdoc, edoc = parse_document(claim), parse_document(evidence)
    c = cdoc.observations[0] if cdoc.observations else None
    e = edoc.observations[0] if edoc.observations else None
    selected: list[Observation] = []
    available: list[str] = []
    reason: str | None = None
    relation = "unresolved"
    if not cdoc.quantitative and not cdoc.observations:
        relation = "not_applicable"
    elif cdoc.unparsed or len(cdoc.observations) != 1:
        reason = "unsupported_or_compound_claim"
    elif edoc.unparsed or not edoc.observations:
        reason = "unsupported_or_missing_evidence"
    else:
        assert c is not None
        same_measure = [r for r in edoc.observations if r.measure == c.measure]
        same_scope = [r for r in same_measure if r.years == c.years]
        comparable = [r for r in same_scope if _family(r.role) == _family(c.role)]
        # Select by declared measure/scope/role, never by desired label/value.
        candidates = comparable or same_scope or same_measure or list(edoc.observations)
        e = candidates[0]
        available = _conversions(c, e, cdoc, edoc)
        reason = _compatibility(c, e)
        if any(r.ambiguity for r in same_scope):
            reason = "unknown_abbreviation"
        if reason is None:
            selected = comparable
            common = selected[0].canonical()
            for row in selected[1:]:
                common = intersect(common, row.canonical())
            if not common:
                reason = "material_conflict"
            elif entails(common, c.canonical()):
                relation = "supports"
            elif not intersect(common, c.canonical()):
                relation = "refutes"
            else:
                reason = "overlapping_bounds"
    na = relation == "not_applicable"
    if na:
        c = e = None
    cs, es = _side(cdoc, c, na), _side(edoc, e, na)
    conversion = available[0] if len(available) == 1 else None
    conversion_applied = conversion if relation in {"supports", "refutes"} and conversion != "bp_lexical_variant" else None
    conversion_rejected = reason if available and reason in {"measure_mismatch", "year_scope_mismatch", "unit_role_mismatch", "unit_mismatch", "unknown_abbreviation"} else None
    evidence_basis = selected or ([e] if e else [])
    basis = {
        "claim": [list(c.span)] if c else [],
        "evidence": [list(s) for s in dict.fromkeys(r.span for r in evidence_basis)],
    }
    return {
        "instrument_id": INSTRUMENT_ID,
        "status": "not_applicable" if na else ("claimed" if relation in {"supports", "refutes"} else "unresolved"),
        "relation": relation,
        "claim_unit": cs["quantity_role"], "evidence_unit": es["quantity_role"],
        "claim_measure": cs["measure"], "evidence_measure": es["measure"],
        "claim_years": cs["time_scope"], "evidence_years": es["time_scope"],
        "conversion": conversion, "ambiguity": relation == "unresolved",
        "abstention_cause": reason,
        "claim_unit_spans": [t["span"] for t in cs["unit_tokens"]],
        "evidence_unit_spans": [t["span"] for t in es["unit_tokens"]],
        "receipt_v2": {
            "input_scope": {"claim": [0, len(claim)], "evidence": [0, len(evidence)]},
            "quantities": {"claim": cs, "evidence": es},
            "unresolved_reason": reason,
            "conversion_rule": {"available": available, "applied": conversion_applied, "rejected_reason": conversion_rejected},
        },
        "receipt_v3": {
            "version": V3_VERSION,
            "basis_kind": "DECLARED_DECISIVE_TEXT_NOT_OBSERVED_CAUSAL_CONSUMPTION",
            "deciding_basis_spans": basis,
            "consumption_independence": "NOT_ESTABLISHED",
        },
        "input_identity": {s: hashlib.sha256(t.encode("utf-8")).hexdigest() for s, t in (("claim", claim), ("evidence", evidence))},
        "source_observations": {
            "claim": [r.public() for r in cdoc.observations],
            "evidence": [r.public() for r in edoc.observations],
        },
        "unparsed_spans": {"claim": [list(s) for s in cdoc.unparsed], "evidence": [list(s) for s in edoc.unparsed]},
        "scope": "EXPOSED_DEVELOPMENT_ONLY_NOT_A_QUALIFIED_CAL_PROCESS",
    }


__all__ = ["analyze", "parse_document", "INSTRUMENT_ID"]
