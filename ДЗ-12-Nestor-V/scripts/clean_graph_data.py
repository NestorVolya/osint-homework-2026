"""
Clean DZ-12 graph CSV exports.

This script performs conservative duplicate cleanup for obvious near-duplicate
channel labels/usernames. It does not delete data silently: all aliases are
recorded in data/processed/deduplication_notes.md.
"""
from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NODES_IN = ROOT / "data" / "nodes_with_communities.csv"
EDGES_IN = ROOT / "data" / "edges_endorsements.csv"
OUT_DIR = ROOT / "data" / "processed"
NODES_OUT = OUT_DIR / "nodes_clean.csv"
EDGES_OUT = OUT_DIR / "edges_endorsements_clean.csv"
NOTES_OUT = OUT_DIR / "deduplication_notes.md"


def norm_label(value: str) -> str:
    value = (value or "").strip().strip('"').lower()
    value = re.sub(r"[^a-z0-9а-яіїєґ_]+", "", value)
    return value


def as_float(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    nodes = read_csv(NODES_IN)
    edges = read_csv(EDGES_IN)

    manual_alias_norm = {
        "moldovapolitcis": "moldovapolitics",
        "moldovapolitcs": "moldovapolitics",
        "modovapolitics": "moldovapolitics",
        "moldovapolitisc": "moldovapolitics",
        "molodovapolitics": "moldovapolitics",
        "moldovapolotics": "moldovapolitics",
        "moldovapoitics": "moldovapolitics",
        "moldovapoolitics": "moldovapolitics",
        "moldovapoltics": "moldovapolitics",
        "primulinm": "primulinmd",
    }

    by_norm: dict[str, dict[str, str]] = {}
    aliases: dict[str, str] = {}
    alias_notes: list[tuple[str, str, str]] = []

    # Prefer existing high-weight node as canonical.
    ordered = sorted(nodes, key=lambda n: as_float(n.get("weighted degree", "0")), reverse=True)
    for node in ordered:
        label = node.get("group_id") or node.get("Label", "")
        nlabel = norm_label(label)
        if not nlabel:
            by_norm[node["Id"]] = node
            continue

        target_norm = manual_alias_norm.get(nlabel)
        canonical = by_norm.get(target_norm) if target_norm else None

        if canonical:
            aliases[node["Id"]] = canonical["Id"]
            alias_notes.append((node.get("Label", ""), canonical.get("Label", ""), "manual typo alias"))
        else:
            by_norm[nlabel] = node
            aliases[node["Id"]] = node["Id"]

    canonical_ids = set(aliases.values())
    clean_nodes = [node for node in nodes if node["Id"] in canonical_ids]

    agg: dict[tuple[str, str], dict[str, str]] = {}
    for edge in edges:
        source = aliases.get(edge.get("Source", ""), edge.get("Source", ""))
        target = aliases.get(edge.get("Target", ""), edge.get("Target", ""))
        if not source or not target or source == target:
            continue
        key = (source, target)
        weight = as_float(edge.get("Weight", "0"))
        if key not in agg:
            merged = dict(edge)
            merged["Source"] = source
            merged["Target"] = target
            merged["Weight"] = str(int(weight) if weight.is_integer() else weight)
            agg[key] = merged
        else:
            current = agg[key]
            new_weight = as_float(current.get("Weight", "0")) + weight
            current["Weight"] = str(int(new_weight) if new_weight.is_integer() else new_weight)
            current["endorses_link_raw"] = ";".join(
                sorted(set(filter(None, [current.get("endorses_link_raw", ""), edge.get("endorses_link_raw", "")])))
            )
            current["endorses_message_id"] = ";".join(
                sorted(set(filter(None, [current.get("endorses_message_id", ""), edge.get("endorses_message_id", "")])))
            )

    clean_edges = list(agg.values())

    write_csv(NODES_OUT, clean_nodes, list(nodes[0].keys()))
    write_csv(EDGES_OUT, clean_edges, list(edges[0].keys()))

    with NOTES_OUT.open("w", encoding="utf-8") as f:
        f.write("# Deduplication Notes\n\n")
        f.write("Conservative cleanup based on near-duplicate labels/usernames.\n\n")
        f.write(f"- Input nodes: {len(nodes)}\n")
        f.write(f"- Output nodes: {len(clean_nodes)}\n")
        f.write(f"- Input edges: {len(edges)}\n")
        f.write(f"- Output edges: {len(clean_edges)}\n\n")
        f.write("## Aliases merged\n\n")
        if not alias_notes:
            f.write("No near-duplicate aliases were merged with the current threshold.\n")
        for alias, canonical, reason in alias_notes:
            f.write(f"- `{alias}` -> `{canonical}` ({reason})\n")
        f.write("\n## Noise policy\n\n")
        f.write("Technical bot/CTA nodes are retained in the clean graph but should be marked in role analysis instead of silently deleted.\n")

    print(f"nodes: {len(nodes)} -> {len(clean_nodes)}")
    print(f"edges: {len(edges)} -> {len(clean_edges)}")
    print(f"notes: {NOTES_OUT}")


if __name__ == "__main__":
    main()
