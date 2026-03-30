# ALADDIN ML System: 42 Components / 138 Security Functions

## 1) Зачем мы это делали

Цель: полностью убрать `mock/compat` из production-контуров и перевести 42 компонента / 138 функций на честные данные, проверяемые записью в БД, контрактами и метриками.

Критерии успеха:
- нет `sfm_mock/sfm_fallback/mock_fallback/reports_compat` в ответах критичных endpoint'ов;
- write-path реально меняет доменные таблицы PostgreSQL;
- iOS и backend синхронизированы по OpenAPI;
- observability (freshness/p95/5xx/alerts) работает как release-gate;
- нет утечек PII/секретов в логах/метриках.

---

## 2) Как теперь устроена система

### 2.1 Runtime path
- iOS -> `gateway :8002` -> explicit routers -> PostgreSQL.
- Для критичных семейств (`reports/family/parental/components`) wildcard fallback в SFM заблокирован.
- Неизвестные пути в этих семействах дают явный `404`.

### 2.2 Data correctness
- Реализованы боевые write handlers для ключевых доменов.
- Freshness считается и публикуется в Prometheus: `aladdin_analytics_freshness_seconds`.
- Алерты по freshness/p95/5xx работают через Prometheus rules.

### 2.3 Contracts and release gates
- OpenAPI snapshot/diff gate.
- iOS `AppConfig.Endpoint` синхронизирован с runtime OpenAPI.
- Matrix-runner покрывает 42/138 и генерирует артефакты PASS/FAIL.

### 2.4 Security
- Применён masking-фильтр логов.
- Удалены preview-логи токенов/секретов из JWT-сервиса.
- Выполнен runtime scan логов и `/metrics` на PII/secret patterns.

---

## 3) Что реализовано по блокам

### Готово (PASS)
- `rel-00`: baseline freeze
- `rel-01`: inventory 42/138
- `rel-02`: db model/domain audit
- `rel-03`: db migrations batch track
- `rel-04`: least-privilege grants
- `rel-05`: ingest/backfill verification
- `rel-06`: endpoint hardening (critical wildcard guard)
- `rel-07`: anti-mock gate
- `rel-08`: contract suite matrix
- `rel-09`: write before/after SQL proofs (critical write-paths)
- `rel-10`: openapi drift + iOS sync
- `rel-11`: observability/SLO checks
- `rel-12`: security/PII audit
- `rel-13`: iOS smoke 42
- `rel-14`: iOS functional 138

### В процессе
- `rel-15`: 24h soak
- `rel-16`: final go/no-go

---

## 4) Самые важные изменения в коде

- `main.py`: guard для критичных API-семейств, исключён wildcard->SFM fallback.
- `security/api/routers/reports_router.py`: реальные POST write-path операции в доменные таблицы.
- `backend/app/services/jwt_service.py`: удалены `Token preview` и `SECRET_KEY preview`.

Автоматизация релизных проверок:
- `tools/release_gate_anti_mock.py`
- `tools/release_contract_matrix_runner.py`
- `tools/release_write_before_after_runner.py`
- `tools/release_openapi_drift_and_ios_sync.py`
- `tools/release_ios_smoke_runner.py`
- `tools/release_ios_functional_138_runner.py`
- `tools/release_soak_24h_monitor.py`
- `tools/release_go_no_go_aggregator.py`

---

## 5) Что проверено повторно (сейчас)

Прогнаны ключевые gate-проверки:
- health `:8002` -> PASS
- anti-mock -> PASS
- contracts 138 -> PASS
- write before/after -> PASS
- openapi drift + ios sync -> PASS
- runtime pii scan -> PASS
- ios smoke 42 -> PASS
- ios functional 138 -> PASS

Оперативные SLO на момент последней проверки:
- p95 ~ `0.0475s`
- 5xx share `0.0`
- active alerts `0`
- freshness по доменам в порогах

---

## 6) Ключевые артефакты

### Gate reports
- `docs/release/gates/anti-mock-report.json`
- `docs/release/gates/endpoint-report.json`
- `docs/release/gates/write-before-after-report.json`
- `docs/release/gates/openapi-drift-report.json`
- `docs/release/gates/ios-endpoint-sync-report.json`
- `docs/release/gates/observability-slo-report.json`
- `docs/release/gates/security-pii-audit-report.json`
- `docs/release/gates/ios-smoke-42-report.json`
- `docs/release/gates/ios-functional-138-report.json`
- `docs/release/gates/full-regression-now.json`

### Release decision
- `docs/release/release-gate-report.json`
- `docs/release/go-no-go.md`

### Soak
- `docs/release/soak/soak-*.samples.jsonl`
- `docs/release/soak/soak-*.summary.json` (финал после 24h)
- `docs/release/rel-15-soak-24h.md`

---

## 7) Почему это важно

Раньше релиз зависел от ручной уверенности и fallback-слоёв. Сейчас релиз управляется инженерными gate-правилами:
- контрактно,
- наблюдаемо,
- проверяемо по данным,
- безопасно по логам/метрикам.

Это снижает риск «скрытой деградации» и выпуска с фейковыми данными.

---

## 8) Что осталось до финального GO

1. Дождаться завершения `rel-15` (24h soak) и получить `soak-*.summary.json`.
2. Пересобрать `rel-16` через `tools/release_go_no_go_aggregator.py`.
3. При PASS всех gate (включая soak) -> финальное решение `GO`.

---

## 9) Текущий статус

- Архитектурно и функционально контур готов к финальному решению.
- Формальный блокер на текущий момент: незавершённый 24h soak.
- Пока soak не завершён, корректный статус — `NO_GO (IN_PROGRESS soak)`.
