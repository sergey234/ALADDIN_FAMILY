## Rollout / Rollback Checklist (ML system aware)

### 1. Pre-Rollout (server ready)
- **Проверить runtime на `:8002`**:
  - `curl -s http://149.154.65.180:8002/api/health`
- **Проверить systemd unit `aladdin-backend.service`**:
  - `WorkingDirectory=/opt/aladdin-backend`
  - `ExecStart=... gunicorn main:app -b 0.0.0.0:8002`
  - `Environment=DISABLE_SFM_MOCK=1`
  - `Restart=always`
- **Права к БД**:
  - runtime‑пользователь имеет `GRANT` на доменные write‑таблицы (identity/location/tracker/cleanup/darkweb/parental).

### 2. Pre-Rollout (gates / артефакты)
- **Убедиться, что актуальны gate‑отчёты**:
  - `docs/release/gates/endpoint-report.json`
  - `docs/release/gates/write-before-after-report.json`
  - `docs/release/gates/openapi-drift-report.json`
  - `docs/release/gates/ios-endpoint-sync-report.json`
  - `docs/release/gates/anti-mock-report.json`
  - `docs/release/gates/observability-slo-report.json`
  - `docs/release/gates/security-pii-audit-report.json`
  - `docs/release/gates/ios-smoke-42-report.json`
  - `docs/release/gates/ios-functional-138-report.json`
- **Проверить сводный gate‑отчёт**:
  - `docs/release/release-gate-report.json` (все, кроме `rel-15`, должны быть `PASS`).
  - `docs/release/go-no-go.md` (финальное решение GO/NO_GO).
- **Проверить отсутствия mock‑маркеров**:
  - по `anti-mock-report.json` и выборочными `curl` на критичные `auth/parental/reports/components` (ответы 4xx/2xx без `sfm_mock/mock_fallback`).

### 3. Rollout (deploy)
- **Шаги деплоя**:
  - залить обновлённый backend‑код/роутеры на `:/opt/aladdin-backend`;
  - `systemctl restart aladdin-backend.service` (или эквивалентная команда через скрипт деплоя).
- **Быстрая проверка после рестарта**:
  - `/openapi.json` доступен и содержит новые роуты;
  - `/api/health` → `200`;
  - критичные POST‑флоу возвращают бизнес‑ответ (не fallback/mock):
    - `/api/auth/register-device`
    - `/api/parental/bypass/apply`
    - `/api/reports/identity-theft/allow|block`
    - `/api/reports/privacy/location/allow|block`
    - `/api/reports/privacy/tracker/whitelist`
    - `/api/reports/privacy/cleanup/start`
    - `/api/reports/dark-web/scan/*`.

### 4. Post-Rollout Validation (gates)
- **Запустить/обновить gates (если нужно выполнить вручную)**:
  - `python3 docs/server/full_system_endpoint_audit.py` (или дождаться актуального `FULL_SYSTEM_ENDPOINT_AUDIT_REPORT_*.json`);
  - `python3 tools/release_write_before_after_runner.py`;
  - iOS gates (`ios-smoke-42`, `ios-functional-138`) с получением:
    - `docs/release/gates/ios-smoke-42-report.json`
    - `docs/release/gates/ios-functional-138-report.json`.
- **Проверить, что после деплоя**:
  - `write-before-after` = **PASS**;
  - `endpoint-report.json` = **PASS**;
  - `anti-mock-report.json` = **PASS** (нет mock‑маркеров на прод‑поверхности);
  - `observability-slo-report.json` = **PASS** (p95/5xx/freshness/alerts в норме);
  - `security-pii-audit-report.json` = **PASS** (нет утечек JWT/секретов);
  - iOS smoke/functional = **PASS**;
  - сводный `release-gate-report.json` обновлён, а `go-no-go.md` отражает текущее решение.

### 5. Rollback Triggers
- Любой критичный security‑эндпоинт (`auth/`, `parental/`, `reports/`, `components/`) начинает возвращать fallback/mock‑ответ.
- SQL before/after проверки для must‑write эндпоинтов (`identity/location/tracker/cleanup/darkweb/parental`) **FAIL**.
- Устойчивый всплеск 5xx или критических алертов после окна деплоя.
- Нарушение SLO по freshness (domain `identity/location/tracker/darkweb/cleanup`) по `aladdin_analytics_freshness_seconds`.

### 6. Rollback Steps
- Откатить backend‑код/роутеры к предыдущей версии (snapshot/backup).
- `systemctl restart aladdin-backend.service` (gunicorn `:8002`).
- Минимальная проверка:
  - `/api/health` и `/openapi.json` в норме;
  - anti‑mock ручными `curl` по критичным префиксам → без mock‑маркеров.
- Повторно прогнать сокращённый `write-before-after`‑набор:
  - identity allow/block,
  - location allow/block/update‑accuracy,
  - tracker whitelist (+idempotent),
  - cleanup start,
  - darkweb scan start/fast/secure,
  - parental bypass apply (+idempotent).

### 7. Ports / Access
- SSH: `22`
- Gateway (backend API): `8002`
- Prometheus: `9090` (если включён в текущем окружении)
- PostgreSQL: локальный доступ через `sudo -u postgres psql`
