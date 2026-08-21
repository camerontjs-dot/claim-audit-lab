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
import re
from typing import Literal, Protocol, TypeAlias, runtime_checkable

import spacy
from quantulum3 import classifier as _q3_classifier  # type: ignore[import-untyped]
from quantulum3 import parser as _q3
from spacy.language import Language
from spacy.tokens import Doc, Token

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
# Bound language (cal-rules-v1.8.0, adr-v1-bound-instantiation.md). A passage
# that states a *bound* — a permitted region — is not stating a *value*, and
# the two rules that compare claim against passage on the assumption of a
# stated value (`6a` equality-within-tolerance, `A3` negation mirroring) have
# no valid operator over it. Single lexemes only; multi-word forms live in
# BOUND_PHRASES because spaCy tokenizes them apart.
BOUND_LEXEMES: frozenset[str] = frozenset(
    {
        "maximum",
        "minimum",
        "max",
        "min",
        "exceed",
        "exceeds",
        "exceeding",
        "threshold",
        "ceiling",
        "limit",
        "limits",
        "between",
    }
)
BOUND_PHRASES: tuple[str, ...] = (
    "at least",
    "at most",
    "no more than",
    "no less than",
    "no fewer than",
    "not exceed",
    "not to exceed",
    "greater than",
    "less than",
    "fewer than",
    "or more",
    "or less",
    "or greater",
    "or fewer",
    "or higher",
    "or lower",
    "up to",
)
# `Part 11`, `21 CFR`, `ICH Q7`, `Annex 11` — a citation is an address, not a
# measurement. quantulum3 reads the digits as quantities, so 6a compares them
# numerically against the passage (D3, live in the shipped rule).
_CITATION_PATTERN = re.compile(
    # title number preceding the code — the `21` of `21 CFR Part 11`
    r"\b\d+(?:\.\d+)*\s*(?:CFR|USC|C\.F\.R\.)\b"
    # …or the locator following a citation keyword — the `11` of `Part 11`
    r"|\b(?:CFR|USC|Part|Annex|Appendix|Chapter|Section|ICH|ISO|EN|Rev(?:ision)?)\b"
    r"[\s.]*(?:[A-Z]\s*)?\d+(?:\.\d+)*",
    re.IGNORECASE,
)
_CITATION_NUMBER = re.compile(r"\d+(?:\.\d+)*")
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
_CLAUSE_SUBJECT_DEPS = frozenset({"expl", "nsubj", "nsubjpass"})
# A1 combined structural guard (adr-v1-a1-imperative-hardening.md): the only
# parser dependencies allowed before an imperative root — interjections
# ("Please …"), adverbial modifiers ("Kindly …"), negation ("Never …"), and
# auxiliaries ("Do not …"). Any other pre-root structure is declarative.
_IMPERATIVE_PREFIX_DEPS = frozenset({"advmod", "aux", "intj", "neg"})
# Depth bound for the elided-subject walk: enough for ordinary coordination,
# finite so a malformed parse cannot loop.
_MAX_CONJUNCT_WALK = 4


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


# Source-coverage claims (cal-rules-v1.10.0, D11). A claim about what a *text*
# does or does not say is not the same kind of claim as one about the world.
# "The guidance does not address X" is settled by the source's completeness;
# "The formulation does not contain X" is settled by evidence. Both lists are
# closed claim-side lexicons, like UNIVERSAL_QUANTIFIERS and ABSENCE_LEXEMES —
# nothing here compares claim terms to passage terms, which the Decision F
# invariant forbids from deciding a degree.
SOURCE_NOUNS: frozenset[str] = frozenset(
    {
        "annex",
        "chapter",
        "clause",
        "document",
        "guidance",
        "guideline",
        "instruction",
        "manual",
        "policy",
        "procedure",
        "protocol",
        "regulation",
        "requirement",
        "section",
        "sop",
        "specification",
        "standard",
        "text",
    }
)
# Predicates about the presence of content *in a text*. Object-level verbs are
# deliberately excluded: a document can genuinely assert that something is not
# required, and evidence can genuinely refute that, so "does not require" and
# "does not apply" stay outside this set.
COVERAGE_VERBS: frozenset[str] = frozenset(
    {
        "address",
        "contain",
        "cover",
        "define",
        "describe",
        "discuss",
        "include",
        "list",
        "mention",
        "name",
        "prescribe",
        "reference",
        "specify",
        "state",
    }
)


