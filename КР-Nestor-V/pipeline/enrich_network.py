"""
Network enrichment: NER on sources → links table.

Two-pass approach:
  Pass 1 — regex: extract person/org names + risk flag keywords (fast, no LLM)
  Pass 2 — Gemini: structured entity extraction for interview/bio sources (optional)

Entity types: persons, orgs, institutions.
Risk flags: RC / ДРЗ / РПЦ / «Русский мир» / інші маркери.
"""

import json
import os
import re
import time
import uuid
from loguru import logger

from pipeline.storage.db import Database
from pipeline.gates.safety_gate import LLM_SYSTEM_PROMPT, sanitize_for_llm

# Risk flag keywords (lowercase)
RISK_KEYWORDS = [
    "русский мир", "russian world",
    "рпц", "руська православна церква", "russian orthodox church",
    "ркц", "дрз", "россотрудничество", "rossotrudnichestvo",
    "фонд мира", "мир без нацизма",
    "культурний міст", "cultural bridge", "humanitarian bridge",
    "dialogue through culture", "діалог через культуру",
    "не все так однозначно", "хороші руські", "хорошие русские",
]

# Ukrainian/Russian org name patterns (simplified)
_ORG_PATTERNS = [
    r"(?:ПЦУ|ПЦ України|Православна церква України)",
    r"(?:УПЦ(?:\s+МП)?)",
    r"(?:УГКЦ|греко-католицька)",
    r"(?:[A-Z][A-Za-z]+\s+(?:Foundation|Institute|Center|Centre|Fund))",
    r"(?:[А-ЯІЇЄA-Z][\w]+\s+(?:академія|університет|інститут|музей))",
]
_ORG_RE = re.compile("|".join(_ORG_PATTERNS), re.IGNORECASE)

# Separate regex WITHOUT IGNORECASE: "Фонд" must be followed by capitalized word or «quoted»
_FOND_RE = re.compile(
    r'Фонд\s+(?:«[^»]{2,40}»|[А-ЯІЇЄA-Z][А-ЯІЇЄа-яіїєA-Za-z]+)'
)

NER_PROMPT = """Extract all named entities from the text below.
Return a JSON array of objects with:
- "name": entity name (string)
- "type": "person" | "organization" | "institution" | "place"
- "context": 1 sentence about this entity's relation to the main subject (string)

Return ONLY valid JSON array. If nothing found, return [].

Text:
"""

ELIGIBLE_TYPES = {"interview", "bio", "project", "news", "social", "other"}

# ── spaCy fallback ─────────────────────────────────────────────────────────

def _load_spacy_nlp():
    """Load first available spaCy model (uk → en). Returns None if unavailable."""
    try:
        import spacy
    except ImportError:
        return None
    for model in ("uk_core_news_sm", "en_core_web_sm", "ru_core_news_sm"):
        try:
            nlp = spacy.load(model)
            logger.info(f"[enrich_network] spaCy model loaded: {model}")
            return nlp
        except OSError:
            continue
    logger.warning("[enrich_network] spaCy: no model found (uk/en/ru)")
    return None


_INST_KEYWORDS = re.compile(
    r"(фонд|університет|академія|інститут|музей|галерея|церква|школа|коледж|"
    r"university|institute|foundation|museum|academy|church|school|center|centre)",
    re.IGNORECASE,
)

_MARKDOWN_LINK_RE = re.compile(r'\[([^\]]*)\]\([^)]*\)')
_MARKDOWN_FMT_RE  = re.compile(r'[#*`~>|_\\]')

_CAPTION_RE = re.compile(
    r"^(Courtesy|Photo|Image|Picture|Credit|Caption|Follow|Via|Source|Getty|"
    r"All Rights|Press Release|File Photo)\b",
    re.IGNORECASE,
)


def _strip_markdown(text: str) -> str:
    text = _MARKDOWN_LINK_RE.sub(r'\1', text)
    text = _MARKDOWN_FMT_RE.sub(' ', text)
    return text


def _call_spacy_ner(text: str, nlp) -> list[dict]:
    """spaCy NER on first 5000 chars. Returns [] if nlp is None.

    Quality filters:
    - PER: 2+ words (first + last name minimum)
    - ORG: 2+ words OR institution keyword present
    - Latin-only single-word entities (Greek, Hebrew, Cyrillic...) rejected
    """
    if nlp is None:
        return []
    doc = nlp(_strip_markdown(text[:5000]))
    seen: set[str] = set()
    entities: list[dict] = []
    for ent in doc.ents:
        if ent.label_ not in ("PER", "PERSON", "ORG"):
            continue
        if '\n' in ent.text:
            continue
        name = ent.text.strip()
        if len(name) < 3 or name.lower() in seen:
            continue
        words = name.split()
        has_cyrillic = bool(re.search(r"[А-ЯІЇЄа-яіїє]", name))
        is_per = ent.label_ in ("PER", "PERSON")

        if is_per:
            # person must have surname + name (2+ words), no initials-only (A. N.)
            if len(words) < 2:
                continue
            if any(len(w.rstrip('.,')) < 2 for w in words):
                continue
            # Latin-only PER: all words must start uppercase + reject caption phrases
            if not has_cyrillic:
                if not all(w[0].isupper() for w in words if w):
                    continue
                if _CAPTION_RE.search(name):
                    continue
        else:
            # org: 2+ words OR institution keyword
            if len(words) < 2 and not _INST_KEYWORDS.search(name):
                continue
            # reject Latin-only multi-word phrases that look like sentences
            # ("to historic conference decorations", "in the world")
            if not has_cyrillic and len(words) > 1:
                # must start with capital letter and not be a preposition phrase
                if not name[0].isupper():
                    continue
                # reject if majority of words are lowercase common words
                caps = sum(1 for w in words if w and w[0].isupper())
                if caps <= len(words) / 2:
                    continue

        seen.add(name.lower())
        entities.append({
            "name": name,
            "type": "person" if is_per else "organization",
            "context": "",
        })
    return entities


