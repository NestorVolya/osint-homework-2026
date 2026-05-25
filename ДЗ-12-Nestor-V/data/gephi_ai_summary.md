## 9. Gephi AI Analysis (MCP)

**Інструмент:** Gephi MCP API v2.0.0 (`http://127.0.0.1:8080`), плагін `gephi-ai` by Matt Artz (github.com/MattArtzAnthro/gephi-ai).

**Що виконано:**
- Перевірено Gephi MCP health → `success: true`
- (Re-)обчислено через Gephi Statistics API: Modularity / Community Detection, Degree, Weighted Degree, PageRank, Betweenness Centrality
- Вузли розфарбовані за `Modularity Class` / `modularity_class` (partition color, auto-palette)
- Розмір вузлів — за `weighted degree` (min 15 / max 80)
- Товщина ребер — за `Weight`
- ForceAtlas 2 протестовано, але через вагу 3235 два hub-вузли злипалися; фінальний PNG зроблено після ручного радіального layout, де кластери рознесені по квадрантах
- Експортовано PNG 1920×1080

**Підтверджені метрики:**

| Метрика | Значення |
|---|---|
| Вузли | 70 |
| Ребра | 68 |
| Кластери (modularity class) | 4 після Gephi re-computation: 0(38), 3(20), 1(6), 2(6) |
| Modularity score (Gephi) | — |

**Топ-10 вузлів за Weighted Degree (live з Gephi API):**

| # | Label | Кластер | Weighted Degree | PageRank |
|---|---|---|---:|---|
| 1 | `Republic_Of_GaGauZia` | 0 (Gagauzia-ядро, 38 вузлів) | 3404 | 0.01362 |
| 2 | `Republic_Of_GaGauzia_MD` | 0 (Gagauzia-ядро, 38 вузлів) | 3235 | 0.01393 |
| 3 | `MoldovaAdevarata` | 0 (Gagauzia-ядро, 38 вузлів) | 87 | 0.01393 |
| 4 | `MoldovaPolitics` | 3 | 66 | 0.01362 |
| 5 | `primulinmd` | 2 (Moldova-сегмент, 26 вузлів) | 14 | 0.01682 |
| 6 | `gagauznewsmd` | 2 (Moldova-сегмент, 26 вузлів) | 12 | 0.01362 |
| 7 | `wtfmoldova` | 3 | 11 | 0.01420 |
| 8 | `contractMObot` | 0 (Gagauzia-ядро, 38 вузлів) | 9 | 0.01393 |
| 9 | `turan_express` | 3 | 9 | 0.01420 |
| 10 | `gagayzineodinoki` | 0 (Gagauzia-ядро, 38 вузлів) | 8 | 0.01393 |

**Betweenness Centrality — діагностика:**

Gephi обчислив BC = 0.0 для всіх вузлів. Це типова картина для hub-and-spoke топології: жоден вузол не лежить на найкоротшому шляху між іншими, бо більшість вузлів є листами (тільки incoming або тільки outgoing ребра). Формальних bridge-вузлів у сенсі betweenness у поточній `ENDORSES`-моделі немає.

**Основні кластери:**
- **Кластер 0** (≥30 вузлів): Gagauzia-ядро. Hub: `Republic_Of_GaGauZia`. Домінує за вагою (wd≈3404).
- **Кластер 2** (Moldova-сегмент): Hub: `MoldovaPolitics` (wd≈66). Менші ваги.
- **Кластер 1** (Периферія): Hub: `pridnestrovec`. Майже без outgoing endorsements.
- **Кластер 3** (з'явився при re-computation): `MoldovaPolitics`, `wtfmoldova`, `turan_express` — можливо, Gephi виділив їх у окремий підкластер; CSV мав 3 кластери, Gephi re-run дав 4.

**Семантичні мости між кластерами:**
Формальних bridge-вузлів (betweenness > 0) немає через star-топологію. Семантичний місток: `gagauznewsmd` — присутній у Moldova-сегменті, але тематично пов'язаний із Gagauzia-контентом кластера 0.

**Аномально сильне ребро:**

`Republic_Of_GaGauZia -> Republic_Of_GaGauzia_MD`, `weight=3235`, `message_id=71800`. Інтерпретація обережна: це може бути багато повторень, агрегована вага або особливість парсингу GroupInt для одного/кількох повідомлень.

**Скріншот:** `screenshots/17-gephi-ai-analysis-export.png`
**Gephi проєкт:** `screenshots/telegram-endorsements-expanded-gephi-ai.gephi`
