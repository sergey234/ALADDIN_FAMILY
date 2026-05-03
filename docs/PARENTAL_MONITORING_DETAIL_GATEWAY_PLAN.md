# План: реальные данные `GET /api/parental-control/monitoring/detail` (aladdin-ai.ru)

## Выводы из логов клиента (2026-05-03)

- **HTTP 200**, задержка ~0.46 с — сеть и TLS в порядке.
- **Тело ~197 байт**, всегда одна и та же форма:  
  `{"function":"get_parental-control_monitoring_detail","params":{"childId":"…"},"result":"","timestamp":"…","source":"","version":"3.0.0-mock-real-protection"}`  
  Это **не** контракт iOS (`ParentalMonitoringDetailResponse`: `top_sites`, `summary`, … на корне JSON).
- **`keyNotFound("top_sites")`** — декодер читает корень как модель мониторинга; полей контракта нет.
- **`NetworkManager.swift:1426`** в логах при том, что в актуальном дереве та же строка логирования находится **около 1494** — на устройстве крутится **старая сборка** без развёртки gateway / fallback пустого payload.
- **`MetricsService: Метрика добавлена`** — побочный шум очереди аналитики, к ошибке декода не относится.

## Вывод `tools/phase0_monitoring_gateway_check.sh` (автоматизация этапа 0, публичная часть)

- `dig +short aladdin-ai.ru` → **149.154.65.180** (тот же хост, что в прод-runbook).
- **До исправления (май 2026):** без JWT приходил **envelope** SFM → код выхода скрипта **2**.
- **Корневая причина:** на `:8002` был **старый** `security/api/routers/parental_control_router.py` (~789 строк, без `GET /monitoring/detail`). Запрос не попадал в FastAPI-роутер и уходил в **`wildcard_handler`** в `main.py` → SFM возвращал `function` / пустой `result`. Nginx уже проксировал `/api/` на `127.0.0.1:8002` — менять vhost **не требовалось**.
- **Сделано на проде:** выкат актуального `parental_control_router.py` (с `monitoring/detail` и `monitoring/events`), `py_compile`, `systemctl restart aladdin-backend`; в `main.py` в `critical_prefixes` добавлен **`parental-control/`** (страховка от SFM при отсутствии роутера).
- **После исправления:** без JWT — **403** `{"detail":"Not authenticated"}` (норма); скрипт phase0 — **exit 0**.

## Внешняя проверка репозиторием (curl, 2026-05-03)

Команда (без заголовка авторизации):

`curl -sS "https://aladdin-ai.ru/api/parental-control/monitoring/detail?childId=MEM_B6DCC7194068"`

Результат:

- **`HTTP/2 200`**, заголовок **`server: nginx`**, **`content-length: 197`**, **`content-type: application/json`**.
- Тело **байт-в-байт совпадает** с логами приложения: тот же envelope, **`result` пустая строка**, **`version":"3.0.0-mock-real-protection"`**.

Выводы:

1. Проблема **не в JWT и не в iOS-сети**: публичный URL отдаёт **заглушку до FastAPI** (или отдельный слой, который не проксирует ответ `ParentalMonitoringDetailResponse`).
2. Даже **без `Authorization`** ответ **200** с mock-оболочкой — типично для «универсального» шлюза, а не для реального защищённого эндпоинта FastAPI (ожидались бы 401/403 с корректным телом ошибки).
3. Каноническая реализация в этом репозитории уже есть: `security/api/routers/parental_control_router.py`, префикс роутера `/api/parental-control`, маршрут `GET /monitoring/detail`, сборка через `_build_parental_monitoring_detail`. На публичном домене этот код **сейчас не виден** снаружи.

### Про пример nginx в репозитории

В `docs/server/NGINX_CONFIG_DASHBOARD.conf` для `location /api/` указан `proxy_pass http://localhost:8000`. В прод-runbook для API часто фигурирует порт **8002**. На реальном хосте нужно сверить: **какой процесс** слушает upstream за nginx и отдаёт ли он FastAPI или промежуточный mock (envelope с `version` …mock-real-protection).

## Этап 0. Базовая диагностика (обновлено)

