# ДЗ-04: Report — Mini-pipeline risu.ua

**Дата:** 2026-05-01  
**Сайт:** [risu.ua](https://risu.ua) — Релігійно-інформаційна служба України  
**Зібрано:** 15 статей за ~57 секунд  
**Стек:** Crawl4AI · Playwright/Chromium · APScheduler · Prometheus · Docker Compose

---

## Що зроблено

### Basic level

Реалізовано повний pipeline збору даних:

1. **worker_html.py** — завантажує список статей з `risu.ua/novini_t1`, фільтрує посилання за патерном `_n\d+`, скрапить кожну статтю через Crawl4AI, зберігає raw JSON
2. **normalize.py** — очищає контент, нормалізує дати, фільтрує links по домену, додає `word_count`
3. **Docker Compose** — один `docker compose run --rm worker-html` запускає весь цикл

Приклад зібраної статті (реальні дані):

```
url:       risu.ua/glava-ugkc-zaklikav…_n163795
title:     Глава УГКЦ закликав до молитви і дієвого милосердя у День хворого
word_count: 494
fetched_at: 2026-05-01T13:54:29+00:00
```

### Advanced level

- **worker_js.py** — другий worker з JS wait strategies: `wait_for="css:h1"`, `delay_before_return_html=1.5`, dismiss cookie banner через `js_code`
- **scheduler.py** — APScheduler запускає crawl кожну годину, normalize через +5 хв
- **metrics.py** — Prometheus endpoint `:8000/metrics` з `success_rate`, `pages_crawled_total`, `pages_failed_total`, histogram `page_content_bytes`
- **Prometheus + Grafana** — повний моніторинг через `compose.yaml`

---

## Технічні знахідки

### 1. URL структура risu.ua

Очікуваний URL `/uk/news/` повертає 404 — сайт не має такого шляху.  
Реальна структура:

| Сторінка | URL |
|----------|-----|
| Список новин | `risu.ua/novini_t1` |
| Категорія | `risu.ua/pravoslavni_t9`, `risu.ua/katoliki_t14` тощо |
| Стаття | `risu.ua/nazva-statti_n163800` |

Патерн ідентифікатора статті: `_n\d+` в кінці URL — надійний і стабільний.

### 2. Playwright install-deps vs ручний список

Перша версія Dockerfile містила ручний список apt-пакетів — бракувало `libcairo2`.  
Рішення: `playwright install-deps chromium` встановлює всі залежності автоматично.

```dockerfile
# Було (неповний список):
RUN apt-get install -y libglib2.0-0 libnss3 ...

# Стало (повний, завжди актуальний):
RUN playwright install-deps chromium
RUN playwright install chromium
```

### 3. Link extraction: CSS strategy vs built-in

`JsonCssExtractionStrategy` не знаходила посилань на список — DOM-структура risu.ua не відповідала селекторам `article a`, `h2 a` тощо.  
Рішення: Crawl4AI вже витягує всі посилання у `result.links.internal` — фільтр по `_n\d+` дає чисті посилання на статті без CSS-специфіки.

### 4. Worker-js: коли він потрібен

На risu.ua `worker_html` достатній — весь контент у статичному HTML.  
`worker_js` потрібен для:
- **Нескінченний скрол** (infinite scroll) — контент завантажується динамічно
- **Lazy-load зображень** — якщо потрібна metadata зображень
- **Cookie/paywall банери** — блокують основний контент до кліку
- **SPA-фрагменти** — React/Vue компоненти, що рендеряться після JS

---

## Метрики запуску (2026-05-01)

```
pages_crawled_total{worker="html"} = 15
pages_failed_total{worker="html"}  = 0
success_rate{worker="html"}        = 1.0
Час виконання: ~57 секунд (15 сторінок × ~3.8 сек/сторінку)
```

Середній розмір контенту: 2 500–8 000 символів залежно від довжини статті.  
Найбільша стаття: `pro-sudovu-postanovu…_n163800` — 7 940 символів.

---

## AI-assisted workflow

Claude Code використовувався для діагностики broken parser:

1. Прочитав `src/config.py` → виявив помилковий `START_URL`
2. Запустив live-тест у Docker-контейнері → підтвердив 404
3. Знайшов правильний URL через crawl `risu.ua/novini_t1`
4. Виправив два файли (`config.py`, `worker_html.py`) автоматично

Детально: [`docs/ai-workflow-example.md`](docs/ai-workflow-example.md)

---

## Висновок

**risu.ua** — добре структурований публічний ресурс для OSINT-моніторингу релігійної сфери України. Crawl4AI з Playwright дає повний доступ до контенту без JavaScript tricks.

**Pipeline виконує своє завдання:** 15 статей зібрано за ~1 хвилину, нормалізовано і готово до подальшого аналізу (MindsDB, NotebookLM, osint-base).

**Головний урок:** URL-структура сайту — першочергова перевірка перед написанням будь-яких CSS-селекторів. Автоматична діагностика через Claude Code скоротила debug з ~30 хв до ~5 хв.

**Можливий наступний крок:** інтеграція з osint-base pipeline — автоматичне додавання зібраних статей у базу MNT-записів для моніторингу згадок про суб'єкт.
