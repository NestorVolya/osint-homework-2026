# Коментар для здачі ДЗ-06

**ДЗ-06 — Теорія графів та графи знань · Basic 🔵 + Advanced 🔴**
Хто / чим: студент Nestor-V + Claude Code (агент); Python/networkx/pandas, Gephi 0.11.2

**Зроблено:**
- Датасет `patents_full_enrichment_0304.xlsx` → граф 7 869 вузлів / 8 819 ребер (видалено 191 `irrelevant`)
- Python-пайплайн `build_graph.py`: xlsx → NetworkX → GEXF + CSV; Louvain (built-in nx 3.6.1), betweenness centrality k=500
- Gephi: Modularity Run → Q=0.956, 702 кластери; Force Atlas 2; Data Laboratory export
- Описано 5 найбільших кластерів (C496, C359, C234, C285, C163) з таблицями centrality, питаннями та явними відповідями
- Google Patents збагачення: inventors/assignees для топ-5 патентів кожного кластера за betweenness
- Виявлено bridge-особу між кластерами: Чернявец В.В. (C234 + C285, 5 патентів)
- Встановлено держустанову ВМФ РФ: ВМА ім. Кузнецова (assignee в C285)
- `reviewer_notes.md`: ручна перевірка AI-чернетки, вилучено overconfidence, ~40% тексту переписано
- `theory_appendix.md`: Louvain, Modularity Q, метрики графа для OSINT-аудиторії

**Де:** Local (Windows 10) — Python + Gephi + git

**Проблеми:**
- `patenton.ru` блокує боти (Cloudflare) → переключено на Google Patents meta itemprop
- `python-louvain` несумісний з Python 3.14 → використано `nx.community.louvain_communities()` (built-in)
- Gephi CSV export не зберіг назви колонок → відновлено вручну за даними

**Acceptance criteria:**
- [x] Граф побудований з `patents_full_enrichment_0304.xlsx` (7 869 вузлів, 8 819 ребер)
- [x] Встановлено зв'язки: патенти → виріб типу БЕК → науковий персонал
- [x] Граф очищений від `irrelevant` вузлів (191 видалено)
- [x] Gephi modularity запущено (Q=0.956, 702 кластери)
- [x] Експортовано `nodes_with_communities.csv` (community + modularity class, 7 869 рядків)
- [x] Описано 5 кластерів: список вузлів, топ centrality, пояснення, питання з відповідями
- [x] Секція `LLM hallucination risks` у `cluster_summaries.md`
- [x] `prompt.md` збережено
- [x] `reviewer_notes.md` з ручними правками
