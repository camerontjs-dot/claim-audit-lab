"""Build a by-construction gold corpus in regulatory prose.

The problem this solves
-----------------------
PILOT-001 is human-coded, and its weakest region is *absence* claims — "the
guidance does not prescribe X". Measured on 2026-08-19, the gold's verdict on
those tracked whether the bundle happened to be starved rather than any stated
rule: all 8 absence claims in starved bundles were coded ``supported`` and all 5
in full bundles were coded otherwise, Fisher exact p = 0.0008. That single
ambiguity accounts for 7 of 34 CAL-gold disagreements.

It is not a rater-quality problem. It is an undeclared parameter: whether the
bundle *is* the source. Declare it and the answer stops being a judgment call.

What this builds
----------------
Cases whose verdict is *derived from how the case was constructed*, never coded
by a rater — the method already used by ``outputs/simple-logic-gold/``, applied
to regulatory prose instead of brass keys in drawers.

The centerpiece is the **variant group**: the same claim and the same supporting
passages, emitted two or three times, differing in exactly one declared
parameter. A group states its own expectation:

* ``separates`` — the parameter must change the answer. The boundary triples do
  this across all three values: ``exhaustive`` makes an absence decidable
  (``supported``), ``bounded`` leaves it open (``not_checkable``), and
  ``named_missing_material`` whose named gaps include the claimed material
  settles it the other way (``contradicted``). One claim, one passage set,
  three verdicts, no rater.
* ``invariant`` — the parameter must *not* change the answer. Irrelevant
  distractor passages are the obvious case, and so is the boundary on a partial
  conjunction: bundle completeness makes claims *about the source* decidable, it
  does not make claims *about the world* decidable.

Failing an ``invariant`` group is as much a defect as failing a ``separates``
one, and neither can be argued with, because no human assigned the labels.

``bounded`` is the majority here by design: real evidence bundles are excerpts,
so the excerpt case is the operating condition and ``exhaustive`` is the control.

Boundaries
----------
DEV construction. Not validation, not gate evidence, not an accuracy claim. The
corpus states what *follows from its own stipulations*; it says nothing about
FDA guidance, and the prose is written for this file rather than quoted from any
real document.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Literal

SourceBoundary = Literal["exhaustive", "bounded", "named_missing_material"]
Relation = Literal[
    "restates",
    "contradicts",
    "absent_from",
    "instantiates_bound",
    "conjunction",
    "partial_conjunction",
    "overgeneralizes",
    "weakens",
    "chains",
]
VariantAxis = Literal["source_boundary", "distractors"]
VariantExpectation = Literal["separates", "invariant"]

OUT = Path(__file__).resolve().parents[2] / "outputs" / "2026-08-19-construction-gold"


# --------------------------------------------------------------------------
# Stipulated sources. These are the whole world for each case; nothing outside
# them is true or false, which is what makes the verdicts derivable.
#
# The first three are FROZEN at their v0.1 text. Changing a byte would silently
# rewrite the thirteen v0.1 cases, so `validate` re-checks every v0.1 claim and
# passage set against a recorded snapshot.
# --------------------------------------------------------------------------

SOURCES: dict[str, dict[str, Any]] = {
    "SRC-EQ-QUAL": {
        "title": "Equipment Qualification and Requalification",
        "passages": [
            (
                "p1",
                "Equipment used in commercial manufacture shall be qualified prior to "
                "first production use. Qualification comprises installation, operational "
                "and performance stages, each with documented acceptance criteria.",
            ),
            (
                "p2",
                "Requalification shall be performed following any change that affects "
                "the qualified state, including relocation, major repair, or modification "
                "of a critical component.",
            ),
            (
                "p3",
                "Where a periodic requalification interval is established by the site, "
                "the interval shall be justified in the validation master plan.",
            ),
        ],
        # Facts the source does NOT state. Under `exhaustive` these are decidably
        # absent; under `bounded` they are simply unknown.
        "silent_on": [
            {"topic": "a fixed numeric requalification interval", "absent_term": "months"},
            {"topic": "requalification of laboratory instruments", "absent_term": "laboratory"},
        ],
    },
    "SRC-STAB": {
        "title": "Stability Testing and Shelf-Life Assignment",
        "passages": [
            (
                "p1",
                "Stability studies shall be conducted on at least three primary batches "
                "of the drug product in the proposed container closure system.",
            ),
            (
                "p2",
                "Long-term testing shall cover a minimum of 12 months at the time of "
                "submission, with testing frequency of every three months in the first "
                "year and every six months in the second year.",
            ),
            (
                "p3",
                "A shelf-life exceeding 24 months shall not be assigned on the basis of "
                "accelerated data alone.",
            ),
        ],
        "silent_on": [
            {"topic": "storage of retention samples", "absent_term": "retention"},
            {"topic": "photostability chamber calibration", "absent_term": "photostability"},
        ],
    },
    "SRC-DEV": {
        "title": "Deviation Handling and Quality Holds",
        "passages": [
            (
                "p1",
                "Any excursion from a validated process parameter shall be recorded as a "
                "deviation within one business day of detection.",
            ),
            (
                "p2",
                "A deviation classified as critical shall trigger a Quality Hold on the "
                "affected batch until the investigation is closed.",
            ),
            (
                "p3",
                "Cold-chain product held above 8 degrees Celsius for more than 6 hours "
                "shall be classified as a critical deviation.",
            ),
        ],
        "silent_on": [
            {"topic": "deviations detected after batch release", "absent_term": "release"},
        ],
    },
    # --- added in v0.2 ----------------------------------------------------
    # Carries the two shapes v0.1 could not express: a two-hop chain whose hops
    # are separately stipulated, and an explicit carve-out that makes a
    # universal claim decidably false rather than merely unsupported.
    "SRC-CC": {
        "title": "Change Control for Manufacturing Equipment",
        "passages": [
            (
                "p1",
                "Relocation of manufacturing equipment between production suites shall "
                "be processed as a major change.",
            ),
            (
                "p2",
                "A change classified as major shall require requalification of the "
                "affected equipment prior to resumption of production.",
            ),
            (
                "p3",
                "Changes classified as minor shall be documented and closed without "
                "requalification of the affected equipment.",
            ),
            (
                "p4",
                "The change control record shall identify each system affected by the "
                "change and the approver accountable for it.",
            ),
        ],
        "silent_on": [
            {
                "topic": "changes implemented under emergency authorization",
                "absent_term": "emergency",
            },
        ],
    },
    # Two near-identical obligations that differ only in the site they govern.
    # This is how a distractor gets built that CLEARS the retrieval floor: a
    # topical distractor is irrelevant because it shares no vocabulary, which is
    # exactly why retrieval drops it before any rule runs. A scope-mismatched
    # distractor shares almost all of it, so it reaches the entailer and the rule
    # layer has to be the thing that sets it aside.
    "SRC-SCOPE": {
        "title": "Site-Specific Deviation Recording Timelines",
        "passages": [
            (
                "p1",
                "At the Building 4 manufacturing site, an excursion from a validated "
                "process parameter shall be recorded as a deviation within one business "
                "day of detection.",
            ),
            (
                "p2",
                "At the contract testing laboratory, an excursion from a validated "
                "process parameter shall be recorded as a deviation within five business "
                "days of detection.",
            ),
        ],
        "silent_on": [
            {"topic": "recording timelines at packaging sites", "absent_term": "packaging"},
        ],
    },
}


def _passage_text(source_id: str, passage_id: str) -> str:
    for pid, text in SOURCES[source_id]["passages"]:
        if pid == passage_id:
            return str(text)
    raise KeyError(f"{source_id}#{passage_id} is not stipulated")


def _ref(case: dict[str, Any], use: Any) -> tuple[str, str]:
    """Normalize a passage reference to ``(source_id, passage_id)``.

    A bare string means the case's own source, which is what every v0.1 case
    uses. A pair means an explicit source, which is how multi-document bundles
    and distractors are written.
    """
    if isinstance(use, str):
        return (case["source_id"], use)
    src, pid = use
    return (src, pid)


# --------------------------------------------------------------------------
# Case construction. Each entry declares the relation it was BUILT to have;
# `derive_verdict` turns that plus the boundary into the expected verdict.
# The gold is the output of that function, never a hand-written label.
# --------------------------------------------------------------------------


def derive_verdict(
    relation: Relation,
    boundary: SourceBoundary,
    *,
    claimed_material_is_a_named_gap: bool = False,
) -> tuple[str, str]:
    """Return ``(expected_verdict, derivation)`` from the construction alone.

    This is the whole point of the corpus: the answer is a function of how the
    case was built, so two people running it get the same gold, and the gold can
    be regenerated rather than trusted.

    ``claimed_material_is_a_named_gap`` only reads under
    ``named_missing_material``, where the bundle is an excerpt that names what it
    left out. Material among the named gaps is stipulated to exist in the source,
    which makes a claim of absence decidably false rather than merely open.
    """
    if relation == "restates":
        return (
            "supported",
            "the claim restates a stipulated passage, so support holds under any boundary",
        )
    if relation == "contradicts":
        return (
            "contradicted",
            "the claim asserts the negation of a stipulated passage, so it is refuted "
            "under any boundary",
        )
    if relation == "instantiates_bound":
        return (
            "supported",
            "a stipulated threshold rule applies to the claim's value, and the claim "
            "states the consequence the rule assigns",
        )
    if relation == "conjunction":
        return (
            "supported",
            "every conjunct restates a stipulated passage, so the conjunction holds",
        )
    if relation == "chains":
        return (
            "supported",
            "two stipulated passages compose — one classifies the instance, the other "
            "assigns the consequence to that class — so the claim follows under any boundary",
        )
    if relation == "weakens":
        return (
            "supported",
            "the claim is a strictly weaker consequence of a stipulated passage, so the "
            "passage entails it under any boundary",
        )
    if relation == "overgeneralizes":
        return (
            "not_checkable",
            "the source assigns the predicate to a proper subset and nowhere excludes "
            "the remainder, so a universal claim is neither carried nor refuted by it",
        )
    if relation == "partial_conjunction":
        return (
            "not_checkable",
            "one conjunct restates a stipulated passage and the other is absent from the "
            "bundle; absence of an object-level assertion is not evidence against it, so "
            "the conjunction is unsettled under every boundary — a complete bundle makes "
            "claims about the source decidable, not claims about the world",
        )
    if relation == "absent_from":
        if boundary == "exhaustive":
            return (
                "supported",
                "the bundle is stipulated to be the complete source and does not state "
                "the material, so the absence is a fact about the source",
            )
        if boundary == "named_missing_material":
            if claimed_material_is_a_named_gap:
                return (
                    "contradicted",
                    "the bundle is an excerpt whose omissions are named and the claimed "
                    "material is among them, so the source is stipulated to address it "
                    "and the claim of absence is false",
                )
            return (
                "not_checkable",
                "the bundle is an excerpt that names its gaps; the claimed material is "
                "not among the named gaps, so its absence from the source is undetermined",
            )
        return (
            "not_checkable",
            "the bundle is stipulated to be an excerpt, so absence from the bundle is "
            "not absence from the source and the claim cannot be settled here",
        )
    raise ValueError(f"unhandled relation: {relation}")


CASES: list[dict[str, Any]] = [
    # ======================================================================
    # v0.1 cases. Frozen: claim text, passage set, relation and boundary are
    # snapshotted in V0_1_SNAPSHOT and re-checked on every build.
    # ======================================================================
    # --- direct support: boundary-independent controls -------------------
    {
        "case_id": "CG-01",
        "source_id": "SRC-EQ-QUAL",
        "uses": ["p1"],
        "relation": "restates",
        "boundary": "bounded",
        "claim": (
            "Equipment used in commercial manufacture must be qualified before it is "
            "first used in production."
        ),
    },
    {
        "case_id": "CG-02",
        "source_id": "SRC-STAB",
        "uses": ["p1"],
        "relation": "restates",
        "boundary": "bounded",
        "claim": (
            "Stability studies must be run on a minimum of three primary batches of the "
            "drug product."
        ),
    },
    # --- direct refutation ----------------------------------------------
    {
        "case_id": "CG-03",
        "source_id": "SRC-STAB",
        "uses": ["p3"],
        "relation": "contradicts",
        "boundary": "bounded",
        "claim": (
            "A shelf-life of 36 months may be assigned on the basis of accelerated data alone."
        ),
    },
    {
        "case_id": "CG-04",
        "source_id": "SRC-EQ-QUAL",
        "uses": ["p2"],
        "relation": "contradicts",
        "boundary": "bounded",
        "claim": ("Relocation of qualified equipment does not require requalification."),
    },
    # --- numeric bound instantiation (the D1 shape) ----------------------
    {
        "case_id": "CG-05",
        "source_id": "SRC-DEV",
        "uses": ["p3", "p2"],
        "relation": "instantiates_bound",
        "boundary": "bounded",
        "claim": (
            "A cold-chain batch held at 10 degrees Celsius for 7 hours must be placed on "
            "Quality Hold."
        ),
    },
    # --- conjunction (the all_of shape) ----------------------------------
    {
        "case_id": "CG-06",
        "source_id": "SRC-STAB",
        "uses": ["p1", "p2"],
        "relation": "conjunction",
        "boundary": "bounded",
        "claim": (
            "Stability studies must cover at least three primary batches and long-term "
            "testing must span at least 12 months at submission."
        ),
    },
    # --- BOUNDARY VARIANTS: identical claim and passages, boundary differs ---
    {
        "case_id": "CG-07a",
        "variant_group": "VG-EQ-INTERVAL",
        "source_id": "SRC-EQ-QUAL",
        "uses": ["p1", "p2", "p3"],
        "relation": "absent_from",
        "boundary": "exhaustive",
        "claim": (
            "The guidance does not prescribe a fixed numeric requalification interval for "
            "equipment."
        ),
    },
    {
        "case_id": "CG-07b",
        "variant_group": "VG-EQ-INTERVAL",
        "source_id": "SRC-EQ-QUAL",
        "uses": ["p1", "p2", "p3"],
        "relation": "absent_from",
        "boundary": "bounded",
        "claim": (
            "The guidance does not prescribe a fixed numeric requalification interval for "
            "equipment."
        ),
    },
    {
        "case_id": "CG-08a",
        "variant_group": "VG-STAB-RETENTION",
        "source_id": "SRC-STAB",
        "uses": ["p1", "p2", "p3"],
        "relation": "absent_from",
        "boundary": "exhaustive",
        "claim": ("The guidance does not address storage conditions for retention samples."),
    },
    {
        "case_id": "CG-08b",
        "variant_group": "VG-STAB-RETENTION",
        "source_id": "SRC-STAB",
        "uses": ["p1", "p2", "p3"],
        "relation": "absent_from",
        "boundary": "bounded",
        "claim": ("The guidance does not address storage conditions for retention samples."),
    },
    {
        "case_id": "CG-09a",
        "variant_group": "VG-DEV-POSTRELEASE",
        "source_id": "SRC-DEV",
        "uses": ["p1", "p2", "p3"],
        "relation": "absent_from",
        "boundary": "exhaustive",
        "claim": ("The procedure does not cover deviations detected after batch release."),
    },
    {
        "case_id": "CG-09b",
        "variant_group": "VG-DEV-POSTRELEASE",
        "source_id": "SRC-DEV",
        "uses": ["p1", "p2", "p3"],
        "relation": "absent_from",
        "boundary": "bounded",
        "claim": ("The procedure does not cover deviations detected after batch release."),
    },
    # --- the third boundary value, as its own control --------------------
    {
        "case_id": "CG-10",
        "source_id": "SRC-EQ-QUAL",
        "uses": ["p1", "p2", "p3"],
        "relation": "absent_from",
        "boundary": "named_missing_material",
        "named_gaps": ["calibration of in-process weighing devices"],
        "claim": ("The guidance does not address requalification of laboratory instruments."),
    },
    # ======================================================================
    # v0.2 additions
    # ======================================================================
    # --- DISTRACTOR VARIANTS ---------------------------------------------
    # Same claim, same supporting passages, same boundary. One arm carries
    # topically unrelated passages from other sources. By construction the
    # distractors are irrelevant, so the gold is identical across the pair and
    # the group's expectation is `invariant`: if CAL's verdict moves, the move
    # is caused by evidence that cannot bear on the claim.
    {
        "case_id": "CG-11a",
        "variant_group": "VG-DIST-SUPPORT",
        "source_id": "SRC-DEV",
        "uses": ["p1"],
        "relation": "restates",
        "boundary": "bounded",
        "claim": (
            "An excursion from a validated process parameter must be recorded as a "
            "deviation within one business day of detection."
        ),
    },
    {
        "case_id": "CG-11b",
        "variant_group": "VG-DIST-SUPPORT",
        "source_id": "SRC-DEV",
        "uses": ["p1"],
        "distractors": [["SRC-STAB", "p3"], ["SRC-CC", "p4"]],
        "distractor_absent_terms": ["excursion", "deviation", "validated", "detection"],
        "relation": "restates",
        "boundary": "bounded",
        "claim": (
            "An excursion from a validated process parameter must be recorded as a "
            "deviation within one business day of detection."
        ),
    },
    {
        "case_id": "CG-12a",
        "variant_group": "VG-DIST-REFUTE",
        "source_id": "SRC-DEV",
        "uses": ["p1"],
        "relation": "contradicts",
        "boundary": "bounded",
        "claim": ("A deviation may be recorded up to five business days after it is detected."),
    },
    {
        "case_id": "CG-12b",
        "variant_group": "VG-DIST-REFUTE",
        "source_id": "SRC-DEV",
        "uses": ["p1"],
        "distractors": [["SRC-EQ-QUAL", "p3"], ["SRC-STAB", "p3"]],
        "distractor_absent_terms": ["deviation", "detected", "business"],
        "relation": "contradicts",
        "boundary": "bounded",
        "claim": ("A deviation may be recorded up to five business days after it is detected."),
    },
    {
        "case_id": "CG-13a",
        "variant_group": "VG-DIST-ABSENCE",
        "source_id": "SRC-EQ-QUAL",
        "uses": ["p1", "p2", "p3"],
        "relation": "absent_from",
        "boundary": "bounded",
        "claim": ("The guidance does not address requalification of laboratory instruments."),
    },
    {
        "case_id": "CG-13b",
        "variant_group": "VG-DIST-ABSENCE",
        "source_id": "SRC-EQ-QUAL",
        "uses": ["p1", "p2", "p3"],
        "distractors": [["SRC-STAB", "p1"], ["SRC-DEV", "p1"]],
        "distractor_absent_terms": ["laboratory", "instrument", "requalification"],
        "relation": "absent_from",
        "boundary": "bounded",
        "claim": ("The guidance does not address requalification of laboratory instruments."),
    },
    # --- MULTI-DOCUMENT BUNDLES ------------------------------------------
    {
        "case_id": "CG-14",
        "source_id": "SRC-STAB",
        "uses": [["SRC-STAB", "p1"], ["SRC-DEV", "p1"]],
        "relation": "conjunction",
        "boundary": "bounded",
        "claim": (
            "Stability studies must be conducted on at least three primary batches, and "
            "any excursion from a validated process parameter must be recorded as a "
            "deviation within one business day of detection."
        ),
        "construction_note": (
            "Each conjunct restates a passage from a different document. Neither document "
            "carries the claim alone."
        ),
    },
    {
        "case_id": "CG-15",
        "source_id": "SRC-CC",
        "uses": ["p1", "p2"],
        "relation": "chains",
        "boundary": "bounded",
        "claim": (
            "Relocating manufacturing equipment between production suites requires "
            "requalification of that equipment before production resumes."
        ),
        "construction_note": (
            "Two hops: p1 classifies relocation as a major change, p2 assigns "
            "requalification to major changes. Neither hop states the claim."
        ),
    },
    {
        "case_id": "CG-16a",
        "variant_group": "VG-MULTIDOC-ABSENCE",
        "source_id": "SRC-STAB",
        "uses": [
            ["SRC-STAB", "p1"],
            ["SRC-STAB", "p2"],
            ["SRC-STAB", "p3"],
            ["SRC-DEV", "p1"],
            ["SRC-DEV", "p2"],
            ["SRC-DEV", "p3"],
        ],
        "relation": "absent_from",
        "boundary": "exhaustive",
        "claim": (
            "Neither the stability testing requirements nor the deviation handling "
            "procedure addresses photostability chamber calibration."
        ),
    },
    {
        "case_id": "CG-16b",
        "variant_group": "VG-MULTIDOC-ABSENCE",
        "source_id": "SRC-STAB",
        "uses": [
            ["SRC-STAB", "p1"],
            ["SRC-STAB", "p2"],
            ["SRC-STAB", "p3"],
            ["SRC-DEV", "p1"],
            ["SRC-DEV", "p2"],
            ["SRC-DEV", "p3"],
        ],
        "relation": "absent_from",
        "boundary": "bounded",
        "claim": (
            "Neither the stability testing requirements nor the deviation handling "
            "procedure addresses photostability chamber calibration."
        ),
    },
    # --- PARTIAL SUPPORT: boundary must NOT move this --------------------
    # The invariant counterpart to the boundary triples. A complete bundle
    # settles claims about what the source says; it does not settle an
    # object-level assertion the source never makes.
    {
        "case_id": "CG-17a",
        "variant_group": "VG-PARTIAL",
        "variant_expectation": "invariant",
        "source_id": "SRC-STAB",
        "uses": ["p1", "p2", "p3"],
        "relation": "partial_conjunction",
        "boundary": "bounded",
        "absent_conjunct_term": "retention",
        "claim": (
            "Stability studies must cover at least three primary batches, and retention "
            "samples must be stored under the same conditions as the primary batches."
        ),
    },
    {
        "case_id": "CG-17b",
        "variant_group": "VG-PARTIAL",
        "variant_expectation": "invariant",
        "source_id": "SRC-STAB",
        "uses": ["p1", "p2", "p3"],
        "relation": "partial_conjunction",
        "boundary": "exhaustive",
        "absent_conjunct_term": "retention",
        "claim": (
            "Stability studies must cover at least three primary batches, and retention "
            "samples must be stored under the same conditions as the primary batches."
        ),
    },
    # --- UNIVERSAL QUANTIFIERS -------------------------------------------
    # Designed contrast: the same overreach shape lands on `not_checkable` when
    # the source is merely silent about the remainder, and on `contradicted`
    # when the source carves the remainder out explicitly.
    {
        "case_id": "CG-18",
        "source_id": "SRC-DEV",
        "uses": ["p1", "p2"],
        "relation": "overgeneralizes",
        "boundary": "bounded",
        "claim": (
            "Every deviation from a validated process parameter triggers a Quality Hold "
            "on the affected batch."
        ),
        "construction_note": (
            "The source assigns the hold to critical deviations only and never says what "
            "happens to the rest. Unsupported, not refuted."
        ),
    },
    {
        "case_id": "CG-19",
        "source_id": "SRC-CC",
        "uses": ["p2", "p3"],
        "relation": "contradicts",
        "boundary": "bounded",
        "claim": (
            "Every change to manufacturing equipment requires requalification before "
            "production resumes."
        ),
        "construction_note": (
            "Same universal shape as CG-18, but here p3 carves out minor changes "
            "explicitly, so the universal is decidably false."
        ),
    },
    # --- LOGICAL WEAKENING ------------------------------------------------
    {
        "case_id": "CG-20",
        "source_id": "SRC-STAB",
        "uses": ["p2"],
        "relation": "weakens",
        "boundary": "bounded",
        "claim": ("Long-term testing must cover at least 6 months at the time of submission."),
        "construction_note": (
            "A minimum of 12 entails a minimum of 6. The passage also contains the phrase "
            "'every six months' in an unrelated role, which is a deliberate lexical trap."
        ),
    },
    # --- NAMED MISSING MATERIAL: the second derivation --------------------
    # These complete two of the boundary variant groups into full triples.
    {
        "case_id": "CG-21",
        "variant_group": "VG-STAB-RETENTION",
        "source_id": "SRC-STAB",
        "uses": ["p1", "p2", "p3"],
        "relation": "absent_from",
        "boundary": "named_missing_material",
        "named_gaps": [
            "storage conditions for retention samples",
            "photostability chamber calibration",
        ],
        "claimed_material_is_a_named_gap": True,
        "claim": ("The guidance does not address storage conditions for retention samples."),
        "construction_note": (
            "Completes VG-STAB-RETENTION into a triple: exhaustive -> supported, bounded "
            "-> not_checkable, named gap -> contradicted. One claim, one passage set, "
            "three verdicts."
        ),
    },
    {
        "case_id": "CG-22",
        "variant_group": "VG-DEV-POSTRELEASE",
        "source_id": "SRC-DEV",
        "uses": ["p1", "p2", "p3"],
        "relation": "absent_from",
        "boundary": "named_missing_material",
        "named_gaps": ["escalation of repeat deviations"],
        "claim": ("The procedure does not cover deviations detected after batch release."),
        "construction_note": (
            "The control for CG-21: same boundary value, but the claimed material is not "
            "among the named gaps, so the answer stays open."
        ),
    },
    # --- SCOPE-MISMATCHED DISTRACTORS ------------------------------------
    # The topical distractors above never reach the entailer: they score far
    # below the retrieval floor, so the floor rejects them and the rule layer is
    # never tested. These share nearly every word with the claim, so they clear
    # the floor comfortably and irrelevance has to be established on scope.
    {
        "case_id": "CG-23a",
        "variant_group": "VG-DIST-SCOPE",
        "source_id": "SRC-SCOPE",
        "uses": ["p1"],
        "relation": "restates",
        "boundary": "bounded",
        "claim": (
            "At the Building 4 manufacturing site, an excursion from a validated process "
            "parameter must be recorded as a deviation within one business day of detection."
        ),
    },
    {
        "case_id": "CG-23b",
        "variant_group": "VG-DIST-SCOPE",
        "source_id": "SRC-SCOPE",
        "uses": ["p1"],
        "distractors": [["SRC-SCOPE", "p2"]],
        "distractor_kind": "scope_mismatch",
        "claim_scope_term": "Building 4",
        "distractor_scope_term": "contract testing laboratory",
        "relation": "restates",
        "boundary": "bounded",
        "claim": (
            "At the Building 4 manufacturing site, an excursion from a validated process "
            "parameter must be recorded as a deviation within one business day of detection."
        ),
    },
    {
        "case_id": "CG-24",
        "source_id": "SRC-SCOPE",
        "uses": ["p1"],
        "distractors": [["SRC-SCOPE", "p2"]],
        "distractor_kind": "scope_mismatch",
        "claim_scope_term": "Building 4",
        "distractor_scope_term": "contract testing laboratory",
        "relation": "contradicts",
        "boundary": "bounded",
        "claim": (
            "At the Building 4 manufacturing site, an excursion from a validated process "
            "parameter may be recorded as a deviation within five business days of detection."
        ),
        "construction_note": (
            "The expensive failure mode, built deliberately: the claim's number is stated "
            "verbatim by a passage in the bundle, but that passage governs a different "
            "site. Reading it as support would be a false `supported` on a claim the "
            "in-scope passage refutes."
        ),
    },
]


# The v0.1 corpus, as published and sealed. `validate` re-checks that every one
# of these still derives the verdict it shipped with, over the same claim text
# and the same passage set. v0.2 is a superset, not a revision.
V0_1_SNAPSHOT: dict[str, tuple[str, int, str]] = {
    "CG-01": ("supported", 1, "bounded"),
    "CG-02": ("supported", 1, "bounded"),
    "CG-03": ("contradicted", 1, "bounded"),
    "CG-04": ("contradicted", 1, "bounded"),
    "CG-05": ("supported", 2, "bounded"),
    "CG-06": ("supported", 2, "bounded"),
    "CG-07a": ("supported", 3, "exhaustive"),
    "CG-07b": ("not_checkable", 3, "bounded"),
    "CG-08a": ("supported", 3, "exhaustive"),
    "CG-08b": ("not_checkable", 3, "bounded"),
    "CG-09a": ("supported", 3, "exhaustive"),
    "CG-09b": ("not_checkable", 3, "bounded"),
    "CG-10": ("not_checkable", 3, "named_missing_material"),
}


# The distinctive term whose absence from the *bundle* is what makes each
# absence case an absence case. Checked mechanically. Declared rather than
# inferred: a head-word check fails on "requalification of laboratory
# instruments", whose source does discuss requalification of equipment.
CLAIMED_ABSENT_TERMS: dict[str, str] = {
    "CG-07a": "months",
    "CG-07b": "months",
    "CG-08a": "retention",
    "CG-08b": "retention",
    "CG-09a": "release",
    "CG-09b": "release",
    "CG-10": "laboratory",
    "CG-13a": "laboratory",
    "CG-13b": "laboratory",
    "CG-16a": "photostability",
    "CG-16b": "photostability",
    "CG-21": "retention",
    "CG-22": "release",
}

# Which parameter a variant group holds everything else constant against, and
# what the group asserts about it. A group is only worth running if it makes a
# falsifiable statement, so both values are checked in `validate`.
DEFAULT_EXPECTATION: dict[str, str] = {
    "source_boundary": "separates",
    "distractors": "invariant",
}


def build() -> dict[str, Any]:
    """Materialize every case with its derived verdict."""
    built: list[dict[str, Any]] = []
    for case in CASES:
        source = SOURCES[case["source_id"]]
        verdict, derivation = derive_verdict(
            case["relation"],
            case["boundary"],
            claimed_material_is_a_named_gap=case.get("claimed_material_is_a_named_gap", False),
        )
        support_refs = [_ref(case, u) for u in case["uses"]]
        distractor_refs = [_ref(case, u) for u in case.get("distractors", [])]
        passages = [
            {"passage_id": f"{src}#{pid}", "text": _passage_text(src, pid), "role": role}
            for role, refs in (("support", support_refs), ("distractor", distractor_refs))
            for src, pid in refs
        ]
        # "Multi-document" is about the *supporting* evidence spanning documents.
        # Distractors also come from other sources, but a case is not a
        # multi-document case just because an irrelevant passage was added.
        support_source_ids = sorted({src for src, _ in support_refs})
        source_ids = sorted({src for src, _ in support_refs + distractor_refs})
        entry: dict[str, Any] = {
            "case_id": case["case_id"],
            "claim_id": f"cg-{case['case_id'].lower()}",
            "claim_text": case["claim"],
            "source_id": case["source_id"],
            "source_title": source["title"],
            "source_ids": source_ids,
            "support_source_ids": support_source_ids,
            "source_titles": [SOURCES[s]["title"] for s in support_source_ids],
            "multi_document": len(support_source_ids) > 1,
            "source_boundary": case["boundary"],
            "relation": case["relation"],
            "passages": passages,
            "n_support_passages": len(support_refs),
            "n_distractor_passages": len(distractor_refs),
            "expected_verdict": verdict,
            "derivation": derivation,
        }
        for optional in (
            "variant_group",
            "named_gaps",
            "claimed_material_is_a_named_gap",
            "absent_conjunct_term",
            "distractor_absent_terms",
            "distractor_kind",
            "claim_scope_term",
            "distractor_scope_term",
            "construction_note",
        ):
            if optional in case:
                entry[optional] = case[optional]
        if case["relation"] == "absent_from":
            entry["claimed_absent_term"] = CLAIMED_ABSENT_TERMS[case["case_id"]]
            entry["source_silent_on"] = source["silent_on"]
        built.append(entry)

    groups = _describe_groups(built)
    for entry in built:
        gid = entry.get("variant_group")
        if gid:
            entry["variant_axis"] = groups[gid]["axis"]
            entry["variant_expectation"] = groups[gid]["expectation"]

    return {
        "corpus_id": "construction-gold-v0.2",
        "schema_version": "cal-construction-gold-v2",
        "supersedes": "construction-gold-v0.1",
        "label": (
            "By-construction DEV gold in regulatory prose. Verdicts are derived from the "
            "stipulated construction, never coded by a rater. Not validation, not gate "
            "evidence, not an accuracy claim, and not a statement about any real guidance."
        ),
        "stipulations": [
            "The passages listed for a case are the entire world for that case. Nothing "
            "outside them is true or false.",
            "source_boundary=exhaustive stipulates the bundle is the complete source, so "
            "a claim about what the source does not say is decidable.",
            "source_boundary=named_missing_material stipulates the bundle is an excerpt "
            "AND that the listed named_gaps exist in the source but were left out, so "
            "material among the named gaps is stipulated to be addressed by the source.",
            "Passages marked role=distractor are stipulated to be irrelevant to the "
            "claim, which is checked by requiring the case's declared distinctive terms "
            "to be absent from them.",
        ],
        "boundary_distribution": {
            b: sum(1 for c in built if c["source_boundary"] == b)
            for b in ("bounded", "exhaustive", "named_missing_material")
        },
        "relation_distribution": {
            r: sum(1 for c in built if c["relation"] == r)
            for r in sorted({c["relation"] for c in built})
        },
        "variant_groups": groups,
        "n_cases": len(built),
        "n_multi_document": sum(1 for c in built if c["multi_document"]),
        "n_with_distractors": sum(1 for c in built if c["n_distractor_passages"]),
        "cases": built,
    }


def _describe_groups(built: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Summarize each variant group: axis, expectation, and the gold partition."""
    groups: dict[str, dict[str, Any]] = {}
    declared = {c["case_id"]: c for c in CASES}
    for entry in built:
        gid = entry.get("variant_group")
        if not gid:
            continue
        groups.setdefault(gid, {"members": []})["members"].append(entry["case_id"])

    for gid, group in groups.items():
        members = [c for c in built if c.get("variant_group") == gid]
        boundaries = {m["source_boundary"] for m in members}
        distractor_counts = {m["n_distractor_passages"] for m in members}
        axis = "source_boundary" if len(boundaries) > 1 else "distractors"
        override = next(
            (
                declared[m["case_id"]].get("variant_expectation")
                for m in members
                if declared[m["case_id"]].get("variant_expectation")
            ),
            None,
        )
        group["axis"] = axis
        group["expectation"] = override or DEFAULT_EXPECTATION[axis]
        group["gold_verdicts"] = {m["case_id"]: m["expected_verdict"] for m in members}
        group["n_distinct_gold_verdicts"] = len({m["expected_verdict"] for m in members})
        group["varies"] = (
            sorted(boundaries) if axis == "source_boundary" else sorted(distractor_counts)
        )
    return groups