def _subject_of(token: Token) -> Token | None:
    """The predicate's subject, walking up conjuncts when it is elided.

    "The guidance mentions X but does not specify Y" attaches no subject to
    *specify*; the conjunct head carries it.
    """
    node = token
    for _ in range(_MAX_CONJUNCT_WALK):
        for child in node.children:
            if child.dep_ in ("nsubj", "nsubjpass"):
                return child
        if node.dep_ == "conj" and node.head is not node:
            node = node.head
            continue
        return None
    return None


def source_coverage_claim(claim: str) -> tuple[str, str] | None:
    """``(subject, predicate)`` iff the claim denies that a *document* says something.

    True for "The guidance does not address retention samples" — a claim about
    the contents of a text, whose truth turns on whether the bundle *is* the
    source. False for "Relocation of qualified equipment does not require
    requalification", which is about the world and which a passage can refute.

    Both conditions are required. The subject test alone would catch "the
    guidance does not apply to biologics", which a passage can legitimately
    refute; the verb test alone would catch "the formulation does not contain
    latex", which is not about a text at all.
    """
    for tok in _parse(claim):
        if tok.dep_ != "neg" or tok.head.pos_ not in _VERBAL_POS:
            continue
        predicate = tok.head
        subject = _subject_of(predicate)
        if subject is None:
            return None
        subject_lemma = subject.lemma_.lower()
        predicate_lemma = predicate.lemma_.lower()
        if subject_lemma in SOURCE_NOUNS and predicate_lemma in COVERAGE_VERBS:
            return (subject_lemma, predicate_lemma)
        return None
    return None


# Site/subject scope (cal-rules-v1.13.0, A7). Eligibility only: a contradiction
# whose locative/nsubj *location phrase* is disjoint from the claim's is not
# licensed to decide. Closed location-head lexicon + dependency attachment —
# nothing here compares claim terms to passage terms to flip a degree (Decision F).
# Distinctive leftovers after stripping the heads are what must overlap.
LOCATION_HEADS: frozenset[str] = frozenset(
    {
        "area",
        "building",
        "campus",
        "chamber",
        "depot",
        "facility",
        "harbor",
        "lab",
        "laboratory",
        "location",
        "plant",
        "room",
        "site",
        "sites",
        "slip",
        "suite",
        "wing",
    }
)
_LOCATIVE_PREPS: frozenset[str] = frozenset({"at", "in", "from"})
_SCOPE_MOD_DEPS: frozenset[str] = frozenset({"compound", "amod", "nummod", "npadvmod"})


# --- D14: identifiers must not be read as numbers --------------------------
#
# spaCy tags an identifier like ``CH-07`` as a NUMBER, so it attaches as a
# modifier rather than heading the subject. With an ambiguous following verb the
# parser is then left with no nominal subject at all — *recorded* becomes an
# adjective and a noun becomes the ROOT — and scope extraction finds nothing on
# that side. ``scope_mismatch`` reads "nothing found" as "no location named",
# A7 stands down, and the adverse verdict A7 exists to withhold goes through.
# Measured at 14 of 66 identifier/verb combinations before this fix.
#
# Forcing ``token.pos_`` does not help: spaCy's parser reads tok2vec vectors, not
# tags, and the parse is unchanged. What works is handing the parser a token it
# can only read as a proper noun, then mapping the anchors back.
#
# Scoped to scope extraction on purpose. Every other feature keeps the exact
# parse it had, so this cannot move a verdict anywhere else. That identifiers are
# read as numbers *elsewhere* is a separate, still-open issue — related to D3,
# where regulatory citations were being parsed as quantities.
_IDENTIFIER_CANDIDATE = re.compile(r"\b[A-Za-z][A-Za-z0-9]*(?:[-_/][A-Za-z0-9]+)*\b")
_PLACEHOLDER_STEM = "Zq"


