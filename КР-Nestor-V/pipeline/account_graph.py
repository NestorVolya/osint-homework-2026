"""
Account Graph: accounts → networkx DiGraph → pyvis HTML.

Nodes  = account_id (one per platform account)
Edges  = shared handle substring / same platform group
"""

import json
from pathlib import Path

import networkx as nx
from loguru import logger

try:
    from pyvis.network import Network
    _PYVIS = True
except ImportError:
    _PYVIS = False

from pipeline.storage.db import Database

PLATFORM_COLORS = {
    "facebook":      "#1877f2",
    "instagram":     "#e1306c",
    "twitter":       "#1da1f2",
    "telegram":      "#0088cc",
    "youtube":       "#ff0000",
    "linkedin":      "#0077b5",
    "behance":       "#053eff",
    "academia":      "#41454a",
    "researchgate":  "#00d0af",
    "tiktok":        "#010101",
    "vkontakte":     "#4a76a8",
    "odnoklassniki": "#f7931e",
}


def _build_graph(accounts: list[dict]) -> nx.DiGraph:
    G = nx.DiGraph()

    for acc in accounts:
        G.add_node(
            acc["account_id"],
            label=f"{acc['platform']}\n@{acc['handle'] or '?'}",
            platform=acc["platform"],
            url=acc["url"] or "",
            handle=acc["handle"] or "",
            title=acc["url"] or acc["account_id"],
        )

    # edges: accounts sharing handle prefix (same person across platforms)
    accs = accounts
    for i, a in enumerate(accs):
        for b in accs[i + 1:]:
            if not a["handle"] or not b["handle"]:
                continue
            ha, hb = a["handle"].lower(), b["handle"].lower()
            # same handle or one contains the other (min 4 chars)
            if len(ha) >= 4 and (ha == hb or ha in hb or hb in ha):
                G.add_edge(
                    a["account_id"], b["account_id"],
                    label="same handle",
                    color="#aaaaaa",
                )

    return G


def run_account_graph(db: Database, report_dir: Path) -> Path | None:
    accounts = db.get_accounts()
    if not accounts:
        logger.info("[account_graph] no accounts in db, skipping")
        return None

    G = _build_graph(accounts)
    logger.info(
        f"[account_graph] nodes={G.number_of_nodes()} edges={G.number_of_edges()}"
    )

    out_path = report_dir / "accounts_graph.html"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if not _PYVIS:
        logger.warning("[account_graph] pyvis not installed — writing plain HTML table")
        _write_fallback(accounts, out_path)
        return out_path

    net = Network(height="500px", width="100%", directed=False,
                  bgcolor="#1a1a2e", font_color="white")
    net.from_nx(G)

    for node in net.nodes:
        platform = node.get("platform", "").lower()
        node["color"] = PLATFORM_COLORS.get(platform, "#6c757d")
        node["size"] = 25
        node["title"] = node.get("url", node.get("id", ""))

    net.set_options("""
    {
      "physics": {
        "barnesHut": {"gravitationalConstant": -6000, "springLength": 180},
        "stabilization": {"iterations": 150}
      },
      "edges": {"smooth": {"type": "dynamic"}}
    }
    """)

    net.save_graph(str(out_path))
    logger.info(f"[account_graph] written → {out_path}")
    return out_path


def _write_fallback(accounts: list[dict], path: Path):
    rows = "".join(
        f"<tr><td>{a['platform']}</td><td>{a['handle'] or '—'}</td>"
        f"<td><a href='{a['url']}'>{a['url']}</a></td></tr>"
        for a in accounts
    )
    path.write_text(
        f"<!DOCTYPE html><html><body>"
        f"<table border='1'><tr><th>Platform</th><th>Handle</th><th>URL</th></tr>"
        f"{rows}</table></body></html>",
        encoding="utf-8",
    )
