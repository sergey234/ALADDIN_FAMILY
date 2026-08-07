# Где лежит VPN и бот — простым языком

## Что значит путь `ALADDIN_NEW/mobile_apps/ALADDIN_iOS/`?

Это **папка в вашем Git-репозитории на компьютере** (в Cursor), а не путь на сервере.

- **`ALADDIN_NEW`** — корень монорепозитория (там же iOS-приложение, бэкенды, документы).
- **`mobile_apps/ALADDIN_iOS`** — каталог **мобильного iOS-проекта** и всего, что к нему «пришито» в этом репо: в том числе **Telegram-магазин** и **VPN API**.

На **продакшен-VPS** этих вложенных папок нет: туда выкатываются только нужные части в `/opt/…`.

## Две «половины» VPN в репо

| В репозитории (разработка) | На сервере (прод) |
|----------------------------|-------------------|
| `telegram_stars_shop_bot/` — бот Stars/магазин, кнопки VPN, оплата | `/opt/aladdin-telegram-shop-bot/` (релизы + `current_app`) |
| `aladdin_shop_vpn_api/` — API: WG, `/sub`, OVPN, jobs, legal | `/opt/aladdin-shop-vpn-api/` |

**Связка:** бот и vpn-api делят секрет `VPN_API_HMAC_SECRET` и дергают друг друга по HTTP (обычно `127.0.0.1:8091` на той же машине).

## Куда класть новые файлы

| Задача | Куда в репо |
|--------|-------------|
| Тексты кнопок, меню VPN в Telegram | `telegram_stars_shop_bot/bot/handlers/vpn.py` |
| Вызовы VPN API из бота | `telegram_stars_shop_bot/bot/services/vpn_api_client.py` |
| Эндпоинты, БД, воркер | `aladdin_shop_vpn_api/aladdin_shop_vpn_api/` |
| Runbook’и, скрипты выката | `aladdin_shop_vpn_api/deploy/` |
| Планы, реестр URL, чеклисты | `telegram_stars_shop_bot/docs/VPN_*.md` |
| Публичные legal/instructions | `aladdin_shop_vpn_api/aladdin_shop_vpn_api/legal_docs/` |

После правок в репо — **rsync/деплой** на VPS (см. `deploy/VPN17_DEPLOY_RUNBOOK.md`), затем `systemctl restart` нужных сервисов.

## iOS-приложение ALADDIN

Клиентское iOS-приложение (`Screens/`, `Core/`) — **отдельный продукт**. VPN в магазине Telegram **не требует** правок в Swift, пока не делаете VPN внутри нативного приложения.
