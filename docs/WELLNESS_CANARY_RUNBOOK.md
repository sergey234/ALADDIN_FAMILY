# Wellness Canary Rollout Runbook (p3-10)

> **Цель:** безопасный rollout Wellness 5% → 25% → 100% без regression по crisis / consent.

---

## 1. Флаги (VPS `.env`)

| Flag | Canary 5% | 25% | 100% |
|------|-----------|-----|------|
| `FEATURE_WELLNESS_ENABLED` | 1 | 1 | 1 |
| `FEATURE_WELLNESS_ORCHESTRATOR` | 0→1 | 1 | 1 |
| `FEATURE_WELLNESS_JUNG` | 0 | 1 | 1 |
| `FEATURE_WELLNESS_REFLECTIVE` | 0 | 1 | 1 |
| `WELLNESS_CANARY_PERCENT` | 5 | 25 | 100 |

---

## 2. Шаги

1. **Pre-flight:** `./scripts/verify_wellness_prod.sh https://aladdin-ai.ru` (10/10)
2. **Deploy:** `./scripts/deploy_wellness_p1.sh root <host> <ssh_key>`
3. **Smoke:** `PYTHONPATH=. python3 scripts/vps_smoke_wellness.py`
4. **Crisis gate:** убедиться `/api/wellness/crisis/status` + 48h cooldown на staging JWT
5. **Canary cohort:** `wellness_canary.py` — `hash(user_id) % 100 < WELLNESS_CANARY_PERCENT` (см. `GET /api/wellness/canary/status`)
6. **Monitor 24h:** 5xx rate, crisis L3 count, premium blocked count
7. **Rollback:** `FEATURE_WELLNESS_ORCHESTRATOR=0`, restart `aladdin-api`

---

## 3. KPI (48h окно)

- Crisis L3 → premium blocked: **100%** (p3-12)
- Check-in success rate ≥ baseline − 2%
- No new App Review health claims in metadata

---

*Связано: p3-04, p3-12, `deploy_wellness_p1.sh`*
