"""v2 decision layer — a pipeline of total stages, for testing against v1.

**Experimental. Not public API.** It ships — it is under ``src/``, so setuptools
packages it and `mypy --strict` checks it, taking the counted source files from
49 to 51. An earlier draft of this header said the opposite of all three, having
been written for a copy of the file that lived outside ``src/``; it is recorded
here because a module that misdescribes its own status is the same defect class
as D17, and this one sat in the header of the file that exists to fix D17.

What "not public API" therefore has to mean in practice: it is deliberately not
re-exported from ``claim_audit_lab.v1.impl``, so nothing reaches it without
naming ``pipeline_rules`` outright, and no stability promise attaches to any name
in it.

This replaces the *decision layer only*. Retrieval, entailment, thresholds and
the seal model are untouched; v2 consumes the same stage-1-to-3 evidence v1
receives and returns a verdict. That makes it replayable against sealed traces
with no model load, which is the point: it can be scored in seconds on every
corpus that has ever been run.

## What it changes, and the measurement behind each

1. **No jumps.** v1 has 33 ``if`` branches, 12 early returns and one
   re-aggregation loop. An exception there *redirects control*, so each gate has
   to remember its own fallback and D6, D7, D9 and D16 are four gates that
   forgot. Here an exception **marks a passage** and every stage runs to
   completion.

2. **Three stages, split by arity, not one.** X1 measured what each v1 gate
   reads: 6 are ``(claim, passage)``, 7 read the claim alone, 3 read the whole
   set. A single eligibility stage cannot hold all three, so predicates sort by
   what they read. Predicates in different stages cannot conflict, which removes
   most of the precedence coupling without anyone deciding a precedence.

3. **Every passage is evaluated.** X1 measured v1's eligibility coverage at
   **33.4%**: of 398 admitted passages across 131 audits, 265 were never
   examined by any predicate. Here every admitted passage gets every
   passage-level predicate.

4. **Removals are recorded.** Every filter emits what it dropped and why.
   A rule that decides adversely can see what it is not looking at. D6 demotes on
   evidence it never looked at; D16 withholds while an eligible passage sits
   unexamined. Both are decisions taken in the presence of an invisible drop.

5. **Eligibility is per-role.** In v1 a passage is eligible or not. But ``P1``
   only ever gated *adverse* decisions: a background source may not refute, and
   may still support. One bit cannot say that, so v1 says it with control flow.

6. **The entailment distribution is carried.** v1's rules read ``label`` and
   ``score``, the argmax and its probability, and never ``p_entail`` or
   ``p_contradict`` (0 references). A passage at entail 0.51 / contradict 0.48
   and one at entail 0.51 / neutral 0.48 are the same object to every v1 rule.
   ``PassageEvidence`` carries both, so a rule here *can* read them — but as of
   this revision none does, and every v2 decision still runs off argmax and its
   probability. Carrying the distribution is the precondition, not the fix; the
   claim is a plumbing change, and stating it as more than that would be the
   over-claim this module is otherwise written against.

7. **Claim type is declared when the caller knows it, parsed only as fallback.**
   X2a measured a three-line resolver *given declared claim type* beating v1's
   445 lines by six cases on adversarial input. The parse is the fallback, and
   when it is used that is recorded, because D17 is what an unrecorded parse
   fallback looks like.

8. **Four null reasons, one per stage that failed.** No extra rule: the stage
   that could not proceed names the outcome.

## What it deliberately does not change

Thresholds, retriever, entailer, the retrieval floor (closed at 0.40), the seal
model, and the invariant that lexical overlap may flag but never decide.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from claim_audit_lab.v1.interval_algebra import evaluate_interval_containment

# ---------------------------------------------------------------------------
# Vocabulary
# ---------------------------------------------------------------------------

Degree = Literal["supported", "contradicted", "not_checkable"]
Role = Literal["support", "refute"]

#: One reason per stage that could not proceed. X4 measured v1's declared
#: vocabulary at 3 of 5 `VerdictReason` values ever emitted, 2 of 6 `AuditFlag`,
#: and 1 of 6 `CitationStatus`. Declaring a vocabulary up front is what produces
#: that; here the reason is whatever stage stopped.
NullReason = Literal[
    "out_of_form",  # stage 0 — not a checkable assertion
    "no_evidence",  # stage 1 — nothing was admitted. A real null
    "all_ineligible",  # stage 2 — evidence was held, none of it may decide
    "no_signal",  # stage 3 — eligible evidence, no reading above threshold
    "not_resolvable",  # stage 4 — readings that do not combine
]

#: Only two modes. `quantitative` was a third in the first draft and it was
#: wrong: see `resolve`. A quantity is a *flag* on a verdict, not a route.
Mode = Literal["ordinary", "coverage"]

SUPPORTED_THRESHOLD = 0.70
CONTRADICTED_THRESHOLD = 0.70
RETRIEVAL_FLOOR = 0.40


# ---------------------------------------------------------------------------
# Records. Every stage returns one; nothing is dropped without a record.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Removal:
    """One thing a stage removed, and why.

    The whole point of the type. A filter that removes silently is
    indistinguishable downstream from a filter that found nothing, and every
    family-two defect is a rule deciding confidently while something it could
    not see had been removed.
    """

    passage_id: str
    stage: str
    predicate: str
    reason: str
    detail: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ClaimFrame:
    """The claim, parsed once.

    v1 calls ``_parse(claim)`` at 16 uncached sites, so a claim is parsed up to
    16 times per audit and every feature is an independent projection of the same
    sentence that no rule sees as one object. That is the representational form
    of the family-one defects: ``has_explicit_negation`` answers "is there a
    scoped *not*", and two absence gates were built on it as though it answered
    "is this a claim about what a document says".
    """

    text: str
    mode: Mode
    mode_source: Literal["declared", "parsed"]
    polarity: Literal["affirmative", "negative"]
    admissible: bool
    quantities: list[Any]
    token_count: int
    sentence_type: str
    scope_anchors: frozenset[str] = frozenset()
    universal: bool = False

    @property
    def mode_was_guessed(self) -> bool:
        """True when the mode came from a parse rather than from the caller.

        Recorded on every verdict. An unrecorded parse fallback is exactly what
        D17 is: two gates silently unreachable, and a register that read as
        though they had considered the case and declined.
        """
        return self.mode_source == "parsed"


@dataclass(frozen=True)
class PassageEvidence:
    """One passage's admission, eligibility and reading.

    A *union* is also a PassageEvidence, with ``members`` naming the passages
    read together and ``passage_id`` their joined handle. Unions compete with
    singles rather than replacing them: the sufficiency probe concatenated
    passages as a diagnostic and said so, and concatenating unconditionally
    would dilute single-passage signal and destroy per-passage attribution.
    """

    passage_id: str
    retrieval_score: float
    label: str
    score: float
    p_entail: float | None
    p_contradict: float | None
    eligible_for: frozenset[Role]
    ineligibility: tuple[Removal, ...] = ()
    trust_level: str | None = None
    source_id: str | None = None
    #: Empty for a single passage; the member ids for a union.
    members: tuple[str, ...] = ()

    @property
    def is_union(self) -> bool:
        return len(self.members) > 1

    def may(self, role: Role) -> bool:
        return role in self.eligible_for


@dataclass(frozen=True)
class V2Verdict:
    degree: Degree
    null_reason: NullReason | None
    mode: Mode
    mode_was_guessed: bool
    deciding_passages: tuple[str, ...]
    removals: tuple[Removal, ...]
    stage_reached: str
    notes: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "degree": self.degree,
            "null_reason": self.null_reason,
            "mode": self.mode,
            "mode_was_guessed": self.mode_was_guessed,
            "deciding_passages": list(self.deciding_passages),
            "n_removed": len(self.removals),
            "removals": [
                {
                    "passage_id": r.passage_id,
                    "stage": r.stage,
                    "predicate": r.predicate,
                    "reason": r.reason,
                    **({"detail": r.detail} if r.detail else {}),
                }
                for r in self.removals
            ],
            "stage_reached": self.stage_reached,
            "notes": list(self.notes),
        }


# ---------------------------------------------------------------------------
# Stage 0 — claim admissibility and mode. Claim-level (X1: 7 v1 gates).
# ---------------------------------------------------------------------------

MIN_CLAIM_TOKENS = 5

#: Closed claim-side lexicons, as in v1. Nothing here compares claim terms to
#: passage terms, which the Decision F invariant forbids from deciding a degree.
SOURCE_NOUNS = frozenset(
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
        "record",
        "regulation",
        "report",
        "requirement",
        "requirements",
        "section",
        "sop",
        "specification",
        "standard",
        "text",
    }
)

#: Coverage predicates. v1 reaches these only through a spaCy ``neg`` dependency,
#: so only *not*, *never* and *n't* get here. X5 measured 1 of 38 paraphrases
#: reaching the gate against 7 of 10 originals. The fix is not a longer list: it
#: is that the caller declares the mode and this is the fallback.
COVERAGE_PREDICATES = frozenset(
    {
        "address",
        "cover",
        "mention",
        "prescribe",
        "specify",
        "state",
        "discuss",
        "describe",
        "define",
        "require",
        "contain",
        "include",
        "silent",
        "omit",
        "lack",
        "reference",
        "provision",
    }
)

#: Surface forms that carry negation without producing a ``neg`` dependency.
#: Present so the fallback is less bad than v1's, NOT as the fix. A lexicon
#: moves the boundary and leaves the shape; the next phrasing breaks it again.
NEGATION_SURFACES = (
    "is silent",
    "are silent",
    "silent on",
    "makes no mention",
    "make no mention",
    "no mention of",
    "omits",
    "omit ",
    "fails to",
    "fail to",
    "lacks",
    "lack any",
    "nothing in",
    "neither",
    " nor ",
    "absent from",
    "does not",
    "do not",
    "did not",
    "never",
    "n't",
    "no requirement",
    "no provision",
    "without reference",
)


def build_claim_frame(
    claim_text: str,
    features: dict[str, Any],
    *,
    declared_mode: Mode | None = None,
    scope_anchors: frozenset[str] = frozenset(),
) -> ClaimFrame:
    """Assemble the claim once. Total: always returns a frame.

    ``declared_mode`` is the caller's statement of what kind of claim this is.
    When absent the mode is guessed and the guess is recorded on the verdict.
    """
    lowered = claim_text.lower()
    negative = bool(features.get("has_explicit_negation")) or any(
        surface in lowered for surface in NEGATION_SURFACES
    )

    if declared_mode is not None:
        mode, mode_source = declared_mode, "declared"
    else:
        subject_is_a_source = any(f" {noun} " in f" {lowered} " for noun in SOURCE_NOUNS)
        predicate_is_coverage = any(verb in lowered for verb in COVERAGE_PREDICATES)
        # Note what the first draft did here and why it was wrong: it routed any
        # claim carrying a numerical value to a `quantitative` mode. Construction
        # gold rejected it immediately, and one of the five regressions was
        # CG-23b, routed to quantities because "Building 4" contains a numeral.
        # That is D14's confusion, identifiers read as quantities, reproduced in
        # new code by the same author who had just fixed it in the old code.
        is_coverage = negative and subject_is_a_source and predicate_is_coverage
        mode = "coverage" if is_coverage else "ordinary"
        mode_source = "parsed"

    sentence_type = str(features.get("sentence_type", "declarative"))
    token_count = int(features.get("claim_token_count", 0))
    admissible = sentence_type not in ("opinion", "question", "imperative") and (
        token_count >= MIN_CLAIM_TOKENS
    )

    return ClaimFrame(
        text=claim_text,
        mode=mode,
        mode_source=mode_source,  # type: ignore[arg-type]
        polarity="negative" if negative else "affirmative",
        admissible=admissible,
        quantities=list(features.get("numerical_values") or []),
        token_count=token_count,
        sentence_type=sentence_type,
        scope_anchors=scope_anchors,
        universal=bool(features.get("has_universal_quantifier")),
    )


# ---------------------------------------------------------------------------
# Stage 1 — admit. Set-level.
# ---------------------------------------------------------------------------

NEAR_MISS_BAND = 0.05


def admit(
    retrieval: list[dict[str, Any]],
    entailment: list[dict[str, Any]],
    *,
    floor: float = RETRIEVAL_FLOOR,
) -> tuple[list[str], list[Removal]]:
    """Return admitted passage ids and a record of everything dropped.

    A near miss is recorded distinctly. v1's ``A2_retrieval_empty`` says only
    "no passage cleared the floor", so a case where five passages scored 0.39 is
    reported identically to one where nothing was retrieved at all. Those are
    different situations for a reviewer, and CG-16a's atoms at 0.3771 against a
    0.40 floor are the second kind reported as the first.
    """
    scored = {r["passage_id"]: r["score"] for r in retrieval}
    entailed = {e["passage_id"] for e in entailment}
    admitted, removals = [], []
    for pid, score in scored.items():
        if pid in entailed or score >= floor:
            admitted.append(pid)
            continue
        removals.append(
            Removal(
                passage_id=pid,
                stage="1-admit",
                predicate="retrieval_floor",
                reason="near_miss" if score >= floor - NEAR_MISS_BAND else "below_floor",
                detail={"score": round(score, 4), "floor": floor},
            )
        )
    return admitted, removals


# ---------------------------------------------------------------------------
# Stage 2 — qualify. Per-passage, per-role (X1: 6 v1 gates).
# ---------------------------------------------------------------------------


def qualify_union(
    frame: ClaimFrame, members: list[PassageEvidence], union_id: str
) -> tuple[frozenset[Role], list[Removal]]:
    """A union may play a role only if **every** member may play it.

    Conservative on purpose, and it is the answer to the hazard named when R2
    was first proposed: A7 over a two-site union is exactly the shape that
    produced D14 and D16. If one member is out of scope, the union is out of
    scope. A union that could refute on the strength of a passage not licensed
    to refute would launder ineligibility through concatenation.

    **A union may support a universal claim, and may not refute one.** Refuting
    a universal needs a counterexample the source actually affirms. Composing two
    passages into one requires reasoning about what the source *omits*, which is
    the same closed-world step A6 refuses for absence claims (D11): silence in an
    excerpt is not refutation. CG-18 is the case, and it is not a one-off:
    a source assigning a predicate to a proper subset, nowhere excluding the
    remainder, reads to the entailer as a refutation of *every*.
    """
    roles = frozenset.intersection(*(m.eligible_for for m in members)) if members else frozenset()
    removals = []
    if frame.universal and "refute" in roles:
        roles = roles - {"refute"}
        removals.append(
            Removal(
                passage_id=union_id,
                stage="2-qualify",
                predicate="Q4_union_universal",
                reason=(
                    "a union may not refute a universal claim: a counterexample "
                    "must be affirmed by the source, not composed from passages"
                ),
                detail={"members": [m.passage_id for m in members]},
            )
        )
    removals += [
        Removal(
            passage_id=union_id,
            stage="2-qualify",
            predicate="Q3_union_inherits",
            reason=f"member {m.passage_id} may not {role}, so the union may not either",
            detail={"member": m.passage_id, "member_roles": sorted(m.eligible_for)},
        )
        for m in members
        for role in ("support", "refute")
        if role not in m.eligible_for
    ]
    return roles, removals


@dataclass(frozen=True)
class QualifyContext:
    """Everything a stage-2 predicate may read. Nothing else is in scope."""

    frame: ClaimFrame
    passage_id: str
    trust_level: str | None
    passage_scope: frozenset[str] | None
    #: This passage's reading of the *negated* claim, when the caller supplied
    #: one. ``None`` means the probe was not run, which is recorded, not assumed.
    negated_reading: dict[str, Any] | None
    claim_reading: dict[str, Any]
    passage_text: str | None = None


#: What a predicate returns: roles it removes, why, and any detail worth a trace.
PredicateResult = tuple[frozenset[Role], str | None, dict[str, Any]]


def _q1_provenance(ctx: QualifyContext) -> PredicateResult:
    """Decision H / D1. A non-primary source may not decide an adverse degree.

    Policy, not accuracy. If deleting it raised agreement it would still stay.
    An absent trust level is a directly-constructed passage and is eligible, so
    the predicate never fires outside the apparatus intake path.
    """
    trust = ctx.trust_level
    if trust is None or trust == "primary":
        return frozenset(), None, {}
    return (
        frozenset({"refute"}),
        "non-primary source may not decide an adverse degree",
        {"trust_level": trust},
    )


def _q2_scope(ctx: QualifyContext) -> PredicateResult:
    """A contradiction whose site is disjoint from the claim's may not decide it.

    Universal claims are exempt: a universal's scope subsumes any instance, so
    disjointness cannot be concluded. Found while gating D14, never registered.

    When passage text is unavailable the predicate reports **not evaluated**
    rather than passing. A check that did not run and a check that passed must
    not look the same downstream; that confusion is what D17 is.
    """
    if ctx.passage_scope is None:
        return frozenset(), "not evaluated: passage text unavailable", {"skipped": True}
    claim_scope = ctx.frame.scope_anchors
    if not claim_scope or not ctx.passage_scope or ctx.frame.universal:
        return frozenset(), None, {}
    if claim_scope & ctx.passage_scope:
        return frozenset(), None, {}
    return (
        frozenset({"refute"}),
        "passage scope is disjoint from the claim's",
        {"claim_scope": sorted(claim_scope), "passage_scope": sorted(ctx.passage_scope)},
    )


def _q3_negation_consistency(ctx: QualifyContext) -> PredicateResult:
    """Check a passage's reading of the claim against its reading of the negation.

    The asymmetry between proving and refuting is why the second forward pass is
    worth its cost: one passage can refute a claim outright, while supporting one
    is a weaker and more easily faked relation. The negated reading therefore
    carries information the positive reading does not.
    """
    neg = ctx.negated_reading
    if neg is None:
        return frozenset(), "not evaluated: no negated-claim reading supplied", {"skipped": True}

    label = ctx.claim_reading.get("label")
    score = ctx.claim_reading.get("score", 0.0)
    neg_entails = neg.get("label") == "entail" and neg.get("score", 0.0) >= SUPPORTED_THRESHOLD
    reading = f"claim {label} {score:.3f} / negation {neg.get('label')} {neg.get('score', 0.0):.3f}"

    if label == "entail" and score >= SUPPORTED_THRESHOLD and neg_entails:
        return (
            frozenset({"support", "refute"}),
            "passage entails the claim and its negation, so it establishes neither",
            {"reading": reading},
        )
    if label == "contradict" and score >= CONTRADICTED_THRESHOLD and not neg_entails:
        veto = neg.get("score", 0.0)
        if veto >= score:
            return (
                frozenset({"refute"}),
                "passage contradicts the claim but does not entail its negation, "
                "and the missing mirror is read at least as confidently as the "
                "contradiction, so the refutation is not carried by its own reading",
                {"reading": reading, "veto": round(veto, 3), "target": round(score, 3)},
            )
        return (
            frozenset(),
            "negation probe is uninformative: the missing mirror is read less "
            "confidently than the contradiction it would veto",
            {"reading": reading, "veto": round(veto, 3), "target": round(score, 3)},
        )
    return frozenset(), None, {}


def _q4_interval_containment(ctx: QualifyContext) -> PredicateResult:
    """Record the interval operator's reading of a numeric bound. **Advisory.**

    The operator compares the claim's asserted bound against a bound found in the
    passage, and its assessment is written to the trace. It removes no role.

    That is deliberate, and it is the difference between an arithmetic operator
    and an arithmetic operator you may decide on. ``interval_algebra`` has no
    *measurand binding*: it finds bounds in a passage but cannot tell whether a
    bound it found is a bound on the thing the claim is about. The first version
    of this predicate dropped ``refute`` on ``satisfied``, which on

        claim    "Product storage must not exceed 25 °C."
        passage  "Ambient lab temperature must not exceed 22 °C.
                  The product excursion reached 40 °C."

    stripped a genuinely refuting passage of its standing to refute, on the
    strength of a bound belonging to a different measurand. A false *supported*
    is the worst verdict this system can produce, and an operator that can be
    pointed at the wrong sentence must not be able to produce one.

    The operator now abstains (``ambiguous``) when a side carries more than one
    bound on the claim's dimension, which closes that specific case. It does not
    close the general one: a passage with exactly one temperature bound that is
    still not the claim's temperature reads as unambiguous. Binding a bound to
    its measurand is the open work; until it exists the assessment informs a
    reviewer and does not move a verdict.

    To let this decide, a caller must be able to establish that claim and passage
    bounds share a measurand. At that point the ``satisfied`` / ``violated``
    branches become role drops and the D12 note in :func:`resolve` comes off.
    """
    if not ctx.frame.quantities or ctx.passage_text is None:
        return frozenset(), None, {}

    assessment = evaluate_interval_containment(ctx.frame.text, ctx.passage_text)
    if assessment.status in ("inconclusive", "incomparable") and assessment.claim_interval is None:
        # Nothing quantitative to say about this pair; keep the trace quiet.
        return frozenset(), None, {}

    return (
        frozenset(),
        f"interval operator reads this passage as {assessment.status}: {assessment.reason}",
        {
            "advisory": True,
            "status": assessment.status,
            "claim_interval": assessment.claim_interval,
            "evidence_interval": assessment.evidence_interval,
            "verdict_impact_if_deciding": assessment.verdict_impact,
        },
    )


#: Stage 2, as data. Adding an eligibility rule is adding a row, not a branch.
ELIGIBILITY_PREDICATES: tuple[tuple[str, Any], ...] = (
    ("Q1_provenance", _q1_provenance),
    ("Q2_scope", _q2_scope),
    ("Q3_negation_consistency", _q3_negation_consistency),
    ("Q4_interval_containment", _q4_interval_containment),
)


def qualify(ctx: QualifyContext) -> tuple[frozenset[Role], list[Removal]]:
    """Fold every stage-2 predicate over one passage. Total, no short circuit.

    Every predicate runs on every passage even after one has disqualified it,
    because a reviewer reading the trace should see every reason, not the first.

    **A predicate that raises marks the passage and removes nothing.** This is
    the property the module header claims and, until it was written here, did not
    have: ``_q4_interval_containment`` reaches arithmetic that could raise on
    ordinary input, and the exception left stage 2 through ``run_v2`` as an
    unhandled error. A predicate that could not run must not be
    indistinguishable from one that passed, and it must certainly not remove a
    role — so the failure is recorded, marked ``skipped`` so it does not read as
    ineligibility, and the fold continues.
    """
    roles: frozenset[Role] = frozenset({"support", "refute"})
    removals: list[Removal] = []
    for name, predicate in ELIGIBILITY_PREDICATES:
        try:
            drop, reason, detail = predicate(ctx)
        except Exception as exc:  # a stage is total; see the docstring above
            drop, reason, detail = (
                frozenset(),
                f"not evaluated: {name} raised {type(exc).__name__}",
                {"skipped": True, "error": f"{type(exc).__name__}: {exc}"},
            )
        roles -= drop
        if reason is not None:
            removals.append(
                Removal(
                    passage_id=ctx.passage_id,
                    stage="2-qualify",
                    predicate=name,
                    reason=reason,
                    detail=detail,
                )
            )
    return roles, removals


# ---------------------------------------------------------------------------
# Stage 4 — resolve. Set-level, one function, dispatch on mode.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ResolveContext:
    """Everything a stage-4 rule may read."""

    frame: ClaimFrame
    evidence: list[PassageEvidence]
    source_boundary: str | None
    nothing_admitted: bool
    claimed_material_is_a_named_gap: bool

    def eligible(self, role: Role, label: str, threshold: float) -> list[PassageEvidence]:
        return [
            e for e in self.evidence if e.may(role) and e.label == label and e.score >= threshold
        ]

    @property
    def refuting(self) -> list[PassageEvidence]:
        return self.eligible("refute", "contradict", CONTRADICTED_THRESHOLD)

    @property
    def supporting(self) -> list[PassageEvidence]:
        return self.eligible("support", "entail", SUPPORTED_THRESHOLD)


#: A stage-4 outcome: degree, null reason, citations, note.
Outcome = tuple[Degree, "NullReason | None", tuple[str, ...], str]


def _cite(pool: list[PassageEvidence]) -> tuple[str, ...]:
    """Cite the narrowest evidence that decides.

    If a single passage settles it, cite the single. A union verdict names two
    passages and a reviewer should be sent to the narrowest evidence that
    actually decides.
    """
    singles = [e for e in pool if not e.is_union]
    return tuple(e.passage_id for e in (singles or pool))


def _r_named_gap(c: ResolveContext) -> Outcome | None:
    """A named-gap boundary refutes a coverage claim only when the caller also
    says the claimed material *is* one of the named gaps.

    The boundary alone does not. CG-21 and CG-22 share it and differ in gold, and
    the flag is the whole discriminator.
    """
    if c.frame.mode != "coverage":
        return None
    if c.source_boundary != "named_missing_material" or not c.claimed_material_is_a_named_gap:
        return None
    return (
        "contradicted",
        None,
        (),
        "the caller declared this material among the source's named gaps",
    )


def _r_coverage_exhaustive(c: ResolveContext) -> Outcome | None:
    """Silence in a source declared complete is a fact about the source.

    Empty retrieval is not a failure here. It **is** the finding, which is why
    this rule sits ahead of the no-evidence rule rather than behind a stage-1
    early return.
    """
    if c.frame.mode != "coverage" or c.source_boundary != "exhaustive":
        return None
    complement = c.eligible("support", "entail", SUPPORTED_THRESHOLD)
    if complement:
        return (
            "contradicted",
            None,
            _cite(complement),
            "a passage entails the positive complement of this coverage claim",
        )
    return "supported", None, (), "silence in a complete source settles it"


def _r_coverage_bounded(c: ResolveContext) -> Outcome | None:
    """Silence in an excerpt is not refutation (D11).

    A passage on an adjacent topic neither confirms nor refutes a claim about
    what a document omits, so this route is never adverse.
    """
    if c.frame.mode != "coverage":
        return None
    return (
        "not_checkable",
        "not_resolvable",
        (),
        "coverage claim over a non-exhaustive source: silence is not refutation",
    )


def _r_no_evidence(c: ResolveContext) -> Outcome | None:
    """Stage 1 admitted nothing, and this claim needed passages."""
    if not c.nothing_admitted:
        return None
    return "not_checkable", "no_evidence", (), "no passage cleared the retrieval floor"


def _r_conflicting(c: ResolveContext) -> Outcome | None:
    """Eligible evidence reads both ways, so neither may settle it alone.

    v1 aggregates to a maximum and picks one, which is D9's shape.
    """
    if not (c.refuting and c.supporting):
        return None
    return (
        "not_checkable",
        "not_resolvable",
        tuple(e.passage_id for e in c.refuting + c.supporting),
        "eligible evidence reads both ways",
    )


def _r_refuted(c: ResolveContext) -> Outcome | None:
    if not c.refuting:
        return None
    return "contradicted", None, _cite(c.refuting), "eligible evidence refutes the claim"


def _r_supported(c: ResolveContext) -> Outcome | None:
    if not c.supporting:
        return None
    return "supported", None, _cite(c.supporting), "eligible evidence establishes the claim"


def _r_no_signal(c: ResolveContext) -> Outcome:
    """Terminal. Evidence was admitted and eligible, and nothing read above
    threshold in either direction."""
    return "not_checkable", "no_signal", (), "eligible evidence, no reading above threshold"


#: Stage 4, as data. First rule whose guard fires decides. Order **is**
#: significant here, unlike stage 2, and that is why the table is explicit: the
#: precedence is a list you can read and reorder, not control flow to trace.
RESOLUTION_RULES: tuple[tuple[str, Any], ...] = (
    ("R1_named_gap", _r_named_gap),
    ("R2_coverage_exhaustive", _r_coverage_exhaustive),
    ("R3_coverage_bounded", _r_coverage_bounded),
    ("R4_no_evidence", _r_no_evidence),
    ("R5_conflicting", _r_conflicting),
    ("R6_refuted", _r_refuted),
    ("R7_supported", _r_supported),
)


def resolve(
    frame: ClaimFrame,
    evidence: list[PassageEvidence],
    *,
    source_boundary: str | None,
    nothing_admitted: bool = False,
    claimed_material_is_a_named_gap: bool = False,
) -> tuple[Degree, NullReason | None, tuple[str, ...], tuple[str, ...]]:
    """Fold the resolution table. The first rule that fires decides.

    ``A6`` is not a gate here: a coverage claim over a source declared complete
    is settled by that completeness, which is a *resolution mode*. X1 measured
    all three v1 ``A6`` rules as claim-level or set-level, so none of them
    belonged in a per-passage stage.

    There is no quantitative mode. That was a third route in the first draft and
    construction gold rejected it in one run: D12 is an operator gap and no
    resolution rule closes it, so the quantity is recorded and not acted on.

    ``Q4`` now does the arithmetic D12 names, and still does not close it. Its
    assessment is advisory (see :func:`_q4_interval_containment`) because the
    operator cannot bind a bound to a measurand, so the note below stands: stage 4
    decides on the entailer's reading and asks the reviewer to confirm the
    quantity. When Q4 can decide, this note comes off with it.
    """
    ctx = ResolveContext(
        frame=frame,
        evidence=evidence,
        source_boundary=source_boundary,
        nothing_admitted=nothing_admitted,
        claimed_material_is_a_named_gap=claimed_material_is_a_named_gap,
    )
    notes: list[str] = []

    # D12 is an operator gap the decision layer cannot close. The first draft
    # tried, by withholding every adverse verdict on a claim carrying a quantity,
    # and it cost four true contradictions (CG-03, CG-12a, CG-12b, CG-24) to
    # avoid one false one (CG-20). The two cannot be separated without doing the
    # arithmetic:
    #   CG-20   passage bound (>= 12 months) SATISFIES claim bound (>= 6) -> entailer wrong
    #   CG-12b  passage bound (<= 1 day)     VIOLATES  claim bound (<= 5) -> entailer right
    # So the quantity is recorded, and the verdict stands.
    if frame.quantities:
        notes.append(
            "verdict depends on a quantity the entailer cannot compare (D12); "
            "confirm the recorded value against the claimed one"
        )

    for name, rule in RESOLUTION_RULES:
        # As in stage 2: a rule that raises is recorded and skipped rather than
        # redirecting control. Precedence is preserved — the next rule in the
        # table gets its turn, exactly as if this one had declined.
        try:
            outcome = rule(ctx)
        except Exception as exc:  # a stage is total; see the module header
            notes.append(f"{name}: not evaluated, raised {type(exc).__name__}: {exc}")
            continue
        if outcome is not None:
            degree, null_reason, citations, note = outcome
            notes.append(f"{name}: {note}")
            return degree, null_reason, citations, tuple(notes)

    degree, null_reason, citations, note = _r_no_signal(ctx)
    notes.append(f"R8_no_signal: {note}")
    return degree, null_reason, citations, tuple(notes)


# ---------------------------------------------------------------------------
# The pipeline. Five stages, each total.
#
# Two early returns exist and both are terminal rather than skips: an
# inadmissible claim (stage 0) and a held set with no eligible passage (stage 2).
# Each names the stage it stopped at in `stage_reached` and its own null reason.
# Nothing downstream of either could change the outcome — that is what makes them
# terminal and not the family of jump this pipeline is written against.
# ---------------------------------------------------------------------------


def run_v2(
    *,
    claim_text: str,
    features: dict[str, Any],
    retrieval: list[dict[str, Any]],
    entailment: list[dict[str, Any]],
    source_boundary: str | None = None,
    claimed_material_is_a_named_gap: bool = False,
    declared_mode: Mode | None = None,
    claim_scope: frozenset[str] = frozenset(),
    passage_scope: dict[str, frozenset[str]] | None = None,
    trust_levels: dict[str, str] | None = None,
    source_ids: dict[str, str] | None = None,
    passage_texts: dict[str, str] | None = None,
    unions: list[dict[str, Any]] | None = None,
    negated_entailment: list[dict[str, Any]] | None = None,
) -> V2Verdict:
    """Run the v2 decision layer over one claim's stage-1-to-3 evidence.

    ``negated_entailment`` is an optional list of per-passage readings of the
    *negated* claim, same shape as ``entailment``. The caller computes it,
    because forming and scoring a premise is inference-stage work. Absent, the
    consistency predicate records itself as not evaluated rather than passing.

    ``unions`` is an optional list of readings over concatenated passages, each
    ``{"members": [...], "label", "score", "p_entail", "p_contradict"}``. The
    caller computes them, because forming a premise is an inference-stage
    decision and not the decision layer's business. Absent, v2 behaves exactly
    as before, which keeps the union effect measurable in isolation.
    """
    removals: list[Removal] = []

    # Stage 0
    frame = build_claim_frame(
        claim_text, features, declared_mode=declared_mode, scope_anchors=claim_scope
    )
    if not frame.admissible:
        return V2Verdict(
            degree="not_checkable",
            null_reason="out_of_form",
            mode=frame.mode,
            mode_was_guessed=frame.mode_was_guessed,
            deciding_passages=(),
            removals=(),
            stage_reached="0-frame",
            notes=(f"sentence_type={frame.sentence_type}, tokens={frame.token_count}",),
        )

    # Stage 1. Emptiness is recorded and carried forward rather than returned:
    # whether it is fatal is stage 4's call, and it is not fatal for a coverage
    # claim over a source declared complete.
    admitted, admit_removals = admit(retrieval, entailment)
    removals.extend(admit_removals)
    nothing_admitted = not admitted
    stage_notes: tuple[str, ...]
    if nothing_admitted and admit_removals:
        near = sum(1 for r in admit_removals if r.reason == "near_miss")
        stage_notes = (f"{len(admit_removals)} passages dropped, {near} within the near-miss band",)
    else:
        stage_notes = ()

    # Stage 2 and 3 — qualify every admitted passage, carry the full reading
    by_id = {e["passage_id"]: e for e in entailment}
    negated_by_id = {e["passage_id"]: e for e in (negated_entailment or [])}
    scores = {r["passage_id"]: r["score"] for r in retrieval}
    evidence: list[PassageEvidence] = []
    for pid in admitted:
        e = by_id.get(pid)
        if e is None:
            removals.append(
                Removal(
                    passage_id=pid,
                    stage="3-score",
                    predicate="entailment_present",
                    reason="admitted but never entailed",
                )
            )
            continue
        roles, why = qualify(
            QualifyContext(
                frame=frame,
                passage_id=pid,
                trust_level=(trust_levels or {}).get(pid),
                passage_scope=(passage_scope or {}).get(pid),
                negated_reading=negated_by_id.get(pid),
                claim_reading=e,
                passage_text=(passage_texts or {}).get(pid),
            )
        )
        removals.extend(why)
        evidence.append(
            PassageEvidence(
                passage_id=pid,
                retrieval_score=scores.get(pid, 0.0),
                label=e["label"],
                score=e["score"],
                p_entail=e.get("p_entail"),
                p_contradict=e.get("p_contradict"),
                eligible_for=roles,
                # A record is ineligibility only if it removed something. A
                # predicate that could not run (`skipped`) or that only reports
                # (`advisory`) is in the trace but is not a reason this passage
                # may not decide.
                ineligibility=tuple(
                    w for w in why if not w.detail.get("skipped") and not w.detail.get("advisory")
                ),
                trust_level=(trust_levels or {}).get(pid),
                source_id=(source_ids or {}).get(pid),
            )
        )

    # Unions, if the caller supplied readings for them. Eligibility is inherited
    # from members rather than recomputed, so a union can never be more eligible
    # than the least eligible passage in it.
    by_pid = {e.passage_id: e for e in evidence}
    for u in unions or []:
        members = [by_pid[m] for m in u["members"] if m in by_pid]
        if len(members) < 2:
            continue
        union_id = "+".join(m.passage_id for m in members)
        roles, why = qualify_union(frame, members, union_id)
        removals.extend(why)
        evidence.append(
            PassageEvidence(
                passage_id=union_id,
                retrieval_score=max(m.retrieval_score for m in members),
                label=u["label"],
                score=u["score"],
                p_entail=u.get("p_entail"),
                p_contradict=u.get("p_contradict"),
                eligible_for=roles,
                members=tuple(m.passage_id for m in members),
            )
        )

    if evidence and not any(e.eligible_for for e in evidence):
        return V2Verdict(
            degree="not_checkable",
            null_reason="all_ineligible",
            mode=frame.mode,
            mode_was_guessed=frame.mode_was_guessed,
            deciding_passages=(),
            removals=tuple(removals),
            stage_reached="2-qualify",
            notes=(f"{len(evidence)} passages held, none eligible for any role",),
        )

    # Stage 4
    degree, null_reason, deciding, notes = resolve(
        frame,
        evidence,
        source_boundary=source_boundary,
        nothing_admitted=nothing_admitted,
        claimed_material_is_a_named_gap=claimed_material_is_a_named_gap,
    )
    return V2Verdict(
        degree=degree,
        null_reason=null_reason,
        mode=frame.mode,
        mode_was_guessed=frame.mode_was_guessed,
        deciding_passages=deciding,
        removals=tuple(removals),
        stage_reached="4-resolve",
        notes=stage_notes + notes,
    )
