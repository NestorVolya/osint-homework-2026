# ДЗ-12: план середовища

**Проблема:** `Streamlit` було встановлено у `D:\AI\.venv`, але це невдала локація.

За `D:\AI\ARCHITECTURE.md`, `D:\AI` має клас `control_plane`: архітектура, рішення, правила, плани, skills, logs. Це не місце для Python virtualenv конкретного ДЗ або Streamlit-залежностей.

---

## Правильне розміщення

### 0. Чому не `D:\servers`

`D:\servers` за `D:\AI\ARCHITECTURE.md` має клас `infra_sensitive`:

```text
VPS configs, .env, SSH, infra files; secrets не логуються
```

Тому `D:\servers` не є правильною локацією для:

- Python virtualenv конкретного ДЗ;
- `streamlit hello`;
- GroupInt checkout;
- course artifacts;
- screenshots або processed data.

Його можна використовувати тільки як **чутливу infra/secret-зону**, наприклад для приватної резервної копії Telegram API credentials або VPS-related `.env`, якщо це справді потрібно. Але runtime-файл, який читає GroupInt, все одно має бути в очікуваному місці:

```text
D:\projects\groupint\.streamlit\secrets.toml
```

Якщо зберігати резервну копію секретів у `D:\servers`, не дублювати її у звіти, logs або git.

---

### 1. Python/Streamlit для ДЗ-12

**Канонічна локація:**

```text
D:\projects\osint-homework-2026\ДЗ-12-Nestor-V\.venv
```

**Чому тут:**

- `D:\projects` = `producer_workspace`: sandbox, курс, прототипи;
- середовище належить конкретному ДЗ-12;
- його можна видалити без впливу на `control_plane`;
- залежності не забруднюють `D:\AI`.

**Команди:**

```powershell
cd D:\projects\osint-homework-2026\ДЗ-12-Nestor-V
python -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install streamlit pandas networkx
.\.venv\Scripts\python -m streamlit run .\scripts\streamlit_smoke_app.py --server.address=127.0.0.1 --server.port=8501
```

---

### 2. GroupInt checkout

GroupInt краще не вкладати як код у `ДЗ-12-Nestor-V`, бо це зовнішній інструмент, а не частина здачі.

**Рекомендована локація:**

```text
D:\projects\groupint
```

**Команди:**

```powershell
cd D:\projects
git clone https://github.com/OSINT-for-Ukraine/groupint.git groupint
cd D:\projects\groupint
```

**Secrets тільки тут і не в git:**

```text
D:\projects\groupint\.streamlit\secrets.toml
```

**Запуск GroupInt:**

```powershell
cd D:\projects\groupint
.\scripts\up-desktop.sh
```

або в Git Bash / WSL, якщо PowerShell не виконує `.sh`.

---

## Що робити з помилковим `D:\AI\.venv`

Не переносити `.venv` вручну. Віртуальні середовища на Windows містять абсолютні шляхи в entrypoint-скриптах, тому надійніше створити нове середовище в правильному місці.

Після успішної перевірки нового середовища:

```powershell
cd D:\projects\osint-homework-2026\ДЗ-12-Nestor-V
.\.venv\Scripts\streamlit --version
.\.venv\Scripts\python -m streamlit run .\scripts\streamlit_smoke_app.py --server.address=127.0.0.1 --server.port=8501
```

тоді можна видалити помилкове середовище:

```powershell
Remove-Item -LiteralPath D:\AI\.venv -Recurse -Force
```

Видалення робити тільки після підтвердження, що новий `.venv` працює.

---

## Остаточна схема

```text
D:\AI
  control_plane
  ARCHITECTURE.md
  PLANS.md
  logs/
  prompts/
  # без .venv для ДЗ

D:\servers
  infra_sensitive
  VPS configs / .env / SSH / secrets
  # не місце для Streamlit .venv або GroupInt checkout

D:\projects\osint-homework-2026\ДЗ-12-Nestor-V
  homework workspace
  .venv/                 # Python helpers, Streamlit smoke, scripts
  data/
  screenshots/
  scripts/
  PLAN.md
  LESSON12_CHECKLIST.html

D:\projects\groupint
  external tool checkout
  .streamlit/secrets.toml # local secret, never commit
  Docker stack
  Neo4j data
```

---

## Acceptance Criteria

- [x] У `D:\AI` немає активного `.venv` для ДЗ-12.
- [x] `D:\servers` не використовується для `.venv`, Streamlit runtime або GroupInt checkout.
- [x] Streamlit встановлено в `D:\projects\osint-homework-2026\ДЗ-12-Nestor-V\.venv`.
- [x] `streamlit --version` працює з нового `.venv`.
- [x] `streamlit hello` запускається з нового `.venv`.
- [x] GroupInt checkout живе окремо: `D:\projects\groupint`.
- [ ] Telegram secrets лежать тільки в `D:\projects\groupint\.streamlit\secrets.toml` — pending, credentials ще не створювалися.
- [x] Помилковий `D:\AI\.venv` видалено тільки після успішної перевірки нового середовища.

---

## Поточний статус після виконання

Дата: 2026-05-25.

Зроблено:

- створено `D:\projects\osint-homework-2026\ДЗ-12-Nestor-V\.venv`;
- встановлено `streamlit 1.57.0`, `pandas 3.0.3`, `networkx 3.6.1`;
- `streamlit hello` перевірено з нового `.venv`;
- створено helper-скрипт `scripts/run_streamlit_hello.ps1`;
- створено CMD launcher `scripts/run_streamlit_smoke.cmd`;
- створено stop-скрипт `scripts/stop_streamlit_8501.ps1`;
- видалено помилковий `D:\AI\.venv`;
- склоновано GroupInt у `D:\projects\groupint`;
- у `.gitignore` додано правила для `.venv/` і `streamlit-hello*.log`.

Команди для ручного запуску:

```powershell
cd D:\projects\osint-homework-2026\ДЗ-12-Nestor-V
.\.venv\Scripts\streamlit --version
.\scripts\run_streamlit_smoke.cmd
```

Після запуску очікуваний URL:

```text
http://127.0.0.1:8501
```

Зупинка локального Streamlit:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\stop_streamlit_8501.ps1
```
