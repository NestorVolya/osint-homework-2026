# Нотатки до КР — actor-osint-front-СС

> Проєктний рівень. Оновлювати перед здачею.

---

## Головна ідея КР

**Задача:** автоматичне OSINT-профілювання публічної особи за ПІБ/псевдонімом/email.  
**Вхід:** `seed` (рядок) + `seed_type` + опційний `profile.yaml`.  
**Вихід:** HTML-досьє + Markdown quality report + SQLite артефакти + ZIP.

**Внесок (новизна):**
- Corpus Health Score (5-gate автоматична оцінка якості корпусу джерел)
- Benchmark profiles — параметризована якість під тип актора (не hardcode)
- ARS-inspired anti-bias шари: DA steelman у класифікації риторики, contradiction detection, temporal gap detection, evidence anchoring в network links
- Validated на 4 акторах різних типів (ALL PASS) → generic pipeline, не overfitted

---

## Що проєкт є / чим не є

### Є:
- Standalone OSINT front pipeline (локальний, людина-тригер)
- Інструмент збору + структурування відкритих джерел
- Аналітична підтримка (corpus health, temporal gaps, blind zones) — не вирок
- Extensible через benchmark profiles

### Не є:
- Surveillance tool / mass-targeting (one-run per actor, human-in-the-loop)
- Замінником аналітика — financial judgment за людиною
- Source of truth — per-run SQLite ізольований, не впливає на інші системи
- Частиною VPS-стеку (Shoykhet, osint-base) — standalone, bridge-only export

---

## Архітектурні межі

```
seed input
  → collect (Exa + Tavily, federated, relevance gates)
  → account_discovery (URL mining + Wayback CDX + Sherlock-like + HIBP)
  → enrich:
      timeline (дати, WAR_CONTEXT_PERIODS)
      statements (Gemini LLM → DA steelman → rhetoric classification)
      network (spaCy NER + Gemini NER → evidence_quote per link)
      geoclusters (period+location aggregation)
  → detect_contradictions (Gemini, budget-gated, на compact statements)
  → quality_check (5 gates → corpus_health_score → temporal_gaps)
  → report HTML (+ accounts_graph.html)
  → report_md (7 секцій: blind zones, temporal gaps, суперечності)
  → ZIP archive
```

**Межі відповідальності:**
- Збір: лише публічні джерела (web search, відкриті акаунти, публічні архіви)
- Storage: per-run SQLite в `output/` — нема persistent global state
- LLM: тільки Gemini Flash, budget-gated (`max_gemini: 60`), з safety gate
- Export до зовнішніх систем: `scripts/export_to_osint_base.py` (read-only contract)

---

## Що вже реалізовано

| Модуль | Файл | Стан |
|--------|------|------|
| Collect (Exa + Tavily + Google CSE) | `pipeline/collect.py` | ✅ |
| Account discovery | `pipeline/account_discovery.py` | ✅ |
| Account graph (pyvis) | `pipeline/account_graph.py` | ✅ |
| Enrich timeline + WAR_CONTEXT | `pipeline/enrich_timeline.py` | ✅ |
| Enrich statements + DA steelman | `pipeline/enrich_statements.py` | ✅ |
| Detect contradictions (Gemini batch) | `pipeline/detect_contradictions.py` | ✅ |
| Enrich network + evidence_quote | `pipeline/enrich_network.py` | ✅ |
| Geoclusters | `pipeline/geoclusters.py` | ✅ |
| Quality check (5 gates + temporal gaps) | `pipeline/quality_check.py` | ✅ |
| Benchmark profiles | `benchmark_profiles/` | ✅ 3 профілі |
| HTML report | `templates/report.html.j2` | ✅ |
| MD report (blind zones, gaps, contradictions) | `pipeline/report_md.py` | ✅ |
| Storage (7 таблиць + evidence_quote) | `pipeline/storage/db.py` | ✅ |
| Gates (input / budget / safety) | `pipeline/gates/` | ✅ |
| Archive (ZIP) | `pipeline/storage/archive.py` | ✅ |

