# OSINT Homework — Nestor V

Домашні завдання курсу OSINT-AI-2026. Кейс: Чекаль Олексій Георгійович.

## Зміст

| Папка | ДЗ | Опис |
|---|---|---|
| [ДЗ-02-Nestor-V/](ДЗ-02-Nestor-V/) | ДЗ-02 | Промптинг, RAG, захист від ін'єкцій, LLM Guard |
| [ДЗ-03/](ДЗ-03/) | ДЗ-03 | MindsDB + ArkhamMirror SHATTERED |
| [ДЗ-04-Nestor-V/](ДЗ-04-Nestor-V/) | ДЗ-04 | Mini-pipeline: Crawl4AI + Playwright + Prometheus (risu.ua) |
| [ДЗ-05-Nestor-V/](ДЗ-05-Nestor-V/) | ДЗ-05 | Entity Resolution, граф зв'язків, Flowsint (🔵+🔴) |
| [ДЗ-06-Nestor-V/](ДЗ-06-Nestor-V/) | ДЗ-06 | Теорія графів: патентний граф БЕК, Gephi modularity, LLM cluster descriptions (🔵+🔴) |

## Середовище та архітектура

### Принцип: Local = розробка, VPS = виконання

| | Local (Windows 10) | VPS (Ubuntu 24.04) |
|---|---|---|
| **Залізо** | i5-6500 · 16GB RAM · GTS 450 | 2 vCPU · 8GB RAM · 96GB SSD |
| **Роль** | Аналіз, написання, git | 24/7 сервіси, Docker |
| **Обмеження** | Локальні LLM неможливі (969MB VRAM) | dev/staging середовище |
| **Доступ до VPS** | SSH port forwarding | — |

### Стан по ДЗ

| ДЗ | Local | VPS |
|---|---|---|
| ДЗ-02 | RAG, промптинг, LLM Guard | — |
| ДЗ-03 | MindsDB Studio (Docker Desktop) | — |
| ДЗ-04 | Розробка, git push | Crawl4AI pipeline (Docker) |
| ДЗ-05 🔵 | Entity table, pyvis граф, collision | — |
| ДЗ-05 🔴 | SSH tunnel → браузер | Flowsint (`make prod`, 6 контейнерів) |
| ДЗ-06 🔵🔴 | Gephi + Python (networkx, pandas) | — |

### Стек

Local: Python · pyvis · networkx · pandas · Gephi · git  
VPS: Docker · Traefik · Flowsint · Crawl4AI · n8n · PostgreSQL + pgvector
