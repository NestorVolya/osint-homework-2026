"""
normalize — читає data/raw/*.json, очищає і зберігає в data/normalized/.
"""

import json
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("normalize")


def _clean_content(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"!\[.*?\]\(.*?\)", "", text)  # strip markdown images
    return text.strip()


def _normalize_date(raw: str) -> str:
    if not raw:
        return ""
    # Already ISO
    if re.match(r"\d{4}-\d{2}-\d{2}", raw):
        return raw[:19] if len(raw) > 19 else raw
    # Try common Ukrainian formats: "28 квітня 2026"
    months = {
        "січня": "01", "лютого": "02", "березня": "03", "квітня": "04",
        "травня": "05", "червня": "06", "липня": "07", "серпня": "08",
        "вересня": "09", "жовтня": "10", "листопада": "11", "грудня": "12",
    }
    m = re.search(r"(\d{1,2})\s+(\w+)\s+(\d{4})", raw.lower())
    if m:
        day, month_name, year = m.group(1), m.group(2), m.group(3)
        month = months.get(month_name)
        if month:
            return f"{year}-{month}-{day.zfill(2)}"
    return raw


def _filter_links(links: list[str]) -> list[str]:
    seen = set()
    result = []
    for link in links:
        parsed = urlparse(link)
        if config.TARGET_DOMAIN not in (parsed.netloc or ""):
            continue
        if link not in seen:
            seen.add(link)
            result.append(link)
    return result


def normalize_one(raw: dict) -> dict:
    content = _clean_content(raw.get("content", ""))
    meta = raw.get("metadata", {})
    date_raw = meta.get("date_raw", "")

    return {
        "url": raw.get("url", ""),
        "title": raw.get("title", "").strip(),
        "fetched_at": raw.get("fetched_at", ""),
        "source": raw.get("source", config.TARGET_DOMAIN),
        "content": content,
        "links": _filter_links(raw.get("links", [])),
        "word_count": len(content.split()),
        "normalized_at": datetime.now(timezone.utc).isoformat(),
        "author": meta.get("author", ""),
        "tags": meta.get("tags", []),
        "published_at": _normalize_date(date_raw),
        "worker": meta.get("worker", "html"),
    }


def run() -> None:
    config.NORMALIZED_DIR.mkdir(parents=True, exist_ok=True)

    raw_files = list(config.RAW_DIR.glob("*.json"))
    if not raw_files:
        log.warning("Немає файлів у %s", config.RAW_DIR)
        return

    log.info("Нормалізую %d файлів", len(raw_files))
    ok = 0

    for path in raw_files:
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            normalized = normalize_one(raw)

            out_path = config.NORMALIZED_DIR / path.name
            out_path.write_text(
                json.dumps(normalized, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            log.info("✓ %s → %d words", path.name, normalized["word_count"])
            ok += 1
        except Exception as exc:
            log.error("Помилка при обробці %s: %s", path.name, exc)

    log.info("Нормалізовано %d/%d файлів", ok, len(raw_files))


if __name__ == "__main__":
    run()
