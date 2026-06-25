"""
Markdown quality report: 7-section template with auto-filled quant sections.

run_report_md(quality_report, seed, run_dir, actor_id, run_id) → Path
Saves to run_dir/report/report_quality.md
"""
from datetime import datetime, timezone
from pathlib import Path

from loguru import logger

from pipeline.dstu import dstu_cite

_GATE_BADGE = {"PASS": "[PASS]", "WARN": "[WARN]", "FAIL": "[FAIL]"}
_SUPPORT_LABEL = {"strong": "strong (>=0.7)", "medium": "medium (0.4-0.7)", "weak": "weak (<0.4)"}

_GATE_LABELS = {
    "coverage_diversity": "Coverage & Diversity",
    "depth_noise":        "Depth & Noise",
    "archive_temporal":   "Archive & Temporal",
    "risk_signal":        "Risk Signal",
    "technical":          "Technical",
}

_SEC8_GLOSSARY = """\
## 8. Пояснення критеріїв якості

### Gates (5 блоків перевірки)

| Gate | Що перевіряє |
|------|-------------|
| Coverage & Diversity | Джерела різноманітні: ≥35% унікальних доменів, mix типів (bio/news/interview/…). Захист від домінування одного сайту. |
| Depth & Noise | Тексти змістовні: shallow_ratio ≤10% (не більше 10% порожніх сторінок), медіанний текст ≥300 символів. |
| Archive & Temporal | Не переважно архів: archive_ratio ≤50%. Хоча б 20% джерел мають дату — для побудови timeline. |
| Risk Signal | Мало RU-доменів (≤60%) і риторично ризикованих висловлювань (≤35% pro-russian). |
| Technical | Нуль або мінімум дублікатів (≤15% за content hash). |

### Основні метрики

| Метрика | Значення |
|---------|---------|
| source_diversity | Частка унікальних доменів від загальної кількості джерел |
| type_entropy | Різноманіття типів джерел (0 = всі однакові, 1 = рівномірний розподіл) |
| shallow_ratio | Частка джерел з текстом < 100 символів (пустишки/заголовки) |
| duplicate_ratio | Частка дублікатів за content hash |
| ru_domain_ratio | Частка .ru / RU-медіа доменів |
| rhetoric_risk_ratio | Частка висловлювань, класифікованих як pro-russian (потребує Gemini NER) |
| date_coverage | Частка джерел з датою публікації |
| archive_ratio | Частка джерел з web.archive.org |

### Порогові значення

Задаються у профілі (`benchmark_profiles/*.yaml`). Поточний профіль: `{profile_id}`.
PASS = норма. WARN = увага, але не критично. FAIL = проблема з корпусом.
"""


def _pct(v: float) -> str:
    return f"{v * 100:.1f}%"


def _load_sources(run_dir: Path, actor_id: str) -> list[dict]:
    db_path = run_dir / "artifacts" / "records.sqlite"
    if not db_path.exists():
        return []
    try:
        from pipeline.storage.db import Database
        db = Database(db_path)
        rows = db.get_sources(actor_id)
        db.close()
        return rows
    except Exception:
        return []


