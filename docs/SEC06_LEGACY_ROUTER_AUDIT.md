# SEC-06 — Legacy vs Explicit Router Audit (Plan–Fact)

**Дата:** 2026-06-09 · **Batch:** B1-12 + sec-06  
**Prod:** `149.154.65.180` · API `:8002`  
**Связано:** `main.py`, `docs/server/test_security_prod_smoke.py`, `docs/server/test_security_openapi_prod_smoke.py`

---

## Цель

Один canonical handler на каждый **iOS/smoke path**. Legacy `security/api/routers/*` остаётся только там, где explicit ещё не покрывает уникальные endpoints.

---

## Правило приоритета (runtime)

```
1. app/routers/* (explicit B1) — регистрируется ПЕРВЫМ в main.py
2. security/api/routers/* (legacy) — вторым, только уникальные path
3. compat (misc_other_compat, parental_compat) — третьим
4. wildcard /api/{path} — 404 для critical_prefixes (B0-05)
```

FastAPI: **первый зарегистрированный route побеждает** на совпадающем path+method.

---

## Tier-таблица (plan → fact)

| Tier | Действие | Роутеры | Статус |
|------|----------|---------|--------|
| **A DISABLED** | Полностью не подключаем | `iot_router`, `components_router` | ✅ B1-07, B1-08 |
| **B SKIP legacy prefix** | Explicit заменил весь URL-prefix | `location_bubble_router` (`/api/location/bubble` → explicit `/api/location-bubble`) | ✅ SEC-06 |
| **C COLLISION hidden** | Path overlap; legacy `include_in_schema=False` | parental monitoring/detail+events, identity `/detect`, darkweb `/check`, misc `/malware/threats` | ✅ B1-11 |
| **D KEEP dual** | Разные path на одном prefix | `data_cleanup`, `identity`, `darkweb`, `parental_control` (кроме monitoring) | ✅ документировано |
| **E MIGRATE later** | Уникальные legacy path → перенести в explicit, потом отключить | см. §Backlog | ⬜ BATCH 2+ |

---

## Path-коллизии (5 штук) — explicit побеждает

| Method | Path | Winner | Legacy в OpenAPI |
|--------|------|--------|------------------|
| POST | `/api/darkweb/check` | `app/routers/darkweb.py` | hidden |
| POST | `/api/identity-theft/detect` | `app/routers/identity_theft.py` | hidden |
| GET | `/api/parental-control/monitoring/detail` | `app/routers/parental_monitoring.py` | hidden |
| POST | `/api/parental-control/monitoring/events` | `app/routers/parental_monitoring.py` | hidden |
| GET | `/api/malware/threats` | `app/routers/malware.py` | hidden (compat runtime dead on this path) |

---

## Explicit routers (B1) — plan/fact

| ID | Router | Prefix | Prod smoke | OpenAPI tag |
|----|--------|--------|------------|-------------|
| B1-01 | `antifake.py` | `/api/antifake` | ✅ | antifake |
| B1-02 | `darkweb.py` | `/api/darkweb` | ✅ | darkweb |
| B1-03 | `identity_theft.py` | `/api/identity-theft` | ✅ | identity-theft |
| B1-04 | `data_cleanup.py` | `/api/data-cleanup` | ✅ | data-cleanup |
| B1-05 | `location_bubble.py` | `/api/location-bubble` | ✅ | location-bubble |
| B1-06 | `malware.py` + `antivirus.py` | `/api/malware`, `/api/antivirus` | ✅ | malware, antivirus |
| B1-07 | `phishing.py` + `components.py` | `/api/phishing`, `/api/components` | ✅ | phishing, components |
| B1-08 | `iot.py` | `/api/iot` | ✅ | iot |
| B1-09 | `mobile_security.py` | `/api/mobile` | ✅ | mobile-security |
| B1-10 | `parental_monitoring.py` | `/api/parental-control/monitoring/*` | ✅ | parental-monitoring |
| B1-11 | OpenAPI audit | 32 routes | ✅ | `test_security_openapi_prod_smoke.py` |
| B1-12 | All domains | orchestrator | ✅ | `test_security_prod_smoke.py` |

---

## Legacy-only endpoints (нельзя отключать без миграции)

### dark_web_monitoring_router (prefix `/api/darkweb`)

- `GET /health`, `GET /status`, `GET /breaches`
- `POST /start-monitoring`, `POST /stop-monitoring`

### identity_theft_protection_router

- `POST /monitor-snils`, `POST /monitor-credit` (legacy path, не `/monitor/credit`)
- `GET /alerts`, `POST /consent`, `POST /revoke-consent`, …

### data_cleanup_router

- `POST /scan`, `POST /remove`, `GET /preferences`, `POST /periodic-scan`, …

### parental_control_router (~40 paths)

- stats, settings, geofences, reports, dns-config, bypass — **кроме** monitoring (explicit)

### misc_other_compat

- devices, quarantine, protection/threats — **кроме** `/api/malware/threats` (explicit)

---

## Backlog SEC-06 Phase 2 (следующая ML-система)

| ID | Задача | Приоритет |
|----|--------|-----------|
| `SEC-06-P2-01` | Мигрировать legacy darkweb `/breaches` → explicit или 410 | P2 |
| `SEC-06-P2-02` | Unify identity `/monitor-credit` vs `/monitor/credit` | P2 |
| `SEC-06-P2-03` | Deprecate `/api/location/bubble` → 301/410 doc | P2 |
| `SEC-06-P2-04` | Split parental_control: monitoring out of mega-router | P2 |
| `SEC-06-P2-05` | misc_other_compat: devices → dedicated router | P3 |

---

## Проверка после изменений

```bash
ssh -i ~/.ssh/aladdin_server root@149.154.65.180
cd /opt/aladdin-backend
/opt/aladdin-backend/venv/bin/python3 docs/server/test_security_prod_smoke.py
# ожидаем: "pass": true, domains_pass: 11
```

---

## Evidence file

`docs/release/gates/security-l3-report.json` → блок `GATE-D-BATCH1`, `OPENAPI-SECURITY`, domain `*-BACKEND` blocks.