def _is_identifier(token: str) -> bool:
    """A letter-initial token carrying a digit: an equipment ID, SOP or lot code.

    Letter-initial is what keeps quantities out. ``12-month``, ``25``, ``3rd`` and
    ``211.22`` all start with a digit and are left untouched, so the numeric
    features — and D3's citation handling — see exactly what they saw before.
    """
    return token[:1].isalpha() and any(char.isdigit() for char in token)


def _placeholder(index: int) -> str:
    """``Zqa``, ``Zqb`` … — letters only, so the tagger cannot read them as numbers."""
    name = ""
    remaining = index
    while True:
        name = chr(ord("a") + remaining % 26) + name
        remaining = remaining // 26 - 1
        if remaining < 0:
            break
    return _PLACEHOLDER_STEM + name


def _normalise_identifiers(text: str) -> tuple[str, dict[str, str]]:
    """Swap identifier tokens for letter-only placeholders, and return the mapping.

    Deterministic: placeholders are assigned in order of first appearance, so the
    same text always normalises to the same string. Anchors are mapped back before
    comparison, so two texts naming different identifiers stay different even
    though both may use ``Zqa``.
    """
    assigned: dict[str, str] = {}
    mapping: dict[str, str] = {}

    def swap(match: re.Match[str]) -> str:
        original = match.group(0)
        if not _is_identifier(original):
            return original
        placeholder = assigned.get(original)
        if placeholder is None:
            placeholder = _placeholder(len(assigned))
            assigned[original] = placeholder
            mapping[placeholder.lower()] = original.lower()
        return placeholder

    return _IDENTIFIER_CANDIDATE.sub(swap, text), mapping


def _phrase_tokens(head: Token) -> set[str]:
    """Lemma (and digit surface) of ``head`` plus its left-side noun modifiers."""
    parts = {head.lemma_.lower()}
    if head.like_num or head.lemma_.isdigit():
        parts.add(head.text.lower())
    for child in head.children:
        if child.dep_ in _SCOPE_MOD_DEPS:
            parts.update(_phrase_tokens(child))
    return parts


def scope_anchors(text: str) -> frozenset[str]:
    """Distinctive lemmas of location phrases in ``text``.

    A phrase counts only when its head (or a modifier) is in ``LOCATION_HEADS``.
    The heads themselves are then stripped, so "Building 4 manufacturing site"
    and "Packaging sites" become ``{building, 4, manufacturing}`` vs
    ``{packaging}`` — disjoint, which is the A7 trigger. Same-site variants
    that share ``4`` / ``building`` do not trigger.

    Identifier tokens are normalised before parsing and mapped back afterwards,
    so ``Chamber CH-07`` is read as a named entity rather than as a number
    (D14). See ``_normalise_identifiers``.
    """
    normalised, identifiers = _normalise_identifiers(text)
    distinctive: set[str] = set()
    for tok in _parse(normalised):
        head: Token | None = None
        if tok.dep_ in {"nsubj", "nsubjpass"}:
            head = tok
        elif tok.dep_ == "pobj" and tok.head.lemma_.lower() in _LOCATIVE_PREPS:
            head = tok
        if head is None:
            continue
        phrase = {identifiers.get(word, word) for word in _phrase_tokens(head)}
        if not (phrase & LOCATION_HEADS) and head.lemma_.lower() not in LOCATION_HEADS:
            continue
        for word in phrase:
            if word in LOCATION_HEADS or word in STOPWORDS or len(word) <= 1:
                continue
            distinctive.add(word)
    return frozenset(distinctive)


def scope_mismatch(claim: str, passage: str) -> bool:
    """True iff both sides name a location phrase and those phrases are disjoint.

    Empty on either side is not a mismatch — A7 must not invent scope the parse
    did not find, and must not suppress a subject-less true contradiction.
    """
    claim_scope = scope_anchors(claim)
    passage_scope = scope_anchors(passage)
    return bool(claim_scope) and bool(passage_scope) and claim_scope.isdisjoint(passage_scope)


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


