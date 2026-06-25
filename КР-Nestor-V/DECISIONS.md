# Architecture Decisions

Довгоживучі рішення з обґрунтуванням. Короткі спостереження/gaps → `NOTES.md`.

---

## ADR-001 — Relevance filter: word-boundary токени
**Дата:** 2026-05-27  
**Рішення:** `_is_relevant()` перевіряє `\b{tok}\b` (regex), не substring.  
**Чому:** substring "чекаль" збігався б у "зачекальній" тощо. Word-boundary відсіює однофамільців і шум.  
**Компроміс:** кирилиця не має стандартних word-boundary chars у всіх локалях — тестовано, працює в Python `re` з `\b`.

---

## ADR-002 — Tavily skip для `site:` запитів
**Дата:** 2026-05-27  
**Рішення:** `if provider == "tavily" and "site:" in query: continue`  
**Чому:** Tavily ігнорує `site:` оператор (повертає нерелевантні результати замість відмови). Exa підтримує коректно.  
**Наслідок:** RU-site-list запити виконуються тільки через Exa.

---

## ADR-003 — Benchmark gold standard: Wikipedia footnotes
**Дата:** 2026-05-27  
**Рішення:** 167 Wikipedia footnotes як еталон покриття для Чекаль.  
**Чому:** Автоматично верифікований набір посилань, незалежний від pipeline. Альтернативи (ручний куратор, золотий список) непрактичні для більшості акторів.  
**Обмеження:** специфічний для одного актора; повторне використання для іншого актора потребує нового еталону.  
**Метрика:** L1 (exact URL) = 1.0, L2 (domain match) = 0.5; weighted recall по класах A-G.

---

## ADR-004 — Quality gates: профільна YAML конфігурація
**Дата:** 2026-05-28  
**Рішення:** Пороги gates в окремих YAML-файлах (`benchmark_profiles/`), не хардкод.  
**Чому:** КР-актор (cultural/RU-sphere) має інші норми ніж politician чи journalist. `ru_domain_ratio` до 60% — норма для каліграфа, аномалія для депутата.  
**Профілі:** `default.yaml` (загальний), `ua_cultural_ru_sphere.yaml` (Чекаль-тип).

---

## ADR-005 — collect_meta: tuple return з run_collect
**Дата:** 2026-05-28  
**Рішення:** `run_collect()` повертає `(list[dict], dict)` замість `list[dict]`.  
**Чому:** quality_check потребує `fetched_total` і `rejected_ratio` для technical gate. Ці дані існують тільки під час виконання collect — передавати через DB недоцільно.  
**Компроміс:** breaking change для існуючих викликів `run_collect` — виправлено в `run.py`.

---

## ADR-006 — Клас B (RU-media): known limitation
**Дата:** 2026-05-28  
**Рішення:** Не впроваджувати Yandex/SerpAPI зараз; зафіксувати як known gap.  
**Чому:** Exa і Tavily не індексують `.ru` медіа (`pravmir.ru`, `artos.org` тощо). RU-site-list запити через Exa технічно відправляються, але API не повертає результати. Yandex XML API потребує окремих ключів і compliance-review.  
**Метрика:** Class B weighted recall = 0% (64 gold refs).  
**Майбутнє:** `_search_yandex()` або SerpAPI як окремий collector, `enable_service_yandex: false` у settings.yaml за замовчуванням.

---

## ADR-007 — Bridge export: read-only package actor-osint-front → osint-base
**Дата:** 2026-05-29  
**Рішення:** `scripts/export_to_osint_base.py` — read-only JSON export, ніякого write-back у osint-base під час КР.  
**Чому:** КР pipeline — самостійний проєкт; прямий write-back додав би coupling і ризик data corruption у production DB. Export-пакет генерується локально, переглядається аналітиком, і тільки потім може бути вручну імпортований.  
**Mapping:**  
- pipeline `sources` → `mnt_records type=SOURCE`  
- pipeline `statements` → `mnt_records type=QUOTE`  
- pipeline `links` (з risk flags) → `mnt_records type=ENTITY`  
- `source_dstu` поле заповнюється автоматично через `pipeline/dstu.py`  
**Обмеження:** Export не включає `embedding` (vector(1536)) — потребує окремого embedding pipeline в osint-base.  
**Майбутнє:** Автоматичний import через `osint-base` ingestion API (post-КР).
