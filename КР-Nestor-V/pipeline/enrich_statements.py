"""
Statement enrichment: sources → Gemini LLM → statements table.
Fallback: regex «...» quote extraction + heuristic rhetoric classification.

LLM guard: safety_gate.LLM_SYSTEM_PROMPT + sanitize_for_llm(text).
Extracts per source: list of {date, quote, summary, platform, rhetoric_type}.
"""

import json
import os
import re
import uuid
from loguru import logger

from pipeline.storage.db import Database
from pipeline.gates.safety_gate import LLM_SYSTEM_PROMPT, sanitize_for_llm
from pipeline.enrich_timeline import get_war_context, normalize_date

ELIGIBLE_TYPES = {"interview", "news", "bio", "social", "other"}

EXTRACTION_PROMPT = """Analyze the following text about a public figure and extract direct quotes or key statements they made.

For each quote or statement found, return a JSON array with objects having these fields:
- "quote": the exact or near-exact statement (string, max 300 chars)
- "summary": 1-2 sentence summary of what the statement means (string, MUST be written in Ukrainian)
- "date": date of the statement if mentioned (string, YYYY or YYYY-MM or YYYY-MM-DD, or "" if unknown)
- "platform": where it was published (string, e.g. "interview", "facebook", "youtube", or "" if unknown)
- "rhetoric_type": classify as one of: "neutral", "pro-ukrainian", "ambiguous", "bridge-building", "pro-russian", "unknown"
  IMPORTANT: Before assigning rhetoric_type, explicitly consider the most charitable (neutral) interpretation of the statement.
  Assign "ambiguous" when the statement could reasonably be read in multiple ways.
  Only assign "pro-russian" or "bridge-building" when the framing is unambiguous — not merely because other sources about this person are pro-russian.

Return ONLY a valid JSON array. If no quotes found, return [].

Text to analyze:
"""

# ── Regex + heuristic fallback ─────────────────────────────────────────────

_GUILLEMET_RE = re.compile(r'«([^»]{25,400})»')
_DBLQUOTE_RE  = re.compile(r'"([^"]{25,300})"')

_PRO_UA_KW = [
    "слава україні", "збройні сили", "окупант", "агресор", "незалежність",
    "суверенітет", "перемога", "звільнення", "деокупація", "знищення ворога",
    "захист вітчизни", "відсіч", "героїчний спротив",
]
_PRO_RU_KW = [
    "русский мир", "денацификаци", "братские народы", "спецоперация",
    "укронацист", "киевский режим", "хохл", "мир без нацизма",
    "бандеровц", "нацистский режим", "легитимные цели",
]
_BRIDGE_KW = [
    "діалог", "культурний обмін", "спільна спадщина", "мирні переговори",
    "примирення", "гуманітарний міст", "не все так однозначно",
]


def _heuristic_rhetoric(text: str) -> str:
    t = text.lower()
    if any(kw in t for kw in _PRO_RU_KW):
        return "pro-russian"
    if any(kw in t for kw in _PRO_UA_KW):
        return "pro-ukrainian"
    if any(kw in t for kw in _BRIDGE_KW):
        return "bridge-building"
    return "unknown"


def _is_readable_quote(text: str) -> bool:
    """Reject binary garbage, URLs, course titles, and non-speech fragments."""
    if len(text) < 15:
        return False
    # high non-printable ratio = binary/garbage
    printable = sum(1 for c in text if c.isprintable() and ord(c) > 31)
    if printable / len(text) < 0.90:
        return False
    # mostly Latin + digits with no spaces = URL or minified code
    words = text.split()
    if len(words) < 3:
        return False
    # must have meaningful alphabetic content — Cyrillic OR Latin (multilingual actors)
    alpha_words = [w for w in words if re.search(r'[а-яіїєa-z]', w.lower())]
    if not alpha_words:
        return False
    return True


def _extract_quotes_regex(text: str) -> list[dict]:
    """Regex fallback: extract «...» / "..." quoted text without LLM. Cap 3 per source."""
    seen: set[str] = set()
    results: list[dict] = []
    for m in list(_GUILLEMET_RE.finditer(text)) + list(_DBLQUOTE_RE.finditer(text)):
        q = m.group(1).strip()
        if q in seen:
            continue
        # must be readable human-speech text (not binary, URL, course title)
        if not _is_readable_quote(q):
            continue
        if not re.search(r'[а-яіїєА-ЯІЇЄa-zA-Z]', q):
            continue
        seen.add(q)
        results.append({
            "quote": q,
            "summary": "[regex]",
            "date": "",
            "platform": "",
            "rhetoric_type": _heuristic_rhetoric(q),
        })
        if len(results) >= 3:
            break
    return results


# ── Gemini ─────────────────────────────────────────────────────────────────

