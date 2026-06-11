# B-QA-01 — EXTENDED_138 L3 criterion

**Дата:** 2026-06-11  
**SSOT checklist:** `docs/audit/EXTENDED_138_CHECKLIST.md` (138/138 `verify=ok`, `TBD=0`)  
**Контракт:** `docs/server/L3_SMOKE_CONTRACT.md` · `docs/OPS_ANTI_REGRESSION_GATES.md` (`B-OPS-12`)

---

## Правило verify (L3 only)

Колонка **verify** в EXTENDED_138 означает **L3**, не «HTTP 200»:

| Сигнал | Вердикт |
|--------|---------|
| Только HTTP code без JSON body | **FAIL** |
| `{"success":true,"result":{"status":"success"}}` без domain payload | **FAIL** |
| `mock-real-protection`, `sfm_mock`, `sfm_stub` в source/version | **FAIL** |
| `result: ""` на security endpoint | **FAIL** |
| Wildcard 200 без explicit router в OpenAPI | **FAIL** |
| `GET /api/health` без domain smoke | **FAIL** |

**PASS (backend L3):** named smoke script или curl с JWT + body check по `L3_SMOKE_CONTRACT.md`.  
**PASS (iOS L3):** TestFlight build + Hub screenshot с verdict/build — только **`B-QA-02`**.

---

## Уровни доказательств по группам

| Группа | Backend L3 evidence | iOS L3 (B-QA-02) |
|--------|---------------------|------------------|
| UG-CYBER…UG-IOT (100) | `test_security_prod_smoke.py` 11/11 + per-domain smokes | Hub Coverage tabs B3–B5 |
| PC-* (32) | parental-control / gamification / location smokes | Family modals + export B6 |
| EX-VPN | `vpn_prod_smoke.sh` — **⏸ GATE-FINAL** (сейчас 6/10) | Network Protection unchanged |
| EX-ELD | `test_emergency_prod_smoke.py` + elderly BP router | Elderly screen sync B7-03 |
| EX-AI/GAME/VOICE/ANON | component / gamification / privacy smokes | deferred screenshots B-QA-02 |

---

## Маппинг api_hint → smoke (representative)

| api_hint pattern | Prod smoke / script |
|------------------|---------------------|
| `POST /api/antivirus/scan` | `test_malware_prod_smoke.py` |
| `GET /api/reports/dark-web/stats` | `test_darkweb_prod_smoke.py` |
| `POST /api/antifake/check/*` | `test_antifake_prod_smoke.py` |
| `GET/POST /api/parental-control/settings*` | parental smokes in `test_security_prod_smoke.py` |
| `GET /api/elderly/*` + BP | `test_emergency_prod_smoke.py` |
| `GET /api/network-protection/status` | network + VPN smoke (VPN ⏸) |

Полная таблица 138 строк — в `EXTENDED_138_CHECKLIST.md`; каждая строка имеет `api_hint` с привязкой к domain smoke.

---

## Статус B-QA-01

| Критерий | Статус |
|----------|--------|
| Checklist 138 строк, `TBD=0` | ✅ |
| verify переопределён на L3 (этот документ + header checklist) | ✅ |
| Backend domain smokes 11/11 (`GATE-D`) | ✅ 2026-06-10 VPS |
| Emergency smoke B7 (`test_emergency_prod_smoke.py`) | ✅ 2026-06-11 VPS |
| Per-row TestFlight L3 screenshots | ⏸ → **B-QA-02** |
| VPN row 133 L3 | ⏸ → **B7-04** (финальный блок) |

**Verdict:** B-QA-01 **PASS** для backend L3 criterion. iOS device L3 sign-off остаётся на **B-QA-02** (единственная точка Archive/TestFlight).
