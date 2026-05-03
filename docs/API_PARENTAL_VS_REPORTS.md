# Разделение API: семейные отчёты и `/api/reports/*`

## Семья (родительский контроль)

- Сводки и списки для экрана «Семья» / мониторинг: префикс **`/api/parental-control/`**  
  Примеры: `GET /api/parental-control/stats`, `GET /api/parental-control/monitoring/detail`,  
  `GET /api/parental-control/reports/weekly`, `GET /api/parental-control/reports/daily`,  
  `POST /api/parental-control/monitoring/events`.
- Данные отчётов в БД: таблица **`parental_reports`** (`type`: `weekly` | `daily`), поле **`content`** — JSON (см. `tools/parental_weekly_content.example.json`).
- События с детского устройства: **`parental_monitoring_events`** (числовой `user_id` из JWT ребёнка).

## Личные «отчёты» продукта (не семья)

- Префикс **`/api/reports/`** и связанные маршруты (dark web, identity, privacy и т.д.) — **другой домен**, не подставлять в семейный UI «Отчёты».

В клиенте не смешивать вызовы: карточка «Отчёты» в семье должна опираться только на **`parental-control/reports/*`** и блок **`reports`** в **`GET /api/parental-control/stats`**.

## Детский клиент (опционально)

- `ParentalControlManager.postChildUrlVisitMonitoring(host:)` — шлёт `url_visit` только с **`url_sha256`** (без полного URL в payload). Вызывайте из своего контура (например расширение браузера / согласованный агент), когда появляется стабильный источник хоста.
- Смоук: `tools/smoke_parental_control.sh` (переменные `ALADDIN_API_BASE`, `ALADDIN_JWT`, опционально `ALADDIN_CHILD_ID`; опционально `ALADDIN_ALLOW_GATEWAY_ENVELOPE=1` на переходный период). План и выводы по публичному домену / nginx: **`docs/PARENTAL_MONITORING_DETAIL_GATEWAY_PLAN.md`**. OpenAPI в репозитории: `docs/release/current/openapi.json` (поиск по пути `/api/parental-control/` и `/api/parental/`).
- Пример JSON для `parental_reports.content`: `tools/parental_weekly_content.example.json`.

## pc-01 Юридика и чувствительные данные (вне кода)

Репозиторий не заменяет юридический консалтинг. Для «100%» продукта нужно отдельно зафиксировать: какие метрики и агрегаты разрешены политикой; отдельное решение по полному URL, SMS и контенту сообщений (согласия, хранение, минимизация); согласованность с офертой и возрастными ограничениями. Техническая часть уже ориентирована на агрегаты и хэши (`url_sha256`, снимки правил), без обязательной передачи полного URL в payload.
