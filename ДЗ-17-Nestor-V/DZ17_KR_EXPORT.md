# DZ-17 → KR Export: концепція, архітектура, шляхи

**Від:** `osint-homework-2026/ДЗ-17-Nestor-V`  
**До:** `actor-osint-front/pipeline/quality_scorer.py` та суміжні модулі  
**Дата:** 2026-06-08

---

## 1. Головна ідея

**Задача ДЗ-17:** маючи набір об'єктів із кількісними поведінковими ознаками — автоматично відокремити надійні від ненадійних без ручної перевірки кожного.

**Об'єкт у ДЗ-17:** акаунт соціальної мережі (бот vs людина).  
**Об'єкт у КР:** джерело даних (URL) (релевантне vs нерелевантне / якісне vs шумове).

Логіка та пайплайн — ідентичні. Змінюються лише назви колонок.

```
features → normalize → describe → correlate → classify → cluster → gate
```

---

## 2. Реалізована концепція

### 2.1 Behavioral feature engineering

Замість того щоб перевіряти кожен об'єкт вручну — вимірюємо його **поведінку** через кількісні сигнали:

| Сигнал | Що вимірює | Чому небезпечний при аномалії |
|--------|-----------|-------------------------------|
| `duplicate_ratio` | частка повторюваного контенту | бот / шумове джерело копіює одне й те саме |
| `posts_per_day` | частота активності | автоматизована поведінка ≠ людська |
| `account_age_days` | глибина існування | новий без історії = низька довіра |
| `followers` | охоплення / авторитет | накрутка або ізольованість |

### 2.2 Нормалізація (StandardScaler)

Різні шкали (тисячі підписників vs частки 0–1) заважають порівнянню.  
`StandardScaler` зводить усі ознаки до єдиного масштабу — обов'язково перед LogReg і KMeans.

### 2.3 Класифікація (LogisticRegression) + recall-пріоритет

LogReg навчається на labeled даних і видає ймовірність класу.

**Ключове рішення:** recall важливіший за precision.  
Пропустити бота (missed detection) → він далі маніпулює.  
Хибна тривога → аналітик верифікує вручну. Менша шкода.

У КР: пропустити релевантне джерело → дірка в досьє.  
Включити зайве → аналітик відкидає після перевірки.

### 2.4 Кластеризація (KMeans) без міток

KMeans ділить об'єкти на групи **без знання labels** — тільки за структурою даних.  
Результат: `source_type_dist` у термінах КР (реєстри / ЗМІ / соцмережі / агрегатори).

### 2.5 PASS/WARN/FAIL gate logic

Пороги на метриках → статус gate. Якщо `FAIL` у критичному gate → `manual_review_required = yes`.

---

## 3. Що і як робили — кроки пайплайну

### Крок 0 — Середовище
```
uv venv .venv --python 3.11
uv pip install -r source/requirements.txt
```
**Чому 3.11:** uv блокує pip install у 3.14; 3.11 має всі wheel-файли для pandas/sklearn/scipy.

### Крок 1 — Генерація датасету
**Що:** 500 синтетичних акаунтів (350 люди / 150 боти), 5 ознак, seed=17.  
**Як:** `numpy.random.default_rng(17)` + gamma/beta розподіли — різні для людей і ботів.  
**Навіщо seed:** відтворюваність — той самий код дає ті самі дані.

```python
rng = np.random.default_rng(17)
humans = pd.DataFrame({
    'account_age_days': rng.gamma(5, 200, n_human).clip(30).round().astype(int),
    'followers':        rng.gamma(3, 500, n_human).clip(1).round().astype(int),
    'following':        rng.integers(50, 1001, n_human),
    'posts_per_day':    rng.gamma(2, 1.5, n_human).round(2),
    'duplicate_ratio':  rng.beta(2, 10, n_human).round(4),
    'is_bot': 0,
})
bots = pd.DataFrame({
    'account_age_days': rng.gamma(1.5, 30, n_bot).clip(1).round().astype(int),
    'followers':        rng.gamma(1, 80, n_bot).clip(0).round().astype(int),
    'following':        rng.integers(1000, 5001, n_bot),
    'posts_per_day':    rng.gamma(3, 8, n_bot).round(2),
    'duplicate_ratio':  rng.beta(5, 2, n_bot).round(4),
    'is_bot': 1,
})
```

### Крок 2 — Первинний огляд
**Що:** `info()`, `describe()`, розподіл класів.  
**Навіщо:** `describe()` відразу показує аномалії (max `posts_per_day` ~50 при середньому ~5).

### Крок 3 — Описова статистика
**Що:** mean / median / mode / std / range для `followers` і `posts_per_day`.  
**Ключовий інсайт:** `mean >> median` → розподіл скошений, медіана краще описує типовий об'єкт.  
**У КР:** той самий паттерн для `text_coverage_avg` / `text_coverage_median` і `niche_gap`.