**ARS-inspired шари (додано в поточній сесії):**
- DA anti-confirmation-bias prompt у `EXTRACTION_PROMPT` (`enrich_statements.py`) — challenge перед `rhetoric_type`
- `detect_contradictions.py` — виявлення суперечностей між statements через Gemini
- `_detect_temporal_gaps()` у `quality_check.py` — rule-based, gap > 12 міс
- `evidence_quote` поле у `links` table + extraction (`enrich_network.py`)
- Секції "Не перевірено", "Часові прогалини", "Суперечності" у `report_md.py`

---

## DoD Evaluation (підтверджено на 4 акторах)

| Метрика | Поріг | Чекаль | Braschi | Коваленко | Філоненко |
|---------|-------|--------|---------|-----------|-----------|
| accepted_sources | ≥ 25 | ✅ 47-54 | ✅ 46 | ✅ 77 | ✅ 54 |
| unique_domains | ≥ 8 | ✅ 33 | ✅ 28 | ✅ 47 | ✅ 32 |
| shallow_ratio | ≤ 0.10 | ✅ 0.021 | ✅ 0.022 | ✅ 0.000 | ✅ 0.000 |
| median_text | ≥ 800 chars | ✅ 2697 | ✅ 2819 | ✅ 4198 | ✅ 3016 |
| runtime | ≤ 8 хв | ✅ ~78s | ✅ 68s | ✅ 93s | ✅ ~80s |
| all gates | 5/5 PASS | ✅ | ✅ | ✅ | ✅ |

Детально: `VALIDATION_REPORT_KR.md`

---

## Source packs без оверфіту під професії

**Проблема оверфіту:** якщо pipeline шукає лише за "каліграф" або "священик" — результати зміщені.

**Рішення (реалізовано):**
- Пошуковий запит будується з `seed` без `source_type` — generic fullname search
- `benchmark_profiles/` містять `query_context` для disambiguation (не для обмеження типу)
  - `braschi_catholic.yaml`: `query_context: "journalist theologian author"` → виключає motorsport Braschi
  - `ua_cultural_ru_sphere.yaml`: контекст для UA cultural actors з RU-sphere exposure
- `relevance_gate` фільтрує за alias-токенами (ПІБ, псевдоніми), а не за profession keywords
- `source_type` класифікується автоматично (`bio`, `interview`, `news`, `project`, `social`, `academic`, `other`) — після збору, не впливає на збір

**Підсумок:** pipeline збирає широко, класифікує вузько — не навпаки.

---

## RU coverage і blind zones

**Відомі обмеження (ADR-006):**

| Джерело | Стан | Причина |
|---------|------|---------|
| pravmir.ru, artos.org, radiovera.ru | ❌ 0% recall | Заблоковані Exa/Tavily crawlers |
| VK / OK | ❌ 0% | Потребує окремого adapter (не реалізовано) |
| Telegram (канали) | ❌ 0% | Потребує telegram-collector (не реалізовано) |
| Dzen / Rutube / YDB | ❌ 0% | Поза поточним coverage |
| web.archive.org | ✅ частково | Wayback CDX для відомих URL |
| Google CSE | ✅ опційно | 100 req/day безкоштовно; RU/IT coverage кращий |

**У кожному звіті (§7 report_quality.md):** секція "Не перевірено" генерується автоматично на базі метрик `telegram_count`, `vk_ok_count`, `ru_domain_ratio` — аналітик бачить blind zones per run.

**Для захисту:** RU-медіа limitation — задокументоване архітектурне рішення (ADR-006), не баг. Рекомендація: запускати паралельно з ручним пошуком по pravmir/artos для акторів з відомим RU-медіа присутністю.

---

## Safety / AI risk / cost

### Safety
- **LLM safety gate** (`pipeline/gates/safety_gate.py`): system prompt забороняє генерацію про приватних осіб, неперевіреної інформації, harm content
- **Human-in-the-loop:** pipeline не приймає рішень — аналітик інтерпретує artifacts
- **PII:** HIBP email → лише breach names (не паролі, не PII), per-run SQLite, нема cloud persistence
- **Output:** "кожен артефакт має тег джерела `[Sherlock]` / `[Gemini]` / `[regex]`" — прозорість провенансу

### AI risk
- **Confirmation bias:** DA steelman у `enrich_statements.py` — Gemini challenge перед rhetoric classification
- **Hallucination:** NER entities фільтруються через relevance gate (alias-токени) перед записом у links
- **Rate-limit fallback:** Gemini rate-limit → spaCy NER (без LLM classification, зазначається в звіті)

