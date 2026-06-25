"""
Collect layer: Exa/Tavily/GoogleCSE search → sources table + raw/.

Flow:
  1. Build search queries from seed + params
  2. Query enabled search APIs (Exa, Google CSE, Tavily)
  3. Dedup by URL (seen_urls) and content hash (sha256)
  4. Save full response JSON to raw/
  5. Strip HTML, extract text + metadata
  6. Insert into sources table
"""

import hashlib
import json
import os
import re
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Optional

import httpx
from loguru import logger

try:
    import ftfy as _ftfy
    _fix_encoding = _ftfy.fix_text
except ImportError:
    _fix_encoding = lambda s: s

from pipeline.storage.db import Database
from pipeline.storage.archive import save_raw_json
from pipeline.gates.budget_gate import BudgetTracker
from pipeline.gates.safety_gate import strip_html

SOCIAL_DOMAINS = {
    "facebook.com", "twitter.com", "x.com", "instagram.com",
    "t.me", "telegram.me", "youtube.com", "linkedin.com",
    "tiktok.com", "vk.com", "ok.ru",
}

SOURCE_TYPE_MAP = {
    "bio": [
        "about", "biography", "profile", "wiki", "author", "автор",
        "calligrapher", "designer", "дизайнер", "каліграф", "researcher",
        "cv", "curriculum-vitae", "хто-такий", "biography",
        "linkedin.com/in/", "academia.edu", "researchgate.net",
    ],
    "interview": [
        "interview", "розмова", "інтерв'ю", "бесіда", "podcast",
        "подкаст", "rozmova", "cases.media", "radiosvoboda",
        "risu.ua", "nakypilo", "hromadske", "suspilne",
        "відповідає", "говорить", "розповідає", "zapytaly",
    ],
    "news": [
        "news", "новини", "стаття", "article", "report", "медіа",
        "media", "прес", "press", "publication", "видання",
        "ukrinform", "unian", "pravda.com", "detector.media",
        "bbc.", "reuters.", "guardian.", "nv.ua", "zn.ua",
    ],
    "project": [
        "project", "проєкт", "exhibit", "виставк", "portfolio",
        "behance.net", "dribbble.com", "галерея", "gallery",
        "workshop", "інсталяція", "installation", "мистецтво",
    ],
    "social": [
        "facebook.com/", "instagram.com/", "twitter.com/",
        "x.com/", "t.me/", "tiktok.com/", "youtube.com/channel",
        "youtube.com/@", "vk.com/",
    ],
    "academic": [
        "scholar.google", "jstor.org", "springer.com", "elsevier.com",
        "scopus", "doi.org", "thesis", "дисертація", "монографія",
        "наукова-стаття", "конференція", "conference",
    ],
}


def _detect_source_type(url: str, title: str) -> str:
    combined = (url + " " + (title or "")).lower()
    for stype, keywords in SOURCE_TYPE_MAP.items():
        if any(k in combined for k in keywords):
            return stype
    return "other"


def _content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


_TRANSLIT_MAP = {
    "а": "a", "б": "b", "в": "v", "г": "h", "ґ": "g", "д": "d",
    "е": "e", "є": "ie", "ж": "zh", "з": "z", "и": "y", "і": "i",
    "ї": "yi", "й": "i", "к": "k", "л": "l", "м": "m", "н": "n",
    "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "kh", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "shch",
    "ь": "", "ю": "yu", "я": "ya",
}


def _transliterate(name: str) -> str:
    return "".join(_TRANSLIT_MAP.get(c, c) for c in name.lower())


_RU_SITE_LIST = (
    "site:pravmir.ru OR site:blagovest-info.ru OR site:artos.org "
    "OR site:calligraphy-museum.com OR site:radiovera.ru OR site:rublev.com"
)

