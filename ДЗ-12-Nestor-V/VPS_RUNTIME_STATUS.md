# DZ-12 GroupInt VPS Runtime Status

Дата фіксації: 2026-05-25.

Цей файл фіксує фактичний VPS-варіант для ДЗ-12. Він замінює локальний Docker Desktop із лекційного чек-листа, але зберігає логіку GroupInt -> Neo4j -> Gephi.

## Схема

| Компонент | Значення |
|---|---|
| VPS alias | `hostinger-vps` |
| VPS host | `srv1621610.hstgr.cloud` |
| VPS шлях | `/docker/groupint` |
| GroupInt public route | `https://groupint.srv1621610.hstgr.cloud` |
| Neo4j Browser public route | `https://neo4j-groupint.srv1621610.hstgr.cloud/browser/` |
| Bolt для Gephi | `neo4j://srv1621610.hstgr.cloud:17687` |
| Web auth | Traefik Basic Auth |
| Neo4j auth | `neo4j` + пароль з `GROUPINT_NEO4J_PASSWORD` |
| Local secrets source | `D:\servers\.env` |
| Remote runtime env | `/docker/groupint/.env` |
| GroupInt Telegram secrets | `/docker/groupint/.streamlit/secrets.toml` |
| Compose файл | `/docker/groupint/docker-compose.vps.yml` |

## Відмінності від уроку

- Локальний `./scripts/up-desktop.sh` не використовується.
- `http://localhost:18501` замінено на public GroupInt route через Traefik.
- `http://localhost:17474` замінено на Neo4j Browser route через Traefik.
- `neo4j://localhost:17687` замінено на `neo4j://srv1621610.hstgr.cloud:17687`.
- У Gephi треба використовувати Neo4j auth, не `No auth`.
- `http://127.0.0.1:8080/health` належить до gephi-ai desktop plugin, не до VPS GroupInt.

## Перевірено

- [x] `/docker/groupint` існує на VPS.
- [x] GroupInt checkout розгорнуто на VPS.
- [x] `groupint-streamlit` запущений і має Docker health `healthy`.
- [x] `groupint-neo4j` запущений.
- [x] Streamlit health всередині контейнера повертає `ok`.
- [x] Neo4j приймає auth через `cypher-shell`.
- [x] Traefik route для GroupInt без Basic Auth повертає `401`.
- [x] Traefik route для Neo4j Browser без Basic Auth повертає `401`.
- [x] HTTP route для GroupInt повертає redirect на HTTPS.
- [x] Traefik Basic Auth password ротовано після діагностики; актуальне значення зберігається тільки в `D:\servers\.env`.
- [ ] Public ingress з локальної машини до `srv1621610.hstgr.cloud:80/443/17687` відкритий.

## Поточний блокер

З VPS Traefik слухає `80` і `443`, а Docker proxy слухає `17687`. Локальний firewall на VPS не блокує ці порти: `ufw` inactive, `iptables INPUT ACCEPT`.

З цієї робочої машини підключення до `srv1621610.hstgr.cloud` на портах `80`, `443` і `17687` зараз не проходить. Оскільки так само недоступні вже наявні public routes на цьому ж хості, проблема схожа не на GroupInt compose, а на provider/VPC ingress або зовнішній firewall перед VPS.

## Наступний gate

У Hostinger/Docker Manager відкрити inbound для:

- `80/tcp`;
- `443/tcp`;
- `17687/tcp`.

Після цього повторити public перевірку:

```powershell
Test-NetConnection srv1621610.hstgr.cloud -Port 443
Test-NetConnection srv1621610.hstgr.cloud -Port 17687
```

Після проходження gate:

- [ ] Відкрити `https://groupint.srv1621610.hstgr.cloud`.
- [ ] Пройти Traefik Basic Auth.
- [ ] У GroupInt створити Telegram client / OTP / saved session.
- [ ] Відкрити `https://neo4j-groupint.srv1621610.hstgr.cloud/browser/`.
- [ ] Пройти Traefik Basic Auth і Neo4j auth.
- [ ] У Gephi імпортувати через `neo4j://srv1621610.hstgr.cloud:17687` з Neo4j auth.
