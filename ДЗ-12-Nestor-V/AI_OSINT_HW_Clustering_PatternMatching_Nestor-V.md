# AI_OSINT_HW_Clustering_PatternMatching_Nestor-V

## 1. Короткий опис задачі

Мета роботи - дослідити Telegram-мережу проросійських або пов'язаних регіональних інформаційних каналів через GroupInt, Neo4j та Gephi. Основний фокус аналізу: зв'язки між каналами через `t.me` посилання, повторювані endorsement-зв'язки, кластери та найбільш впливові вузли.

Початкові seed-канали:

| Seed | Коментар |
|---|---|
| `Republic_Of_GaGauZia` | головний seed, дав найбільше endorsement-зв'язків |
| `pridnestrovec` | канал із великою кількістю повідомлень, але майже без endorsement-зв'язків |
| `gagauznewsmd` | додатковий регіональний seed |
| `MoldovaPolitics` | seed із помітним окремим набором посилань |

Період збору: дані збирались через GroupInt 25-26 травня 2026 року. Для кожного seed-каналу завантажувались останні 1000-3000 повідомлень залежно від етапу збору.

## 2. Методологія

Збір даних виконано через GroupInt, розгорнутий на VPS у Docker. Telegram-сесія була створена через OTP і збережена як server-side session. Neo4j використовувався як сховище графових даних.

Через те, що основні об'єкти є Telegram-каналами, список учасників та авторів повідомлень був недоступний або нерелевантний. Тому основна графова модель побудована на зв'язках `ENDORSES`, які GroupInt формує з `t.me` посилань і згадок у повідомленнях.

Використані типи вузлів:

| Тип вузла | Опис |
|---|---|
| `Group` | Telegram-канал або група |

Використані типи ребер:

| Тип ребра | Опис |
|---|---|
| `ENDORSES` | посилання або згадка одного Telegram-ресурсу в повідомленнях іншого |

Інструменти:

| Інструмент | Роль |
|---|---|
| GroupInt | збір повідомлень і витягнення `ENDORSES` |
| Neo4j | зберігання вузлів і ребер |
| Gephi | імпорт графа, layout, modularity, degree/PageRank аналіз |

## 3. Графова візуалізація

Граф імпортовано в Gephi через Neo4j plugin. Для підключення використовувався SSH tunnel до Neo4j Bolt:

```text
neo4j://localhost:17687
```

Імпортовані дані:

| Labels | Relationships |
|---|---|
| `Group` | `ENDORSES` |

Після імпорту в Gephi отримано:

| Показник | Значення |
|---|---:|
| Вузли | 70 |
| Основні community classes | 3 |

Візуалізація:

- колір вузла: `Modularity Class`;
- розмір/насиченість вузла: `Degree` або `Weighted Degree`;
- layout: ForceAtlas 2;
- додаткові таблиці: Data Laboratory top weighted degree, top endorsement edges.

Скріншоти:

| Файл | Що показує |
|---|---|
| `screenshots/13-gephi-expanded-modularity-70nodes.png` | кластери за modularity |
| `screenshots/14-gephi-expanded-degree-70nodes.png` | центральність / впливовість вузлів |
| `screenshots/15-gephi-data-lab-top-weighted-degree.png` | топ вузлів за weighted degree |
| `screenshots/16-gephi-data-lab-top-endorsement-edges.png` | топ endorsement-ребер |

Експортовані таблиці:

| Файл | Опис |
|---|---|
| `data/nodes_with_communities.csv` | вузли з community class, degree, weighted degree, PageRank |
| `data/edges_endorsements.csv` | ребра `ENDORSES` з вагою, raw link і message id |

## 4. Основні кластери

За `modularity_class` виявлено 3 кластери:

