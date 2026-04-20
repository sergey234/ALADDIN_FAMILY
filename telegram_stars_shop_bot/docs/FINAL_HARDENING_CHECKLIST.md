# Final Hardening Checklist (P1)

Цель: закрыть обязательные пункты перед боевым релизом.

## 1. Приёмка на staging/prod

- [ ] Пройден `docs/ACCEPTANCE_CHECKLIST.md` целиком.
- [ ] Отдельно проверены сценарии API-заказа + payment webhook + status changed webhook.
- [ ] Итог приёмки сохранён в журнале релиза.

## 2. Надёжность исходящих webhook

- [x] Добавлена очередь `outbound_webhook_events`.
- [x] Добавлены повторные попытки доставки с backoff.
- [x] Добавлен статус `failed` после исчерпания попыток.
- [x] Добавлен worker `python3 -m partner_api.webhook_worker` для cron/systemd.
- [ ] Настроен периодический job/reconciler на staging/prod (cron или systemd), который запускает worker.

## 3. Тесты негативных кейсов

- [x] API: тесты на 404/422 и невалидные запросы.
- [x] Payment webhook: тест на конфликтный статус (409).
- [x] Outbound webhook: тест на retry и успешную доставку после ошибки.

## 4. CI качество

- [x] Добавлен `ruff` в CI.
- [x] Добавлен `mypy` в CI в режиме optional (`continue-on-error`).
- [ ] (опционально) перевести `mypy` в обязательный после очистки предупреждений.

## 5. Sentry и инциденты

- [x] Добавлен runbook `docs/SENTRY_INCIDENT_RESPONSE.md`.
- [ ] Созданы alert rules в Sentry (prod/staging).
- [ ] Назначен on-call и канал эскалации.

## Release Gate

Go-live разрешён, когда:
1) приёмка завершена,  
2) нет blocker-багов,  
3) webhook queue не копит критические `failed` без реакции.
