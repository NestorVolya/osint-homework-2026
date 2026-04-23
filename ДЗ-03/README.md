# ДЗ-03 — Nestor V

**Об'єкт:** Чекаль Олексій Георгійович  
**Дата:** 2026-04-23  
**Середовище:** Windows 10 Pro, i5-6500, 16GB RAM, GTS 450 (969MB VRAM)

---

## Структура

```
homework/
├── ДЗ-03-Nestor-V/               ← Базовий рівень (MindsDB)
│   ├── README.md
│   ├── report.md
│   └── screenshots/              ← 7 скріншотів (docker + SQL + агент)
│
└── dz-mindsdb-arkham-Nestor-V/   ← Просунутий рівень (ArkhamMirror)
    ├── README.md
    ├── arkham-overview.md        ← Огляд платформи
    ├── arkham/                   ← docker-compose + .env
    └── screenshot-arkham_*.png   ← 5 скріншотів (dashboard, docs, MindsDB)
```

---

## Базовий рівень — MindsDB

→ **[ДЗ-03-Nestor-V/README.md](ДЗ-03-Nestor-V/README.md)**

| Що зроблено | Результат |
|---|---|
| MindsDB 26.0.1 підключено до mention-index.csv (30+ записів) | ✅ |
| 3 SQL-запити: агрегація по країні, RU-фільтр, часовий аналіз | ✅ |
| AI агент `chekal_analyst` (Gemini 2.5 Flash) — 5 питань | ✅ |
| Документовані обмеження агента (галюцинації на SQL-схемі) | ✅ |
| 7 скріншотів | ✅ |

---

## Просунутий рівень — ArkhamMirror SHATTERED

→ **[dz-mindsdb-arkham-Nestor-V/README.md](dz-mindsdb-arkham-Nestor-V/README.md)**  
→ **[dz-mindsdb-arkham-Nestor-V/arkham-overview.md](dz-mindsdb-arkham-Nestor-V/arkham-overview.md)** — що таке ArkhamMirror

| Що зроблено | Результат |
|---|---|
| ArkhamMirror SHATTERED v0.1.0 запущено (Docker, port 8100) | ✅ |
| 5 документів завантажено через API і processed | ✅ |
| MindsDB ↔ ArkhamMirror PostgreSQL інтеграція (SELECT 5 rows) | ✅ |
| Auth chain фікс: `updated_at` column + email domain + localStorage key | ✅ |
| 5 скріншотів (реальний UI: dashboard + documents) | ✅ |

---

## Загальний висновок

**Два рівні аналітичного стеку без GPU і без cloud-LLM:**

```
mention-index.csv ──▶ MindsDB (SQL + AI агент) ──▶ аналіз 30+ записів
     +
ArkhamMirror (ingest/parse/store) ──▶ PostgreSQL ──▶ MindsDB ──▶ Claude
```

Вартість сесії: **~$0.002** (Gemini Flash API) замість ~$0.86 при прямому читанні Claude.
