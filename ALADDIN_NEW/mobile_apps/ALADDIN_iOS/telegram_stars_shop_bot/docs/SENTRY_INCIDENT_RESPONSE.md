# Sentry Alerts и регламент реакции

Документ задаёт минимальный operational baseline для боевого релиза.

## 1) Что настроить в Sentry

- Проекты: `telegram-shop-bot` и `telegram-shop-partner-api` (или один общий проект с тегом `service`).
- Environments: `staging`, `production`.
- Alert rules:
  - `Level=error`, `count >= 5` за 10 минут (production) -> канал дежурного.
  - `Unhandled exception` сразу -> канал дежурного.
  - `partner_webhook_failed` и `partner_webhook_retry_scheduled` >= 10 за 15 минут -> техканал.
- Дополнительно: weekly digest по новым issue.

## 2) Кто и как реагирует

- **On-call инженер (L1):** подтверждение алерта <= 10 минут.
- **Backend инженер (L2):** подключается при повторном алерте или массовом сбое.
- **Owner продукта:** уведомляется при инциденте уровня High (деградация оплаты/API).

## 3) Playbook на инцидент

1. Проверить `Sentry issue`, traceback, affected environment.
2. Проверить логи приложения и health:
   - `/health` для Partner API
   - ошибки webhook доставки (`outbound_webhook_events` со статусом `failed`)
3. Классифицировать:
   - `P1`: оплаты/заказы не проходят или массово падают.
   - `P2`: частичные сбои, есть workaround.
4. Принять действие:
   - hotfix / rollback / временное выключение проблемной интеграции.
5. После восстановления:
   - зафиксировать RCA (корень проблемы),
   - добавить тест, чтобы исключить повторение.

## 4) SQL-подсказки для webhook деградации

```sql
SELECT id, order_id, attempts, max_attempts, last_error, created_at
FROM outbound_webhook_events
WHERE status = 'failed'
ORDER BY id DESC
LIMIT 50;
```

```sql
SELECT status, COUNT(*) AS c
FROM outbound_webhook_events
GROUP BY status;
```

## 5) Definition of Done для операции

- Alert доставлен и подтверждён.
- Восстановлен рабочий поток заказов/API.
- Issue в Sentry переведён в `resolved`.
- Постмортем (короткий) добавлен в рабочий журнал команды.
