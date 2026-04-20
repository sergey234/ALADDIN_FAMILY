# Deploy: webhook worker (systemd or cron)

Этот документ закрывает операционный пункт P1: периодический запуск обработчика очереди `outbound_webhook_events`.

## Вариант A (рекомендуется): systemd

1. Скопируйте unit:
   - источник: `docs/webhook-worker.service`
   - назначение: `/etc/systemd/system/aladdin-webhook-worker.service`
2. Проверьте пути внутри unit:
   - `WorkingDirectory=/opt/telegram_stars_shop_bot`
   - `EnvironmentFile=/opt/telegram_stars_shop_bot/.env`
   - `ExecStart=/usr/bin/python3 -m partner_api.webhook_worker --forever --sleep-sec 30 --limit 200`
3. Включите сервис:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now aladdin-webhook-worker.service
sudo systemctl status aladdin-webhook-worker.service --no-pager
```

4. Проверка логов:

```bash
sudo journalctl -u aladdin-webhook-worker.service -n 100 --no-pager
tail -n 100 /var/log/aladdin-webhook-worker.log
```

## Вариант B: cron

1. Откройте cron:

```bash
crontab -e
```

2. Добавьте строку из `docs/webhook-worker.crontab`.
3. Проверьте, что лог обновляется:

```bash
tail -n 50 /var/log/aladdin-webhook-worker.log
```

## Smoke-check после включения

1. Убедиться, что worker запускается:
   - в логах есть `webhook_worker_cycle sent=...` (systemd) или `webhook_worker_once sent=...` (cron).
2. Проверить очередь:

```sql
SELECT status, COUNT(*) AS c
FROM outbound_webhook_events
GROUP BY status;
```

3. Убедиться, что `pending` не копится бесконтрольно, а `failed` обрабатываются оператором.

## Минимальные требования

- Корректный `.env` (тот же, что использует API).
- Рабочий DNS/сеть до `webhook_url` партнёров.
- Доступ на запись в `/var/log/aladdin-webhook-worker.log`.
