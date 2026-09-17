"""Competing proposal instruments for CAL Deontic Measurement Machinery RC0.

These functions produce measurement proposals only. They do not warrant semantic
authority or participate directly in verdict formation.
"""

from __future__ import annotations

import importlib
import re
from typing import Any

from .cohort import (
    APPROVE_RECORD,
    ARCHIVE_RECORD,
    CONTRACTORS,
    QA,
    QA_APPROVES,
    QA_SIGNS,
    RECONCILE_DISCREPANCY,
    RELEASE_BATCH,
    TECH,
    Mode,
    Norm,
    Observation,
    Status,
)

_SUBJECTS = {
    "qualified technicians": TECH,
    "qa": QA,
}

_ACTIONS = {
    "release the batch": RELEASE_BATCH,
    "approve the record": APPROVE_RECORD,
    "archive the record": ARCHIVE_RECORD,
}

_OPEN_ACTIONS = {
    ("release", "batch"): RELEASE_BATCH,
    ("approve", "record"): APPROVE_RECORD,
    ("archive", "record"): ARCHIVE_RECORD,
    ("reconcile", "discrepancy"): RECONCILE_DISCREPANCY,
}

_DEONTIC_CUES = re.compile(
    r"\b(may|must|shall|permitted|prohibited|required|only|permits)\b",
    re.IGNORECASE,
)

_REPORTING = re.compile(
    r"\b(report|witness|article|author|study)\b.*\b(says?|said|states?|reported|claims?)\b",
    re.IGNORECASE,
)


def _clean(text: str) -> str:
    return " ".join(text.strip().split())


def _strip_period(text: str) -> str:
    return text[:-1] if text.endswith(".") else text


def _hard_scope_hazard(text: str) -> str | None:
    low = text.casefold()
    if '"' in text or "'" in text:
        return "quotation/attribution scope"
    if _REPORTING.search(text) is not None:
        return "reporting scope"
    if " may not " in f" {low} ":
        return "may-not ambiguity"
    if " not required " in f" {low} ":
        return "negated obligation"
    if " either " in f" {low} " or " unless " in f" {low} ":
        return "unsupported disjunction/nested exception"
    if " can " in f" {low} ":
        return "ability is not permission"
    if low.startswith("only ") and (" must " in f" {low} " or " shall " in f" {low} "):
        return "only + obligation scope"
    if " may release and archive " in f" {low} ":
        return "multi-action conjunction"
    return None


def _parse_modifiers(text: str) -> tuple[str, tuple[str, ...], str | None, str | None, str | None]:
    body = text
    exceptions: tuple[str, ...] = ()
    condition: str | None = None
    temporal_relation: str | None = None
    temporal_reference: str | None = None

    match = re.search(r"\s+except\s+contractors$", body, re.IGNORECASE)
    if match is not None:
        exceptions = (CONTRACTORS,)
        body = body[: match.start()]

    match = re.search(r"\s+if\s+QA\s+approves$", body, re.IGNORECASE)
    if match is not None:
        condition = QA_APPROVES
        body = body[: match.start()]

    match = re.search(r"\s+(after|before)\s+QA\s+signs$", body, re.IGNORECASE)
    if match is not None:
        temporal_relation = match.group(1).upper()
        temporal_reference = QA_SIGNS
        body = body[: match.start()]

    return body, exceptions, condition, temporal_relation, temporal_reference


def _subject(value: str) -> str | None:
    return _SUBJECTS.get(value.casefold().strip())


def _action(value: str) -> str | None:
    return _ACTIONS.get(value.casefold().strip())


def _observation(
    mode: Mode,
    subject: str,
    action: str,
    *,
    exceptions: tuple[str, ...] = (),
    condition: str | None = None,
    temporal_relation: str | None = None,
    temporal_reference: str | None = None,
) -> Observation:
    return Observation.claimed(
        Norm(
            mode=mode,
            subject=subject,
            action=action,
            exceptions=exceptions,
            condition=condition,
            temporal_relation=temporal_relation,
            temporal_reference=temporal_reference,
        )
    )


