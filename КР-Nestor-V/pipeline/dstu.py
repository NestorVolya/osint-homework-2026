"""ДСТУ 8302:2015 citation formatter for electronic resources."""

from datetime import date


def dstu_cite(source: dict, access_date: str | None = None) -> str:
    """Return ДСТУ 8302:2015 formatted citation for a web source."""
    today = access_date or date.today().strftime("%d.%m.%Y")
    title = (source.get("title") or "").strip() or "Без назви"
    url = (source.get("url") or "").strip()
    date_raw = (source.get("date_raw") or "").strip()

    year = ""
    if date_raw:
        # extract 4-digit year if present
        import re
        m = re.search(r"\b(20\d\d|19\d\d)\b", date_raw)
        if m:
            year = m.group(1) + ". "

    url_part = f"URL: {url}" if url else ""
    access = f"(дата звернення: {today})"

    parts = [f"{title} [Електронний ресурс]."]
    if year:
        parts.append(year.rstrip())
    if url_part:
        parts.append(url_part)
    parts.append(access)

    return " ".join(parts)
