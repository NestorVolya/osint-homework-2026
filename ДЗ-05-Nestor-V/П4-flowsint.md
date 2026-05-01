# П4 — Flowsint: автоматичне розслідування

**Суб'єкт:** Чекаль Олексій Георгійович  
**Сутність для Flowsint:** `hramozdatel.ru` (домен авторського сайту)  
**Інструмент:** Flowsint, розгорнутий на VPS 93.127.186.188 через `make prod`

---

## Встановлення

```bash
git clone https://github.com/reconurge/flowsint.git /opt/flowsint
cd /opt/flowsint
make prod
```

Запущено 6 контейнерів: `flowsint-app-prod`, `flowsint-api-prod`, `flowsint-celery-prod`, `flowsint-postgres-prod`, `flowsint-redis-prod`, `flowsint-neo4j-prod`.  
Доступ через SSH tunnel: `ssh -N -L 5173:localhost:5173 -L 5001:localhost:5001 root@93.127.186.188`

---

## Процес розслідування

1. Зареєстровано акаунт на `http://localhost:5173/register`
2. Створено нове розслідування: `hramozdatel`
3. Додано сутність: `hramozdatel.ru` (тип: domain)
4. Запущено всі доступні збагачувачі:
   - `domain_to_ip` — DNS lookup
   - `domain_to_subdomains` — пошук субдоменів
   - `domain_to_history` — WHOIS: власник, email, організація
   - `domain_to_root_domain` — кореневий домен
   - `domain_to_asn` — помилка: відсутній `PDCP_API_KEY` (ProjectDiscovery)

---

## Результат: 8 вузлів

| Вузол | Тип | Enricher |
|---|---|---|
| `hramozdatel.ru` | domain | початкова сутність |
| `www.hramozdatel.ru` | domain | domain_to_subdomains |
| `sub.hramozdatel.ru` | domain | domain_to_subdomains |
| `176.57.65.127` | ip | domain_to_ip |
| `https://hramozdatel.ru/` | website | domain_to_history |
| `hramozdatel.ru@domain.com` | email | domain_to_history |
| `Алексей Чекаль` | individual | domain_to_history (WHOIS) |
| `hramozdatel.ru` | whois | domain_to_history |

**Ребра:** HAS_SUBDOMAIN, RESOLVES_TO, HAS_WEBSITE, IS_RELATED_TO, HAS_WHOIS

---

## Скріншоти

- `graphs/Screenshot_1.png` — граф після збагачення hramozdatel.ru
- `graphs/Screenshot_2.png` — панель enrichers

---

## Нові вузли для подальшого слідування

- `176.57.65.127` → можна запустити `ip_to_asn`, `ip_to_geolocation`
- `hramozdatel.ru@domain.com` → email enrichers
