**ДЗ-17 — Статистика в OSINT: робота з даними та пошук закономірностей · Basic 🔵 + Advanced 🔴**

Хто / чим: студент Nestor-V + Claude Code (агент); Python 3.11 · pandas · numpy · matplotlib · scikit-learn · scipy

ТУТ: https://github.com/NestorVolya/osint-homework-2026/tree/main/ДЗ-17-Nestor-V

**Зроблено:**

- Згенеровано синтетичний датасет 500 акаунтів (350 людей / 150 ботів), 5 ознак: `account_age_days`, `followers`, `following`, `posts_per_day`, `duplicate_ratio`
- Первинний огляд: `info()`, `describe()`, розподіл класів
- Описова статистика для `followers` і `posts_per_day`: mean / median / mode / std / range
- Гістограма `posts_per_day` та boxplot `followers` з інтерпретацією
- Кореляційна матриця (Пірсон + Спірмен) та scatter plot топ-пари
- Класифікація ботів: `LogisticRegression`, accuracy / precision / recall, confusion matrix
- Кластеризація: `KMeans(n_clusters=2)` + `StandardScaler`, порівняння кластерів із мітками
- Висновки до кожного етапу + ≥3 обмеження з пом'якшенням
- Наративний звіт із OSINT-контекстом та зв'язком із Курсовим проєктом

**Де:** Local (Windows 10) — Python 3.11 (venv), Jupyter Notebook у VS Code

---

## Структура здачі

| Файл | Зміст |
|---|---|
| [DZ17_Bot_Detection_Nestor-V.ipynb](DZ17_Bot_Detection_Nestor-V.ipynb) | Основний ноутбук: весь код + аналіз + висновки |
| [AI_OSINT_HW_Statistics_Nestor-V.md](AI_OSINT_HW_Statistics_Nestor-V.md) | Наративний звіт простими словами (ЩО/ЯК/НАВІЩО) |
| [data/accounts.csv](data/accounts.csv) | Датасет 500 акаунтів (генерується ноутбуком) |
| [screenshots/histogram_posts_per_day.png](screenshots/histogram_posts_per_day.png) | Гістограма posts_per_day |
| [screenshots/boxplot_followers.png](screenshots/boxplot_followers.png) | Boxplot followers |
| [screenshots/scatter_plot.png](screenshots/scatter_plot.png) | Scatter plot топ-пари кореляції |
| [screenshots/correlation_heatmap.png](screenshots/correlation_heatmap.png) | Теплова карта кореляцій |
| [screenshots/feature_importance.png](screenshots/feature_importance.png) | Коефіцієнти LogReg (важливість ознак) |
| [source/](source/) | Матеріали заняття (лекція, туторіал, requirements) |

## OSINT-контекст та зв'язок із Курсовим проєктом

**Про Курсовий проєкт:** система профілювання акторів — збирає відкриті дані про людину з різних джерел і оцінює їх якість перед включенням у звіт.

Логіка ДЗ-17 і КР ідентична: є об'єкт (акаунт / джерело даних), є ознаки поведінки, мета — відфільтрувати ненадійний від надійного.

| Що в ДЗ-17 | Що це означає в КР |
|---|---|
| `duplicate_ratio` — частка однакових дописів | Частка дублікатів серед матеріалів джерела. Сайт, що повторює один текст 40 разів — шум, не інформація |
| `posts_per_day` — активність акаунта | Частота публікацій джерела. 200 статей на день — агрегатор або спам |
| `account_age_days` — вік акаунта | Глибина архіву джерела. Свіжий ресурс без історії — низька довіра |
| `followers` — аудиторія | Охоплення джерела. Ширша аудиторія = вища вага в підсумковій оцінці |
| LogisticRegression + recall | Класифікатор релевантне / нерелевантне джерело. Recall пріоритетний: пропустити важливе джерело гірше, ніж включити зайве |
| KMeans | Групування джерел за типом: реєстри / ЗМІ / соцмережі / агрегатори |
| StandardScaler | Нормалізація різнорідних метрик перед підрахунком підсумкового балу надійності |

Детально — у [AI_OSINT_HW_Statistics_Nestor-V.md](AI_OSINT_HW_Statistics_Nestor-V.md), розділ 9.

---

## Acceptance Criteria — самоперевірка

### 🔵 Базовий

- [x] датасет успішно згенерований (`data/accounts.csv`, 500 × 6)
- [x] виконано первинний аналіз даних (`info()`, `describe()`, розподіл класів)
- [x] обчислено описову статистику (mean / median / mode / std / range для `followers` та `posts_per_day`)
- [x] побудовано всі необхідні графіки (гістограма, boxplot, scatter plot)
- [x] виконано кореляційний аналіз (матриця Пірсон + Спірмен + heatmap)
- [x] навчено Logistic Regression (accuracy / precision / recall / confusion matrix)
- [x] проведено кластеризацію K-Means (`StandardScaler` + `n_clusters=2`)
- [x] сформульовано висновки до кожного етапу
- [x] описано мінімум три обмеження дослідження (5 обмежень із пом'якшенням)
- [x] код запускається "з нуля" без помилок (перевірено через `nbconvert --execute`)

### 🔴 Просунутий

- [x] порівняння KMeans vs DBSCAN з обґрунтуванням (таблиця у Частині 7)
- [x] наративний звіт з OSINT-контекстом (зв'язок із реальним пайплайном та КР — `AI_OSINT_HW_Statistics_Nestor-V.md`)
- [x] аналіз важливості ознак (коефіцієнти LogReg на стандартизованих ознаках + barh chart)