def _content_words(text: str) -> set[str]:
    """Words long enough to carry subject matter, for the near-twin check."""
    return {w.strip(".,;:") for w in text.split() if len(w.strip(".,;:")) >= 5}


def validate(corpus: dict[str, Any]) -> list[str]:
    """Fail-closed checks that the gold really is derived, not authored."""
    problems: list[str] = []
    seen: set[str] = set()
    declared = {c["case_id"]: c for c in CASES}

    for case in corpus["cases"]:
        cid = case["case_id"]
        if cid in seen:
            problems.append(f"{cid}: duplicate case_id")
        seen.add(cid)

        # The recorded verdict must be exactly what the deriver returns.
        verdict, derivation = derive_verdict(
            case["relation"],
            case["source_boundary"],
            claimed_material_is_a_named_gap=case.get("claimed_material_is_a_named_gap", False),
        )
        if case["expected_verdict"] != verdict:
            problems.append(
                f"{cid}: recorded verdict {case['expected_verdict']!r} != derived {verdict!r}"
            )
        if case["derivation"] != derivation:
            problems.append(f"{cid}: derivation text is not the derived one")

        # Every passage must be a stipulated one, verbatim.
        for passage in case["passages"]:
            src, _, pid = passage["passage_id"].partition("#")
            if passage["text"] != _passage_text(src, pid):
                problems.append(f"{cid}: passage {passage['passage_id']} is not verbatim")

        bundle = " ".join(p["text"].lower() for p in case["passages"])
        support = " ".join(p["text"].lower() for p in case["passages"] if p["role"] == "support")

        # `exhaustive` is a strong stipulation: the bundle must actually contain
        # every stipulated passage of every source it draws on, or the case is
        # claiming completeness it does not have.
        if case["source_boundary"] == "exhaustive":
            held = {p["passage_id"] for p in case["passages"]}
            for src in case["source_ids"]:
                for pid, _ in SOURCES[src]["passages"]:
                    if f"{src}#{pid}" not in held:
                        problems.append(f"{cid}: declared exhaustive but bundle omits {src}#{pid}")

        # An absence claim is only well-formed if the bundle really is silent on
        # the claimed material. Checking a declared distinctive term rather than
        # a head word is what lets "requalification of laboratory instruments" be
        # absent from a source that does discuss requalification of equipment.
        if case["relation"] == "absent_from":
            term = case["claimed_absent_term"].lower()
            if term in bundle:
                problems.append(
                    f"{cid}: bundle is not silent on the claimed material — it contains {term!r}"
                )
            for silent in case["source_silent_on"]:
                if silent["absent_term"].lower() in support:
                    problems.append(
                        f"{cid}: source is not silent on {silent['topic']!r} — "
                        f"it contains {silent['absent_term']!r}"
                    )
            if case["source_boundary"] == "named_missing_material":
                gaps = case.get("named_gaps")
                if not gaps:
                    problems.append(f"{cid}: named_missing_material with no named_gaps")
                in_gaps = case.get("claimed_material_is_a_named_gap", False)
                mentioned = any(term in gap.lower() for gap in gaps or [])
                if in_gaps != mentioned:
                    problems.append(
                        f"{cid}: claimed_material_is_a_named_gap={in_gaps} does not match "
                        f"whether {term!r} appears in named_gaps ({mentioned})"
                    )

        # A partial conjunction needs one conjunct that really is missing.
        if case["relation"] == "partial_conjunction":
            missing = case["absent_conjunct_term"].lower()
            if missing in bundle:
                problems.append(
                    f"{cid}: absent conjunct {missing!r} is present in the bundle, so the "
                    "case is not a partial conjunction"
                )
            if missing not in case["claim_text"].lower():
                problems.append(f"{cid}: absent conjunct {missing!r} is not in the claim")

        # A distractor is only a distractor if it cannot bear on the claim, and
        # there are two ways to establish that mechanically.
        distractors = [p for p in case["passages"] if p["role"] == "distractor"]
        if distractors:
            kind = case.get("distractor_kind", "topical")
            claim_l = case["claim_text"].lower()
            joined = " ".join(p["text"].lower() for p in distractors)

            if kind == "topical":
                # Irrelevant because it shares none of the claim's subject matter.
                terms = case.get("distractor_absent_terms")
                if not terms:
                    problems.append(
                        f"{cid}: topical distractor with no disjointness terms declared"
                    )
                for term in terms or []:
                    if term.lower() not in claim_l:
                        problems.append(
                            f"{cid}: disjointness term {term!r} is not in the claim, so "
                            "checking it proves nothing"
                        )
                    if term.lower() in joined:
                        problems.append(
                            f"{cid}: distractor is not disjoint from the claim — "
                            f"it contains {term!r}"
                        )
                for passage in distractors:
                    src, _, _ = passage["passage_id"].partition("#")
                    if src == case["source_id"]:
                        problems.append(
                            f"{cid}: topical distractor {passage['passage_id']} comes from "
                            "the case's own source"
                        )

            elif kind == "scope_mismatch":
                # Irrelevant because it governs a different, declared scope. Same
                # document is fine here — same-document scope confusion is the
                # realistic failure. What must hold is that the two scopes are
                # disjoint and that the distractor is lexically close enough to
                # survive retrieval, or it tests nothing the topical ones don't.
                claim_scope = case.get("claim_scope_term", "").lower()
                dist_scope = case.get("distractor_scope_term", "").lower()
                if not claim_scope or not dist_scope:
                    problems.append(f"{cid}: scope_mismatch distractor with no scopes declared")
                if claim_scope and claim_scope not in claim_l:
                    problems.append(f"{cid}: claim scope {claim_scope!r} is not in the claim")
                if claim_scope and claim_scope in joined:
                    problems.append(
                        f"{cid}: distractor is in the claim's scope — it names {claim_scope!r}"
                    )
                if dist_scope and dist_scope not in joined:
                    problems.append(
                        f"{cid}: distractor does not name its declared scope {dist_scope!r}"
                    )
                if dist_scope and dist_scope in claim_l:
                    problems.append(
                        f"{cid}: the claim names the distractor's scope {dist_scope!r}, so "
                        "the scopes are not disjoint"
                    )
                shared = {w for w in _content_words(claim_l) if w in _content_words(joined)}
                if len(shared) < 6:
                    problems.append(
                        f"{cid}: scope_mismatch distractor shares only {len(shared)} content "
                        "words with the claim, so retrieval will drop it and it tests "
                        "nothing the topical distractors do not"
                    )
            else:
                problems.append(f"{cid}: unknown distractor_kind {kind!r}")

    # Variant groups must hold everything constant except their declared axis,
    # and must make a falsifiable statement about it.
    by_group: dict[str, list[dict[str, Any]]] = {}
    for case in corpus["cases"]:
        gid = case.get("variant_group")
        if gid:
            by_group.setdefault(gid, []).append(case)

    for gid, members in sorted(by_group.items()):
        if len(members) < 2:
            problems.append(f"{gid}: variant group needs at least two members")
            continue
        axis = members[0]["variant_axis"]
        expectation = members[0]["variant_expectation"]

        claims = {m["claim_text"] for m in members}
        if len(claims) != 1:
            problems.append(f"{gid}: members do not share one claim text")
        support_sets = {
            tuple(p["passage_id"] for p in m["passages"] if p["role"] == "support") for m in members
        }
        if len(support_sets) != 1:
            problems.append(f"{gid}: members do not share one supporting passage set")

        boundaries = [m["source_boundary"] for m in members]
        distractor_sets = {
            tuple(p["passage_id"] for p in m["passages"] if p["role"] == "distractor")
            for m in members
        }
        if axis == "source_boundary":
            if len(set(boundaries)) != len(boundaries):
                problems.append(f"{gid}: boundary axis but two members share a boundary")
            if len(distractor_sets) != 1:
                problems.append(f"{gid}: boundary axis but distractor sets also differ")
        else:
            if len(set(boundaries)) != 1:
                problems.append(f"{gid}: distractor axis but boundaries also differ")
            if len(distractor_sets) != len(members):
                problems.append(f"{gid}: distractor axis but distractor sets do not differ")

        distinct = len({m["expected_verdict"] for m in members})
        if expectation == "separates" and distinct < 2:
            problems.append(
                f"{gid}: declared to separate but every member derives the same verdict — "
                "the group tests nothing"
            )
        if expectation == "invariant" and distinct != 1:
            problems.append(
                f"{gid}: declared invariant but members derive different verdicts — "
                "the parameter is not actually irrelevant here"
            )

    # v0.2 is a superset of v0.1, not a revision of it.
    by_id = {c["case_id"]: c for c in corpus["cases"]}
    for cid, (verdict, n_support, boundary) in V0_1_SNAPSHOT.items():
        case = by_id.get(cid)
        if case is None:
            problems.append(f"{cid}: v0.1 case is missing from v0.2")
            continue
        if case["expected_verdict"] != verdict:
            problems.append(
                f"{cid}: v0.1 shipped {verdict!r}, this build derives {case['expected_verdict']!r}"
            )
        if case["source_boundary"] != boundary:
            problems.append(f"{cid}: v0.1 boundary {boundary!r} changed")
        if case["n_support_passages"] != n_support:
            problems.append(
                f"{cid}: v0.1 used {n_support} passages, this build uses "
                f"{case['n_support_passages']}"
            )
        if case["n_distractor_passages"]:
            problems.append(f"{cid}: v0.1 case must not gain distractors")

    for cid in declared:
        if cid not in by_id:
            problems.append(f"{cid}: declared but not built")
    return problems