def run_report_md(
    quality_report: dict,
    seed: str,
    run_dir: Path,
    actor_id: str = "",
    run_id: str = "",
) -> Path:
    report_dir = run_dir / "report"
    report_dir.mkdir(exist_ok=True)

    m = quality_report.get("metrics", {})
    gates = quality_report.get("quality_gates", {})
    chs = quality_report.get("corpus_health_score", 0.0)
    qs = quality_report.get("quant_support", "weak")
    diag = quality_report.get("auto_diagnostics", "")
    profile_id = quality_report.get("_profile_id", "default")
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    run_label = run_id or run_dir.name

    # ── Section 1: Passport ───────────────────────────────────────────────────
    gate_rows = "\n".join(
        "| {} | {} | {} |".format(
            _GATE_LABELS.get(g, g),
            _GATE_BADGE.get(v["status"], v["status"]),
            "; ".join(v.get("triggered_by", [])) or "—",
        )
        for g, v in gates.items()
    )

    sec1 = """\
## 1. Паспорт

| Параметр | Значення |
|---|---|
| Actor | `{seed}` |
| Run ID | `{run}` |
| Actor ID | `{aid}` |
| Profile | `{pid}` |
| Дата | {now} |
| Corpus Health Score | **{chs:.2f}** — {qs_label} |
| Джерел | {n} (унікальних доменів: {ud}) |

### Gate Summary

| Gate | Статус | Тригери |
|---|---|---|
{gate_rows}
""".format(
        seed=seed, run=run_label, aid=actor_id, pid=profile_id, now=now_str,
        chs=chs, qs_label=_SUPPORT_LABEL.get(qs, qs),
        n=m.get("source_count", 0), ud=m.get("unique_domains", 0),
        gate_rows=gate_rows,
    )

    # ── Section 2: Research questions (TODO) ─────────────────────────────────
    sec2 = """\
## 2. Дослідницькі питання

<!-- TODO аналітик: сформулюй 3-5 ключових питань цього досьє -->
- [ ] ?
- [ ] ?
- [ ] ?
"""

    # ── Section 3: Quant corpus state (auto) ─────────────────────────────────
    type_counts = m.get("type_counts", {})
    n_src = max(m.get("source_count", 1), 1)
    type_rows = "\n".join(
        "| {} | {} | {} |".format(k, v, _pct(v / n_src))
        for k, v in sorted(type_counts.items(), key=lambda x: -x[1])
    )

    sec3 = """\
## 3. Кількісний стан корпусу

### Метрики

| Метрика | Значення |
|---|---|
| Джерел (n) | {n} |
| Унікальних доменів | {ud} |
| Source diversity | {div} |
| Type entropy (norm) | {ent} |
| Text coverage (>200 chars) | {tc} |
| Shallow ratio (<100 chars) | {sr} |
| Median text length | {mtl} chars |
| Archive ratio | {ar} |
| Date coverage | {dc} |
| RU-domain ratio | {rdr} |
| Rhetoric risk ratio | {rrr} |
| Duplicate ratio | {dr} |
| Rejected ratio | {rr} |
| Fetched total | {ft} |

### Типи джерел

| Тип | Кількість | % |
|---|---|---|
{type_rows}

### Авто-діагностика

> {diag}
""".format(
        n=m.get("source_count", 0),
        ud=m.get("unique_domains", 0),
        div=_pct(m.get("source_diversity", 0)),
        ent=_pct(m.get("type_entropy", 0)),
        tc=_pct(m.get("text_coverage", 0)),
        sr=_pct(m.get("shallow_ratio", 0)),
        mtl=m.get("median_text_length", 0),
        ar=_pct(m.get("archive_ratio", 0)),
        dc=_pct(m.get("date_coverage", 0)),
        rdr=_pct(m.get("ru_domain_ratio", 0)),
        rrr=_pct(m.get("rhetoric_risk_ratio", 0)),
        dr=_pct(m.get("duplicate_ratio", 0)),
        rr=_pct(m.get("rejected_ratio", 0)),
        ft=m.get("fetched_total", 0),
        type_rows=type_rows,
        diag=diag,
    )

    # ── Section 4: ДСТУ 8302:2015 bibliography (auto) ───────────────────────
    sources = _load_sources(run_dir, actor_id)
    if sources:
        dstu_lines = "\n".join(
            f"{i}. {dstu_cite(dict(s))}"
            for i, s in enumerate(sources, 1)
        )
        sec4 = f"""\
## 4. Бібліографія джерел (ДСТУ 8302:2015)

{dstu_lines}

<!-- TODO аналітик: видали нерелевантні, додай власні -->
"""
    else:
        sec4 = """\
## 4. Бібліографія джерел (ДСТУ 8302:2015)

<!-- TODO аналітик: заповни бібліографічний список -->
"""

    # ── Section 5: Findings ───────────────────────────────────────────────────
    sec5 = """\
## 5. Знахідки

<!-- TODO аналітик: перелічи конкретні знахідки F1, F2... -->

| ID | Знахідка | Quant support | Qual confidence | Примітка |
|---|---|---|---|---|
| F1 | [TODO] | {qs} | [TODO] | |
| F2 | [TODO] | {qs} | [TODO] | |

*Quant support auto = `{qs}` (corpus health score = {chs:.2f})*
""".format(qs=qs, chs=chs)

    # ── Section 6: Quant×Qual integration ────────────────────────────────────
    ru_level = "high" if m.get("ru_domain_ratio", 0) > 0.3 else "low"
    rhet_level = "detected" if m.get("rhetoric_risk_ratio", 0) > 0 else "none"

    sec6 = """\
## 6. Інтеграція quant × qual

| Вимір | Auto (quant) | Аналітик (qual) | Інтегровано |
|---|---|---|---|
| Надійність корпусу | {qs} | [TODO] | [TODO] |
| RU-ризик | {ru} | [TODO] | [TODO] |
| Риторичний ризик | {rh} | [TODO] | [TODO] |
""".format(qs=qs, ru=ru_level, rh=rhet_level)

    # ── Section 7: Limitations + actions ─────────────────────────────────────
    gap_lines: list[str] = []
    if m.get("source_count", 0) < 20:
        gap_lines.append(
            f"- Малий корпус ({m.get('source_count', 0)} джерел) — збільши через додаткові запити"
        )
    if m.get("ru_domain_ratio", 0) > 0.3:
        gap_lines.append(
            f"- RU-домени {_pct(m.get('ru_domain_ratio', 0))} — перевір кожне джерело клас B вручну"
        )
    if m.get("date_coverage", 0) < 0.3:
        gap_lines.append(
            "- Низьке date_coverage — хронологічні висновки ненадійні"
        )
    fail_gates = [_GATE_LABELS.get(g, g) for g, v in gates.items() if v["status"] == "FAIL"]
    if fail_gates:
        gap_lines.append(f"- Провалені gates: {', '.join(fail_gates)}")
    if not gap_lines:
        gap_lines.append("- Структурних прогалин не виявлено")

    # ── Platform coverage: не перевірено ──────────────────────────────────────
    not_checked: list[str] = []
    if m.get("telegram_count", 0) == 0:
        not_checked.append("- **Telegram** (t.me): джерел не знайдено — blind zone")
    if m.get("vk_ok_count", 0) == 0:
        not_checked.append("- **VK / OK** (vk.com, ok.ru): не перевірено (потребує окремого adapter)")
    if m.get("ru_domain_ratio", 0) < 0.05:
        not_checked.append("- **.ru медіа**: покриття відсутнє або мінімальне")
    not_checked.append("- **Reverse image / geosearch**: не реалізовано")
    not_checked.append("- **Dzen / Rutube / YDB**: поза поточним coverage")

    # ── Temporal gaps ──────────────────────────────────────────────────────────
    temporal_gaps = quality_report.get("temporal_gaps", [])
    if temporal_gaps:
        tgap_lines = [
            f"- {g['from']} → {g['to']} ({g['months']} міс.)"
            for g in temporal_gaps
        ]
        tgap_sec = "### Часові прогалини в таймлайні (auto)\n\n" + "\n".join(tgap_lines) + "\n"
    else:
        tgap_sec = "### Часові прогалини в таймлайні (auto)\n\n- Не виявлено\n"

    # ── Contradiction summary ──────────────────────────────────────────────────
    contradictions_path = run_dir / "artifacts" / "contradictions.json"
    contradictions: list[dict] = []
    if contradictions_path.exists():
        try:
            import json as _json
            contradictions = _json.loads(contradictions_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    if contradictions:
        cont_lines = [
            f"- [{c.get('severity','?').upper()}] "
            f"#{c.get('idx_a','?')} vs #{c.get('idx_b','?')} "
            f"({c.get('contradiction_type','?')}): {c.get('note','')}"
            for c in contradictions
        ]
        cont_sec = (
            "### Суперечності між statements (auto)\n\n"
            + "\n".join(cont_lines)
            + "\n\n*Потребує ручної верифікації аналітиком.*\n"
        )
    else:
        cont_sec = "### Суперечності між statements (auto)\n\n- Не виявлено\n"

    sec7 = """\
## 7. Обмеження та дії

### Структурні прогалини (auto)

{gaps}

### Не перевірено (blind zones)

{not_checked}

{tgap_sec}
{cont_sec}
### Аналітичні нотатки

<!-- TODO аналітик -->
""".format(
        gaps="\n".join(gap_lines),
        not_checked="\n".join(not_checked),
        tgap_sec=tgap_sec,
        cont_sec=cont_sec,
    )

    # ── Assemble ──────────────────────────────────────────────────────────────
    md = (
        f"# OSINT Quality Report — {seed} ({now_str})\n\n"
        f"> **Actor ID:** `{actor_id}` | **Run:** `{run_label}` | **Profile:** `{profile_id}`\n\n"
        + sec1 + "\n"
        + sec2 + "\n"
        + sec3 + "\n"
        + sec4 + "\n"
        + sec5 + "\n"
        + sec6 + "\n"
        + sec7 + "\n"
        + _SEC8_GLOSSARY.format(profile_id=profile_id)
    )

    out = report_dir / "report_quality.md"
    out.write_text(md, encoding="utf-8")
    logger.info(f"[report_md] written → {out}")
    return out
