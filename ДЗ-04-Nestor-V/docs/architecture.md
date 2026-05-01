# Архітектура: risu.ua mini-pipeline

## Схема потоку даних

```
┌─────────────────────────────────────────────────────────┐
│                      risu.ua                            │
│              https://risu.ua/uk/news/                   │
└───────────────────┬─────────────────────────────────────┘
                    │ HTTP (Playwright/Chromium)
          ┌─────────▼──────────┐
          │   worker-html      │  CSS extraction
          │  (Crawl4AI basic)  │  list page → article links
          └─────────┬──────────┘  → article content
                    │                → raw JSON × 15
                    │ reads URLs
          ┌─────────▼──────────┐
          │    worker-js       │  JS wait + structured
          │ (Crawl4AI +JS cfg) │  extraction (lead, tags,
          └─────────┬──────────┘  images) → raw_js JSON
                    │
          ┌─────────▼──────────┐
          │   normalize.py     │  clean content
          │                    │  normalize dates
          └─────────┬──────────┘  filter links
                    │             → normalized JSON
          ┌─────────▼──────────┐
          │    data/           │
          │  raw/*.json        │
          │  normalized/*.json │
          └────────────────────┘

─── Scheduling ────────────────────────────────────────────

          ┌─────────────────────┐
          │    scheduler.py     │  APScheduler
          │                     │  crawl   @ every 60 min
          └──┬──────────────────┘  normalize @ +5 min
             │ triggers
             ▼
        worker-html → normalize

─── Monitoring ────────────────────────────────────────────

  worker-html :8000/metrics ──┐
  worker-js   :8000/metrics ──┼──► Prometheus :9090 ──► Grafana :3000
                               │    (scrape every 30s)    (dashboards)
```

## Сервіси Docker Compose

| Сервіс | Image | Port | Роль |
|--------|-------|------|------|
| worker-html | custom (Python 3.11 + Playwright) | 8000 | HTML crawl + metrics |
| worker-js | custom (Python 3.11 + Playwright) | 8001 | JS crawl + metrics |
| scheduler | custom | — | APScheduler trigger |
| prometheus | prom/prometheus | 9090 | Metrics store |
| grafana | grafana/grafana | 3000 | Visualization |

## Формати файлів

```
data/
├── raw/
│   ├── uk_news_article-slug.json      ← worker-html output
│   └── uk_news_article-slug_js.json   ← worker-js output
└── normalized/
    ├── uk_news_article-slug.json      ← cleaned, word_count added
    └── uk_news_article-slug_js.json
```

## Технологічний стек

- **Crawl4AI** — async web crawler з Playwright backend
- **APScheduler** — планувальник задач (BlockingScheduler)
- **prometheus-client** — Python SDK для Prometheus метрик
- **Docker Compose** — оркестрація всіх сервісів

## Відмінність worker-html / worker-js

```
worker-html:                    worker-js:
  BrowserConfig(                  BrowserConfig(
    headless=True                   headless=True,
  )                                 java_script_enabled=True
  CrawlerRunConfig(               )
    extraction=CssExtract         CrawlerRunConfig(
  )                                 js_code=dismiss_cookies,
                                    wait_for="css:h1",
                                    delay_before_return_html=1.5,
                                    extraction=JsonCssExtract(schema)
                                  )
```