def main() -> None:
    corpus = build()
    problems = validate(corpus)

    OUT.mkdir(parents=True, exist_ok=True)
    body = json.dumps(corpus, indent=2, sort_keys=True) + "\n"
    (OUT / "corpus.json").write_text(body, encoding="utf-8")

    gold = {
        "gold_version": "construction-gold-v0.2",
        "derived_from": "scripts/build_construction_gold.py::derive_verdict",
        "note": "Regenerate rather than trust. No rater produced these labels.",
        "claims": [
            {
                "claim_id": c["claim_id"],
                "gold_verdict": c["expected_verdict"],
                "source_boundary": c["source_boundary"],
                "derivation": c["derivation"],
            }
            for c in corpus["cases"]
        ],
    }
    (OUT / "gold.json").write_text(
        json.dumps(gold, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    digest = hashlib.sha256(body.encode()).hexdigest()
    print(f"cases            : {corpus['n_cases']}")
    print(f"boundaries       : {corpus['boundary_distribution']}")
    print(f"relations        : {corpus['relation_distribution']}")
    print(f"multi-document   : {corpus['n_multi_document']}")
    print(f"with distractors : {corpus['n_with_distractors']}")
    print(f"corpus sha256    : {digest[:16]}")
    verdicts: dict[str, int] = {}
    for c in corpus["cases"]:
        verdicts[c["expected_verdict"]] = verdicts.get(c["expected_verdict"], 0) + 1
    print(f"derived verdicts : {verdicts}")
    print("\nvariant groups:")
    for gid, group in sorted(corpus["variant_groups"].items()):
        print(
            f"  {gid:<22} axis={group['axis']:<16} expects={group['expectation']:<10} "
            f"{len(group['members'])} members, {group['n_distinct_gold_verdicts']} distinct gold"
        )
    if problems:
        print(f"\nVALIDATION FAILED ({len(problems)}):")
        for p in problems:
            print(f"  - {p}")
        raise SystemExit(1)
    print("\nvalidation: all checks passed")
    print(f"wrote {OUT}/corpus.json and gold.json")


if __name__ == "__main__":
    main()
