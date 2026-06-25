# 🔍 actor-osint-front-СС · КР-Nestor-V

> Автоматизований OSINT pipeline: seed → SQLite + HTML-досьє + JSON + ZIP

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)](https://python.org)
[![pytest](https://img.shields.io/badge/pytest-15%2F15%20PASS-brightgreen?logo=pytest)](tests/)
[![Corpus Health](https://img.shields.io/badge/Corpus%20Health-1.00-brightgreen)](examples/sample_run/)
[![Gates](https://img.shields.io/badge/Quality%20Gates-5%2F5%20PASS-brightgreen)](VALIDATION_REPORT_KR.md)

**Gold actor:** Олексій Чекаль — 44 джерела · 34 домени · health = 1.00 · 5/5 gates PASS

---

## Навігація

| 📄 | Що всередині |
|---|---|
| [examples/sample_run/](examples/sample_run/) | Реальний прогін (Чекаль): HTML-досьє, граф акаунтів, SQLite |
| [KR_PRODUCT_AUDIT.md](KR_PRODUCT_AUDIT.md) | Критика з 4 позицій + roadmap до production |
| [VALIDATION_REPORT_KR.md](VALIDATION_REPORT_KR.md) | 4 актори, всі gates PASS |
| [docs/adr/](docs/adr/) | 7 архітектурних рішень (ADR-001 … ADR-007) |
| [docs/COMPARATIVE_ANALYSIS.md](docs/COMPARATIVE_ANALYSIS.md) | Чому обрана ця реалізація: незалежний аудит 5 версій |
| [../README.md](../README.md) | Вся монорепа: ДЗ-02 … ДЗ-20 + КР |

---

## Контекст і вибір об'єкта дослідження

### Завдання курсу

Напрям 1 — **«Персони та соціальні мережі/геолокація»**.  
Задача: журналіст або правозахисна організація хоче верифікувати публічну особу, яка може поширювати небезпечні наративи — при цьому вхідна інформація фрагментарна (нікнейм, email або ПІБ).

Пайплайн має вирішувати **реальну задачу**, а не синтетичну. Не "знайди все про відому особу" — а "автоматично зберіть структуровану доказову базу, яку аналітик потім верифікує".

### Чому цей тип актора

Фокус КР — **маскований актор у культурно-релігійній сфері**:  
публічна фігура, що демонструє проукраїнську позицію, але при цьому системно присутня в проєктах, мережах або інституціях з Росією.

Контекст: повномасштабне вторгнення — і одночасно активна робота з гуманітарними "містками", церковними організаціями, культурними обмінами. Такий актор — типова задача для аналітика-розслідувача, але надзвичайно трудомістка вручну.

### Чому Чекаль як gold actor

До початку роботи над пайплайном існувало вручну складене OSINT-досьє:  
хронологічна таблиця подій, висловлювання з war-context, мережа зв'язків, гео-кластери, гіпотези A/B/В.

Основа ручного еталону — **Wikipedia-стаття про Чекаля**, яка містила вичерпну джерельну базу з первинними посиланнями: radiovera.ru, artos.org, pravmir.ru, meetingrimini.org, drukarnia.com.ua та ін. Стаття була видалена з Вікіпедії після публічного розкриття зв'язків у січні 2026 року, але збережена в archive.org:

> 📦 **Ручний еталон (архів):** [web.archive.org/web/20260129202211/uk.wikipedia.org/wiki/Чекаль…](https://web.archive.org/web/20260129202211/https://uk.wikipedia.org/wiki/%D0%A7%D0%B5%D0%BA%D0%B0%D0%BB%D1%8C_%D0%9E%D0%BB%D0%B5%D0%BA%D1%81%D1%96%D0%B9_%D0%93%D0%B5%D0%BE%D1%80%D0%B3%D1%96%D0%B9%D0%BE%D0%B2%D0%B8%D1%87)

Це дало **унікальну можливість валідації**: запустити pipeline на тому ж акторі і порівняти автоматичний результат із ручним еталоном — які події збіглись, що пропустив алгоритм, де помилився. Саме так виникла метрика **Corpus Health Score** і 5-gate система.

> Gold actor — не "найзручніша публічна особа", а **методологічний бенчмарк**:  
> відтворюваний, порівнювальний, задокументований.

Підсумок валідації: 44 джерела, 34 домени, health = 1.00, 5/5 gates PASS.  
Детально → [VALIDATION_REPORT_KR.md](VALIDATION_REPORT_KR.md)

---

## Як це будувалось

### Шлях від ДЗ до КР

Проєкт — синтез серії домашніх завдань курсу. Кожне ДЗ внесло шар або стало архітектурним аргументом "не брати":

```
ДЗ-02 Промптинг, RAG, LLM Guard   → steelman anti-bias prompt для Gemini
ДЗ-04 Crawl4AI + Playwright        → ADR-004: складна інфраструктура, відхилено
ДЗ-05 Entity resolution, pyvis     → NER + граф акаунтів (accounts_graph.html)
ДЗ-06 Gephi / Louvain clustering   → ADR: overkill для 20 акаунтів, відхилено
ДЗ-11 Doppelganger Italy звіт      → методологія explicit blind zones у звіті
ДЗ-12 GroupInt, Telegram topology  → ADR: вирішує іншу задачу, не mentions
ДЗ-17 ML-scoring (LogReg + KMeans) → ADR-005: YAML thresholds кращі, відхилено
ДЗ-20 Берклійський протокол        → принцип: документуй що НЕ підтверджено
```

### Multi-AI розробка

| AI-система | Роль |
|---|---|
| **Claude Code** | Основний партнер: архітектура, 15 модулів pipeline, тести, ADR, аудит |
| **Gemini 2.0-flash** | Вбудований у pipeline: NER, statement extraction, contradiction detection |
| **ChatGPT** | Допоміжна: діаграми для презентації, cross-validation аналізу, альтернативні погляди |

Підхід: не "AI пише за мене" — AI як **колега-розробник**. Рішення пояснюються, trade-offs документуються, відхилені варіанти записані в ADR.

### Порівняльний аудит: чому саме ця версія

До фіксації фінальної бази — незалежний аудит 5 паралельних реалізацій ([повний звіт →](docs/COMPARATIVE_ANALYSIS.md)):

| Реалізація | Тести | Validation | Звіт | Рішення |
|---|:---:|:---:|:---:|:---:|
| **actor-osint-front-СС** | ✅ 15/15 | ✅ 4 актори | ✅ 160KB HTML | **→ здача** |
| actor-osint-front | ⚠️ smoke | ⚠️ застарів | ⚠️ мінімальний sample | референс: кращі ідеї пошуку |
| osint-persona | ❌ без pytest | ❌ | ⚠️ | референс: username/email coverage |
| (CODEX) / (ClaudeCode) | — | — | — | тільки діаграми для презентації |

Критерій: не "більше функцій" — **validated на реальних акторах + документовані обмеження + відтворюваний запуск**.

---

## Аудит продукту

Детально → [KR_PRODUCT_AUDIT.md](KR_PRODUCT_AUDIT.md)

<table>
<tr>
<td width="50%">

**🧑‍⚖️ Споживач (журналіст / юрист)**
- ✅ Всі джерела з посиланнями і датами
- ✅ ДСТУ 8302:2015 бібліографія
- ✅ Explicit blind zones у §7 звіту
- ⚠️ Немає executive summary → H1
- ⚠️ Ризики розкидані, не зведені → H1

</td>
<td width="50%">

**👨‍💻 Програміст**
- ✅ 15 модулів, чітка відповідальність
- ✅ ADR-001 … ADR-007
- ✅ YAML-профілі замість хардкоду
- ⚠️ Sequential API calls (~15 хв) → H3
- ⚠️ Немає stage retry → H3

</td>
</tr>
<tr>
<td>

**🕵️ OSINT-пошуковець**
- ✅ 3 API-пошуковики + дедуплікація
- ✅ Wayback CDX, Sherlock-like, HIBP
- ⚠️ RU-медіа Class B = 0% recall → H2
- ⚠️ Telegram mentions відсутні → H2

</td>
<td>

**🔬 Дослідник / аналітик**
- ✅ Steelman anti-bias prompt
- ✅ Rhetoric classification (5 типів)
- ✅ Contradiction detection
- ⚠️ Немає longitudinal аналізу → H3
- ⚠️ Source credibility tier → H1

</td>
</tr>
</table>

---

## Стратегія розвитку

```
сьогодні ────────────────────────────────────────────────────► production
    │
    ▼
  [ H0 ]        [ H1 ]          [ H2 ]           [ H3 ]
  Здача    →  Analyst UX   →  Coverage +    →    Scale
  ✅ done     1-2 тижні       Web UI             1-2 місяці
                              2-4 тижні
                                    │
                                    ▼
                              Post-KR стадія:
                              VK mirrors, ЄДРПОУ,
                              RU-media direct,
                              Telegram (приватне)
```

| Горизонт | Що з'явиться | Нові залежності |
|---|---|---|
| **H1** | Executive summary (Gemini Flash Lite), red flags block, Chart.js timeline + rhetoric trend, source credibility tier, auto-hypotheses, tqdm | Chart.js (CDN) |
| **H2** | Brave Search API (→ .ru coverage), Telegram "поле зацікавленості" (mentions у публічних каналах), FastAPI Web UI, Sherlock → 50+ платформ | Brave API, tgstat API, FastAPI |
| **H3** | asyncio (15 хв → 3–4 хв), multi-actor correlation, longitudinal analysis, stage retry, per-statement confidence | aiohttp |

**Принцип:** мінімум залежностей. Кожна нова — тільки якщо вирішує реальну задачу і не складніша за custom-реалізацію.

<details>
<summary>Що свідомо не робимо і чому</summary>

| Що | Чому ні |
|---|---|
| ML quality scoring (ДЗ-17) | YAML thresholds простіші, пояснювані, validated на 4 акторах. ML на 44 зразках — гірша точність |
| Crawl4AI / Playwright | Складна інфраструктура для маргінального gain. Brave API вирішує простіше |
| Louvain / Gephi | Правильний інструмент для 7K+ вузлів. Для 20 акаунтів — overkill |
| Flowsint entity resolution | VPS-сервіс. rapidfuzz — одна бібліотека, достатньо |
| GroupInt для Telegram | Вирішує network topology, не пошук згадок людини |
| ArkhamMirror інтеграція | 28-shard framework змінює архітектуру принципово |
| VK API | Недоступний для UA після 2022 |
| LLM-generated verdict | Галюцинації в юридично значущому контексті. Auto-hypotheses = питання, не відповіді |

</details>

---

## Встановлення та запуск

**Вимоги:** Python 3.11+, API-ключі ([.env.example](.env.example))

```bash
git clone https://github.com/NestorVolya/osint-homework-2026
cd osint-homework-2026/КР-Nestor-V

python -m venv .venv && .venv\Scripts\activate   # Windows
pip install -r requirements.txt
python -m spacy download uk_core_news_sm
cp .env.example .env   # заповнити ключі
```

```bash
# Повний прогін (gold actor):
python -m pipeline.run --seed "Олексій Чекаль" --seed_type fullname \
  --profile benchmark_profiles/ua_cultural_ru_sphere.yaml

# Dry-run (без API, перевірка конфігурації):
python -m pipeline.run --seed "Тест" --seed_type fullname --dry-run

# Docker:
docker build -t actor-osint .
docker run --env-file .env -v "$(pwd)/output:/app/output" actor-osint \
  --seed "Ім'я Прізвище" --seed_type fullname
```

Підтримувані `seed_type`: `fullname` | `nickname` | `email` | `auto`

---

## Вихідні артефакти

```
output/2026-06-06_23-31-12/          ← gold actor run
├── report/
│   ├── report.html                  ← HTML-досьє (160KB)
│   │   timeline · statements · accounts · risk entities · bibliography
│   ├── report_quality.md            ← 7 секцій: паспорт, метрики, ДСТУ, blind zones
│   └── accounts_graph.html          ← інтерактивний граф акаунтів (pyvis)
├── artifacts/
│   ├── records.sqlite               ← 7 таблиць: sources, events, statements,
│   │                                   links, locations, accounts, geoclusters
│   └── contradictions.json
├── quality_report.json              ← corpus_health_score · 5 gates · 15+ метрик
└── 2026-06-06_23-31-12.zip         ← повний архів + raw API responses
```

📂 Приклад: [examples/sample_run/report/report.html](examples/sample_run/report/report.html)

---

## API та джерела

| Сервіс | Призначення | Ключ |
|---|---|---|
| [Exa Search](https://exa.ai) | Основний веб-пошук, semantic search | `EXA_API_KEY` |
| [Tavily](https://tavily.com) | Резервний пошук | `TAVILY_API_KEY` |
| [Gemini 2.0-flash](https://ai.google.dev) | NER · statements · contradictions · risk | `GEMINI_API_KEY` |
| [Google CSE](https://developers.google.com/custom-search) | RU/multilingual (100 req/day free) | `GOOGLE_CSE_API_KEY` |
| [Wayback CDX](https://web.archive.org/cdx/) | Архівні записи | — |
| [HIBP v3](https://haveibeenpwned.com/API/v3) | Email breach check | `HIBP_API_KEY` |
| HTTP probing | Sherlock-like: 10 платформ за username | — |

Fallback: Gemini rate-limit → spaCy `uk_core_news_sm`

---

## Технічний стан

| Компонент | Статус |
|---|:---:|
| pytest | ✅ 15/15 |
| 4-actor validation (Чекаль + Braschi + 2 UA) | ✅ 5/5 gates |
| Corpus Health Score (gold actor) | ✅ 1.00 |
| Docker | ✅ |
| ADR (7 рішень) | ✅ |
| Відомі обмеження (RU Class B, Sherlock FP, HIBP) | ✅ задокументовані |

<details>
<summary>Повний статус модулів pipeline</summary>

| Модуль | Файл | Статус |
|---|---|:---:|
| Collect (Exa + Tavily) | `pipeline/collect.py` | ✅ |
| Account discovery | `pipeline/account_discovery.py` | ✅ |
| Account graph | `pipeline/account_graph.py` | ✅ pyvis |
| Enrich timeline | `pipeline/enrich_timeline.py` | ✅ WAR_CONTEXT |
| Enrich statements | `pipeline/enrich_statements.py` | ✅ Gemini + steelman |
| Enrich network | `pipeline/enrich_network.py` | ✅ NER + risk flags |
| Geoclusters | `pipeline/geoclusters.py` | ✅ |
| Quality Check | `pipeline/quality_check.py` | ✅ 5 gates |
| Detect contradictions | `pipeline/detect_contradictions.py` | ✅ H/M/L |
| MD Report | `pipeline/report_md.py` | ✅ 7 секцій |
| HTML Report | `templates/report.html.j2` | ✅ |
| Benchmark profiles | `benchmark_profiles/` | ✅ default + ua_cultural_ru_sphere + braschi |
| Storage (SQLite) | `pipeline/storage/db.py` | ✅ 7 таблиць |
| Archive (ZIP) | `pipeline/storage/archive.py` | ✅ |
| Gates | `pipeline/gates/` | ✅ input / budget / safety |
| Bridge export | `scripts/export_to_osint_base.py` | ✅ ADR-007 |

</details>

---

<sub>Монорепа курсу: <a href="../README.md">osint-homework-2026</a> · ДЗ-02 … ДЗ-20 + КР</sub>