# Foreign first names in Cyrillic → (zone, canonical Latin form)
_FOREIGN_FIRST_NAMES: dict[str, tuple[str, str]] = {
    # Italian
    "франческо": ("it", "Francesco"), "маттео": ("it", "Matteo"),
    "антоніо": ("it", "Antonio"), "джованні": ("it", "Giovanni"),
    "паоло": ("it", "Paolo"), "лука": ("it", "Luca"),
    "марко": ("it", "Marco"), "луїджі": ("it", "Luigi"),
    "пьєтро": ("it", "Pietro"), "ансельмо": ("it", "Anselmo"),
    "фабіо": ("it", "Fabio"), "алессандро": ("it", "Alessandro"),
    "маріо": ("it", "Mario"), "андреа": ("it", "Andrea"),
    "стефано": ("it", "Stefano"), "карло": ("it", "Carlo"),
    "роберто": ("it", "Roberto"), "массімо": ("it", "Massimo"),
    # French
    "жан": ("fr", "Jean"), "філіп": ("fr", "Philippe"),
    "мішель": ("fr", "Michel"), "крістоф": ("fr", "Christophe"),
    # German
    "ганс": ("de", "Hans"), "вальтер": ("de", "Walter"),
    "клаус": ("de", "Klaus"), "вернер": ("de", "Werner"),
    # Spanish/Portuguese
    "хуан": ("es", "Juan"), "хосе": ("es", "José"),
    "карлос": ("es", "Carlos"), "рамон": ("es", "Ramón"),
    # Polish
    "кшиштоф": ("pl", "Krzysztof"), "тадеуш": ("pl", "Tadeusz"),
    "войцех": ("pl", "Wojciech"), "яцек": ("pl", "Jacek"),
}

# Italian surname suffix corrections (longest-first to avoid partial matches):
# Cyrillic ending → Italian ending; UA transliteration is wrong for these.
_IT_SURNAME_SUFFIXES: list[tuple[str, str]] = [
    ("скі", "schi"),   # Браскі → Braschi (UA spelling)
    ("ски", "schi"),   # Браски → Braschi (RU spelling)
    ("кі",  "chi"),    # Маркі  → Marchi  (UA)
    ("ки",  "chi"),    # Марки  → Marchi  (RU)
    ("джі", "gi"),
    ("джи", "gi"),
]

# Per-zone site search hints for foreign-language actors
_ZONE_SITE_LISTS: dict[str, str] = {
    "it": "site:it OR site:vatican.va OR site:avvenire.it OR site:agensir.it",
    "fr": "site:fr OR site:lefigaro.fr OR site:lemonde.fr",
    "de": "site:de OR site:faz.net OR site:spiegel.de",
    "es": "site:es OR site:elpais.com",
    "pl": "site:pl OR site:wyborcza.pl",
}


# UA-specific Cyrillic → Russian equivalents for RU-domain site queries
_UA_TO_RU = str.maketrans("іїєґ", "ииег")


def _ru_variant(text: str) -> str:
    return text.translate(_UA_TO_RU)


def _it_surname_correct(cyrillic_surname: str) -> str:
    cy = cyrillic_surname.lower()
    for cy_suf, it_suf in _IT_SURNAME_SUFFIXES:
        if cy.endswith(cy_suf):
            base = _transliterate(cyrillic_surname[: -len(cy_suf)])
            return (base + it_suf).title()
    return _transliterate(cyrillic_surname).title()


def _detect_name_zone_heuristic(seed: str) -> tuple[str | None, str | None]:
    """Fast offline detection: checks _FOREIGN_FIRST_NAMES dict only."""
    parts = seed.strip().split()
    if len(parts) < 2:
        return None, None
    for i, part in enumerate(parts):
        entry = _FOREIGN_FIRST_NAMES.get(part.lower())
        if entry:
            zone, latin_first = entry
            surnames = [p for j, p in enumerate(parts) if j != i]
            if zone == "it":
                latin_surnames = [_it_surname_correct(s) for s in surnames]
            else:
                latin_surnames = [_transliterate(s).title() for s in surnames]
            return zone, latin_first + " " + " ".join(latin_surnames)
    return None, None


_ZONE_VALID = frozenset(
    "af sq am ar hy az eu be bn bs bg ca zh hr cs da nl en et fi "
    "fr gl ka de el gu ht ha he hi hu is ig id ga it ja jv kn kk "
    "km ko ku ky lo la lv lt lb mk ms ml mt mi mr mn my ne no ps "
    "fa pl pt pa ro ru sm gd sr st sn sd si sk sl so es su sw sv "
    "tl tg ta tt te th tr tk uk ur ug uz vi cy xh yi yo zu".split()
)


