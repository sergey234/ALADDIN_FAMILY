# Ротация секретов: LAVA, Crypto Pay, xRocket

Краткий runbook для продакшена (`shared/.env` на сервере, путь см. `docs/ML_SYSTEM_HANDOFF_FINAL.md`). Секреты **не** хранятся в git.

## 1. Перед сменой

1. Убедиться, что есть **свежий бэкап** БД и копия текущего `.env` (вне репозитория).
2. Запланировать окно: после смены ключей нужен **рестарт** сервисов, пока они читают env при старте.

## 2. LAVA (`LAVA_SHOP_ID`, `LAVA_SECRET_KEY`, при смене URL — `LAVA_HOOK_URL`)

1. Обновить значения в `shared/.env` на сервере.
2. `systemctl restart aladdin-partner-api.service aladdin-webhook-worker.service` (и при необходимости `aladdin-telegram-bot.service`, если LAVA дергается только из API).
3. Проверка: `curl -sS -m 8 http://127.0.0.1:8090/health` → `{"status":"ok"}`.
4. Если менялся публичный URL вебхука — заново прописать hook в кабинете LAVA и сделать **тестовый платёж** на малый заказ.

## 3. Crypto Pay (`CRYPTO_PAY_API_TOKEN`)

1. Новый токен выдаётся в @CryptoBot (или testnet-боте) → Crypto Pay → приложение. Это **не** `BOT_TOKEN` магазина.
2. Записать в `shared/.env`, сохранить файл.
3. `systemctl restart aladdin-partner-api.service aladdin-webhook-worker.service`.
4. В кабинете Crypto Pay проверить URL вебхука (`POST …/v1/payments/crypto-pay-webhook`) и при необходимости обновить.
5. Смоук: малый заказ → оплата → в БД статус заказа `paid` без ручной кнопки «Оплачен».

## 4. xRocket Pay (`XROCKET_PAY_API_KEY`)

Аналогично п.3: правка `.env` → рестарт `aladdin-partner-api` + worker → проверка вебхука xRocket → смоук-оплата.

## 5. После ротации

- Логи первых минут: ошибки подписи вебхука (`401`/invalid signature) почти всегда означают **несовпадение секрета** с тем, что в кабинете провайдера.
- Rate limit Partner API (`PARTNER_API_RATE_LIMIT_*`) на секреты не влияет; при массовых 429 смотреть IP/клиента, а не ротацию.

## 6. Откат

Вернуть предыдущие значения из бэкапа `.env`, рестарт тех же unit’ов, повторить health и один смоук-вебхук.
