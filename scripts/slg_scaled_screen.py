"""Deterministic screen + P2 validation for free-prose Antigravity cells.

Reads a packet cell dir (case.json + raw_response.txt, optional p2-response.json)
and writes deterministic-screen.json + candidate-receipt.json + SHA256SUMS.
No CAL retrieval, entailment, or verdict — screening only.

Adaptation vs the sealed-scaffold screen (documented): free prose has no choice
markers, so the choice/slash residue check is dropped; only echoed XML-style
tags are treated as residue (a prompt-leak signal). Subject, banned-lemma,
proposition, paragraph-count, and word-band gates are unchanged.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from slg_scaled_antigravity_packet import (  # noqa: E402
    BANNED_LEMMAS,
    DOMAIN_PROPOSITIONS,
    DOMAIN_SUBJECTS,
    PLAIN_PROPOSITIONS,
    PLAIN_SUBJECTS,
    TIERS,
)

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
LANE_SETS = {
    "domain": (DOMAIN_SUBJECTS, DOMAIN_PROPOSITIONS),
    "plain": (PLAIN_SUBJECTS, PLAIN_PROPOSITIONS),
}


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9]+(?:[’'-][A-Za-z0-9]+)*", text.lower())


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def screen(
    raw: str,
    subjects: tuple[str, ...],
    propositions: tuple[str, ...],
    paragraphs: int,
    min_w: int,
    max_w: int,
) -> dict[str, Any]:
    blocks = [b.strip() for b in re.split(r"\n\s*\n", raw.strip()) if b.strip()]
    reasons: list[str] = []
    title = blocks[0] if blocks else ""
    paras = blocks[1:]
    body = "\n\n".join(paras)
    body_words = words(body)
    normalized = " ".join(body_words)

    subject_hits = [s for s in subjects if re.search(rf"\b{re.escape(s)}\b", normalized)]
    banned_hits = [
        lemma for lemma in BANNED_LEMMAS if re.search(rf"\b{BANNED_PATTERNS[lemma]}\b", normalized)
    ]
    proposition_hits = [p for p in propositions if " ".join(words(p)) in normalized]
    tag_residue = re.findall(r"<[^>]+>", raw)

    if not blocks:
        reasons.append("empty response")
    if len(paras) != paragraphs:
        reasons.append(f"paragraph count {len(paras)} != contract {paragraphs}")
    if any(not p for p in paras):
        reasons.append("empty paragraph")
    if not min_w <= len(body_words) <= max_w:
        reasons.append(f"body word count {len(body_words)} outside {min_w}-{max_w}")
    if subject_hits:
        reasons.append("forbidden subject hit")
    if banned_hits:
        reasons.append("banned outcome verb morphology hit")
    if proposition_hits:
        reasons.append("exact normalized proposition hit")
    if tag_residue:
        reasons.append("echoed tag residue")

    clean = not reasons
    return {
        "schema_version": "cal-scaled-corpus-freeprose-deterministic-screen-v1",
        "title": title,
        "paragraph_count": len(paras),
        "paragraph_count_ok": len(paras) == paragraphs,
        "body_word_count": len(body_words),
        "body_word_count_ok": min_w <= len(body_words) <= max_w,
        "forbidden_subject_hits": subject_hits,
        "banned_outcome_or_derivation_hits": banned_hits,
        "exact_or_normalized_proposition_hits": proposition_hits,
        "echoed_tag_residue": tag_residue,
        "admissible_to_independent_p2": clean,
        "decision": "continue_to_p2" if clean else "reject_deterministic_screen",
        "reasons": reasons,
    }


def parse_p2(text: str) -> dict[str, Any] | None:
    """Extract the JSON review object from a possibly noisy model response."""
    for candidate in (text, *re.findall(r"```(?:json)?\s*(.*?)```", text, re.S)):
        candidate = candidate.strip()
        try:
            return json.loads(candidate)
        except Exception:
            pass
    start, end = text.find("{"), text.rfind("}")
    if 0 <= start < end:
        try:
            return json.loads(text[start : end + 1])
        except Exception:
            return None
    return None


def validate_p2(payload: dict[str, Any] | None, n: int) -> tuple[bool, str]:
    if not isinstance(payload, dict):
        return False, "p2 unparseable"
    reviews = payload.get("reviews")
    expected = [f"P{i:02d}" for i in range(1, n + 1)]
    if not isinstance(reviews, list) or [r.get("id") for r in reviews] != expected:
        return False, "p2 id set mismatch"
    if payload.get("overall") != "clean":
        return False, f"p2 overall={payload.get('overall')}"
    non_unrelated = [r.get("id") for r in reviews if r.get("relation") != "unrelated"]
    if non_unrelated:
        return False, f"p2 non-unrelated: {non_unrelated}"
    return True, "p2 clean"


def write_manifest(root: Path) -> None:
    manifest = root / "SHA256SUMS"
    entries = sorted(
        (sha256_file(p), p.relative_to(root))
        for p in root.rglob("*")
        if p.is_file() and p.name != "SHA256SUMS"
    )
    manifest.write_text("".join(f"{h}  {rel}\n" for h, rel in entries), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cell", type=Path, required=True)
    args = ap.parse_args()
    cell = args.cell
    case = json.loads((cell / "case.json").read_text(encoding="utf-8"))
    tier = TIERS[case["tier"]]
    subjects, propositions = LANE_SETS[case["lane"]]

    raw = (cell / "raw_response.txt").read_text(encoding="utf-8")
    result = screen(
        raw, subjects, propositions, tier["paragraphs"], tier["min_words"], tier["max_words"]
    )
    result["raw_response_sha256"] = "sha256:" + sha256_file(cell / "raw_response.txt")
    (cell / "deterministic-screen.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    p2_clean, p2_reason = False, "no p2 response present"
    p2_path = cell / "p2-response.json"
    if p2_path.exists():
        payload = parse_p2(p2_path.read_text(encoding="utf-8"))
        p2_clean, p2_reason = validate_p2(payload, len(propositions))

    final = (
        "screened_candidate_pending_cameron"
        if result["admissible_to_independent_p2"] and p2_clean
        else "rejected_or_incomplete"
    )
    receipt = {
        "schema_version": "cal-scaled-corpus-freeprose-candidate-receipt-v1",
        "cell_id": case["cell_id"],
        "lane": case["lane"],
        "world_id": case["world_id"],
        "tier": case["tier"],
        "genre": case["genre"],
        "generator_surface": case.get("generator_surface", "antigravity"),
        "preregistration": case.get("preregistration"),
        "preregistration_admitted": False,
        "raw_response_sha256": result["raw_response_sha256"],
        "deterministic_screen": result["decision"],
        "deterministic_reasons": result["reasons"],
        "p2_clean": p2_clean,
        "p2_reason": p2_reason,
        "final_status": final,
        "note": "DEV pre-admission candidate; not admitted, not CAL evidence.",
    }
    (cell / "candidate-receipt.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    write_manifest(cell)
    print(
        json.dumps(
            {
                "final_status": final,
                "screen": result["decision"],
                "screen_reasons": result["reasons"],
                "p2": p2_reason,
                "cal_inference_performed": False,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
