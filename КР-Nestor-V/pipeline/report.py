import json
from collections import Counter
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from markupsafe import Markup
from loguru import logger

from pipeline.storage.db import Database
from pipeline.dstu import dstu_cite


def run_report(
    actor_id: str,
    seed: str,
    db: Database,
    run_dir: Path,
    templates_dir: Path,
    quality_report: dict | None = None,
) -> Path:
    report_dir = run_dir / "report"
    report_dir.mkdir(exist_ok=True)

    sources = db.get_sources(actor_id)
    events = db.get_events(actor_id)
    statements = db.get_statements(actor_id)
    links_raw = db.get_links()
    accounts = db.get_accounts()
    geoclusters = db.get_geoclusters()

    env = Environment(loader=FileSystemLoader(str(templates_dir)), autoescape=True)

    env.filters["dstu_cite"] = lambda s: dstu_cite(dict(s))

    def _tojson_safe(v: object) -> Markup:
        # escape </ to prevent </script> injection; return Markup so Jinja2
        # doesn't double-escape it in autoescape mode
        s = json.dumps(v, ensure_ascii=False).replace("</", r"<\/")
        return Markup(s)

    env.filters["tojson"] = _tojson_safe

    try:
        tmpl = env.get_template("report.html.j2")
    except Exception:
        logger.warning("[report] template not found, writing minimal HTML")
        out = report_dir / "report.html"
        out.write_text(
            f"<h1>Actor: {seed}</h1>"
            f"<p>Sources: {len(sources)} | Events: {len(events)} | "
            f"Statements: {len(statements)} | Links: {len(links_raw)}</p>",
            encoding="utf-8",
        )
        return out

    sources_map = {s["source_id"]: s for s in sources}

    locations_map: dict[str, dict] = {}
    if geoclusters:
        for r in db.conn.execute("SELECT * FROM locations").fetchall():
            rd = dict(r)
            locations_map[rd["location_id"]] = rd

    # parse flags JSON, dedup links by subject_b (keep highest-flag first)
    seen_subjects: set[str] = set()
    deduped_links: list[dict] = []
    for lnk in sorted(links_raw, key=lambda x: len(x.get("flags") or ""), reverse=True):
        lnk = dict(lnk)
        try:
            lnk["flags"] = json.loads(lnk["flags"]) if lnk.get("flags") else []
        except (json.JSONDecodeError, TypeError):
            lnk["flags"] = []
        subj = lnk.get("subject_b", "")
        if subj not in seen_subjects:
            seen_subjects.add(subj)
            deduped_links.append(lnk)
    links_display = deduped_links[:50]

    statements = sorted(statements, key=lambda s: s.get("date") or "9999")

    # summary stats
    rhetoric_counts = dict(Counter(
        s.get("rhetoric_type") or "unknown" for s in statements
    ))
    source_type_counts = dict(Counter(
        s.get("source_type") or "other" for s in sources
    ))
    risk_entities = [l for l in links_display if l.get("flags")][:8]

    # export payloads as Python objects — template renders via | tojson (safe)
    _STMT_KEYS = ["statement_id", "date", "quote", "summary", "platform",
                  "rhetoric_type", "war_context", "source_id"]
    _SRC_KEYS = ["source_id", "source_type", "title", "url", "date_raw"]
    statements_export = [{k: s.get(k, "") for k in _STMT_KEYS} for s in statements]
    sources_export = [{k: s.get(k, "") for k in _SRC_KEYS} for s in sources]

    qr = quality_report or {}

    contradictions: list[dict] = []
    _cont_path = run_dir / "artifacts" / "contradictions.json"
    if _cont_path.exists():
        try:
            contradictions = json.loads(_cont_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    temporal_gaps = qr.get("temporal_gaps") or []

    html = tmpl.render(
        seed=seed,
        actor_id=actor_id,
        sources=sources,
        sources_map=sources_map,
        events=events,
        statements=statements,
        links=links_display,
        accounts=accounts,
        geoclusters=geoclusters,
        locations_map=locations_map,
        rhetoric_counts=rhetoric_counts,
        source_type_counts=source_type_counts,
        risk_entities=risk_entities,
        statements_export=statements_export,
        sources_export=sources_export,
        corpus_health_score=qr.get("corpus_health_score"),
        quant_support=qr.get("quant_support"),
        quality_gates=qr.get("quality_gates", {}),
        quality_metrics=qr.get("metrics", {}),
        quality_diagnostics=qr.get("auto_diagnostics", ""),
        contradictions=contradictions,
        temporal_gaps=temporal_gaps,
    )
    out = report_dir / "report.html"
    out.write_text(html, encoding="utf-8")
    logger.info(f"[report] written → {out}")
    return out
