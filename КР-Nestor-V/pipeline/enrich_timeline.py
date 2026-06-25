"""
Timeline enrichment: sources → events table.

Steps:
  1. Read sources for actor
  2. Normalize date_raw → ISO date string (YYYY / YYYY-MM / YYYY-MM-DD)
  3. Map date → war_context label
  4. Extract location hint from text (regex, best-effort)
  5. Insert events into db
"""

import re
import uuid
from loguru import logger

from pipeline.storage.db import Database

# Ukraine war context — sorted ascending by date prefix
WAR_CONTEXT_PERIODS = [
    ("2022-02-24", "повномасштабне вторгнення"),
    ("2022-03",    "перший місяць вторгнення"),
    ("2022-04",    "відступ з Київщини / Маріуполь"),
    ("2022-06",    "Донбаська кампанія"),
    ("2022-09",    "Харківський контрнаступ"),
    ("2022-10",    "ракетні удари по інфраструктурі"),
    ("2022-11",    "звільнення Херсона"),
    ("2023-01",    "Бахмут / зимова кампанія"),
    ("2023-06",    "контрнаступ ЗСУ"),
    ("2023-10",    "позиційна боротьба"),
    ("2024-01",    "2024 — позиційна фаза"),
    ("2024-10",    "курський напрямок"),
    ("2025-01",    "2025 — продовження"),
]
WAR_CONTEXT_BEFORE = "до повномасштабного вторгнення"

# city → country lookup for quick location extraction
_CITY_COUNTRY = {
    "київ": ("Київ", "Україна"),
    "kyiv": ("Kyiv", "Ukraine"),
    "харків": ("Харків", "Україна"),
    "kharkiv": ("Kharkiv", "Ukraine"),
    "lviv": ("Lviv", "Ukraine"),
    "львів": ("Львів", "Україна"),
    "одеса": ("Одеса", "Україна"),
    "odesa": ("Odesa", "Ukraine"),
    "dnipro": ("Дніпро", "Україна"),
    "дніпро": ("Дніпро", "Україна"),
    "запоріжжя": ("Запоріжжя", "Україна"),
    "черкаси": ("Черкаси", "Україна"),
    "cherkasy": ("Cherkasy", "Ukraine"),
    "rome": ("Rome", "Italy"),
    "рим": ("Рим", "Італія"),
    "warsaw": ("Warsaw", "Poland"),
    "варшава": ("Варшава", "Польща"),
    "berlin": ("Berlin", "Germany"),
    "берлін": ("Берлін", "Німеччина"),
    "paris": ("Paris", "France"),
    "париж": ("Париж", "Франція"),
    "new york": ("New York", "USA"),
    "london": ("London", "UK"),
    "лондон": ("Лондон", "Велика Британія"),
}


def get_war_context(date_str: str) -> str:
    if not date_str:
        return ""
    label = WAR_CONTEXT_BEFORE
    for prefix, ctx in WAR_CONTEXT_PERIODS:
        if date_str >= prefix:
            label = ctx
        else:
            break
    return label


def normalize_date(raw: str) -> str:
    if not raw:
        return ""
    raw = raw.strip()
    # ISO 8601 with time: 2022-05-26T08:40:00.000Z → 2022-05-26
    m = re.match(r"(\d{4}-\d{2}-\d{2})T", raw)
    if m:
        return m.group(1)
    # YYYY-MM-DD
    if re.match(r"\d{4}-\d{2}-\d{2}$", raw):
        return raw
    # YYYY-MM
    if re.match(r"\d{4}-\d{2}$", raw):
        return raw
    # YYYY
    if re.match(r"\d{4}$", raw):
        return raw
    # DD.MM.YYYY
    m = re.match(r"(\d{2})\.(\d{2})\.(\d{4})", raw)
    if m:
        return f"{m.group(3)}-{m.group(2)}-{m.group(1)}"
    return ""


def _extract_location(text: str, db: Database) -> str | None:
    if not text:
        return None
    text_lower = text.lower()
    for keyword, (city, country) in _CITY_COUNTRY.items():
        if keyword in text_lower:
            loc_id = f"loc_{keyword.replace(' ', '_')}"
            db.upsert_location(loc_id, city, country, keyword)
            return loc_id
    return None


def run_enrich_timeline(actor_id: str, db: Database) -> list[dict]:
    sources = db.get_sources(actor_id)
    events = []
    skipped_no_date = 0

    for src in sources:
        date = normalize_date(src.get("date_raw") or "")
        if not date:
            skipped_no_date += 1
            continue

        war_ctx = get_war_context(date)
        location_id = _extract_location(src.get("text") or "", db)

        event_id = f"evt_{src['source_id']}"
        title = (src.get("title") or "Untitled")[:200]
        description = None

        db.insert_event(
            event_id=event_id,
            actor_id=actor_id,
            date=date,
            title=title,
            description=description,
            war_context=war_ctx,
            location_id=location_id,
            source_id=src["source_id"],
        )
        events.append({
            "event_id": event_id,
            "date": date,
            "war_context": war_ctx,
            "title": title,
            "location_id": location_id,
        })
        logger.info(f"[timeline] {date} [{war_ctx[:20]}] {title[:60]}")

    logger.info(
        f"[timeline] events: {len(events)} created, {skipped_no_date} skipped (no date)"
    )
    return events
