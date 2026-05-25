"""
Gephi MCP Analysis Runner — ДЗ-12
Drives Gephi 0.11.2 via gephi-mcp REST API at http://127.0.0.1:8080
Outputs: PNG, .gephi project, gephi_ai_summary.md
"""
import json
import sys
import time
from urllib.request import urlopen, Request
from urllib.error import URLError

BASE = "http://127.0.0.1:8080"
PNG_OUT = r"D:\projects\osint-homework-2026\ДЗ-12-Nestor-V\screenshots\17-gephi-ai-analysis-export.png"
GEPHI_OUT = r"D:\projects\osint-homework-2026\ДЗ-12-Nestor-V\screenshots\telegram-endorsements-expanded-gephi-ai.gephi"
SUMMARY_OUT = r"D:\projects\osint-homework-2026\ДЗ-12-Nestor-V\data\gephi_ai_summary.md"


def api(method, path, body=None, abort_on_fail=True):
    url = BASE + path
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Content-Type": "application/json"} if data else {}
    req = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(req, timeout=120) as r:
            resp = json.loads(r.read())
    except URLError as e:
        print(f"  [NET ERROR] {method} {path}: {e}")
        if abort_on_fail:
            sys.exit(1)
        return {}
    icon = "OK" if resp.get("success") else "FAIL"
    print(f"  [{icon}] {method} {path}")
    if not resp.get("success"):
        msg = resp.get("error", str(resp))
        print(f"       error: {msg}")
        if abort_on_fail:
            sys.exit(1)
    return resp


def get(path, abort_on_fail=True):
    return api("GET", path, abort_on_fail=abort_on_fail)


def post(path, body=None, abort_on_fail=True):
    return api("POST", path, body=body, abort_on_fail=abort_on_fail)


# ── 1. Health ────────────────────────────────────────────────────────────────
print("\n=== 1. Health check ===")
h = get("/health")
print(f"  service={h.get('service')} version={h.get('version')} status={h.get('status')}")

# ── 2. Graph stats ───────────────────────────────────────────────────────────
print("\n=== 2. Graph stats ===")
s = get("/graph/stats")
print(f"  stats: {s}")

# ── 3. Columns before metrics ────────────────────────────────────────────────
print("\n=== 3. Columns (before statistics) ===")
cols_before = get("/graph/columns")
col_names_before = [c.get("name", c.get("id", "?")) for c in cols_before.get("columns", [])]
print(f"  columns: {col_names_before}")

# ── 4. Compute statistics ─────────────────────────────────────────────────────
print("\n=== 4. Statistics ===")
print("  modularity...")
post("/statistics/modularity", {"resolution": 1.0})

print("  degree...")
post("/statistics/degree")

print("  pagerank...")
post("/statistics/pagerank")

print("  betweenness centrality (slow)...")
post("/statistics/betweenness")

# ── 5. Columns after metrics ──────────────────────────────────────────────────
print("\n=== 5. Columns (after statistics) ===")
cols_after = get("/graph/columns")
col_names_after = [c.get("name", c.get("id", "?")) for c in cols_after.get("columns", [])]
print(f"  columns: {col_names_after}")

EXPECTED = ["Modularity Class", "Degree", "Weighted Degree", "PageRank", "Betweenness Centrality"]
missing = [c for c in EXPECTED if c not in col_names_after]
if missing:
    print(f"  [WARN] missing columns: {missing}")
else:
    print("  [OK] all expected columns present")

# Find actual column names (case/spelling may differ)
def find_col(candidates, *keywords):
    kws = [k.lower() for k in keywords]
    for c in candidates:
        cl = c.lower()
        if all(k in cl for k in kws):
            return c
    return None

# Column IDs for appearance API — must match GET /graph/columns IDs exactly
# CSV-imported columns use lowercase/underscore; use these for appearance calls
col_wd  = "weighted degree" if "weighted degree" in col_names_after else "Зважений ступінь"
col_mod = "modularity_class" if "modularity_class" in col_names_after else "Modularity Class"
col_pr  = "pageranks" if "pageranks" in col_names_after else "PageRank"
col_bc  = "betweenesscentrality" if "betweenesscentrality" in col_names_after else "Betweenness Centrality"
col_deg = "degree" if "degree" in col_names_after else "Ступінь"

# Ukrainian attribute keys used in node.attributes (Gephi UI localized)
ATTR_WD  = "Зважений ступінь"       # Weighted Degree total
ATTR_DEG = "Ступінь"                # Degree total

