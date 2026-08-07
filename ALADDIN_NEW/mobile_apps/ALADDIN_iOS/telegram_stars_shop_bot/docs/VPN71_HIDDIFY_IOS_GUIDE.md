# vpn-71 — iOS: Hiddify (запасной клиент)

**Когда использовать:** HitWave недоступен / не подходит; нет foreign Apple ID для v2RayTun.

## Установка Hiddify

1. App Store (RU) — поиск **Hiddify** (если есть) **или**
2. TestFlight / sideload по официальной инструкции Hiddify (ops актуализирует ссылку)
3. **Не** используйте v2RayVPN из Ru Store — формат не совместим

## Import подписки

1. Скопируйте ссылку `/sub/…` из бота (после оплаты)
2. Hiddify → **Add profile** → **Subscription link** → вставить URL
3. Обновить подписку → включить **auto-update** если есть

## Профили на 4G (порядок)

1. **Мобильный мост**
2. **Мобильный интернет**
3. **Мобильный CDN**

На Wi‑Fi: **Домашний Wi‑Fi**.

## Apple ID другого региона (альтернатива)

Для **v2RayTun** / **Streisand**:

1. Настройки → Apple ID → Media & Purchases → сменить регион (или второй Apple ID)
2. App Store → v2RayTun → Install
3. Import URL из бота

**Риск:** правила Apple для второго аккаунта — на усмотрение пользователя.

## OpenVPN / WireGuard

Только **«🔀 Запасные способы»** в боте. На 4G **не рекомендуем**.

## Проверка

4G → fast.com ≥1 Mbit/s ≥5 min на одном из Xray-профилей.

См. также `vpn-instructions.md` и `VPN94_DEEP_LINK_MATRIX.md`.
