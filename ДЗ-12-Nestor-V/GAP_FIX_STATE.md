# ДЗ-12 — поточний стан і план закриття недоліків

Дата фіксації: 2026-05-26

Цей файл фіксує стан після первинної здачі ДЗ-12 і перелік вимог викладача, які ще треба закрити без вигадування результатів.

## 1. Поточний стан

Опублікований GitHub commit:

```text
7b88b8a Add DZ-12 Telegram graph analysis
```

Папка ДЗ:

```text
D:\projects\osint-homework-2026\ДЗ-12-Nestor-V
```

Основний звіт:

```text
AI_OSINT_HW_Clustering_PatternMatching_Nestor-V.md
```

Наявні структуровані дані:

| Файл | Стан | Що містить |
|---|---:|---|
| `data/nodes_with_communities.csv` | є | 70 вузлів `Group`, Gephi metrics, communities |
| `data/edges_endorsements.csv` | є | 68 directed `ENDORSES` ребер, weight, raw link, message id |
| `data/gephi_ai_summary.md` | є | підсумок Gephi MCP / gephi-ai |

Наявні графові артефакти:

| Файл | Стан |
|---|---:|
| `screenshots/13-gephi-expanded-modularity-70nodes.png` | є |
| `screenshots/14-gephi-expanded-degree-70nodes.png` | є |
| `screenshots/15-gephi-data-lab-top-weighted-degree.png` | є |
| `screenshots/16-gephi-data-lab-top-endorsement-edges.png` | є |
| `screenshots/17-gephi-ai-analysis-export.png` | є |
| `screenshots/telegram-endorsements-expanded-gephi-ai.gephi` | є |

## 2. Що вже закрито

| Вимога | Статус | Підстава |
|---|---:|---|
| GroupInt для збору даних | виконано | скріншоти GroupInt, опис методології |
| Neo4j / Gephi граф | виконано | `.gephi`, Gephi screenshots |
| degree / weighted degree | виконано | `nodes_with_communities.csv` |
| PageRank | виконано додатково | `nodes_with_communities.csv`, `gephi_ai_summary.md` |
| betweenness centrality | виконано | значення 0.0 для всіх вузлів |
| modularity / community detection | виконано | 3 класи в CSV, 4 після Gephi re-computation |
| топ-10 впливових каналів | виконано | секція 5 звіту |
| повторювані посилання | виконано | `edges_endorsements.csv`, секція Pattern matching |

## 3. Незакриті або частково закриті вимоги

| Вимога | Поточний статус | Чому не закрито |
|---|---:|---|
| Очистити дублікати / технічний шум | частково | у звіті лише вказано, що є дублікати типу `MoldovaPolitics`; нормалізація не виконана |
| Однакові або схожі формулювання | не виконано | у репозиторії немає текстів повідомлень |
| Синхронні публікації | не виконано | немає таблиці з timestamps + текстом повідомлень |
| Поширення однакових наративів | не виконано | немає NLP/text pattern layer |
| Джерела первинного поширення | частково | hub-и описані, але не класифіковані окремою таблицею ролей |
| Ретранслятори | частково | частина ролей є в топ-10, але немає окремої системної класифікації |
| Порівняти Gephi та Neo4j | частково | workflow описано, але немає окремої таблиці порівняння counts/metrics/обмежень |
| Гіпотеза про координацію | частково | є обережний висновок про hub-and-spoke, але немає окремо сформульованої гіпотези |

## 4. Ключовий блокер

Для тез, схожих формулювань, синхронності й наративів потрібен експорт повідомлень з Neo4j / GroupInt у структурованому форматі:

```text
data/raw/groupint_messages.csv
```

Мінімальні поля:

| Поле | Для чого |
|---|---|
| `message_id` | стабільний ідентифікатор |
| `group_id` або `channel_id` | канал / джерело |
| `group_title` або `channel_title` | читабельна назва |
| `date` / `created_at` | часовий аналіз і синхронність |
| `text` | тези, формулювання, NLP |
| `forward_from` / `reply_to` / `source` якщо є | пересилання і первинні джерела |
| `urls` / `links` якщо є | repeated links / narrative indicators |

