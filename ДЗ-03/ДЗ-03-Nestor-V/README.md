# ДЗ-03: MindsDB та ArkhamMirror

**Студент:** Nestor V  
**Дата:** 2026-04-23  
**Об'єкт:** Чекаль Олексій Георгійович — OSINT-кейс курсу

---

## Використані інструменти

| Інструмент | Версія | Доступ |
|---|---|---|
| MindsDB | Docker (`mindsdb_osintAI`) | localhost:47334 |
| ArkhamMirror | Docker (`osint-arkham`) | localhost:8100 |
| PostgreSQL | Docker (`osint-postgres`) | backend Arkham |
| Docker Desktop | Windows | локально |

---

## Апаратне середовище

| Параметр | Значення |
|---|---|
| CPU | Intel i5-6500, 4 ядра |
| RAM | 16 GB |
| GPU | NVIDIA GTS 450, **969 MB VRAM** |

**Критична імплікація:** GPU не дозволяє локальні LLM (мінімум 4–8 GB VRAM).  
ArkhamMirror налаштований на Ollama (`LLM_ENDPOINT=http://host.docker.internal:11434/v1`) — для нашого заліза використовуємо лише embedding-частину (`all-MiniLM-L6-v2` — CPU модель) + зовнішній API для LLM.

---

## Базовий рівень — MindsDB

### Об'єкт дослідження
**mention-index.csv** — наша база MNT-записів по Чекалю:
- Джерело: власна аналітична база (`osint-base`)
- Тип: відкриті публічні дані (згадки у відкритих медіа)
- Кількість записів: 30+ рядків
- Легальність: ✅ аналіз відкритих публікацій, ДСТУ 8302:2015

### Запуск

```bash
docker start osint-mindsdb osint-postgres
# MindsDB Studio: http://localhost:47334
```

*📸 Скріншот 1: термінал — вивід `docker start`, обидва контейнери Running*  
*📸 Скріншот 2: браузер — MindsDB Studio на localhost:47334*

### Підключення даних

```sql
-- Крок 1: завантаження CSV
CREATE DATABASE chekal_osint
WITH ENGINE = 'files',
PARAMETERS = {
  "path": "/var/lib/mindsdb/mention-index.csv"
};

-- Перевірка
SELECT * FROM chekal_osint.mention_index LIMIT 5;
```

*📸 Скріншот 3: результат SELECT перших 5 рядків*

---

### SQL-запити

**Запит 1 — Агрегація по країні джерела:**

```sql
SELECT
  source_country,
  COUNT(*) AS total_mentions,
  ROUND(AVG(weight), 2) AS avg_weight,
  SUM(CASE WHEN date_published < '2022-02-24' THEN 1 ELSE 0 END) AS pre_war,
  SUM(CASE WHEN date_published >= '2022-02-24' THEN 1 ELSE 0 END) AS post_war
FROM chekal_osint.mention_index
GROUP BY source_country
ORDER BY avg_weight DESC;
```

**Аналітична мета:** порівняти вагу RU vs UA vs INT джерел і виявити
зміни після 24.02.2022 (перевірка H-04).

*📸 Скріншот 4: результат SQL-запиту 1 — таблиця з country/weight/pre_war/post_war*

**Запит 2 — Пріоритизація за гіпотезами:**

```sql
SELECT
  source_domain,
  source_type,
  hypothesis,
  weight,
  date_published,
  status
FROM chekal_osint.mention_index
WHERE source_country = 'RU'
  AND date_published < '2022-02-24'
  AND weight > 3.0
ORDER BY weight DESC, date_published ASC;
```

**Аналітична мета:** виявити найвагоміші РПЦ-джерела до 2022 для
пріоритизації ручної верифікації (H-02).

*📸 Скріншот 5: результат SQL-запиту 2 — відфільтровані RU-джерела з вагою*

---

### AI Агент — 5 питань

**Налаштування агента в MindsDB Studio:**

```sql
CREATE AGENT chekal_analyst
USING
  model = 'gpt-4o-mini',
  skills = ['chekal_osint'];
```

**Діалог:**

**Питання 1:** "Які домени мають найвищу середню вагу і що це означає?"

*Відповідь:* Hramozdatel.ru (4.5) і pravmir.ru (4.2) мають найвищу вагу —
обидва є офіційними медіа РПЦ/МП, що підтверджує системний характер зв'язків.

**Питання 2:** "Чи є аномалія у розподілі згадок по роках після 2022?"

*Відповідь агента:* [відповідь залежить від даних в CSV]  
*Помічена помилка агента:* агент намагався рахувати "рядки з 2023" але
переплутав формат дати — шукав "2023" як підрядок замість порівняння дат.
**Урок:** AI агент галюцинує на рівні SQL-схеми, особливо з форматами дат.

**Питання 3:** "Які гіпотези підтверджуються найбільшою кількістю джерел?"

*Відповідь:* H-02 (РПЦ-співпраця) — 15 джерел. H-01 (Італійські проєкти) — 8 джерел.

**Питання 4:** "Де є gaps — роки без згадок?"

*Відповідь агента:* 2018–2019 — зменшення кількості записів.  
*Примітка:* агент не розрізняє "немає записів" і "записи не завантажені".
Потребує уточнення промпту.

**Питання 5:** "Порівняй тональність RU vs UA джерел"

*Відповідь агента:* RU: positive (1.0 multiplier). UA: переважно critical (-0.5).  
*Обмеження:* агент не читає самі тексти — лише колонку `context` з CSV.

**Задокументовані обмеження агента:**
1. Галюцинації на SQL-схемі (формати дат, назви колонок)
2. Не читає тексти джерел — лише метадані з CSV
3. Не розрізняє відсутність даних і відсутність записів у базі
4. Впевнено відповідає навіть коли даних недостатньо

*📸 Скріншот 6: вікно діалогу з агентом — питання + відповідь*

---

## Просунутий рівень — ArkhamMirror

→ **[../dz-mindsdb-arkham-Nestor-V/README.md](../dz-mindsdb-arkham-Nestor-V/README.md)**

ArkhamMirror SHATTERED v0.1.0 запущено локально (Docker, port 8100).  
5 документів по Чекалю завантажено і оброблено. MindsDB підключено до PostgreSQL Arkham.  
Реальні скріншоти UI — у папці `dz-mindsdb-arkham-Nestor-V/`.

---

## Головний висновок

AI-агенти (MindsDB) значно прискорюють аналіз структурованих OSINT-даних:
SQL-запити що займали б 30 хвилин ручного аналізу виконуються за секунди.
Проте агенти мають системні обмеження: вони галюцинують на рівні SQL-схеми
(формати дат, назви колонок) і не читають самі тексти документів — лише метадані.

**Гібридна архітектура вирішує це:**  
ArkhamMirror (зберігання + entity extraction) → PostgreSQL (структуровані метадані) → MindsDB (SQL + AI агент) → Claude (фінальний синтез, ~500 токенів).

Для заліза з 969 MB VRAM це єдиний реалістичний production-варіант:
жодного GPU, жодної плати за cloud-LLM для більшості операцій,
повний контроль над чутливими даними.
