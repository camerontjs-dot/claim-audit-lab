"""Download the preregistered pool and freeze bytes before claim selection.

This script does not write claims or labels. It records retrieval, extraction,
and the hash split.
"""

from __future__ import annotations

import hashlib
import html
import json
import subprocess
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "sources" / "raw"
TEXT = ROOT / "sources" / "text"
WINDOW_LIMIT = 80000


class _Text(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._skip = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "noscript"}:
            self._skip += 1
        if tag in {"p", "div", "li", "tr", "h1", "h2", "h3", "h4", "br"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"} and self._skip:
            self._skip -= 1
        if tag in {"p", "div", "li", "tr", "h1", "h2", "h3", "h4"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._skip == 0:
            self.parts.append(data)


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _html_text(raw: bytes) -> str:
    parser = _Text()
    parser.feed(raw.decode("utf-8", "replace"))
    lines = [" ".join(html.unescape(part).split()) for part in "".join(parser.parts).splitlines()]
    return "\n".join(line for line in lines if line)


def _pdf_text(path: Path) -> str:
    completed = subprocess.run(
        ["pdftotext", "-layout", "-enc", "UTF-8", str(path), "-"],
        check=False,
        capture_output=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.decode("utf-8", "replace")[:400])
    return completed.stdout.decode("utf-8", "replace")


def _download(url: str) -> tuple[int, str, bytes, str]:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "cal-research-source-freeze/1.0"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        status = int(response.status)
        final_url = response.geturl()
        body = response.read()
        media = str(response.headers.get("Content-Type", ""))
    return status, final_url if final_url else url, body, media


def main() -> None:
    pool = json.loads((ROOT / "SOURCE_POOL.json").read_text(encoding="utf-8"))
    RAW.mkdir(parents=True, exist_ok=True)
    TEXT.mkdir(parents=True, exist_ok=True)
    records = []
    for source in pool["sources"]:
        source_id = source["source_id"]
        record = {
            "source_id": source_id,
            "title": source["title"],
            "requested_url": source["url"],
            "status": "retrieval_failed",
        }
        try:
            status, final_url, body, media = _download(source["url"])
        except Exception as exc:
            record["error"] = type(exc).__name__
            record["detail"] = str(exc)[:300]
            records.append(record)
            continue
        raw_path = RAW / f"{source_id}.bin"
        raw_path.write_bytes(body)
        record.update(
            {
                "http_status": status,
                "final_url": final_url,
                "media_type": media,
                "raw_bytes": len(body),
                "raw_sha256": _sha(body),
                "raw_path": f"sources/raw/{source_id}.bin",
            }
        )
        if status != 200 or not body:
            record["status"] = "retrieval_failed"
            records.append(record)
            continue
        try:
            if "pdf" in media.lower() or source["url"].lower().endswith(".pdf"):
                extracted = _pdf_text(raw_path)
                method = "pdftotext-layout-utf8"
            else:
                extracted = _html_text(body)
                method = "html-strip-script-style-noscript"
        except Exception as exc:
            record["status"] = "extraction_failed"
            record["error"] = type(exc).__name__
            record["detail"] = str(exc)[:300]
            records.append(record)
            continue
        truncated = len(extracted) > WINDOW_LIMIT
        window = extracted[:WINDOW_LIMIT]
        text_path = TEXT / f"{source_id}.txt"
        text_path.write_text(window, encoding="utf-8")
        record.update(
            {
                "status": "frozen" if window.strip() else "extraction_failed",
                "extraction_method": method,
                "extraction_characters": len(extracted),
                "window_characters": len(window),
                "truncated": truncated,
                "window_sha256": _sha(window.encode("utf-8")),
                "text_path": f"sources/text/{source_id}.txt",
            }
        )
        records.append(record)

    usable = sorted(
        (row for row in records if row["status"] == "frozen"),
        key=lambda row: row["raw_sha256"],
    )
    midpoint = (len(usable) + 1) // 2
    for index, row in enumerate(usable):
        row["partition"] = "calibration" if index < midpoint else "held_out"
    for row in records:
        row.setdefault("partition", "unpartitioned")

    manifest = {
        "schema": "cal-v1-independent-judges-natural-rc1-source-freeze",
        "pool_sha256": _sha((ROOT / "SOURCE_POOL.json").read_bytes()),
        "protocol_sha256": _sha((ROOT / "PROTOCOL.md").read_bytes()),
        "sources": records,
        "calibration_source_ids": [row["source_id"] for row in usable if row["partition"] == "calibration"],
        "held_out_source_ids": [row["source_id"] for row in usable if row["partition"] == "held_out"],
        "unpartitioned_source_ids": [row["source_id"] for row in records if row["partition"] == "unpartitioned"],
    }
    (ROOT / "SOURCE_FREEZE.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "frozen": manifest["calibration_source_ids"],
        "held_out": manifest["held_out_source_ids"],
        "unpartitioned": manifest["unpartitioned_source_ids"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