def direct_grammar(text: str) -> Observation:
    """Bounded direct grammar with an explicit fail-closed scope envelope."""

    compact = _strip_period(_clean(text))
    hazard = _hard_scope_hazard(compact)
    if hazard is not None:
        return Observation.unresolved(hazard)

    body, exceptions, condition, temporal_relation, temporal_reference = _parse_modifiers(compact)

    restricted = re.fullmatch(
        r"Only\s+(?P<subject>Qualified technicians)\s+may\s+"
        r"(?P<action>release the batch|approve the record|archive the record)",
        body,
        re.IGNORECASE,
    )
    if restricted is not None:
        subject = _subject(restricted.group("subject"))
        action = _action(restricted.group("action"))
        assert subject is not None and action is not None
        return _observation(
            Mode.PERMISSION_RESTRICTED_TO,
            subject,
            action,
            exceptions=exceptions,
            condition=condition,
            temporal_relation=temporal_relation,
            temporal_reference=temporal_reference,
        )

    modal = re.fullmatch(
        r"(?P<subject>Qualified technicians|QA)\s+"
        r"(?P<modal>may|must not|must)\s+"
        r"(?P<action>release the batch|approve the record|archive the record)",
        body,
        re.IGNORECASE,
    )
    if modal is not None:
        subject = _subject(modal.group("subject"))
        action = _action(modal.group("action"))
        assert subject is not None and action is not None
        token = modal.group("modal").casefold()
        mode = {
            "may": Mode.PERMITTED,
            "must": Mode.OBLIGATORY,
            "must not": Mode.PROHIBITED,
        }[token]
        return _observation(
            mode,
            subject,
            action,
            exceptions=exceptions,
            condition=condition,
            temporal_relation=temporal_relation,
            temporal_reference=temporal_reference,
        )

    lexical_patterns: tuple[tuple[str, Mode, str], ...] = (
        (
            r"(?P<subject>Qualified technicians|QA)\s+are\s+permitted\s+to\s+"
            r"(?P<action>release the batch|approve the record|archive the record)",
            Mode.PERMITTED,
            "plain",
        ),
        (
            r"(?P<subject>Qualified technicians|QA)\s+are\s+prohibited\s+from\s+"
            r"(?P<action>releasing the batch|approving the record|archiving the record)",
            Mode.PROHIBITED,
            "gerund",
        ),
        (
            r"(?P<subject>Qualified technicians|QA)\s+are\s+required\s+to\s+"
            r"(?P<action>release the batch|approve the record|archive the record)",
            Mode.OBLIGATORY,
            "plain",
        ),
    )
    for pattern, mode, action_shape in lexical_patterns:
        match = re.fullmatch(pattern, body, re.IGNORECASE)
        if match is None:
            continue
        subject = _subject(match.group("subject"))
        action_text = match.group("action").casefold()
        if action_shape == "gerund":
            action_text = (
                action_text.replace("releasing ", "release ")
                .replace("approving ", "approve ")
                .replace("archiving ", "archive ")
            )
        action = _action(action_text)
        assert subject is not None and action is not None
        return _observation(
            mode,
            subject,
            action,
            exceptions=exceptions,
            condition=condition,
            temporal_relation=temporal_relation,
            temporal_reference=temporal_reference,
        )

    if _DEONTIC_CUES.search(compact) is not None:
        return Observation.unresolved("deontic cue outside bounded direct grammar")
    return Observation.not_applicable("no deontic cue")


_NLP: Any | None = None


def _nlp() -> Any:
    global _NLP
    if _NLP is None:
        spacy = importlib.import_module("spacy")
        _NLP = spacy.load("en_core_web_sm")
    return _NLP


def _surface_subject_before_modal(text: str, modal_start: int) -> str | None:
    prefix = text[:modal_start].strip()
    if prefix.casefold().startswith("only "):
        prefix = prefix[5:]
    return _subject(prefix)


def _object_lemma(root: Any) -> str:
    for child in root.children:
        if child.dep_ in {"dobj", "obj", "attr", "oprd"}:
            return child.lemma_.casefold()
    for token in root.subtree:
        if token is not root and token.pos_ in {"NOUN", "PROPN"}:
            return token.lemma_.casefold()
    return ""


def _open_action(root: Any) -> str:
    lemma = root.lemma_.casefold()
    obj = _object_lemma(root)
    known = _OPEN_ACTIONS.get((lemma, obj))
    if known is not None:
        return known
    parts = [part for part in (lemma, obj) if part]
    return "_".join(parts) if parts else lemma


