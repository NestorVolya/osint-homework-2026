# ДЗ-12: план виконання

**Тема:** кластеризація Telegram-груп та візуалізація графів
**Фокус:** проросійські інформаційні мережі, впливові канали, кластери, pattern matching
**Формат здачі:** `AI_OSINT_HW_Clustering_PatternMatching_Nestor-V.md` + дані + скриншоти графів
**Робоча папка:** `D:\projects\osint-homework-2026\ДЗ-12-Nestor-V`

---

## 0. Межі та безпека

- Працювати тільки з відкритими або наданими викладачем групами/каналами.
- Не публікувати `api_id`, `api_hash`, Telegram session files, номери телефонів, OTP.
- У звіті не цитувати персональні дані приватних користувачів без потреби.
- Для графа пріоритетно аналізувати канали/групи/джерела, а не приватних учасників.
- Всі сирі дані зберігати локально; у git додавати тільки очищені/санітизовані файли.

---

## 1. Цільовий результат

Підготувати короткий OSINT-звіт на 3-5 сторінок у Markdown:

- опис задачі, початкового списку каналів і періоду аналізу;
- методологія збору через GroupInt;
- схема вузлів і ребер;
- графова візуалізація Gephi або Neo4j;
- 2-5 кластерів з поясненням;
- топ-10 впливових або цитованих каналів;
- мінімум 3 приклади pattern matching;
- висновок, заснований на графових метриках.

---

## 2. Структура папки

```text
ДЗ-12-Nestor-V/
├── README.md
├── PLAN.md
├── PLAN.html
├── ENVIRONMENT_PLAN.md
├── LESSON12_CHECKLIST.html
├── SCREENSHOTS.md
├── SCREENSHOTS.html
├── AI_OSINT_HW_Clustering_PatternMatching_Nestor-V.md
├── methodology.md
├── reproduce.md
├── scripts/
│   ├── export_groupint.py
│   ├── build_edges.py
│   ├── compute_metrics.py
│   └── pattern_matching.py
├── data/
│   ├── input_channels.csv
│   ├── raw/
│   │   ├── groupint_messages.csv
│   │   ├── groupint_groups.csv
│   │   └── groupint_relationships.csv
│   └── processed/
│       ├── nodes.csv
│       ├── edges.csv
│       ├── top10_influence.csv
│       ├── clusters.csv
│       ├── patterns.csv
│       └── telegram_network.gexf
└── screenshots/
    ├── groupint-scrape.png
    ├── gephi-overview.png
    ├── gephi-modularity.png
    ├── gephi-centrality.png
    └── neo4j-browser-optional.png
```

---

## 3. Дані та період

### 3.1 Початковий список

Створити `data/input_channels.csv`:

| Поле | Значення |
|---|---|
| `seed_id` | короткий id рядка |
| `input` | `@username` або `https://t.me/...` |
| `type_hint` | `channel` / `group` / `unknown` |
| `source` | `teacher_list` |
| `notes` | опційно |

### 3.2 Період аналізу

Базовий варіант: останні 30-90 днів або період, який дозволить GroupInt без перевантаження.

У звіті явно зафіксувати:

- дату запуску збору;
- часовий діапазон повідомлень;
- кількість seed-каналів;
- кількість фактично зібраних каналів/груп;
- кількість повідомлень;
- обмеження доступу: приватні групи, заблоковані канали, недоступні історії.

---

## 4. Збір через GroupInt

### 4.1 Підготовка

1. Клонувати GroupInt:

```bash
git clone https://github.com/OSINT-for-Ukraine/groupint.git
cd groupint
```

2. Створити `.streamlit/secrets.toml`:

```toml
[telegram]
phone = "+XXXXXXXXXXX"
api_id = "12345678"
api_hash = "your_api_hash_here"
```

3. Запустити Desktop stack:

```bash
./scripts/up-desktop.sh
```

4. Перевірити:

| Сервіс | URL |
|---|---|
| GroupInt | `http://localhost:18501` |
| Neo4j Browser | `http://localhost:17474` |
| Bolt для Gephi | `bolt://localhost:17687` |

### 4.2 Scrape workflow

Для кожного seed-каналу:

1. Resolve target group/channel у GroupInt.
2. `Get messages from group`.
3. `Extract users from stored messages`.
4. `Extract endorsements`, якщо доступно.
5. Зафіксувати canonical id.
6. Зробити скриншот успішного збору для 1-2 каналів.

### 4.3 Контроль якості

Neo4j перевірки:

```cypher
MATCH (g:Group) RETURN g.id, g.title, g.user_counts LIMIT 20;
MATCH (m:Message) RETURN count(m);
MATCH ()-[r]->() RETURN type(r), count(r) ORDER BY count(r) DESC;
```

Мінімальний pass:

