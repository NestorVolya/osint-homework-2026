# КР Product Audit: actor-osint-front-СС

**Дата аудиту:** 2026-06-25  
**Аудитор:** незалежна оцінка pipeline як продукту  
**База:** `КР-Nestor-V/`  
**Статус КР:** технічно завершений (pytest 15/15, health=1.00, 4-actor validation PASS)

---

## 1. Що система реально дає

Pipeline автоматизує збір і структурування відкритих джерел про конкретного актора (особу). Від seed-вхідних даних (ПІБ, нікнейм або email) до повного набору артефактів:

| Артефакт | Опис |
|---|---|
| `report.html` | Інтерактивний HTML-звіт: timeline, statements, accounts, risk entities, bibliography |
| `report_quality.md` | 8-секційний MD-звіт: паспорт, corpus metrics, ДСТУ-бібліографія, обмеження |
| `quality_report.json` | Machine-readable: corpus_health_score, 5 gate statuses, 15+ metrics |
| `records.sqlite` | 7-таблична SQLite БД: sources, events, statements, links, accounts, geoclusters, locations |
| `accounts_graph.html` | Інтерактивний граф соціальних акаунтів (pyvis) |
| `contradictions.json` | Виявлені суперечності між statements |
| `*.zip` | Повний архів прогону: raw API responses + всі артефакти + БД |

**Час прогону:** ~15–25 хв залежно від Gemini rate-limit  
**Gold actor (benchmark):** Олексій Чекаль — 44 джерела, 34 унікальних домени, health=1.00

---

## 2. Критична оцінка з 4 позицій

### 2.1. Споживач (замовник, журналіст, юрист)

**Добре:**
- Звіт самодостатній — всі джерела з посиланнями і датами
- ДСТУ 8302:2015 бібліографія готова для академічної/юридичної документації
- Явне документування blind zones (аналітик знає, чого система не знайшла)
- Corpus Health Score дає швидку оцінку якості зібраного

