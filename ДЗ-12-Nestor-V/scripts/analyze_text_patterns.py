"""
Analyze DZ-12 message text patterns.

Input required:
  data/raw/groupint_messages.csv

Expected columns:
  message_id, group_id, group_title, date, text, urls

Outputs:
  data/processed/text_patterns.csv
  data/processed/synchronized_posts.csv
  data/processed/pattern_examples.md
  data/processed/narrative_patterns.csv
  data/processed/narrative_summary.md

This script intentionally does not invent narratives. It only reports exact or
near-duplicate text/link clusters present in the input CSV.
"""
from __future__ import annotations

import csv
import hashlib
import re
from collections import defaultdict
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "raw" / "groupint_messages.csv"
OUT_DIR = ROOT / "data" / "processed"
PATTERNS_CSV = OUT_DIR / "text_patterns.csv"
SYNC_CSV = OUT_DIR / "synchronized_posts.csv"
EXAMPLES_MD = OUT_DIR / "pattern_examples.md"
NARRATIVES_CSV = OUT_DIR / "narrative_patterns.csv"
NARRATIVES_MD = OUT_DIR / "narrative_summary.md"


def norm_text(value: str) -> str:
    value = value or ""
    value = value.lower()
    value = re.sub(r"https?://\S+|t\.me/\S+|@\w+", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def text_hash(value: str) -> str:
    return hashlib.sha256(norm_text(value).encode("utf-8")).hexdigest()[:16]


NARRATIVE_RULES = [
    ("anti_sandu_governance", ["санду", "диктатор", "коррупц", "кризис", "уничтож"]),
    ("transnistria_russia_protection", ["приднестров", "россиян", "защит", "одесс"]),
    ("gagauz_identity_history", ["гагауз", "язык", "культур", "истор"]),
    ("russian_language_identity", ["русск", "язык", "пушкин", "славян"]),
    ("russian_citizenship", ["российск", "гражданств", "указ", "посольств"]),
    ("anti_west_eu", ["европарламент", "евро", "запад", "ес"]),
]


def narrative_tags(text: str) -> list[str]:
    ntext = norm_text(text)
    tags = []
    for tag, keywords in NARRATIVE_RULES:
        hits = sum(1 for keyword in keywords if keyword in ntext)
        if hits >= 2:
            tags.append(tag)
    return tags


def parse_dt(value: str) -> datetime | None:
    if not value:
        return None
    value = value.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(value)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def load_rows() -> list[dict[str, str]]:
    if not INPUT.exists():
        raise SystemExit(f"Missing input: {INPUT}")
    with INPUT.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    required = {"message_id", "group_id", "date", "text"}
    missing = required - set(rows[0].keys() if rows else [])
    if missing:
        raise SystemExit(f"Missing columns in {INPUT}: {sorted(missing)}")
    return rows


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = load_rows()

    for row in rows:
        row["_norm_text"] = norm_text(row.get("text", ""))
        row["_text_hash"] = text_hash(row.get("text", ""))
        row["_dt"] = parse_dt(row.get("date", ""))

    exact_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        if len(row["_norm_text"]) >= 40:
            exact_groups[row["_text_hash"]].append(row)

    pattern_rows = []
    for h, items in exact_groups.items():
        channels = sorted({r.get("group_id", "") for r in items})
        if len(items) >= 2 and len(channels) >= 2:
            dated = [r for r in items if r["_dt"] is not None]
            dated.sort(key=lambda r: r["_dt"])
            first = dated[0] if dated else items[0]
            pattern_rows.append({
                "pattern_type": "same_text",
                "pattern_id": h,
                "count": str(len(items)),
                "channels": ";".join(channels),
                "first_seen_at": first["_dt"].isoformat() if first.get("_dt") else "",
                "first_seen_group": first.get("group_id", ""),
                "narrative_tags": ";".join(narrative_tags(items[0].get("text", ""))),
                "example_text": items[0].get("text", "")[:500],
            })

    # Conservative near-duplicate pass: compare only across channels and only
    # relatively short set to avoid O(n^2) blowups on large exports.
    candidate_rows = [r for r in rows if len(r["_norm_text"]) >= 80][:600]
    seen_pairs = set()
    for i, left in enumerate(candidate_rows):
        for right in candidate_rows[i + 1:]:
            if left.get("group_id") == right.get("group_id"):
                continue
            left_len = len(left["_norm_text"])
            right_len = len(right["_norm_text"])
            if min(left_len, right_len) / max(left_len, right_len) < 0.75:
                continue
            key = tuple(sorted((left.get("message_id", ""), right.get("message_id", ""))))
            if key in seen_pairs:
                continue
            seen_pairs.add(key)
            ratio = SequenceMatcher(None, left["_norm_text"], right["_norm_text"]).ratio()
            if ratio >= 0.86:
                pattern_rows.append({
                    "pattern_type": "similar_text",
                    "pattern_id": f"{left.get('message_id')}::{right.get('message_id')}",
                    "count": "2",
                    "channels": f"{left.get('group_id')};{right.get('group_id')}",
                    "first_seen_at": min(left["_dt"], right["_dt"]).isoformat() if left["_dt"] and right["_dt"] else "",
                    "first_seen_group": left.get("group_id") if left["_dt"] and right["_dt"] and left["_dt"] <= right["_dt"] else right.get("group_id"),
                    "narrative_tags": ";".join(narrative_tags(left.get("text", ""))),
                    "example_text": left.get("text", "")[:500],
                })

    with PATTERNS_CSV.open("w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "pattern_type", "pattern_id", "count", "channels",
            "first_seen_at", "first_seen_group", "narrative_tags", "example_text",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(pattern_rows)

    sync_rows = []
    grouped = defaultdict(list)
    for row in rows:
        if len(row["_norm_text"]) >= 40:
            grouped[row["_text_hash"]].append(row)
    for h, items in grouped.items():
        if len({r.get("group_id", "") for r in items}) < 2:
            continue
        dated = [r for r in items if r["_dt"] is not None]
        dated.sort(key=lambda r: r["_dt"])
        if not dated:
            continue
        first_by_channel = {}
        for item in dated:
            first_by_channel.setdefault(item.get("group_id", ""), item)
        channel_items = list(first_by_channel.values())
        channel_items.sort(key=lambda r: r["_dt"])
        first = channel_items[0]
        last = channel_items[-1]
        delta = (last["_dt"] - first["_dt"]).total_seconds() / 60
        if delta <= 60 and len(channel_items) >= 2:
            channels = sorted({r.get("group_id", "") for r in channel_items})
            sync_rows.append({
                "pattern_id": h,
                "window_start": first["_dt"].isoformat(),
                "window_end": last["_dt"].isoformat(),
                "window_minutes": f"{delta:.1f}",
                "message_count": str(len(channel_items)),
                "channels": ";".join(channels),
                "first_seen_group": first.get("group_id", ""),
                "narrative_tags": ";".join(narrative_tags(first.get("text", ""))),
                "example_text": first.get("text", "")[:500],
            })

    with SYNC_CSV.open("w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "pattern_id", "window_start", "window_end", "window_minutes",
            "message_count", "channels", "first_seen_group", "narrative_tags", "example_text",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sync_rows)

    narrative_rows = []
    for row in pattern_rows:
        for tag in filter(None, row.get("narrative_tags", "").split(";")):
            narrative_rows.append({
                "narrative_tag": tag,
                "pattern_id": row["pattern_id"],
                "pattern_type": row["pattern_type"],
                "channels": row["channels"],
                "first_seen_at": row.get("first_seen_at", ""),
                "first_seen_group": row.get("first_seen_group", ""),
                "example_text": row["example_text"],
            })

    with NARRATIVES_CSV.open("w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "narrative_tag", "pattern_id", "pattern_type", "channels",
            "first_seen_at", "first_seen_group", "example_text",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(narrative_rows)

    with EXAMPLES_MD.open("w", encoding="utf-8") as f:
        f.write("# Pattern Examples\n\n")
        f.write("Generated from `data/raw/groupint_messages.csv`.\n\n")
        f.write("## Exact / Similar Text Patterns\n\n")
        if not pattern_rows:
            f.write("No cross-channel exact or near-duplicate text patterns found with the current thresholds.\n")
        for row in pattern_rows[:20]:
            f.write(f"- `{row['pattern_type']}` across `{row['channels']}`: {row['example_text']}\n")
        f.write("\n## Synchronized Posts\n\n")
        if not sync_rows:
            f.write("No cross-channel synchronized exact-text posts found in 60-minute windows.\n")
        for row in sync_rows[:20]:
            f.write(
                f"- `{row['window_start']}` to `{row['window_end']}` "
                f"({row['window_minutes']} min) across `{row['channels']}`: "
                f"{row['example_text']}\n"
            )

    with NARRATIVES_MD.open("w", encoding="utf-8") as f:
        f.write("# Narrative Summary\n\n")
        f.write("Generated from repeated exact/near-duplicate text patterns. Tags are analyst-coded keyword categories, not proof of intent.\n\n")
        if not narrative_rows:
            f.write("No repeated text patterns matched the conservative narrative keyword rules.\n")
        by_tag = defaultdict(list)
        for row in narrative_rows:
            by_tag[row["narrative_tag"]].append(row)
        for tag, items in sorted(by_tag.items(), key=lambda kv: len(kv[1]), reverse=True):
            f.write(f"## `{tag}` ({len(items)} patterns)\n\n")
            for row in items[:5]:
                f.write(
                    f"- channels `{row['channels']}`, first seen `{row['first_seen_group']}` "
                    f"at `{row['first_seen_at']}`: {row['example_text'][:300]}\n"
                )
            f.write("\n")

    print(f"patterns: {len(pattern_rows)} -> {PATTERNS_CSV}")
    print(f"synchronized windows: {len(sync_rows)} -> {SYNC_CSV}")
    print(f"narrative patterns: {len(narrative_rows)} -> {NARRATIVES_CSV}")
    print(f"examples: {EXAMPLES_MD}")


if __name__ == "__main__":
    main()
