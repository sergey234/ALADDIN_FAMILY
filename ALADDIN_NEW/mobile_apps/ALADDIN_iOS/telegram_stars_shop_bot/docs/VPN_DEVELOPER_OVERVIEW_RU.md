# AiMonkeyVPN — обзор для разработчиков

## WireGuard бесплатен?

Да. **WireGuard** — open-source: приложение у пользователя и `wireguard` на сервере **без лицензии**. Платите за VPS, трафик и свою разработку.

## Что в файле `.conf` и в QR

| | Файл `.conf` | QR |
|---|--------------|-----|
| Содержимое | Текст: **PrivateKey** клиента, **PublicKey** сервера, Endpoint, AllowedIPs | **Тот же текст**, закодирован в QR (бот: `qrcode`) |
| Для пользователя | Документ в чат Telegram | Картинка в чат |
| Не является | Программой, установщиком | Отдельным VPN |

## Цепочка после оплаты

1. Заказ → `paid` в `shop.db` (`user_id` = Telegram ID).
2. `vpn_payment_hook` → `POST /internal/v1/provision` (idempotency `shop-vpn-prov:{order_id}`).
3. VPN API → job `provision` → worker → `wg-peer-up.sh` → peer на `wg0`, статус `vpn_active`.
4. Бот poll `POST /internal/v1/wg/conf` → **авто 📥** (+ **авто 📷** если `VPN_AUTO_SEND_QR_AFTER_PAID=true`).

Ручных действий разработчика на заказ **не нужно**, если worker и WG в порядке.

## Три компонента

- **telegram_stars_shop_bot** — оплата, UI, доставка в Telegram.
- **aladdin-shop-vpn-api** — `vpn.db`, jobs, сборка `.conf`.
- **WireGuard на VPS** — туннель; бот с WG не говорит.

## Мониторинг (бот)

- **`/admin`** — блок **VPN health** при открытии дашборда.
- **`/admin_vpn_health`** — снимок по запросу.
- Фон: `VPN_OPS_HEALTH_INTERVAL_SECONDS` (по умолчанию **300** с) → алерт при `degraded` / `critical`.

Проверки: `/health`, `/ready` (интерфейс WG), circuit breaker, `vpn.db` (pending/failed jobs, stale pending, `vpn_failed`).

Внешний мониторинг: Prometheus/Grafana (см. `aladdin_shop_vpn_api/deploy/VPN15_*`).

## Переменные (бот)

| Переменная | Назначение |
|------------|------------|
| `VPN_API_BASE_URL` | URL vpn-api |
| `VPN_API_HMAC_SECRET` | HMAC к internal API |
| `VPN_DB_PATH` | Путь к `vpn.db` для админ-метрик |
| `VPN_AUTO_SEND_WG_AFTER_PAID` | Авто-файл после оплаты |
| `VPN_AUTO_SEND_QR_AFTER_PAID` | Авто-QR после файла |
| `VPN_OPS_HEALTH_INTERVAL_SECONDS` | Интервал health-check (0 = выкл.) |

См. также `docs/VPN_SHOP_API.md`, `docs/ML_SYSTEM_HANDOFF_FINAL.md`.
