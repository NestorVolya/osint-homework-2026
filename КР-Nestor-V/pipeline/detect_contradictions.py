"""
Contradiction detection: compare statements batch → identify contradictions.
Uses Gemini Flash on compact statement list (not raw corpus).

run_detect_contradictions(actor_id, db, budget, run_dir) → list[dict]
Saves: run_dir/artifacts/contradictions.json
"""
import json
import os
from pathlib import Path

from loguru import logger

from pipeline.storage.db import Database
from pipeline.gates.safety_gate import LLM_SYSTEM_PROMPT

_CONTRADICTION_PROMPT = """Analyze the following statements made by or attributed to a person.
Identify pairs of statements that directly contradict each other.

Statements:
{statements_text}

For each contradictory pair, output JSON:
[{{
  "idx_a": <number>,
  "idx_b": <number>,
  "contradiction_type": "rhetoric_reversal" | "factual_conflict" | "position_shift",
  "severity": "high" | "medium" | "low",
  "note": "brief explanation in Ukrainian (1 sentence)"
}}]

Definitions:
- rhetoric_reversal: speaker uses clearly opposite rhetoric in different statements
- factual_conflict: speaker states contradictory facts (dates, names, events)
- position_shift: speaker's stated position reverses over time

Return [] if no contradictions found. Return ONLY valid JSON array.
"""


def run_detect_contradictions(
    actor_id: str,
    db: Database,
    budget=None,
    run_dir: Path | None = None,
) -> list[dict]:
    statements = db.get_statements(actor_id)
    if len(statements) < 3:
        logger.info(f"[contradictions] {len(statements)} statements — skipping (need ≥3)")
        _save([], run_dir)
        return []

    compact_lines = []
    for i, s in enumerate(statements):
        quote = (s.get("quote") or "")[:200].strip()
        rtype = s.get("rhetoric_type") or "unknown"
        date = s.get("date") or ""
        compact_lines.append(f"[{i + 1}] [{rtype}] {date} — {quote}")

    result = _call_gemini("\n".join(compact_lines), budget)
    _save(result, run_dir)

    if result:
        logger.info(f"[contradictions] found {len(result)} contradiction(s)")
        for c in result:
            logger.info(
                f"[contradictions] [{c.get('severity', '?')}] "
                f"#{c.get('idx_a', '?')} vs #{c.get('idx_b', '?')}: "
                f"{c.get('note', '')[:80]}"
            )
    else:
        logger.info("[contradictions] none detected")

    return result


def _call_gemini(statements_text: str, budget) -> list[dict]:
    if budget is None:
        return []

    try:
        from google import genai as _genai
        from google.genai import types as _gtypes
    except ImportError:
        logger.warning("[contradictions] google-genai not installed")
        return []

    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        logger.debug("[contradictions] GEMINI_API_KEY not set")
        return []

    try:
        budget.check_service("gemini")
    except Exception as e:
        logger.info(f"[contradictions] budget limit: {e}")
        return []

    prompt = _CONTRADICTION_PROMPT.format(statements_text=statements_text)

    try:
        client = _genai.Client(api_key=api_key)
        for model_name in ("gemini-2.0-flash", "gemini-2.5-flash", "gemini-2.0-flash-lite"):
            try:
                resp = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=_gtypes.GenerateContentConfig(
                        system_instruction=LLM_SYSTEM_PROMPT,
                    ),
                )
                budget.consume("gemini", 1)
                raw = resp.text.strip()
                if raw.startswith("```"):
                    raw = "\n".join(raw.split("\n")[1:])
                if raw.endswith("```"):
                    raw = "\n".join(raw.split("\n")[:-1])
                return json.loads(raw)
            except Exception as e:
                err = str(e)
                if "429" in err or "RESOURCE_EXHAUSTED" in err.upper():
                    logger.debug("[contradictions] rate-limited")
                    return []
                logger.debug(f"[contradictions] {model_name} failed: {type(e).__name__}")
                continue
    except json.JSONDecodeError:
        logger.warning("[contradictions] non-JSON response from Gemini")
    except Exception as e:
        logger.error(f"[contradictions] error: {type(e).__name__}")
    return []


def _save(data: list[dict], run_dir: Path | None) -> None:
    if run_dir is None:
        return
    out = run_dir / "artifacts" / "contradictions.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
