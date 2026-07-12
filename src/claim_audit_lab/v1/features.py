"""Deterministic linguistic feature extractors for CAL v1 claims.

These replace the v0.2 ``_CLAIM_TYPE_PATTERNS`` regex tuples. Each extractor
is a pure function over a claim string. Numeric parsing uses ``quantulum3``;
syntactic features use a pinned ``spaCy`` dependency parse (``en_core_web_sm``).

The closed-set lexicons below (universal quantifier, prescriptive/hedge
modals, first-person opinion markers, and the Decision F sets — deontic
strength split, partial scope, approximation markers, absence lexemes) are
**ADR-locked** — new entries go through an ADR amendment, never a quiet add.
They are the v1 analog of the v0.2 trigger sets the F1–F15 review found
drifting. See ``plans/adr-v1-lexicons.md`` (contents + governance, incl. the
2026-07-02 amendment), DECISIONS.md § 2026-06-21 § 4,
``plans/adr-v1-rule-order.md``, and
``plans/adr-v1-rules-v1.4.0-semantic-fixes.md``.
"""

from __future__ import annotations

import functools
from typing import Literal, Protocol, TypeAlias, runtime_checkable

import spacy
from quantulum3 import classifier as _q3_classifier  # type: ignore[import-untyped]
from quantulum3 import parser as _q3
from spacy.language import Language
from spacy.tokens import Doc

from claim_audit_lab.text import STOPWORDS
from claim_audit_lab.v1.models import (
    ExtractedFeatures,
    ModalStrength,
    Quantity,
    SentenceType,
)

# CAL pins quantulum3 to deterministic no-classifier mode. quantulum3 sets
# USE_CLF=True whenever scikit-learn imports, then loads a bundled SGDClassifier
# pickle to disambiguate ambiguous unit *surfaces* (e.g. "mg/kg"). That pickle is
# scikit-learn 1.8-built; under the 1.9 runtime it loads only with an
# InconsistentVersionWarning ("may give invalid results") and has intermittently
# failed to unpickle outright (ModuleNotFoundError: No module named '_loss'). CAL
# consumes numeric *values* only (rule 6a compares values; the unit is trace-only
# metadata), and a byte-reproducible audit trace must not depend on an ML model
# running under a version combo its own library disclaims. USE_CLF=False routes
# disambiguation through quantulum3's deterministic static-table fallback
# (no_classifier.py) — environment-independent and crash-proof. disambiguate.py
# reads this flag at call time, so setting the module global here suffices.
_q3_classifier.USE_CLF = False

_SPACY_MODEL = "en_core_web_sm"

