# SFM — быстрый старт для ML (30 секунд)

**Не путайся:** SFM **есть** на сервере. Проблема была в **пути import** и **ложном health**, не в отсутствии кода.

---

## Шаг 1 — одна команда

```bash
ssh -i ~/.ssh/aladdin_server root@149.154.65.180 \
  'bash /opt/aladdin-backend/docs/server/sfm_truth_check.sh 2>/dev/null || curl -s http://127.0.0.1:8003/api/sfm/status'
```

## Шаг 2 — интерпретация

| Поле | OK | Проблема → задача |
|------|-----|-------------------|
| `sfm_loaded` | `true` | `false` → **B-SFM-W03**…**W04** |
| `registry_count` | ≥ 1000 | < 1000 → **B-SFM-W06** |
| `fallback_mode` | `false` | `true` → **B-OPS-03**, SFM-WIRE |
| `code_path` | содержит `app/security/safe_function_manager.py` | иначе → forensic |
| `PYTHONPATH` | **`app` перед `backend`** | иначе shadow `security/` → W03 |

## Шаг 3 — что НЕ делать

- ❌ Искать только `security/safe_function_manager.py`
- ❌ Верить `functions_count: 1074` без `sfm_loaded`
- ❌ Считать `status:success` за работу агента

## Полная документация

`docs/SFM_SINGLE_SOURCE_OF_TRUTH.md`