| Кластер | Кількість вузлів | Ключові вузли | Інтерпретація |
|---:|---:|---|---|
| 0 | 38 | `Republic_Of_GaGauZia`, `Republic_Of_GaGauzia_MD`, `MoldovaAdevarata` | найбільший endorsement-кластер навколо Gagauzia-сегмента |
| 2 | 26 | `MoldovaPolitics`, `gagauznewsmd`, `primulinmd`, `wtfmoldova`, `turan_express` | другий інформаційний сегмент із молдовськими/регіональними каналами |
| 1 | 6 | `pridnestrovec` та кілька слабко пов'язаних вузлів | малий периферійний кластер |

Граф має hub-and-spoke структуру: кілька seed-каналів створюють більшість вихідних endorsement-зв'язків, а багато інших вузлів є периферійними отримувачами посилань.

## 5. Найбільш впливові канали

Основним показником впливовості для цієї роботи обрано `weighted degree`, бо він враховує повторюваність endorsement-зв'язків, а не лише факт наявності одного ребра.

| Канал | Кластер | Основна роль | Показник впливовості | Коментар |
|---|---:|---|---:|---|
| `Republic_Of_GaGauZia` | 0 | hub / джерело посилань | weighted degree 3404 | головний центр графа, формує більшість ваги |
| `Republic_Of_GaGauzia_MD` | 0 | цитований ресурс | weighted degree 3235 | найсильніше пов'язаний із головним hub |
| `MoldovaAdevarata` | 0 | цитований ресурс | weighted degree 87 | помітний повторюваний endorsement |
| `MoldovaPolitics` | 2 | hub / ретранслятор | degree 20, weighted degree 66 | центр другого кластера |
| `primulinmd` | 2 | локальний вузол | weighted degree 14 | помітний вузол у другому кластері |
| `gagauznewsmd` | 2 | seed / локальний ретранслятор | degree 5, weighted degree 12 | додатковий Gagauzia-сегмент |
| `wtfmoldova` | 2 | цитований ресурс | weighted degree 11 | частий отримувач посилань |
| `turan_express` | 2 | цитований ресурс | weighted degree 9 | частий отримувач посилань |
| `contractMObot` | 0 | технічний/CTA-вузол | weighted degree 9 | імовірно службовий або call-to-action ресурс |
| `gagayzineodinoki` | 0 | периферійний ресурс | weighted degree 8 | повторюваний периферійний вузол |

## 6. Pattern matching

### Патерн 1: домінантне систематичне посилання

Найсильніший зв'язок:

```text
Republic_Of_GaGauZia -> Republic_Of_GaGauzia_MD
weight: 3235
raw link: @Republic_Of_GaGauzia_MD
message id: 71800
```

Це свідчить про систематичне повторення одного й того самого Telegram-посилання або регулярне взаємне підсилення між пов'язаними ресурсами.

### Патерн 2: повторюване цитування медійного/політичного ресурсу

Помітний зв'язок:

```text
Republic_Of_GaGauZia -> MoldovaAdevarata
weight: 87
raw link: @MoldovaAdevarata
message id: 71690
```

Це другий за силою endorsement-зв'язок у кластері 0 після головної пари `Republic_Of_GaGauZia` / `Republic_Of_GaGauzia_MD`.

### Патерн 3: окремий MoldovaPolitics-сегмент

У кластері 2 зафіксовані повторювані посилання:

```text
MoldovaPolitics -> primulinmd, weight 11, raw link @primulinmd
MoldovaPolitics -> wtfmoldova, weight 11, raw link @wtfmoldova
MoldovaPolitics -> turan_express, weight 9, raw link @turan_express
```

Ваги цих зв'язків нижчі, ніж у головному Gagauzia-кластері, але вони формують окремий інформаційний сегмент.

## 7. Висновки

Мережа не є рівномірною. Вона має кілька центрів ретрансляції та багато периферійних вузлів. Найсильніший вузол - `Republic_Of_GaGauZia`, який формує найбільшу кількість і вагу endorsement-зв'язків.

