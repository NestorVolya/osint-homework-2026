## ДЗ-03: MindsDB та ArkhamMirror

### Середовище виконання

Всі кроки виконано локально на Windows 10 Pro (x64) без хмарних сервісів.
MindsDB підключений до Gemini 2.5 Flash через OpenAI-compatible API.
ArkhamMirror (SHATTERED) — локальний Docker-стек: FastAPI + PostgreSQL + pgvector.

### Використані інструменти

- MindsDB 26.0.1 (Docker, port 47436)
- ArkhamMirror SHATTERED v0.1.0 (Docker, port 8100)
- PostgreSQL 15 + pgvector (Docker)
- Docker Desktop 29.4.0

---

### Базовий рівень — MindsDB

Виконано в `ДЗ-03-Nestor-V/` (окрема папка здачі):
- 3 SQL-запити по 13 записах osint-base (FACT, SOURCE, GAP, DISC, ENTITY)
- AI агент `chekal_analyst` (Gemini 2.5 Flash) — 5 питань

→ Деталі та скріншоти: `../ДЗ-03-Nestor-V/report.md`

---

### Просунутий рівень — ArkhamMirror

#### Запуск

```bash
cd dz-mindsdb-arkham-Nestor-V/arkham
docker compose up -d
# shattered-app    → healthy, port 8100
# shattered-postgres → healthy, port 5433
```

```bash
curl http://localhost:8100/api/health
# {"status":"healthy","frame":{"version":"0.1.0","services":{"database":true,"vectors":true,...},"shards":[25 шардів]}}
```

📸 **[screenshot-arkham_health.png](screenshot-arkham_health.png)** — docker ps + health check JSON (25 шардів, status: healthy)

📸 **[screenshot-arkham_dashboard.png](screenshot-arkham_dashboard.png)** — ArkhamMirror SHATTERED Dashboard UI (реальний браузер): Database Online, Vector Store Online, Workers 14 queues, Event Bus Online, LLM Offline

#### Завантажені файли (5 документів)

| Файл | Тип | Зміст |
|---|---|---|
| f1_pravmir.txt | TXT | pravmir.ru 2013 — Чекаль, ПСТГУ, Артос, Rimini Meeting |
| f2_artos.txt | TXT | artos.org/artos.gallery — SOURCE SRC-003/004 |
| f3_russianschool.txt | TXT | russianclassicalschool.ru — RPC-афілійоване джерело |
| f4_mention_index.csv | CSV | mention-index.csv — 13 записів osint-base |
| f5_hypotheses.md | MD | H-01..H-05 — статуси гіпотез по Чекалю |

```bash
# Upload через API (JWT auth)
curl -X POST http://localhost:8100/api/ingest/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@f1_pravmir.txt" -F "project_id=$PROJECT_ID"
# {"job_id":"...","filename":"f1_pravmir.txt","status":"queued","route":["cpu-light"]}
```

📸 **[screenshot-arkham_documents_real.png](screenshot-arkham_documents_real.png)** — ArkhamMirror Documents UI (реальний браузер): 5 total, 5 processed — f1..f5 зі статусом ✓ Processed

#### Інтеграція MindsDB ↔ ArkhamMirror PostgreSQL

```sql
-- Підключення бази Arkham до MindsDB
CREATE DATABASE arkham_db WITH ENGINE = 'postgres'
PARAMETERS = {
  "host": "host.docker.internal",
  "port": 5433,
  "user": "arkham",
  "database": "arkhamdb"
};

-- Перегляд документів з Arkham через MindsDB
SELECT id, filename, file_type, status, created_at
FROM arkham_db.arkham_documents.documents
ORDER BY created_at DESC LIMIT 10;
```

**Результат:** 5 рядків — всі файли по Чекалю зі статусом `processed`

📸 **[screenshot-arkham_mindsdb.png](screenshot-arkham_mindsdb.png)** — MindsDB Studio — SELECT з arkham_db (5 документів Arkham)

---

### Задокументовані обмеження

1. **LLM вимкнений:** Ollama не запущений (969 MB VRAM). Замість нього — Gemini API через MindsDB. ArkhamMirror без LLM: entity extraction (NER) і AI-аналіз недоступні.
2. **GPU shards вимкнені:** `gpu-paddle` (OCR), `gpu-qwen` (Vision), `gpu-whisper` (Audio) — потребують 2–8 GB VRAM.
3. **pgvector dimension mismatch:** перший старт з іншою розмірністю ембедингів (1024 vs 384) — vector search недоступний до очищення колекцій.
4. **Auth/me bug:** missing `updated_at` column в initial migration — пофіксовано через `ALTER TABLE`.

---

### Головний висновок

ArkhamMirror (SHATTERED) — production-рівень OSINT-платформа (25 шардів, 400+ API endpoints, ~217,000 рядків коду). На залізі з 969 MB VRAM основна цінність — структурований document store + PostgreSQL з pgvector для гібридного пошуку, без GPU-залежних функцій.

Інтеграція MindsDB ↔ ArkhamMirror через PostgreSQL дозволяє поєднати:
- ArkhamMirror: ingest, parsing, entity extraction, storage
- MindsDB: SQL-аналітика + AI-агент поверх даних Arkham

**Повний аналітичний стек без GPU і без cloud-LLM-витрат:**
`ArkhamMirror (storage)` → `PostgreSQL (vectors)` → `MindsDB (SQL+AI)` → `Claude (синтез)`