# --- Closed-set lexicons (ADR-locked) -------------------------------------
UNIVERSAL_QUANTIFIERS: frozenset[str] = frozenset(
    {"all", "every", "always", "never", "no", "none", "each", "any"}
)
PRESCRIBE_LEXEMES: frozenset[str] = frozenset(
    {
        "must",
        "shall",
        "should",
        "ought",
        "required",
        "require",
        "requires",
        "mandated",
        "mandatory",
        "obligated",
    }
)
HEDGE_LEXEMES: frozenset[str] = frozenset(
    {
        "may",
        "might",
        "could",
        "likely",
        "possibly",
        "perhaps",
        "probably",
        "seems",
        "appears",
        "suggests",
        "indicates",
    }
)
# --- Decision F sets (adr-v1-lexicons.md § Amendment 2026-07-02) -----------
# The deontic split is consumed only by rule 6b's strength comparison;
# PRESCRIBE_LEXEMES above still classifies the trace's modal_strength unchanged.
STRONG_DEONTIC_LEXEMES: frozenset[str] = frozenset(
    {"must", "shall", "required", "require", "requires", "mandated", "mandatory", "obligated"}
)
WEAK_DEONTIC_LEXEMES: frozenset[str] = frozenset(
    {"should", "ought", "recommended", "recommend", "recommends", "advised", "advisable"}
)
PARTIAL_SCOPE_LEXEMES: frozenset[str] = frozenset(
    {
        "some",
        "most",
        "many",
        "several",
        "few",
        "typically",
        "usually",
        "generally",
        "often",
        "sometimes",
        "occasionally",
    }
)
APPROXIMATION_MARKERS: frozenset[str] = frozenset(
    {"approximately", "approx", "about", "around", "roughly", "nearly", "almost", "circa", "~"}
)
# `free` is deliberately absent: it counts only in the syntactic shapes
# `X-free` / `free of|from` (see expresses_negation). `no` is matched by
# dep-edge (determiner), not bag membership.
ABSENCE_LEXEMES: frozenset[str] = frozenset(
    {"none", "without", "absence", "absent", "devoid", "lack"}
)
OPINION_MARKERS: tuple[str, ...] = (
    "i think",
    "i believe",
    "i feel",
    "in my opinion",
    "in my view",
    "to me",
    "we believe",
)
# `personally` is deliberately excluded: as the only single-token marker it
# collides with "personally identifiable information" (PII) — which CAL must
# audit, not route to out_of_scope. Re-add only behind a clause-initial +
# ROOT-verb gate. See plans/adr-v1-lexicons.md.
OPINION_MARKER_TOKENS: tuple[tuple[str, ...], ...] = tuple(
    tuple(marker.split()) for marker in OPINION_MARKERS
)
"""``OPINION_MARKERS`` pre-split into token sequences so the match is
contiguous and word-boundary aware — never a raw substring. See
``_contains_opinion_marker``."""
_ROOT = "ROOT"
_SUBJECT_DEPS = frozenset({"nsubj", "nsubjpass"})
_VERBAL_POS = frozenset({"VERB", "AUX"})


@functools.lru_cache(maxsize=1)
def _nlp() -> Language:
    """Load the pinned spaCy model once (NER disabled — not used)."""
    return spacy.load(_SPACY_MODEL, disable=["ner"])


def _parse(claim: str) -> Doc:
    return _nlp()(claim)


def has_numerical_value(claim: str) -> list[Quantity]:
    """Parse the claim for numeric values + units via ``quantulum3``.

    ``5 percent``, ``5%`` and ``5 pct`` collapse to the same ``Quantity``.
    Dimensionless units are recorded as ``None``. Empty list when no number.
    """
    results: list[Quantity] = []
    for q in _q3.parse(claim):
        unit_name = q.unit.name if q.unit is not None else None
        if unit_name == "dimensionless":
            unit_name = None
        results.append(Quantity(value=float(q.value), unit=unit_name, surface_text=str(q.surface)))
    return results


def has_explicit_negation(claim: str) -> bool:
    """True iff the claim contains a *clause-level* (syntactically scoped) negation.

    A ``neg`` dependency whose head is a verb/aux is clause-level negation
    ("does not validate" → True). Constituent negation, where the ``neg`` head
    is a noun/determiner ("not all systems" → False), is excluded — the
    dep-parse gives us the scope a word list cannot.
    """
    return any(t.dep_ == "neg" and t.head.pos_ in _VERBAL_POS for t in _parse(claim))


def has_universal_quantifier(claim: str) -> bool:
    """True iff the claim makes a universal-scope assertion.

    A closed-set quantifier lexeme counts only when it scopes the main clause:
    a clause-level adverb on the root (``never``/``always``), a determiner on
    the subject (``all systems pass``), or the subject itself. A determiner on
    an object (``we test all systems``) does not count.
    """
    doc = _parse(claim)
    for tok in doc:
        if tok.lower_ not in UNIVERSAL_QUANTIFIERS:
            continue
        if tok.dep_ in {"neg", "advmod"} and tok.head.dep_ == _ROOT:
            return True
        if tok.dep_ == "det" and tok.head.dep_ in _SUBJECT_DEPS:
            return True
        if tok.dep_ in _SUBJECT_DEPS:
            return True
    return False


def has_modal_strength(claim: str) -> ModalStrength:
    """Return the modal strength of the claim's assertion.

    ``prescribes`` (deontic: must/shall/should/required) takes precedence over
    ``hedges`` (epistemic: may/might/likely), which takes precedence over the
    default bare ``asserts``. Closed-set lexemes over lemma + surface form.
    """
    lexemes = {t.lower_ for t in _parse(claim)} | {t.lemma_.lower() for t in _parse(claim)}
    if lexemes & PRESCRIBE_LEXEMES:
        return "prescribes"
    if lexemes & HEDGE_LEXEMES:
        return "hedges"
    return "asserts"


