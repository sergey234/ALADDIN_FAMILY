# P0 — контракты API (уведомления, обход, мониторинг, метрики)

Единый источник для **p0-1 … p0-4**. Канонический код роутеров в репозитории: каталог  
`security/api/routers/` (импорт в `main.py`). Выкладка на прод: см.  
[`ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md`](../ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md) — `/opt/aladdin-backend`, смоук `curl http://149.154.65.180:8002/api/health`.

---

## p0-1 — `GET /api/notifications`

**Файл:** `security/api/routers/notifications_router.py`  
**Префикс роутера:** `/api/notifications`

### Query

| Параметр       | Тип    | По умолчанию | Описание |
|----------------|--------|--------------|----------|
| `familyId`     | string | см. ниже     | ID семьи; если не передан, на стороне сервера может использоваться fallback bucket (в коде `DEFAULT_FAMILY_ID`) — на проде нужно свести к семье из JWT/членства. |
| `limit`        | int    | 50           | 1…100 |
| `includeRead`  | bool   | true         | Включать прочитанные |

### Ответ (`NotificationListResponse`)

JSON с **`snake_case`** полями (клиент iOS: `JSONDecoder.convertFromSnakeCase`).

| Поле             | Тип        | Описание |
|------------------|------------|----------|
| `notifications`  | array      | Элементы см. ниже |
| `unread_count`   | int        | Число непрочитанных в выборке |

Элемент (`NotificationItem`):

| Поле              | Тип    | Описание |
|-------------------|--------|----------|
| `id`              | string | Уникальный id записи |
| `icon`            | string | Emoji от сервера |
| `title`           | string | Заголовок |
| `message`         | string | Текст |
| `type`            | string | **Каноническое строковое значение** из `NotificationType` (`app/security/family/family_notification_manager_enhanced.py`), напр. `bypass_attempt`, `threat_detected`, `security_alert` |
| `priority`        | string | `low` \| `medium` \| `high` \| `critical` \| `emergency` |
| `timestamp`       | ISO8601 | Дата создания |
| `is_read`         | bool   | Прочитано |
| `action_required` | bool   | Нужно действие |
| `action_url`      | string?| Опционально |
| `metadata`        | object | Рекомендуется `correlation_id` (string) для склейки с bypass/monitoring и офлайн-событиями |

### Матрица `type` (сервер) → `NotificationKind` (iOS)

Источник маппинга на клиенте: `NotificationsViewModel.NotificationKind.init(from:)`.

| Значения `type` с сервера (примеры) | Клиентский `NotificationKind` | Фильтр UI «Угрозы» / «Обход» |
|-------------------------------------|------------------------------|-------------------------------|
| `threat_detected`, `security_alert`, `emergency` (+ legacy `threat`) | `.threat` | Угрозы |
| `bypass_attempt`, `bypass`, и др. см. Swift | `.bypassAttempt` | Обход |
| `payment_success`, `subscription_activated`, `referral_reward`, `success` | `.success` | Успех |
| `warning`, `system_update`, `subscription_expiring`, `subscription_expired` | `.warning` | Предупреждения |
| Остальные из `NotificationType` | `.info` | Инфо / прочее |

Новые типы на сервере: добавить в enum и в таблицу выше, затем расширить `switch` в Swift (**обязательно** согласовать с p0-1).

---

## p0-2 — Цепочка обхода (ingest → stats → уведомление)

**Ingest:** `POST /api/parental-control/monitoring/events`  
**Файл:** `security/api/routers/parental_control_router.py`

Тело: `{ "events": [ { "kind": "…", "payload": { … } } ] }`.

Условия «это обход» и дельты счётчиков: `_is_bypass_monitoring_event`, `_bypass_counter_deltas` в том же файле.

После успешной записи события:

1. Обновление `parental_bypass_stats` (если найдена пара member id родитель–ребёнок).
2. In-app уведомление через `_emit_bypass_notification_from_ingest` с типом **`bypass_attempt`** и `metadata.correlation_id`, если `payload` содержит `correlation_id` / `correlationId`.

**Чтение счётчиков:** `GET /api/parental/bypass/stats?childId=…` (`bypass_router`).

Скоуп выбранного ребёнка на iOS: `parental_selected_child_id`.

---

## p0-3 — `GET /api/parental-control/monitoring/detail`

**Файл:** `security/api/routers/parental_control_router.py`

### Query

| Параметр  | Описание |
|-----------|----------|
| `childId` | Опционально; резолв в numeric user id через `_resolve_target_user_id`. |

### Семантика пустого ответа

Если целевой пользователь не резолвится (`target is None`), возвращается **`ParentalMonitoringDetailResponse()`** — все списки пустые, `summary` нулевой. Это **не ошибка** HTTP 200 (контракт «нет данных», а не 404).

Модель ответа (`ParentalMonitoringDetailResponse`): поля `top_sites`, `top_apps`, `browser_history`, `app_history`, `peak_hours`, `suspicious`, `contacts`, `summary` — см. Pydantic в роутере.

Ошибки ingest/events: 401 при нечисловом user id для JWT ребёнка; 500 при сбое INSERT.

---

## p0-4 — `POST /api/metrics/upload`

**Файл:** `security/api/routers/metrics_router.py`

Принимает пакет метрик без обязательной авторизации (как на iOS). Для `type == "user_action"` поле `action` — произвольная строка; в коде задан **справочник канонических имён** `METRICS_USER_ACTION_CANONICAL` (логирование неизвестных имён на уровне debug, ответ всё равно `success`).

### Канонические `user_action.action` (iOS → сервер)

| `action` | Источник в коде |
|----------|-----------------|
| `network_protection_smart_dns_state` | `DNSProtectionManager` |
| `network_protection_safari_cb_state` | `ContentBlockerManager` |
| `safari_content_blocker_rules_changed` | `ContentBlockerManager` |
| `security_notifications_anomaly` | `NotificationsViewModel` |
| `screen_load_complete` | `PerformanceMonitor` |
| `network_request_complete` | `PerformanceMonitor` |
| `action_performance` | `PerformanceMonitor` |
| `memory_usage_check` | `PerformanceMonitor` |
| `fps_measurement` | `PerformanceMonitor` |

Новые события: добавить в таблицу и в `METRICS_USER_ACTION_CANONICAL` в `metrics_router.py`; параметры — только нечувствительные (на клиенте уже `sanitizeMetricParameters`).

---

## Версии клиента и контракта (p5-2)

В iOS: `AppConfig.apiContractVersion` (строка-маркер, напр. дата `YYYY.MM.DD`) и `AppConfig.minimumClientBuildForApiContract` (минимальный **CFBundleVersion**, ожидаемый для текущего контракта).

**Правило при ломающих изменениях API** (удаление полей, смена семантики `type` уведомлений, обязательные новые query и т.п.):

1. Обновить этот документ и связанные экраны клиента.
2. Поднять **`apiContractVersion`** до нового маркера.
3. Поднять **`minimumClientBuildForApiContract`** до номера сборки, в которой клиент уже понимает новый контракт (или выше).
4. При необходимости отразить то же в ответах сервера (опциональное поле `apiContractVersion` в stats и т.д. — см. планы выравнивания семьи/подписок).

---

## Версия документа

| Версия | Изменение |
|--------|-----------|
| 1.0    | Первичное описание P0 по коду `security/api/routers/*`; выравнивание с iOS `NotificationsViewModel`, `RemoteNotificationsService`, `ParentalMonitoringDetail` |
| 1.1    | Добавлен §«Версии клиента и контракта (p5-2)»: правило bump `AppConfig.apiContractVersion` / `minimumClientBuildForApiContract` |
