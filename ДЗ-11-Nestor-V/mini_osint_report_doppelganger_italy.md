# Міні-OSINT-звіт: Doppelganger — Italian Campaign

**Курс:** OSINT  
**Студент:** Nestor-V  
**Дата:** 2026-05-19  
**Кейс:** Операція Doppelganger (фокус: Італія, 2022–2024)

---

## 1. Короткий опис

**Doppelganger** (також відома як Recent Reliable News / RRN) — проросійська операція інформаційного впливу, що розпочалась не пізніше лютого 2022 року. Операція стала публічно відомою у вересні 2022 року після [розслідування EU DisinfoLab](https://www.disinfo.eu/doppelganger/).

Суть операції: масове клонування вебсайтів авторитетних медіа (typosquatting), публікація на них сфальшованих матеріалів та їхнє розповсюдження через соціальні мережі.

**Атрибуція:** у грудні 2022 року [Meta вперше публічно атрибутувала](https://transparency.meta.com/sr/Q3-2023-Adversarial-threat-report/) операцію двом російським компаніям — **Social Design Agency (SDA)** та **Structura National Technologies**. У липні 2023 року ЄС запровадив санкції проти цих організацій. У 2024 році [Міністерство фінансів США також санкціонувало](https://transparency.meta.com/integrity-reports-q1-2024/) ці структури.

Операція залишається активною станом на 2024–2025 роки, [адаптуючи методи у відповідь на блокування](https://www.euronews.com/next/2024/09/05/threat-is-ongoing-as-russian-doppelganger-operation-continues-on-x-and-meta-despite-eu-pro).

---

## 2. Основні приклади активності (5 кейсів)

### Кейс 1. Клонування ANSA, La Stampa, La Repubblica (2022–2024)
Серед задокументованих дій — клонування вебсайтів **ANSA** (провідне інф. агентство), **La Stampa** та **La Repubblica** (найбільші щоденні газети Італії). [Домен `ansa.ltd` імітував оригінальний `ansa.it`](https://www.disinfo.eu/doppelganger/) — одне з перших задокументованих клонувань в рамках операції. [Домени La Stampa і La Repubblica зареєстровано між січнем і травнем 2024 року](https://euvsdisinfo.eu/uploads/2024/06/EEAS-TechnicalReport-DoppelgangerEE24_June2024.pdf) напередодні виборів до ЄП.

### Кейс 2. Наратив «санкції проти Росії = катастрофа для Італії» (2022–2023)
Одним із основних меседжів для італійської аудиторії були матеріали, що нагнітали страх перед економічними наслідками антиросійських санкцій. [EU DisinfoLab зафіксував цей наратив](https://www.disinfo.eu/wp-content/uploads/2022/09/Doppelganger-1.pdf) як один із ключових у вересні 2022 року. Мета — формувати суспільний опір підтримці України серед економічно чутливої аудиторії.

### Кейс 3. Рекламні кампанії на Meta (2023)
[Meta виявила щонайменше **98 рекламних оголошень**](https://transparency.meta.com/sr/Q3-2023-Adversarial-threat-report/), що просували проросійський контент Doppelganger у Франції, Німеччині, Польщі та **Італії**. Контент поширювався через фейкові сторінки та вів до клонованих медіасайтів. Облікові записи були видалені Meta до публікації звіту (Q3 2023).

### Кейс 4. Активність під час виборів до Європарламенту (червень 2024)
Упродовж 4–28 червня 2024 року [зафіксовано понад **1 300 проросійських публікацій**](https://www.euronews.com/next/2024/09/05/threat-is-ongoing-as-russian-doppelganger-operation-continues-on-x-and-meta-despite-eu-pro) від мережі Doppelganger на платформі X (колишній Twitter). Загальна кількість переглядів — **4,6 мільйона**. Незважаючи на звернення EDMO до X через Digital Services Act, більшість акаунтів не була заблокована протягом шести тижнів.

### Кейс 5. Координація через VK — підтвердження Italian audience targeting (2024)
[Розслідування Correctiv (липень 2024)](https://correctiv.org/en/fact-checking-en/2024/07/22/inside-doppelganger-how-russia-uses-eu-companies-for-its-propaganda/) виявило внутрішні чати команди Doppelganger у VK. На одному зі скриншотів зафіксовано символ піци поряд з координацією поширення контенту — підтвердження цілеспрямованої роботи з **italian-language контентом**. Технічна інфраструктура (сервери Hetzner у Фінляндії, Aurologic у Німеччині) була спільною для всіх країн, включно з Італією.

---

## 3. Методи роботи

- **Клонування медіасайтів (typosquatting):** реєстрація доменів, схожих на оригінал (`.ltd`, `.online`, `.foo` замість `.it`, `.com`). Серед клонованих: ANSA, Der Spiegel, Le Monde, The Guardian, Fox News, Bild
- **Соціальні мережі:** платна реклама та органічне поширення через Facebook, Instagram, X (Twitter)
- **Обхід систем модерації:** використання символів і пробілів для маскування URL у публікаціях
- **Багатомовний контент:** матеріали створювались окремо для кожної цільової аудиторії, зокрема італійською мовою
- **AI-генерований контент (2024+):** за даними звітів, операція почала використовувати AI для масштабування контентного виробництва
- **Координація через закриті платформи:** VK як канал внутрішньої комунікації між виконавцями

---

## 4. Основні наративи

Наративи операції можна згрупувати у п'ять тематичних кластерів:

### Група 1: Економічний страх
- Санкції проти Росії = зростання цін, рецесія, енергетична криза для Італії та Європи
- Підтримка України = марнування грошей платників податків
- *Механізм:* таргетування на чутливість до інфляції та вартості життя

### Група 2: Дискредитація України
- Зеленський = корумпований, нелегітимний лідер
- Україна = нацистська / failed state
- Заперечення воєнних злочинів (зокрема Бучі)
- *Механізм:* клоновані сайти з фейковими «репортажами»

### Група 3: Антизахідний / антиінституційний
- НАТО = загроза миру, провокатор війни
- ЄС = бюрократія, що жертвує громадянами заради геополітики
- Підтримка євроскептичних і проросійських партій напередодні виборів до ЄП 2024
- *Механізм:* платна реклама на Meta, органічне поширення на X

### Група 4: Підрив довіри до медіа
- Клонування ANSA / La Repubblica / La Stampa — розмивання межі між оригіналом і фейком
- «Мейнстримні медіа брешуть» — перенаправлення до проросійських альтернатив
- *Механізм:* typosquatting + дизайн-клони

### Група 5: Поляризація суспільства
- Міграційна криза = вина ЄС / наслідок підтримки України
- Посилення внутрішніх розколів (інфляція, безпека, ідентичність)
- *Механізм:* мікротаргетинг за соціально-демографічними групами

---

## 5. Таблиця кейсів

| Дата / Період | Кейс / Кампанія | Країна / Аудиторія | Метод | Джерело |
|---|---|---|---|---|
| Лютий–вересень 2022 | Клон ANSA (`ansa.ltd`) — публікація сфальшованих матеріалів | Італія | Typosquatting, fake news site | [EU DisinfoLab, вересень 2022](https://www.disinfo.eu/doppelganger/) |
| 2022–2023 | Наратив «санкції = економічна катастрофа для Італії» | Італія | Multi-platform content, social media | [EU DisinfoLab звіт](https://www.disinfo.eu/wp-content/uploads/2022/09/Doppelganger-1.pdf) |
| 2023 | 98 платних рекламних оголошень на Meta (France/Germany/Poland/Italy) | Італія, ЄС | Paid ads, Facebook/Instagram | [Meta Q3 2023 Adversarial Threat Report](https://transparency.meta.com/sr/Q3-2023-Adversarial-threat-report/) |
| Червень 2024 | 1 300+ публікацій на X під час виборів до ЄП, 4,6 млн переглядів | ЄС / Італія | X/Twitter coordinated posting | [Euronews, 05.09.2024](https://www.euronews.com/next/2024/09/05/threat-is-ongoing-as-russian-doppelganger-operation-continues-on-x-and-meta-despite-eu-pro) |
| Липень 2024 | VK-чати: підтвердження italian-language targeting | Італія | Internal coordination, VK | [Correctiv, 22.07.2024](https://correctiv.org/en/fact-checking-en/2024/07/22/inside-doppelganger-how-russia-uses-eu-companies-for-its-propaganda/) |

---

## 6. Висновок

Кейс Doppelganger у контексті Італії демонструє кілька ключових характеристик сучасних російських інформаційних операцій:

**Масштаб і системність.** Операція не є спонтанною — вона структурована, фінансується комерційними суб'єктами (SDA, Structura), використовує рекламні бюджети та координується через закриті платформи.

**Адаптивність.** Попри санкції (ЄС 2023, США 2024), численні takedowns від Meta та X, операція продовжується, змінюючи домени та тактики. Це ознака стійкої інституційної підтримки.

**Вибір Італії як мети.** Значний євроскептицизм, наявність проросійських політичних сил, чутливість до економічної тематики — все це робить Італію пріоритетною аудиторією для Kremlin-aligned операцій.

**Розмивання інформаційного простору.** Клонування авторитетних медіа (ANSA) спрямоване не лише на поширення конкретних наративів, а й на системне зниження довіри до медіа загалом.

---

## Артефакти

| Файл | Опис |
|---|---|
| `mini_osint_report_doppelganger_italy.md` | Основний звіт (цей файл) |
| `mini_osint_report_doppelganger_italy.html` | HTML-версія звіту з нумерованими посиланнями |
| `sources.md` | Повний список 16 джерел зі статусом перевірки |
| `sources.html` | HTML-версія таблиці джерел |
| `screenshots/` | 16 скріншотів першоджерел (перейменовані за змістом) |

Ключові скріншоти:
- `eu-disinfolab-doppelganger-fake-site-example.png` — приклад клонованого сайту
- `mapfre-2024-09-04-italy-la-repubblica-doppelganger.png` — інцидент La Repubblica, вересень 2024
- `meta-q3-2023-russia-section-cib-rt-accounts-removed.png` — Meta Q3 2023: видалення CIB-мережі
- `correctiv-2024-07-inside-doppelganger-eu-companies.png` — Correctiv: SDA через EU-компанії
- `eeas-report-doppelganger-strikes-back-italy-content-placement.png` — EEAS: Italy content placement

---

## AI-компонент

У роботі AI використовувався як допоміжний інструмент для структурування матеріалів, короткого резюмування джерел, виділення ключових фактів та групування наративів. Пошук джерел виконувався через відкриті вебзапити (WebSearch/WebFetch) до публічних звітів EU DisinfoLab, Meta, Euronews та Correctiv. Усі фактичні твердження перевірені за відкритими джерелами. AI не використовувався як самостійне джерело фактів.

---

## 7. Джерела

1. **EU DisinfoLab** — *Doppelganger: Media clones serving Russian propaganda*, вересень 2022  
   https://www.disinfo.eu/doppelganger/

2. **EU DisinfoLab** — Повний звіт (PDF), вересень 2022  
   https://www.disinfo.eu/wp-content/uploads/2022/09/Doppelganger-1.pdf

3. **EU DisinfoLab** — Doppelganger Hub (агрегатор кампаній)  
   https://www.disinfo.eu/doppelganger-hub/

4. **Meta Transparency Center** — Quarterly Adversarial Threat Report Q3 2023  
   https://transparency.meta.com/sr/Q3-2023-Adversarial-threat-report/

5. **Meta Transparency Center** — Integrity Reports Q1 2024  
   https://transparency.meta.com/integrity-reports-q1-2024/

6. **EUvsDisinfo / EEAS** — *Doppelganger Strikes Back: FIMI Activities Targeting European Parliament Elections*, червень 2024  
   https://euvsdisinfo.eu/uploads/2024/06/EEAS-TechnicalReport-DoppelgangerEE24_June2024.pdf

7. **Euronews** — *'Threat is ongoing' as Russian Doppelganger operation continues on X and Meta despite EU probe*, 5 вересня 2024  
   https://www.euronews.com/next/2024/09/05/threat-is-ongoing-as-russian-doppelganger-operation-continues-on-x-and-meta-despite-eu-pro

8. **Correctiv** — *Inside Doppelganger: How Russia uses EU companies for its propaganda*, 22 липня 2024  
   https://correctiv.org/en/fact-checking-en/2024/07/22/inside-doppelganger-how-russia-uses-eu-companies-for-its-propaganda/