def _call_gemini_zone(seed: str) -> tuple[str | None, str | None]:
    """Ask Gemini to detect language zone and canonical Latin alias for a Cyrillic name.

    Never raises. Returns (None, None) on any failure.
    Uses short prompt (~60 tokens) — one cheap call per run.
    """
    try:
        from google import genai as _genai
    except ImportError:
        return None, None

    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        return None, None

    prompt = (
        f'Cyrillic name: "{seed}"\n'
        "If this is a foreign (non-Ukrainian, non-Russian) name transliterated to Cyrillic, "
        'reply with JSON: {"zone":"<ISO-639-1>","alias":"<canonical Latin spelling>"}\n'
        'If Ukrainian or Russian name, reply: {"zone":null,"alias":null}\n'
        "JSON only, no markdown, no explanation."
    )

    for model_name in ("gemini-2.0-flash", "gemini-2.5-flash", "gemini-2.0-flash-lite"):
        try:
            client = _genai.Client(api_key=api_key)
            response = client.models.generate_content(model=model_name, contents=prompt)
            raw = response.text.strip()
            logger.debug(f"[collect] Gemini zone raw ({model_name}): {raw!r}")
            # Strip markdown fences
            if raw.startswith("```"):
                raw = "\n".join(raw.split("\n")[1:])
            if raw.endswith("```"):
                raw = "\n".join(raw.split("\n")[:-1])
            raw = raw.strip()
            data = json.loads(raw)
            zone = data.get("zone")
            alias = data.get("alias")
            # Validate
            if zone is not None and (not isinstance(zone, str) or zone not in _ZONE_VALID):
                logger.warning(f"[collect] Gemini zone: invalid zone {zone!r}, ignoring")
                return None, None
            if alias is not None and (not isinstance(alias, str) or not alias.strip()):
                logger.warning(f"[collect] Gemini zone: invalid alias {alias!r}, ignoring")
                return None, None
            logger.info(f"[collect] Gemini zone → zone={zone!r} alias={alias!r} (model={model_name})")
            return zone, alias
        except json.JSONDecodeError:
            logger.warning(f"[collect] Gemini zone: non-JSON from {model_name}: {raw!r}")
            return None, None
        except Exception as e:
            err = str(e)
            if "429" in err or "RESOURCE_EXHAUSTED" in err.upper():
                logger.info("[collect] Gemini zone: rate-limited, falling back to dict-only")
                return None, None
            logger.debug(f"[collect] Gemini zone: {model_name} failed ({type(e).__name__}), trying next")
            continue
    logger.debug("[collect] Gemini zone: all models failed, no zone detected")
    return None, None


def _detect_name_zone(seed: str) -> tuple[str | None, str | None]:
    """Detect foreign language zone + canonical Latin alias from Cyrillic seed.

    Strategy:
      1. Fast heuristic dict (_FOREIGN_FIRST_NAMES) — no API, instant.
      2. Gemini fallback for any name not in dict — handles arbitrary foreign names.
    Returns (zone, latin_alias) or (None, None) for Ukrainian/Russian names.
    """
    zone, alias = _detect_name_zone_heuristic(seed)
    if zone:
        return zone, alias
    return _call_gemini_zone(seed)


