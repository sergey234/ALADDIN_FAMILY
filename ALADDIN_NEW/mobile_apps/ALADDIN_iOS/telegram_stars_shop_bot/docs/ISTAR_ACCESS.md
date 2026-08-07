# Доступ к iStar (кабинет и API)

Интеграция бота использует **iStar Partner API** для покупки Stars/Premium на Fragment.

## Рабочие URL

| Назначение | URL |
|------------|-----|
| **Вход в кабинет** (API key, webhook) | https://istar.fragmentapi.com/ |
| **Документация API** | https://istar.fragmentapi.com/docs |
| **Лендинг / регистрация** | https://fragmentapi.com/ |
| **Альтернативный лендинг** | https://istar.tg/api |
| **Базовый URL API** (в `.env` `ISTAR_API_BASE`) | `https://v1.fragmentapi.com/api/v1/partner` |

Корень `https://v1.fragmentapi.com/` отдаёт **404** — это нормально. Рабочие пути: `/api/v1/partner/...`.

## Если `istar.fragmentapi.com` не открывается

1. Попробуйте **VPN** (сайт на зарубежном хостинге).
2. Откройте **https://fragmentapi.com/** или **https://istar.tg/api** — ссылки на регистрацию.
3. API с сервера бота (`149.154.65.180`) обычно доступен по `v1.fragmentapi.com` даже если браузер с РФ не открывает кабинет.

## Что взять в кабинете

1. **API Key** → `ISTAR_API_KEY`
2. **Webhook secret** → `ISTAR_WEBHOOK_SECRET`
3. Webhook URL: `https://aladdin-ai.ru/v1/payments/istar-webhook`
4. Привязать **TON-кошелёк** магазина (`ISTAR_WALLET_TYPE=TON`)

## Шаблон `.env`

См. `docs/env.autofulfill.prod.template` и `docs/FRAGMENT_AUTO_FULFILL_ML_HANDOFF.md`.
