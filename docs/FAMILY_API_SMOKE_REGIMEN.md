# Смоук-регламент: семья (create / join / add / remove / stats)

Один чеклист для **тестовой сети** и прода. Подставьте базу и токен; не коммитьте секреты в репозиторий.

## Базы

| Окружение | Пример базы | Примечание |
|-----------|-------------|------------|
| Публичный шлюз | `https://aladdin-ai.ru` | Как в приложении из логов |
| Прямой API (гайд ML / сервер) | `http://149.154.65.180:8002` | Health: `GET …/api/health` |

Переменные для копирования в shell (задайте локально):

- `ALADDIN_API_BASE` — URL **без** завершающего `/`
- `ALADDIN_JWT` — Bearer для родителя/создателя семьи
- Опционально `ALADDIN_FAMILY_ID`, `ALADDIN_MEMBER_ID` — из ответов предыдущих шагов

Заголовки по умолчанию: `Authorization: Bearer $ALADDIN_JWT`, при необходимости `X-API-Key` и `X-Family-Id` как в приложении.

---

## 1. Health (опционально для :8002)

```bash
curl -sS -m 8 "${ALADDIN_API_BASE}/api/health"
```

Ожидание: HTTP 200, тело с признаком живости (`status` ok или эквивалент).

---

## 2. Создать семью

- **Клиент iOS:** `POST /api/family/create` с телом `CreateFamilyRequest` (роль, возраст, буква, `device_type`), см. `FamilyRegistrationViewModel` / `APIService.createFamily`.
- **Смоук curl:** повторите тот же контракт, что шлёт приложение (или зафиксируйте пример тела в Postman).

Проверить в ответе: `family_id`, `your_member_id`, при необходимости recovery-код.

Сохранить: `FAMILY_ID`, `PARENT_MEMBER_ID`.

---

## 3. Статистика после create

```bash
curl -sS -m 15 -H "Authorization: Bearer ${ALADDIN_JWT}" \
  -H "X-Family-Id: ${ALADDIN_FAMILY_ID}" \
  "${ALADDIN_API_BASE}/api/family/stats"
```

Ожидаемые поля квоты ростера (выровнены с gate на `POST /api/family/add`): `familyRosterUsed`, `familyRosterMax`, `ownerSubscriptionTier` (при отсутствии семьи — кап по `subscription_level` самого пользователя, `familyRosterUsed=0`).

Ожидание: HTTP 200, `totalMembers` ≥ 1, согласовано с `GET /api/family/members` для той же семьи.

---

## 4. Join по коду приглашения

- **Клиент iOS:** `POST /api/family/join` + fallback `POST /family/join`, тело `JoinFamilyRequest` (`family_id`, `role`, `age_group`, `personal_letter`, `device_type`).
- **Контракт в репозитории:** в `docs/release/current/openapi.json` на `/api/family/join` есть **GET** (compat) и **POST** (боевой join, схемы `JoinFamilyRequest` / `FamilyJoinAPIResponse`). Детали выката — `docs/server/BACKEND_FAMILY_JOIN_AND_ADD_GATE.md`.

Смоук DoD: второе устройство / второй JWT проходит join **без 404** на основном пути, в ответе есть данные семьи и `your_member_id` для нового участника.

---

## 5. Добавить участника (админ в существующей семье)

- **Клиент:** `POST /api/family/add` с `Idempotency-Key`, см. `APIService.addFamilyMember`.

Проверить: HTTP 200, новая строка в `GET /api/family/members`, `GET /api/family/stats` увеличил `totalMembers` (после кэша/задержки допустим один повтор запроса).

---

## 6. Удалить участника

- **Клиент iOS:** `DELETE /api/family/remove` с JSON-телом `RemoveFamilyMemberRequest` (`memberId` обязателен; `source`, `reason`, `familyId` опционально), см. `APIService.removeFamilyMember`.
- **OpenAPI (репозиторий):** тот же путь: **DELETE** с `RemoveFamilyMemberRequest`; дополнительно есть **GET** compat (не используется iOS).

Проверить: HTTP 200, в members нет удалённого id, `stats.totalMembers` уменьшился.

---

## 7. Главный экран (приложение)

После шагов 5–6 (или только remove):

- Открыть главную (или pull-to-refresh / повторный заход), убедиться что счётчик членов и слоты **X / Y** совпадают с `stats` и лимитом тарифа (`SubscriptionManager.currentFamilyLimit`).
- После удаления: сработали бы `FamilyMembersUpdated` / `MainFamilyStatsForceRefresh` (в коде уже есть) — в логах Xcode виден debounced `loadDashboardData` или обновление без устаревшего TTL.

---

## 8. Лимит Personal (семейные слоты)

Ожидаемое **максимальное число членов семьи** для тарифа Personal на клиенте после выравнивания: **2** (как в `subscription_limits.py` на проде). См. `REGISTRATION_AND_TARIFF_MAIN_SCREEN_ML_REFERENCE.md` §10.1.

---

## 9. Anti-race stress smoke (20 parallel add)

Цель: подтвердить, что при параллельных запросах лимит ростера не пробивается (лишние попытки получают `409 family_roster_full`).

```bash
python3 scripts/family_parallel_add_smoke.py \
  --base "${ALADDIN_API_BASE}" \
  --token "${ALADDIN_JWT}" \
  --family-id "${ALADDIN_FAMILY_ID}" \
  --attempts 20 \
  --workers 20
```

DoD:
- итоговый `familyRosterUsed <= familyRosterMax`;
- `200` не превышает доступные места до старта;
- переполнение возвращает `409 family_roster_full`;
- нет неожиданных кодов ответа.

---

## 10. Client tamper guard smoke (static contract)

Цель: гарантировать, что подмена локальных `max/used` на клиенте не влияет на решение сервера.

```bash
python3 scripts/family_client_tamper_guard_smoke.py
```

Проверяется:
- `AddFamilyMemberRequest` не содержит клиентских quota-полей (`max/used/...`);
- сервер принимает решение только по server-side owner level + `COUNT(*)`;
- guard выполняется до `INSERT INTO family_members`;
- anti-race lock присутствует в `/api/family/add` и `/api/family/join`.

---

## Критерий «смоук пройден»

Все шаги 2 → 3 → (4 или 5) → 6 → 7 + шаги 9/10 выполняются на выбранной базе без расхождения чисел между **members**, **stats** и **главной**, без необоснованного **404** на join (если join в scope), и без пробоя лимита при параллельных add.
