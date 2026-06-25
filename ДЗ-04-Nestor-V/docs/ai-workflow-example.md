# AI-assisted workflow: перевірка парсера після зміни DOM

**Дата:** 2026-05-01  
**Інструмент:** Claude Code (claude-sonnet-4-6)  
**Задача:** parser повернув порожній `content` у кількох статтях після оновлення risu.ua

---

## Контекст

Під час першого запуску `worker_html.py` парсер знаходив 0 статей — список був порожній. Потрібно було знайти причину і виправити селектори без ручного перебирання DOM.

---

## Сесія з Claude Code

### Крок 1 — діагностика

Промпт (з `prompts/check_parser_dom_change.md`):

```
Прочитай src/config.py і знайди поточні CSS-селектори для risu.ua.
Потім завантаж https://risu.ua/uk/news/ і перевір чи існують елементи у DOM.
```

**Claude Code виконав:**
```bash
# Прочитав src/config.py
START_URL = "https://risu.ua/uk/news/"   # ← знайдений URL

# Запустив перевірку
docker compose run --rm worker-html python -c "
import asyncio
from crawl4ai import AsyncWebCrawler
async def test():
    async with AsyncWebCrawler() as c:
        r = await c.arun('https://risu.ua/uk/news/')
        print('success:', r.success)
        print('markdown:', r.markdown[:200])
asyncio.run(test())
"
```

**Вивід:**
```
success: True
markdown: # 404
## Page not found :(
```

**Висновок Claude:** URL `https://risu.ua/uk/news/` повертає 404 — сторінки не існує.

---

### Крок 2 — знаходження правильного URL

```
Перевір альтернативні URL: risu.ua/, risu.ua/novini_t1, і покажи знайдені посилання.
```

**Claude Code виконав:**
```bash
docker compose run --rm worker-html python -c "
import asyncio
from crawl4ai import AsyncWebCrawler
async def test():
    async with AsyncWebCrawler() as c:
        r = await c.arun('https://risu.ua/novini_t1')
        articles = [l['href'] for l in r.links.get('internal',[])
                    if '_n' in l.get('href','')]
        print(f'Знайдено {len(articles)} статей')
        for a in articles[:5]: print(' ', a)
asyncio.run(test())
"
```

**Вивід:**
```
Знайдено 23 статей
  https://risu.ua/pro-sudovu-postanovu..._n163800
  https://risu.ua/u-sofijskomu-sobori..._n163798
  ...
```

---

### Крок 3 — виправлення коду

Claude Code **автоматично відредагував** `src/config.py`:

```diff
- START_URL = "https://risu.ua/uk/news/"
+ START_URL = "https://risu.ua/novini_t1"
```

І `src/worker_html.py`:

```diff
- return bool(re.search(r"/uk/(news|article)/", parsed.path))
+ return bool(re.search(r"_n\d+$", parsed.path))
```

---

### Крок 4 — верифікація

```bash
docker compose run --rm worker-html
```

```
[INFO] worker-html — Знайдено 23 унікальних посилань на статті
[INFO] worker-html — Збережено → pro-sudovu…_n163800.json (7940 chars)
...
[INFO] worker-html — Готово. Зібрано сторінок: 15
```

✅ **Проблема вирішена за 4 кроки без ручного перегляду HTML.**

---

## Висновок

Claude Code дозволив:
- **діагностувати** причину (404 на старому URL) без ручного debugging
- **знайти** правильний URL через live-тест прямо в контейнері
- **виправити** два файли автоматично з поясненням змін
- **верифікувати** результат одразу

Весь процес зайняв ~5 хвилин замість ручного 20–30 хв перебирання DOM і логів.

---

## Як запустити самостійно

```bash
# Відкрити проєкт у Claude Code
claude .

# Вставити промпт з файлу
cat prompts/check_parser_dom_change.md
```
