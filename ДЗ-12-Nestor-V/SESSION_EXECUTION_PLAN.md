# ДЗ-12 — структурований план і опис виконання сесії

Дата сесії: 2026-05-25 — 2026-05-26  
Проєкт: `D:\projects\osint-homework-2026\ДЗ-12-Nestor-V`  
GitHub: https://github.com/NestorVolya/osint-homework-2026/tree/main/ДЗ-12-Nestor-V

## 1. Мета сесії

Підготувати ДЗ-12 за вимогами викладача:

- зібрати Telegram-дані через GroupInt;
- побудувати граф каналів / груп;
- знайти кластери, впливові канали, повторювані патерни;
- зробити Gephi / Neo4j аналіз;
- додати gephi-ai / Claude Code аналіз;
- підготувати звіт, CSV, скриншоти, `.gephi` файли і відтворюваність;
- розмістити результат на GitHub.

## 2. Вихідні обмеження і рішення

### 2.1. Архітектурне рішення

Початковий урок описував desktop workflow:

```text
GroupInt localhost:18501
Neo4j localhost:17474 / 17687
Gephi через Neo4j plugin
```

Фактичне рішення для цієї роботи:

```text
GroupInt + Neo4j на VPS / Docker
Traefik public routes
Neo4j auth enabled
Gephi через SSH tunnel
gephi-ai MCP локально
```

Причина: користувач не хотів локальний Docker Desktop; Docker runtime дозволено на VPS.

### 2.2. Графова модель

Оскільки основні seed-об'єкти були Telegram-каналами, а не відкритими групами, учасники / автори не стали основою графа.

Обрана модель:

| Об'єкт | Тип |
|---|---|
| Telegram канал / група | `Group` node |
| t.me / @mention посилання між каналами | `ENDORSES` edge |

Це зафіксовано у звіті як обмеження: аналіз побудований на `ENDORSES`, а не на membership graph.

## 3. Етапи виконання

## Етап 1 — підготовка плану і чеклистів

Створено робочі матеріали:

| Файл | Призначення |
|---|---|
| `PLAN.md` / `PLAN.html` | план виконання ДЗ-12 |
| `SCREENSHOTS.md` / `SCREENSHOTS.html` | перелік потрібних скриншотів |
| `LESSON12_CHECKLIST.html` | чеклист з уроку 12 у HTML |
| `ENVIRONMENT_PLAN.md` | план середовища local/VPS |

Мета етапу: не починати технічне виконання без зрозумілого плану і меж відповідальності.

## Етап 2 — перевірка локального Streamlit і відмова від локального Docker

Було перевірено локальне Python/Streamlit середовище. Streamlit smoke app запускався на `localhost:8501`, але це не було GroupInt runtime.

Після уточнення архітектури ухвалено:

- локально Docker Desktop не використовувати;
- GroupInt і Neo4j розгорнути на VPS;
- локально використовувати Gephi, Claude Code, gephi-ai MCP, scripts.

## Етап 3 — розгортання GroupInt / Neo4j на VPS

VPS:

```text
alias: hostinger-vps
path: /docker/groupint
```

Підготовлено runtime notes:

| Файл | Призначення |
|---|---|
| `VPS_RUNTIME_STATUS.md` | стан VPS runtime |
| `VPS_RUNTIME_STATUS.html` | HTML-версія |
| `vps/docker-compose.groupint.yml` | compose reference для GroupInt/Neo4j |

Рішення:

- GroupInt public через Traefik + Basic Auth;
- Neo4j Browser через Traefik route;
- Neo4j Bolt з auth;
- для Gephi використовувати SSH tunnel замість public Bolt/TLS.

## Етап 4 — Telegram session у GroupInt

Telegram / Grizzly / API credentials були вже підготовлені користувачем.

У GroupInt:

- створено Telegram client;
- пройдено OTP;
- session збережено на сервері;
- screenshot sanitized перед публікацією.

Важливе security-рішення:

- не публікувати `.env`, `secrets.toml`, OTP, phone, api_id, api_hash, session string;
- чутливий screenshot `04-groupint-telegram-session-saved-sensitive.png` додатково замазано перед GitHub.

## Етап 5 — збір seed-каналів

Seed-канали:

| Seed | Роль у зборі |
|---|---|
| `Republic_Of_GaGauZia` | головний seed, дав найбільше endorsement edges |
| `pridnestrovec` | багато повідомлень, мало endorsement-зв'язків |
| `gagauznewsmd` | додатковий регіональний seed |
| `MoldovaPolitics` | окремий Moldova-сегмент |

У GroupInt виконувались:

```text
Get messages from group
Extract endorsements from messages
```

Результат первинного графа:

```text
70 Group nodes
68 directed ENDORSES edges
```

## Етап 6 — Neo4j → Gephi

Public Bolt через browser / direct URI мав проблеми з discovery/TLS.

Рішення:

```powershell
ssh -L 17687:localhost:17687 hostinger-vps
```

У Gephi:

