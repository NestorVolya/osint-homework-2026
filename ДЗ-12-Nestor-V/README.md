# ДЗ-12 — кластеризація Telegram-мереж і візуалізація графів · Basic + Advanced

Хто / чим: студент Nestor-V + Claude Code; GroupInt, Telegram API, Neo4j, Gephi, gephi-ai MCP, VPS Docker stack.

Тут: https://github.com/NestorVolya/osint-homework-2026/tree/main/ДЗ-12-Nestor-V

**Зроблено:**

- зібрано Telegram-повідомлення та `ENDORSES`-зв'язки через GroupInt;
- розгорнуто GroupInt + Neo4j на VPS у Docker з Traefik-доступом;
- імпортовано Neo4j-граф у Gephi через SSH tunnel;
- побудовано `Group -> Group` endorsement-граф на 70 вузлів і 68 ребер;
- обчислено degree, weighted degree, PageRank, betweenness centrality та modularity;
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
| [data/gephi_ai_summary.md](data/gephi_ai_summary.md) | секція Gephi AI / MCP для звіту |
| [scripts/gephi_mcp_run.py](scripts/gephi_mcp_run.py) | відтворення Gephi MCP аналізу та експорту |
| [screenshots/](screenshots/) | скріншоти GroupInt, Neo4j/Gephi імпорту, метрик і графів |
| [screenshots/17-gephi-ai-analysis-export.png](screenshots/17-gephi-ai-analysis-export.png) | фінальний експорт графа через gephi-ai |
| [screenshots/telegram-endorsements-expanded-gephi-ai.gephi](screenshots/telegram-endorsements-expanded-gephi-ai.gephi) | збережений Gephi-проєкт після MCP аналізу |
| [VPS_RUNTIME_STATUS.md](VPS_RUNTIME_STATUS.md) | короткий опис VPS/Traefik/GroupInt runtime |
| [PLAN.md](PLAN.md) | робочий план виконання |
| [SCREENSHOTS.md](SCREENSHOTS.md) | перелік потрібних скріншотів |

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

### Просунутий рівень

- [x] Додано Neo4j + Gephi workflow.
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
