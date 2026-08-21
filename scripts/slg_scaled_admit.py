"""Record Cameron's admission of Lane A scaled-corpus cells (his gate).

Admission is the human decision that a byte-exact filler candidate is accepted
into the corpus and becomes eligible for construction + a measured run (prereg
§7). This tool does NOT decide — it records a decision Cameron gave — and it is
fail-closed: before writing any admission it independently re-verifies each cell
(re-hash the filler == screening record, recompute the deterministic screen to
continue_to_p2, confirm the P2 'clean' verdict). Any cell that fails re-verify is
REFUSED, not admitted. Additive only: screening artifacts are left byte-exact; an
admission.json is layered per cell and a packet-level ledger is written.

Binds each admission to the exact raw_response_sha256 (prereg §7 "one exact raw
hash"). Performs NO CAL retrieval, entailment, or verdict.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from slg_scaled_antigravity_packet import TIERS, write_manifest  # noqa: E402
from slg_scaled_screen import LANE_SETS, parse_p2, screen, validate_p2  # noqa: E402

PREREG = "plans/2026-07-20-lane-a-antigravity-cloud-generation-superseding-preregistration.md"
GREEN = "screened_candidate_pending_cameron"


def sha_file(p: Path) -> str:
    return "sha256:" + hashlib.sha256(p.read_bytes()).hexdigest()


def write_once_or_same(path: Path, payload: dict) -> None:
    """Write an admission artifact once; exact repeats are idempotent."""
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if path.exists():
        if path.read_text(encoding="utf-8") != rendered:
            raise FileExistsError(f"refusing to overwrite admission history: {path}")
        return
    path.write_text(rendered, encoding="utf-8")


def reverify(cell: Path) -> tuple[bool, list[str], dict]:
    """Independent fail-closed re-verification of one screened cell."""
    prob: list[str] = []
    case = json.loads((cell / "case.json").read_text())
    tier = TIERS[case["tier"]]
    subjects, props = LANE_SETS[case["lane"]]

    receipt = json.loads((cell / "candidate-receipt.json").read_text())
    if receipt.get("final_status") != GREEN:
        prob.append(f"final_status={receipt.get('final_status')}")

    raw_path = cell / "raw_response.txt"
    raw_hash_now = sha_file(raw_path)
    if receipt.get("raw_response_sha256") != raw_hash_now:
        prob.append("raw hash drift vs screening receipt")

    ds = json.loads((cell / "deterministic-screen.json").read_text())
    if ds.get("raw_response_sha256") != raw_hash_now:
        prob.append("raw hash drift vs deterministic-screen")

    s = screen(
        raw_path.read_text(),
        subjects,
        props,
        tier["paragraphs"],
        tier["min_words"],
        tier["max_words"],
    )
    if s["decision"] != "continue_to_p2":
        prob.append(f"screen recompute={s['reasons']}")

    p2rec = json.loads((cell / "p2-record.json").read_text())
    surface, model = p2rec.get("p2_judge_surface", "?"), str(p2rec.get("p2_judge_model", "?"))
    if "gemini" in model.lower():
        prob.append(f"p2 not independent of generator: {model}")
    ok_p2, reason = validate_p2(parse_p2((cell / "p2-response.json").read_text()), len(props))
    if not ok_p2:
        prob.append(f"p2 revalidate={reason}")

    ctx = {
        "case": case,
        "raw_hash": raw_hash_now,
        "receipt_sha": sha_file(cell / "candidate-receipt.json"),
        "p2_surface": surface,
        "p2_model": model,
    }
    return (not prob), prob, ctx


def admit_cell(cell: Path, admitter: str, at: str, channel: str, ctx: dict) -> dict:
    case = ctx["case"]
    rec = {
        "schema_version": "cal-scaled-corpus-admission-v1",
        "cell_id": case["cell_id"],
        "lane": case["lane"],
        "world_id": case["world_id"],
        "tier": case["tier"],
        "genre": case["genre"],
        "admitted": True,
        "admitted_by": admitter,
        "admitted_at": at,
        "admission_channel": channel,
        "admission_basis": (
            "re-verified at admission: raw hash matches screening record, "
            "deterministic screen recomputes continue_to_p2, P2 verdict clean "
            "and independent of the Gemini generator"
        ),
        "raw_response_sha256": ctx["raw_hash"],  # the exact hash admitted (prereg §7)
        "candidate_receipt_sha256": ctx["receipt_sha"],
        "deterministic_screen": "continue_to_p2",
        "p2_verdict": "clean",
        "p2_surface": ctx["p2_surface"],
        "p2_model": ctx["p2_model"],
        "governing_preregistration": PREREG,
        "unlocks": "construction + measured-run per prereg §7 (Cameron gates each measured run)",
        "interpretation_boundary": (
            "prereg §9 — admits a DEV world×tier harness cell only; "
            "no dilution curve, knee, validation, fresh-gate, or GxP claim"
        ),
        "cal_inference_performed": False,
    }
    write_once_or_same(cell / "admission.json", rec)
    write_manifest(cell)  # refresh the per-cell manifest so admission.json is covered
    return rec


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--packet", type=Path, required=True)
    ap.add_argument("--admitter", default="cameron")
    ap.add_argument("--at", required=True, help="UTC ISO timestamp of the admission decision")
    ap.add_argument("--channel", default="in-session chat authorization via Claude Code operator")
    ap.add_argument("--session", default="")
    ap.add_argument("--apply", action="store_true", help="write records; without it, dry-run only")
    args = ap.parse_args()

    cells = sorted(args.packet.glob("*/SLG-*/T*"))
    admitted, refused = [], []
    for cell in cells:
        ok, prob, ctx = reverify(cell)
        label = f"{ctx['case']['lane']}/{cell.parent.name}/{cell.name}"
        if not ok:
            refused.append({"cell": label, "problems": prob})
            continue
        if args.apply:
            admit_cell(cell, args.admitter, args.at, args.channel, ctx)
        admitted.append({"cell": label, "raw_response_sha256": ctx["raw_hash"]})

    ledger = {
        "schema_version": "cal-scaled-corpus-admission-ledger-v1",
        "governing_preregistration": PREREG,
        "admitter": args.admitter,
        "admitted_at": args.at,
        "admission_channel": args.channel,
        "session": args.session,
        "reverification": (
            "each cell re-hashed + screen recomputed + P2 revalidated before admission"
        ),
        "corpus_scope": "Lane A scaled corpus — 36 domain + 36 plain (72 cells)",
        "admitted_count": len(admitted),
        "refused_count": len(refused),
        "refused": refused,
        "interpretation_boundary": "prereg §9; measured runs remain individually gated by Cameron",
        "cal_inference_performed": False,
        "cells": admitted,
    }
    if args.apply and not refused:
        led_dir = args.packet / "admission"
        led_dir.mkdir(exist_ok=True)
        write_once_or_same(led_dir / "admission-ledger-v1.json", ledger)
        write_manifest(args.packet)
    print(
        json.dumps(
            {
                "mode": "APPLIED" if (args.apply and not refused) else "DRY-RUN/HELD",
                "admitted": len(admitted),
                "refused": len(refused),
                "refused_detail": refused,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
