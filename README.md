# OSINT Homework 2026 — Nestor V

Монорепозиторій курсу «AI для OSINT і розвідки» · Robot Dreams · 2026  
**Студент:** Олександр Корнієнко · псевдо Nestor-V  
**Інструменти:** Claude Code · OpenAI Codex · Gemini · Python · Docker · Gephi

---

## Курсова робота

### [КР-Nestor-V/](КР-Nestor-V/) — actor-osint-front-СС

Автоматизований OSINT pipeline: **seed (ПІБ / нікнейм / email) → SQLite + HTML-досьє + JSON + ZIP**

**Напрям 1** — «Персони та соціальні мережі/геолокація»  
**Gold actor:** health = 1.00 · 5/5 gates PASS · 44 джерела · pytest 15/15 → [деталі](#gold-actor)

| Компонент | Деталь |
|---|---|
| Пошук | Exa Search + Tavily + Google CSE + Wayback CDX |
| Аналіз | Gemini 2.0-flash (NER, statements, contradictions) + spaCy fallback |
| Візуалізація | pyvis граф акаунтів + Jinja2 HTML-досьє |
| Якість | 5-gate Corpus Health Score (YAML benchmark profiles) |
| Валідація | 4 актори різних типів — всі PASS |
| Архів | ZIP Evidence preservation (raw JSON + SQLite + report) |

---

## Домашні завдання

| Папка | ДЗ | Тема | Рівень |
|---|---|---|---|
| [ДЗ-02-Nestor-V/](ДЗ-02-Nestor-V/) | ДЗ-02 | Промптинг, RAG, LLM Guard, захист від ін'єкцій | 🔵🔴 |
| [ДЗ-03/](ДЗ-03/) | ДЗ-03 | MindsDB SQL + ArkhamMirror SHATTERED (28 shards) | 🔵🔴 |
| [ДЗ-04-Nestor-V/](ДЗ-04-Nestor-V/) | ДЗ-04 | Mini-pipeline: Crawl4AI + Playwright + Prometheus (risu.ua) | 🔴 |
| [ДЗ-05-Nestor-V/](ДЗ-05-Nestor-V/) | ДЗ-05 | Entity Resolution, граф зв'язків, Flowsint | 🔵🔴 |
| [ДЗ-06-Nestor-V/](ДЗ-06-Nestor-V/) | ДЗ-06 | Теорія графів: патентний граф БЕК, Gephi, Louvain (Q=0.956, 702 communities) | 🔵🔴 |
| [ДЗ-11-Nestor-V/](ДЗ-11-Nestor-V/) | ДЗ-11 | OSINT-звіт: операція Doppelganger (Italian campaign 2022–2024) | 🔵 |
| [ДЗ-12-Nestor-V/](ДЗ-12-Nestor-V/) | ДЗ-12 | Telegram-кластеризація: GroupInt + Neo4j + Gephi + gephi-ai MCP | 🔵🔴 |
| [ДЗ-17-Nestor-V/](ДЗ-17-Nestor-V/) | ДЗ-17 | Статистика: виявлення ботів — LogisticRegression + KMeans (500 акаунтів) | 🔵🔴 |
| [ДЗ-20-Nestor-V/](ДЗ-20-Nestor-V/) | ДЗ-20 | Верифікація супутникового знімку Maxar (Буча) за Берклійським протоколом | 🔵 |

---

## Gold actor

**Gold actor** — об'єкт дослідження з верифікованим ручним еталоном, на якому вимірюється точність pipeline.

Більшість ДЗ курсу побудовано навколо одного наскрізного кейсу: **публічна особа культурно-релігійної сфери з задокументованими інституційними зв'язками в RU-сфері** — типова задача для аналітика-розслідувача.

До запуску pipeline існувало вручну зібране OSINT-досьє з 167 верифікованих джерел (Wikipedia + первинні посилання). Це дало унікальну можливість валідації: автоматичний результат порівнюється з ручним еталоном по кожному домену і класу джерел. Саме звідси виникла метрика **Corpus Health Score** і 5-gate система.

> Gold actor — не «найзручніша публічна особа», а **методологічний бенчмарк**: відтворюваний, порівнювальний, задокументований.

Детальніше → [КР-Nestor-V/README.md § Контекст і вибір об'єкта](КР-Nestor-V/README.md)

---

## Стек

| Шар | Технології |
|---|---|
| Пошук | Exa Search · Tavily · Google CSE · Wayback CDX · HIBP |
| LLM | Gemini 2.0-flash · spaCy uk_core_news_sm · LLM Guard |
| Графи | pyvis · networkx · Gephi · Neo4j |
| Pipeline | Python 3.11 · Docker · Crawl4AI · Playwright · APScheduler |
| Дані | SQLite · PostgreSQL + pgvector · JSON |
| AI-агенти | Claude Code · OpenAI Codex · ChatGPT (діаграми) |
