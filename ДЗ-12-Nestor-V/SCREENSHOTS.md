# ДЗ-12: список скриншотів

**Папка:** `D:\projects\osint-homework-2026\ДЗ-12-Nestor-V\screenshots`

Ціль: мати мінімальний набір доказових скриншотів для звіту, без секретів, OTP, номерів телефону, `api_id`, `api_hash` або Telegram session data.

---

## Обов'язкові скриншоти

| Файл | Що показати | Для якого розділу |
|---|---|---|
| `01-groupint-stack-running.png` | GroupInt відкритий у браузері або Docker containers `groupint-streamlit` + `groupint-neo4j` у статусі running | Методологія |
| `02-groupint-telegram-connected.png` | GroupInt після успішного підключення Telegram session; секрети мають бути приховані | Методологія |
| `03-groupint-scrape-result.png` | Результат збору одного seed-каналу: canonical id, кількість повідомлень/учасників/endorsements, якщо видно | Збір даних |
| `04-neo4j-labels-relationships.png` | Neo4j Browser або cypher-shell з labels/relationship types: `Group`, `Message`, `User`, `MEMBER_OF`, `ENDORSES` тощо | Підготовка даних |
| `05-gephi-import-overview.png` | Граф після імпорту в Gephi до фінального layout або на першому overview | Графова візуалізація |
| `06-gephi-modularity-report.png` | Gephi Statistics: Modularity report або таблиця з `modularity_class` | Кластери |
| `07-gephi-centrality-ranking.png` | Gephi Data Laboratory / Statistics з degree, weighted degree, betweenness або PageRank | Найвпливовіші канали |
| `08-gephi-final-network.png` | Фінальна візуалізація: кольори = кластери, розмір вузлів = influence metric, ребра = weight | Графова візуалізація |
| `09-pattern-matching-examples.png` | Таблиця/CSV/ноутбук/термінал з 3 прикладами pattern matching | Pattern matching |
| `10-final-report-preview.png` | Перегляд готового Markdown/HTML/PDF звіту або структура фінального файлу | Відтворюваність / здача |

---

## Опційні скриншоти для просунутого рівня

| Файл | Що показати | Коли потрібен |
|---|---|---|
| `11-neo4j-browser-central-nodes.png` | Neo4j Browser graph view або Cypher top central nodes | Якщо порівнюємо Gephi та Neo4j |
| `12-gephi-bridge-nodes-betweenness.png` | Вузли-мости за high betweenness, бажано zoom на міжкластерну зону | Якщо окремо описуємо bridge channels |
| `13-forward-only-graph.png` | Окремий граф лише для forwards / endorsements | Якщо робиться окремий тип графа |
| `14-mentions-only-graph.png` | Окремий граф лише для mentions | Якщо робиться порівняння типів ребер |
| `15-narrative-timeline.png` | Часова лінія поширення одного наративу | Якщо додається часовий аналіз |
| `16-gephi-project-saved.png` | Gephi з відкритим `.gephi` або експортом `.gexf` | Для доказу відтворюваності |

---

## Правила санітизації

- Замазати або обрізати телефон, OTP, `api_id`, `api_hash`, session names.
- Не показувати приватні повідомлення або персональні дані приватних користувачів.
- Для прикладів pattern matching достатньо каналу, часу, короткого фрагмента тези, URL/domain і hash/message id.
- Якщо скриншот містить сирий Telegram-текст, залишати тільки релевантний фрагмент і не перевантажувати звіт довгими цитатами.

---

## Мінімальний набір для здачі

Якщо часу мало, достатньо цих 5:

1. `03-groupint-scrape-result.png`
2. `05-gephi-import-overview.png`
3. `06-gephi-modularity-report.png`
4. `08-gephi-final-network.png`
5. `09-pattern-matching-examples.png`

Цей набір закриває: GroupInt, graph import, community detection, graph visualization, pattern matching.
