# ДЗ-20 — Верифікація цифрового матеріалу за Берклійським протоколом · Basic 🔵

**Виконавець:** Nestor-V + Claude Code (WebSearch / WebFetch / PowerShell)  
**URL проєкту:** https://github.com/NestorVolya/osint-homework-2026/tree/main/ДЗ-20-Nestor-V  
**Дата:** 2026-06-07

---

## Обраний матеріал

**Супутниковий знімок Maxar Technologies — вул. Яблунська, Буча, 19 березня 2022 р.**

Сенсор WorldView-3 (GSD 0.31м) зафіксував тіла на вул. Яблунській під час російської окупації Бучі. Знімок опублікований через AP 4 квітня 2022 р. та підтверджений незалежно NYT, Bellingcat та Amnesty International.

---

## Виконано

- [x] Ідентифікований один конкретний медіаматеріал із URL, платформою, датою (Розділ 0)
- [x] Верифіковано автора — Maxar Technologies, NYSE: MAXR, публічна компанія (Розділ 1)
- [x] Описано chain of custody: Maxar → AP → Reuters/NYT/Bellingcat/Amnesty (Розділ 1)
- [x] Геолокація: 50.54148° N, 30.228898° E, ≥3 орієнтири (Розділ 2)
- [x] Хронолокація: 5 незалежних індикаторів, дата 19 березня 2022 підтверджена (Розділ 3)
- [x] Факти відокремлено від інтерпретацій (Розділ 4)
- [x] Ознаки маніпуляцій перевірено — не виявлені (Розділ 4)
- [x] Правовий аналіз сформульовано як потенційна релевантність (Розділ 5)
- [x] Таблиця доказової цінності заповнена (Розділ 6)
- [x] ≥13 джерел з URL та датами (sources.md)
- [x] SHA-256 від публічної копії з поміткою (source-material/sha256.txt)
- [x] Розділ 7 рефлексії заповнений (обмеження, bias, AI)
- [x] Геолокаційні мапи: 4 OSM тайли (geolocation/)
- [x] Хронолокаційні матеріали: WorldView-3 сенсор (chronolocation/)

---

## Файлова структура

```
ДЗ-20-Nestor-V/
├── README.md                          ← цей файл
├── verification-report.md             ← основний бланк верифікації (розділи 0–7)
├── verification-report.html           ← HTML-версія з посиланнями
├── narrative-report.md                ← plain language пояснення методології
├── submission_comment.md              ← текст для копіювання в інтерфейс здачі
├── sources.md                         ← 13 верифікованих джерел
│
├── source-material/
│   ├── maxar-yablunska-20220319.webp  ← публічна копія Maxar знімку (AIAA)
│   └── sha256.txt                     ← хеш + примітка про тип копії
│
├── geolocation/
│   ├── map-scheme-bucha-z15.png       ← Буча в контексті (OSM zoom 15)
│   ├── landmark-1-yablunska-z16.png   ← вул. Яблунська з вигином (OSM zoom 16)
│   ├── landmark-2-yablunska-z17.png   ← деталі вулиці (OSM zoom 17)
│   └── map-scheme-osm-tile.png        ← додатковий тайл zoom 17
│
└── chronolocation/
    ├── worldview3-sensor-platform.jpg           ← WorldView-3 сенсор-платформа (аналог EXIF)
    └── cross-reference-bellingcat-comparison.png ← Bellingcat: відео-порівняння кадрів (крос-референс)
```

---

## Де виконувалось

**Локально** — Windows 10, PowerShell + Claude Code  
**Інструменти:** WebSearch (пошук джерел), WebFetch (завантаження контенту), PowerShell (завантаження зображень, SHA-256), Write (генерація файлів)  
**Картографія:** OpenStreetMap (© contributors, ODbL 1.0)
