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
