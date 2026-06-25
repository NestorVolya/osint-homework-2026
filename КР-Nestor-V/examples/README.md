# examples/

Приклад artifacts із тестового запуску pipeline.

> **Увага:** поточний `sample_run/` згенерований на benchmark actor (Олексій Чекаль).
> Перед здачею КР — замінити на run з фінальним КР actor (ПІБ надає студент).

## Команда, якою згенеровано

```powershell
$env:DOTENV_PATH = "/path/to/secrets.env"
python -m pipeline.run `
  --seed "Олексій Чекаль" `
  --seed_type fullname `
  --profile benchmark_profiles/ua_cultural_ru_sphere.yaml
```

**Run ID:** `2026-05-29_01-24-51`  
**Sources:** 48 | **Health Score:** 1.00 | **Gates:** 5/5 PASS | **Runtime:** 79.3s

## Вміст sample_run/

```
sample_run/
  report/
    report.html           ← HTML-досьє (таймлайн, акаунти, висловлювання, граф)
    report_quality.md     ← 7-секційний аналітичний MD-звіт
    accounts_graph.html   ← інтерактивний граф акаунтів (pyvis)
  quality_report.json     ← JSON метрики: corpus_health_score, 5 gates
```

Повний ZIP-архів з `records.sqlite` і raw API-відповідями:
запустіть pipeline локально — архів генерується автоматично в `output/`.