- є вузли `Group`;
- є повідомлення або інші зібрані об'єкти;
- є ребра між групами/каналами або користувачами/групами;
- є дані для імпорту в Gephi.

---

## 5. Модель графа

### 5.1 Вузли

Основний граф для звіту:

| Тип вузла | Опис | Чому використовується |
|---|---|---|
| `Channel/Group` | Telegram-канали та групи | головний об'єкт кластеризації |
| `SourceDomain` | домени з URL у повідомленнях | виявлення спільних джерел |
| `Narrative/Pattern` | повторювані тези або схожі тексти | pattern matching |

Опційно:

| Тип вузла | Умова |
|---|---|
| `User/Author` | тільки якщо це публічні адміністратори/автори або потрібно для GroupInt-графа |
| `Message` | тільки для малого графа або окремого pattern graph |

### 5.2 Ребра

| Тип ребра | Напрямок | Вага |
|---|---|---|
| `FORWARDS_FROM` | канал -> джерело пересилання | кількість пересилань |
| `MENTIONS` | канал -> згаданий канал | кількість згадок |
| `LINKS_TO` | канал -> домен або URL | кількість посилань |
| `ENDORSES` | канал -> канал | GroupInt endorsement |
| `SHARES_PATTERN` | канал -> pattern або канал -> канал | кількість схожих тез |

Базовий граф для Gephi: `Channel/Group` nodes + `ENDORSES`, `MENTIONS`, `FORWARDS_FROM`, `LINKS_TO` as weighted edges.

---

## 6. Обробка даних

### 6.1 Очистка

- нормалізувати Telegram handles: `@name`, `https://t.me/name`, `t.me/name` -> `name`;
- злити дублікати group id / username / title;
- прибрати технічні URL: `t.me/c/...`, tracking params, короткі службові посилання;
- домени привести до lowercase без `www.`;
- залишити лише ребра з вагою >= 1, а для шумних типів можна threshold >= 2;
- окремо зберегти список відкинутих технічних вузлів.

### 6.2 Експорт

Підготувати:

- `data/processed/nodes.csv`;
- `data/processed/edges.csv`;
- `data/processed/telegram_network.gexf`;
- `data/processed/top10_influence.csv`;
- `data/processed/clusters.csv`;
- `data/processed/patterns.csv`.

Рекомендовані поля `nodes.csv`:

```csv
id,label,type,cluster,degree,weighted_degree,betweenness,pagerank,role,notes
```

Рекомендовані поля `edges.csv`:

```csv
source,target,type,weight,first_seen,last_seen,evidence_count
```

---

## 7. Gephi / Neo4j workflow

### 7.1 Gephi

1. Import Spreadsheet або Neo4j plugin.
2. Імпорт `nodes.csv` і `edges.csv` або напряму з Neo4j.
3. Statistics:
   - Average Degree;
   - Network Diameter / Betweenness Centrality;
   - Modularity;
   - PageRank, якщо доступно.
4. Appearance:
   - color = `modularity_class`;
   - node size = weighted degree або PageRank;
   - label size = degree/PageRank;
   - edge thickness = weight.
5. Layout:
   - ForceAtlas 2;
   - Prevent overlap;
   - Label adjust.
6. Export:
   - PNG overview;
   - PNG top cluster zoom;
   - Gephi project `.gephi`;
   - GEXF/GraphML для відтворення.

### 7.2 Neo4j опційно

Залишити Neo4j як джерело перевірки і для Cypher-запитів:

```cypher
MATCH (a)-[r]->(b)
RETURN labels(a), type(r), labels(b), count(*) AS c
ORDER BY c DESC;
```

Якщо є час, побудувати окремий Neo4j Browser screenshot з центральними каналами.

---

## 8. Метрики і ролі каналів

### 8.1 Топ-10

Таблиця у звіті:

| Канал | Кластер | Основна роль | Показник впливовості | Коментар |
|---|---|---|---|---|
| `@...` | C1 | Джерело / ретранслятор / міст / підсилювач | PageRank / Degree / Betweenness | Чому важливий |

### 8.2 Інтерпретація ролей

| Роль | Критерій |
|---|---|
| Джерело первинного поширення | багато вихідних цитувань/пересилань з інших каналів на нього; ранні timestamp для наративу |
| Ретранслятор | багато outgoing forwards/mentions; поширює чужі повідомлення |
| Міст | високий betweenness між кластерами |
| Підсилювач | висока активність і weighted degree, але не обов'язково первинне джерело |

---

## 9. Pattern matching

Мінімум 3 приклади:

1. Однакове або майже однакове формулювання у 2+ каналах.
2. Синхронні публікації в короткому часовому вікні.
3. Повторення однакового URL/домена або джерела.

### 9.1 Базовий метод