def expresses_bound(text: str) -> bool:
    """True iff ``text`` states a bound — a permitted region — rather than a value.

    ``cal-rules-v1.8.0``. A passage saying *"a maximum of 6 hours"* does not
    assert that the duration **is** six hours; it asserts that compliant
    durations satisfy ``x <= 6``. Two rules compare claim against passage on
    the assumption that the passage states a value, and neither has a valid
    operator over a bound:

    * ``6a`` asks *are the quantities equal, within tolerance?* On a claim that
      instantiates the bound (*"a cycle reaching seven hours triggers a hold"*)
      inequality is the **content** of the claim, not evidence against it.
    * ``A3`` asks *does the passage express the claim's negation?* A negative
      consequence (*"a batch below 40% cannot pass"*) follows correctly from a
      positively-stated rule, which need not express any negation.

    Used only to **suppress** those rules, never to fire one. A false positive
    costs a rule fire; it cannot produce a verdict. That asymmetry is why a
    closed-set lexical detector is permitted here under the Decision F
    invariant (*overlap may flag, never decide*) — the invariant guards against
    lexically-driven **adverse** verdicts, and suppression is the safe
    direction.
    """
    lowered = text.lower()
    if any(phrase in lowered for phrase in BOUND_PHRASES):
        return True
    return any(t.lower_ in BOUND_LEXEMES or t.lemma_.lower() in BOUND_LEXEMES for t in _parse(text))


def citation_numbers(text: str) -> frozenset[float]:
    """Numbers that appear inside a regulatory citation in ``text`` (D3).

    ``21 CFR Part 11`` is an address, not a measurement, but quantulum3 reads
    it as the quantities 21 and 11 — which ``6a`` then compares numerically
    against the passage. quantulum3 exposes no span in the pinned
    deterministic (no-classifier) mode, so the exclusion is by **value**: a
    claim quantity whose value also appears inside a citation is not compared.

    Known and accepted cost: a claim citing *Part 11* whose genuine measurement
    is also ``11`` loses that comparison. That suppresses a rule fire, never a
    verdict, so it fails in the safe direction.
    """
    found: set[float] = set()
    for match in _CITATION_PATTERN.finditer(text):
        for number in _CITATION_NUMBER.findall(match.group()):
            try:
                found.add(float(number))
            except ValueError:  # pragma: no cover — regex admits only numerics
                continue
    return frozenset(found)


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


def has_conjunct_scoped_negation(claim: str) -> bool:
    """True when negation is confined to a non-root coordinated conjunct.

    A3's negation mirror is unary.  It has no valid operator when a compound
    claim asserts one conjunct and negates another (``P but not Q``).  Keep the
    detector deliberately narrow: if the root predicate is also negated, the
    negation can scope the whole coordination and A3 must retain its ordinary
    contradiction guard.
    """
    doc = _parse(claim)
    negated_heads = [token.head for token in doc if token.dep_ == "neg"]
    return bool(negated_heads) and all(head.dep_ == "conj" for head in negated_heads)


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


_UNIVERSAL_FIRST_TOKENS = frozenset({"all", "each", "every"})
_DO_SUPPORT = {"VBD": "did", "VBP": "do", "VBZ": "does"}


