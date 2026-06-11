# ALADDIN — VPN в экосистеме (KB для Hermes)

## Важно: два разных VPN-продукта

| Продукт | Где | Для кого |
|---------|-----|----------|
| **ALADDIN Family VPN** | Мобильное приложение ALADDIN, защита сети семьи | Пользователи iOS-приложения |
| **AiMonkeyVPN (Telegram Shop)** | Отдельный Telegram Shop Bot | Покупатели Stars/VPN в боте, **не** в iOS |

В ответах **не путать**: вопрос из iOS-приложения → ALADDIN Family VPN; вопрос про оплату Stars/VPN в Telegram → Shop Bot.

## ALADDIN Family VPN (приложение)

- Статус VPN и защиты сети — в разделе **Защита сети** / аналитика.
- Intent в AI Assistant: `network_vpn_status` — ответы с опорой на SFM aggregates (статус защиты), не выдумывать IP/локацию.
- Настройка зависит от тарифа и роли в семье.

## Если пользователь спрашивает про VPN в Telegram-магазине

- Это **отдельный** продукт (`telegram_stars_shop_bot`, `/opt/aladdin-shop-vpn-api`).
- Поддержка магазина — через shop-бот, не через AI Companion для детей.
- В приложении ALADDIN не выдавать ключи WireGuard из shop API.

## Типичные ответы

**«Как включить VPN?»** (в приложении) → Настройки / Защита сети, проверить подписку и профиль семьи.

**«Купил VPN в боте, где ключ?»** → Обратиться в support shop-бота; это не экран ALADDIN iOS.
