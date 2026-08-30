"""Frozen RC3 research-only decomposition and scoped-rule interpretation candidates.

No production imports. No case IDs, gold labels, family labels, or evaluator metadata
are accepted by this module. Unsupported or ambiguous structures remain unresolved.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Literal

Relation = Literal["entailment", "neutral", "contradiction", "unresolved"]


def _norm(text: str) -> str:
    text = text.lower().replace("‑", "-").replace("–", "-").replace("—", "-")
    text = re.sub(r"\s+", " ", text)
    return text.strip(" .")


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]


@dataclass(frozen=True)
class ScopedState:
    exclusions: tuple[str, ...] = ()
    explicit_opposites: tuple[str, ...] = ()
    alternate_processes: tuple[str, ...] = ()
    narrow_exemptions: tuple[tuple[str, str], ...] = ()
    temporal_scopes: tuple[str, ...] = ()
    restored_rules: tuple[str, ...] = ()
    only_permissions: tuple[tuple[str, str], ...] = ()
    recognized_reasons: tuple[str, ...] = ()

    @property
    def recognized(self) -> bool:
        return bool(self.recognized_reasons)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


_EXCEPTION_REL = re.compile(
    r"\bexcept(?: for)? (?P<exc>[^,.]+), (?P<rel>who|which) (?P<rest>[^.]+)",
    flags=re.IGNORECASE,
)
_EXCEPTION_BARE = re.compile(
    r"\bexcept(?: for)? (?P<exc>[^,.]+)(?:[,.]|$)", flags=re.IGNORECASE
)
_OTHER_THAN = re.compile(
    r"\bother than (?P<exc>[A-Z][A-Za-z]*(?: [A-Za-z]+){0,2})", flags=re.IGNORECASE
)
_EXEMPT = re.compile(
    r"(?P<subject>[A-Za-z][A-Za-z -]{1,60}?) (?:are|is) exempt(?: only)? from "
    r"(?P<object>[^.]+)",
    flags=re.IGNORECASE,
)
_ONLY = re.compile(
    r"\bonly (?P<class>[A-Za-z][A-Za-z -]+?) may (?P<action>[^.]+)",
    flags=re.IGNORECASE,
)


def interpret_scoped_rule(premise: str) -> ScopedState:
    exclusions: list[str] = []
    opposites: list[str] = []
    alternate: list[str] = []
    exemptions: list[tuple[str, str]] = []
    temporal: list[str] = []
    restored: list[str] = []
    only_permissions: list[tuple[str, str]] = []
    reasons: list[str] = []

    for m in _EXCEPTION_REL.finditer(premise):
        exc = m.group("exc").strip()
        rest = m.group("rest").strip()
        exclusions.append(exc)
        reasons.append("exception_relative")
        low = _norm(rest)
        if any(x in low for x in ("must not ", "required not to ", "prohibited from ")):
            opposites.append(f"{exc} {rest}")
        elif any(x in low for x in (" use ", "uses ", " follow ", "follows ", "assigned to ")):
            alternate.append(f"{exc} {rest}")

    for m in _EXCEPTION_BARE.finditer(premise):
        exc = m.group("exc").strip()
        if exc and exc not in exclusions:
            exclusions.append(exc)
            reasons.append("exception_bare")

    for m in _OTHER_THAN.finditer(premise):
        exc = m.group("exc").strip()
        if exc not in exclusions:
            exclusions.append(exc)
            reasons.append("other_than")

    for sentence in _sentences(premise):
        low = _norm(sentence)
        if "outside the scope of" in low or "excluded from" in low or "carved out of" in low:
            reasons.append("explicit_scope")
            head = re.split(r"\b(?:is|are)\b", sentence, maxsplit=1, flags=re.IGNORECASE)[0].strip()
            if head and len(head.split()) <= 5 and head not in exclusions:
                exclusions.append(head)

        if any(x in low for x in ("must not ", "required not to ", "prohibited from ")):
            opposites.append(sentence.strip(" ."))
            reasons.append("explicit_opposite")

        if (
            ("carved out" in low or "other than" in low or "except " in low)
            and any(x in low for x in ("required to follow", "assigned to", "which use", "which follows"))
        ):
            alternate.append(sentence.strip(" ."))
            reasons.append("alternate_process")
        elif any(x in low for x in ("assigned to queue ", "required to follow chain ")):
            alternate.append(sentence.strip(" ."))
            reasons.append("alternate_process")

        for m in _EXEMPT.finditer(sentence):
            exemptions.append((m.group("subject").strip(), m.group("object").strip()))
            reasons.append("narrow_exemption")

        if any(
            token in low
            for token in (
                "first 30 days",
                "approved leave",
                "active emergency",
                "while the review system is offline",
                "while the alarm is active",
                "during an evacuation",
                "during their first",
            )
        ):
            temporal.append(sentence.strip(" ."))
            reasons.append("temporal_scope")

        if any(
            token in low
            for token in (
                "after the first 30 days",
                "once approved leave ends",
                "when the emergency ends",
                "when the system is online",
                "outside an evacuation",
                "when the alarm is cleared",
                "applies again",
                "schedule resumes",
                "again need",
            )
        ):
            restored.append(sentence.strip(" ."))
            reasons.append("restored_rule")

        m_only = _ONLY.search(sentence)
        if m_only:
            only_permissions.append(
                (m_only.group("class").strip(), m_only.group("action").strip())
            )
            reasons.append("only_permission")

    def uniq(values: list[str]) -> tuple[str, ...]:
        return tuple(dict.fromkeys(v.strip() for v in values if v.strip()))

    return ScopedState(
        exclusions=uniq(exclusions),
        explicit_opposites=uniq(opposites),
        alternate_processes=uniq(alternate),
        narrow_exemptions=tuple(dict.fromkeys((a.strip(), b.strip()) for a, b in exemptions)),
        temporal_scopes=uniq(temporal),
        restored_rules=uniq(restored),
        only_permissions=tuple(dict.fromkeys((a.strip(), b.strip()) for a, b in only_permissions)),
        recognized_reasons=uniq(reasons),
    )


def decompose_for_nli(premise: str) -> str:
    """Expose stated scope in controlled English without inventing opposite behavior."""
    state = interpret_scoped_rule(premise)
    additions: list[str] = []

    for exc in state.exclusions:
        additions.append(
            f"Scoped rule statement: {exc} is outside the scope of the immediately governing rule."
        )
    for item in state.explicit_opposites:
        additions.append(f"Explicit exception requirement: {item}.")
    for item in state.alternate_processes:
        additions.append(f"Explicit alternate process: {item}.")
    for subject, obj in state.narrow_exemptions:
        additions.append(f"Narrow exemption statement: {subject} is exempt from {obj}.")
    for item in state.temporal_scopes:
        additions.append(f"Temporal scope statement: {item}.")
    for item in state.restored_rules:
        additions.append(f"Restored-rule statement: {item}.")

    if not additions:
        return premise
    return premise.rstrip() + " " + " ".join(dict.fromkeys(additions))


def _token_overlap(a: str, b: str) -> float:
    stop = {
        "the", "a", "an", "is", "are", "to", "from", "of", "under", "this", "that",
        "rule", "requirement", "policy", "applies", "apply", "governed", "by", "must",
        "may", "not", "every", "all", "during", "while", "on", "in", "and", "or",
    }
    ta = {x for x in re.findall(r"[a-z0-9]+", _norm(a)) if x not in stop}
    tb = {x for x in re.findall(r"[a-z0-9]+", _norm(b)) if x not in stop}
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / min(len(ta), len(tb))


def _subject_hint(hypothesis: str) -> str:
    m = re.match(
        r"^(.+?)\s+(?:must|may|is|are|uses|use|follows|follow|remains|remain|follows|follow)\b",
        hypothesis.strip(),
        flags=re.IGNORECASE,
    )
    if not m:
        return ""
    words = m.group(1).strip().split()
    return " ".join(words[-4:])


def _matches_excluded_subject(state: ScopedState, hypothesis: str) -> bool:
    h = _norm(hypothesis)
    hint = _norm(_subject_hint(hypothesis))
    for exc in state.exclusions:
        e = _norm(exc)
        e_head = re.split(r"\b(?:during|while|when|on day|in their first)\b", e, maxsplit=1)[0].strip()
        if e in h or (e_head and e_head in h) or (hint and _token_overlap(e_head, hint) >= 0.6):
            return True
    return False


def typed_relation(premise: str, hypothesis: str) -> tuple[Relation, str, dict[str, object]]:
    """Conservatively project the frozen typed state against a hypothesis.

    The function intentionally prefers unresolved over guessing.
    """
    state = interpret_scoped_rule(premise)
    p = _norm(premise)
    h = _norm(hypothesis)

    if h and h in p:
        return "entailment", "hypothesis appears explicitly in premise", state.to_dict()

    for opp in state.explicit_opposites:
        o = _norm(opp)
        if _token_overlap(o, h) >= 0.55:
            if any(x in h for x in ("must not ", "required not to ", "prohibited from ", "may not ")):
                return "entailment", "matches explicit opposite requirement", state.to_dict()
            if any(x in h for x in (" must ", "required to ", " may ")):
                return "contradiction", "positive obligation conflicts with explicit opposite", state.to_dict()

    for allowed_class, action in state.only_permissions:
        if _token_overlap(action, h) >= 0.6:
            if _norm(allowed_class) in h:
                return "entailment", "matches only-permitted class", state.to_dict()
            hint = _norm(_subject_hint(hypothesis))
            if hint and re.search(
                rf"\b{re.escape(hint)}\b.*\bnot (?:a |an )?{re.escape(_norm(allowed_class).rstrip('s'))}\b",
                p,
            ):
                if "may not " in h:
                    return "entailment", "non-member excluded by only-permission", state.to_dict()
                if " may " in f" {h} ":
                    return "contradiction", "non-member conflicts with only-permission", state.to_dict()

    excluded = _matches_excluded_subject(state, hypothesis)
    if excluded:
        if any(x in h for x in ("excluded from", "outside the scope", "temporarily outside")):
            return "entailment", "matches explicit scoped exclusion", state.to_dict()
        if any(x in h for x in ("governed by", "rule governs", "rule applies to", "policy applies to", "included among")):
            return "contradiction", "hypothesis places excluded subject inside rule scope", state.to_dict()
        if any(x in h for x in ("must not ", "never ", "do not ", "does not ", "prohibited from ")):
            return "neutral", "bare exclusion does not license opposite behavior", state.to_dict()
        if " must " in f" {h} " or "required to " in h:
            return "neutral", "bare exclusion does not license positive obligation", state.to_dict()

    if state.alternate_processes:
        no_process_markers = (
            "no workflow", "no procedure", "no chain", "no processing queue",
            "no process", "follows no", "use no", "uses no",
        )
        if any(x in h for x in no_process_markers):
            return "contradiction", "explicit alternate process defeats no-process hypothesis", state.to_dict()
        if any(_token_overlap(item, hypothesis) >= 0.65 for item in state.alternate_processes):
            return "entailment", "matches explicit alternate process", state.to_dict()

    for subject, obj in state.narrow_exemptions:
        if _token_overlap(subject, hypothesis) < 0.6:
            continue
        if _token_overlap(obj, hypothesis) >= 0.75:
            return "entailment", "matches explicit narrow exemption", state.to_dict()
        if "exempt from" in h:
            tail = h.split("exempt from", 1)[1]
            if any(
                _token_overlap(tail, sent) >= 0.55
                for sent in _sentences(premise)
                if any(x in _norm(sent) for x in ("remain required", "remains required", "mandatory", "still apply"))
            ):
                return "contradiction", "alleged exemption conflicts with explicitly retained requirement", state.to_dict()
            if "all " in h and any(x in p for x in ("all other ", "remain required", "remains mandatory")):
                return "contradiction", "broad exemption conflicts with retained controls", state.to_dict()
            return "neutral", "narrow exemption does not license broader exemption", state.to_dict()

    m_bound = re.search(r"first (\d+) days", p)
    m_day = re.search(r"day (\d+)", h)
    if m_bound and m_day:
        bound = int(m_bound.group(1))
        day = int(m_day.group(1))
        if day <= bound:
            if any(x in h for x in ("excluded from", "outside", "exempt from")):
                return "entailment", "hypothesis falls inside explicit temporary exception", state.to_dict()
            if "must not " in h:
                return "neutral", "temporary exclusion is not a prohibition", state.to_dict()
        elif state.restored_rules:
            if any(x in h for x in ("governed by", "rule applies", "required")):
                return "entailment", "hypothesis falls after explicit restoration", state.to_dict()
            if "exempt from" in h:
                return "contradiction", "post-bound exemption conflicts with explicit restoration", state.to_dict()

    if state.temporal_scopes and state.restored_rules:
        inside = any(
            x in h
            for x in (
                "during an evacuation", "on approved leave", "during approved leave",
                "active emergency", "while the review system is offline", "while the alarm is active",
            )
        )
        outside = any(
            x in h
            for x in (
                "outside an evacuation", "after approved leave ends", "after the emergency ends",
                "while the system is online", "after the alarm is cleared",
            )
        )
        if inside and any(x in h for x in ("excluded from", "outside", "suspended", "exempt from")):
            return "entailment", "matches bounded exception condition", state.to_dict()
        if inside and any(x in h for x in ("must not ", "prohibited from ")):
            return "neutral", "bounded exclusion is not a prohibition", state.to_dict()
        if outside and any(x in h for x in ("governed by", "rule applies", "required")):
            return "entailment", "matches explicit restored rule", state.to_dict()
        if outside and any(x in h for x in ("exempt from", "remains suspended")):
            return "contradiction", "outside-scope exemption conflicts with restoration", state.to_dict()

    if not state.recognized:
        return "unresolved", "no frozen scoped-rule grammar matched", state.to_dict()
    return "unresolved", "recognized structure but hypothesis projection is not licensed", state.to_dict()


__all__ = [
    "Relation",
    "ScopedState",
    "decompose_for_nli",
    "interpret_scoped_rule",
    "typed_relation",
]