### Cost per run (Gemini Flash)
| Компонент | Токени ~avg | Вартість |
|-----------|-------------|----------|
| enrich_statements | 20-50K | ~$0.002 |
| detect_contradictions | 5-15K | ~$0.001 |
| enrich_network (NER) | 10-30K | ~$0.002 |
| **Разом** | ~35-95K | **~$0.005-0.010** |

Exa: ~$0.01-0.02/run (10-20 requests × $0.001). Tavily: аналогічно.  
**Загальний cost per run: < $0.05** при 47 sources.

---

## Що доробити перед здачею

- [ ] **Оновити VALIDATION_REPORT_KR.md** — додати новий run Чекаль 2026-06-06 (47 sources, health=1.00, temporal_gaps=5, ARS шари активні)
- [ ] **Перевірити pytest** — `pytest tests/ -v` має проходити (особливо після змін detect_contradictions + quality_check zero-sources fix)
- [ ] **Запустити хоча б 1 більше актора** (напр. Francesco Braschi або Філоненко) з новими ARS шарами → переконатись що detect_contradictions активується при наявності statements
- [ ] **Перевірити evidence_quote** у `records.sqlite` → таблиця links, колонка evidence_quote (не NULL для релевантних links)
- [ ] **README.md** — додати рядок про ARS-inspired шари до "Статус реалізації"
- [ ] **Перевірити Docker** (опційно) — `docker build` + dry-run

---

## Що не треба оверінженерити

- **Оркестрація:** pipeline sequential, без черги / broker — не потрібно для local front
- **Multi-language statements:** Italian / Russian statements через Gemini regex = 0, але це відомо й задокументовано — не треба фіксити для КР
- **HIBP:** опційний, pipeline деградує gracefully без ключа — не блокер
- **Export до osint-base:** `scripts/export_to_osint_base.py` — bridge contract, достатньо як є (read-only)
- **Narrative detection / echo clusters** — backlog, поза scope КР
- **Web UI / API endpoint** — не в scope (CLI)
- **CI/CD / GitHub Actions** — не потрібно для локального проєкту

---

## Формулювання для захисту

**На питання "що вирішує пайплайн?":**  
> Pipeline автоматизує першу фазу OSINT-розслідування: збір, структурування та якісну оцінку корпусу відкритих джерел про публічну особу. Замість ручного пошуку по 20+ платформах і Excel — отримуємо HTML-досьє з Corpus Health Score, таймлайном і мережею зв'язків за ~80 секунд.

**На питання "як уникнути bias?":**  
> Реалізовано три шари: (1) DA steelman instruction перед класифікацією риторики — Gemini зобов'язаний знайти найбільш нейтральну інтерпретацію перед вердиктом; (2) contradiction detection на compact statements — виявляє риторичні розгорнення; (3) blind zones секція в звіті — аналітик бачить що не перевірялось.

**На питання "чому 5 gates?":**  
> Кожен gate вимірює окремий вимір якості корпусу: coverage diversity (не один домін), depth/noise (не поверхневі тексти), risk signal (RU-rhetoric ratio), archive/temporal (архівна глибина), technical (дедуплікація). Composite Corpus Health Score = зважена сума, визначається профілем — інші профілі для різних типів акторів.

**На питання "чому не Shoykhet/осінт-бейс?":**  
> Різні шари. actor-osint-front-СС = producer front: збирає, структурує, оцінює. Shoykhet = judgment pipeline: приймає готові evidence packs і виносить вердикт FACT/DISC/GAP. Bridge contract забезпечує однобічну передачу.

**На питання "безпека?":**  
> (1) LLM safety gate у системному промпті; (2) всі артефакти теговані джерелом — аналітик знає провенанс; (3) per-run SQLite без cloud persistence; (4) HIBP повертає лише назви витоків, не паролі; (5) pipeline не робить вердиктів — тільки структурує.

**На питання "оверфіт на Чекаля?":**  
> Validated на 4 акторах: Чекаль (UA cultural), Braschi (IT/multilingual, 4 мови), Коваленко (UA-orthodox/social), Філоненко (academic/philosopher). Всі — 5/5 gates PASS, sources≥25, runtime≤93s. Braschi з 4 мовами і disambiguation через `query_context` — найсильніший anti-overfit аргумент.
