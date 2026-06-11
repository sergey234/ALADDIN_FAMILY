# L3 Smoke Contract — обязательный для ML-проверок

**Версия:** 1.0 · **2026-06-09**  
**Связано:** `docs/OPS_ANTI_REGRESSION_GATES.md`, `ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md`

---

## Запрещённые критерии PASS

- `GET /api/health` → ok **без** проверки тела security endpoints
- HTTP 200 / 403 **без** анализа JSON
- `{"success":true,"result":{"status":"success"}}` — **всегда FAIL** для security
- `version` содержит `mock-real-protection` — **FAIL**
- `source` ∈ `sfm_mock`, `mock`, `sfm_stub` — **FAIL**
- `result: ""` — **FAIL**
- OpenAPI path отсутствует, но wildcard 200 — **FAIL**
- EXTENDED_138 `verify=ok` только по HTTP code — **FAIL**

---

## Уровень A — SFM (:8003)

```bash
ssh -i ~/.ssh/aladdin_server root@149.154.65.180

curl -s http://127.0.0.1:8003/api/health | python3 -c "
import sys,json
d=json.load(sys.stdin)
assert d.get('sfm_loaded') is True, 'sfm_loaded missing/false'
assert d.get('functions_count',0) >= 1000, 'registry too small'
print('A-OK', d)
"

curl -s -X POST http://127.0.0.1:8003/api/execute \
  -H 'Content-Type: application/json' \
  -d '{"function":"__nonexistent_test_fn__","params":{}}' | python3 -c "
import sys,json
d=json.load(sys.stdin)
assert d.get('success') is False or d.get('error'), 'unknown fn must not succeed'
print('A-unknown-OK')
"
```

---

## Уровень B — API (через https://aladdin-ai.ru или localhost:8002)

1. `POST /api/auth/register-device` → JWT  
2. Для antifake: `POST /api/antifake/check/text` `{"text":"..."}`  

**PASS если:**
- `verdict` ∈ `likely_fake`, `uncertain`, `likely_real`
- `source` ∉ mock list
- нет `mock-real-protection` в любом поле

---

## Уровень C — L2 toggles

```bash
# POST /api/protection/settings categories.deepfakes=true
# GET /api/protection/settings → deepfakes MUST be true
# POST /api/protection/enable {"categoryId":"deepfakes"} → 200 (not 500)
```

---

## Уровень D — iOS L3 (после backend PASS)

- TestFlight build **только** после всех batch (см. handoff)
- Скриншот Hub с вердиктом + build number в `docs/release/gates/`

---

## Отчёт ML

Писать в `docs/release/gates/security-l3-report.json`:

```json
{
  "block": "SFM-WIRE",
  "timestamp": "ISO8601",
  "level_a": "pass|fail",
  "level_b": "pass|fail",
  "level_c": "pass|fail",
  "level_d": "pending|pass|fail",
  "evidence": ["curl output snippet or test name"]
}
```

**Без файла evidence — отчёт недействителен.**