def _build_queries(
    seed: str,
    seed_type: str,
    language_hint: list[str],
    query_context: list[str] | None = None,
    latin_alias: str | None = None,
    zone: str | None = None,
) -> list[str]:
    # If query_context is set, narrow every query with a context filter to
    # prevent same-name actor contamination (e.g. priest vs. racing driver).
    ctx_filter = ""
    if query_context:
        ctx_terms = " OR ".join(f'"{t}"' for t in query_context[:4])
        ctx_filter = f" ({ctx_terms})"

    queries = [seed + ctx_filter] if ctx_filter else [seed]
    if seed_type == "fullname":
        queries.append(f'"{seed}"{ctx_filter} інтерв\'ю')
        queries.append(f'"{seed}"{ctx_filter} проєкт')
        # EN transliterated variant for broader coverage
        en = _transliterate(seed).title()
        queries.append(f'"{en}"{ctx_filter} biography OR interview OR project')
        # Class B: explicit RU-domain queries (Exa-only — Tavily ignores site: operator)
        # Use RU Cyrillic variant (і→и, є→е) since RU sites use Russian spelling.
        ru_seed = _ru_variant(seed)
        queries.append(f'"{ru_seed}" ({_RU_SITE_LIST})')
        if ru_seed != seed:
            queries.append(f'"{seed}" ({_RU_SITE_LIST})')
        # Class B alt: transliterated + RU sites
        if en != seed:
            queries.append(f'"{en}" ({_RU_SITE_LIST})')
        # Auto-detected foreign zone: add canonical Latin alias queries
        if latin_alias and latin_alias.lower() != en.lower():
            queries.append(f'"{latin_alias}"{ctx_filter}')
            queries.append(f'"{latin_alias}"{ctx_filter} biography OR interview OR profile')
            if zone and zone in _ZONE_SITE_LISTS:
                queries.append(f'"{latin_alias}" ({_ZONE_SITE_LISTS[zone]})')
    elif seed_type == "nickname":
        queries.append(f'"{seed}" site:facebook.com OR site:instagram.com OR site:t.me')
    return queries