- нормалізувати текст: lowercase, прибрати URL, punctuation, зайві пробіли;
- exact match для коротких повторів;
- fuzzy similarity для схожих тез;
- окремо рахувати повтор URL/domain;
- для синхронності: групувати подібні повідомлення в інтервалі 5-60 хвилин.

### 9.2 Поля `patterns.csv`

```csv
pattern_id,type,summary,channels,first_seen,last_seen,count,evidence_refs,comment
```

Типи:

- `same_text`;
- `similar_text`;
- `same_url`;
- `same_domain`;
- `synchronized_posting`;
- `repeated_narrative`.

---

## 10. Структура фінального звіту

Файл: `AI_OSINT_HW_Clustering_PatternMatching_Nestor-V.md`

```markdown
# AI_OSINT_HW_Clustering_PatternMatching_Nestor-V

## 1. Короткий опис задачі

## 2. Методологія

## 3. Дані та модель графа

## 4. Графова візуалізація

## 5. Основні кластери

## 6. Найбільш впливові канали

## 7. Pattern matching

## 8. Висновки

## 9. Відтворення аналізу

## 10. Обмеження
```

---

## 11. Acceptance Criteria

### Базовий рівень

- [ ] Використано GroupInt для збору даних.
- [ ] Збережено сирі результати у структурованому форматі.
- [ ] Побудовано `nodes.csv` і `edges.csv`.
- [ ] Зафіксовано типи вузлів і ребер.
- [ ] Побудовано граф у Gephi або Neo4j.
- [ ] Додано хоча б один скриншот графа.
- [ ] Пораховано degree / weighted degree.
- [ ] Пораховано betweenness centrality.
- [ ] Пораховано modularity / community detection.
- [ ] Описано мінімум 2 кластери.
- [ ] Складено топ-10 впливових або цитованих каналів.
- [ ] Додано мінімум 3 приклади pattern matching.
- [ ] Висновок спирається на графові метрики.
- [ ] Додано короткий опис відтворення аналізу.

### Просунутий рівень

- [ ] Порівняно Gephi та Neo4j або NetworkX-метрики.
- [ ] Окремо виділено bridge-канали за betweenness.
- [ ] Побудовано окремий граф для пересилань або згадок.
- [ ] Додано часовий аналіз поширення одного наративу.
- [ ] Використано NLP/fuzzy matching для схожих текстів.
- [ ] Сформульовано обережну гіпотезу про координацію.

---

## 12. Послідовність виконання

| Крок | Дія | Артефакт | Gate |
|---|---|---|---|
| 1 | Створити seed list | `data/input_channels.csv` | всі канали з викладацького списку внесені |
| 2 | Підняти GroupInt | screenshot / notes | Streamlit і Neo4j доступні |
| 3 | Авторизувати Telegram | локальна session | OTP пройдений, session не комітиться |
| 4 | Зібрати дані | `data/raw/*` | є Group/Message/relationship дані |
| 5 | Очистити і нормалізувати | `data/processed/*` | дублікати і шум прибрані |
| 6 | Побудувати граф | `.gexf`, `.gephi` | граф має >0 вузлів і ребер |
| 7 | Порахувати метрики | `top10_influence.csv`, `clusters.csv` | є degree, betweenness, modularity |
| 8 | Pattern matching | `patterns.csv` | є мінімум 3 доказові приклади |
| 9 | Написати звіт | final `.md` | структура відповідає ДЗ |
| 10 | Самоперевірка | README checklist | всі мінімальні вимоги закриті |

---

## 13. Ризики

| Ризик | Вплив | Мітигація |
|---|---|---|
| Telegram акаунт заблокований або OTP недоступний | немає збору | використати власний дозволений акаунт або новий номер; не автоматизувати агресивно |
| Частина каналів приватна | неповний граф | явно описати coverage і missing data |
| GroupInt збирає мало endorsement edges | слабкий граф канал-канал | додати edges з mentions, forwards, links |
| Забагато Message/User вузлів | Gephi зависає | імпортувати тільки channel-level graph |
| Pattern matching дає шум | хибні висновки | показувати тільки приклади з evidence і ручною перевіркою |
| Впливовість плутається з активністю | неправильні ролі | розділяти degree/PageRank/betweenness і пояснювати роль окремо |

---

## 14. Рекомендований мінімальний шлях

1. Зібрати через GroupInt повідомлення та endorsements для seed-каналів.
2. Зробити channel-level граф: канал -> канал / домен / згадка.
3. У Gephi порахувати modularity, degree, betweenness.
4. Описати 2-3 найбільші кластери.
5. Зробити топ-10 за комбінованою логікою: PageRank або weighted degree + betweenness.
6. Додати 3 pattern examples з конкретними timestamp/channel evidence.
7. Не перевантажувати звіт сирими повідомленнями; основа оцінки - граф, метрики, відтворюваність.
