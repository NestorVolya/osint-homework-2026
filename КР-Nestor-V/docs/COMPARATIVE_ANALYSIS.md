# Порівняльний аналіз виконань КР OSINT

Дата аудиту: 2026-06-18
Головний критерій: здача курсового проєкту з напряму 1, тобто runnable pipeline від seed до HTML/PDF/JSON/SQLite/ZIP, з README, прикладом роботи, evidence preservation, quality/limitations і без хардкоду секретів.

## 1. Scope

Перевірені джерела:

- `course-root/` — первинна папка завдання, створена 2026-05-26.
- `course-root/actor-osint-front (CODEX)` — ChatGPT-generated diagrams та prompt files.
- `course-root/actor-osint-front-СC(ClaudeCode)` — Claude Code implementation images.
- `actor-osint-front/` — паралельна реалізація pipeline.
- `actor-osint-front-СС/` — основна реалізація (фінальна база здачі).
- `osint-persona/` — sidecar для username/email/Telegram профілювання.
- Session logs та planning docs (internal).

Не змінювався код жодного з проєктів. Створено окрему audit-папку з датою 2026-06-18.

## 2. Executive Conclusion

Найкраща база для здачі КР: `actor-osint-front-СС/` (цей репозиторій, `КР-Nestor-V/`).

Причина: це єдине виконання, яке має одночасно повний runnable pipeline, README з 8 потрібними секціями, examples/sample_run, multi-actor validation, quality gates, великі HTML/MD звіти, SQLite, ZIP artifacts, Dockerfile, bridge/export skeleton, і логовану перевірку `pytest 15/15 PASS` у сесійному журналі.

`actor-osint-front/` не треба брати як фінальну базу для здачі. Його цінність інша: це джерело кращих ідей для методології пошуку і чесного опису blind zones: source packs, `search_quality.json`, social adapter contract, Facebook discovery diagnostics. Але поточний artifact у `output` після smoke є sample-only, statements=0, а full live all-4 після останніх змін не виконано.

`osint-persona/` корисний як ранній sidecar: він краще відповідає буквальним пунктам завдання про nickname/email, HIBP/Holehe, Sherlock-like probing, avatar pHash, Telegram public channel, EXIF geo. Але він слабший як фінальна КР-система: менше validation, менші звіти, не той actor-profiling корпус, немає multi-actor DoD, і це радше інструмент для облікових слідів, ніж повне публічне досьє.

Вкладені `(CODEX)` / `(ClaudeCode)` папки в основній директорії курсового не є кодовими реалізаціями: там збережені ChatGPT image prompts/діаграми. Їх можна використати як презентаційні матеріали, але не як виконання КР.

## 3. Development Timeline

| Дата | Гілка/папка | Розвиток | Значення для здачі |
|---|---|---|---|
| 2026-05-26 | `osint-persona` | Перший runnable прототип для username/email/telegram, локальна SQLite, HTML, ZIP. | Добре закриває буквальний напрям 1, але не має достатньо сильного фінального validation. |
| 2026-05-27 | `actor-osint-front-СС` | Швидкий end-to-end pipeline: Exa/Tavily, SQLite 7 таблиць, gates, graph, live runs. | Початок найсильнішої гілки для здачі. |
| 2026-05-27 | `actor-osint-front` | Local-first Codex baseline, federated search, scoring, manual layer, smoke без pytest. | Чистіша архітектура, але слабша submission-готовність. |
| 2026-05-28/29 | `actor-osint-front-СС` | Quality gates, README, examples, Dockerfile, DSTU, bridge skeleton, multi-actor validation. | Формується майже повний submission package. |
| 2026-05-29 | `actor-osint-front` | All-4 validation до PASS 4/4, але з ризиком high noise для A. | Доказ, що база теж може пройти DoD, але не фіналізована після пізніших змін. |
| 2026-06-03 | обидві actor-гілки | ARS methodology: temporal gaps, blind zones, evidence quotes; СС отримує більше LLM-методів. | СС стає сильнішим аналітичним звітом; Codex залишається rule-based/partial. |
| 2026-06-06 | `actor-osint-front-СС` | Final Chekal run, Braschi run, zero-source fix, Wikipedia User filter, examples оновлено, pytest 15/15 PASS. | Найкраща точка для здачі. |
| 2026-06-08 | `actor-osint-front` | Social Adapter Framework v0.1, Search Quality instrumentation, Facebook discovery, query builder tests. | Сильний методологічний layer, але full live all-4 не повторено. |
| 2026-06-18 | `actor-osint-front` | Поточний smoke sample run має 5 sources і 0 statements. | Не використовувати поточний output як submission evidence. |

