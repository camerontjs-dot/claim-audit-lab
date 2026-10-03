"""Apply the frozen source window. This file must not import CAL."""

from __future__ import annotations

import html
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "raw"
WINDOW = 120_000

COMPARISON = re.compile(
    r"\b(higher|lower|greater|smaller|larger|fewer|less than|more than|compared with|"
    r"compared to|exceeded|outpaced|faster than|slower than|above|below|increased|decreased|"
    r"rose|fell|outnumbered|versus|percent)\b|\bthan\b",
    re.IGNORECASE,
)
TEMPORAL = re.compile(r"\b(before|after|prior to|following)\b", re.IGNORECASE)
MODAL = re.compile(r"\b(shall|must|should)\b", re.IGNORECASE)
SKIP_PHRASES = (
    "cookie",
    "privacy policy",
    "skip to main",
    "skip to content",
    "table of contents",
    "breadcrumb",
    "javascript",
    "sign up",
    "subscribe",
)


def _html_text(raw: bytes) -> str:
    text = raw.decode("utf-8", errors="replace")
    text = re.sub(r"(?is)<(script|style|noscript)\b.*?>.*?</\1>", " ", text)
    text = re.sub(r"(?is)<br\s*/?>", "\n", text)
    text = re.sub(r"(?is)</p>", "\n", text)
    text = re.sub(r"(?is)<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"[ \t]+", " ", text)
    return text


def _extract(source_id: str, media: str | None, body: Path) -> str:
    raw = body.read_bytes()
    pdf = (media or "").lower().startswith("application/pdf") or raw.startswith(b"%PDF")
    if pdf:
        pdftotext = shutil.which("pdftotext")
        if pdftotext is None:
            return ""
        destination = RAW / f"{source_id}.extract.txt"
        subprocess.run(
            [pdftotext, "-layout", "-enc", "UTF-8", str(body), str(destination)],
            check=False,
            capture_output=True,
            text=True,
        )
        return destination.read_text(encoding="utf-8", errors="replace") if destination.exists() else ""
    text = _html_text(raw)
    (RAW / f"{source_id}.extract.txt").write_text(text, encoding="utf-8")
    return text


def _skip_reason(sentence: str) -> str | None:
    lowered = sentence.casefold()
    if any(phrase in lowered for phrase in SKIP_PHRASES):
        return "navigation_or_banner"
    if "...." in sentence or sentence.count(".") > 12:
        return "contents_or_dotted_leader"
    if MODAL.search(sentence):
        return "modal_verb"
    if re.fullmatch(r"[\W\dA-Za-z]{0,40}", sentence) and re.search(r"\b\d{4}\b", sentence):
        return "header_date"
    return None


def _sentences(text: str) -> list[dict[str, object]]:
    window = text[:WINDOW]
    rows = []
    for index, sentence in enumerate(re.split(r"(?<=[.!?])\s+", window)):
        compact = re.sub(r"\s+", " ", sentence).strip()
        if not 80 <= len(compact) <= 700:
            continue
        reason = _skip_reason(compact)
        if reason is not None:
            continue
        cues = []
        if COMPARISON.search(compact):
            cues.append("comparison")
        if TEMPORAL.search(compact):
            cues.append("temporal")
        rows.append({"index": index, "cues": cues, "text": compact})
    return rows


def main() -> None:
    retrieval = json.loads((ROOT / "RETRIEVAL.json").read_text(encoding="utf-8"))
    sources = []
    for row in retrieval["sources"]:
        body = RAW / row["body_name"]
        if row["retrieval"] != "ok" or not body.exists():
            sources.append({**row, "sentences": [], "extraction": "unavailable"})
            continue
        text = _extract(row["source_id"], row.get("media_type"), body)
        sources.append(
            {
                "source_id": row["source_id"],
                "title": row["title"],
                "retrieval": row["retrieval"],
                "raw_sha256": row["raw_sha256"],
                "extract_chars": len(text),
                "window_chars": min(len(text), WINDOW),
                "sentences": _sentences(text),
            }
        )
    payload = {
        "schema": "cal-v1-pressure-selection-window-rc0",
        "rule": "SOURCE_POOL.json selection_rule",
        "sources": sources,
    }
    (ROOT / "SELECTION_WINDOW.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    for source in sources:
        flagged = [row for row in source.get("sentences", []) if row.get("cues")]
        print(source["source_id"], source.get("retrieval"), "flagged", len(flagged), "kept", len(source.get("sentences", [])))


if __name__ == "__main__":
    main()
