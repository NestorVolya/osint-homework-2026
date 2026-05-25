# Структура репозиторію

```
osint-homework-2026/
├── README.md
├── STRUCTURE.md               ← цей файл
├── .gitignore
│
├── ДЗ-02-Nestor-V/            ← Промптинг, RAG, захист від ін'єкцій
│   ├── README.md
│   ├── Б1-промпти.md          ← A/B тест: поганий vs структурований промпт
│   ├── Б2-галюцинації.md      ← верифікація 10 фактів, таблиця, відсоток
│   ├── П1-RAG-порівняння.md   ← 4 варіанти RAG + порівняльна таблиця
│   ├── П2-pipeline.md         ← Jina → NotebookLM → H-аналіз → MNT
│   ├── П3-injection.md        ← до/після захисту (промпт-рівень)
│   ├── П4-llm-guard.md        ← FastAPI + LLM Guard: захист RAG на рівні retrieval
│   ├── notes-n8n-prompts.md   ← еволюція промптів, архітектура n8n
│   ├── promt 1.png            ← ChatGPT без контексту (Prompt A)
│   ├── promt 2.png            ← ChatGPT зі структурованим промптом (Prompt Б)
│   ├── screenshot-p3-before.png  ← П3: без захисту — injection прийнятий
│   ├── screenshot-p3-after.png   ← П3: з захистом — injection відхилений
│   ├── Guarded LLM Retrieval-2026-04-23-000546.png  ← П4: LLM Guard flowchart
│   ├── Guarded LLM Retrieval-2026-04-23-000721.png  ← П4: LLM Guard flowchart v2
│   ├── pipline Shoykhet.png   ← П2: OSINT pipeline схема
│   └── ...
│
├── ДЗ-06-Nestor-V/            ← Теорія графів: патентний граф БЕК
│   ├── README.md              ← опис, ключові знахідки, acceptance criteria
│   ├── build_graph.py         ← xlsx → NetworkX → GEXF + CSV (Louvain, centrality)
│   ├── requirements.txt       ← openpyxl, pandas (networkx вже встановлено)
│   ├── theory_appendix.md     ← теорія: Louvain, Modularity Q, метрики графа
│   ├── data/
│   │   ├── patents_graph.gexf                    ← 7 869 вузлів, для Gephi
│   │   ├── modularity-report.html                ← Gephi modularity HTML-звіт
│   │   └── screenshots/
│   │       ├── gephi-graph-overview.png           ← загальний вигляд графа
│   │       ├── gephi-modularity-report.png        ← Q=0.956, 702 communities
│   │       ├── gephi-colored-clusters.png         ← кластери за кольором
│   │       ├── gephi-force-atlas2.png             ← Force Atlas 2 layout
│   │       ├── gephi-data-laboratory.png          ← таблиця вузлів з Modularity Class
│   │       └── communities-size-distribution.png  ← розподіл розмірів кластерів
│   └── homework_cluster_summaries/
│       ├── nodes_with_communities.csv ← 7 869 вузлів + Community_Python + Modularity_Class_Gephi
│       ├── cluster_summaries.md       ← 5 кластерів + науковий персонал + LLM hallucination risks
│       ├── prompt.md                  ← системний промпт для Claude Sonnet 4.6
│       └── reviewer_notes.md          ← ручна перевірка AI-описів + збагачення Google Patents
│
├── ДЗ-11-Nestor-V/            ← OSINT: Doppelganger (Italian campaign 2022–2024)
│   ├── README.md
│   ├── mini_osint_report_doppelganger_italy.md  ← основний звіт: опис, 5 кейсів, методи, наративи
│   ├── mini_osint_report_doppelganger_italy.html ← HTML з нумерованими виносками-посиланнями
│   ├── sources.md                                ← таблиця 16 джерел зі статусом перевірки
│   ├── sources.html                              ← HTML-версія (клікабельні лінки)
│   └── screenshots/                              ← 16 скріншотів першоджерел
│
├── ДЗ-12-Nestor-V/            ← Кластеризація Telegram-каналів: GroupInt + Neo4j + Gephi
│   ├── README.md
│   ├── AI_OSINT_HW_Clustering_PatternMatching_Nestor-V.md  ← основний OSINT-звіт
│   ├── PLAN.md                                            ← план виконання
│   ├── SCREENSHOTS.md                                     ← перелік скріншотів
│   ├── VPS_RUNTIME_STATUS.md                              ← VPS/Traefik/GroupInt runtime notes
│   ├── data/
│   │   ├── nodes_with_communities.csv                     ← вузли, clusters, centrality metrics
│   │   ├── edges_endorsements.csv                         ← ребра ENDORSES з weight/raw links/message ids
│   │   └── gephi_ai_summary.md                            ← підсумок Gephi MCP аналізу
│   ├── scripts/
│   │   └── gephi_mcp_run.py                               ← відтворення Gephi AI/MCP аналізу
│   └── screenshots/
│       ├── 01-hostinger-docker-manager-projects.png
│       ├── 03-hostinger-docker-manager-groupint-compose-setup.png
│       ├── 04-groupint-telegram-session-saved-sensitive.png
│       ├── 05-groupint-target-republic-of-gagauzia-selected.png
│       ├── 08-groupint-republic-endorsements-663-dark.png
│       ├── 10-gephi-neo4j-import-group-endorsements.png
│       ├── 13-gephi-expanded-modularity-70nodes.png
│       ├── 15-gephi-data-lab-top-weighted-degree.png
│       ├── 16-gephi-data-lab-top-endorsement-edges.png
│       ├── 17-gephi-ai-analysis-export.png
│       └── telegram-endorsements-expanded-gephi-ai.gephi
│
└── ДЗ-03/                     ← MindsDB + ArkhamMirror SHATTERED
    ├── README.md              ← спільний огляд обох рівнів
    │
    ├── ДЗ-03-Nestor-V/        ← Базовий рівень: MindsDB
    │   ├── README.md
    │   ├── report.md          ← SQL-запити + діалог AI агента (Gemini 2.5 Flash)
    │   └── screenshots/
    │       ├── screenshot-01-docker.png       ← docker ps, контейнери Running
    │       ├── screenshot-02-studio.png       ← MindsDB Studio UI
    │       ├── screenshot-03-show-tables.png  ← SHOW TABLES / SELECT перших рядків
    │       ├── screenshot-04-query1.png       ← SQL Query 1: агрегація по країні
    │       ├── screenshot-05-query2.png       ← SQL Query 2: RU-джерела з вагою
    │       ├── screenshot-06-query3.png       ← SQL Query 3: фільтр
    │       └── screenshot-07-agent.png        ← AI агент chekal_analyst відповідає
    │
    └── dz-mindsdb-arkham-Nestor-V/   ← Просунутий рівень: ArkhamMirror
        ├── README.md                 ← результати, скріншоти, обмеження
        ├── arkham-overview.md        ← що таке ArkhamMirror (архітектура платформи)
        ├── report.md
        ├── docker-compose.osint.yml
        ├── arkham/
        │   ├── docker-compose.yml   ← запуск: shattered-app + shattered-postgres
        │   └── .env.example         ← шаблон змінних (без паролів)
        ├── screenshot-arkham_health.png      ← health check: 25 shards, status healthy
        ├── screenshot-arkham_dashboard.png   ← реальний UI Dashboard (всі сервіси Online)
        ├── screenshot-arkham_documents.png   ← реальний UI Documents: 5 файлів processed
        ├── screenshot-arkham_documents_real.png
        ├── screenshot-arkham_mindsdb.png     ← MindsDB SELECT з arkham_db (5 рядків)
        └── screenshots/
            ├── 01-docker-containers-running.png
            ├── 02-mindsdb-studio-editor.png
            ├── 03-docker-desktop-stats.png
            └── 04-gordon-setup-complete.png
```

---

## Шаблон оформлення ДЗ

### README.md (інтро-блок)

```
**ДЗ-XX — [Назва теми] · Basic 🔵 [+ Advanced 🔴]**

Хто / чим: студент Nestor-V + Claude Code (агент); [інструменти]

ТУТ: https://github.com/NestorVolya/osint-homework-2026/tree/main/ДЗ-XX-Nestor-V

**Зроблено:**

- [bullet 1]
- [bullet 2]
- ...

**Де:** Local (Windows 10) [/ VPS] — [інструменти]

---

## Структура здачі

| Файл | Зміст |
|---|---|
| [файл.md](файл.md) | Опис |

## Acceptance Criteria — самоперевірка

### 🔵 Базовий

- [x] Критерій 1
- [x] Критерій 2
```

### Каталог ДЗ (рядок у головному README.md)

```
| ДЗ-XX | [Назва](ДЗ-XX-Nestor-V/) | Короткий опис | 🔵 Basic |
```
