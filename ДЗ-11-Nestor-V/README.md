# ДЗ-11: Міні-OSINT-звіт — Дезінформаційна мережа

**ДЗ-11 — Міні-OSINT-звіт: Дезінформаційна мережа · Basic 🔵**

Хто / чим: студент Nestor-V + Claude Code (агент); WebSearch/WebFetch, EU DisinfoLab, Meta, EEAS, Euronews, Correctiv

ТУТ: https://github.com/NestorVolya/osint-homework-2026/tree/main/ДЗ-11-Nestor-V

**Зроблено:**

- Обрано кейс **Doppelganger** (Italian campaign, 2022–2024) — клонування медіасайтів проросійськими акторами

- Зібрано та верифіковано 8 першоджерел: EU DisinfoLab (2022), Meta Q3 2023, EEAS Technical Report (квітень 2024), Euronews (09.2024), Correctiv (07.2024)

- Описано 5 кейсів: клон ANSA/`lastampa.in`/`repubblica.in` (зареєстровано 2024-04-05, заголовки *«Non c'è salvezza: l'UE distruggerà l'economia italiana»*, *«Bruxelles uccide»*), наратив «санкції = катастрофа», 98 Meta-оголошень, 1 300+ постів на X під час виборів ЄП, VK-координація italian-targeting

- Визначено 6 методів роботи: typosquatting, платна реклама, обхід модерації, багатомовний контент, AI-генерація, VK-координація

- Наративи згруповано у 5 кластерів: економічний страх, дискредитація України, антизахідний, підрив довіри до медіа, поляризація суспільства

- Усі твердження у розділах 1–2 мають вбудовані активні посилання на джерела

**Де:** Local (Windows 10) — WebSearch/WebFetch + git

---

## Структура здачі

| Файл | Зміст |
|---|---|
| [mini_osint_report_doppelganger_italy.md](mini_osint_report_doppelganger_italy.md) | Основний звіт: опис, 5 кейсів, методи, наративи, висновок, джерела |
| [mini_osint_report_doppelganger_italy.html](mini_osint_report_doppelganger_italy.html) | HTML-версія з нумерованими виносками-посиланнями |
| [sources.md](sources.md) | Повна таблиця 16 джерел зі статусом перевірки |
| [sources.html](sources.html) | HTML-версія таблиці джерел (клікабельні лінки) |
| [screenshots/](screenshots/) | 16 скріншотів першоджерел (перейменовані за змістом) |

### Ключові скріншоти

| Файл | Що показує |
|---|---|
| `eu-disinfolab-doppelganger-fake-site-example.png` | Приклад клонованого медіасайту (EU DisinfoLab, вер. 2022) |
| `mapfre-2024-09-04-italy-la-repubblica-doppelganger.png` | Інцидент La Repubblica — DOJ, вер. 2024 |
| `eeas-report-doppelganger-strikes-back-italy-content-placement.png` | EEAS: розміщення контенту через Italy-клони |
| `meta-q3-2023-russia-section-cib-rt-accounts-removed.png` | Meta Q3 2023: видалення CIB-мережі пов'язаної з RT |
| `correctiv-2024-07-inside-doppelganger-eu-companies.png` | Correctiv: SDA координує через EU-компанії |
| `mapfre-media-freedom-map-doppelganger-europe-incidents.png` | Карта інцидентів Doppelganger по Європі |

---

## Acceptance Criteria — самоперевірка

### 🔵 Базовий

- [x] Обрано релевантну проросійську дезінформаційну групу (Doppelganger)
- [x] Використано 5–8 якісних відкритих джерел (використано 8)
- [x] Джерела наведені у фінальному звіті
- [x] Підготовлено короткий профіль групи (розділ 1)
- [x] Описано 3–5 прикладів активності (5 кейсів, розділ 2)
- [x] Визначено основні методи роботи групи (6 методів, розділ 3)
- [x] Виділено 3–5 ключових наративів (5 наративів у 5 групах, розділ 4)
- [x] Додано обов'язкову таблицю (розділ 5: дата / кейс / країна / метод / джерело)
- [x] Додано короткий опис використання AI
- [x] AI не використано як джерело фактів — всі факти перевірені через WebSearch/WebFetch
- [x] Дотримано правил безпечної OSINT-роботи (тільки відкриті джерела, без взаємодії з інфраструктурою)
- [x] Звіт має чітку структуру й короткий висновок
