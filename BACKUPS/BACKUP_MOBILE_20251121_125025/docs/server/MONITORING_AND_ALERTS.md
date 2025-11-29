# MONITORING & ALERTS FOR payment_service

Документ описывает, как следить за работой backend `payment_service` и вовремя реагировать на ошибки (особенно связанные с `/api/payments/status`).

---

## 1. Базовые команды

```bash
# Логи сервиса
journalctl -u payment_service -n 200 --no-pager

# Фильтр 4xx/5xx по статусу платежа
journalctl -u payment_service --since "1 hour ago" | grep "/api/payments/status"

# Проверить состояние systemd
systemctl status payment_service --no-pager
```

---

## 2. Скрипт для алертов (journalctl)

Файл: `/opt/aladdin-backend/scripts/check_payment_status_errors.sh`

```bash
#!/bin/bash
THRESHOLD=10
COUNT=$(journalctl -u payment_service --since "15 minutes ago" --no-pager | grep "/api/payments/status" | egrep "404|500" | wc -l)

if [ "$COUNT" -ge "$THRESHOLD" ]; then
  echo "[ALERT] payment_service: $COUNT errors in last 15 minutes" | mail -s "payment_service alert" admin@example.com
  # или curl -X POST https://api.telegram.org/botTOKEN/sendMessage ...
fi
```

Права и запуск:
```bash
chmod +x /opt/aladdin-backend/scripts/check_payment_status_errors.sh
```

Cron (каждые 15 минут):
```bash
*/15 * * * * /opt/aladdin-backend/scripts/check_payment_status_errors.sh
```

---

## 3. Структурированные логи

В `payment_service/start.sh` добавить:
```bash
exec /opt/aladdin-backend/venv/bin/python3 -m uvicorn main:app \
  --host 0.0.0.0 --port 8000 \
  --log-config /opt/aladdin-backend/logging.yaml
```

Пример `logging.yaml`:
```yaml
version: 1
formatters:
  json:
    "()": "pythonjsonlogger.jsonlogger.JsonFormatter"
handlers:
  default:
    class: logging.StreamHandler
    formatter: json
    stream: ext://sys.stdout
loggers:
  uvicorn:
    handlers: [default]
    level: INFO
```

Так логи будут в JSON, их можно парсить и отправлять в ELK/Prometheus.

---

## 4. Что мониторим

- `/api/payments/status` — всплеск 404/500.
- `/api/payments/confirm` — ошибки вебхука → код не генерируется.
- `/api/subscription/activation/*` — коды активации (важно видеть 502/500).
- systemd `Active: failed` → перезапуск сервиса.

---

## 5. Реакция на алерты

1. Посмотреть логи (`journalctl -u payment_service`).
2. Проверить статус сервиса (`systemctl status`).
3. Если много 404 — проверить success.html (правильный `paymentId`?), наличие записи в БД.
4. Если 500 — смотреть traceback, перезапустить сервис.
5. Сообщить в чат поддержки/DevOps, если проблема массовая.

---

## 6. Дальнейшие улучшения

- Интеграция с Prometheus + Alertmanager.
- Отправка логов в ELK/Graylog для поиска.
- Дашборд с графиками количества 200/404/500 по endpoint’ам.