**Відсутнє:**
- Немає executive summary — аналітик отримує дані, не висновки
- `Corpus Health = 1.00` не означає "всі факти підтверджені" — метрика структури корпусу, не достовірності
- Ризикові сигнали (RU-риторика, підозрілі зв'язки) розкидані по звіту — немає зведеного red flags блоку
- Немає графічного timeline — тільки таблиця з подіями

### 2.2. Програміст (той хто підтримує або розширює)

**Добре:**
- 15 Python-модулів з чіткою відповідальністю
- ADR (Architecture Decision Records) документують 7 ключових рішень
- YAML-профілі дозволяють перелаштовувати quality thresholds без зміни коду
- Budget gate запобігає неконтрольованим витратам API

**Відсутнє:**
- Всі API calls — sequential (~15 хв). Без asyncio
- Немає відновлення після збою — збій на stage 8 з 11 = перезапуск з нуля
- Pipeline stage не є плагіном — новий collector = ручне редагування `run.py`
- 80% enrichment pipeline (statements, network, contradictions) покрито тільки smoke-тестом, не unit-тестами
- War context periods (`WAR_CONTEXT_PERIODS`) hardcoded в `enrich_timeline.py`, не в config

### 2.3. OSINT-пошуковець (оператор)

**Добре:**
- 3 незалежних пошуковики з дедуплікацією (Exa + Tavily + Google CSE)
- Word-boundary relevance filter (`\b{token}\b`) відсіює однофамільців
- Sherlock-like probing: 10 платформ, Wayback CDX архівний пошук
- RU-site-list варіанти запитів для Exa

**Відсутнє / відоме обмеження:**
- **Class B recall = 0%** — pravmir.ru, artos.org, radiovera.ru поза досяжністю Exa/Tavily (ADR-006). 64 Wikipedia gold refs пропущено для актора Чекаль
- **Telegram = мінімальне покриття** — t.me/s/ не є пошуком по згадках особи в публічних каналах
- Sherlock знаходить акаунти за іменем, не за ідентичністю — результати вимагають ручної верифікації
- HIBP email breach check вимикається без ключа ($3.50/міс)

### 2.4. Дослідник / аналітик

**Добре:**
- Steelman anti-bias prompt в Gemini statement extraction: "consider charitable interpretation before assigning pro-russian"
- Автоматичне виявлення temporal gaps (>12 місяців між подіями)
- Rhetoric classification: 5 класів (pro-UA / pro-RU / bridge-building / ambiguous / neutral)
- 4-actor cross-validation на VALIDATION_REPORT_KR.md (Чекаль + Braschi + 2 UA актори)
- Contradiction detection між statements

**Відсутнє:**
- Research questions §2 — тільки TODO-шаблон для аналітика, нуль автоматики
- Немає longitudinal аналізу — як змінювалась риторика за роками?
- Temporal gaps виявлені, але причини не пропонуються
- Source credibility нерозмежована — BBC.com = local-blog.ua
- Contradiction detection shallow — між stored statements, не між наративами джерел
- Відсутній feedback loop — аналітик не може виправити помилкове statement і "зберегти" корекцію

---

## 3. Відомі обмеження (зафіксовані в ADR)

| Обмеження | ADR | Причина | Наслідок |
|---|---|---|---|
| RU-media (Class B) = 0% recall | ADR-006 | Exa/Tavily не індексують .ru медіа | Прогалина для акторів з РФ-зв'язками |
| Tavily ігнорує `site:` operator | ADR-002 | API limitation | .ru site-list тільки через Exa |
| Sherlock false positives | — | Пошук за іменем, не ідентичністю | Акаунти потребують ручної верифікації |
| Gemini rate-limit fallback | — | ResourceExhausted → regex/spaCy | rhetoric_risk_ratio = 0 при rate-limit (може бути оманливим) |
| HIBP потребує ключа | — | Платний API ($3.50/міс) | Email breach check silently skipped |
| Telegram coverage | — | t.me/s/ — публічні канали, не пошук згадок | Поле зацікавленості актором не виявляється |

---

## 4. Roadmap до production

### H1 — Аналітичний досвід (1–2 тижні)
*Тільки зміни в report.py + шаблоні. DB schema незмінна.*

- **Executive summary** — Gemini Flash Lite генерує 3–5 bullet findings. Disclaimer: "автоматично, потребує верифікації"
- **Red flags block** — зведений топ ризик-сигналів з explicit thresholds:
  - `rhetoric_risk_ratio > 0.20` → HIGH
  - `ru_domain_ratio > 0.40` → HIGH
  - `links.flags` з risk keywords → MEDIUM per entity
  - `temporal_gap > 36 months` → INFO
- **Timeline chart** — Chart.js замість таблиці подій, кольорування по war_context
- **Rhetoric trend** — bar chart by year: зміна rhetoric_type пропорцій
- **Source credibility tier** — top 30 tier1 (BBC/Reuters/Wikipedia/Суспільне/Радіо Свобода/...) + proxy rule
- **Auto-hypotheses** — Gemini: 3 відкритих питання для аналітика, не висновки
- **CLI progress bars** — tqdm по stages для нетехнічного аналітика

### H2 — Покриття джерел + Web UI (2–4 тижні)
*Нова залежність: Brave Search API (безкоштовний tier).*

- **Collect adapters architecture** — ABC pattern для нових collectors, реєстр в run.py
- **Brave Search API** — розширює покриття .ru доменів. Верифікувати: чи pravmir.ru/artos.org присутні в Brave
- **Telegram "поле зацікавленості"** — пошук згадок імені в публічних каналах через tgstat.com.ua API. Нова таблиця `telegram_mentions`. Виявляє мережу каналів що говорять про актора
- **Web UI (FastAPI)** — для нетехнічних аналітиків: submit seed → status polling → перехід до report. Мінімальний scope: POST /run, GET /status/{run_id}, GET /reports
- **Sherlock → 50+ платформ** + identity confirmation (2+ незалежних сигнали → `[confirmed]`)
- **Entity fuzzy dedup** — rapidfuzz (threshold 85%) в enrich_network.py

### H3 — Архітектурна зрілість (1–2 місяці)
*Після стабілізації H1–H2.*

- **Async collect** — asyncio/aiohttp: паралельні API calls. Прогноз: 15 хв → ~3–4 хв
- **Multi-actor correlation** — `compare_actors.py`: спільні entities між 2 акторами (SQLite ATTACH)
- **Longitudinal analysis** — при 2+ runs одного актора: rhetoric trend diff, нові/втрачені джерела
- **Stage retry** — при збої: 2 спроби + 30s затримка (замість повного перезапуску)
- **Per-statement confidence v1** — `confidence_score` = f(source_tier, extraction_method, corroboration_count)
- **War context config** — WAR_CONTEXT_PERIODS → settings.yaml (не hardcoded)

### Post-КР стадія (наступний цикл)
*Після завершення H1–H3. Вирішуватимуться більш складні gaps.*

- VK/OK: indirect sources (архіви, дзеркала) — VK API недоступний для UA
- RU-media direct scraping: CommonCrawl-based або проксі через партнерські мережі
- Telegram (приватні групи): потребує правового основання + акаунту
- ЄДРПОУ / Prozorro cross-reference: окремий data pipeline
- HIBP integration: отримати ключ ($3.50/міс) — швидка перемога

---

## 5. Що свідомо не робимо

| Рішення | Обґрунтування |
|---|---|
| ML quality scoring замість YAML thresholds | YAML простіший, пояснюваніший, вже validated на 4 акторах. ML на 44 зразках = гірша точність |
| Crawl4AI/Playwright scraper | Складна інфраструктура для маргінального gain. Brave API вирішує простіше |
| Louvain graph clustering | Коректний інструмент для 7K+ вузлів. Для 20 акаунтів одного актора — overkill |
| ArkhamMirror інтеграція | 28-shard framework змінює архітектуру принципово. Окрема оцінка |
| LLM-generated verdict | Ризик галюцинацій у юридично значущому контексті. Auto-hypotheses = питання, не відповіді |
| Real-time monitoring | One-shot архітектура. Черга + workers = окремий продукт |
| Face recognition | Legal/ethical gray zone в UA |

---

## 6. Production trajectory

```
КР (здача) → H1: UX → H2: Coverage + WebUI → H3: Scale → Post-KR: Deep gaps
```

Кожен горизонт — завершений, автономний стан. Деградації назад немає.

**Принцип розвитку:** обирати оптимальний інструмент за якістю рішення, не кількістю. Кожна нова залежність виправдана тільки якщо: (а) вирішує реальну задачу, (б) не складніша за custom-реалізацію, (в) не додає VPS-залежності без необхідності.

---

*Документ підготовлено на основі аудиту codebase, сесійних логів 2026-05-27 — 2026-06-23, та порівняльного аналізу `KR_OSINT_EXECUTION_COMPARATIVE_ANALYSIS.md`.*
