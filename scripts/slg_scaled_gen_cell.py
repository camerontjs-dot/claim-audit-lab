"""Generate one Lane A cell via the Antigravity CLI (agy), exclusion-aware.

Reads a packet cell (case.json + prompt.txt), appends the lane's word-avoidance
block (single-token subjects + banned verbs; propositions stay hidden), calls
`agy --print`, and preserves raw_response.txt + prompt_sent.txt +
generation-record.json. Detects quota/empty responses as non-candidates.
No CAL inference.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from slg_scaled_antigravity_packet import (  # noqa: E402
    BANNED_LEMMAS, DOMAIN_SUBJECTS, PLAIN_SUBJECTS,
)

LANE_SUBJECTS = {"domain": DOMAIN_SUBJECTS, "plain": PLAIN_SUBJECTS}


def avoidance_block(lane: str) -> str:
    subjects = LANE_SUBJECTS[lane]
    avoid = ", ".join(sorted(subjects))  # all subjects incl. multi-word (e.g. "line clearance")
    verbs = ", ".join(BANNED_LEMMAS)
    return (f"\n<avoidance>\n- Do NOT use any of these words or their variants: {avoid}.\n"
            f"- Do NOT use these verbs or their variants: {verbs}.\n"
            f"- CRITICAL: a ban blocks ANY word that STARTS WITH that stem. So also avoid, "
            f"among others: passage, passenger, passion, passport (pass-); failure (fail-); "
            f"storm, story, stories, storage, storefront, storyline (stor-); weight, weighty "
            f"(weigh-); sealed (seal-); shipment, shipping (ship-); returning, returned "
            f"(return-); approval (approv-); verification (verif-). Pick entirely different words.\n"
            f"- These are lexical bans only; write around them naturally.\n</avoidance>\n")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cell", type=Path, required=True)
    ap.add_argument("--model", default="Gemini 3.5 Flash (High)")
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--attempts", type=int, default=3, help="retries on empty/tool-denied response")
    args = ap.parse_args()
    cell = args.cell
    case = json.loads((cell / "case.json").read_text())
    base = (cell / "prompt.txt").read_text()
    prompt = base.replace("<task>", avoidance_block(case["lane"]) + "\n<task>", 1)
    prompt += ("\n\nIMPORTANT: You have no tools and no file access in this session. "
               "Do not run commands, call tools, or read/write files. Reply with only "
               "the requested document text.")
    (cell / "prompt_sent.txt").write_text(prompt)

    out, err = "", ""
    for attempt in range(1, args.attempts + 1):
        try:
            proc = subprocess.run(["agy", "-p", prompt, "--model", args.model],
                                  capture_output=True, text=True, stdin=subprocess.DEVNULL,
                                  timeout=args.timeout)
        except subprocess.TimeoutExpired:
            print(json.dumps({"cell": case["cell_id"], "status": "timeout"})); sys.exit(2)
        out, err = proc.stdout.strip(), proc.stderr.strip()
        if "quota" in err.lower():
            print(json.dumps({"cell": case["cell_id"], "status": "quota_blocked",
                              "stderr": err[:200]})); sys.exit(3)
        if out:
            break  # got a real response
    if not out:
        print(json.dumps({"cell": case["cell_id"], "status": "empty_regenerate",
                          "attempts": args.attempts, "stderr": err[:220]})); sys.exit(2)

    (cell / "raw_response.txt").write_text(out + "\n")
    rec = {
        "schema_version": "cal-scaled-corpus-antigravity-generation-record-v1",
        "cell_id": case["cell_id"], "lane": case["lane"], "world_id": case["world_id"],
        "tier": case["tier"], "generator_surface": "antigravity", "generator_cli": "agy 1.1.4",
        "generator_model": args.model, "generation_mode": "exclusion-aware-lexical",
        "preregistration": case.get("preregistration"), "preregistration_admitted": False,
        "operator": "claude-code-on-behalf-of-cameron",
        "prompt_sent_sha256": "sha256:" + hashlib.sha256(prompt.encode()).hexdigest(),
        "raw_response_sha256": "sha256:" + hashlib.sha256((out + "\n").encode()).hexdigest(),
        "note": "DEV pre-admission candidate; not admitted, not CAL evidence.",
    }
    (cell / "generation-record.json").write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"cell": case["cell_id"], "status": "generated", "bytes": len(out)}))


if __name__ == "__main__":
    main()
