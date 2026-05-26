# ДЗ-12 — кластеризація Telegram-мереж і візуалізація графів · Basic + Advanced

![Gephi endorsement graph](screenshots/17-gephi-ai-analysis-export.png)

Хто / чим: студент Nestor-V + Claude Code; GroupInt, Telegram API, Neo4j, Gephi, gephi-ai MCP, VPS Docker stack.

Тут: https://github.com/NestorVolya/osint-homework-2026/tree/main/ДЗ-12-Nestor-V

**Зроблено:**

- зібрано Telegram-повідомлення та `ENDORSES`-зв'язки через GroupInt;
- розгорнуто GroupInt + Neo4j на VPS у Docker з Traefik-доступом;
- імпортовано Neo4j-граф у Gephi через SSH tunnel;
- побудовано `Group -> Group` endorsement-граф на 70 вузлів і 68 ребер;
- додано conservative deduplication: 60 вузлів і 58 ребер у clean graph;
- обчислено degree, weighted degree, PageRank, betweenness centrality та modularity;
- експортовано `Message` nodes з Neo4j у `data/raw/groupint_messages.csv`;
- виконано text pattern matching: однакові формулювання, синхронні публікації, повторювані наративи;
- класифіковано ролі каналів: primary source candidates, retransmitters, amplifiers, bridge notes;
- виконано Gephi AI / MCP аналіз, експортовано PNG і збережено `.gephi` проєкти;
- підготовлено фінальний OSINT-звіт у Markdown.

**Де:** Local Windows 10 + VPS `hostinger-vps` (`/docker/groupint`) + Gephi Desktop 0.11.2.

---

## Структура здачі

| Файл | Зміст |
|---|---|
| [AI_OSINT_HW_Clustering_PatternMatching_Nestor-V.md](AI_OSINT_HW_Clustering_PatternMatching_Nestor-V.md) | основний звіт ДЗ-12 |
| [data/nodes_with_communities.csv](data/nodes_with_communities.csv) | експорт вузлів з Gephi: communities, PageRank, degree, weighted degree |
| [data/edges_endorsements.csv](data/edges_endorsements.csv) | експорт ребер `ENDORSES` з вагами, raw links і message ids |
| [data/raw/groupint_messages.csv](data/raw/groupint_messages.csv) | raw export повідомлень з Neo4j / GroupInt для text analysis |
| [data/processed/nodes_clean.csv](data/processed/nodes_clean.csv) | вузли після conservative deduplication |
| [data/processed/edges_endorsements_clean.csv](data/processed/edges_endorsements_clean.csv) | ребра після conservative deduplication |
| [data/processed/deduplication_notes.md](data/processed/deduplication_notes.md) | протокол очищення дублікатів і шуму |
| [data/processed/text_patterns.csv](data/processed/text_patterns.csv) | знайдені exact/similar повтори текстів |
| [data/processed/synchronized_posts.csv](data/processed/synchronized_posts.csv) | синхронні exact-text публікації |
| [data/processed/narrative_summary.md](data/processed/narrative_summary.md) | групування повторюваних тез за narrative tags |
| [data/processed/channel_roles.csv](data/processed/channel_roles.csv) | ролі каналів за графовими ознаками |
| [data/processed/gephi_neo4j_comparison.md](data/processed/gephi_neo4j_comparison.md) | порівняння ролей Neo4j та Gephi у workflow |
| [data/processed/coordination_hypothesis.md](data/processed/coordination_hypothesis.md) | обережна гіпотеза про можливу координацію / спільне джерело |
| [data/gephi_ai_summary.md](data/gephi_ai_summary.md) | секція Gephi AI / MCP для звіту |
| [scripts/gephi_mcp_run.py](scripts/gephi_mcp_run.py) | відтворення Gephi MCP аналізу та експорту |
| [scripts/clean_graph_data.py](scripts/clean_graph_data.py) | conservative deduplication для вузлів і ребер |
| [scripts/classify_channel_roles.py](scripts/classify_channel_roles.py) | евристична класифікація ролей каналів |
| [scripts/analyze_text_patterns.py](scripts/analyze_text_patterns.py) | пошук repeated text, sync windows і narrative tags |
| [screenshots/](screenshots/) | скріншоти GroupInt, Neo4j/Gephi імпорту, метрик і графів |
| [screenshots/17-gephi-ai-analysis-export.png](screenshots/17-gephi-ai-analysis-export.png) | фінальний експорт графа через gephi-ai |
| [screenshots/telegram-endorsements-expanded-gephi-ai.gephi](screenshots/telegram-endorsements-expanded-gephi-ai.gephi) | збережений Gephi-проєкт після MCP аналізу |

## Acceptance Criteria — самоперевірка

### Базовий рівень

- [x] Використано GroupInt для збору Telegram-даних.
- [x] Збережено структуровані дані у CSV.
- [x] Побудовано граф у Gephi.
- [x] Є мінімум одна графова візуалізація.
- [x] Є таблиця топ-10 найбільш впливових / цитованих каналів.
- [x] Описано мінімум 2 кластери.
- [x] Наведено мінімум 3 приклади pattern matching.
- [x] Висновки зроблені на основі графа, а не лише ручного перегляду каналів.
- [x] Зафіксовано очищення дублікатів і технічного шуму.
- [x] Позначено ролі каналів: primary source candidates, retransmitters, amplifiers, bridge notes.
- [x] Додано обережну гіпотезу про можливу координацію без видавання її за доведений факт.

### Просунутий рівень

- [x] Додано Neo4j + Gephi workflow.
- [x] Додано порівняння ролей Neo4j та Gephi у workflow.
- [x] Додано gephi-ai MCP / Claude Code аналіз.
- [x] Перевірено PageRank, weighted degree, betweenness centrality.
- [x] Виділено hub-and-spoke структуру та відсутність формальних bridge-вузлів за betweenness.
- [x] Збережено відтворюваний скрипт `scripts/gephi_mcp_run.py`.

## Відтворення

1. Запустити GroupInt + Neo4j на VPS або локально.
2. Підключити Telegram-сесію через GroupInt.
3. Для seed-каналів зібрати messages і `Extract endorsements from messages`.
4. Імпортувати в Gephi labels `Group` і relationship `ENDORSES`.
5. Запустити Gephi MCP plugin і перевірити `http://127.0.0.1:8080/health`.
6. Виконати:

```powershell
cd D:\projects\osint-homework-2026\ДЗ-12-Nestor-V
D:\projects\gephi-ai\.venv\Scripts\python.exe scripts\gephi_mcp_run.py
```

7. Перевірити PNG, `.gephi` і `data/gephi_ai_summary.md`.
8. Для clean data, ролей і pattern matching виконати:

```powershell
python scripts/clean_graph_data.py
python scripts/classify_channel_roles.py
python scripts/analyze_text_patterns.py
```
