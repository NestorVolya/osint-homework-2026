"""
Geoclusters: aggregate events by period + location → geoclusters table.

Groups events by (year-period, location_id) and counts occurrences.
Period granularity: year (YYYY) derived from event date.
"""

import uuid
from loguru import logger

from pipeline.storage.db import Database


def _date_to_period(date: str) -> str:
    if not date:
        return "unknown"
    return date[:4]  # YYYY


def run_geoclusters(db: Database) -> list[dict]:
    events = db.get_events_with_location()
    if not events:
        logger.info("[geoclusters] no events with location, skipping")
        return []

    # aggregate: (period, location_id, type) → count
    agg: dict[tuple, int] = {}
    for ev in events:
        loc = ev.get("location_id")
        if not loc:
            continue
        period = _date_to_period(ev.get("date", ""))
        key = (period, loc, "event")
        agg[key] = agg.get(key, 0) + 1

    clusters = []
    for (period, location_id, ctype), count in agg.items():
        cluster_id = f"gc_{uuid.uuid4().hex[:8]}"
        db.insert_geocluster(
            cluster_id=cluster_id,
            type_=ctype,
            period=period,
            location_id=location_id,
            count=count,
        )
        clusters.append({
            "cluster_id": cluster_id,
            "period": period,
            "location_id": location_id,
            "count": count,
        })
        logger.info(f"[geoclusters] {period} / {location_id} → {count} events")

    logger.info(f"[geoclusters] clusters: {len(clusters)}")
    return clusters
