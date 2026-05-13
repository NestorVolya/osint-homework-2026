"""
build_graph.py — Patent similarity graph builder for ДЗ-06

Input:  patents_full_enrichment_0304.xlsx
Output: data/patents_graph.gexf
        homework_cluster_summaries/nodes_base.csv
"""

import os
import sys
import time
import pandas as pd
import networkx as nx
from networkx.algorithms.community import louvain_communities

XLSX_PATH = r"D:\Documents\!!Діалогерство\!УСБ\ПРОГРАМИ, Бази\patents_full_enrichment_0304.xlsx"
GEXF_OUT  = r"data\patents_graph.gexf"
CSV_OUT   = r"homework_cluster_summaries\nodes_base.csv"


def load_data(path):
    print("Loading Elements...")
    elements = pd.read_excel(path, sheet_name="Elements", engine="openpyxl")
    elements.columns = ["Colour", "Label", "Type", "Tags", "PatentID", "Title", "Priority", "URL"]

    print("Loading Connections...")
    connections = pd.read_excel(path, sheet_name="Connections", engine="openpyxl")
    connections.columns = ["Source", "Target", "Type", "Tags", "Description"]

    return elements, connections


def build_graph(elements, connections):
    # Filter out irrelevant nodes
    keep = elements[elements["Colour"] != "irrelevant"].copy()
    keep_ids = set(keep["PatentID"].astype(str))
    print(f"Nodes after filtering irrelevant: {len(keep_ids)}")

    # Filter edges — both endpoints must be in keep set
    edges = connections[
        connections["Source"].astype(str).isin(keep_ids) &
        connections["Target"].astype(str).isin(keep_ids)
    ]
    print(f"Edges after filtering: {len(edges)}")

    G = nx.Graph()

    # Add nodes with attributes
    for _, row in keep.iterrows():
        node_id = str(row["PatentID"])
        G.add_node(
            node_id,
            label=str(row["Label"]),
            colour=str(row["Colour"]),
            tags=str(row["Tags"]),
            title=str(row["Title"])[:200] if pd.notna(row["Title"]) else "",
            url=str(row["URL"]) if pd.notna(row["URL"]) else "",
        )

    # Add edges
    for _, row in edges.iterrows():
        G.add_edge(str(row["Source"]), str(row["Target"]))

    # Remove isolated nodes
    isolated = list(nx.isolates(G))
    G.remove_nodes_from(isolated)
    print(f"Removed {len(isolated)} isolated nodes")
    print(f"Final graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    return G


def compute_communities(G):
    print("Computing Louvain communities (seed=42)...")
    t0 = time.time()
    communities = louvain_communities(G, seed=42)
    print(f"Found {len(communities)} communities in {time.time()-t0:.1f}s")

    community_map = {}
    for idx, cluster in enumerate(communities):
        for node in cluster:
            community_map[node] = idx

    return community_map


def compute_centrality(G):
    print("Computing degree centrality...")
    degree_cent = nx.degree_centrality(G)

    print(f"Computing approximate betweenness centrality (k=500)...")
    t0 = time.time()
    betweenness_cent = nx.betweenness_centrality(G, k=500, seed=42)
    print(f"Betweenness done in {time.time()-t0:.1f}s")

    return degree_cent, betweenness_cent


def export_gexf(G, community_map, degree_cent, betweenness_cent, path):
    print(f"Exporting GEXF to {path}...")
    for node in G.nodes():
        G.nodes[node]["community"] = community_map.get(node, -1)
        G.nodes[node]["degree_centrality"] = round(degree_cent.get(node, 0), 6)
        G.nodes[node]["betweenness_centrality"] = round(betweenness_cent.get(node, 0), 6)

    os.makedirs(os.path.dirname(path), exist_ok=True)
    nx.write_gexf(G, path)
    print(f"GEXF saved: {path}")


def export_csv(G, community_map, degree_cent, betweenness_cent, path):
    print(f"Exporting CSV to {path}...")
    rows = []
    for node in G.nodes():
        attrs = G.nodes[node]
        rows.append({
            "Id": node,
            "Label": attrs.get("label", node),
            "Colour": attrs.get("colour", ""),
            "Tags": attrs.get("tags", ""),
            "Title": attrs.get("title", ""),
            "Community_Python": community_map.get(node, -1),
            "Degree": round(degree_cent.get(node, 0), 6),
            "Betweenness": round(betweenness_cent.get(node, 0), 6),
        })

    df = pd.DataFrame(rows).sort_values("Community_Python")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"CSV saved: {path} ({len(df)} rows)")

    # Print community size summary
    sizes = df["Community_Python"].value_counts().sort_values(ascending=False)
    print("\nTop 10 communities by size:")
    for comm_id, size in sizes.head(10).items():
        print(f"  Community {comm_id}: {size} nodes")


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    elements, connections = load_data(XLSX_PATH)
    G = build_graph(elements, connections)
    community_map = compute_communities(G)
    degree_cent, betweenness_cent = compute_centrality(G)
    export_gexf(G, community_map, degree_cent, betweenness_cent, GEXF_OUT)
    export_csv(G, community_map, degree_cent, betweenness_cent, CSV_OUT)
    print("\nDone.")


if __name__ == "__main__":
    main()