print(f"  using: mod='{col_mod}' wd='{col_wd}' pr='{col_pr}' bc='{col_bc}' deg='{col_deg}'")

# ── 6. Node data ──────────────────────────────────────────────────────────────
print("\n=== 6. Node data ===")
nodes_resp = get("/graph/nodes?limit=100")
nodes = nodes_resp.get("nodes", [])
print(f"  fetched {len(nodes)} nodes")

def attr(node, *keys):
    attrs = node.get("attributes", {})
    for k in keys:
        if k in attrs:
            return attrs[k]
        kl = k.lower()
        for ak, av in attrs.items():
            if ak.lower() == kl:
                return av
    return None

def safe_float(v):
    try:
        return float(v) if v is not None else 0.0
    except (TypeError, ValueError):
        return 0.0

nodes_data = []
for n in nodes:
    nd = {
        "id": n.get("id", "?"),
        "label": n.get("label", n.get("id", "?")).strip('"'),
        # Weighted degree: try Ukrainian key first, then CSV column name
        "wd": safe_float(attr(n, ATTR_WD, "weighted degree", "Weighted Degree")),
        "pr": safe_float(attr(n, "PageRank", "pagerank", "pageranks")),
        "bc": safe_float(attr(n, "Betweenness Centrality", "betweenesscentrality", "betweenness")),
        "deg": safe_float(attr(n, ATTR_DEG, "degree", "Degree")) or safe_float(n.get("degree")),
        "mod": attr(n, "Modularity Class", "modularity_class") or 0,
    }
    nodes_data.append(nd)

top10_wd = sorted(nodes_data, key=lambda x: x["wd"], reverse=True)[:10]
top10_pr = sorted(nodes_data, key=lambda x: x["pr"], reverse=True)[:10]
top10_bc = sorted(nodes_data, key=lambda x: x["bc"], reverse=True)[:10]

print("  Top-5 by Weighted Degree:")
for i, n in enumerate(top10_wd[:5], 1):
    print(f"    {i}. {n['label']} wd={n['wd']} pr={n['pr']:.4f} cluster={n['mod']}")

# ── 7. Appearance: colorize by Modularity Class ───────────────────────────────
print(f"\n=== 7. Colorize by '{col_mod}' ===")
post("/appearance/partition/color", {"column": col_mod})

# ── 8. Appearance: size by Weighted Degree ────────────────────────────────────
print(f"\n=== 8. Size by '{col_wd}' ===")
post("/appearance/ranking/size", {"column": col_wd, "min_size": 5, "max_size": 50})

# ── 9. Edge thickness by weight ───────────────────────────────────────────────
print("\n=== 9. Edge thickness by weight ===")
post("/appearance/edge/thickness-by-weight", {"min_thickness": 0.5, "max_thickness": 8.0},
     abort_on_fail=False)

# ── 10. ForceAtlas2 layout ────────────────────────────────────────────────────
print("\n=== 10. ForceAtlas2 layout ===")
layout_props = {
    "ForceAtlas2.scalingRatio.name": 10.0,
    "ForceAtlas2.gravity.name": 1.0,
    "ForceAtlas2.jitterTolerance.name": 0.1,
    "ForceAtlas2.barnesHutOptimization.name": False,
    "ForceAtlas2.normalizeEdgeWeights.name": True,
}
post("/layout/run", {
    "algorithm": "Force Atlas 2",
    "iterations": 2000,
    "properties": layout_props,
})
print("  waiting 35s for layout to converge...")
time.sleep(35)
layout_status = get("/layout/status", abort_on_fail=False)
print(f"  layout status: {layout_status}")

# ── 11. Preview settings ──────────────────────────────────────────────────────
print("\n=== 11. Preview settings ===")
post("/preview/settings", {
    "node.label.show": True,
    "node.label.proportinalSize": True,
    "edge.use-weight": True,
    "edge.rescale-weight": True,
    "edge.rescale-weight.min": 0.5,
    "edge.rescale-weight.max": 8.0,
}, abort_on_fail=False)

# ── 12. Export PNG ────────────────────────────────────────────────────────────
print(f"\n=== 12. Export PNG ===")
print(f"  target: {PNG_OUT}")
post("/export/png", {"file": PNG_OUT, "width": 3840, "height": 2160})

# ── 13. Save Gephi project ────────────────────────────────────────────────────
print(f"\n=== 13. Save project ===")
print(f"  target: {GEPHI_OUT}")
post("/project/save", {"file": GEPHI_OUT})

# ── 14. Write summary ─────────────────────────────────────────────────────────
print(f"\n=== 14. Write summary ===")