## 4. Project Inventory

| Виконання | Тип | Code size | Artifacts | Git state | Ключовий висновок |
|---|---:|---:|---:|---|---|
| `actor-osint-front-СС` | Full pipeline | 26 Python files, ~4459 LOC | 38 ZIP, 83 HTML, 488 JSON | not git repo | Best submission candidate. |
| `actor-osint-front` | Full pipeline + diagnostics | 40 Python files, ~4822 LOC | current output only sample after smoke | not git repo | Best source of search/social-quality ideas, not final package. |
| `osint-persona` | Sidecar/persona OSINT | 20 Python files, ~1400 LOC | 4 ZIP, 8 HTML | not git repo | Useful for username/email/telegram features. |
| nested `(CODEX)` | Visual prompt package | no code | images + prompt txt | no repo | Use for diagram/presentation only. |
| nested `(ClaudeCode)` | Visual prompt package | no code | images + prompt txt | no repo | Use for simplified explanation/defense only. |

## 5. Rubric Matrix

Scoring: 0 = absent, 1 = weak, 2 = partial, 3 = good, 4 = strong, 5 = strongest among these candidates.

| Критерій здачі | `actor-osint-front-СС` | `actor-osint-front` | `osint-persona` | Visual folders | Коментар |
|---|---:|---:|---:|---:|---|
| Runs from seed to report | 5 | 4 | 4 | 0 | СС має documented live runs; Codex має runnable architecture, але current smoke output слабкий. |
| Collect layer | 5 | 5 | 3 | 0 | СС: Exa/Tavily/Google CSE; Codex: federated search + source packs; persona: username/email/telegram, не general full-name corpus. |
| Evidence preservation | 5 | 5 | 3 | 0 | Обидва actor-проєкти мають timestamped output, SQLite, raw, ZIP; persona простіший. |
| Analysis/enrichment | 5 | 4 | 3 | 0 | СС має statements, links, contradictions, temporal gaps, quality gates; Codex має timeline/statements/links + search/social diagnostics. |
| Report quality | 5 | 3 | 3 | 2 | СС HTML 160k+ і report_quality.md; Codex звіт методологічно хороший, але current sample маленький. |
| Multi-actor validation | 5 | 4 | 1 | 0 | СС: 4 actors, 5/5 gates PASS; Codex: all-4 PASS до 2026-05-29, але не після фінальних змін. |
| Search quality | 4 | 5 | 2 | 0 | Codex має найкращу діагностику query intents/source packs/Facebook/social blind zones. |
| Social/account coverage | 3 | 4 | 5 | 0 | Persona найкраще закриває username/email/telegram/pHash/EXIF; Codex найкраще описує blind zones. |
| README/submission docs | 5 | 3 | 4 | 0 | СС README найближчий до вимог викладача. |
| Tests/verification | 5 | 3 | 1 | 0 | СС має лог `pytest 15/15 PASS`; Codex має query/social tests, але smoke зараз падає на empty statements. |
| Safety/secrets | 5 | 5 | 4 | 0 | Усі кодові гілки читають ключі з env/.env, без включення секретів. |
| Presentation/defense assets | 4 | 5 | 2 | 5 | Codex і visual folders мають найкращі пояснювальні діаграми/рамки. |
| Final readiness | 5 | 3 | 2 | 1 | Для здачі найменший ризик у СС. |

Weighted conclusion: `actor-osint-front-СС` є фінальною базою; `actor-osint-front` і `osint-persona` є donor/reference гілками, але не merger targets перед здачею.

## 6. Detailed Candidate Review

### 6.1. `actor-osint-front-СС`

Сильні сторони:

