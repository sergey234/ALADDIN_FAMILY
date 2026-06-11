# B-QA-05 — Prod registry ≥1074 + weekly smoke

**Дата:** 2026-06-11  
**Скрипт:** `docs/server/sfm_truth_check.sh`  
**Timer:** `aladdin-sfm-prod-smoke.timer` (15m) · `aladdin-security-prod-smoke.timer` (15m, B-OPS-22)

---

## VPS run (2026-06-11)

```bash
ssh -i ~/.ssh/aladdin_server root@149.154.65.180 \
  'bash /opt/aladdin-backend/docs/server/sfm_truth_check.sh'
```

**Result:** `overall: PASS`

| Field | Value |
|-------|-------|
| `registry_count` | **1074** |
| `runtime_functions_count` | 1068 |
| `sfm_loaded` | True |
| `fallback_mode` | False |
| `code_path` | `/opt/aladdin-backend/app/security/safe_function_manager.py` |
| `stub_at_root` | false |

---

## Weekly / periodic criteria

| Check | Interval | PASS |
|-------|----------|------|
| `sfm_truth_check.sh` | 15m systemd | overall PASS, registry ≥1000 |
| `test_security_prod_smoke.py` | 15m (B-OPS-22) | domains_pass 11/11 |
| Manifest sync | repo `data/sfm/function_registry.manifest.json` | count 1074 |

**Запрещено:** отчёты «1074 ok» без живого `sfm_truth_check` на процессе :8003.

---

## Статус

**Verdict:** B-QA-05 **PASS** (registry 1074, truth check PASS 2026-06-11).
