# ДЗ-04 — Mini-pipeline: risu.ua

**Автор:** Nestor V.  
**Курс:** OSINT 2026  
**Рівень:** Advanced

Невеликий pipeline для збору новин із [risu.ua](https://risu.ua) — публічного українського ресурсу про релігію та суспільство. Збирає 10–15 сторінок, зберігає raw + normalized JSON, має scheduler, метрики (Prometheus + Grafana).

---

## Структура проєкту

```
ДЗ-04-Nestor-V/
├── compose.yaml          # Docker Compose: 5 сервісів
├── Dockerfile            # Python 3.11 + Playwright/Chromium
├── requirements.txt
├── config/
│   └── prometheus.yml    # Конфіг Prometheus scrape
├── src/
│   ├── config.py         # URL, шляхи, селектори
│   ├── metrics.py        # Prometheus counters/gauges
│   ├── worker_html.py    # Основний HTML-воркер
│   ├── worker_js.py      # JS-розширений воркер
│   ├── normalize.py      # Нормалізація raw → normalized
│   └── scheduler.py      # APScheduler
├── data/
│   ├── raw/              # Сирі JSON (один файл = одна сторінка)
│   └── normalized/       # Нормалізовані JSON
├── prompts/
│   └── check_parser_dom_change.md
├── docs/
│   ├── architecture.md
│   └── runbook.md
└── screenshots/
    └── run-example.png
```

---

## Швидкий старт

### Зібрати один раз (без scheduler)

```bash
# Зібрати образ і запустити worker-html
docker compose run --rm worker-html

# Нормалізувати результати
docker compose run --rm worker-html python src/normalize.py
```

### Повний стек (з scheduler + моніторингом)

```bash
docker compose up --build
```

Сервіси:

| Сервіс | Порт | Опис |
|--------|------|------|
| worker-html | 8000/metrics | HTML-воркер + Prometheus endpoint |
| worker-js | 8001/metrics | JS-воркер + Prometheus endpoint |
| scheduler | — | Запускає воркери кожну годину |
| prometheus | 9090 | Збирає метрики |
| grafana | 3000 | Дашборд (admin/admin) |

### Перевірити результати

```bash
ls data/raw/        # JSON файли сирих даних
ls data/normalized/ # Нормалізовані файли
curl localhost:8000/metrics  # Prometheus метрики
```

---

## Формат JSON

### Raw (`data/raw/`)

```json
{
  "url": "https://risu.ua/uk/news/...",
  "title": "Назва статті",
  "fetched_at": "2026-05-01T12:00:00+00:00",
  "source": "risu.ua",
  "content": "Текст статті у markdown-форматі...",
  "links": ["https://risu.ua/uk/news/..."],
  "metadata": {
    "worker": "html",
    "author": "Автор",
    "tags": ["релігія", "Україна"],
    "date_raw": "2026-04-30",
    "content_length": 3500
  }
}
```

### Normalized (`data/normalized/`)

```json
{
  "url": "https://risu.ua/uk/news/...",
  "title": "Назва статті",
  "fetched_at": "2026-05-01T12:00:00+00:00",
  "source": "risu.ua",
  "content": "Очищений текст статті...",
  "links": ["https://risu.ua/uk/news/..."],
  "word_count": 450,
  "normalized_at": "2026-05-01T12:05:00+00:00",
  "author": "Автор",
  "tags": ["релігія", "Україна"],
  "published_at": "2026-04-30",
  "worker": "html"
}
```

---

## worker-html vs worker-js

| | worker-html | worker-js |
|--|-------------|-----------|
| Мета | Список + базовий контент | Динамічний контент |
| wait_for | — | `css:h1` (чекає завантаження) |
| JS | Playwright за замовчуванням | + dismiss cookies JS |
| delay | — | 1.5 сек перед зчитуванням |
| Файли | `*.json` | `*_js.json` |

**Коли потрібен worker-js:** сторінки з lazy-load контентом, вбудованими відео, динамічними коментарями або будь-яким контентом, що з'являється після рендерингу JS.

---

## Метрики

Доступні через `GET :8000/metrics` (Prometheus format):

- `pages_crawled_total{worker}` — успішно зібрані сторінки
- `pages_failed_total{worker}` — помилки
- `success_rate{worker}` — частка успіху
- `last_crawl_timestamp` — час останнього crawl
- `page_content_bytes{worker}` — розмір контенту (histogram)
