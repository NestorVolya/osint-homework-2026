"""
Bridge export: actor-osint-front-СС → osint-base (ADR-007).

Read-only export — generates JSON package compatible with mnt_records schema.
Does NOT write to any database. The package is for manual or scripted import.

Usage:
    python scripts/export_to_osint_base.py \
        --run output/2026-05-29_01-24-51 \
        --seed "Олексій Чекаль" \
        --out bridge_export.json

Output format (bridge_export.json):
    {
        "meta": {...},
        "SOURCE": [...],   # mnt_records type=SOURCE
        "QUOTE": [...],    # mnt_records type=QUOTE
        "ENTITY": [...]    # mnt_records type=ENTITY (risk-flagged links)
    }

Schema reference: osint-base/schema.sql (mnt_records table)
ADR: DECISIONS.md#ADR-007
"""

import argparse
import json
import re
import sqlite3
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from pipeline.dstu import dstu_cite


def _extract_domain(url: str) -> str:
    try:
        return urlparse(url).netloc.lstrip("www.")
    except Exception:
        return ""


def _parse_date(raw: str | None) -> str | None:
    if not raw:
        return None
    m = re.search(r"(\d{4}-\d{2}-\d{2})", raw)
    if m:
        return m.group(1)
    m = re.search(r"\b(20\d\d|19\d\d)\b", raw)
    if m:
        return f"{m.group(1)}-01-01"
    return None


def _load_db(run_dir: Path) -> sqlite3.Connection:
    db_path = run_dir / "artifacts" / "records.sqlite"
    if not db_path.exists():
        raise FileNotFoundError(f"DB not found: {db_path}")
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def export_sources(conn: sqlite3.Connection, seed: str) -> list[dict]:
    rows = conn.execute("SELECT * FROM sources").fetchall()
    today = date.today().strftime("%d.%m.%Y")
    records = []
    for r in rows:
        r = dict(r)
        records.append({
            "id": f"src_{r['source_id']}",
            "type": "SOURCE",
            "actor_topic": seed,
            "source_url": r.get("url"),
            "source_domain": _extract_domain(r.get("url") or ""),
            "source_type": r.get("source_type"),
            "date_published": _parse_date(r.get("date_raw")),
            "date_discovered": date.today().isoformat(),
            "content": r.get("title"),
            "notes": (r.get("text") or "")[:500],
            "source_dstu": dstu_cite(r, today),
            "status": "НЕПІДТВЕРДЖЕНО",
            "tags": [r["source_type"]] if r.get("source_type") else [],
            "_provenance": {
                "pipeline": "actor-osint-front-СС",
                "source_id": r["source_id"],
                "actor_id": r.get("actor_id"),
                "collected_at": r.get("collected_at"),
            },
        })
    return records


def export_quotes(conn: sqlite3.Connection, seed: str) -> list[dict]:
    rows = conn.execute("SELECT * FROM statements").fetchall()
    records = []
    for r in rows:
        r = dict(r)
        tags = []
        if r.get("rhetoric_type"):
            tags.append(r["rhetoric_type"])
        if r.get("war_context"):
            tags.append(r["war_context"])
        records.append({
            "id": f"qte_{r['statement_id']}",
            "type": "QUOTE",
            "actor_topic": seed,
            "source_url": None,
            "date_event": _parse_date(r.get("date")),
            "date_discovered": date.today().isoformat(),
            "quote": r.get("quote"),
            "content": r.get("summary"),
            "context": r.get("platform"),
            "status": "НЕПІДТВЕРДЖЕНО",
            "tags": tags,
            "_provenance": {
                "pipeline": "actor-osint-front-СС",
                "statement_id": r["statement_id"],
                "source_id": r.get("source_id"),
                "actor_id": r.get("actor_id"),
            },
        })
    return records


def export_entities(conn: sqlite3.Connection, seed: str) -> list[dict]:
    rows = conn.execute(
        "SELECT * FROM links WHERE flags IS NOT NULL AND flags != '[]'"
    ).fetchall()
    seen: set[str] = set()
    records = []
    for r in rows:
        r = dict(r)
        subj = r.get("subject_b", "")
        if subj in seen:
            continue
        seen.add(subj)
        try:
            flags = json.loads(r.get("flags") or "[]")
        except (json.JSONDecodeError, TypeError):
            flags = []
        if not flags:
            continue
        records.append({
            "id": f"ent_{r['link_id']}",
            "type": "ENTITY",
            "actor_topic": seed,
            "content": subj,
            "context": r.get("context"),
            "temporal_context": r.get("period"),
            "mention_type": r.get("link_type"),
            "date_discovered": date.today().isoformat(),
            "status": "НЕПІДТВЕРДЖЕНО",
            "tags": flags,
            "_provenance": {
                "pipeline": "actor-osint-front-СС",
                "link_id": r["link_id"],
                "source_id": r.get("source_id"),
            },
        })
    return records


def main():
    p = argparse.ArgumentParser(description="Export pipeline run → osint-base bridge package")
    p.add_argument("--run", required=True, help="Path to run dir (output/YYYY-MM-DD_...)")
    p.add_argument("--seed", default="", help="Actor seed name (for actor_topic field)")
    p.add_argument("--out", default="bridge_export.json", help="Output JSON path")
    args = p.parse_args()

    run_dir = Path(args.run)
    if not run_dir.exists():
        print(f"ERROR: run dir not found: {run_dir}", file=sys.stderr)
        sys.exit(1)

    conn = _load_db(run_dir)

    sources = export_sources(conn, args.seed)
    quotes = export_quotes(conn, args.seed)
    entities = export_entities(conn, args.seed)
    conn.close()

    package = {
        "meta": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "pipeline": "actor-osint-front-СС",
            "run_dir": str(run_dir),
            "seed": args.seed,
            "counts": {
                "SOURCE": len(sources),
                "QUOTE": len(quotes),
                "ENTITY": len(entities),
            },
            "schema_ref": "osint-base/schema.sql (mnt_records)",
            "note": "Read-only export. Review before import. No write-back performed.",
        },
        "SOURCE": sources,
        "QUOTE": quotes,
        "ENTITY": entities,
    }

    out_path = Path(args.out)
    out_path.write_text(json.dumps(package, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Bridge export → {out_path}")
    print(f"  SOURCE: {len(sources)} | QUOTE: {len(quotes)} | ENTITY: {len(entities)}")


if __name__ == "__main__":
    main()
