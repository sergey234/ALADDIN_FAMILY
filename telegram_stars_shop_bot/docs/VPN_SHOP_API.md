# ALADDIN Shop VPN — контракт API (`aladdin-shop-vpn-api`)

**Статус:** черновик SSOT; дополнять вместе с реализацией. Архитектура и фазы — в `VPN_SHOP_INTEGRATION_PLAN.md` §0. Публичные домены/точки входа — в **`VPN_PUBLIC_SURFACE_REGISTRY.md`**.

**Принципы:** только **оплаченный** доступ (без триала); API **не** торчит в публичный интернет без TLS+ACL; вызовы от бота/Partner API — с **HMAC**, **nonce**, **`Idempotency-Key`**; подписка Xray — **`GET /sub/<opaque_token>`** без query string (логи nginx для `location` отключить или маскировать).

---

## Аутентификация (внутренние вызовы)

| Элемент | Правило |
|---------|---------|
| Транспорт | По умолчанию `127.0.0.1` или unix socket; при вынесении на другую VPS — **HTTPS + mTLS** между `partner_api` и vpn-api. |
| Заголовки | `X-Timestamp` (unix sec), `X-Nonce` (случайная строка), `X-Signature` = HMAC-SHA256(`VPN_API_HMAC_SECRET`, `METHOD + "\n" + path + "\n" + timestamp + "\n" + nonce + "\n" + sha256(body)`) |
| Окно времени | ±60–120 с относительно `X-Timestamp` |
| Anti-replay | `nonce` одноразовый: таблица `nonce_cache(nonce, expires_at)` или Redis с TTL |
| Идемпотентность | Заголовок `Idempotency-Key`: `payment_event_id` или `order_id:activate` / `order_id:extend` — повтор возвращает тот же результат без побочных эффектов |
| Ротация секрета / sudo на VPS | Один и тот же **`VPN_API_HMAC_SECRET`** в `shared/.env` бота и в `env` vpn-api; порядок ротации и узкий `sudoers` — **`aladdin_shop_vpn_api/deploy/VPN13_SECRETS_SUDOERS_RUNBOOK.md`**. |
| Операторский break-glass | Команды бота **`/admin_vpn_*`** (только `ADMIN_IDS`): статус в `vpn.db`, **revoke** → `vpn_manual_override` при админ-причине, **extend** — см. **`VPN14_SUPPORT_ADMIN_RUNBOOK.md`**. |

---

## Rate limits (edge + приложение)

- Отдельные лимиты для: выдачи конфигов / `GET /sub/...` (публично опасные пути — только opaque token + проверка БД).
- Внутренние `activate`/`extend` с HMAC — более высокий лимит, только с loopback.
- По возможности: `limit_req` в nginx по `$binary_remote_addr`; политика хранения IP — согласовать с legal (не хранить / короткий TTL / обезличивание). **Готовый сниппет:** `aladdin_shop_vpn_api/deploy/nginx_vpn_sub_rate_limit_snippet.conf.example`.

---

## Эндпоинты (черновик имён)

| Метод | Путь | Назначение |
|-------|------|------------|
| GET | `/health` | Liveness (процесс) |
| GET | `/ready` | Readiness: WG-интерфейс, маршрут, при необходимости Xray порт |
| GET | `/v1/legal/vpn-terms` | Публичный markdown: условия VPN (черновик; **vpn-02**) |
| GET | `/v1/legal/vpn-aup` | Публичный markdown: AUP (**vpn-02**) |
| GET | `/v1/legal/vpn-data` | Публичный markdown: минимизация данных (**vpn-02**) |
| GET | `/internal/v1/locations/catalog` | Каталог строк «локации» для бота (HMAC+nonce; тело запроса пустое). Ответ JSON: `{"lines": [...], "preview_n": N}`. Источник данных — **`VPN_LOCATIONS_JSON`** на стороне vpn-api (как в боте). |
| POST | `/internal/v1/provision` | Создать/обновить peer по оплате (только HMAC, с `Idempotency-Key`) |
| POST | `/internal/v1/extend` | Продлить `paid_until` до абсолютной даты (webhook → job → сюда) |
| POST | `/internal/v1/add-subscription-days` | Нарастить подписку на **N календарных дней** от `max(now, paid_until)`; при отсутствии строки в `vpn_accounts` — создать; затем job `extend` |
| POST | `/internal/v1/revoke` | Отключить доступ (истёк срок, админ, abuse) |
| POST | `/internal/v1/wg/conf` | Тело JSON `{"telegram_user_id":…}` — текст WireGuard `.conf` (HMAC+nonce; **без** `Idempotency-Key`) |
| POST | `/internal/v1/locations/select` | `{"telegram_user_id", "location_slug"}` — сохранить предпочитаемую локацию для `Endpoint` в WG |
| GET | `/internal/v1/egress/catalog` | JSON нод из **`VPN_EGRESS_NODES_JSON`** (HMAC+nonce) |
| POST | `/internal/v1/ovpn/conf` | Тело JSON `{"telegram_user_id":…}` — per-user `.ovpn` (`VPN_OVPN_CLIENT_ISSUE_SCRIPT` → `var/ovpn-profiles/{id}.ovpn`) |
| GET | `/v1/legal/vpn-instructions` | Публичный markdown: **хаб инструкций** (vpn-38); файл `legal_docs/vpn-instructions.md` в `aladdin-shop-vpn-api` |
| GET | `/sub/<opaque_token>` | Подписка Xray (VLESS). **404** unknown token; **403** expired; **200** + `text/plain` если активен. Тело: **`VPN_SUBSCRIBE_VLESS_TEMPLATE`** (приоритет) или **`VPN_SUBSCRIBE_BODY_FILE`** с `{opaque_token}`, `{xray_uuid}`, `{host}`, `{port}`, … |
| POST | `/internal/v1/rotate-opaque` | Смена opaque token по запросу / политике |
| GET | `/metrics` | **Prometheus** exposition (vpn-15): HTTP histogram/counter + gauges из `vpn.db`. Только loopback / ACL — см. **`deploy/VPN15_OBSERVABILITY_RUNBOOK.md`** |

