# Prompt: Перевірка парсера після зміни DOM

**Використання:** запусти цей промпт у Claude Code коли підозрюєш, що risu.ua змінив структуру HTML і парсер перестав збирати контент.

---

## Промпт для Claude Code

```
Прочитай src/config.py і знайди поточні CSS-селектори для risu.ua:
- ARTICLE_LINK_SELECTORS (посилання на статті зі списку)
- TITLE_SELECTORS (заголовок статті)
- CONTENT_SELECTORS (тіло статті)
- DATE_SELECTORS (дата публікації)

Потім завантаж сторінку https://risu.ua/uk/news/ і одну статтю звідти (перше посилання).

Для кожного селектора перевір:
1. Чи існує елемент у поточному HTML?
2. Якщо ні — знайди відповідний елемент у DOM і запропонуй новий селектор.
3. Якщо так — покажи перші 100 символів знайденого тексту як підтвердження.

Після перевірки:
- Якщо всі селектори працюють → виведи "✓ Parser OK"
- Якщо є зламані селектори → оновити src/config.py з виправленими значеннями
  і пояснити що змінилось
```

---

## Ознаки зламаного парсера

| Симптом | Можлива причина |
|---------|----------------|
| `title` порожній у raw JSON | `h1` замінено на інший тег або клас |
| `content` порожній | CSS-клас `.article-body` змінився |
| `links` = [] | Шаблон URL `/uk/news/` змінився |
| 0 файлів у data/raw/ | Сторінка списку не завантажилась або змінилась структура |
| `fetched_at` є, але `content` < 100 chars | Контент захищений або lazy-load |

## Швидка ручна перевірка

```bash
# Перевірити останній зібраний файл
cat data/raw/*.json | python -c "
import json,sys
d=json.load(sys.stdin)
print('title:', d['title'][:60])
print('content len:', len(d['content']))
print('links:', len(d['links']))
"

# Або через docker
docker compose run --rm worker-html python -c "
import asyncio
from crawl4ai import AsyncWebCrawler
async def test():
    async with AsyncWebCrawler() as c:
        r = await c.arun('https://risu.ua/uk/news/')
        print('Success:', r.success)
        print('Links found:', len(r.links.get('internal',[])))
asyncio.run(test())
"
```