```text
Neo4j plugin
URL: neo4j://localhost:17687
Auth: neo4j + password з D:\servers\.env
Labels: Group
Relationships: ENDORSES
```

Створено Gephi-проєкти:

| Файл | Призначення |
|---|---|
| `screenshots/telegram-endorsements-republic-of-gagauzia.gephi` | первинний граф |
| `screenshots/telegram-endorsements-expanded.gephi` | розширений граф |
| `screenshots/telegram-endorsements-expanded-gephi-ai.gephi` | граф після gephi-ai |

## Етап 7 — Gephi аналіз

У Gephi виконано:

- layout;
- modularity / community detection;
- degree / weighted degree;
- PageRank;
- betweenness centrality;
- Data Laboratory export.

Ключові результати:

| Метрика | Значення |
|---|---:|
| Вузли | 70 |
| Ребра | 68 |
| Основні кластери в CSV | 3 |
| Кластери після Gephi re-computation | 4 |
| Найбільший weighted degree | `Republic_Of_GaGauZia` — 3404 |
| Betweenness | 0.0 для всіх вузлів |

Основні screenshots:

| Файл | Що показує |
|---|---|
| `13-gephi-expanded-modularity-70nodes.png` | modularity clusters |
| `14-gephi-expanded-degree-70nodes.png` | degree / centrality |
| `15-gephi-data-lab-top-weighted-degree.png` | топ вузлів |
| `16-gephi-data-lab-top-endorsement-edges.png` | топ ребер |

## Етап 8 — gephi-ai + Claude Code

Підготовлено локально:

```text
D:\projects\gephi-ai
D:\projects\gephi-ai\.venv
```

Проблеми й рішення:

| Проблема | Рішення |
|---|---|
| Java 25 ламав Maven jar packaging | використано Gephi bundled Java 17 для build |
| Python 3.14 PEP 668 | створено venv `D:\projects\gephi-ai\.venv` |
| `pyproject.toml` gephi-ai mcp-server мав проблему dependencies | виправлено локально |
| Gephi MCP `/health` не відповідав | встановлено `.nbm` plugin у Gephi і перезапущено |

Підтверджено:

```text
http://127.0.0.1:8080/health
success: true
service: Gephi MCP API
version: 2.0.0
```

Claude MCP:

```text
gephi-mcp: Connected
```

Створено:

| Файл | Призначення |
|---|---|
| `scripts/gephi_mcp_run.py` | відтворення Gephi MCP analysis |
| `data/gephi_ai_summary.md` | summary для звіту |
| `screenshots/17-gephi-ai-analysis-export.png` | фінальний gephi-ai PNG |

## Етап 9 — первинний звіт і GitHub push

Створено фінальний звіт:

```text
AI_OSINT_HW_Clustering_PatternMatching_Nestor-V.md
```

Створено README за стандартом репозиторію:

```text
README.md
```

Оновлено:

```text
D:\projects\osint-homework-2026\README.md
D:\projects\osint-homework-2026\STRUCTURE.md
```

Перший GitHub commit:

```text
7b88b8a Add DZ-12 Telegram graph analysis
```

## Етап 10 — аудит вимог викладача

Після першого push проведено жорстку перевірку вимог.

Виявлені прогалини:

| Вимога | Прогалина |
|---|---|
| очищення дублікатів / шуму | було лише описано як обмеження |
| однакові / схожі формулювання | не було текстового аналізу |
| синхронні публікації | не було timestamp/text layer |
| повторювані наративи | не було narrative layer |
| джерела / ретранслятори | не було окремої role table |
| Gephi vs Neo4j | не було окремого comparison |
| гіпотеза про координацію | не була оформлена |

Створено:

```text
GAP_FIX_STATE.md
```

## Етап 11 — експорт Message nodes з Neo4j

Потрібний файл:

```text
data/raw/groupint_messages.csv
```

Перший export через `cypher-shell` був некоректний: тексти містили лапки й переноси, CSV ламався.

Фінальне рішення:

- експорт через Python `csv` всередині `groupint-streamlit`;
- підключення до Neo4j через Python driver;
- один рядок = один `Message`.

Результат:

| Показник | Значення |
|---|---:|
| Унікальні повідомлення | 15100 |
| Повідомлення з непорожнім текстом | 11781 |
| Колонки | `message_id`, `group_id`, `group_title`, `date`, `text`, `telegram_url`, `group_telegram_url` |

## Етап 12 — очищення дублікатів і шуму

Створено скрипт:

```text
scripts/clean_graph_data.py
```

Створено артефакти:

| Файл | Результат |
|---|---|
| `data/processed/nodes_clean.csv` | 60 вузлів |
| `data/processed/edges_endorsements_clean.csv` | 58 ребер |
| `data/processed/deduplication_notes.md` | протокол очищення |

Консервативно злиті лише очевидні typo-alias:

- варіанти `MoldovaPolitics`;
- `primulinm` -> `primulinmd`.

Важливе виправлення: автоматичний fuzzy merge помилково зливав `Republic_Of_GaGauZia` і `Republic_Of_GaGauzia_MD`; це було скасовано.