`MoldovaPolitics` утворює другий, менший кластер. `pridnestrovec` має значний обсяг повідомлень, але в межах endorsement-графа майже не створює посилань на інші Telegram-ресурси, тому виглядає слабко пов'язаним у цій моделі.

З точки зору інформаційної операції або пропагандистської екосистеми, граф показує не одну щільну мережу, а структуру з окремими центрами підсилення. Найважливіші вузли визначаються не лише кількістю повідомлень, а саме вагою повторюваних посилань на інші ресурси.

## 8. Відтворення аналізу

1. Запустити GroupInt на VPS.
2. Підключити Telegram session через OTP.
3. Для кожного seed-каналу виконати:

```text
Get messages from group
Extract endorsements from messages
```

4. Імпортувати граф у Gephi через Neo4j plugin:

```text
Labels: Group
Relationships: ENDORSES
```

5. У Gephi виконати:

```text
ForceAtlas 2
Modularity
Average Degree
PageRank
Network Diameter
```

6. Зберегти `.gephi`, скріншоти графів і таблиці топ-вузлів/ребер.

## 9. Gephi AI Analysis (MCP)

Додатковий аналіз виконано через Gephi MCP API v2.0.0 (`http://127.0.0.1:8080`) і плагін `gephi-ai` by Matt Artz.

Що виконано:

- перевірено Gephi MCP health: `success: true`;
- повторно обчислено в Gephi Statistics API: modularity / community detection, degree, weighted degree, PageRank, betweenness centrality;
- вузли розфарбовано за `Modularity Class`;
- розмір вузлів задано за `weighted degree`;
- товщину ребер задано за `Weight`;
- через надмірну вагу ребра `Republic_Of_GaGauZia -> Republic_Of_GaGauzia_MD` ForceAtlas 2 дав менш читабельний результат, тому фінальний експорт зроблено після ручного радіального layout: кластери рознесені по квадрантах, hub-вузли винесені в центри підмереж;
- експортовано PNG `screenshots/17-gephi-ai-analysis-export.png`;
- збережено проєкт `screenshots/telegram-endorsements-expanded-gephi-ai.gephi`.

Підтверджені метрики:

| Метрика | Значення |
|---|---:|
| Вузли | 70 |
| Ребра | 68 |
| Кластери після Gephi re-computation | 4 |
| Найбільший weighted degree | 3404 (`Republic_Of_GaGauZia`) |
| Найбільший PageRank | 0.0168 (`primulinmd`) |
| Betweenness centrality | 0.0 для всіх вузлів |

Gephi re-computation розбив попередній кластер 2 на два підкластери: початковий CSV мав 3 основні `modularity_class`, а повторний запуск у Gephi дав 4 community classes: 0 (38), 3 (20), 1 (6), 2 (6).

Betweenness centrality дорівнює 0.0 для всіх вузлів. Це означає не те, що "зв'язків немає", а що в поточній `ENDORSES`-моделі Gephi не виявив формальних bridge-вузлів: структура ближча до кількох star-підмереж, де більшість вузлів є листами.

Найсильніше ребро:

```text
Republic_Of_GaGauZia -> Republic_Of_GaGauzia_MD
weight: 3235
message id: 71800
```

Це аномально сильний endorsement-зв'язок. Його варто інтерпретувати обережно: вага може відображати багато повторень, агрегований результат парсингу GroupInt або особливість витягнення посилань з одного/кількох повідомлень.

## 10. Обмеження

- Частина Telegram-об'єктів є каналами, тому список учасників і авторів не використовувався як основа графа.
- Основна модель побудована на `ENDORSES`, тобто на `t.me` посиланнях і згадках.
- Частина вузлів має дублікати або варіанти назв, наприклад різні форми `MoldovaPolitics`; для глибшого аналізу потрібна додаткова нормалізація.
- Neo4j Browser через public HTTPS не використовувався для основного аналізу через обмеження TLS/Bolt; Gephi підключався через SSH tunnel.
