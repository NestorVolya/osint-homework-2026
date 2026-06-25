"""
Quality check: structural metrics + 5 gates → corpus_health_score.

run_quality_check(actor_id, db, collect_meta, profile_path) → dict
"""

import json
import math
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

import yaml
from loguru import logger

from pipeline.storage.db import Database

_ARCHIVE_DOMAINS = {"web.archive.org", "archive.today", "archive.is", "archive.ph"}
_RISK_RHETORIC = {"pro-russian", "bridge-building", "both-sides", "bothsides", "pro_russian"}
_ALL_TYPES = {"bio", "interview", "news", "project", "social", "academic", "other"}

_DEFAULT_PROFILE = Path(__file__).parent.parent / "benchmark_profiles" / "default.yaml"

_DEFAULT_WEIGHTS = {
    "coverage_diversity": 0.25,
    "depth_noise":        0.25,
    "risk_signal":        0.20,
    "archive_temporal":   0.15,
    "technical":          0.15,
}


def _domain(url: str) -> str:
    try:
        return urlparse(url).netloc.lower()
    except Exception:
        return ""


def _load_profile(profile_path: Path | None) -> dict:
    path = profile_path or _DEFAULT_PROFILE
    if not path.exists():
        logger.warning(f"[quality] profile not found: {path}, using empty thresholds")
        return {}
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _entropy(counts: dict) -> float:
    total = sum(counts.values())
    if total == 0 or len(counts) <= 1:
        return 0.0
    return -sum((c / total) * math.log2(c / total) for c in counts.values() if c > 0)


def _gate_status(value: float, threshold: dict) -> str:
    if "pass_min" in threshold:
        if value >= threshold["pass_min"]:
            return "PASS"
        if value >= threshold.get("warn_min", 0):
            return "WARN"
        return "FAIL"
    if "pass_max" in threshold:
        if value <= threshold["pass_max"]:
            return "PASS"
        if value <= threshold.get("warn_max", 1):
            return "WARN"
        return "FAIL"
    return "PASS"


def _date_to_ym(date_str: str) -> tuple[int, int] | None:
    """Convert YYYY / YYYY-MM / YYYY-MM-DD to (year, month). Returns None on failure."""
    if not date_str:
        return None
    parts = str(date_str).strip().split("-")
    try:
        year = int(parts[0])
        month = int(parts[1]) if len(parts) > 1 else 6
        if 1990 <= year <= 2100 and 1 <= month <= 12:
            return (year, month)
    except (ValueError, IndexError):
        pass
    return None


def _detect_temporal_gaps(events: list[dict], gap_months: int = 12) -> list[dict]:
    """Return list of gaps > gap_months between consecutive events with dates."""
    dated = sorted(
        (_date_to_ym(e.get("date", "")) for e in events),
        key=lambda x: x or (0, 0),
    )
    dated = [ym for ym in dated if ym is not None]
    gaps = []
    for i in range(1, len(dated)):
        y1, m1 = dated[i - 1]
        y2, m2 = dated[i]
        diff = (y2 - y1) * 12 + (m2 - m1)
        if diff > gap_months:
            gaps.append({
                "from": f"{y1:04d}-{m1:02d}",
                "to": f"{y2:04d}-{m2:02d}",
                "months": diff,
            })
    return gaps


def _worst(statuses: list[str]) -> str:
    for s in ("FAIL", "WARN", "PASS"):
        if s in statuses:
            return s
    return "PASS"


def _parse_flags(flags_raw) -> bool:
    if not flags_raw:
        return False
    try:
        flags = json.loads(flags_raw) if isinstance(flags_raw, str) else flags_raw
        return bool(flags)
    except Exception:
        return False


