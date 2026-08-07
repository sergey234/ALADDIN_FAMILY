# Смоук: автовыдача (iStar) + админка (п.37)

Короткий чеклист перед продом. Секреты только в `.env` на сервере, не в репозитории.

Полный план: `docs/FRAGMENT_AUTO_FULFILL_ML_HANDOFF.md`.

## 1. Конфиг

- `AUTO_FULFILL_ENABLED=true`, типы: `AUTO_FULFILL_STARS_ENABLED` / `AUTO_FULFILL_PREMIUM_ENABLED` по плану.
- `AUTO_FULFILL_MAX_ORDER_RUB=50000`, `AUTO_FULFILL_MAX_ATTEMPTS=5`, `AUTO_FULFILL_POLL_INTERVAL_SECONDS=60`.
- `ISTAR_API_KEY`, `ISTAR_API_BASE`, `ISTAR_WALLET_TYPE=TON`, `ISTAR_WEBHOOK_SECRET`.
- `ISTAR_MIN_TON_BALANCE_ALERT=20` (рекомендуется) — ниже порога воркер не берёт заказы + ops-алерт.
- `STUCK_PROCESSING_ALERT_MINUTES=30`, `STUCK_PAID_ALERT_HOURS=24`.
- `AUTO_FULFILL_FAILURE_ALERTS_ENABLED=true`.
- В кабинете iStar: URL вебхука `https://<ваш-домен>/v1/payments/istar-webhook`, секрет совпадает с `.env`.
- Partner API: `GET https://<домен>/health` → `200`, `{"status":"ok"}`.
- Webhook без подписи: `POST …/istar-webhook` → **401** (не 503).

## 2. Воркер

```bash
systemctl enable --now auto-fulfill-worker.service
journalctl -u auto-fulfill-worker.service -n 50 --no-pager
```

Один цикл вручную:

```bash
/opt/aladdin-telegram-shop-bot/venv/bin/python3 -m partner_api.auto_fulfill_worker --limit 5
```

В логах `stats=` — нули, если нет `paid` или выключен мастер-флаг. При низком TON: `low_ton_skip=1`.

При старте бота/воркера с `AUTO_FULFILL_ENABLED=true` без `ISTAR_API_KEY` — **WARNING** в логах.

## 3. Счастливый путь

1. Заказ **100 Stars** (или Premium 3/6/12 мес.) с валидным `@username` → **`paid`** (LAVA / баланс / админ).
2. Воркер ≤ 60 с → **`processing`**, в админке заполнен **fulfillment_provider_ref**.
3. Webhook iStar `order.completed` → **`completed`**, покупателю «Готово».
4. Stars/Premium видны в Telegram у получателя.

## 4. Premium 1 месяц

- В политике бота **1 / 3 / 6 / 12** мес. допускаются в авто.
- **iStar API** в документации указывает для Premium только **3 / 6 / 12**. Заказ **Premium 1 мес.** может уйти оператору, если iStar отклонит `months=1` — это ожидаемый fallback.

## 5. Админка

- **«Только вручную»** — воркер не берёт; аудит `adm:ffman`.
- Супер-админ: **«Снова авто»**, **«Сброс авто-полей»**; аудит `adm:ffauto` / `adm:ffrst`.
- **`/admqueue`** — очередь оператора.

## 6. Негатив

| Кейс | Ожидание |
|------|----------|
| Неверный `@username` | `paid`, ошибка в карточке, после 5 попыток — оператор |
| `order.failed` от iStar | ошибка в заказе, сообщение покупателю |
| Низкий TON (`ISTAR_MIN_TON_BALANCE_ALERT`) | batch пропущен, ops-алерт |
| `insufficient funds` при create | откат `processing`→`paid`, ops-алерт |
| Двойной webhook completed | без повторной выдачи / рефки (`fulfillment_applied_at`) |

## 7. Регрессия

```bash
cd telegram_stars_shop_bot && python3 -m pytest -q
```
