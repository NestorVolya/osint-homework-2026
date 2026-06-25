# Коментар для здачі ДЗ-17

**ДЗ-17 — Статистика в OSINT: як працювати з даними та знаходити закономірності · Basic 🔵 + Advanced 🔴**
Хто / чим: студент Nestor-V + Claude Code (агент); Python 3.11 · pandas · numpy · matplotlib · scikit-learn · scipy · Jupyter Notebook

**Зроблено:**
- Синтетичний датасет `accounts.csv`: 500 акаунтів (350 людей / 150 ботів), 5 ознак (`account_age_days`, `followers`, `following`, `posts_per_day`, `duplicate_ratio`) + мітка `is_bot`; seed `rng(17)` — повна відтворюваність
- Первинний огляд: `info()`, `describe()`, розподіл класів; описова статистика (mean / median / mode / std / range) для `followers` і `posts_per_day` — виявлено сильну правосторонню асиметрію
- Візуалізація: гістограма `posts_per_day` (правий хвіст — автоматизована активність), boxplot `followers` (викиди вгорі)
- Кореляційний аналіз: матриця Пірсон + Спірмен, heatmap (без seaborn — чистий matplotlib imshow), scatter plot топ-пари `following` vs `duplicate_ratio`
- Класифікація: `LogisticRegression` (stratify, max_iter=1000) — accuracy/precision/recall/confusion matrix; recall пріоритетний (пропущений бот = більша шкода)
- Аналіз важливості ознак: коефіцієнти LogReg на `StandardScaler`-нормованих даних + barh chart — топ ознаки: `duplicate_ratio`, `posts_per_day`, `following`
- Кластеризація: `KMeans(n_clusters=2)` + `StandardScaler`; crosstab vs реальні мітки; порівняння KMeans vs DBSCAN
- Наративний звіт `AI_OSINT_HW_Statistics_Nestor-V.md` простими словами + секція синергії з Курсовим проєктом

**Зв'язок із Курсовим проєктом:** КР — система профілювання акторів: збирає відкриті дані з сотень джерел і оцінює їх якість перед включенням у звіт. Логіка ДЗ-17 і КР ідентична: є об'єкт (акаунт / джерело), є ознаки поведінки, мета — відфільтрувати ненадійний від надійного. `duplicate_ratio`, `posts_per_day`, LogReg, KMeans — всі ці інструменти з ДЗ-17 напряму переносяться в модуль оцінки якості джерел КР без змін логіки.

**Де:** Local (Windows 10) — Python 3.11 venv (uv), Jupyter Notebook у VS Code / Google Colab

**Проблеми:**
- uv-managed Python 3.14.4 блокує `pip install` → вирішено: `uv venv --python 3.11` (Python 3.11.15, всі wheel-файли доступні)
- matplotlib heatmap без seaborn → реалізовано через `plt.imshow + colorbar + text annotations`

**Acceptance criteria:**

🔵 Базовий:
- [x] Датасет згенерований (`data/accounts.csv`, 500×6)
- [x] Первинний аналіз даних (`info()`, `describe()`, розподіл класів)
- [x] Описова статистика (mean / median / mode / std / range для `followers` та `posts_per_day`)
- [x] Побудовано всі необхідні графіки (гістограма, boxplot, scatter plot)
- [x] Кореляційний аналіз (матриця Пірсон + Спірмен + heatmap)
- [x] Навчено Logistic Regression (accuracy / precision / recall / confusion matrix)
- [x] Кластеризація K-Means (`StandardScaler` + `n_clusters=2`)
- [x] Висновки до кожного етапу
- [x] Мінімум три обмеження дослідження (описано 5 обмежень із пом'якшенням)
- [x] Код запускається "з нуля" без помилок (перевірено через `nbconvert --execute` та Google Colab)

🔴 Просунутий:
- [x] Порівняння KMeans vs DBSCAN з обґрунтуванням
- [x] Наративний звіт з OSINT-контекстом та зв'язком із Курсовим проєктом
- [x] Аналіз важливості ознак (коефіцієнти LogReg на стандартизованих ознаках + barh chart)

**Репозиторій:** https://github.com/NestorVolya/osint-homework-2026/tree/main/ДЗ-17-Nestor-V

**Ноутбук у Google Colab (виконаний):** https://colab.research.google.com/drive/11lLxATRgW7oN0Rn7dDt8R8sItNrhHw7F#scrollTo=GflS3WLzm6dL