- Реальний end-to-end pipeline: `collect -> accounts -> enrich_timeline/statements/network -> quality_check -> report -> archive`.
- Пошук: Exa + Tavily + Google CSE; Google CSE додано як покриття для multilingual/RU/IT cases.
- Збереження: SQLite з таблицями `sources`, `events`, `statements`, `links`, `accounts`, `geoclusters`; raw provider JSON; ZIP artifacts.
- Quality: `quality_report.json`, `corpus_health_score`, 5 gates, `report_quality.md`.
- Report: великий HTML, `accounts_graph.html`, `report_quality.md`, glossary для критеріїв.
- Validation: 4 актори різного типу, PASS у всіх; наявні приклади:
  - Чекаль 2026-06-06_23-31-12: 44 sources, health 1.00, 5/5 PASS.
  - Braschi 2026-06-06_22-10-49: 40 sources, 53 statements, health 1.00.
  - Коваленко: 77 sources.
  - Філоненко: 54 sources.
- README має потрібні для здачі секції: опис, напрям, install, run, input, output, API, limitations.
- Є `examples/sample_run` і `examples/sample_run.zip`.
- Є documented `pytest 15/15 PASS` у session log 2026-06-06.

Слабкі місця:

- Не Git-репозиторій.
- Частина останніх `output` після 2026-06-08/17 є порожніми DB runs; їх не можна подавати як приклад.
- Social blind zones залишаються: VK/OK/TG не закриті повноцінно.
- pHash/reverse image є слабшими, ніж у `osint-persona`.
- Деякі quality gates можуть виглядати надто оптимістично: health 1.00 навіть при statements=0 для Чекаля. Це треба пояснити як corpus-health, не truth-confidence.

Оцінка для здачі: 46-51/53 залежно від того, чи буде зроблено GitHub/ZIP packaging і коротке demo.

### 6.2. `actor-osint-front`

Сильні сторони:

- Найкраща методологічна робота з пошуком після 2026-06-03/08.
- Source packs generic, не overfit під професію: `regional_web`, `media_news`, `public_social`, `video_public`, `archives`, `organizations_sites`.
- `raw/search_queries.json` як transparency/cost audit.
- `search_quality.json`: query intent coverage, provider errors, rejected/accepted counts, missing zones, Facebook candidates.
- Social Adapter Framework v0.1: `checked/partial/blind_zone/provider_required/high_risk` і чесна рамка для Facebook/VK/OK/Telegram.
- Query builder локально перевірений на A/B/C/D: profile, interview, archive, historical, social, Facebook, source-pack coverage.
- Хороші submission notes і defense wording.

Слабкі місця:

- Не Git-репозиторій.
- Поточний `output` був перезаписаний smoke run 2026-06-18 і не є submission-ready: 5 sources, 0 statements, `niche_gap=1.0`.
- `tests/test_smoke.py` зараз падає, бо очікує `statements > 0`, а sample fixture дає порожні statements.
- Full live all-4 після Social Adapter Framework/Search Quality/Facebook discovery не виконано.
- Немає такого сильного `examples/sample_run`, як у СС.

Оцінка для здачі: не брати як final root без додаткового live refresh і smoke fix. Як donor: дуже цінний для формулювання обмежень, search roadmap і future work.

### 6.3. `osint-persona`

Сильні сторони:

- Найближче до буквального формулювання “nickname/email”: username enumeration, HIBP, Holehe, Telegram public channel.
- Є pHash avatar matching і EXIF reverse geolocation, чого бракує actor-гілкам.
- Простий CLI і невеликий код.
- Є output HTML/ZIP/SQLite.
- Zero-LLM by design: дешевий і контрольований sidecar.

Слабкі місця:

- Не має actor-profile повноти: статті/інтерв’ю/проєкти/джерела корпусу не так розвинені.
- Немає multi-actor quality validation.
- Reports менші й менш переконливі для аналітичного досьє.
- Не є найкращою базою для публічної особи/fullname case.

Оцінка для здачі: не фінальна база, але варто згадати у roadmap як майбутній account-discovery sidecar або donor для pHash/EXIF/email modules.

### 6.4. Visual folders in course root

Сильні сторони:

