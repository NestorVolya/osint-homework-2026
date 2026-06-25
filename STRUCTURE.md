# Структура репозиторію

```
osint-homework-2026/
├── README.md
├── STRUCTURE.md               ← цей файл
├── SECURITY.md
├── .gitignore
│
├── КР-Nestor-V/               ← Курсова робота: автоматизований OSINT pipeline
│   ├── README.md              ← showcase-navigator: 8 обов'язкових секцій + навігація
│   ├── KR_PRODUCT_AUDIT.md   ← критика з 4 позицій + roadmap H0→H3
│   ├── VALIDATION_REPORT_KR.md ← 4-actor validation: Чекаль + Braschi + Коваленко + Філоненко
│   ├── DECISIONS.md           ← ADR-001 … ADR-007
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── pipeline/              ← 15 модулів: collect → report
│   │   ├── run.py             ← entry point
│   │   ├── collect.py         ← Exa + Tavily + Google CSE
│   │   ├── account_discovery.py
│   │   ├── account_graph.py   ← pyvis
│   │   ├── enrich_timeline.py ← WAR_CONTEXT mapping
│   │   ├── enrich_statements.py ← Gemini NER + steelman prompt
│   │   ├── enrich_network.py  ← NER + risk flags
│   │   ├── geoclusters.py
│   │   ├── detect_contradictions.py
│   │   ├── quality_check.py   ← 5-gate Corpus Health Score
│   │   ├── report.py          ← HTML (Jinja2)
│   │   ├── report_md.py       ← Markdown 7 секцій
│   │   ├── dstu.py            ← ДСТУ 8302:2015 бібліографія
│   │   ├── storage/           ← SQLite (7 таблиць) + ZIP archive
│   │   └── gates/             ← input / budget / safety gates
│   ├── benchmark_profiles/    ← YAML: ua_cultural_ru_sphere + braschi_catholic + default
│   ├── config/
│   │   └── settings.yaml
│   ├── templates/
│   │   └── report.html.j2
│   ├── tests/                 ← pytest 15/15
│   ├── scripts/
│   │   └── export_to_osint_base.py ← ADR-007: bridge export
│   ├── docs/
│   │   ├── adr/               ← ADR-001 … ADR-007
│   │   ├── COMPARATIVE_ANALYSIS.md ← аудит 5 реалізацій (Claude Code vs OpenAI Codex)
│   │   ├── pipeline_diagram.png
│   │   └── demoCHEKAL.gif     ← demo: скрол звіту gold actor
│   └── examples/
│       └── sample_run/        ← реальний прогін Чекаля: HTML + SQLite + граф
│
├── ДЗ-02-Nestor-V/            ← Промптинг, RAG, захист від ін'єкцій
│   ├── README.md
│   ├── Б1-промпти.md          ← A/B тест: поганий vs структурований промпт
│   ├── Б2-галюцинації.md      ← верифікація 10 фактів, таблиця, відсоток
│   ├── П1-RAG-порівняння.md   ← 4 варіанти RAG + порівняльна таблиця
│   ├── П2-pipeline.md         ← Jina → NotebookLM → H-аналіз → MNT
│   ├── П3-injection.md        ← до/після захисту (промпт-рівень)
│   └── П4-llm-guard.md        ← FastAPI + LLM Guard: захист RAG на рівні retrieval
│
├── ДЗ-03/                     ← MindsDB + ArkhamMirror SHATTERED
│   ├── README.md
│   ├── ДЗ-03-Nestor-V/        ← Базовий: MindsDB SQL + AI агент
│   │   ├── README.md
│   │   ├── report.md
│   │   └── screenshots/
│   └── dz-mindsdb-arkham-Nestor-V/ ← Просунутий: ArkhamMirror (28 shards)
│       ├── README.md
│       ├── arkham/
│       │   ├── docker-compose.yml
│       │   └── .env.example
│       └── screenshots/
│
├── ДЗ-04-Nestor-V/            ← Mini-pipeline: risu.ua (Crawl4AI + Docker + Prometheus)
│   ├── README.md
│   ├── compose.yaml           ← 5 сервісів: scraper + scheduler + Prometheus + Grafana
│   ├── Dockerfile             ← Python 3.11 + Playwright/Chromium
│   ├── src/                   ← scraper, normalizer, scheduler
│   ├── config/
│   │   └── prometheus.yml
│   ├── data/                  ← raw + normalized JSON
│   ├── docs/
│   └── screenshots/
│
├── ДЗ-05-Nestor-V/            ← Entity Resolution та граф зв'язків (Чекаль)
│   ├── README.md
│   ├── Б1-ідентифікатори.md   ← ідентифікатори актора
│   ├── Б2-граф-spec.md        ← специфікація графа зв'язків
│   ├── Б3-collision.md        ← collision detection: однофамільці
│   ├── П4-flowsint.md         ← Flowsint entity resolution
│   ├── П5-порівняння.md       ← порівняння методів
│   └── graphs/                ← pyvis HTML-графи
│
├── ДЗ-06-Nestor-V/            ← Теорія графів: патентний граф БЕК (Gephi + Louvain)
│   ├── README.md
│   ├── build_graph.py         ← xlsx → NetworkX → GEXF + CSV
│   ├── theory_appendix.md     ← Louvain, Modularity Q, метрики
│   ├── data/
│   │   ├── patents_graph.gexf ← 7 869 вузлів
│   │   └── modularity-report.html
│   └── homework_cluster_summaries/
│       ├── nodes_with_communities.csv
│       ├── cluster_summaries.md
│       └── prompt.md
│
├── ДЗ-11-Nestor-V/            ← OSINT: Doppelganger Italy (2022–2024)
│   ├── README.md
│   ├── mini_osint_report_doppelganger_italy.md
│   ├── mini_osint_report_doppelganger_italy.html ← HTML з ДСТУ виносками
│   ├── sources.md
│   ├── sources.html
│   └── screenshots/           ← 16 скріншотів першоджерел
│
├── ДЗ-12-Nestor-V/            ← Telegram-кластеризація: GroupInt + Neo4j + Gephi
│   ├── README.md
│   ├── AI_OSINT_HW_Clustering_PatternMatching_Nestor-V.md
│   ├── data/
│   │   ├── nodes_with_communities.csv
│   │   └── edges_endorsements.csv
│   ├── scripts/
│   │   └── gephi_mcp_run.py
│   └── screenshots/
│
├── ДЗ-17-Nestor-V/            ← Статистика: виявлення ботів (LogReg + KMeans)
│   ├── README.md
│   ├── DZ17_Bot_Detection_Nestor-V.ipynb
│   ├── AI_OSINT_HW_Statistics_Nestor-V.md
│   ├── data/
│   │   └── accounts.csv       ← 500 акаунтів: 350 людей / 150 ботів
│   └── screenshots/
│
└── ДЗ-20-Nestor-V/            ← Верифікація за Берклійським протоколом (Буча, Maxar)
    ├── README.md
    ├── narrative-report.md
    ├── verification-report.md
    ├── verification-report.html
    ├── sources.md
    ├── submission_comment.md
    ├── geolocation/
    ├── chronolocation/
    └── source-material/
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