def _call_gemini(text: str, budget) -> list[dict] | None:
    """Returns list on success, [] on empty/error, None on rate-limit."""
    try:
        from google import genai as _genai
        from google.genai import types as _gtypes
    except ImportError:
        logger.error("[enrich_statements] google-genai not installed")
        return []

    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        logger.warning("[enrich_statements] GEMINI_API_KEY not set")
        return []

    try:
        budget.check_service("gemini")
    except Exception as e:
        logger.warning(f"[enrich_statements] budget: {e}")
        return []

    try:
        client = _genai.Client(api_key=api_key)
        clean_text = sanitize_for_llm(text, max_chars=6000)
        response = None
        for model_name in ("gemini-2.0-flash", "gemini-2.5-flash",
                           "gemini-2.0-flash-lite"):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=EXTRACTION_PROMPT + clean_text,
                    config=_gtypes.GenerateContentConfig(
                        system_instruction=LLM_SYSTEM_PROMPT,
                    ),
                )
                budget.consume("gemini", 1)
                break
            except Exception as e:
                err = str(e)
                if "429" in err or "RESOURCE_EXHAUSTED" in err.upper():
                    logger.debug("[enrich_statements] rate-limited, stopping for this run")
                    return None
                logger.debug(f"[enrich_statements] model {model_name} failed: {type(e).__name__}")
                continue
        if response is None:
            logger.error("[enrich_statements] all Gemini models failed")
            return []
        raw = response.text.strip()
        if raw.startswith("```"):
            raw = "\n".join(raw.split("\n")[1:])
        if raw.endswith("```"):
            raw = "\n".join(raw.split("\n")[:-1])
        return json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("[enrich_statements] Gemini returned non-JSON")
        return []
    except Exception as e:
        logger.error(f"[enrich_statements] Gemini error: {type(e).__name__}")
        return []


# ── Orchestrator ───────────────────────────────────────────────────────────

def run_enrich_statements(
    actor_id: str,
    db: Database,
    budget=None,
) -> list[dict]:
    if budget is None:
        logger.warning("[enrich_statements] no budget tracker, skipping")
        return []

    sources = db.get_sources(actor_id)
    eligible = [s for s in sources if s.get("source_type") in ELIGIBLE_TYPES
                and len(s.get("text") or "") > 200]

    logger.info(f"[enrich_statements] eligible sources: {len(eligible)}/{len(sources)}")

    all_statements: list[dict] = []
    gemini_available = True

    for src in eligible:
        text = src.get("text", "")
        platform_hint = _platform_from_url(src.get("url", ""))

        if gemini_available:
            extracted = _call_gemini(text, budget)
            if extracted is None:
                gemini_available = False
                logger.warning(
                    "[enrich_statements] Gemini rate-limited — switching to regex fallback"
                )
                extracted = _extract_quotes_regex(text)
            elif not extracted:
                # Gemini found nothing; try regex as second chance
                extracted = _extract_quotes_regex(text)
        else:
            extracted = _extract_quotes_regex(text)

        for item in extracted:
            if not item.get("quote"):
                continue

            date = normalize_date(item.get("date") or src.get("date_raw") or "")
            war_ctx = get_war_context(date) if date else ""
            platform = item.get("platform") or platform_hint or src.get("source_type", "")
            stmt_id = f"stmt_{uuid.uuid4().hex[:8]}"

            db.insert_statement(
                statement_id=stmt_id,
                actor_id=actor_id,
                quote=item["quote"][:500],
                summary=item.get("summary", "")[:300],
                date=date,
                platform=platform,
                war_context=war_ctx,
                rhetoric_type=item.get("rhetoric_type", "unknown"),
                source_id=src["source_id"],
            )
            all_statements.append({
                "statement_id": stmt_id,
                "date": date,
                "war_context": war_ctx,
                "rhetoric_type": item.get("rhetoric_type"),
                "quote": item["quote"][:80],
            })
            method = "gemini" if gemini_available or item.get("summary") != "[regex]" else "regex"
            logger.info(
                f"[enrich_statements] [{item.get('rhetoric_type','?')}][{method}] "
                f"{date or '—'} «{item['quote'][:60]}»"
            )

    logger.info(f"[enrich_statements] statements extracted: {len(all_statements)}")
    return all_statements


def _platform_from_url(url: str) -> str:
    url = url.lower()
    for keyword, label in [
        ("facebook.com", "facebook"), ("instagram.com", "instagram"),
        ("youtube.com", "youtube"), ("t.me", "telegram"),
        ("twitter.com", "twitter"), ("x.com", "twitter"),
        ("rozmova", "interview"), ("cases.media", "interview"),
        ("radiosvoboda", "radio"), ("risu.ua", "media"),
    ]:
        if keyword in url:
            return label
    return ""