- Є prompts і зображення для системної діаграми pipeline.
- Корисно для презентації/захисту: простими словами пояснюють flow seed -> search -> DB -> enrichment -> report.

Слабкі місця:

- Немає коду, README, runnable pipeline або artifacts.
- Не є виконанням КР у технічному сенсі.

Оцінка для здачі: presentation support only.

## 7. Best-of-Breed Matrix

| Компонент | Найкраще джерело | Чому |
|---|---|---|
| Final root для здачі | `actor-osint-front-СС` | Найповніший submission package і validation. |
| README | `actor-osint-front-СС` | Закриті 8 обов’язкових секцій. |
| Приклад output | `actor-osint-front-СС\examples\sample_run` | Великий report, quality report, ZIP. |
| Search diagnostics | `actor-osint-front` | `search_quality.json`, query intents, Facebook candidates. |
| Source packs | `actor-osint-front` | Generic evidence-surface packs без професійного overfit. |
| Social blind-zone framing | `actor-osint-front` | Versioned social adapter contract. |
| Quality gates | `actor-osint-front-СС` | 5 gates + health score + report_quality.md. |
| LLM statement extraction | `actor-osint-front-СС` | Gemini + regex fallback + DA steelman. |
| Contradictions/gaps | `actor-osint-front-СС` | `detect_contradictions`, temporal gaps, report sections. |
| Username/email/pHash/EXIF | `osint-persona` | Єдине виконання з цими modules. |
| Presentation diagram | nested visual folders + Codex docs | Найкращі пояснювальні artifacts. |

## 8. Main Risks Before Submission

| Ризик | Severity | Де | Коментар | Рішення |
|---|---|---|---|---|
| Немає Git repo | High | усі code roots | GitHub варіант здачі зараз не готовий. | Для здачі або curated ZIP, або `git init` тільки у `actor-osint-front-СС`. |
| Порожні/невдалі runs змішані з добрими | High | `actor-osint-front-СС\output` | Є нульові DB runs 2026-06-08/17. | В examples лишати тільки curated sample run; у ZIP не включати весь output. |
| Codex current smoke failed | Medium | `actor-osint-front` | `statements=0` у sample. | Не брати Codex current output як evidence. |
| Social blind zones | Medium | усі | VK/OK/TG/Facebook deep extraction не закриті. | Чесно описати як limitation; не claiming absence. |
| Quality score може бути misunderstood | Medium | СС | Health=1.00 не означає truth=1.00. | У README/defense казати: corpus health, not final judgment. |
| Overengineering before deadline | High | strategy | Merge гілок може зламати готовий package. | Freeze СС; переносити тільки формулювання/документацію, не код. |

## 9. Recommended Strategy

### Decision

Final submission should be based on `actor-osint-front-СС/` (цей репозиторій).

### Strategy Steps

1. Freeze code in `actor-osint-front-СС` as submission root.
2. Use `examples/sample_run` / `output\2026-06-06_23-31-12` as the canonical example, not later empty runs.
3. Do not merge `actor-osint-front` code before submission.
4. Borrow only documentation concepts from Codex branch:
   - `search_quality` as future work / limitation language;
   - source packs idea as generic coverage layers;
   - social adapter contract wording: `partial`, `blind_zone`, `provider_required`, `high_risk`.
5. Mention `osint-persona` only as future sidecar for nickname/email/pHash/EXIF, unless the teacher specifically wants nickname/email emphasis.
6. Submission packaging choice:
   - Fastest: curated ZIP from `actor-osint-front-СС` with source, config, README, requirements, Dockerfile, examples, validation docs.
   - Better: initialize Git in a clean copy of `actor-osint-front-СС`, commit, push to GitHub, add `popovvasile` collaborator.
7. Include visual diagram from nested folder or `docs/KR_STRATEGY_PERSONS_DIAGRAM.html` as presentation/support material.
8. Keep limitations honest:
   - no final judgment/agency claims;
   - VK/OK/TG/Facebook deep extraction not fully checked;
   - reverse image geosearch is limited or future work;
   - results are evidence candidates and need human review.

### Do Not Do Before Submission

