from pyvis.network import Network

net = Network(height="700px", width="100%", directed=True, bgcolor="#ffffff", font_color="#333333")
net.set_options("""
{
  "physics": {
    "forceAtlas2Based": {
      "gravitationalConstant": -80,
      "springLength": 200
    },
    "solver": "forceAtlas2Based",
    "stabilization": { "iterations": 150 }
  },
  "edges": {
    "font": { "size": 10, "align": "middle" },
    "smooth": { "type": "continuous" },
    "arrows": { "to": { "enabled": true, "scaleFactor": 0.7 } }
  },
  "nodes": {
    "font": { "size": 13 }
  }
}
""")

# Nodes: (id, label, color, shape)
nodes = [
    ("N1",  "Чекаль Олексій\nГеоргійович",       "#dae8fc", "ellipse"),
    ("N2",  "PanicDesign",                         "#fff2cc", "ellipse"),
    ("N3",  "Артос",                               "#fff2cc", "ellipse"),
    ("N4",  "ПСТГУ",                               "#fff2cc", "ellipse"),
    ("N5",  "Fondazione\nRussia Cristiana",         "#fff2cc", "ellipse"),
    ("N6",  "Rimini Meeting 2013",                  "#d6b656", "ellipse"),
    ("N7",  "Харків",                              "#d5e8d4", "ellipse"),
    ("N8",  "Москва",                              "#d5e8d4", "ellipse"),
    ("N9",  "pravmir.ru",                           "#f8cecc", "ellipse"),
    ("N10", "hramozdatel.ru",                       "#f8cecc", "ellipse"),
]

for nid, label, color, shape in nodes:
    border = "#6c8ebf" if color == "#dae8fc" else \
             "#d6b656" if color == "#fff2cc" else \
             "#82b366" if color == "#d5e8d4" else \
             "#b85450"
    net.add_node(nid, label=label, color={"background": color, "border": border},
                 shape=shape, size=30)

# Edges: (from, to, label)
edges = [
    ("N1",  "N2",  "WORKS_FOR · 8/10"),
    ("N1",  "N3",  "PARTNERED_WITH · 9/10"),
    ("N1",  "N4",  "COLLABORATED_WITH · 8/10"),
    ("N1",  "N5",  "DESIGNED_FOR · 8/10"),
    ("N1",  "N6",  "PARTICIPATED_IN · 9/10"),
    ("N1",  "N7",  "ORIGIN_FROM · 8/10"),
    ("N1",  "N8",  "BASED_IN · 8/10"),
    ("N5",  "N6",  "ORGANIZED · 8/10"),
    ("N3",  "N6",  "EXHIBITED_AT · 8/10"),
    ("N9",  "N1",  "PUBLISHED_ABOUT · 9/10"),
    ("N10", "N1",  "PUBLISHED_ABOUT · 9/10"),
]

for src, dst, label in edges:
    net.add_edge(src, dst, label=label)

output = "graph-chekal.html"
net.write_html(output)
print(f"Збережено: {output}")
