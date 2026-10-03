"""Download the frozen source pool. This file must not import CAL."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from email import message_from_string
from pathlib import Path

ROOT = Path(__file__).resolve().parent
POOL = json.loads((ROOT / "SOURCE_POOL.json").read_text(encoding="utf-8"))
RAW = ROOT / "raw"
UA = "Mozilla/5.0 (compatible; CAL-pressure-custody/1.0; research)"


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    rows = []
    for source in POOL["sources"]:
        source_id = source["source_id"]
        body_path = RAW / f"{source_id}.body"
        header_path = RAW / f"{source_id}.headers"
        started = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        command = [
            "curl",
            "-sS",
            "-L",
            "--retry",
            "2",
            "--retry-delay",
            "1",
            "--max-time",
            "90",
            "-A",
            UA,
            "-D",
            str(header_path),
            "-o",
            str(body_path),
            "-w",
            "%{http_code} %{content_type} %{url_effective}",
            source["url"],
        ]
        completed = subprocess.run(command, capture_output=True, text=True)
        finished = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        body = body_path.read_bytes() if body_path.exists() else b""
        headers = header_path.read_text(encoding="utf-8", errors="replace") if header_path.exists() else ""
        status = None
        media = None
        final_url = None
        if completed.stdout.strip():
            parts = completed.stdout.strip().split(" ", 2)
            status = int(parts[0]) if parts and parts[0].isdigit() else None
            media = parts[1] if len(parts) > 1 else None
            final_url = parts[2] if len(parts) > 2 else None
        # The last HTTP status in the header dump is the followed response.
        blocks = [block for block in headers.split("\r\n\r\n") if block.strip()]
        if blocks:
            parsed = message_from_string(blocks[-1] if blocks[-1].lower().startswith("http/") else "\n".join(blocks[-1].splitlines()))
            if parsed.get_content_type():
                media = media or parsed.get_content_type()
        rows.append(
            {
                "source_id": source_id,
                "title": source["title"],
                "publisher": source["publisher"],
                "requested_url": source["url"],
                "final_url": final_url,
                "started_at_utc": started,
                "finished_at_utc": finished,
                "http_status": status,
                "media_type": media,
                "raw_sha256": _sha256(body),
                "raw_bytes": len(body),
                "body_name": body_path.name,
                "curl_returncode": completed.returncode,
                "curl_stderr": completed.stderr.strip()[:500],
                "retrieval": "ok" if completed.returncode == 0 and status == 200 and body else "failed",
            }
        )
        print(source_id, rows[-1]["retrieval"], status, len(body), rows[-1]["raw_sha256"][:12])
    (ROOT / "RETRIEVAL.json").write_text(json.dumps({"schema": "cal-v1-pressure-retrieval-rc0", "sources": rows}, indent=2) + "\n")


if __name__ == "__main__":
    main()