def _extract_evidence_quote(text: str, entity: str, max_chars: int = 200) -> str:
    """Return first sentence containing entity name, or surrounding context."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    entity_lower = entity.lower()
    for sent in sentences:
        if entity_lower in sent.lower():
            return sent.strip()[:max_chars]
    idx = text.lower().find(entity_lower)
    if idx >= 0:
        start = max(0, idx - 60)
        end = min(len(text), idx + 140)
        return text[start:end].strip()[:max_chars]
    return ""


def _detect_risk_flags(text: str) -> list[str]:
    text_lower = text.lower()
    return [kw for kw in RISK_KEYWORDS if kw in text_lower]


def _extract_orgs_regex(text: str) -> list[str]:
    results = {m.group(0) for m in _ORG_RE.finditer(text) if m.group(0)[0].isupper()}
    results.update(m.group(0) for m in _FOND_RE.finditer(text))
    return list(results)


def _call_gemini_ner(text: str, budget) -> list[dict] | None:
    """Returns list on success, [] on parse error, None on rate-limit (caller should stop NER)."""
    try:
        from google import genai as _genai
        from google.genai import types as _gtypes
    except ImportError:
        return []

    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        return []

    try:
        budget.check_service("gemini")
    except Exception:
        return []

    try:
        client = _genai.Client(api_key=api_key)
        clean = sanitize_for_llm(text, max_chars=4000)
        resp = None
        for model_name in ("gemini-2.0-flash", "gemini-2.5-flash",
                           "gemini-2.0-flash-lite"):
            try:
                resp = client.models.generate_content(
                    model=model_name,
                    contents=NER_PROMPT + clean,
                    config=_gtypes.GenerateContentConfig(
                        system_instruction=LLM_SYSTEM_PROMPT,
                    ),
                )
                budget.consume("gemini", 1)
                break
            except Exception as e:
                err = str(e)
                if "429" in err or "RESOURCE_EXHAUSTED" in err.upper():
                    logger.debug("[enrich_network] NER rate-limited, stopping NER for this run")
                    return None
                logger.debug(f"[enrich_network] model {model_name} failed: {type(e).__name__}")
                continue
        if resp is None:
            return []
        raw = resp.text.strip()
        if raw.startswith("```"):
            raw = "\n".join(raw.split("\n")[1:])
        if raw.endswith("```"):
            raw = "\n".join(raw.split("\n")[:-1])
        return json.loads(raw)
    except Exception as e:
        logger.warning(f"[enrich_network] Gemini NER error: {type(e).__name__}")
        return []


def run_enrich_network(
    actor_id: str,
    db: Database,
    budget=None,
) -> list[dict]:
    sources = db.get_sources(actor_id)
    all_links: list[dict] = []
    ner_available = True
    spacy_nlp = _load_spacy_nlp()

    for src in sources:
        text = src.get("text") or ""
        if not text:
            continue

        flags = _detect_risk_flags(text)
        orgs_regex = _extract_orgs_regex(text)

        # Pass 1: regex-detected orgs → links
        for org in orgs_regex:
            link_id = f"lnk_{uuid.uuid4().hex[:8]}"
            db.insert_link(
                link_id=link_id,
                subject_a=actor_id,
                subject_b=org,
                link_type="організаційний",
                period=src.get("date_raw", ""),
                context=f"Згадується у: {src.get('title','')[:80]}",
                flags=flags,
                source_id=src["source_id"],
                evidence_quote=_extract_evidence_quote(text, org),
            )
            all_links.append({"link_id": link_id, "subject_b": org, "flags": flags})
            logger.info(f"[network] {org[:50]}" + (f" ⚑ {flags}" if flags else ""))

        # Pass 2: NER for rich sources (Gemini → spaCy fallback)
        if src.get("source_type") not in ELIGIBLE_TYPES or len(text) <= 300:
            continue

        if ner_available and budget:
            entities = _call_gemini_ner(text, budget)
            if entities is None:
                ner_available = False
                logger.warning(
                    "[enrich_network] Gemini NER rate-limited — switching to spaCy fallback"
                )
                entities = _call_spacy_ner(text, spacy_nlp)
        else:
            entities = _call_spacy_ner(text, spacy_nlp)

        for ent in entities:
            name = ent.get("name", "").strip()
            etype = ent.get("type", "")
            context = ent.get("context", "")
            if not name or etype == "place":
                continue
            if any(name.lower() in o.lower() for o in orgs_regex):
                continue

            ent_flags = _detect_risk_flags(name + " " + context)
            evidence = context.strip()[:200] if context.strip() else _extract_evidence_quote(text, name)
            link_id = f"lnk_{uuid.uuid4().hex[:8]}"
            db.insert_link(
                link_id=link_id,
                subject_a=actor_id,
                subject_b=name,
                link_type="особистий" if etype == "person" else "організаційний",
                period=src.get("date_raw", ""),
                context=context[:200],
                flags=ent_flags or flags,
                source_id=src["source_id"],
                evidence_quote=evidence,
            )
            all_links.append({
                "link_id": link_id,
                "subject_b": name,
                "type": etype,
                "flags": ent_flags,
            })
            logger.info(
                f"[network] [{etype}] {name[:50]}"
                + (f" ⚑ {ent_flags}" if ent_flags else "")
            )

    logger.info(f"[enrich_network] links created: {len(all_links)}")
    return all_links
