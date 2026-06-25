"""
Account Discovery: sources → accounts table.

Strategy (four-pass):
  Pass 1 — mine social URLs already in sources table (free, instant)
  Pass 2 — Wayback CDX API for archived profile snapshots (optional, budgeted)
  Pass 3 — Sherlock-like: probe username candidates across top platforms
  Pass 4 — HIBP: check email seed in known data breaches (requires HIBP_API_KEY)
"""

import os
import re
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urlparse

import httpx
from loguru import logger

from pipeline.storage.db import Database
from pipeline.gates.budget_gate import BudgetTracker

# platform domain → canonical platform name
PLATFORM_DOMAINS = {
    "facebook.com": "facebook",
    "fb.com": "facebook",
    "instagram.com": "instagram",
    "twitter.com": "twitter",
    "x.com": "twitter",
    "t.me": "telegram",
    "telegram.me": "telegram",
    "youtube.com": "youtube",
    "youtu.be": "youtube",
    "linkedin.com": "linkedin",
    "tiktok.com": "tiktok",
    "vk.com": "vkontakte",
    "ok.ru": "odnoklassniki",
    "behance.net": "behance",
    "academia.edu": "academia",
    "researchgate.net": "researchgate",
}

# Wayback CDX API — query for known social profile patterns
WAYBACK_CDX = "https://web.archive.org/cdx/search/cdx"

# ── Sherlock-like platform probes ─────────────────────────────────────────────
# Only platforms that reliably return 404 for non-existent usernames.
# EXCLUDED (return HTTP 200 for non-existent → false positives with HEAD):
#   instagram, pinterest, tiktok, linkedin (redirect to login), telegram (ambiguous),
#   twitter/X (rate-limited, inconsistent), researchgate (URL format: First-Last with hyphen)
SHERLOCK_SITES = [
    ("github",      "https://github.com/{}"),
    ("reddit",      "https://www.reddit.com/user/{}"),
    ("medium",      "https://medium.com/@{}"),
    ("behance",     "https://www.behance.net/{}"),
    ("flickr",      "https://www.flickr.com/people/{}"),
    ("youtube",     "https://www.youtube.com/@{}"),
    ("vkontakte",   "https://vk.com/{}"),
    ("academia",    "https://independent.academia.edu/{}"),
    ("soundcloud",  "https://soundcloud.com/{}"),
    ("keybase",     "https://keybase.io/{}"),
]

_TRANSLIT_AD = {
    "а": "a", "б": "b", "в": "v", "г": "h", "ґ": "g", "д": "d",
    "е": "e", "є": "ie", "ж": "zh", "з": "z", "и": "y", "і": "i",
    "ї": "yi", "й": "i", "к": "k", "л": "l", "м": "m", "н": "n",
    "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "kh", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "shch",
    "ь": "", "ю": "yu", "я": "ya",
}


def _translit(name: str) -> str:
    return "".join(_TRANSLIT_AD.get(c, c) for c in name.lower())


def _username_candidates(seed: str, seed_type: str) -> list[str]:
    """Generate username candidates for Sherlock-like probing."""
    if seed_type == "nickname":
        return [seed.lstrip("@").lower()]
    if seed_type == "email":
        return [seed.split("@")[0].lower()]
    # fullname → transliterate + combine
    parts = seed.strip().split()
    en = [_translit(p) for p in parts]
    first = en[0] if en else ""
    last = en[-1] if en else ""
    candidates: set[str] = set()
    if first and last:
        candidates.update([
            f"{first}{last}", f"{first}_{last}", f"{first}.{last}",
            f"{last}{first}", f"{last}_{first}",
            f"{first[0]}{last}", f"{first[0]}_{last}",
        ])
    candidates.discard("")
    return [c for c in sorted(candidates) if 3 <= len(c) <= 30]


_SHERLOCK_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; OSINT-pipeline/1.0)"}


def _check_one_platform(platform: str, url: str) -> dict | None:
    """Single platform HTTP probe with HEAD→GET fallback. Returns dict or None."""
    try:
        resp = httpx.head(url, timeout=4, follow_redirects=True, headers=_SHERLOCK_HEADERS)
        if resp.status_code == 405:
            # Server rejects HEAD — retry with GET
            resp = httpx.get(url, timeout=4, follow_redirects=True, headers=_SHERLOCK_HEADERS)
        if resp.status_code == 200:
            return {"platform": platform, "url": url}
        return None
    except Exception:
        return None