def run_quality_check(
    actor_id: str,
    db: Database,
    collect_meta: dict | None = None,
    profile_path: Path | None = None,
) -> dict:
    collect_meta = collect_meta or {}
    profile = _load_profile(profile_path)
    thresholds = profile.get("thresholds", {})
    weights = profile.get("weights", _DEFAULT_WEIGHTS)
    profile_id = profile.get("profile_id", "default")

    sources = db.get_sources(actor_id)
    statements = db.get_statements(actor_id)
    links = db.get_links()
    events = db.get_events(actor_id)

    n = len(sources)
    if n == 0:
        logger.warning("[quality] no sources — returning zero metrics")
        zero_metrics = {
            "source_count": 0, "unique_domains": 0, "source_diversity": 0.0,
            "type_entropy": 0.0, "type_counts": {}, "text_coverage": 0.0,
            "shallow_ratio": 0.0, "median_text_length": 0, "archive_ratio": 0.0,
            "risk_source_count": 0, "risk_rhetoric_count": 0,
            "archive_date_count": 0, "temporal_span_years": 0.0,
            "multi_year_coverage": 0.0, "statement_count": 0,
            "ru_domain_ratio": 0.0, "telegram_count": 0, "vk_ok_count": 0,
            "temporal_gaps": [],
        }
        return {
            "_profile_id": profile_id,
            "metrics": zero_metrics,
            "quality_gates": {},
            "corpus_health_score": 0.0,
            "quant_support": "weak",
            "auto_diagnostics": "Корпус порожній. Перевір роботу collect.",
        }

    # ── Group 1: Coverage & Diversity ────────────────────────────────────────
    domains = [_domain(s.get("url", "")) for s in sources if s.get("url")]
    unique_domains = {d for d in domains if d}
    source_diversity = len(unique_domains) / n

    type_counts = Counter(s.get("source_type") or "other" for s in sources)
    type_entropy = _entropy(type_counts) / math.log2(len(_ALL_TYPES))

    # ── Group 2: Depth & Noise ────────────────────────────────────────────────
    text_lengths = [len(s.get("text") or "") for s in sources]
    text_coverage = sum(1 for l in text_lengths if l > 200) / n
    shallow_ratio = sum(1 for l in text_lengths if l < 100) / n
    sorted_lens = sorted(text_lengths)
    mid = len(sorted_lens) // 2
    median_text_length = (sorted_lens[mid] + sorted_lens[~mid]) / 2

    # ── Group 3: Archive & Temporal ───────────────────────────────────────────
    archive_ratio = sum(
        1 for s in sources if _domain(s.get("url", "")) in _ARCHIVE_DOMAINS
    ) / n
    date_coverage = sum(
        1 for s in sources if s.get("date_raw") and str(s["date_raw"]).strip()
    ) / n

    # ── Platform coverage counts ──────────────────────────────────────────────
    telegram_count = sum(1 for s in sources if "t.me" in (s.get("url") or "").lower())
    vk_ok_count = sum(
        1 for s in sources
        if any(d in (s.get("url") or "").lower() for d in ["vk.com", "ok.ru"])
    )

    # ── Group 4: КР-специфічні ───────────────────────────────────────────────
    ru_domain_ratio = sum(
        1 for s in sources if _domain(s.get("url", "")).endswith(".ru")
    ) / n

    total_stmt = len(statements)
    rhetoric_risk_ratio = sum(
        1 for s in statements
        if (s.get("rhetoric_type") or "").lower().replace(" ", "-").replace("_", "-")
        in _RISK_RHETORIC
    ) / max(total_stmt, 1)

    total_links = len(links)
    risk_flag_ratio = sum(
        1 for lnk in links if _parse_flags(lnk.get("flags"))
    ) / max(total_links, 1)

    # ── Group 5: Technical ────────────────────────────────────────────────────
    hashes = [s.get("content_hash") or "" for s in sources]
    unique_hashes = len({h for h in hashes if h})
    duplicate_ratio = max(0.0, 1 - unique_hashes / n)

    rejected_ratio = collect_meta.get("rejected_ratio", 0.0)
    fetch_success_rate = collect_meta.get("fetch_success_rate", 1.0)
    fetched_total = collect_meta.get("fetched_total", n)

    # ── Metrics dict ─────────────────────────────────────────────────────────
    metrics = {
        "source_count": n,
        "unique_domains": len(unique_domains),
        "source_diversity": round(source_diversity, 4),
        "type_entropy": round(type_entropy, 4),
        "type_counts": dict(type_counts),
        "text_coverage": round(text_coverage, 4),
        "shallow_ratio": round(shallow_ratio, 4),
        "median_text_length": round(median_text_length),
        "archive_ratio": round(archive_ratio, 4),
        "date_coverage": round(date_coverage, 4),
        "ru_domain_ratio": round(ru_domain_ratio, 4),
        "rhetoric_risk_ratio": round(rhetoric_risk_ratio, 4),
        "risk_flag_ratio": round(risk_flag_ratio, 4),
        "duplicate_ratio": round(duplicate_ratio, 4),
        "rejected_ratio": round(rejected_ratio, 4),
        "fetch_success_rate": round(fetch_success_rate, 4),
        "fetched_total": fetched_total,
        "total_statements": total_stmt,
        "total_links": total_links,
        "telegram_count": telegram_count,
        "vk_ok_count": vk_ok_count,
    }

    # ── Gates ─────────────────────────────────────────────────────────────────
    def _t(key):
        return thresholds.get(key, {})

    gate_defs = {
        "coverage_diversity": [
            ("source_diversity", source_diversity),
            ("type_entropy",     type_entropy),
        ],
        "depth_noise": [
            ("text_coverage",        text_coverage),
            ("shallow_ratio",        shallow_ratio),
            ("median_text_length",   median_text_length),
        ],
        "archive_temporal": [
            ("archive_ratio",  archive_ratio),
            ("date_coverage",  date_coverage),
        ],
        "risk_signal": [
            ("ru_domain_ratio",       ru_domain_ratio),
            ("rhetoric_risk_ratio",   rhetoric_risk_ratio),
        ],
        "technical": [
            ("duplicate_ratio", duplicate_ratio),
        ],
    }

    quality_gates: dict[str, dict] = {}

    for gate_name, pairs in gate_defs.items():
        triggered: list[str] = []
        statuses: list[str] = []

        for metric_key, value in pairs:
            t = _t(metric_key)
            if not t:
                continue
            s = _gate_status(value, t)
            statuses.append(s)
            if s != "PASS":
                triggered.append(f"{metric_key}={value:.3f}")

        if gate_name == "coverage_diversity" and n < 10:
            statuses.append("FAIL")
            triggered.append(f"n={n}<10")

        status = _worst(statuses) if statuses else "PASS"
        gate_score = {"PASS": 1.0, "WARN": 0.5, "FAIL": 0.0}[status]

        quality_gates[gate_name] = {
            "status": status,
            "score": gate_score,
            "triggered_by": triggered,
            "summary": gate_name + ": " + status
            + ((" (" + ", ".join(triggered) + ")") if triggered else ""),
        }
        logger.info(
            f"[quality] gate {gate_name}: {status}"
            + (f" — {', '.join(triggered)}" if triggered else "")
        )

    # ── corpus_health_score ───────────────────────────────────────────────────
    total_weight = sum(weights.get(g, 0) for g in quality_gates)
    corpus_health_score = (
        sum(weights.get(g, 0) * v["score"] for g, v in quality_gates.items()) / total_weight
        if total_weight > 0 else 0.0
    )

    if corpus_health_score >= 0.7:
        quant_support = "strong"
    elif corpus_health_score >= 0.4:
        quant_support = "medium"
    else:
        quant_support = "weak"

    # ── auto_diagnostics ──────────────────────────────────────────────────────
    diag: list[str] = []
    if n < 20:
        diag.append(f"Малий корпус ({n} джерел), рекомендовано ≥20.")
    fail_gates = [g for g, v in quality_gates.items() if v["status"] == "FAIL"]
    warn_gates = [g for g, v in quality_gates.items() if v["status"] == "WARN"]
    if fail_gates:
        diag.append(f"FAIL gates: {', '.join(fail_gates)}.")
    if warn_gates:
        diag.append(f"WARN gates: {', '.join(warn_gates)}.")
    if ru_domain_ratio > 0.3:
        diag.append(f"RU-домени: {ru_domain_ratio:.0%} — перевір на пропаганду.")
    if source_diversity < 0.3:
        diag.append("Низька різноманітність джерел — кілька сторінок одного домену?")
    if not diag:
        diag.append("Корпус відповідає базовим структурним вимогам.")

    logger.info(
        f"[quality] health={corpus_health_score:.2f} ({quant_support}) "
        + " | ".join(f"{g}={v['status']}" for g, v in quality_gates.items())
    )

    temporal_gaps = _detect_temporal_gaps(events)
    if temporal_gaps:
        logger.info(f"[quality] temporal gaps: {len(temporal_gaps)}")

    return {
        "_profile_id": profile_id,
        "metrics": metrics,
        "quality_gates": quality_gates,
        "corpus_health_score": round(corpus_health_score, 4),
        "quant_support": quant_support,
        "auto_diagnostics": " ".join(diag),
        "temporal_gaps": temporal_gaps,
    }