- Do not try to combine `actor-osint-front` and `actor-osint-front-СС` code.
- Do not rerun destructive smoke tests that clean `output`.
- Do not include all historical `output` directories in final ZIP.
- Do not present social blind zones as “nothing found”.
- Do not connect to `osint-base`, VPS runtime, or production DB.

## 10. Strategy Verification

Verification against teacher rubric:

| Rubric item | Strategy result | Status |
|---|---|---|
| Pipeline runs from scratch | СС has documented CLI, dry-run, live runs, pytest log. | PASS, but final package should include one clean run command. |
| Collect -> Store -> Report | СС implements all three stages. | PASS |
| Artifact archive timestamped | СС has `output/YYYY-MM-DD_HH-MM-SS`, SQLite, ZIP. | PASS |
| Final report | СС has HTML + `report_quality.md` + graphs. | PASS |
| Real problem, not synthetic | Multi-actor public-person profiling with real sources. | PASS |
| Code quality / env | `.env.example`, gates, no secret hardcode in reviewed docs. | PASS |
| README | СС README covers required sections. | PASS |
| Example output | `examples/sample_run` exists. | PASS |
| Graph bonus | `accounts_graph.html`, graph export. | BONUS PASS |
| Docker bonus | Dockerfile exists. | BONUS partial/pass if not demoed. |
| Known limitations | README/NOTES/validation discuss blind zones. | PASS |

Verification against available evidence:

- `actor-osint-front-СС\VALIDATION_REPORT_KR.md`: 4 actors PASS, 5/5 gates.
- Session log 2026-06-06: final run, examples updated, pytest 15/15 PASS.
- Existing SQLite/JSON scan: strong runs have 40-46+ sources and large reports; later empty runs exist but are avoidable by curated packaging.
- `actor-osint-front\VALIDATION_REPORT_KR.md`: useful independent confirmation of concepts, but notes full live all-4 is still required after latest changes.
- `osint-persona` code scan: useful sidecar features, but not sufficient as primary КР submission.

Strategy verdict: verified. The lowest-risk route to здача КР is a curated submission from `actor-osint-front-СС`, with Codex/osint-persona material used only as explanatory support and roadmap, not as code merge.

## 11. Proposed Final Package Contents

For ZIP or Git repo:

```text
actor-osint-front-СС/
  pipeline/
  benchmark_profiles/
  config/
  templates/
  tests/
  examples/
    sample_run/
    sample_run.zip
  scripts/
  README.md
  VALIDATION_REPORT_KR.md
  NOTES_КР.md
  MASTER_PLAN.md
  DECISIONS.md
  requirements.txt
  Dockerfile
  .env.example
  .gitignore
```

Exclude:

```text
.venv/
.pytest_cache/
__pycache__/
output/old experimental runs/
real .env
raw files with secrets if any
```

Optional include:

```text
course-root/actor-osint-front-СC(ClaudeCode)/*.png
actor-osint-front/docs/KR_STRATEGY_PERSONS_DIAGRAM.html
```

## 12. Next Operational Plan

1. Make a clean copy/export folder from `actor-osint-front-СС`, excluding old output and caches.
2. Verify `examples/sample_run` opens locally: `report.html`, `report_quality.md`, `accounts_graph.html`.
3. Run non-destructive static checks only first: inspect README, requirements, `.env.example`, validation docs.
4. If live API keys/budget are available, run one final controlled live run for the chosen actor and archive it as the new canonical example. If not, keep the already validated sample run.
5. Create final ZIP named according to course format or initialize GitHub repo.
6. Prepare short defense narrative:
   - task direction: persons/social/geolocation;
   - pipeline stages;
   - evidence preservation;
   - quality gates;
   - limitations/blind zones;
   - why outputs are evidence candidates, not final judgments.

## 13. Bottom Line

Для здачі не треба шукати “ідеальний об’єднаний проєкт”. Треба здати найменш ризиковий, найкраще задокументований і вже провалідований package.

Це `actor-osint-front-СС`.

`actor-osint-front` — методологічний донор для майбутньої версії.
`osint-persona` — sidecar для nickname/email/social-account розвідки.
Visual folders — матеріал для пояснювальної діаграми.
