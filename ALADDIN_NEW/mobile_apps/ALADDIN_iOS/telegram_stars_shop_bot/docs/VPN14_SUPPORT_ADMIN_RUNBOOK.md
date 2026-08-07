# vpn-14: поддержка VPN (FAQ) и админ-команды (revoke / extend / `vpn_manual_override`)

**Связано:** `VPN_SHOP_INTEGRATION_PLAN.md` §13, `VPN_SHOP_API.md`, `aladdin_shop_vpn_api/deploy/VPN13_SECRETS_SUDOERS_RUNBOOK.md`.

---

## 1. Статусы в `vpn.db` (кратко для саппорта)

| Статус | Смысл |
|--------|--------|
| `vpn_provisioning` | Оплата принята, job `provision` в очереди или в работе |
| `vpn_active` | Подписка активна, peer WG (после успешного hook) |
| `vpn_expired` | Срок `paid_until` прошёл или отзыв «мягкий» (истечение) — peer снят |
| `vpn_failed` | Ошибка провижининга (см. `last_error`, jobs `failed`) — **часто нужен оператор** |
| `vpn_manual_override` | Доступ отключён по решению оператора / abuse (после **revoke** с причиной ≠ auto-expire) |

Юридически про `vpn_manual_override` см. публичные **`vpn-terms`** / AUP.

---

## 2. FAQ для пользователей (шпаргалка)

- **«Оплатил, VPN не включается»** — проверить `/admin_vpn_status <telegram_id>`: `vpn_failed` / `vpn_provisioning` / pending jobs. При `vpn_failed` — логи воркера `aladdin-shop-vpn-worker`, `VPN_WG_POST_PROVISION_SCRIPT`, `wg show`. После исправления инфраструктуры — повторный `provision` через повторную выдачу заказа или ручной сценарий (отдельное решение продукта).
- **«Нужно отключить доступ срочно»** — `/admin_vpn_revoke <tid> <причина>` → статус **`vpn_manual_override`**, peer снимается воркером (если был active).
- **«Нужно продлить вручную до даты X»** — `/admin_vpn_extend <tid> <ISO8601> [order_id]`; без `order_id` бот подставит последний заказ с `product_kind=vpn` / `product_id` вида `vpn_*` для этого пользователя.
- **Юридические тексты** — публичные URL из `VPN_DOCS_PUBLIC_BASE` (`/vpn-terms`, `/vpn-aup`, `/vpn-data`).

---

## 3. Команды Telegram (только `ADMIN_IDS`)

Все команды требуют настроенных **`VPN_API_BASE_URL`** и **`VPN_API_HMAC_SECRET`**. Для **`/admin_vpn_status`** дополнительно нужен **`VPN_DB_PATH`** на том же хосте, что доступен боту (чтение `vpn.db`).

| Команда | Действие |
|---------|----------|
| `/admin_vpn` | Краткая справка по всем подкомандам |
| `/admin_vpn_status <telegram_user_id>` | Снимок строки `vpn_accounts` + последние jobs по этому `telegram_user_id` |
| `/admin_vpn_revoke <telegram_user_id> [причина…]` | `POST /internal/v1/revoke` → очередь revoke (итог **`vpn_manual_override`**, если причина не из списка auto-expire в воркере) |
| `/admin_vpn_extend <telegram_user_id> <paid_until_iso> [order_id]` | `POST /internal/v1/extend` → job extend; `order_id` опционален (последний VPN-заказ в `shop.db`) |

Идемпотентность: для каждого вызова генерируются новые ключи (`admin-revoke:…`, `admin-extend:…`) — **не** нажимать дважды без необходимости.

Аудит: в `admin_audit_log` пишутся действия `vpn:admin_revoke`, `vpn:admin_extend`, `vpn:admin_status`.

---

## 4. Технические детали API

- **Revoke:** тело `{"telegram_user_id": N, "reason": "…"}` — см. `RevokeBody` в репозитории `aladdin_shop_vpn_api`.
- **Extend:** тело `{"telegram_user_id", "order_id", "paid_until"}` — см. `ExtendBody`; `paid_until` в ISO UTC (как в webhook provision).

После enqueue воркер обработает job; при проблемах смотреть `jobs.last_error` и логи `aladdin-shop-vpn-worker`.