## Етап 13 — ролі каналів

Створено скрипт:

```text
scripts/classify_channel_roles.py
```

Створено:

```text
data/processed/channel_roles.csv
```

Ролі:

| Канал | Роль |
|---|---|
| `Republic_Of_GaGauZia` | `retransmitter;amplifier` |
| `Republic_Of_GaGauzia_MD` | `primary_source_candidate;amplifier` |
| `MoldovaAdevarata` | `primary_source_candidate;amplifier` |
| `MoldovaPolitics` | `retransmitter;amplifier` |

Обмеження: `primary_source_candidate` не означає доведене первинне авторство.

## Етап 14 — text pattern matching, синхронність і наративи

Створено скрипт:

```text
scripts/analyze_text_patterns.py
```

Перший запуск мав методологічну помилку:

```text
508 synchronized windows
```

Причина: порожній текст рахувався як однаковий hash.

Виправлення:

- синхронність рахується тільки для текстів з normalized length >= 40;
- один pattern = один window між каналами;
- додано `first_seen_at`, `first_seen_group`;
- додано narrative keyword tags.

Фінальний результат:

| Файл | Результат |
|---|---:|
| `data/processed/text_patterns.csv` | 9 repeated text patterns |
| `data/processed/synchronized_posts.csv` | 4 валідні sync windows |
| `data/processed/narrative_patterns.csv` | 10 narrative-tag matches |
| `data/processed/narrative_summary.md` | narrative summary |
| `data/processed/pattern_examples.md` | приклади текстових тез |

Повторювані narrative tags:

- `gagauz_identity_history`;
- `anti_sandu_governance`;
- `anti_west_eu`;
- `transnistria_russia_protection`;
- `russian_language_identity`;
- `russian_citizenship`.

## Етап 15 — Gephi vs Neo4j і гіпотеза про координацію

Створено:

| Файл | Призначення |
|---|---|
| `data/processed/gephi_neo4j_comparison.md` | comparison Neo4j vs Gephi |
| `data/processed/coordination_hypothesis.md` | обережна гіпотеза |

Гіпотеза сформульована як:

> Є ознаки можливої координації або спільного джерела контенту, але це не доведення координації.

Альтернативні пояснення також зафіксовані:

- копіювання з одного відкритого джерела;
- repost / quote blocks;
- обмежені metadata GroupInt;
- синхронність як індикатор, не доказ.

## Етап 16 — оновлення фінального звіту

Фінальний звіт оновлено:

```text
AI_OSINT_HW_Clustering_PatternMatching_Nestor-V.md
```

Додано розділи:

- очищення дублікатів і шуму;
- однакові формулювання / тези;
- синхронні публікації;
- повторювані наративи;
- ролі каналів;
- порівняння Gephi та Neo4j;
- гіпотеза про координацію;
- оновлена відтворюваність.

## 4. Остаточна перевірка вимог

| Вимога викладача | Статус |
|---|---:|
| GroupInt для збору даних | виконано |
| використати seed-канали | виконано |
| зібрати публікації | виконано |
| зібрати згадки / посилання | виконано |
| зберегти CSV | виконано |
| вузли / ребра | виконано |
| очистити дублікати / шум | виконано |
| Gephi / Neo4j граф | виконано |
| degree / weighted degree | виконано |
| betweenness | виконано |
| modularity | виконано |
| кластери | виконано |
| топ-10 впливових каналів | виконано |
| однакові / схожі формулювання | виконано |
| синхронні публікації | виконано |
| повторювані посилання | виконано |
| систематичне цитування джерела | виконано |
| повторювані наративи | виконано |
| ролі: джерела / ретранслятори / мости / підсилювачі | виконано з чесними обмеженнями |
| Gephi vs Neo4j comparison | виконано |
| гіпотеза про координацію | виконано |
| відтворюваність | виконано |

## 5. Чесні обмеження

1. `primary_source_candidate` не є доведеним первинним авторством.
2. Betweenness не знайшов формальних bridge-вузлів: усі значення 0.0.
3. Координація не доведена, лише сформульована гіпотеза.
4. Neo4j GDS не запускався; порівняння Neo4j/Gephi є workflow/data comparison, а не algorithm benchmark.
5. Аналіз наративів базується на keyword tags для повторюваних текстів, не на повній NLP-класифікації всіх 15100 повідомлень.

## 6. Поточний Git-стан після доробок

Після першого GitHub push нові файли ще потрібно окремо закомітити й запушити:

- `GAP_FIX_STATE.md`;
- `data/raw/groupint_messages.csv`;
- `data/processed/*`;
- `scripts/clean_graph_data.py`;
- `scripts/classify_channel_roles.py`;
- `scripts/analyze_text_patterns.py`;
- оновлений `AI_OSINT_HW_Clustering_PatternMatching_Nestor-V.md`.

Також є modified `.gephi` файл:

```text
screenshots/telegram-endorsements-expanded-gephi-ai.gephi
```

Його треба або включити свідомо, або не чіпати.
