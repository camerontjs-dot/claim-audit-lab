"""Independent P2 contamination judge via the Cursor CLI (cursor-agent).

Judge defaults to composer-2.5 (Cursor's Composer, on Cursor credits) — a THIRD
surface off both Antigravity pools (Gemini generation + Claude/GPT P2), so it
conserves Opus/Claude entirely. Cross-family independent from the Gemini
generator. Runs in an isolated scratch cwd (cursor-agent is an agent with tool
access; --trust + a throwaway dir contains it). No CAL inference.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

SCREEN = Path(__file__).resolve().parent / "slg_scaled_screen.py"
# Throwaway cwd that contains the agent (see the module docstring). Derived at
# run time so it carries no authoring machine's paths; override with
# CAL_P2_WORKDIR to place it somewhere specific.
WORKDIR = Path(
    os.environ.get("CAL_P2_WORKDIR") or Path(tempfile.gettempdir()) / "cal-p2-cursor-work"
)


def judge_cell(cell: Path, model: str, timeout: int, attempts: int) -> dict:
    tmpl = (cell / "p2-prompt.txt").read_text()
    body = (cell / "raw_response.txt").read_text().strip()
    prompt = tmpl.replace("{PASTE THE EXACT GENERATED TITLE + BODY HERE}", body)
    prompt += ("\n\nIMPORTANT: You have no tools in this session. Do not run commands, call "
               "tools, read, or write files. Output ONLY the JSON object described above.")
    WORKDIR.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, "NO_OPEN_BROWSER": "1"}
    out, err = "", ""
    for _ in range(attempts):
        try:
            p = subprocess.run(
                ["cursor-agent", "-p", prompt, "--model", model, "--output-format", "text", "--trust"],
                capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=timeout,
                cwd=str(WORKDIR), env=env)
        except subprocess.TimeoutExpired:
            return {"status": "timeout"}
        out, err = p.stdout.strip(), p.stderr.strip()
        if "quota" in err.lower() or "credit" in err.lower() or "limit" in err.lower():
            return {"status": "quota_blocked", "stderr": err[:200]}
        if out:
            break
    if not out:
        return {"status": "empty", "stderr": err[:200]}
    (cell / "p2-response.json").write_text(out)
    rec = {"schema_version": "cal-scaled-corpus-p2-record-v1", "p2_judge_surface": "cursor-cli",
           "p2_judge_model": model, "independent_context": True,
           "independent_of_generator": "generator=Gemini via Antigravity; judge=%s via Cursor (cross-family)" % model,
           "p2_response_sha256": "sha256:" + hashlib.sha256(out.encode()).hexdigest()}
    (cell / "p2-record.json").write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n")
    v = subprocess.run([sys.executable, str(SCREEN), "--cell", str(cell)], capture_output=True, text=True)
    final = json.loads(v.stdout).get("final_status") if v.stdout.strip() else "validator_error"
    return {"status": "p2_done", "final_status": final}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cells", nargs="+", type=Path, required=True)
    ap.add_argument("--model", default="composer-2.5")
    ap.add_argument("--timeout", type=int, default=360)
    ap.add_argument("--attempts", type=int, default=3)
    args = ap.parse_args()
    for cell in args.cells:
        info = judge_cell(cell, args.model, args.timeout, args.attempts)
        print(json.dumps({"cell": cell.parent.name + "/" + cell.name, **info}), flush=True)
        if info.get("status") == "quota_blocked":
            print(json.dumps({"note": "Cursor credits exhausted — stopping"}), flush=True)
            break


if __name__ == "__main__":
    main()
