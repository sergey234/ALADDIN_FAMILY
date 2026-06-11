# Ops: анти-регрессия SFM + честные проверки для ML

**Цель:** после реализации плана ничего не «слетает»; ML-система **не может** отчитаться «работает» без L3-доказательства.

**Онбординг:** не меняем до COPY batch.

---

## 1. Почему ломалось и как не допустить снова

| Причина | Защита (обязательно внедрить) | Batch |
|---------|-------------------------------|-------|
| `start_sfm_core_http` import fail → `sfm=None` silent | **Startup gate:** процесс не healthy, если SFM class не loaded | `B-OPS-01` |
| Health врёт `functions_count:1074` | **Honest health:** count = `len(registry)` из файла | `B-OPS-02` |
| `{"status":"success"}` на любой fn | **503** если fn не в registry / handler missing | `B-OPS-03` |
| `deploy_optimized_sfm.sh` mock | **Запрет** скриптов с OptimizedSFM в prod deploy runbook | `B-OPS-04` |
| Registry перезаписан пустым init | Registry write только через `register_*.py` + backup before write | `B-OPS-05` |
| PYTHONPATH / symlink | **systemd Environment=** + preflight в CI | `B-OPS-06` |
| Wildcard маскирует 404 | Security paths → explicit router only | `B0-05` |
| ML smoke = HTTP 200 | **L3 smoke contract** (см. §2) | `B-OPS-07` |
| Нет мониторинга | Timer каждые 15m + alert Telegram ops | `B-OPS-08` |

---

## 2. Контракт проверки для ML-систем (обязательный)

Любая ML-проверка **PASS** только если **все** условия:

### Уровень A — инфра (SFM)

```bash
# 1. SFM реально loaded (не None)
curl -s http://127.0.0.1:8003/api/health | jq -e '.sfm_loaded == true'

# 2. Честный count
curl -s http://127.0.0.1:8003/api/health | jq -e '.functions_count >= 1000'

# 3. Неизвестная функция → 503, НЕ success
curl -s -X POST http://127.0.0.1:8003/api/execute \
  -d '{"function":"__nonexistent_fn__","params":{}}' | jq -e '.success == false'
```

### Уровень B — API (security paths)

```bash
# JWT register-device → token
# POST /api/antifake/check/text {"text":"..."}
# PASS если:
#   - HTTP 200
#   - verdict in [likely_fake, uncertain, likely_real]
#   - source != sfm_mock
#   - version НЕ содержит mock-real-protection
#   - result НЕ пустая строка
```

### Уровень C — L2 (toggles)

```bash
# POST protection/settings deepfakes:true
# GET protection/settings → deepfakes MUST be true
```

### Уровень D — L3 (TestFlight / manual)

- Пользователь видит вердикт на экране Hub
- Скриншот + build number в `docs/release/gates/`

**Запрещённые критерии PASS:** только `GET /api/health`, только HTTP code, 404 в functional runner, `status:success` без verdict.

Дополнить: `ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md` § PRODUCTION HARD RULE ссылкой на этот файл.

---

## 3. CI/CD и deploy gates (чтобы не слетало)

| Gate | Когда | Действие при fail |
|------|-------|-------------------|
| **Pre-deploy** | перед rsync | `scripts/preflight_sfm.py` — import SFM, registry ≥1000 | block deploy |
| **Post-deploy** | после restart | `docs/server/sfm_health_check.sh` L3 version | rollback + alert |
| **Every 15m** | systemd timer | `aladdin-sfm-prod-smoke.timer` (новый) | Telegram ops |
| **Every 6h** | timer | full security smoke all domains | ticket |
| **On registry change** | register script | auto-backup `function_registry.json.TIMESTAMP` | — |
| **No mock deploy** | CI grep | block commit with `OptimizedSFM` + `mock-real-protection` in `start_sfm*` | block merge |

---

## 4. Единый источник правды (файлы на сервере)

| Файл | Роль |
|------|------|
| `/opt/aladdin-backend/data/sfm/function_registry.json` | Каталог функций (не перезаписывать init'ом) |
| `/opt/aladdin-backend/app/security/safe_function_manager.py` | Код SFM |
| `docs/server/L3_SMOKE_CONTRACT.md` | Правила для ML (создать в B-OPS-07) |
| `docs/release/gates/security-l3-report.json` | Машиночитаемый статус 138 |

---

## 5. Задачи OPS batch (добавить в IMPLEMENTATION_BATCHES)

| ID | Задача |
|----|--------|
| `B-OPS-01` | :8003 health: `sfm_loaded`, `registry_count`, fail systemd if false |
| `B-OPS-02` | Убрать hardcoded 1074 из health |
| `B-OPS-03` | unknown execute → 503 JSON |
| `B-OPS-04` | Deprecate `deploy_optimized_sfm.sh`; deploy runbook only SFM-WIRE |
| `B-OPS-05` | Registry backup hook + forbid empty overwrite |
| `B-OPS-06` | systemd PYTHONPATH + `preflight_sfm.py` in deploy |
| `B-OPS-07` | `L3_SMOKE_CONTRACT.md` + update ML guide |
| `B-OPS-08` | `aladdin-sfm-prod-smoke.timer` 15m |
| `B-OPS-09` | Fix `sfm-healthcheck.service` 203 EXEC |
| `B-OPS-10` | `security-l3-report.json` generator from smoke |
| `B-OPS-11` | Block wildcard responses in functional-138 runner |
| `B-OPS-12` | EXTENDED_138: verify=L3 only |

### SFM Truth — чтобы ML не путались (обязательно)

| ID | Задача |
|----|--------|
| `B-OPS-13` | `GET /api/sfm/status` — честный JSON (`sfm_loaded`, `registry_count`, `fallback_mode`) |
| `B-OPS-14` | Deploy `docs/server/sfm_truth_check.sh` на VPS + chmod +x |
| `B-OPS-15` | `docs/SFM_ML_QUICKSTART.md` — первая страница для любой ML |
| `B-OPS-16` | `AGENTS.md` + handoff: шаг 0 = sfm truth check |
| `B-OPS-17` | Stub rename `safe_function_manager.py` → `.STUB_DO_NOT_IMPORT` |
| `B-OPS-18` | `app/security/README_SFM.md` на сервере с каноническими путями |
| `B-OPS-19` | Deploy gate: `sfm_truth_check.sh` exit 0 или block |
| `B-OPS-20` | `function_registry.manifest.json` в репо (count + sha256 prod sync) |

**Спека:** `docs/SFM_SINGLE_SOURCE_OF_TRUTH.md`

---

## 6. Порядок: реализация + защита одновременно

```
SFM-WIRE + B-OPS-01…06  (подключить + gates)
        ↓
BATCH 0 SEC-INFRA
        ↓
BATCH 1…5 (antifake → … → device)
        ↓
B-OPS-07…12 (ML contract + monitoring)
        ↓
BATCH QA 138 L3 sign-off
```

Без B-OPS параллельно с SFM-WIRE — снова возможен «тихий» fallback.
