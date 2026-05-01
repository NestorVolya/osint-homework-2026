# Б2 — Граф зв'язків (специфікація для draw.io)

**Суб'єкт:** Чекаль Олексій Георгійович  
**Інструмент:** [draw.io](https://app.diagrams.net/) (браузер, без реєстрації)  
**Вузлів:** 10 · **Ребер:** 11

---

## Колірне кодування

| Колір | Тип вузла |
|---|---|
| 🔵 Синій | PERSON |
| 🟡 Жовтий | ORG / EVENT |
| 🟢 Зелений | LOCATION |
| 🔴 Червоний | SOURCE (артефакт) |

---

## Вузли

| ID | Назва | Тип | Колір |
|---|---|---|---|
| N1 | Чекаль Олексій Георгійович | PERSON | Синій |
| N2 | PanicDesign | ORG | Жовтий |
| N3 | Артос | ORG | Жовтий |
| N4 | ПСТГУ | ORG | Жовтий |
| N5 | Fondazione Russia Cristiana | ORG | Жовтий |
| N6 | Rimini Meeting 2013 | EVENT | Жовтий (темний) |
| N7 | Харків | LOCATION | Зелений |
| N8 | Москва | LOCATION | Зелений |
| N9 | pravmir.ru | SOURCE | Червоний |
| N10 | hramozdatel.ru | SOURCE | Червоний |

---

## Ребра

| Від | До | Тип зв'язку | Впевн. | Джерело |
|---|---|---|---|---|
| N1 | N2 | WORKS_FOR | 8/10 | pravmir.ru |
| N1 | N3 | PARTNERED_WITH | 9/10 | artos.org |
| N1 | N4 | COLLABORATED_WITH | 8/10 | pravmir.ru |
| N1 | N5 | DESIGNED_FOR | 8/10 | russiacristiana.org |
| N1 | N6 | PARTICIPATED_IN | 9/10 | pravmir.ru |
| N1 | N7 | ORIGIN_FROM | 8/10 | pravmir.ru |
| N1 | N8 | BASED_IN | 8/10 | artos.org |
| N5 | N6 | ORGANIZED | 8/10 | russiacristiana.org |
| N3 | N6 | EXHIBITED_AT | 8/10 | artos.org |
| N9 | N1 | PUBLISHED_ABOUT | 9/10 | pravmir.ru (direct) |
| N10 | N1 | PUBLISHED_ABOUT | 9/10 | hramozdatel.ru (direct) |

---

## Інструкція draw.io (покроково)

1. Відкрити [app.diagrams.net](https://app.diagrams.net/) → «Blank Diagram»
2. Для кожного вузла: подвійний клік → ввести назву → змінити колір через правий клік → «Edit Style» → `fillColor=...`
   - Синій: `#dae8fc`  
   - Жовтий: `#fff2cc`  
   - Зелений: `#d5e8d4`  
   - Червоний: `#f8cecc`
3. Для кожного ребра: навести на вузол-джерело → з'явиться стрілка → тягнути до вузла-цілі
4. Підписати ребро: подвійний клік на лінії → ввести `тип · X/10`
   - Приклад: `WORKS_FOR · 8/10`
5. Зберегти → File → Export as → PNG → `graph-chekal.png`
6. Помістити файл у `graphs/`

---

## Аналітичний висновок

Центральний вузол мережі — **N1 (Чекаль)**. Він з'єднує дві географічні зони (Харків/Москва) і три організаційні кластери (православне мистецтво: Артос/ПСТГУ; дизайн: PanicDesign; міжнародна мережа: Russia Cristiana).

Вузол-коннектор між Україною, РФ і Італією: **N6 (Rimini Meeting 2013)** — до нього тягнуться одночасно Чекаль, Артос і Russia Cristiana, що підтверджує H-02 і H-03.

Джерела N9 і N10 — Tier 3 (РПЦ-медіасфера); їх confidence cap = 8/10 як незалежний факт.