Точные JSON-тела и коды ошибок — добавить при реализации.

### `POST /internal/v1/add-subscription-days`

**Тело (JSON):** `telegram_user_id` (int), `order_id` (int), `days` (int, 1..3660), `reason` (string, опционально).

**Поведение:** читает текущий `paid_until`; новый срок = `max(now_utc, parsed_paid_until) + days`; upsert в `vpn_accounts` (`vpn_active`); ставит job типа `extend` с итоговым `paid_until`. Те же заголовки HMAC/nonce и **`Idempotency-Key`**, что у остальных internal-роутов.

**Ответ 202:** JSON с `job_id`, `status`, `paid_until`, `telegram_user_id`.

---

## Модель состояний (связка оплата ↔ VPN)

Рекомендуемые статусы учёта VPN (отдельно от статуса заказа в магазине):

- `vpn_provisioning` — оплата учтена, идёт провижининг
- `vpn_active` — peer/сертификат выдан, `paid_until` в будущем
- `vpn_expired` — срок `paid_until` истёк (воркер перевёл автоматически)
- `vpn_failed` — ошибка + счётчик ретраев + причина
- `vpn_manual_override` — саппорт вмешался

Заказ может быть `completed`, а VPN — `vpn_failed`; процедура компенсации (refund / ручной довод) — продуктово зафиксировать в legal/runbook.

---

## Очередь `jobs`

Типы: `provision`, `extend`, `revoke`, `rotate_url`. Воркер с backoff, concurrency **1** для мутирующих операций при SQLite. Webhook не вызывает `wg set` синхронно — только постановка в очередь.

После успешного выполнения job **`provision`** в режиме **`VPN_DEV_STUB_WG=1`** (и в будущем — после реального WG в **`vpn-04`**) воркер может вызвать внешний скрипт **`VPN_WG_POST_PROVISION_SCRIPT`** с аргументом **`telegram_user_id`** — узкая обёртка на сервере (`sudoers` на `wg` и т.д.), без root у Python.

---

## Наблюдаемость (vpn-api)

### Sentry

Те же переменные, что у бота/Partner API: **`SENTRY_DSN`**, **`SENTRY_ENVIRONMENT`**, **`SENTRY_TRACES_SAMPLE_RATE`**. Инициализация в `aladdin_shop_vpn_api.main` при старте (пакет `sentry-sdk` в `aladdin_shop_vpn_api/requirements.txt`).

### Prometheus (vpn-15)

- **`GET /metrics`** — текстовый формат для scrape; зависимость **`prometheus-client`** в `aladdin_shop_vpn_api/requirements.txt`.
- Метрики: **`aladdin_shop_vpn_http_request_duration_seconds`** (Histogram, labels `method`, `route`), **`aladdin_shop_vpn_http_requests_total`** (Counter, `status_class`), gauges **`aladdin_shop_vpn_jobs_*`** и **`aladdin_shop_vpn_accounts_vpn_*`** (снимок из `vpn.db` при каждом scrape).
- **PromQL p95**, scrape, безопасность **`/metrics`**, импорт дашборда Grafana: **`aladdin_shop_vpn_api/deploy/VPN15_OBSERVABILITY_RUNBOOK.md`**; JSON дашборда: **`aladdin_shop_vpn_api/deploy/grafana/aladdin_shop_vpn_api_dashboard.json`**.

---

## Версионирование документа

| Дата | Изменение |
|------|-----------|
| 2026-05-14 | **vpn-15:** **`GET /metrics`** (Prometheus: HTTP histogram/counter, gauges jobs/accounts); runbook **`VPN15_OBSERVABILITY_RUNBOOK.md`**; Grafana **`deploy/grafana/aladdin_shop_vpn_api_dashboard.json`**; nginx ACL-пример **`nginx_vpn_metrics_allow_local.conf.example`**. |
| 2026-05-14 | **GET** `/internal/v1/locations/catalog`; **GET** `/v1/legal/vpn-instructions`; Sentry в vpn-api; сниппет nginx для `limit_req` на `/sub/`. **POST** `/internal/v1/wg/conf`, переменные `VPN_WG_*` / `WG_KEYS_DIR`; nginx: только **`/v1/legal/vpn-*`**. Черновик: auth, idempotency, эндпоинты, состояния, jobs; без триала. **`POST /internal/v1/add-subscription-days`** — VPN-рефералка. |
| 2026-05-16 | Реализация v0.1 в репо: `aladdin_shop_vpn_api` — provision/extend/revoke + jobs + воркер (stub WG); опционально **`VPN_WG_POST_PROVISION_SCRIPT`** после успешного `provision` (мост к **`vpn-04`**). |
| 2026-05-16 | Бот: авто-📥 после `paid` (`VPN_AUTO_SEND_WG_AFTER_PAID`); **`vpn:check`**; каталог локаций с `endpoint_host` из egress; WG `.conf` только IPv4 (`AllowedIPs 0.0.0.0/0`). |
| 2026-05-15 | **vpn-06** OVPN :1194; **egress/catalog**; генератор `/sub`; **MTU** в WG conf; single-node **VPN30** doc. |