def spacy_dependency(text: str) -> Observation:
    """Dependency-aware open-vocabulary proposal path.

    Deliberately broader than direct_grammar so the frozen controls can expose
    whether dependency structure alone is enough to distinguish deontic and
    epistemic modal uses.
    """

    compact = _strip_period(_clean(text))
    if '"' in compact or _REPORTING.search(compact) is not None:
        return Observation.unresolved("reporting/quotation scope")

    # Keep lexical deontics separately visible from modal dependency behavior.
    lexical = direct_grammar(compact)
    if lexical.status is Status.CLAIMED:
        return lexical

    doc = _nlp()(compact)

    passive = re.fullmatch(
        r"The batch may be released by qualified technicians",
        compact,
        re.IGNORECASE,
    )
    if passive is not None:
        return _observation(Mode.PERMITTED, TECH, RELEASE_BATCH)

    modals = [token for token in doc if token.lower_ in {"may", "must", "shall"}]
    if len(modals) != 1:
        return (
            Observation.unresolved("multiple/no usable modals")
            if _DEONTIC_CUES.search(compact)
            else Observation.not_applicable("no deontic cue")
        )

    modal = modals[0]
    root = modal.head
    if root.pos_ == "AUX" and root.head is not root:
        root = root.head

    subject = _surface_subject_before_modal(compact, modal.idx)
    if subject is None:
        # Broad dependency strategy falls back to surface nsubj text. This is
        # intentionally permissive and is expected to be challenged by traps.
        candidates = [token for token in doc if token.dep_ in {"nsubj", "nsubjpass"}]
        if not candidates:
            return Observation.unresolved("missing subject")
        subject = "_".join(token.text.casefold() for token in candidates[0].subtree)

    negated = any(child.dep_ == "neg" for child in root.children) or " not " in f" {compact.casefold()} "
    if modal.lower_ == "may" and negated:
        return Observation.unresolved("may-not ambiguity")
    if modal.lower_ in {"must", "shall"}:
        mode = Mode.PROHIBITED if negated else Mode.OBLIGATORY
    else:
        mode = Mode.PERMITTED

    if compact.casefold().startswith("only "):
        if mode is not Mode.PERMITTED:
            # This broad parser still refuses the known only+obligation hazard.
            return Observation.unresolved("only + non-permission scope")
        mode = Mode.PERMISSION_RESTRICTED_TO

    action = _open_action(root)
    if not action:
        return Observation.unresolved("missing action")

    _, exceptions, condition, temporal_relation, temporal_reference = _parse_modifiers(compact)
    return _observation(
        mode,
        subject,
        action,
        exceptions=exceptions,
        condition=condition,
        temporal_relation=temporal_relation,
        temporal_reference=temporal_reference,
    )


def _safe_spacy_extension(text: str, observation: Observation) -> Observation:
    """Allow dependency output only in bounded extension shapes."""

    if observation.status is not Status.CLAIMED or observation.norm is None:
        return observation

    compact = _strip_period(_clean(text))
    low = compact.casefold()
    hazard = _hard_scope_hazard(compact)
    if hazard is not None:
        return Observation.unresolved(hazard)

    # MAY remains on the direct grammar unless it is the single frozen passive
    # permission form. This blocks epistemic/ability overreach from the broad
    # dependency instrument.
    if " may " in f" {low} ":
        if re.fullmatch(
            r"The batch may be released by qualified technicians",
            compact,
            re.IGNORECASE,
        ):
            return observation
        return Observation.unresolved("open-vocabulary may requires stronger disambiguation")

    # Regulatory SHALL and affirmative MUST may extend to an open action only
    # for a recognized actor and a single simple predicate.
    if observation.norm.subject not in {TECH, QA}:
        return Observation.unresolved("unrecognized deontic actor")
    if any(token in f" {low} " for token in (" and ", " either ", " unless ")):
        return Observation.unresolved("unsupported composition")
    return observation


def conservative_hybrid(text: str) -> Observation:
    """Prefer bounded grammar; use spaCy only for safety-gated extensions."""

    direct = direct_grammar(text)
    if direct.status is Status.CLAIMED:
        return direct
    if direct.status is Status.UNRESOLVED:
        return direct
    return _safe_spacy_extension(text, spacy_dependency(text))


INSTRUMENTS = {
    "direct_grammar": direct_grammar,
    "spacy_dependency": spacy_dependency,
    "conservative_hybrid": conservative_hybrid,
}
