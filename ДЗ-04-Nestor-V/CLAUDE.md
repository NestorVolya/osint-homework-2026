# CLAUDE.md — ДЗ-04 risu.ua pipeline

## Мета проєкту

Mini-pipeline для збору новин із risu.ua. Використовує Crawl4AI + Docker Compose.
Навчальний проєкт курсу OSINT 2026 (Advanced level).

## Ключові файли

| Файл | Роль |
|------|------|
| `src/config.py` | CSS-селектори, URL, шляхи |
| `src/worker_html.py` | Головний воркер (list → articles → raw JSON) |
| `src/worker_js.py` | JS-воркер (re-crawl з очікуванням контенту) |
| `src/normalize.py` | raw → normalized JSON |
| `src/scheduler.py` | APScheduler (запуск кожну годину) |
| `src/metrics.py` | Prometheus counters/gauges |
| `compose.yaml` | 5 Docker-сервісів |

## Як перевірити, що parser працює

```bash
# 1. Запустити воркер вручну
docker compose run --rm worker-html

# 2. Перевірити наявність файлів
ls data/raw/

# 3. Перевірити вміст першого файлу
cat data/raw/*.json | head -30

# 4. Якщо title або content порожній — запустити перевірку через Claude Code
# Промпт: prompts/check_parser_dom_change.md
```

## AI-assisted workflow

```bash
# Відкрити проєкт у Claude Code
claude .

# Запустити перевірку парсера
# /run prompts/check_parser_dom_change.md

# Типовий сценарій: DOM на risu.ua змінився, селектори перестали працювати
# Claude Code:
# 1. Читає src/config.py (поточні селектори)
# 2. Завантажує рису.ua/uk/news/
# 3. Перевіряє наявність елементів у HTML
# 4. Пропонує оновлені селектори
# 5. Редагує src/config.py
```

## Обмеження і важливі деталі

- `PYTHONPATH=/app/src` — всі src-файли доступні як модулі без відносних імпортів
- `data/` монтується як volume — файли зберігаються між перезапусками контейнера
- worker-js читає URL із data/raw/ → треба запустити worker-html першим
- Playwright потребує Chromium-залежностей у Dockerfile — не видаляй apt-get блок
- Rate limiting: `asyncio.sleep(1)` між сторінками — не прибирай без причини

## Що перевіряти після зміни DOM

1. Заголовок (`h1`) — завжди є, якщо сторінка завантажилась
2. Контент (`.article-body`) — якщо порожній, клас змінився
3. Посилання (внутрішній `/uk/news/`) — якщо 0, змінився шаблон URL
4. Дата (`time[datetime]`) — перевірити атрибут vs текст

Для швидкої перевірки: `prompts/check_parser_dom_change.md`