```python
def descriptive_stats(series):
    return {
        'mean':   series.mean(),
        'median': series.median(),
        'mode':   series.mode()[0],
        'std':    series.std(),
        'range':  series.max() - series.min(),
    }
```

### Крок 4 — Візуалізація
**Що:** гістограма `posts_per_day`, boxplot `followers`.  
**Техніка:** `plt.savefig()` + `plt.close('all')` після кожного plot (запобігає memory leak).  
**CWD у Jupyter:** `Path.cwd()` (не `__file__` — не працює в Jupyter).

### Крок 5 — Кореляційний аналіз
**Що:** матриця Пірсон + Спірмен, heatmap (без seaborn — чистий `plt.imshow`), scatter plot топ-пари.  
**Топ-пара:** `following` vs `duplicate_ratio` (найсильніший зв'язок).  
**Принцип:** кореляція ≠ причинність. Обидві ознаки — симптоми автоматизації, не причина.

### Крок 6 — Класифікація (LogisticRegression)
**Що:** train/test split (stratify=y), `LogisticRegression(max_iter=1000)`, confusion matrix, classification report.  
**Recall-пріоритет:** прийнято свідомо — задокументовано в ноутбуку.

```python
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, stratify=y, random_state=42)
model = LogisticRegression(max_iter=1000, random_state=42)
model.fit(X_train, y_train)
```

### Крок 6.3 — Важливість ознак
**Що:** коефіцієнти LogReg на `StandardScaler`-нормованих даних → barh chart.  
**Навіщо normalization перед коефіцієнтами:** без неї коефіцієнти непорівнянні (різні шкали).  
**Результат:** топ-3 ознаки — `duplicate_ratio`, `posts_per_day`, `following`.

```python
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_train)
model_fi = LogisticRegression(max_iter=1000, random_state=42).fit(X_scaled, y_train)
coef_df = pd.Series(model_fi.coef_[0], index=features).sort_values()
```

### Крок 7 — Кластеризація (KMeans)
**Що:** `KMeans(n_clusters=2)` + `StandardScaler` → crosstab vs реальні мітки.  
**Навіщо StandardScaler:** KMeans чутливий до масштабу — без нормалізації `followers` (тисячі) домінує над `duplicate_ratio` (0–1).  
**KMeans vs DBSCAN:** DBSCAN краще для пошуку аномалій-одинаків (не примушує до кластера).

### Крок 8 — Висновки + 5 обмежень
5 обмежень із пом'якшенням у таблиці: синтетичні дані / оверфітинг / кореляція≠причинність / автоматичне маркування / статичний зріз.

---

## 4. Архітектура проєкту — шляхи до файлів

```
D:\projects\osint-homework-2026\ДЗ-17-Nestor-V\
│
├── DZ17_Bot_Detection_Nestor-V.ipynb   ← ГОЛОВНИЙ ФАЙЛ: весь код, 43 cells, 17 з outputs
├── AI_OSINT_HW_Statistics_Nestor-V.md  ← наративний звіт + KR mapping (Секція 9)
├── DZ17_KR_EXPORT.md                   ← цей файл
├── submission_comment.md               ← коментар для здачі
├── README.md                           ← acceptance criteria + KR synergy table
│
├── data/
│   └── accounts.csv                    ← датасет (500, 6): генерується Cell 1 ноутбука
│
├── screenshots/
│   ├── histogram_posts_per_day.png     ← Cell 4
│   ├── boxplot_followers.png           ← Cell 4
│   ├── scatter_plot.png                ← Cell 5
│   ├── correlation_heatmap.png         ← Cell 5
│   └── feature_importance.png          ← Cell 6.3
│
├── source/
│   ├── requirements.txt                ← pandas numpy matplotlib scikit-learn scipy jupyter
│   ├── Туторіал_Заняття_17_Python.ipynb
│   └── Лекція 17.pptx.pdf
│
└── .venv/                              ← Python 3.11.15 (uv venv --python 3.11)
    └── Scripts/python.exe              ← D:\projects\osint-homework-2026\ДЗ-17-Nestor-V\.venv\Scripts\python.exe
```

---

## 5. Mapping DZ-17 → KR модулі

| DZ-17 (ноутбук) | KR модуль | Що перенести |
|-----------------|-----------|--------------|
| Cell 3: `descriptive_stats()` | `quality_scorer.py` | `text_coverage_avg/median`, `niche_gap` |
| Cell 5: `df.corr()` | `quality_scorer.py` | кореляція між source-метриками |
| `duplicate_ratio` feature | `quality_scorer.py` | буквально та сама метрика |
| Cell 6: LogReg + recall gate | `gate_evaluator.py` | `false_positive_rate` gate: PASS/WARN/FAIL |
| Cell 6.3: StandardScaler + coef | `quality_scorer.py` | `integrated_assessment` score |
| Cell 7: KMeans + StandardScaler | `source_clusterer.py` | `source_type_dist` кластеризація |
| Cell 8: обмеження таблиця | `README.md` КР | Відомі обмеження / Валідація |

### Перейменування колонок (DZ-17 → КР)

```python
DZ17_TO_KR = {
    'duplicate_ratio':  'duplicate_ratio',       # без змін
    'posts_per_day':    'publication_frequency',
    'account_age_days': 'source_depth_days',
    'followers':        'source_reach',
    'following':        'outbound_links_count',
}
```

---

## 6. Мінімальний стартовий код для `quality_scorer.py`

```python
"""
quality_scorer.py
Refactored from DZ17_Bot_Detection_Nestor-V.ipynb (Cells 0, 3, 5, 6, 6.3, 7)
Input:  pd.DataFrame sources with columns: url, text, source_type, fetch_ok, duplicate_ratio, ...
Output: dict with OSINT_REPORT_STANDARD v1.1-kr metrics
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.cluster import KMeans


def compute_corpus_metrics(sources: pd.DataFrame) -> dict:
    """Quantitative corpus health — OSINT_REPORT_STANDARD §4."""
    texts = sources['text'].dropna()
    lengths = texts.str.len()

    return {
        'source_diversity':      sources['url'].apply(lambda u: u.split('/')[2]).nunique(),
        'duplicate_ratio':       sources.get('duplicate_ratio', pd.Series([0])).mean().round(4),
        'text_coverage_avg':     lengths.mean().round(1),
        'text_coverage_median':  lengths.median().round(1),
        'niche_gap':             (lengths < 500).mean().round(4),
        'fetch_success_rate':    sources.get('fetch_ok', pd.Series([True])).mean().round(4),
        'archive_ratio':         sources['url'].str.contains('archive|web.archive').mean().round(4),
        'source_type_dist':      sources['source_type'].value_counts().to_dict(),
    }


def evaluate_gates(metrics: dict) -> dict:
    """PASS / WARN / FAIL per gate — OSINT_REPORT_STANDARD §5."""
    gates = {}

    # Coverage & Diversity
    gates['coverage_diversity'] = (
        'PASS' if metrics['source_diversity'] >= 5
        else 'WARN' if metrics['source_diversity'] >= 3
        else 'FAIL'
    )

    # Depth & Noise
    gates['depth_noise'] = (
        'PASS' if metrics['duplicate_ratio'] < 0.2 and metrics['niche_gap'] < 0.3
        else 'WARN' if metrics['duplicate_ratio'] < 0.4
        else 'FAIL'
    )

    # Archive & Temporal
    gates['archive_temporal'] = (
        'PASS' if metrics['archive_ratio'] > 0.1
        else 'WARN'
    )

    # Technical Reliability
    gates['technical_reliability'] = (
        'PASS' if metrics['fetch_success_rate'] >= 0.85
        else 'WARN' if metrics['fetch_success_rate'] >= 0.6
        else 'FAIL'
    )

    gates['manual_review_required'] = gates['depth_noise'] == 'FAIL'
    return gates


def cluster_sources(sources: pd.DataFrame, feature_cols: list, n_clusters: int = 3) -> pd.Series:
    """KMeans source clustering — DZ-17 Cell 7 pattern."""
    X = sources[feature_cols].fillna(0)
    X_scaled = StandardScaler().fit_transform(X)
    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    return pd.Series(km.fit_predict(X_scaled), index=sources.index, name='source_cluster')
```

---

## 7. Виконання / перевірка

```powershell
# Перевірити що ноутбук виконується без помилок
& "D:\projects\osint-homework-2026\ДЗ-17-Nestor-V\.venv\Scripts\python.exe" `
  -m jupyter nbconvert --to notebook --execute --inplace `
  "D:\projects\osint-homework-2026\ДЗ-17-Nestor-V\DZ17_Bot_Detection_Nestor-V.ipynb"

# Перевірити датасет
& "D:\projects\osint-homework-2026\ДЗ-17-Nestor-V\.venv\Scripts\python.exe" -c "
import pandas as pd
df = pd.read_csv(r'D:\projects\osint-homework-2026\ДЗ-17-Nestor-V\data\accounts.csv')
print('shape:', df.shape)         # (500, 6)
print(df['is_bot'].value_counts())  # 0: 350, 1: 150
"
```

---

## 8. Git

```
Репо:   https://github.com/NestorVolya/osint-homework-2026
Гілка:  main
Папка:  ДЗ-17-Nestor-V/
Остан. commit: f820e39 — Add KR synergy section to DZ-17 README
```
