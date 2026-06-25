# ДЗ-06: Теорія графів та графи знань

**Курс:** OSINT · Robot Dreams · 2026  
**Студент:** Nestor-V  
**Дата:** 2026-05-13  
**Рівень:** Базовий 🔵 + Просунутий 🔴

---

## Датасет

**`patents_full_enrichment_0304.xlsx`** — граф семантичної схожості російських та радянських патентів у сфері морської техніки. Контекст: патентний ландшафт технологій типу **БЕК** (безпілотний надводний катер).

| Параметр | Значення |
|----------|---------|
| Вузли після фільтрації | 7 869 патентів |
| Ребра | 8 819 зв'язків (тип: `similar`) |
| Видалено (`irrelevant`) | 191 вузол |
| Modularity Q (Gephi) | **0.956** — відмінна кластерна структура |
| Кластерів (Louvain) | 702 |

> **Чому не filtered (parsed-only):** граф лише з `parsed`-вузлів дає 72 ребра на 1 188 вузлів — розпадається. Потрібен повний граф.

---

## Структура здачі

### 🔵 Базовий рівень

| Файл | Зміст |
|---|---|
| [homework_cluster_summaries/nodes_with_communities.csv](homework_cluster_summaries/nodes_with_communities.csv) | Таблиця вузлів: ID, Colour, Tags, Title, Community_Python, Modularity_Class_Gephi, Degree, Betweenness |
| [homework_cluster_summaries/cluster_summaries.md](homework_cluster_summaries/cluster_summaries.md) | Описи 5 найбільших кластерів + науковий персонал + LLM hallucination risks |
| [homework_cluster_summaries/prompt.md](homework_cluster_summaries/prompt.md) | Промпт для LLM (Claude Sonnet 4.6) |
| [homework_cluster_summaries/reviewer_notes.md](homework_cluster_summaries/reviewer_notes.md) | Ручна перевірка AI-описів |
| [data/screenshots/gephi-modularity-report.png](data/screenshots/gephi-modularity-report.png) | Gephi Modularity Report (Q=0.956, 702 communities) |
| [data/screenshots/gephi-colored-clusters.png](data/screenshots/gephi-colored-clusters.png) | Граф після фарбування по Modularity Class |
| [data/screenshots/gephi-force-atlas2.png](data/screenshots/gephi-force-atlas2.png) | Force Atlas 2 layout |
| [data/screenshots/gephi-data-laboratory.png](data/screenshots/gephi-data-laboratory.png) | Data Laboratory — таблиця вузлів |
| [data/screenshots/communities-size-distribution.png](data/screenshots/communities-size-distribution.png) | Розподіл розмірів 702 кластерів |

### 🔴 Просунутий рівень

| Файл | Зміст |
|---|---|
| [build_graph.py](build_graph.py) | Python-пайплайн: xlsx → NetworkX → GEXF + CSV + Louvain |
| [theory_appendix.md](theory_appendix.md) | Теорія: Louvain, Modularity Q, метрики графа |
| [data/patents_graph.gexf](data/patents_graph.gexf) | GEXF для Gephi (7 869 вузлів з атрибутами) |
| [data/modularity-report.html](data/modularity-report.html) | HTML-звіт Gephi Modularity |

---

## Ключові знахідки

### Топ-5 кластерів

| Кластер | Розмір | Тема |
|---------|--------|------|
| C496 | 331 | Глісери та пропульсивні системи |
| C359 | 213 | Бойові та спеціалізовані кораблі |
| C234 | 196 | Рятувальні системи + імпеллерні судна |
| C285 | 153 | Навігація та автоматичне управління |
| C163 | 150 | Маломірні судна та легкі конструкції |

### Науковий персонал (витягнуто з Google Patents)

| Особа / Установа | Кластери | Примітка |
|------------------|----------|----------|
| **Чернявец Владимир Васильевич** | C234, C285 | Єдина bridge-особа між двома кластерами; 5 патентів |
| **ВМА ім. Кузнецова** (ВМФ РФ, С.-Петербург) | C285 | Встановлена держустанова; assignee в RU2798921C1 |
| Юхнін В.Є. + Спіридопуло В.І. + Селіванов М.П. | C359 | Команда з 3 спільних патентів; НДІ не ідентифіковано |
| Голубенко Михаил Іванович | C234 | 2 імпеллерних патенти (2020, 2024) |
| Карпенко Анатолій Григорович | C163 | Серія "лодка Поля" — приватний винахідник |

> ⚠️ **Обмеження:** patenton.ru блокує автоматичний скрапінг; дані зібрані через Google Patents для топ-5 патентів кожного кластера за betweenness centrality.

---

## Gephi Workflow

```
1. File → Open → data/patents_graph.gexf
2. Statistics → Modularity → Run (resolution=1.0)
3. Appearance → Nodes → Color → Partition → Modularity Class → Apply
4. Layout → Force Atlas 2 (LinLog ON, ~3-5 хв) → Stop
5. Data Laboratory → Export Spreadsheet → nodes_with_communities.csv
```

---

## Запуск Python-пайплайну

```bash
pip install -r requirements.txt
python build_graph.py
# Вихід: data/patents_graph.gexf + homework_cluster_summaries/nodes_with_communities.csv
```

**Залежності:** Python 3.14, networkx 3.6.1 (louvain built-in), openpyxl, pandas

---

## Acceptance Criteria — самоперевірка

### 🔵 Базовий

- [x] Граф побудований на основі `patents_full_enrichment_0304.xlsx`
- [x] Встановлено зв'язки між групами патентів, виробом типу БЕК та науковим персоналом
- [x] Граф очищений від `irrelevant`-вузлів (191 видалено)
- [x] У Gephi запущено modularity (Q=0.956, 702 communities)
- [x] Експортовано `nodes_with_communities.csv` з Modularity_Class_Gephi + Community_Python
- [x] Описано 5 найбільших кластерів
- [x] Кожен кластер: список вузлів, топ за centrality, можливе пояснення
- [x] Кожен кластер: питання для перевірки **з явними відповідями**
- [x] Секція `LLM hallucination risks` у `cluster_summaries.md`
- [x] `prompt.md` збережено
- [x] `reviewer_notes.md` з ручними правками

### 🔴 Просунутий

- [x] Python-пайплайн `build_graph.py` з повним алгоритмом Louvain
- [x] GEXF-файл з атрибутами для Gephi
- [x] Збагачення Google Patents API (inventors/assignees для топ-патентів)
- [x] Виявлено bridge-особу між кластерами (Чернявец В.В.)
- [x] Встановлено держустанову ВМФ РФ як assignee (ВМА Кузнецова)
- [x] Теоретичний додаток `theory_appendix.md`
