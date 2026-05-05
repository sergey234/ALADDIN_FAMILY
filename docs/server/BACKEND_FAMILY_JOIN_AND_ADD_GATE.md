# Бэкенд: join (POST) и жёсткий лимит на add

Документ для владельца API. Клиент iOS в репозитории ALADDIN_iOS уже реализует контракт ниже; без этих шагов на шлюзе **join по коду** и **серверный предел ростера** остаются расхождениями «на 100%».

## 1. Обязательный `POST /api/family/join`

**Проблема (исторически):** на шлюзе часто был только **GET** compat, тогда как iOS шлёт **`POST`** с телом:

```json
{
  "family_id": "<uuid или извлечённый из FAM-… кода>",
  "role": "parent|child|…",
  "age_group": "<строка как сегодня с клиента>",
  "personal_letter": "<A-Z>",
  "device_type": "smartphone|tablet|…"
}
```

**Требование:** реализовать **`POST /api/family/join`** (рядом с существующим GET compat или вместо заглушки), который:

- Принимает тело, совместимое с полями выше (имена полей как в iOS `JoinFamilyRequest`).
- Возвращает структуру, которую уже декодирует клиент как успешный join (аналог `FamilyResponse` / обёртка `APIResponse<FamilyResponse>` — как у действующего create/join на стенде, где join работает).
- Отдаёт осмысленные **409 / 403 / 404** с `detail`, чтобы приложение могло показать причину.

В репозитории iOS: реализация в `app/routers/family.py` (`POST /join`), схемы в `docs/release/current/openapi.json`. После выката на хост — при желании перезаписать весь **`openapi.json`** снимком с `GET /openapi.json` API (чтобы пути совпали с продом на 100%) и перепроверить смоук `docs/FAMILY_API_SMOKE_REGIMEN.md` §4.

## 2. Жёсткий gate на `POST /api/family/add` (рекомендуется)

**Проблема:** в аудите зафиксировано, что в обработчике add на дату проверки **не** вызывался `getMaxFamilyMembersFor` / **COUNT** перед вставкой — единственный надёжный gate был на iOS (`canAddFamilyMember`).

**Требование:** перед INSERT в `family_members`:

- Посчитать текущее число слотов семьи для того же `family_id`, что и для JWT-актора.
- Сравнить с **`getMaxFamilyMembersFor(subscription_level)`** (или эквивалент из `subscription_limits.py`).
- При превышении вернуть **409** с явным `detail` (например `family_roster_full`).

Так сервер остаётся источником правды, даже если клиент устарел или обойдён.

## 3. Лимиты (напоминание)

| Уровень   | Макс. членов семьи (прод-конфиг в аудите) |
|-----------|--------------------------------------------|
| free      | 1 |
| trial     | 3 |
| personal  | **2** |
| family    | 6 |
| premium   | 10 |

iOS **`SubscriptionManager.familyMemberLimit`** для `personal` выровнен на **2** под эту таблицу.
