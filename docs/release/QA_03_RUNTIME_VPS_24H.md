# B-QA-03 (runtime) — VPS 24h mock grep

**Дата:** 2026-06-11  
**Связано:** `QA_03_MOCK_GREP_AUDIT.md` (iOS static ✅)

## Проверка

```bash
ssh root@149.154.65.180
for u in aladdin-api aladdin-backend nginx; do
  journalctl -u "$u" --since "24 hours ago" | grep -cE "mock-real-protection|sfm_mock|sfm_stub"
done
```

## Результат 2026-06-11 (initial)

| Service | Hits (24h) |
|---------|------------|
| `aladdin-api` | **0** |
| `aladdin-backend` | **0** |
| `nginx` | **0** |

## Re-run at TestFlight prep (R-08…10 bundle)

**Команда:** `scripts/run_hub_demo_vps_smoke.sh` (includes mock grep tail)

| Service | Hits (24h) | Re-run |
|---------|------------|--------|
| `aladdin-api` | **0** | ✅ 2026-06-11 |
| `aladdin-backend` | **0** | ✅ 2026-06-11 |
| `nginx` | **0** | ✅ 2026-06-11 |

**Evidence:** `docs/release/gates/hub-demo-smoke-report.json`

**Verdict:** B-QA-03 runtime **PASS** — mock markers absent in prod service logs (24h window).