def _sherlock_probe(seed: str, seed_type: str) -> list[dict]:
    """Pass 3: Sherlock-like parallel username probing across SHERLOCK_SITES."""
    candidates = _username_candidates(seed, seed_type)
    if not candidates:
        return []

    # Limit: top 2 candidates × all sites
    tasks: list[tuple[str, str, str]] = []  # (username, platform, url)
    for username in candidates[:2]:
        for platform, url_tpl in SHERLOCK_SITES:
            tasks.append((username, platform, url_tpl.format(username)))

    found: list[dict] = []
    with ThreadPoolExecutor(max_workers=10) as pool:
        futures = {
            pool.submit(_check_one_platform, platform, url): (username, platform, url)
            for username, platform, url in tasks
        }
        for future in as_completed(futures):
            username, platform, url = futures[future]
            try:
                result = future.result()
            except Exception:
                continue
            if result:
                found.append({
                    "platform": platform,
                    "handle": username,
                    "url": url,
                    "source": "sherlock",
                })
                logger.info(f"[sherlock] ✓ {platform} @{username} → {url[:70]}")
            else:
                logger.debug(f"[sherlock] – {platform}/{username}")

    logger.info(
        f"[sherlock] probed {len(tasks)} URLs ({len(candidates[:2])} candidates "
        f"× {len(SHERLOCK_SITES)} sites), found: {len(found)}"
    )
    return found


def _hibp_check(email: str) -> list[dict]:
    """Pass 4: HIBP v3 — check if email appears in known data breaches."""
    api_key = os.environ.get("HIBP_API_KEY", "")
    if not api_key:
        logger.debug("[hibp] HIBP_API_KEY not set, skipping")
        return []
    try:
        resp = httpx.get(
            f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}",
            headers={
                "hibp-api-key": api_key,
                "User-Agent": "actor-osint-pipeline",
            },
            params={"truncateResponse": "false"},
            timeout=10,
        )
        if resp.status_code == 404:
            logger.info(f"[hibp] {email} — no breaches found")
            return []
        if resp.status_code == 401:
            logger.warning("[hibp] invalid or missing API key")
            return []
        resp.raise_for_status()
        breaches = resp.json()
        logger.info(f"[hibp] {email} found in {len(breaches)} breach(es)")
        return [{"name": b["Name"], "date": b.get("BreachDate", ""), "domain": b.get("Domain", "")}
                for b in breaches]
    except httpx.HTTPStatusError as e:
        logger.warning(f"[hibp] HTTP {e.response.status_code}")
        return []
    except Exception as e:
        logger.warning(f"[hibp] error: {type(e).__name__}")
        return []


def _platform_from_url(url: str) -> str | None:
    try:
        host = urlparse(url).netloc.lstrip("www.")
        for domain, platform in PLATFORM_DOMAINS.items():
            if host == domain or host.endswith("." + domain):
                return platform
    except Exception:
        pass
    return None


_NON_PROFILE_PATHS = {
    # YouTube
    "watch", "shorts", "playlist", "results",
    # LinkedIn
    "pulse", "jobs", "company", "in", "feed", "search",
    # ResearchGate, Behance, etc.
    "publication", "article", "download", "view", "gallery",
    # Generic
    "posts", "videos", "stories", "events", "pages", "channel",
    "groups", "profile", "user",
}


def _handle_from_url(url: str, platform: str) -> str | None:
    try:
        parsed = urlparse(url)
        path = parsed.path.strip("/")
        if not path:
            return None
        parts = path.split("/")
        handle = parts[0]
        # YouTube: only channel/@handle paths are profiles
        if platform == "youtube":
            if handle in _NON_PROFILE_PATHS:
                return None
            if handle.startswith("@"):
                return handle
            # /channel/UCxxx or /@handle
            if len(parts) > 1 and parts[0] == "channel":
                return parts[1]
            return None  # video URLs are not profiles
        # LinkedIn: only /in/<handle> is a profile
        if platform == "linkedin":
            if len(parts) >= 2 and parts[0] == "in":
                return parts[1]
            return None  # pulse, jobs, company, etc. are not profiles

        # skip non-profile first segments — no fallback
        if handle in _NON_PROFILE_PATHS:
            return None

        return handle or None
    except Exception:
        return None


def _mine_sources(sources: list[dict], db: Database) -> list[dict]:
    found: dict[str, dict] = {}  # account_id → record

    for src in sources:
        url = src.get("url", "")
        platform = _platform_from_url(url)
        if not platform:
            continue

        handle = _handle_from_url(url, platform)
        if handle is None:
            continue  # non-profile URL (video, article, publication, etc.)

        account_id = f"{platform}_{handle}"

        if account_id in found:
            # add source reference
            found[account_id]["sources"].append(src["source_id"])
            continue

        found[account_id] = {
            "account_id": account_id,
            "platform": platform,
            "handle": handle,
            "url": url,
            "display_name": None,
            "bio": None,
            "first_seen": src.get("date_raw"),
            "last_seen": src.get("date_raw"),
            "sources": [src["source_id"]],
        }

    return list(found.values())


