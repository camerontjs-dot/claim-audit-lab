"""Freeze and deterministically screen one T3 filler candidate; never run CAL."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

TITLE = "Suite B routine facilities record — week of 19 May"
PARAGRAPH_COUNT = 30
MIN_WORDS = 1400
MAX_WORDS = 1600
WORLD_ID = "SLG-01-d"
ATOM_ID = "SLG-01-d-a1"
FORBIDDEN_SUBJECTS = (
    "sample",
    "cabinet",
    "autoclave",
    "qualification",
    "logbook",
    "line clearance",
    "deviation",
    "excursion",
    "night shift",
    "analyst chen",
    "assay",
    "batch disposition",
    "disposition form",
    "verification record",
    "cold-chain",
    "shipment",
    "distribution center",
    "temperature range",
)
BANNED_LEMMAS = ("pass", "fail", "seal", "weigh", "store", "return", "ship", "approve", "verify")
BANNED_PATTERNS = {
    "pass": r"pass\w*",
    "fail": r"fail\w*",
    "seal": r"seal\w*",
    "weigh": r"weigh\w*",
    "store": r"stor\w*",
    "return": r"return\w*",
    "ship": r"ship\w*",
    "approve": r"approv\w*",
    "verify": r"verif\w*",
}
PROPOSITIONS = (
    "The retained sample is in cabinet A.",
    "The retained sample is not in cabinet A; it is in cabinet B.",
    "The retained sample was returned.",
    "The retained sample was returned before noon.",
    "The complete listed autoclave roster contains only A1, A2, and A3.",
    "Autoclave A1 passed the qualification check.",
    "Autoclave A2 passed the qualification check.",
    "Autoclave A2 failed the qualification check.",
    "Autoclave A3 passed the qualification check.",
    "Every listed autoclave passed the qualification check.",
    "The listed logbook entry covers line clearance only; it is not a deviation register.",
    "No temperature excursion was reported during the night shift.",
    "The stability sample was weighed.",
    "The stability sample was sealed.",
    "The stability sample was weighed and sealed.",
    "The stability sample was not sealed.",
    "The signed statement says Analyst Chen reported that the assay passed.",
    "Analyst Chen reported that the assay passed.",
    "The assay passed.",
    (
        "A batch disposition is sufficiently approved only when it has both a signed disposition "
        "form and an independent verification record."
    ),
    "The disposition form has a signature.",
    "The batch disposition has a signed disposition form.",
    "An independent verification record exists.",
    "The cold-chain shipment left the distribution center.",
    "The cold-chain shipment stayed within its temperature range.",
)


def render_target_blind_fixture() -> str:
    """Render one fixed, relation-neutral T3 candidate without CAL access."""
    subjects = ("calendar", "corridor", "glossary", "lamp", "label", "supply shelf")
    activities = ("lists", "records", "notes", "shows", "keeps", "sets out")
    details = (
        "weekday times and room labels",
        "plain wording for routine notices",
        "counts of blank paper forms",
        "locations for ordinary cleaning carts",
        "dates for attendance sessions",
        "spacing used in printed schedules",
    )
    paragraphs: list[str] = []
    for index in range(PARAGRAPH_COUNT):
        subject = subjects[index % len(subjects)]
        activity = activities[index % len(activities)]
        detail = details[index % len(details)]
        paragraphs.append(
            f"The weekly {subject} {activity} {detail}. Morning and afternoon rows use the "
            "same simple layout for each weekday. A routine facilities note gives the date, "
            "room, and time beside each entry. Staff use the page for ordinary planning, "
            "with no further narrative attached to the record."
        )
    return TITLE + "\n\n" + "\n\n".join(paragraphs) + "\n"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9]+(?:[’'-][A-Za-z0-9]+)*", text.lower())


def split_raw(raw: str) -> tuple[str, list[str]]:
    blocks = [block.strip() for block in re.split(r"\n\s*\n", raw.strip())]
    if len(blocks) != PARAGRAPH_COUNT + 1:
        raise ValueError(f"expected title plus {PARAGRAPH_COUNT} paragraphs; got {len(blocks)}")
    title, *paragraphs = blocks
    if title != TITLE:
        raise ValueError("title mismatch")
    if any(not paragraph for paragraph in paragraphs):
        raise ValueError("empty paragraph")
    return title, paragraphs


def screen(raw: str) -> dict[str, Any]:
    title, paragraphs = split_raw(raw)
    body = "\n\n".join(paragraphs)
    body_words = words(body)
    normalized = " ".join(body_words)
    subject_hits = [
        term for term in FORBIDDEN_SUBJECTS if re.search(rf"\b{re.escape(term)}\b", normalized)
    ]
    banned_hits = [
        lemma for lemma in BANNED_LEMMAS if re.search(rf"\b{BANNED_PATTERNS[lemma]}\b", normalized)
    ]
    proposition_hits = [p for p in PROPOSITIONS if " ".join(words(p)) in normalized]
    residue = re.findall(r"[()]|/|<[^>]+>", raw)
    reasons: list[str] = []
    if not MIN_WORDS <= len(body_words) <= MAX_WORDS:
        reasons.append("body word count outside contract")
    if subject_hits:
        reasons.append("forbidden subject hit")
    if banned_hits:
        reasons.append("banned outcome verb morphology hit")
    if proposition_hits:
        reasons.append("exact normalized proposition hit")
    if residue:
        reasons.append("choice or template residue")
    clean = not reasons
    return {
        "schema_version": "cal-scaled-corpus-t3-deterministic-screen-v1",
        "title_exact": title == TITLE,
        "paragraph_count": len(paragraphs),
        "paragraph_count_ok": len(paragraphs) == PARAGRAPH_COUNT,
        "body_word_count": len(body_words),
        "body_word_count_ok": MIN_WORDS <= len(body_words) <= MAX_WORDS,
        "choice_marker_residue": residue,
        "forbidden_subject_hits": subject_hits,
        "banned_outcome_or_derivation_hits": banned_hits,
        "exact_or_normalized_proposition_hits": proposition_hits,
        "admissible_to_independent_p2": clean,
        "decision": "continue_to_p2" if clean else "reject_deterministic_screen",
        "reasons": reasons,
    }


def validate_p2(payload: dict[str, Any]) -> bool:
    reviews = payload.get("reviews")
    expected = [f"P{i:02d}" for i in range(1, 26)]
    return (
        isinstance(reviews, list)
        and [row.get("id") for row in reviews] == expected
        and payload.get("overall") == "clean"
        and all(row.get("relation") == "unrelated" for row in reviews)
    )


def write_manifest(root: Path) -> None:
    manifest = root / "SHA256SUMS"
    entries = [
        (digest(path), path.relative_to(root))
        for path in sorted(root.rglob("*"))
        if path.is_file() and path != manifest
    ]
    manifest.write_text(
        "".join(f"{value}  {relative}\n" for value, relative in entries), encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--p2", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--render-target-blind", action="store_true")
    args = parser.parse_args()
    if args.out.exists():
        raise FileExistsError(f"refusing to overwrite candidate directory: {args.out}")
    raw = (
        render_target_blind_fixture()
        if args.render_target_blind
        else args.raw.read_text(encoding="utf-8")
    )
    result = screen(raw)
    args.out.mkdir(parents=True)
    (args.out / "raw_response.txt").write_text(raw, encoding="utf-8")
    result["raw_response_sha256"] = "sha256:" + digest(args.out / "raw_response.txt")
    (args.out / "deterministic-screen.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    p2_clean = False
    if args.p2:
        payload = json.loads(args.p2.read_text(encoding="utf-8"))
        (args.out / "p2-response.json").write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        p2_clean = validate_p2(payload)
    receipt = {
        "schema_version": "cal-scaled-corpus-t3-candidate-receipt-v1",
        "candidate_id": "slg01d-t3-easy-paperwork-generation-01",
        "lane": "A",
        "world_id": WORLD_ID,
        "atom_id": ATOM_ID,
        "tier": "T3",
        "difficulty": "easy",
        "genre": "pharmaceutical-paperwork",
        "raw_response_sha256": result["raw_response_sha256"],
        "deterministic_screen": result["decision"],
        "p2_clean": p2_clean,
        "final_status": "screened_candidate_pending_cameron"
        if result["admissible_to_independent_p2"] and p2_clean
        else "rejected_or_incomplete",
    }
    (args.out / "candidate-receipt.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    write_manifest(args.out)
    print(
        json.dumps(
            {"final_status": receipt["final_status"], "cal_inference_performed": False},
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