def _search_exa(query: str, budget: BudgetTracker, num_results: int = 15) -> list[dict]:
    api_key = os.environ.get("EXA_API_KEY", "")
    if not api_key:
        logger.warning("EXA_API_KEY not set, skipping Exa search")
        return []
    budget.consume("exa", 1)
    try:
        resp = httpx.post(
            "https://api.exa.ai/search",
            headers={"x-api-key": api_key, "Content-Type": "application/json"},
            json={"query": query, "numResults": num_results, "contents": {"text": True}},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("results", [])
    except httpx.HTTPStatusError as e:
        logger.error(f"Exa HTTP {e.response.status_code} for query={query!r}")
        return []
    except Exception as e:
        logger.error(f"Exa search error: {type(e).__name__}")
        return []


def _search_tavily(query: str, budget: BudgetTracker, max_results: int = 10) -> list[dict]:
    api_key = os.environ.get("TAVILY_API_KEY", "")
    if not api_key:
        logger.warning("TAVILY_API_KEY not set, skipping Tavily search")
        return []
    budget.consume("tavily", 1)
    try:
        resp = httpx.post(
            "https://api.tavily.com/search",
            # api_key in body per Tavily spec — redacted from logs below
            json={
                "api_key": api_key,
                "query": query,
                "max_results": max_results,
                "include_raw_content": True,
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("results", [])
    except httpx.HTTPStatusError as e:
        logger.error(f"Tavily HTTP {e.response.status_code} for query={query!r}")
        return []
    except Exception as e:
        logger.error(f"Tavily search error: {type(e).__name__}")
        return []


def _fetch_url_text(url: str, timeout: int = 8) -> str:
    """Fetch full page text for Google CSE results (snippets are too short)."""
    try:
        resp = httpx.get(
            url, timeout=timeout, follow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0 (compatible; OSINT-pipeline/1.0)"},
        )
        if resp.status_code == 200 and resp.text:
            return strip_html(resp.text)[:12000]
    except Exception:
        pass
    return ""


def _search_google_cse(
    query: str,
    budget: BudgetTracker,
    num: int = 10,
    language_hint: list[str] | None = None,
) -> list[dict]:
    """Google CSE — per-language queries for multilingual coverage.

    Sends one request per non-English language in language_hint (lr=lang_XX).
    No domain lists — Google finds the right sites for any actor type.
    """
    api_key = os.environ.get("GOOGLE_CSE_API_KEY", "")
    cse_id  = os.environ.get("GOOGLE_CSE_ID", "")
    if not api_key or not cse_id:
        logger.debug("[google_cse] GOOGLE_CSE_API_KEY or GOOGLE_CSE_ID not set, skipping")
        return []

    # Unrestricted first, then one request per non-English language.
    # English already covered by Exa/Tavily — skip lang_en.
    lr_variants: list[str | None] = [None]
    for lang in (language_hint or []):
        if lang and lang.lower() != "en":
            lr_code = f"lang_{lang.lower()}"
            if lr_code not in lr_variants:
                lr_variants.append(lr_code)

    all_items: list[dict] = []
    seen_item_urls: set[str] = set()

    for lr in lr_variants:
        try:
            budget.consume("google_cse", 1)
        except Exception as e:
            logger.warning(f"[google_cse] budget exhausted: {e}")
            break
        params: dict = {"key": api_key, "cx": cse_id, "q": query, "num": min(num, 10)}
        if lr:
            params["lr"] = lr
        try:
            resp = httpx.get(
                "https://www.googleapis.com/customsearch/v1",
                params=params, timeout=15,
            )
            resp.raise_for_status()
            items = resp.json().get("items", [])
            logger.info(f"[google_cse] lr={lr or 'any'}: {len(items)} results")
            for item in items:
                url = item.get("link", "")
                if url and url not in seen_item_urls:
                    seen_item_urls.add(url)
                    all_items.append(item)
        except httpx.HTTPStatusError as e:
            logger.error(f"[google_cse] HTTP {e.response.status_code} lr={lr}")
        except Exception as e:
            logger.error(f"[google_cse] error lr={lr}: {type(e).__name__}")

    def _fetch_one(item: dict) -> dict | None:
        url = item.get("link", "")
        if not url:
            return None
        text = _fetch_url_text(url) or item.get("snippet", "")
        if not text:
            return None
        return {"url": url, "title": item.get("title", ""), "text": text, "published_date": ""}

    results = []
    with ThreadPoolExecutor(max_workers=5) as pool:
        for r in pool.map(_fetch_one, all_items):
            if r:
                results.append(r)
    logger.info(
        f"[google_cse] {len(results)} pages fetched "
        f"({len(lr_variants)} lr variants) for {query[:50]!r}"
    )
    return results


def _relevance_tokens(seed: str, seed_type: str, latin_alias: str | None = None) -> list[str]:
    """Return tokens that must appear in title+text for the result to be relevant.

    For fullname: SURNAME only (not first name). First names like "Олександр",
    "Іван", "Петро" are too common and cause wrong-actor contamination.
    """
    parts = seed.strip().split()
    tokens = []
    if seed_type == "fullname" and len(parts) >= 2:
        tokens.append(parts[-1].lower())   # surname: "філоненко", "чекаль"
        en = _transliterate(parts[-1])     # transliterated: "filonenko", "chekal"
        if en:
            tokens.append(en)
        # Also add middle name if provided (3-part name) for disambiguation
        if len(parts) >= 3:
            tokens.append(parts[1].lower())  # по-батькові
        # Foreign alias: add Latin surname so foreign-language pages pass the filter
        if latin_alias:
            alias_surname = latin_alias.strip().split()[-1].lower()
            if alias_surname not in tokens:
                tokens.append(alias_surname)
    elif seed_type == "nickname":
        tokens.append(seed.lstrip("@").lower())
    else:
        tokens.append(parts[-1].lower())
    return tokens


# Wikipedia User/draft namespaces — researcher's own notes, not published sources
_BLOCKED_URL_PATTERNS = [
    r"wikipedia\.org/wiki/User:",
    r"wikipedia\.org/wiki/%D0%9A%D0%BE%D1%80%D0%B8%D1%81%D1%82%D1%83%D0%B2%D0%B0%D1%87:",  # Користувач:
    r"wikipedia\.org/wiki/Користувач:",
]
_BLOCKED_URL_RE = re.compile("|".join(_BLOCKED_URL_PATTERNS), re.IGNORECASE)


def _is_blocked_url(url: str) -> bool:
    return bool(_BLOCKED_URL_RE.search(url))


def _is_relevant(title: str, text: str, tokens: list[str]) -> bool:
    """True if at least ONE seed token appears as whole word in title or text."""
    haystack = (title + " " + text).lower()
    return any(re.search(r'\b' + re.escape(tok) + r'\b', haystack) for tok in tokens)


def _normalize_result(raw: dict, provider: str) -> Optional[dict]:
    if provider == "exa":
        url = raw.get("url", "")
        title = raw.get("title", "")
        text = raw.get("text") or raw.get("extract", "")
        date_raw = raw.get("publishedDate") or raw.get("published_date", "")
    elif provider == "google_cse":
        url = raw.get("url", "")
        title = raw.get("title", "")
        text = raw.get("text") or raw.get("snippet", "")
        date_raw = raw.get("published_date", "")
    else:  # tavily
        url = raw.get("url", "")
        title = raw.get("title", "")
        text = raw.get("raw_content") or raw.get("content", "")
        date_raw = raw.get("published_date", "")

    if not url or not text:
        return None
    text = strip_html(text) if "<" in text else _fix_encoding(text.strip())
    title = _fix_encoding(title) if title else title
    # reject binary/garbage sources (high non-printable char ratio)
    if len(text) > 50:
        printable = sum(1 for c in text if c.isprintable() and ord(c) > 31)
        if printable / len(text) < 0.85:
            return None
    return {"url": url, "title": title, "text": text, "date_raw": date_raw}


def run_collect(
    seed: str,
    actor_id: str,
    seed_type: str,
    db: Database,
    run_dir: Path,
    budget: BudgetTracker,
    language_hint: list[str] = None,
    platform_hint: list[str] = None,
    time_window: str = None,
    query_context: list[str] = None,
) -> tuple[list[dict], dict]:
    seen_urls: set[str] = set()
    seen_hashes: set[str] = set()
    collected: list[dict] = []
    skipped_irrelevant = 0
    fetched_total = 0

    zone, latin_alias = _detect_name_zone(seed) if seed_type == "fullname" else (None, None)
    if latin_alias:
        source = "dict" if _detect_name_zone_heuristic(seed)[0] else "gemini"
        logger.info(f"[collect] zone={zone!r} alias={latin_alias!r} (source={source})")
    rel_tokens = _relevance_tokens(seed, seed_type, latin_alias=latin_alias)
    queries = _build_queries(seed, seed_type, language_hint or [], query_context,
                             latin_alias=latin_alias, zone=zone)

    for query in queries:
        for provider, search_fn in [
            ("exa", _search_exa),
            ("google_cse", _search_google_cse),
            ("tavily", _search_tavily),
        ]:
            if provider in ("tavily", "google_cse") and "site:" in query:
                continue
            try:
                if provider == "google_cse":
                    raw_results = search_fn(query, budget, language_hint=language_hint or [])
                else:
                    raw_results = search_fn(query, budget)
            except Exception as e:
                logger.warning(f"{provider} budget/error: {e}")
                continue

            save_raw_json(run_dir, f"{provider}_{_content_hash(query)}", raw_results)

            for raw in raw_results:
                norm = _normalize_result(raw, provider)
                if not norm:
                    continue
                fetched_total += 1
                url = norm["url"]
                if url in seen_urls:
                    continue
                chash = _content_hash(norm["text"])
                if chash in seen_hashes:
                    continue

                if _is_blocked_url(url):
                    skipped_irrelevant += 1
                    logger.debug(f"[collect] skip blocked url: {url[:70]}")
                    continue

                if not _is_relevant(norm["title"], norm["text"], rel_tokens):
                    skipped_irrelevant += 1
                    logger.debug(f"[collect] skip irrelevant: {url[:70]}")
                    continue

                seen_urls.add(url)
                seen_hashes.add(chash)

                source_id = str(uuid.uuid4())[:8]
                source_type = _detect_source_type(url, norm["title"])

                db.insert_source(
                    source_id=source_id,
                    actor_id=actor_id,
                    url=url,
                    title=norm["title"],
                    text=norm["text"],
                    source_type=source_type,
                    date_raw=norm["date_raw"],
                    content_hash=chash,
                )
                collected.append({
                    "source_id": source_id,
                    "url": url,
                    "title": norm["title"],
                    "source_type": source_type,
                })
                logger.info(f"[collect] {source_type} {url[:80]}")

    logger.info(
        f"[collect] total sources: {len(collected)} "
        f"(fetched: {fetched_total}, skipped irrelevant: {skipped_irrelevant})"
    )
    return collected, {
        "fetched_total": fetched_total,
        "skipped_irrelevant": skipped_irrelevant,
        "rejected_ratio": skipped_irrelevant / max(fetched_total, 1),
        "fetch_success_rate": 1.0,
    }