def _wayback_profile_snapshots(seed: str, platform: str,
                                budget: BudgetTracker) -> list[dict]:
    """Query Wayback CDX for archived profile pages on given platform."""
    domain = next((d for d, p in PLATFORM_DOMAINS.items() if p == platform), None)
    if not domain:
        return []
    try:
        budget.consume("wayback", 1)
    except Exception:
        return []

    url_pattern = f"*{domain}*{seed.replace(' ', '*')}*"
    try:
        resp = httpx.get(
            WAYBACK_CDX,
            params={
                "url": url_pattern,
                "output": "json",
                "fl": "timestamp,original",
                "limit": 5,
                "filter": "statuscode:200",
                "collapse": "urlkey",
            },
            timeout=8,
        )
        resp.raise_for_status()
        rows = resp.json()
        if not rows or len(rows) < 2:
            return []
        # first row is header
        return [{"timestamp": r[0], "url": r[1]} for r in rows[1:]]
    except Exception as e:
        logger.warning(f"[account_discovery] Wayback CDX error: {type(e).__name__}")
        return []


def run_account_discovery(
    seed: str,
    actor_id: str,
    seed_type: str,
    db: Database,
    run_dir: Path,
    budget: BudgetTracker,
) -> list[dict]:
    sources = db.get_sources(actor_id)

    # Pass 1: mine social URLs from collected sources
    accounts = _mine_sources(sources, db)

    # Pass 2: Wayback CDX for additional snapshots of known accounts
    for acc in accounts:
        if acc["platform"] in ("facebook", "instagram", "twitter", "telegram"):
            snapshots = _wayback_profile_snapshots(
                acc["handle"] or seed, acc["platform"], budget
            )
            for snap in snapshots:
                archived_url = f"https://web.archive.org/web/{snap['timestamp']}/{snap['url']}"
                ts = snap["timestamp"]
                date_str = f"{ts[:4]}-{ts[4:6]}-{ts[6:8]}" if len(ts) >= 8 else ts
                if not acc["first_seen"] or date_str < acc["first_seen"]:
                    acc["first_seen"] = date_str
                if not acc["last_seen"] or date_str > acc["last_seen"]:
                    acc["last_seen"] = date_str

    # Pass 3: Sherlock-like username probing
    sherlock_results = _sherlock_probe(seed, seed_type)
    seen_urls = {a["url"] for a in accounts}
    for sr in sherlock_results:
        if sr["url"] in seen_urls:
            continue
        account_id = f"{sr['platform']}_{sr['handle']}_sherlock"
        accounts.append({
            "account_id": account_id,
            "platform": sr["platform"],
            "handle": sr["handle"],
            "url": sr["url"],
            "display_name": "[Sherlock — потребує верифікації]",
            "bio": "Знайдено за збігом username. Може належати іншій особі.",
            "first_seen": None,
            "last_seen": None,
            "sources": [],
        })
        seen_urls.add(sr["url"])

    # Pass 4: HIBP — only for email seeds
    if seed_type == "email":
        hibp_results = _hibp_check(seed)
        if hibp_results:
            logger.info(f"[hibp] breaches: {[b['name'] for b in hibp_results]}")
            # Store as synthetic account entry for report visibility
            breach_note = "; ".join(f"{b['name']} ({b['date']})" for b in hibp_results[:5])
            accounts.append({
                "account_id": f"hibp_{seed.replace('@','_')}",
                "platform": "hibp",
                "handle": seed,
                "url": f"https://haveibeenpwned.com/account/{seed}",
                "display_name": f"HIBP: {len(hibp_results)} breaches",
                "bio": breach_note,
                "first_seen": None,
                "last_seen": None,
                "sources": [],
            })

    # Write to db
    for acc in accounts:
        db.upsert_account(
            account_id=acc["account_id"],
            platform=acc["platform"],
            url=acc["url"],
            handle=acc["handle"],
            display_name=acc["display_name"],
            bio=acc["bio"],
            first_seen=acc["first_seen"],
            last_seen=acc["last_seen"],
            sources=acc["sources"],
        )
        logger.info(
            f"[account_discovery] {acc['platform']} @{acc['handle']} → {acc['url'][:60]}"
        )

    logger.info(f"[account_discovery] accounts found: {len(accounts)}")
    return accounts
