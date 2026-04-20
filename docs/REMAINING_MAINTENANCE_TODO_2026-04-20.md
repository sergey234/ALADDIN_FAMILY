# Remaining Maintenance TODO (2026-04-20)

Электронный трекер оставшихся пунктов после закрытия основного контура (`42/42`, `138/138`).

## Current Baseline

- 42 components `verify`: **42/42** (100%)
- 42 components `inventory`: **42/42** (100%)
- 138 functions `verify`: **138/138** (100%)

## Remaining TODO

- [ ] Поддерживать `138/138`: новые строки/изменения добавлять только при подтвержденном сценарии (prod API + device/UI факт).
- [ ] При любых изменениях API/UX выполнять точечный re-check затронутых пунктов и фиксировать результат.
- [ ] После каждого re-check синхронизировать документы: `docs/PLAN_FOR_NEXT_ML_SYSTEM_20260328.md`, `docs/HANDOFF_NEXT_ML_SYSTEM_2026-04-20.md`, `docs/MASTER_PROGRESS_DASHBOARD_2026-04-20.md`.
- [ ] Вести список активных блокеров (если появятся): причина, влияние, владелец, ETA, критерий снятия блокера.

## Current Maintenance Cycle (executed)

- [x] Подтверждено сохранение baseline `138/138`: в `EXTENDED_138_CHECKLIST.md` `ok=138`, `TBD=0`.
- [x] Выполнен точечный re-check консистентности ключевых источников (`AUDIT_42_INVENTORY` + `EXTENDED_138_CHECKLIST`).
- [x] Синхронизированы `PLAN` + `HANDOFF` + `MASTER_DASHBOARD` после re-check.

## Tracking Log

- 2026-04-20: Базовый контур закрыт (`42/42`, `138/138`), переход в режим поддержки.
- 2026-04-20: Выполнен maintenance-cycle: re-check `138/138`, подтверждена консистентность, синхронизированы статус-документы.
