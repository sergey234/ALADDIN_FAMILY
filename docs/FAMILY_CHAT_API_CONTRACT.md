# Family API: контракт `GET /members` и семейного чата

Каноническая реализация: `app/routers/family.py` (прод: деплой по внутреннему runbook).

## `GET /api/family/members`

| Условие | HTTP | Тело | Заголовки |
|--------|------|------|-----------|
| Есть primary family для JWT | 200 | Список участников | `X-Resolved-Family-Id`, при наличии строки членства — `X-Current-Member-Id` |
| Нет primary, query `familyId` передан (устаревший кэш) | **404** | `detail`: `No family registered for this account (invalid familyId query)` | — |
| Нет primary, query **нет** | 200 | `[]` | `X-Family-Context: none` (клиент сбрасывает локальный `family_id` / ростер) |
| Primary есть, `familyId` ≠ primary | **409** | `familyId does not match...` | — |

## `GET /api/family/chat/messages`

| Условие | HTTP | Тело | Заголовки |
|--------|------|------|-----------|
| Есть effective family (членство или primary) | 200 | Сообщения | `X-Resolved-Family-Id` |
| Передан query `familyId`, effective family **нет** | **404** | `No family context for requested familyId` | — |
| Query нет, effective **нет** | 200 | `[]` | — |

## `POST /api/family/chat/send` и `POST /api/family/chat/send/typing`

- Резолв семьи: `_resolve_effective_family_id_for_chat` (как у ленты для send).
- Нет семьи: **404** `Family not found` (раньше typing всегда возвращал 200 — исправлено).

## iOS

- Заголовок `X-Family-Context: none` обрабатывается в `APIService.applyFamilyMembersListHeaders` → `FamilyLocalStore.clearPersistedFamilyContextWhenServerReportsNoFamily()`.
- 404 на `GET /members` с текстом про `invalid familyId` / `No family registered` — тот же сброс в `performGetFamilyMembers`.
- Экран чата: `chatFamilyContextInvalid`, баннер, блок отправки при пустом ростере после sync.