1. Локально (без секретов): `./tools/phase0_monitoring_gateway_check.sh` — DNS (`dig`) и `curl` на публичный HTTPS; код выхода **2** = envelope/mock, **0** = уже FastAPI-форма.
2. На сервере (по гайду подключения): сравнить ответ **публичного** URL с ответом **origin** (uvicorn, например `127.0.0.1:8002` / порт из runbook), с тем же `childId` и с валидным JWT родителя; зафиксировать **`proxy_pass`** в активном `nginx` для `location /api/` (**8000** vs **8002**).
3. Зафиксировать цепочку: **DNS → nginx → (SFM/mock?) → FastAPI**.

Критерий: задокументировано, на каком hop появляется `function` / пустой `result`.

## Этап 1. Шлюз / mock-слой (0.5–2 дня)

В репозитории iOS **нет** генерации `get_parental-control_monitoring_detail` и `3.0.0-mock-real-protection` — это **внешний** слой перед FastAPI.

- Пример точечного `proxy_pass` на FastAPI (подставить порт после этапа 0b):  
  `docs/server/nginx_snippet_parental_monitoring_pass_through.conf.example`
- Инвентаризация: конфиг **nginx** (и любые `lua`, `sub_filter`, upstream maps), Cloudflare / отдельный Python-прокси.
- Варианты исправления:
  - **Passthrough** для `GET /api/parental-control/monitoring/detail` и при необходимости `POST /api/parental-control/monitoring/events` на актуальный upstream с FastAPI.
  - Если оболочка обязательна — **сериализовать** `ParentalMonitoringDetailResponse` в строку/объект поля `result` (хуже, дублирование контракта).

Критерий: `curl` с публичного URL (с JWT) возвращает JSON с **`top_sites`** на корне (или осознанная оболочка с непустым JSON в `result`, согласованная с клиентом).

## Этап 2. Версия бэкенда за nginx (0.5–1 день)

- Деплой актуального `security/api/routers/parental_control_router.py` и зависимостей на сервер, где крутится FastAPI; перезапуск по runbook; health-check.
- Проверка OpenAPI / прямой `GET` к uvicorn: маршрут существует, ответ — Pydantic-модель.

Критерий: на origin при пустой БД — **валидный** JSON с пустыми массивами и нулями в `summary`, не пустая строка `result` внутри envelope.

## Этап 3. Данные (продукт + ingest)

- Детский клиент: стабильный **`POST /api/parental-control/monitoring/events`** (JWT ребёнка с числовым `user_id`).
- БД: `parental_monitoring_events`, `parental_reports` — см. `_build_parental_monitoring_detail`.
- Смоук: `tools/smoke_parental_control.sh` (после фикса шлюза; при переходном периоде см. `ALADDIN_ALLOW_GATEWAY_ENVELOPE` в скрипте).

Критерий: после тестового ingest для того же `childId` в ответе появляются непустые списки там, где есть события.

## Этап 4. Клиент iOS

- **Clean build + переустановка** с текущего `Core/Network/NetworkManager.swift` (unwrap gateway, пустой `result` → пустой контракт, лимит/coalesce для `monitoring/detail`).
- В DEBUG ожидается знаменатель **400** в строке rate limit для этого path, не **100**; номера строк логов декода должны сдвинуться относительно старых **1426**.

Критерий: нет циклического `keyNotFound(top_sites)` на envelope; после фикса сервера UI показывает данные.

## Этап 5. Наблюдаемость

- Метрика/алерт: доля ответов с корневым полем `function` для `monitoring/detail` на проде → **0**.
- Регрессия: cron или CI с `jq 'has("top_sites")'` на прод URL с JWT.
- Минимальная проверка **без секретов** (публичный URL, без JWT): `tools/ci_check_parental_monitoring_detail_public.sh` — падает, если снова появился envelope.

## Риски

| Риск | Митигация |
|------|-----------|
| Passthrough ломает другие пути | Менять только `monitoring/detail` / `monitoring/events`. |
| Неверный `main.py` на проде | Этап 2 + смоук с авторизацией. |
| Пустые списки после фикса | Норма без ingest; не ошибка сети. |

## Порядок работ

Этап 0 → параллельно Этап 1 (nginx/SFM) и Этап 2 (FastAPI) → Этап 3 → Этап 4 → Этап 5.