DeonticStrength: TypeAlias = Literal["strong", "weak"]

_NON_CONTENT_POS = frozenset({"DET", "AUX", "PART", "PUNCT", "SPACE", "NUM", "SYM"})


def _lexeme_bag(text: str) -> set[str]:
    doc = _parse(text)
    return {t.lower_ for t in doc} | {t.lemma_.lower() for t in doc}


def expresses_negation(text: str) -> bool:
    """True iff ``text`` expresses negated/absent content in *any* surface form.

    The broad, passage-side counterpart to :func:`has_explicit_negation`
    (Decision F1). A passage agrees with a negated claim whether it negates the
    clause ("does not contain"), the constituent ("contains **no** latex"), or
    lexicalizes the absence ("latex-**free**", "**without** latex",
    "**absence of** latex"). The MoNLI backstop (rule A3) must not flip such a
    passage to contradicted, so its passage check needs this detector — the
    narrow clause-level one is claim-side scope policy, not absence detection.
    """
    doc = _parse(text)
    for tok in doc:
        if tok.dep_ == "neg" and tok.head.pos_ in _VERBAL_POS:
            return True
        if tok.lower_ == "no" and tok.dep_ == "det":
            return True
        if tok.lower_ in ABSENCE_LEXEMES or tok.lemma_.lower() in ABSENCE_LEXEMES:
            return True
        if tok.lower_ == "free":
            if tok.i > 0 and doc[tok.i - 1].text == "-":
                return True
            if tok.i + 1 < len(doc) and doc[tok.i + 1].lower_ in {"of", "from"}:
                return True
    return False


def deontic_strength(text: str) -> DeonticStrength | None:
    """Return the deontic strength of ``text``: strong, weak, or None.

    ``strong`` (must/shall/required/…) precedes ``weak`` (should/ought/
    recommended/…). Finer than the trace's three-way ``modal_strength`` —
    rule 6b compares claim strength against evidence strength on this axis
    (gold heuristic H2/H3: "required-on-recommended"), which the coarse
    ``prescribes`` bucket cannot express. Closed sets, ADR-locked.
    """
    lexemes = _lexeme_bag(text)
    if lexemes & STRONG_DEONTIC_LEXEMES:
        return "strong"
    if lexemes & WEAK_DEONTIC_LEXEMES:
        return "weak"
    return None


def scope_strength(text: str) -> DeonticStrength | None:
    """Classify evidence text's scope strength for the 6b comparison.

    ``strong`` — a strong-deontic or universal lexeme appears anywhere (bag
    membership, no dep-scope on the evidence side: precedence strong > weak
    makes the coarse read conservative, suppressing the downgrade).
    ``weak`` — a weak-deontic, hedge, or partial-scope lexeme appears.
    ``None`` — plain assertive text, which per Decision F2 does **not**
    trigger 6b: descriptive practice grounding a prescriptive claim is
    packet-relative support, not overreach.
    """
    lexemes = _lexeme_bag(text)
    if lexemes & (STRONG_DEONTIC_LEXEMES | UNIVERSAL_QUANTIFIERS):
        return "strong"
    if lexemes & (WEAK_DEONTIC_LEXEMES | HEDGE_LEXEMES | PARTIAL_SCOPE_LEXEMES):
        return "weak"
    return None


def has_approximation_marker(claim: str) -> bool:
    """True iff the claim carries an approximation marker (``approximately`` …).

    Claim-level, not per-quantity: claims are single propositions (compound
    claims are flagged upstream), and a false positive from the polysemous
    markers (``about``/``around``) only *widens* 6a's numeric tolerance —
    the conservative direction.
    """
    return any(t.lower_ in APPROXIMATION_MARKERS for t in _parse(claim))


