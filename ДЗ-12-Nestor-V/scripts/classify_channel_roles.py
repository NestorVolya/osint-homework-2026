"""
Classify channel roles for DZ-12 from graph exports.

Inputs:
  data/processed/nodes_clean.csv if present, else data/nodes_with_communities.csv
  data/processed/edges_endorsements_clean.csv if present, else data/edges_endorsements.csv

Output:
  data/processed/channel_roles.csv
"""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "processed"
NODES = OUT_DIR / "nodes_clean.csv"
EDGES = OUT_DIR / "edges_endorsements_clean.csv"
if not NODES.exists():
    NODES = ROOT / "data" / "nodes_with_communities.csv"
if not EDGES.exists():
    EDGES = ROOT / "data" / "edges_endorsements.csv"
OUT = OUT_DIR / "channel_roles.csv"


def as_float(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    nodes = load_csv(NODES)
    edges = load_csv(EDGES)

    incoming_weight = defaultdict(float)
    outgoing_weight = defaultdict(float)
    incoming_count = defaultdict(int)
    outgoing_count = defaultdict(int)
    for edge in edges:
        source = edge.get("Source", "")
        target = edge.get("Target", "")
        weight = as_float(edge.get("Weight", "0"))
        outgoing_weight[source] += weight
        incoming_weight[target] += weight
        outgoing_count[source] += 1
        incoming_count[target] += 1

    rows = []
    for node in nodes:
        node_id = node.get("Id", "")
        label = node.get("Label", "").strip('"')
        wd = as_float(node.get("weighted degree", "0"))
        out_w = outgoing_weight[node_id]
        in_w = incoming_weight[node_id]
        bc = as_float(node.get("betweenesscentrality", node.get("Betweenness Centrality", "0")))

        roles = []
        if out_w >= 50 or outgoing_count[node_id] >= 10:
            roles.append("retransmitter")
        if in_w >= 50:
            roles.append("primary_source_candidate")
        if wd >= 50:
            roles.append("amplifier")
        if bc > 0:
            roles.append("bridge")
        if not roles:
            roles.append("peripheral")

        rows.append({
            "Id": node_id,
            "Label": label,
            "cluster": node.get("modularity_class", ""),
            "weighted_degree": str(int(wd) if wd.is_integer() else wd),
            "incoming_weight": str(int(in_w) if in_w.is_integer() else in_w),
            "outgoing_weight": str(int(out_w) if out_w.is_integer() else out_w),
            "incoming_edges": str(incoming_count[node_id]),
            "outgoing_edges": str(outgoing_count[node_id]),
            "betweenness": str(bc),
            "roles": ";".join(roles),
            "role_note": "heuristic from ENDORSES graph; primary source requires text/timestamp confirmation",
        })

    rows.sort(key=lambda r: (as_float(r["weighted_degree"]), as_float(r["outgoing_weight"])), reverse=True)
    with OUT.open("w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "Id", "Label", "cluster", "weighted_degree", "incoming_weight",
            "outgoing_weight", "incoming_edges", "outgoing_edges",
            "betweenness", "roles", "role_note",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