Без цього файлу чесно виконати вимоги про "схожі формулювання", "синхронні публікації" і "наративи" неможливо.

## 5. План виправлень

### Крок 1 — експорт повідомлень з Neo4j

Створити `data/raw/groupint_messages.csv` з текстами й timestamps. Якщо Neo4j schema відрізняється, спочатку виконати read-only schema discovery:

```cypher
CALL db.labels();
CALL db.relationshipTypes();
MATCH (m:Message) RETURN keys(m) LIMIT 5;
MATCH (g:Group) RETURN keys(g) LIMIT 5;
```

Після discovery сформувати CSV export.

### Крок 2 — очищення дублікатів / шуму

Вихідні файли:

```text
data/processed/nodes_clean.csv
data/processed/edges_endorsements_clean.csv
data/processed/deduplication_notes.md
```

Що зробити:

- нормалізувати `group_id`, `group_username`, `group_telegram_url`;
- звести obvious duplicates, наприклад варіанти `MoldovaPolitics`;
- прибрати технічні bot/CTA вузли в окрему категорію, не видаляючи їх без пояснення;
- зафіксувати правила очищення.

### Крок 3 — текстовий pattern matching

Вихідні файли:

```text
data/processed/text_patterns.csv
data/processed/pattern_examples.md
```

Що знайти:

- exact duplicate texts;
- near-duplicate texts;
- однакові URL / domains;
- повторювані короткі тези;
- повторювані entity/narrative markers.

### Крок 4 — синхронні публікації

Вихідні файли:

```text
data/processed/synchronized_posts.csv
screenshots/18-narrative-timeline.png
```

Метод:

- групувати однакові або схожі повідомлення у часових вікнах 5, 15, 30, 60 хвилин;
- рахувати кількість каналів у кожному вікні;
- не називати це координацією автоматично, лише "ознака можливої синхронізації".

### Крок 5 — ролі каналів

Вихідний файл:

```text
data/processed/channel_roles.csv
```

Ролі:

| Роль | Операційне правило |
|---|---|
| `primary_source_candidate` | ранній timestamp для повторюваної тези / багато incoming citations |
| `retransmitter` | багато outgoing endorsements / повторює чужі links |
| `bridge` | betweenness > 0 або семантичний зв'язок між кластерами |
| `amplifier` | висока weighted degree / багато повторів одного link/narrative |
| `peripheral` | низький degree, отримувач або одиничний link |

### Крок 6 — Gephi vs Neo4j comparison

Вихідний файл:

```text
data/processed/gephi_neo4j_comparison.md
```

Порівняти:

- node count;
- edge count;
- labels / relationship types;
- що рахується в Neo4j;
- що рахується в Gephi;
- чому Gephi re-computation дав 4 community classes, а CSV мав 3.

### Крок 7 — гіпотеза про координацію

Додати у звіт окремий розділ:

```text
## Гіпотеза про координацію
```

Вимога до формулювання:

- тільки як гіпотеза, не як доведений факт;
- спиратися на повторювані links, синхронність, ролі каналів;
- окремо вказати альтернативне пояснення: редакційна схожість, автоматичні repost/CTA, особливість парсингу GroupInt.

## 6. Definition of Done для виправлення

- [ ] `data/raw/groupint_messages.csv` створено або чесно зафіксовано, що повідомлення недоступні.
- [ ] `data/processed/nodes_clean.csv` створено.
- [ ] `data/processed/edges_endorsements_clean.csv` створено.
- [ ] `data/processed/deduplication_notes.md` створено.
- [ ] `data/processed/text_patterns.csv` створено.
- [ ] `data/processed/pattern_examples.md` створено.
- [ ] `data/processed/synchronized_posts.csv` створено або зафіксовано, що синхронність неможлива без timestamps.
- [ ] `data/processed/channel_roles.csv` створено.
- [ ] `data/processed/gephi_neo4j_comparison.md` створено.
- [ ] Звіт оновлено без вигаданих тез.
- [ ] README оновлено після виправлень.
