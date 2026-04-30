# P7 SyncEngine Publishing Rules (Formal DoD)

Date: 2026-04-30

## Purpose

Закрепить единый регламент: **любой новый API/sync поток обязан публиковать состояние в `SyncEngine`**.
Это предотвращает появление "тихих" флоу без sync-индикаторов в UI.

## Mandatory Contract

Для любого нового потока синхронизации должны публиковаться события:

1. `*_load_start` -> `.syncing`
2. `*_load_complete` -> `.synced`  
   (или `*_load_local` -> `.local` при локальном fallback)
3. `*_change_pending` -> `.pending` (когда пользователь изменил данные до отправки)
4. `*_save_start` -> `.syncing`
5. `*_save_complete` -> `.synced`
6. `*_save_error` -> `.error(message)`

## Domain Mapping

- `offline` — unified offline sync runtime.
- `familyChat` — чат/typing/presence.
- `aiStreaming` — AI stream lifecycle.
- `family` — roster/family sync.
- `settings` — общие настройки и modals.
- `networkProtection` — сетевые/антивирусные/security settings.

## PR Checklist (must pass)

- [ ] В новом sync/API флоу есть публикация в `SyncEngine`.
- [ ] UI читает единый state из `SyncEngine`, а не локальный ad-hoc флаг.
- [ ] Есть обработка `.error(...)` и fallback state.
- [ ] Не нарушены существующие smoke-гейты (`phase8_*` + `xcodebuild`).

## Definition of Done for P7

P7 считается формально закрытым, когда:

- все новые realtime/offline/settings флоу проходят через этот контракт;
- при code review отсутствие `SyncEngine.publish(...)` в новом sync-флоу считается blocker;
- regression gates зелёные.

