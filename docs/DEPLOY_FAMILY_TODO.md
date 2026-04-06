# TODO по деплою и проверке семьи (12 задач)

Контекст: правки в `app/routers/family.py` (full members по familyId, admin-add `user_id=NULL`, remove parent-first actor, reconcile очистка конфликтных `user_id`, метрики). Ниже — что нужно сделать, чтобы другая ML-система могла выполнить без расспросов.

## DEP-1 — Deploy backend changes (family.py) to prod/staging
- Залить `app/routers/family.py` в `/opt/aladdin-backend/app/routers/` (SCP/SFTP, SSH `root@149.154.65.180`).
- Убедиться, что файл обновлён (например, `grep metric_family_members_count family.py` на сервере).

## DB-1 — Индексы
- Выполнить (идемпотентно):
  - `CREATE INDEX IF NOT EXISTS idx_family_members_family_id_id ON family_members (family_id, id);`
  - `CREATE INDEX IF NOT EXISTS idx_family_members_user_id ON family_members (user_id);`
- Через `psql $DATABASE_URL` или psql на сервере.

## OPS-1 — Рестарт и инвалидация
- Перезапустить backend (systemd/pm2/docker compose — что реально используется на сервере).
- Инвалидировать кэш/прокси для `/api/family/*`, если есть CDN/NGINX кеши.
- Health-check: `curl -s -S -m 8 http://127.0.0.1:8002/api/health` и внешний `http://149.154.65.180:8002/api/health`.

## FIX-1 — Разовая чистка конфликтных user_id
- Запустить `POST /api/family/reconcile` (Bearer токен) для семьи, где воспроизводилась проблема, чтобы обнулить `user_id` у не-parent с тем же `user_id`, что у актора.

## FIX-2 — Массовый reconcile
- Выполнить `POST /api/family/reconcile` для текущей семьи и по возможности для топ-50 активных семей (скриптом или джобой), чтобы убрать наследованные конфликты `user_id`.

## QA-1 — E2E happy-path (add→delete)
- Шаги:
  1) Родитель добавляет ребёнка.
  2) `GET /api/family/members` должен вернуть ≥2 id.
  3) Родитель удаляет ребёнка — ожидать `200 OK`, карточка исчезает; повторный `GET /api/family/members` без этого id.

## QA-2 — Негативные сценарии
- Проверить, что:
  - self-removal → `400 Self-removal is not allowed`;
  - удаление последнего родителя → `400 Cannot remove the last parent`;
  - не-админ удаляет → `403 Only administrators can remove members`.

## OBS-1 — Метрики и алерты
- Завести графики/алерты по лог-метрикам:
  - `metric_family_members_count`
  - `metric_family_member_added`
  - `metric_family_member_removed`
  - `metric_family_reconcile`
- Алерт на частые partial-subset (server_count < local_count).

## TEST-1 — Интеграционные тесты backend
- Покрыть кейс: add → members → remove → members (read-after-write).
- Проверить контекст familyId и parent-only политику.

## CRON-1 — Ночной reconcile
- Поставить джоб, проходящий по всем family_id, вызывающий reconcile или аналогичный SQL для чистки конфликтных `user_id` и статусов.

## DOC-1 — Документация
- Обновить API-доку: админ-добавленные участники сохраняются с `user_id=NULL` до их собственного логина; actor выбирается parent-first при remove.

## RB-1 — Rollback/feature-flag
- Описать план отката и фича-флаг для логики parent-first actor (если потребуется быстро отключить), плюс вернуть старое поведение `user_id` на add при катастрофе.
