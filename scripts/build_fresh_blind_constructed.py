"""Build a 50-item by-construction twin of the sealed fresh-blind packet.

The sealed 2026-07-24 packet (25 pharma + 25 plain narrative) has human gold.
Those items were not constructed with a stipulated relation, so they cannot be
given derived keys after the fact — recoding them would still be a judgment.

This corpus keeps the packet's *shape*: n=50, two registers, mostly single-passage
restates, a starved/unaddressed band, some direct contradictions, one numeric bound.
Verdicts come from ``derive_verdict`` (plus ``unaddressed``), never from a rater.

DEV construction. Not a confirmatory gate, not a replacement of the sealed human
packet, not an accuracy claim, and not a statement about any real document.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any, Literal


def _load_construction_gold() -> Any:
    path = Path(__file__).resolve().parent / "build_construction_gold.py"
    spec = importlib.util.spec_from_file_location("build_construction_gold", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_CG = _load_construction_gold()
PHARMA_SOURCES: dict[str, dict[str, Any]] = _CG.SOURCES
derive_construction_verdict = _CG.derive_verdict

SourceBoundary = Literal["exhaustive", "bounded", "named_missing_material"]
Relation = Literal[
    "restates",
    "contradicts",
    "absent_from",
    "instantiates_bound",
    "unaddressed",
]
Register = Literal["pharma_regulatory", "plain_narrative"]

OUT = Path(__file__).resolve().parents[2] / "outputs" / "2026-08-20-fresh-blind-constructed"

# ---------------------------------------------------------------------------
# Narrative worlds. Pharma reuses the stipulated sources from construction gold.
# ---------------------------------------------------------------------------

NARRATIVE_SOURCES: dict[str, dict[str, Any]] = {
    "SRC-DEPOT": {
        "title": "Depot night log — bus 412",
        "passages": [
            (
                "p1",
                "Marco worked the night shift in bay 3. He opened the headlight housing "
                "on bus 412, fitted a new bulb, checked the beam against the painted wall "
                "line, and wrote the time in the depot night log.",
            ),
            (
                "p2",
                "A bus held out of service for more than 6 hours after a safety defect is "
                "found shall be tagged do-not-dispatch until a supervisor clears it.",
            ),
            (
                "p3",
                "The depot night log records headlight replacements and the time of the "
                "work. The log does not list parts invoices.",
            ),
        ],
        "silent_on": [
            {"topic": "overtime pay", "absent_term": "overtime"},
            {"topic": "union steward attendance", "absent_term": "steward"},
        ],
    },
    "SRC-KITCHEN": {
        "title": "Morning bake notes — rye deck",
        "passages": [
            (
                "p1",
                "The baker preheated the deck oven to 220 degrees Celsius before loading "
                "the rye loaves. Three starter batches of rye were mixed before dawn.",
            ),
            (
                "p2",
                "A tray held above 180 degrees Celsius for more than 5 minutes after a "
                "burnt-sugar alarm shall be discarded.",
            ),
            (
                "p3",
                "The morning bake sheet records oven setpoint and load time. It does not "
                "list wholesale orders.",
            ),
        ],
        "silent_on": [
            {"topic": "wholesale orders", "absent_term": "wholesale"},
            {"topic": "delivery van schedule", "absent_term": "van"},
        ],
    },
    "SRC-HIVE": {
        "title": "Apiary morning notes",
        "passages": [
            (
                "p1",
                "Mara inspected the brood frames in the morning, smoked the box lightly, "
                "and left the capped honey in place. The yard has four hives along the fence.",
            ),
            (
                "p2",
                "Honey supers stored above 30 degrees Celsius for more than 4 hours shall "
                "be moved to the shade shed.",
            ),
            (
                "p3",
                "The yard notes record which hives were opened and whether brood was seen. "
                "They do not list bottling dates.",
            ),
        ],
        "silent_on": [
            {"topic": "extracted honey weight", "absent_term": "pounds"},
            {"topic": "bottling", "absent_term": "bottling"},
        ],
    },
    "SRC-HARBOR": {
        "title": "Slip 2 morning ferry log",
        "passages": [
            (
                "p1",
                "The ferry left slip 2 at 06:15 with twelve passengers. Tickets were sold "
                "only at the wooden kiosk. The skipper logged a clear channel.",
            ),
            (
                "p2",
                "A vessel delayed more than 20 minutes shall radio the harbor office before "
                "leaving the slip.",
            ),
            (
                "p3",
                "The slip log records departure time and passenger count. It does not list "
                "freight cargo.",
            ),
        ],
        "silent_on": [
            {"topic": "freight cargo", "absent_term": "freight"},
            {"topic": "overnight berth fees", "absent_term": "berth"},
        ],
    },
    "SRC-LIBRARY": {
        "title": "West-stack closing notes",
        "passages": [
            (
                "p1",
                "The night clerk reshelved the returned atlases before locking the west "
                "stack. The west stack holds the map collection. The clerk signed the "
                "closing book at 21:40.",
            ),
            (
                "p2",
                "Any reference volume left off the shelf for more than 3 hours after "
                "closing shall be logged as missing-pending.",
            ),
            (
                "p3",
                "The closing book records who locked the west stack and the time. It does "
                "not list overdue fines.",
            ),
        ],
        "silent_on": [
            {"topic": "overdue fines", "absent_term": "fines"},
            {"topic": "interlibrary loan", "absent_term": "interlibrary"},
        ],
    },
}

SOURCES: dict[str, dict[str, Any]] = {**PHARMA_SOURCES, **NARRATIVE_SOURCES}


def derive_twin_verdict(
    relation: Relation,
    boundary: SourceBoundary,
    *,
    claimed_material_is_a_named_gap: bool = False,
) -> tuple[str, str]:
    """Derived gold. ``unaddressed`` is the starved-cell analogue: object-level
    claim, stipulated passages silent. That is not a source-coverage claim, so
    exhaustiveness does not settle it.
    """
    if relation == "unaddressed":
        return (
            "not_checkable",
            "the stipulated passages do not address the claim; silence in an excerpt "
            "is not a verdict on the claim and is not absence from the source",
        )
    return derive_construction_verdict(
        relation,
        boundary,
        claimed_material_is_a_named_gap=claimed_material_is_a_named_gap,
    )


def _passage_text(source_id: str, passage_id: str) -> str:
    for pid, text in SOURCES[source_id]["passages"]:
        if pid == passage_id:
            return str(text)
    raise KeyError(f"{source_id}#{passage_id} is not stipulated")


def _ref(case: dict[str, Any], use: Any) -> tuple[str, str]:
    if isinstance(use, str):
        return (case["source_id"], use)
    src, pid = use
    return (src, pid)


# Distinctive term that must be absent from the bundle for unaddressed / absent_from.
CLAIMED_ABSENT_TERMS: dict[str, str] = {}


def _case(
    case_id: str,
    *,
    register: Register,
    source_id: str,
    uses: list[Any],
    relation: Relation,
    claim: str,
    boundary: SourceBoundary = "bounded",
    absent_term: str | None = None,
    variant_group: str | None = None,
    named_gaps: list[str] | None = None,
    claimed_material_is_a_named_gap: bool = False,
) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "case_id": case_id,
        "register": register,
        "source_id": source_id,
        "uses": uses,
        "relation": relation,
        "boundary": boundary,
        "claim": claim,
    }
    if variant_group:
        entry["variant_group"] = variant_group
    if named_gaps is not None:
        entry["named_gaps"] = named_gaps
    if claimed_material_is_a_named_gap:
        entry["claimed_material_is_a_named_gap"] = True
    if absent_term is not None:
        CLAIMED_ABSENT_TERMS[case_id] = absent_term
    return entry


CASES: list[dict[str, Any]] = [
    # =====================================================================
    # Pharma register (25). Same stipulated worlds as construction gold.
    # Mix mirrors the sealed packet: restates, contradictions, starved
    # (unaddressed), one numeric bound, one absence pair on boundary.
    # =====================================================================
    _case(
        "FBC-P-01",
        register="pharma_regulatory",
        source_id="SRC-EQ-QUAL",
        uses=["p1"],
        relation="restates",
        claim=(
            "Equipment used in commercial manufacture shall be qualified before first "
            "production use."
        ),
    ),
    _case(
        "FBC-P-02",
        register="pharma_regulatory",
        source_id="SRC-EQ-QUAL",
        uses=["p2"],
        relation="restates",
        claim=(
            "Requalification is required after relocation, major repair, or modification "
            "of a critical component."
        ),
    ),
    _case(
        "FBC-P-03",
        register="pharma_regulatory",
        source_id="SRC-STAB",
        uses=["p1"],
        relation="restates",
        claim=(
            "Stability studies shall be run on at least three primary batches in the "
            "proposed container closure system."
        ),
    ),
    _case(
        "FBC-P-04",
        register="pharma_regulatory",
        source_id="SRC-STAB",
        uses=["p2"],
        relation="restates",
        claim=(
            "Long-term testing shall cover a minimum of 12 months at the time of submission."
        ),
    ),
    _case(
        "FBC-P-05",
        register="pharma_regulatory",
        source_id="SRC-DEV",
        uses=["p1"],
        relation="restates",
        claim=(
            "An excursion from a validated process parameter shall be recorded as a "
            "deviation within one business day of detection."
        ),
    ),
    _case(
        "FBC-P-06",
        register="pharma_regulatory",
        source_id="SRC-CC",
        uses=["p1"],
        relation="restates",
        claim=(
            "Relocation of manufacturing equipment between production suites shall be "
            "processed as a major change."
        ),
    ),
    _case(
        "FBC-P-07",
        register="pharma_regulatory",
        source_id="SRC-CC",
        uses=["p3"],
        relation="restates",
        claim=(
            "Minor changes shall be documented and closed without requalification of the "
            "affected equipment."
        ),
    ),
    _case(
        "FBC-P-08",
        register="pharma_regulatory",
        source_id="SRC-SCOPE",
        uses=["p1"],
        relation="restates",
        claim=(
            "At the Building 4 manufacturing site, an excursion shall be recorded as a "
            "deviation within one business day of detection."
        ),
    ),
    _case(
        "FBC-P-09",
        register="pharma_regulatory",
        source_id="SRC-EQ-QUAL",
        uses=["p3"],
        relation="restates",
        claim=(
            "Where a site establishes a periodic requalification interval, that interval "
            "shall be justified in the validation master plan."
        ),
    ),
    # --- contradictions ---------------------------------------------------
    _case(
        "FBC-P-10",
        register="pharma_regulatory",
        source_id="SRC-STAB",
        uses=["p3"],
        relation="contradicts",
        claim=(
            "A shelf-life of 36 months may be assigned on the basis of accelerated data alone."
        ),
    ),
    _case(
        "FBC-P-11",
        register="pharma_regulatory",
        source_id="SRC-EQ-QUAL",
        uses=["p2"],
        relation="contradicts",
        claim="Relocation of qualified equipment does not require requalification.",
    ),
    _case(
        "FBC-P-12",
        register="pharma_regulatory",
        source_id="SRC-DEV",
        uses=["p2"],
        relation="contradicts",
        claim=(
            "A deviation classified as critical does not trigger a Quality Hold on the "
            "affected batch."
        ),
    ),
    _case(
        "FBC-P-13",
        register="pharma_regulatory",
        source_id="SRC-CC",
        uses=["p3"],
        relation="contradicts",
        claim=(
            "Changes classified as minor shall require requalification of the affected "
            "equipment before production resumes."
        ),
    ),
    # --- unaddressed (starved analogue): object-level claim, bundle silent
    _case(
        "FBC-P-14",
        register="pharma_regulatory",
        source_id="SRC-EQ-QUAL",
        uses=["p1"],
        relation="unaddressed",
        claim="Laboratory instruments shall be requalified every 18 months.",
        absent_term="laboratory",
    ),
    _case(
        "FBC-P-15",
        register="pharma_regulatory",
        source_id="SRC-EQ-QUAL",
        uses=["p2"],
        relation="unaddressed",
        claim="Incoming laboratory reagents expire after six months.",
        absent_term="laboratory",
    ),
    _case(
        "FBC-P-16",
        register="pharma_regulatory",
        source_id="SRC-STAB",
        uses=["p1"],
        relation="unaddressed",
        claim="Retention samples shall be stored at 2 to 8 degrees Celsius.",
        absent_term="retention",
    ),
    _case(
        "FBC-P-17",
        register="pharma_regulatory",
        source_id="SRC-STAB",
        uses=["p2"],
        relation="unaddressed",
        claim="Photostability chambers shall be calibrated quarterly.",
        absent_term="photostability",
    ),
    _case(
        "FBC-P-18",
        register="pharma_regulatory",
        source_id="SRC-DEV",
        uses=["p1"],
        relation="unaddressed",
        claim="Deviations detected after batch release require no investigation.",
        absent_term="release",
    ),
    _case(
        "FBC-P-19",
        register="pharma_regulatory",
        source_id="SRC-DEV",
        uses=["p2"],
        relation="unaddressed",
        claim="Released batches are exempt from Quality Hold.",
        absent_term="Released",
    ),
    _case(
        "FBC-P-20",
        register="pharma_regulatory",
        source_id="SRC-CC",
        uses=["p1"],
        relation="unaddressed",
        claim="Emergency authorization changes skip documentation.",
        absent_term="emergency",
    ),
    _case(
        "FBC-P-21",
        register="pharma_regulatory",
        source_id="SRC-CC",
        uses=["p4"],
        relation="unaddressed",
        claim="Emergency generators need no change control record.",
        absent_term="emergency",
    ),
    _case(
        "FBC-P-22",
        register="pharma_regulatory",
        source_id="SRC-SCOPE",
        uses=["p1"],
        relation="unaddressed",
        claim="Packaging sites shall record deviations within two hours.",
        absent_term="packaging",
    ),
    _case(
        "FBC-P-23",
        register="pharma_regulatory",
        source_id="SRC-STAB",
        uses=["p3"],
        relation="unaddressed",
        claim="Photostability testing may replace long-term testing at submission.",
        absent_term="photostability",
    ),
    # --- numeric bound (P-22 analogue, constructed cleanly) --------------
    _case(
        "FBC-P-24",
        register="pharma_regulatory",
        source_id="SRC-DEV",
        uses=["p3", "p2"],
        relation="instantiates_bound",
        claim=(
            "A cold-chain batch held at 10 degrees Celsius for 7 hours must be placed on "
            "Quality Hold."
        ),
    ),
    # --- absence pair: same claim, boundary varies (not in original packet;
    # included so the twin still has one derived source-coverage control).
    _case(
        "FBC-P-25",
        register="pharma_regulatory",
        source_id="SRC-EQ-QUAL",
        uses=["p1", "p2", "p3"],
        relation="absent_from",
        boundary="exhaustive",
        claim=(
            "The guidance does not prescribe a fixed numeric requalification interval for "
            "equipment."
        ),
        absent_term="months",
    ),
    # =====================================================================
    # Narrative register (25). Plain-prose worlds; same relations.
    # Original S-band is restates-heavy with two starved cells.
    # =====================================================================
    _case(
        "FBC-S-01",
        register="plain_narrative",
        source_id="SRC-DEPOT",
        uses=["p1"],
        relation="restates",
        claim="The bus depot mechanic worked on a headlight during the night shift.",
    ),
    _case(
        "FBC-S-02",
        register="plain_narrative",
        source_id="SRC-DEPOT",
        uses=["p1"],
        relation="restates",
        claim="Marco fitted a new bulb in the headlight housing on bus 412.",
    ),
    _case(
        "FBC-S-03",
        register="plain_narrative",
        source_id="SRC-DEPOT",
        uses=["p1"],
        relation="restates",
        claim="Marco checked the headlight beam against the painted wall line.",
    ),
    _case(
        "FBC-S-04",
        register="plain_narrative",
        source_id="SRC-DEPOT",
        uses=["p1"],
        relation="restates",
        claim="Marco wrote the time of the headlight work in the depot night log.",
    ),
    _case(
        "FBC-S-05",
        register="plain_narrative",
        source_id="SRC-KITCHEN",
        uses=["p1"],
        relation="restates",
        claim="The baker preheated the deck oven to 220 degrees Celsius.",
    ),
    _case(
        "FBC-S-06",
        register="plain_narrative",
        source_id="SRC-KITCHEN",
        uses=["p1"],
        relation="restates",
        claim="Three starter batches of rye were mixed before dawn.",
    ),
    _case(
        "FBC-S-07",
        register="plain_narrative",
        source_id="SRC-KITCHEN",
        uses=["p1"],
        relation="restates",
        claim="The baker loaded rye loaves after preheating the deck oven.",
    ),
    _case(
        "FBC-S-08",
        register="plain_narrative",
        source_id="SRC-HIVE",
        uses=["p1"],
        relation="restates",
        claim="Mara inspected the brood frames in the morning.",
    ),
    _case(
        "FBC-S-09",
        register="plain_narrative",
        source_id="SRC-HIVE",
        uses=["p1"],
        relation="restates",
        claim="The yard has four hives along the fence.",
    ),
    _case(
        "FBC-S-10",
        register="plain_narrative",
        source_id="SRC-HIVE",
        uses=["p1"],
        relation="restates",
        claim="Mara left the capped honey in place after inspecting the brood frames.",
    ),
    _case(
        "FBC-S-11",
        register="plain_narrative",
        source_id="SRC-HARBOR",
        uses=["p1"],
        relation="restates",
        claim="The ferry left slip 2 at 06:15.",
    ),
    _case(
        "FBC-S-12",
        register="plain_narrative",
        source_id="SRC-HARBOR",
        uses=["p1"],
        relation="restates",
        claim="Twelve passengers were on the ferry when it left slip 2.",
    ),
    _case(
        "FBC-S-13",
        register="plain_narrative",
        source_id="SRC-HARBOR",
        uses=["p1"],
        relation="restates",
        claim="Tickets for the ferry were sold only at the wooden kiosk.",
    ),
    _case(
        "FBC-S-14",
        register="plain_narrative",
        source_id="SRC-LIBRARY",
        uses=["p1"],
        relation="restates",
        claim="The night clerk reshelved the returned atlases before locking the west stack.",
    ),
    _case(
        "FBC-S-15",
        register="plain_narrative",
        source_id="SRC-LIBRARY",
        uses=["p1"],
        relation="restates",
        claim="The west stack holds the map collection.",
    ),
    _case(
        "FBC-S-16",
        register="plain_narrative",
        source_id="SRC-LIBRARY",
        uses=["p1"],
        relation="restates",
        claim="The night clerk signed the closing book at 21:40.",
    ),
    _case(
        "FBC-S-17",
        register="plain_narrative",
        source_id="SRC-DEPOT",
        uses=["p3"],
        relation="restates",
        claim="The depot night log records headlight replacements and the time of the work.",
    ),
    _case(
        "FBC-S-18",
        register="plain_narrative",
        source_id="SRC-KITCHEN",
        uses=["p3"],
        relation="restates",
        claim="The morning bake sheet records oven setpoint and load time.",
    ),
    _case(
        "FBC-S-19",
        register="plain_narrative",
        source_id="SRC-HARBOR",
        uses=["p3"],
        relation="restates",
        claim="The slip log records departure time and passenger count.",
    ),
    _case(
        "FBC-S-20",
        register="plain_narrative",
        source_id="SRC-LIBRARY",
        uses=["p3"],
        relation="restates",
        claim="The closing book records who locked the west stack and the time.",
    ),
    # --- contradictions ---------------------------------------------------
    _case(
        "FBC-S-21",
        register="plain_narrative",
        source_id="SRC-DEPOT",
        uses=["p1"],
        relation="contradicts",
        claim="Marco left the headlight housing on bus 412 unopened during the night shift.",
    ),
    _case(
        "FBC-S-22",
        register="plain_narrative",
        source_id="SRC-KITCHEN",
        uses=["p1"],
        relation="contradicts",
        claim="The baker loaded the rye loaves without preheating the deck oven.",
    ),
    _case(
        "FBC-S-23",
        register="plain_narrative",
        source_id="SRC-HARBOR",
        uses=["p1"],
        relation="contradicts",
        claim="The ferry left slip 2 with no passengers.",
    ),
    # --- unaddressed (S-15 / S-18 starved analogue) ----------------------
    _case(
        "FBC-S-24",
        register="plain_narrative",
        source_id="SRC-HIVE",
        uses=["p1"],
        relation="unaddressed",
        claim="The beekeeper extracted 50 pounds of wildflower honey.",
        absent_term="pounds",
    ),
    _case(
        "FBC-S-25",
        register="plain_narrative",
        source_id="SRC-DEPOT",
        uses=["p1"],
        relation="unaddressed",
        claim="The depot paid Marco overtime for the night shift.",
        absent_term="overtime",
    ),
]

DEFAULT_EXPECTATION = {"source_boundary": "separates", "distractors": "invariant"}


def build() -> dict[str, Any]:
    if len(CASES) != 50:
        raise RuntimeError(f"twin must have 50 cases, built {len(CASES)}")
    built: list[dict[str, Any]] = []
    for case in CASES:
        source = SOURCES[case["source_id"]]
        verdict, derivation = derive_twin_verdict(
            case["relation"],
            case["boundary"],
            claimed_material_is_a_named_gap=case.get("claimed_material_is_a_named_gap", False),
        )
        support_refs = [_ref(case, u) for u in case["uses"]]
        passages = [
            {
                "passage_id": f"{src}#{pid}",
                "text": _passage_text(src, pid),
                "role": "support",
            }
            for src, pid in support_refs
        ]
        support_source_ids = sorted({src for src, _ in support_refs})
        entry: dict[str, Any] = {
            "case_id": case["case_id"],
            "claim_id": case["case_id"].lower(),
            "register": case["register"],
            "claim_text": case["claim"],
            "source_id": case["source_id"],
            "source_title": source["title"],
            "source_ids": support_source_ids,
            "support_source_ids": support_source_ids,
            "multi_document": len(support_source_ids) > 1,
            "source_boundary": case["boundary"],
            "relation": case["relation"],
            "passages": passages,
            "n_support_passages": len(support_refs),
            "n_distractor_passages": 0,
            "expected_verdict": verdict,
            "derivation": derivation,
        }
        for optional in ("variant_group", "named_gaps", "claimed_material_is_a_named_gap"):
            if optional in case:
                entry[optional] = case[optional]
        if case["relation"] in {"absent_from", "unaddressed"}:
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
        "corpus_id": "fresh-blind-constructed-v0.1",
        "schema_version": "cal-construction-gold-v2",
        "label": (
            "By-construction DEV twin of the 50-item fresh-blind packet. Verdicts are "
            "derived from the stipulated construction, never coded by a rater. Not "
            "validation, not a confirmatory gate, not an accuracy claim."
        ),
        "stipulations": [
            "The passages listed for a case are the entire world for that case.",
            "relation=unaddressed is an object-level claim the passages do not address "
            "(the starved-cell analogue). It is not a source-coverage claim.",
            "source_boundary=exhaustive makes claims about what the source does not say "
            "decidable; it does not settle object-level claims the source is silent on.",
            "This corpus does not recode the sealed 2026-07-24 human gold.",
        ],
        "n_cases": len(built),
        "by_register": {
            r: sum(1 for c in built if c["register"] == r)
            for r in ("pharma_regulatory", "plain_narrative")
        },
        "boundary_distribution": {
            b: sum(1 for c in built if c["source_boundary"] == b)
            for b in ("bounded", "exhaustive", "named_missing_material")
        },
        "relation_distribution": {
            r: sum(1 for c in built if c["relation"] == r)
            for r in sorted({c["relation"] for c in built})
        },
        "variant_groups": groups,
        "n_multi_document": sum(1 for c in built if c["multi_document"]),
        "n_with_distractors": 0,
        "cases": built,
    }


def _describe_groups(built: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
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
        axis = "source_boundary" if len(boundaries) > 1 else "distractors"
        group["axis"] = axis
        group["expectation"] = DEFAULT_EXPECTATION[axis]
        group["gold_verdicts"] = {m["case_id"]: m["expected_verdict"] for m in members}
        group["n_distinct_gold_verdicts"] = len({m["expected_verdict"] for m in members})
        group["varies"] = sorted(boundaries)
        _ = declared
    return groups


def validate(corpus: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    seen: set[str] = set()
    declared = {c["case_id"]: c for c in CASES}

    if corpus["n_cases"] != 50:
        problems.append(f"n_cases is {corpus['n_cases']}, want 50")
    if corpus["by_register"].get("pharma_regulatory") != 25:
        problems.append(f"pharma register is {corpus['by_register']}, want 25")
    if corpus["by_register"].get("plain_narrative") != 25:
        problems.append(f"narrative register is {corpus['by_register']}, want 25")

    for case in corpus["cases"]:
        cid = case["case_id"]
        if cid in seen:
            problems.append(f"{cid}: duplicate case_id")
        seen.add(cid)

        verdict, derivation = derive_twin_verdict(
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
        if "gold_coder" in case or "human_verdict" in case:
            problems.append(f"{cid}: rater field present — gold must be derived only")

        for passage in case["passages"]:
            src, _, pid = passage["passage_id"].partition("#")
            if passage["text"] != _passage_text(src, pid):
                problems.append(f"{cid}: passage {passage['passage_id']} is not verbatim")

        bundle = " ".join(p["text"].lower() for p in case["passages"])

        if case["source_boundary"] == "exhaustive":
            held = {p["passage_id"] for p in case["passages"]}
            for src in case["source_ids"]:
                for pid, _ in SOURCES[src]["passages"]:
                    if f"{src}#{pid}" not in held:
                        problems.append(
                            f"{cid}: declared exhaustive but bundle omits {src}#{pid}"
                        )

        if case["relation"] in {"absent_from", "unaddressed"}:
            term = case["claimed_absent_term"].lower()
            if term in bundle:
                problems.append(
                    f"{cid}: bundle is not silent on the claimed material — it contains {term!r}"
                )
            # unaddressed is an object-level claim about the missing material, so
            # the distinctive term must appear in the claim. absent_from is a
            # source-coverage claim; the silent term may be a proxy (e.g. "months"
            # for "fixed numeric interval") the way construction gold uses it.
            if case["relation"] == "unaddressed" and term not in case["claim_text"].lower():
                problems.append(f"{cid}: absent term {term!r} is not in the claim")

        if case["relation"] == "restates" and len(case["passages"]) < 1:
            problems.append(f"{cid}: restates with no passages")

    for cid in declared:
        if cid not in seen:
            problems.append(f"{cid}: declared but not built")
    return problems


def main() -> None:
    corpus = build()
    problems = validate(corpus)
    OUT.mkdir(parents=True, exist_ok=True)
    body = json.dumps(corpus, indent=2, sort_keys=True) + "\n"
    (OUT / "corpus.json").write_text(body, encoding="utf-8")
    gold = {
        "gold_version": "fresh-blind-constructed-v0.1",
        "derived_from": "scripts/build_fresh_blind_constructed.py::derive_twin_verdict",
        "note": "Regenerate rather than trust. No rater produced these labels.",
        "claims": [
            {
                "claim_id": c["claim_id"],
                "gold_verdict": c["expected_verdict"],
                "register": c["register"],
                "relation": c["relation"],
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
    print(f"registers        : {corpus['by_register']}")
    print(f"boundaries       : {corpus['boundary_distribution']}")
    print(f"relations        : {corpus['relation_distribution']}")
    print(f"corpus sha256    : {digest[:16]}")
    verdicts: dict[str, int] = {}
    for c in corpus["cases"]:
        verdicts[c["expected_verdict"]] = verdicts.get(c["expected_verdict"], 0) + 1
    print(f"derived verdicts : {verdicts}")
    if problems:
        print(f"\nVALIDATION FAILED ({len(problems)}):")
        for p in problems:
            print(f"  - {p}")
        raise SystemExit(1)
    print("\nvalidation: all checks passed")
    print(f"wrote {OUT}/corpus.json and gold.json")


if __name__ == "__main__":
    main()
