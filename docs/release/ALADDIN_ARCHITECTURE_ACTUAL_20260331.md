# ALADDIN: Актуальная архитектура и фактическое состояние (31.03.2026)

## Для чего этот документ
Этот файл фиксирует текущее, фактически проверенное состояние системы после перехода от compat/mock поведения к боевому контуру данных.  
Цель: чтобы любая другая ML/engineering команда быстро поняла, как устроены мобильное приложение, сервер, БД, мониторинг, релизные гейты и где находятся артефакты проверки.

## Короткий ответ на главный вопрос
- Да, выполнен полный прогон по матрице:
  - 42 компонента: `PASS 42/42` (`docs/release/gates/ios-smoke-42-report.json`)
  - 138 функций: `PASS 138/138` (`docs/release/gates/endpoint-report.json`)
- Да, проверены критичные write-path сценарии с SQL before/after:
  - `PASS 13/13` (`docs/release/gates/write-before-after-report.json`)
- Ограничение на текущий момент:
  - финальный GO по релизу зависит от полного 24h soak (`rel-15`), сейчас gate показывает `IN_PROGRESS`, поэтому сводный `rel-16` временно `NO_GO`.

## Что было раньше и что стало сейчас

### Было (до hardening и write-path фиксов)
- Часть критичных endpoint-ов могла уходить в compat/fallback слой.
- Для части доменов ответы были совместимыми, но не всегда подтверждали боевую запись в доменные таблицы.
- Могли быть неявные маршруты (wildcard/fallback), усложняющие контроль прод-поведения.
- Релизное решение сильно зависело от ручной проверки.

### Стало (текущее состояние)
- Для критичных API-семейств включено явное маршрутизирование и hardening:
  - неизвестные пути в критичных префиксах возвращают 404, не fallback.
- Ключевые security write действия пишут в БД и подтверждаются SQL before/after.
- Anti-mock gate подтверждает отсутствие mock-маркеров в целевых ответах.
- OpenAPI drift и iOS endpoint sync автоматизированы и проходят PASS.
- Релизный контур переведен в artifact-based проверку (JSON/CSV/MD отчеты).

## Архитектура (как взаимодействуют части)

### 1) iOS слой
- Клиент использует endpoint-контракты из `Core/Config/AppConfig.swift`.
- Проверка синхронизации с backend OpenAPI:
  - `docs/release/gates/ios-endpoint-sync-report.json` (`PASS`)
- Smoke на 42 карточки/компонента:
  - `docs/release/gates/ios-smoke-42-report.json` (`PASS 42/42`)
- Functional по 138 функциям:
  - `docs/release/gates/ios-functional-138-report.json`

### 2) Backend/API слой
- Основной runtime: `:8002` (gunicorn/uvicorn).
- Основной API контур: FastAPI роутеры в `security/api/routers/*` и `app/security/api/routers/*`.
- Для критичных префиксов включено hardening (без wildcard fallback для unknown paths).
- Контрактная проверка матрицы:
  - `docs/release/gates/endpoint-report.json` (`PASS 138/138`)

### 3) DB слой
- PostgreSQL с доменными схемами (`darkweb`, `identity`, `tracker`, `location`, `cleanup`) + необходимые public таблицы.
- Freshness строится по `analytics_freshness` (последние события доменов).
- Гранты/least-privilege и миграционный контур вынесены в `docs/release/db/*`.

### 4) Observability слой
- Метрики Prometheus (включая freshness, latency, 5xx).
- Alert rules + dashboard артефакты в `docs/observability/*`.
- SLO отчет:
  - `docs/release/gates/observability-slo-report.json` (`PASS`)
- Runtime PII audit:
  - `docs/release/gates/security-pii-audit-report.json` (`PASS`)

### 5) Release-gate слой
- Гейты `rel-06..rel-16` собираются в единое решение:
  - `docs/release/release-gate-report.json`
  - `docs/release/go-no-go.md`
- Текущий статус: все до `rel-14` PASS, `rel-15` в процессе, поэтому `rel-16` пока `NO_GO`.

## Что именно покрыто по 42/138

## Компоненты (42)
- Факт покрытия подтвержден артефактом:
  - `target_components=42`, `checked_components=42`, `passed=42`, `failed=0`
  - источник: `docs/release/gates/ios-smoke-42-report.json`

## Функции/эндпоинты (138)
- Факт покрытия подтвержден артефактом:
  - `total_checked=138`, `passed=138`, `failed=0`
  - источник: `docs/release/gates/endpoint-report.json`
