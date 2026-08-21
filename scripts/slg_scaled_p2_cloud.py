"""Independent P2 contamination judge in the CLOUD via the Antigravity CLI.

Judge defaults to Claude Opus 4.6 (Thinking) — cross-family independent from the
Gemini generator, and uses the Claude/GPT quota pool (separate from Gemini
generation). Uses ZERO local memory, unlike the qwen3:14b local judge that
crushed the host. Substitutes the cell's filler into p2-prompt.txt, calls agy,
saves p2-response.json + p2-record.json, then re-runs the screen validator.
No CAL inference.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

SCREEN = Path(__file__).resolve().parent / "slg_scaled_screen.py"


def judge_cell(cell: Path, model: str, timeout: int, attempts: int) -> dict:
    tmpl = (cell / "p2-prompt.txt").read_text()
    body = (cell / "raw_response.txt").read_text().strip()
    prompt = tmpl.replace("{PASTE THE EXACT GENERATED TITLE + BODY HERE}", body)
    prompt += ("\n\nIMPORTANT: You have no tools in this session. Do not run commands "
               "or call tools. Output ONLY the JSON object described above.")
    out, err = "", ""
    for _ in range(attempts):
        try:
            p = subprocess.run(["agy", "-p", prompt, "--model", model],
                               capture_output=True, text=True, stdin=subprocess.DEVNULL,
                               timeout=timeout)
        except subprocess.TimeoutExpired:
            return {"status": "timeout"}
        out, err = p.stdout.strip(), p.stderr.strip()
        if "quota" in err.lower():
            return {"status": "quota_blocked", "stderr": err[:200]}
        if out:
            break
    if not out:
        return {"status": "empty", "stderr": err[:200]}
    (cell / "p2-response.json").write_text(out)
    rec = {"schema_version": "cal-scaled-corpus-p2-record-v1", "p2_judge_surface": "antigravity-cloud",
           "p2_judge_model": model, "independent_context": True,
           "independent_of_generator": "generator=Gemini via Antigravity; judge=%s (cross-family)" % model,
           "p2_response_sha256": "sha256:" + hashlib.sha256(out.encode()).hexdigest()}
    (cell / "p2-record.json").write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n")
    v = subprocess.run([sys.executable, str(SCREEN), "--cell", str(cell)], capture_output=True, text=True)
    final = json.loads(v.stdout).get("final_status") if v.stdout.strip() else "validator_error"
    return {"status": "p2_done", "final_status": final}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cells", nargs="+", type=Path, required=True)
    ap.add_argument("--model", default="Claude Sonnet 4.6 (Thinking)")  # conserve Opus; same pool, cheaper, cross-family
    ap.add_argument("--timeout", type=int, default=360)
    ap.add_argument("--attempts", type=int, default=3)
    args = ap.parse_args()
    for cell in args.cells:
        info = judge_cell(cell, args.model, args.timeout, args.attempts)
        label = cell.parent.name + "/" + cell.name
        print(json.dumps({"cell": label, **info}), flush=True)
        if info.get("status") == "quota_blocked":
            print(json.dumps({"note": "Claude/GPT pool exhausted — stopping"}), flush=True)
            break


if __name__ == "__main__":
    main()