def content_lemma_set(text: str) -> frozenset[str]:
    """Return the lowered content lemmas of ``text`` (Decision F5).

    Excludes determiners, auxiliaries, particles, punctuation, numerals, and
    the shared stopword set, so inflection pairs unify (``approved`` /
    ``approves`` → ``approve``) and function words never count as content.
    Replaces the v0.2 ``light_stem`` bag as 6c's verbatim primitive — per the
    Decision F invariant this signal may set the ``inferred`` flag but never
    decides a degree.
    """
    lemmas: set[str] = set()
    for tok in _parse(text):
        if tok.pos_ in _NON_CONTENT_POS or tok.like_num:
            continue
        lemma = tok.lemma_.lower().strip()
        if not lemma or lemma in STOPWORDS or tok.lower_ in STOPWORDS:
            continue
        lemmas.add(lemma)
    return frozenset(lemmas)


def claim_token_count(claim: str) -> int:
    """spaCy token count (non-space), the input-contract length proxy.

    The hard DeBERTa 512-token budget is enforced at the entailer (Phase 2);
    this lightweight count drives the 5–80 token routing in the rules layer.
    """
    return sum(1 for t in _parse(claim) if not t.is_space)


def is_compound_claim(claim: str) -> bool:
    """True iff the claim coordinates multiple assertions (a top-level ``conj``).

    Flags multi-assertion claims for the trace (43% of the PILOT-001 gold).
    v1 flags but does not split — splitting is upstream (Stage −1). See
    ``adr-v1-input-contract.md``.
    """
    return any(t.dep_ == "conj" for t in _parse(claim))


def _contains_opinion_marker(doc: Doc) -> bool:
    """True iff a first-person opinion marker appears as a contiguous token run.

    Token-sequence matching, not substring: ``to me`` fires on "according to
    me" but not on "to meet" / "to measure" / "to mention". Raw substring
    matching (the v0.2 habit) produced exactly that class of false positive.
    """
    lowers = [t.lower_ for t in doc if not t.is_space]
    for phrase in OPINION_MARKER_TOKENS:
        width = len(phrase)
        if any(tuple(lowers[i : i + width]) == phrase for i in range(len(lowers) - width + 1)):
            return True
    return False


def sentence_type(claim: str) -> SentenceType:
    """Classify the claim's sentence type for the out_of_scope gate.

    First-person opinion markers win, then questions ("?"), then subject-less
    imperatives; otherwise declarative. The opinion check is token-aware (see
    ``_contains_opinion_marker``), not substring.
    """
    doc = _parse(claim)
    if _contains_opinion_marker(doc):
        return "opinion"
    if claim.strip().endswith("?"):
        return "question"
    roots = [t for t in doc if t.dep_ == _ROOT]
    if roots:
        root = roots[0]
        has_subject = any(c.dep_ in {"nsubj", "nsubjpass", "expl"} for c in root.children)
        if root.pos_ in _VERBAL_POS and not has_subject:
            return "imperative"
    return "declarative"


@runtime_checkable
class FeatureExtractor(Protocol):
    """A bundle of per-claim feature extractors.

    Implementations compose the extractor functions above into one ``extract``
    call so the rest of the pipeline stays agnostic about the linguistic
    toolchain producing the features.
    """

    def extract(self, claim: str) -> ExtractedFeatures:
        """Run all v1 feature extractors over ``claim`` and return them."""
        ...


__all__ = [
    "ABSENCE_LEXEMES",
    "APPROXIMATION_MARKERS",
    "DeonticStrength",
    "FeatureExtractor",
    "HEDGE_LEXEMES",
    "OPINION_MARKERS",
    "PARTIAL_SCOPE_LEXEMES",
    "PRESCRIBE_LEXEMES",
    "STRONG_DEONTIC_LEXEMES",
    "UNIVERSAL_QUANTIFIERS",
    "WEAK_DEONTIC_LEXEMES",
    "claim_token_count",
    "content_lemma_set",
    "deontic_strength",
    "expresses_negation",
    "has_approximation_marker",
    "has_explicit_negation",
    "has_modal_strength",
    "has_numerical_value",
    "has_universal_quantifier",
    "is_compound_claim",
    "scope_strength",
    "sentence_type",
]