def negate_claim(claim: str) -> str | None:
    """Return the structural sentential negation of ``claim``, or None to abstain.

    The A4 negation-consistency negator (``adr-v1-slg09-negation-consistency.md``),
    pure parse structure per the Decision F invariant. First matching rule wins:
    compound guard (abstain — negation scope over coordinated assertions is
    ambiguous); clause-level negation removal (¬¬X → X); universal-quantifier
    prefixing ("Every … passed" → "Not every … passed" — never verb-scope, which
    would change the proposition); copular-root insertion; auxiliary insertion;
    finite do-support. Anything else abstains, and an abstention must never
    demote — the caller retains the original verdict.
    """
    if ";" in claim or is_compound_claim(claim):
        return None
    doc = _parse(claim)
    tokens = list(doc)

    first_alpha = next((t for t in tokens if not t.is_space and not t.is_punct), None)
    # D5: ¬(No X P) is (Some X P). Auxiliary insertion yields "No X was not P",
    # a different proposition. Abstain rather than invert. "None" as a bare
    # subject is the same quantifier family. Incidence 1/325; safe direction.
    if first_alpha is not None and first_alpha.lower_ == "no" and first_alpha.dep_ == "det":
        return None
    if first_alpha is not None and first_alpha.lower_ == "none":
        return None

    for tok in tokens:
        if tok.dep_ == "neg" and tok.head.pos_ in _VERBAL_POS:
            return "".join(t.text + t.whitespace_ for t in tokens if t.i != tok.i).strip()
    if (
        first_alpha is not None
        and first_alpha.lower_ in _UNIVERSAL_FIRST_TOKENS
        and has_universal_quantifier(claim)
    ):
        stripped = claim.strip()
        return "Not " + stripped[0].lower() + stripped[1:]

    roots = [t for t in tokens if t.dep_ == _ROOT]
    if not roots:
        return None
    root = roots[0]

    def _insert_not_after(index: int) -> str:
        parts = []
        for t in tokens:
            if t.i == index:
                parts.append(t.text + " not" + (" " if t.whitespace_ else ""))
            else:
                parts.append(t.text + t.whitespace_)
        return "".join(parts).strip()

    if root.pos_ == "AUX" or root.lemma_ == "be":
        return _insert_not_after(root.i)

    auxes = [c for c in root.children if c.dep_ in {"aux", "auxpass", "cop"}]
    if auxes:
        return _insert_not_after(min(auxes, key=lambda t: t.i).i)

    if root.pos_ == "VERB" and root.tag_ in _DO_SUPPORT:
        parts = []
        for t in tokens:
            if t.i == root.i:
                parts.append(f"{_DO_SUPPORT[root.tag_]} not {root.lemma_}{t.whitespace_}")
            else:
                parts.append(t.text + t.whitespace_)
        return "".join(parts).strip()

    return None


def _is_imperative_shape(doc: Doc, root: Token) -> bool:
    """Combined A1 structural guard over a subject-less verbal root.

    Grammar decides, not a word list (``adr-v1-a1-imperative-hardening.md``):
    (1) a non-root ``VERB``/``AUX`` carrying its own subject makes the sentence
    declarative — recovering parses where the apparent root heads a noun-initial
    clause whose subject attaches to a secondary verbal predicate; (2) every
    non-space, non-punctuation token before the root must be discourse,
    negation, or auxiliary material (``_IMPERATIVE_PREFIX_DEPS``). Deliberately
    conservative: an unusual imperative with other pre-root structure stays in
    scope for audit rather than being discarded ``out_of_scope`` — the safer
    error direction.
    """
    if any(
        token is not root
        and token.pos_ in _VERBAL_POS
        and any(child.dep_ in _CLAUSE_SUBJECT_DEPS for child in token.children)
        for token in doc
    ):
        return False
    return all(
        token.dep_ in _IMPERATIVE_PREFIX_DEPS
        for token in doc[: root.i]
        if not token.is_space and not token.is_punct
    )


def sentence_type(claim: str) -> SentenceType:
    """Classify the claim's sentence type for the out_of_scope gate.

    First-person opinion markers win, then questions ("?"), then subject-less
    imperatives passing the combined A1 structural guard (see
    ``_is_imperative_shape``); otherwise declarative. The opinion check is
    token-aware (see ``_contains_opinion_marker``), not substring.
    """
    doc = _parse(claim)
    if _contains_opinion_marker(doc):
        return "opinion"
    if claim.strip().endswith("?"):
        return "question"
    roots = [t for t in doc if t.dep_ == _ROOT]
    if roots:
        root = roots[0]
        has_subject = any(c.dep_ in _CLAUSE_SUBJECT_DEPS for c in root.children)
        if root.pos_ in _VERBAL_POS and not has_subject and _is_imperative_shape(doc, root):
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
    "COVERAGE_VERBS",
    "APPROXIMATION_MARKERS",
    "DeonticStrength",
    "FeatureExtractor",
    "HEDGE_LEXEMES",
    "OPINION_MARKERS",
    "PARTIAL_SCOPE_LEXEMES",
    "PRESCRIBE_LEXEMES",
    "SOURCE_NOUNS",
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
    "has_conjunct_scoped_negation",
    "negate_claim",
    "scope_strength",
    "source_coverage_claim",
    "sentence_type",
]