- Примечание по кодам:
  - В матрице встречаются 200/401/404/422/400/405 как ожидаемые исходы для разных контрактов (в т.ч. auth/validation/protected routes), при этом mock-маркеры отсутствуют.

## Какие write-функции подтверждены “по-настоящему” (SQL before/after)
Подтверждены сценарии:
- `identity_allow`
- `identity_block`
- `location_allow`
- `location_block`
- `tracker_whitelist`
- `tracker_whitelist_idempotent`
- `cleanup_start`
- `darkweb_scan_start`
- `darkweb_scan_fast`
- `darkweb_scan_secure`
- `parental_bypass_apply`
- `parental_bypass_apply_idempotent`
- `location_update_accuracy`

Источник: `docs/release/gates/write-before-after-report.json` (`PASS 13/13`).

## Ключевые endpoint-ы, которые сейчас реально пишут в БД (подтвержденный контур)
- `POST /api/reports/identity-theft/allow`
- `POST /api/reports/identity-theft/block`
- `POST /api/reports/privacy/location/allow`
- `POST /api/reports/privacy/location/block`
- `POST /api/reports/privacy/location/update-accuracy`
- `POST /api/reports/privacy/tracker/whitelist`
- `POST /api/reports/privacy/cleanup/start`
- `POST /api/reports/dark-web/scan/start`
- `POST /api/reports/dark-web/scan/fast`
- `POST /api/reports/dark-web/scan/secure`
- `POST /api/parental/bypass/apply`

## Что с endpoint-ами вне “must-write” контура
- Не каждый POST обязан писать в БД (часть endpoint-ов — orchestration/validation/auth/delegation).
- Для top-gap ручная бизнес-классификация вынесена в:
  - `docs/release/gates/db-write-registry-business.csv`
- Авто-скан всех mutating endpoint-ов:
  - `docs/release/gates/db-write-registry.csv`
  - `docs/release/gates/db-write-registry-summary.json`

## Anti-mock и контрактная честность
- Anti-mock gate:
  - `docs/release/gates/anti-mock-report.json` (`PASS`)
- Проверяется отсутствие:
  - `sfm_mock`, `sfm_fallback`, `mock_fallback`, `reports_compat`, `"source":"mock"`

## OpenAPI и iOS синхронизация
- Drift:
  - `docs/release/gates/openapi-drift-report.json` (`PASS`, удалений/дрейфа нет)
- iOS sync:
  - `docs/release/gates/ios-endpoint-sync-report.json` (`PASS`, отсутствующих endpoint-ов нет)

## Observability/SLO и безопасность
- `docs/release/gates/observability-slo-report.json`: `PASS`
  - p95 и 5xx в целевых пределах
  - freshness в доменных порогах
  - активных алертов на момент отчета нет
- `docs/release/gates/security-pii-audit-report.json`: `PASS`
  - утечки PII/secret маркеров в runtime/metrics не обнаружены

## Что уже подключено и как это работает вместе
- iOS вызывает backend endpoint-ы по контракту.
- Backend роутеры:
  - читают/пишут PostgreSQL (где нужна бизнес-персистентность),
  - отдают DTO-контракты без mock marker-ов,
  - защищены hardening-правилами на критичных API семействах.
- Prometheus считывает метрики (включая freshness), Alertmanager/Grafana работают по правилам и дашборду.
- Release pipeline собирает gate-артефакты и выдает формальное GO/NO-GO.

## Текущее релизное состояние на момент документа
- `rel-06..rel-14`: PASS
- `rel-15`: IN_PROGRESS (идет 24h soak)
- `rel-16`: временно `NO_GO` до завершения rel-15

## Что нужно для финального GO
- Завершить полное 24h soak окно.
- Получить итоговый `soak-*.summary.json` с PASS по SLO checks.
- Пересобрать `release-gate-report.json` и `go-no-go.md`.
- После этого решение станет финальным (GO или NO_GO по факту метрик).

## Разъяснение: почему 13/13 и как это связано с 42/138
- `138/138 PASS` означает: все функции из контрактной матрицы отработали по ожидаемому API-поведению (статусы/DTO/без mock-marker).
- `13/13 PASS` означает: для 13 критичных write-сценариев дополнительно доказана реальная запись в БД через SQL before/after.
- Это не означает, что в системе только 13 функций пишут в БД.
- Это означает, что именно 13 критичных write-сценариев покрыты самым строгим доказательным тестом (бизнес-эффект в PostgreSQL).

## Полная проверка каждой функции из 138 на признак DB-write (актуальный срез)
Для исключения двусмысленности выполнена отдельная сверка каждой функции из `endpoint-report.json`:
- подробный файл по каждой функции:
  - `docs/release/gates/function-db-write-audit-138.csv`