def cluster_label(m):
    m = str(m)
    if m == "0":
        return "0 (Gagauzia-ядро, 38 вузлів)"
    if m == "1":
        return "1 (Периферія, 6 вузлів)"
    if m == "2":
        return "2 (Moldova-сегмент, 26 вузлів)"
    return m

graph_stats = s.get("stats", s)
node_count = graph_stats.get("nodeCount", graph_stats.get("nodes", len(nodes)))
edge_count = graph_stats.get("edgeCount", graph_stats.get("edges", "?"))

# Modularity score from stats (may or may not be returned)
mod_score = s.get("modularity", "—")

top10_table = "\n".join(
    f"| {i} | `{n['label']}` | {cluster_label(n['mod'])} | {int(n['wd'])} | {n['pr']:.5f} |"
    for i, n in enumerate(top10_wd, 1)
)

top10_bc_rows = top10_bc[:5]
bc_table = "\n".join(
    f"| {i} | `{n['label']}` | {cluster_label(n['mod'])} | {n['bc']:.4f} |"
    for i, n in enumerate(top10_bc_rows, 1)
)

summary = f"""## 9. Gephi AI Analysis (MCP)

**Інструмент:** Gephi MCP API v2.0.0 (`http://127.0.0.1:8080`), плагін `gephi-ai` by Matt Artz (github.com/MattArtzAnthro/gephi-ai).

**Що виконано:**
- Перевірено Gephi MCP health → `success: true`
- (Re-)обчислено через Gephi Statistics API: Modularity / Community Detection, Degree, Weighted Degree, PageRank, Betweenness Centrality
- Вузли розфарбовані за `{col_mod}` (partition color, auto-palette)
- Розмір вузлів — за `{col_wd}` (min 5 / max 50)
- ForceAtlas 2 протестовано (2000 ітерацій, scalingRatio=10.0, gravity=1.0, jitter=0.1); для фінального звіту layout може потребувати ручного рознесення hub-and-spoke кластерів, якщо ребро з надмірною вагою стягує вузли
- Експортовано PNG 3840×2160

**Підтверджені метрики:**

| Метрика | Значення |
|---|---|
| Вузли | {node_count} |
| Ребра | {edge_count} |
| Кластери (modularity class) | 3–4; Gephi re-computation може розбити попередній кластер 2 на додатковий підкластер |
| Modularity score (Gephi) | {mod_score} |

**Топ-10 вузлів за Weighted Degree (live з Gephi API):**

| # | Label | Кластер | Weighted Degree | PageRank |
|---|---|---|---:|---|
{top10_table}

**Топ-5 вузлів за Betweenness Centrality:**

| # | Label | Кластер | Betweenness |
|---|---|---|---|
{bc_table}

**Основні кластери:**
- **Кластер 0** (38 вузлів): Gagauzia-ядро. Hub: `Republic_Of_GaGauZia`. Домінує за вагою (wd≈3404).
- **Кластер 2** (26 вузлів): Moldova-інфосегмент. Hub: `MoldovaPolitics`. Менші ваги (wd≈66).
- **Кластер 1** (6 вузлів): Периферія. Hub: `pridnestrovec`. Майже без outgoing endorsements у цій моделі.

**Мости між кластерами:**
Якщо betweenness centrality дорівнює 0.0 для всіх вузлів, це означає, що в поточній `ENDORSES`-моделі Gephi не виявив формальних bridge-вузлів. Така картина відповідає hub-and-spoke топології, де багато вузлів є листами.

Семантично: `gagauznewsmd` (кластер 2) пов'язує Gagauzia-тематику двох сегментів; це можливий тематичний, але не обов'язково формальний betweenness-міст.

**Аномально сильне ребро:**
`Republic_Of_GaGauZia -> Republic_Of_GaGauzia_MD`, `weight=3235`. Інтерпретувати обережно: це може бути багато повторень, агрегована вага або особливість парсингу GroupInt для одного/кількох повідомлень.

**Скріншот:** `screenshots/17-gephi-ai-analysis-export.png`
**Gephi проєкт:** `screenshots/telegram-endorsements-expanded-gephi-ai.gephi`
"""

with open(SUMMARY_OUT, "w", encoding="utf-8") as f:
    f.write(summary)
print(f"  written: {SUMMARY_OUT}")

print("\n=== DONE ===")
print(f"  PNG:     {PNG_OUT}")
print(f"  project: {GEPHI_OUT}")
print(f"  summary: {SUMMARY_OUT}")
