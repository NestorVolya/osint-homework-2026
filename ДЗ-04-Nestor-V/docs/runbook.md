# Runbook: risu.ua pipeline

## Перевірити, що parser працює

### 1. Запустити збір вручну

```bash
docker compose run --rm worker-html
```

Очікуваний вивід:
```
2026-05-01 12:00:00 [INFO] worker-html — Збираю список статей з https://risu.ua/uk/news/
2026-05-01 12:00:03 [INFO] worker-html — Знайдено 15 унікальних посилань на статті
2026-05-01 12:00:05 [INFO] worker-html — Скрапинг статті: https://risu.ua/uk/news/...
2026-05-01 12:00:07 [INFO] worker-html — Збережено → uk_news_....json (2800 chars)
...
2026-05-01 12:01:30 [INFO] worker-html — Готово. Зібрано сторінок: 15
```

### 2. Перевірити файли

```bash
ls data/raw/
# uk_news_article1.json  uk_news_article2.json  ...

# Перевірити перший файл
python -c "
import json, glob
f = sorted(glob.glob('data/raw/*.json'))[0]
d = json.load(open(f, encoding='utf-8'))
print('URL:', d['url'])
print('Title:', d['title'][:60])
print('Content (перші 200 chars):', d['content'][:200])
print('Links count:', len(d['links']))
"
```

### 3. Нормалізувати

```bash
docker compose run --rm worker-html python src/normalize.py
ls data/normalized/
```

### 4. Перевірити метрики

```bash
curl -s localhost:8000/metrics | grep pages_
# pages_crawled_total{worker="html"} 15.0
# pages_failed_total{worker="html"} 0.0
# success_rate{worker="html"} 1.0
```

---

## Діагностика проблем

### Симптом: 0 файлів у data/raw/

1. Перевір підключення до інтернету в контейнері:
   ```bash
   docker compose run --rm worker-html curl -I https://risu.ua
   ```
2. Перевір логи на ОШИБКИ:
   ```bash
   docker compose logs worker-html | grep ERROR
   ```
3. Можливо risu.ua змінив URL або заблокував bot. Спробуй вручну:
   ```bash
   docker compose run --rm worker-html python -c "
   import asyncio
   from crawl4ai import AsyncWebCrawler
   async def test():
       async with AsyncWebCrawler() as c:
           r = await c.arun('https://risu.ua/uk/news/')
           print('success:', r.success)
           print('links internal:', len(r.links.get('internal',[])))
   asyncio.run(test())
   "
   ```

### Симптом: файли є, але title або content порожні

Парсер не знайшов елементи → DOM змінився. Запусти:
```bash
# Prompt для Claude Code
cat prompts/check_parser_dom_change.md
```

Або вручну перевір нові селектори:
```bash
docker compose run --rm worker-html python -c "
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
schema = {'name':'test','baseSelector':'body','fields':[
    {'name':'h1','selector':'h1','type':'text'},
    {'name':'article','selector':'article','type':'text'},
]}
async def test():
    async with AsyncWebCrawler() as c:
        cfg = CrawlerRunConfig(extraction_strategy=JsonCssExtractionStrategy(schema))
        r = await c.arun('https://risu.ua/uk/news/religiya/2026/test-article/', config=cfg)
        import json; print(json.dumps(json.loads(r.extracted_content)[0], indent=2, ensure_ascii=False)[:500])
asyncio.run(test())
"
```

### Симптом: Prometheus не показує метрики

```bash
# Перевірити чи контейнер доступний
curl localhost:8000/metrics

# Перевірити Prometheus targets
curl localhost:9090/api/v1/targets | python -m json.tool | grep health
```

### Симптом: Grafana не підключається до Prometheus

1. Перейди на http://localhost:3000 (admin/admin)
2. Configuration → Data Sources → Add data source → Prometheus
3. URL: `http://prometheus:9090`
4. Save & Test

---

## Повний перезапуск

```bash
docker compose down
docker compose up --build
```

## Переглянути всі логи

```bash
docker compose logs -f
```