- сводка:
  - `docs/release/gates/function-db-write-audit-138-summary.json`

Фактический итог по 138 функциям:
- `functions_total`: 138
- `contract_pass_total`: 138
- `mutating_candidate_total`: 57
- `read_only_or_validation_total`: 81
- `business_classified_total`: 28
- `business_must_not_write_total`: 18
- `business_unknown_total`: 10

Важно:
- В текущем 138-контрактном наборе нет части специальных `reports/*` write-путей, которые проверяются в `write-before-after`.
- Поэтому `13/13` — это отдельный критичный write-контур, а не подмножество “всех 138” в прямом сравнении один-к-одному.

## Проверка по 42 компонентам: какие должны писать в БД
Сделана отдельная сводка на основании smoke-матрицы 42:
- детально по компонентам:
  - `docs/release/gates/component-db-write-classification-42.csv`
- сводка:
  - `docs/release/gates/component-db-write-classification-summary-42.json`

Интерпретация:
- smoke-42 использует в основном representative endpoint для проверки доступности/контракта,
- поэтому классификация DB-write на уровне smoke-42 почти всегда `unknown` (это нормально),
- для точного DB-write решения ориентируемся на:
  - `function-db-write-audit-138.csv`
  - `db-write-registry-business.csv`
  - `write-before-after-report.json`.

## Где смотреть “истину” по текущему состоянию
- Архитектурно-исполнительный отчет:
  - `docs/release/ALADDIN_ML_SYSTEM_42x138_ARCHITECTURE_AND_EXECUTION_REPORT.md`
- Gate результаты:
  - `docs/release/gates/*.json`
- Финальное решение:
  - `docs/release/release-gate-report.json`
  - `docs/release/go-no-go.md`
- Soak:
  - `docs/release/soak/*.samples.jsonl`
  - `docs/release/soak/*.summary.json`

## Контроль полноты этого документа
В документ включены:
- текущее состояние 42/138,
- подтвержденные write-path и endpoint-ы,
- was->now изменения,
- сервер+iOS+DB+observability взаимодействия,
- гейты, артефакты и финальные критерии GO/NO-GO.

## Обновление: полная классификация 57 mutating-функций (100%)
Выполнена отдельная полная классификация всех mutating-кандидатов из контрактной матрицы:
- файл: `docs/release/gates/function-db-write-business-57.csv`
- сводка: `docs/release/gates/function-db-write-business-57-summary.json`

Актуальный итог по 57:
- `functions_mutating_total`: 57
- `must_write_db`: 4
- `must_not_write_db`: 53
- `unknown`: 0
- `business_registry_rows`: 18

Интерпретация:
- `must_write_db`: функции, для которых подтвержден обязательный write-path (по текущей бизнес-классификации).
- `must_not_write_db`: функции, где запись в БД не является обязательной бизнес-целью.
- `unknown`: функции, где нужен отдельный серверный trace/DB before-after для финальной бизнес-классификации.

Остаток `unknown=0`: runtime-backlog закрыт.
- `docs/release/gates/function-db-write-business-57-runtime-backlog.csv`

Важно:
- Это не меняет факт `13/13` по критичному SQL before/after контуру.
- Это расширяет прозрачность: теперь все 57 mutating-функций имеют явный статус в отдельном артефакте.

## Операционное обновление (01.04.2026)
- Runtime подтвержден как единый `gunicorn` на `:8002` (`aladdin-backend.service`), с `DISABLE_SFM_MOCK=1` и `PYTHONPATH=/opt/aladdin-backend`.
- Для wildcard-hardening подтверждено, что критичный префикс `auth/` не уходит в SFM fallback:
  - `POST /api/auth/unknown` -> `404` (без `sfm_mock/mock_fallback`).
- Восстановлен и проверен ожидаемый endpoint мобильного клиента:
  - `POST /api/auth/register-device` присутствует в OpenAPI и возвращает валидный JWT-ответ при корректном теле.
- Для аналитического контракта добавлен и проверен legacy-path:
  - `GET /api/reports/tracker/stats` -> `200`,
  - `GET /api/reports/privacy/tracker/stats` -> `200`.
- Гейты после фиксов:
  - `anti-mock-report.json` -> `PASS`
  - `endpoint-report.json` -> `PASS`
  - `ios-smoke-42-report.json` -> `PASS`
  - `ios-functional-138-report.json` -> `PASS`
- `release-gate-report.json` пересобран; агрегированное решение остаётся `NO_GO` до закрытия внешних release-условий (в т.ч. soak/gates вне текущего hotfix-контра).
